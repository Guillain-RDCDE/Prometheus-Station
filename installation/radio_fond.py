# Prometheus Station - fond de carte du trajet des messages, hors ligne (27/11/2026). Python pur : essais tests/radio.
#
# Les donnees de Natural Earth (domaine public, naturalearthdata.com) : cotes, frontieres, regions, fleuves, lacs,
# routes principales, villes. Telechargees une fois (internet, ~110 Mo), reduites a ~10 Mo dans FOND_CARTE :
# chaque trait est coupe en petits morceaux (MORCEAU points), chacun avec son cadre, et ecrit en « polyline »
# (le codage de Google, au millieme de degre, ~100 m) : la station ne decode que les morceaux a l'ecran, et ne
# garde que les points distants d'au moins un pixel. Aucune tuile, aucun serveur de cartes : tout reste ici.
import json, math, os

SOURCE = 'https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/'
# couche -> fichier Natural Earth (10 m : le plus detaille)
COUCHES = {'cotes': 'ne_10m_coastline', 'frontieres': 'ne_10m_admin_0_boundary_lines_land',
           'regions': 'ne_10m_admin_1_states_provinces_lines', 'fleuves': 'ne_10m_rivers_lake_centerlines',
           'lacs': 'ne_10m_lakes', 'routes': 'ne_10m_roads'}
VILLES = 'ne_10m_populated_places_simple'
MORCEAU = 64            # points par morceau de trait
PRECISION = 1000        # millieme de degre
MAX_VILLES = 14


# ----- codage « polyline » (entiers signes, par difference avec le point precedent)
def _coder_nombre(n):
    n = ~(n << 1) if n < 0 else n << 1
    s = []
    while n >= 0x20:
        s.append(chr((0x20 | (n & 0x1f)) + 63))
        n >>= 5
    s.append(chr(n + 63))
    return ''.join(s)


def coder(points):
    """[[lon, lat], …] -> texte (lat puis lon, comme Google)."""
    res, plat, plon = [], 0, 0
    for lon, lat in points:
        ilat, ilon = round(lat * PRECISION), round(lon * PRECISION)
        res.append(_coder_nombre(ilat - plat) + _coder_nombre(ilon - plon))
        plat, plon = ilat, ilon
    return ''.join(res)


def decoder(texte):
    points, i, lat, lon = [], 0, 0, 0
    while i < len(texte):
        vals = []
        for _ in range(2):
            n = decal = 0
            while True:
                b = ord(texte[i]) - 63
                i += 1
                n |= (b & 0x1f) << decal
                decal += 5
                if b < 0x20:
                    break
            vals.append(~(n >> 1) if n & 1 else n >> 1)
        lat += vals[0]
        lon += vals[1]
        points.append([lon / PRECISION, lat / PRECISION])
    return points


# ----- reduire un fichier GeoJSON de Natural Earth
def traits(geometrie):
    """Les traits d'une geometrie (lignes, ou contours des surfaces), en listes de [lon, lat]."""
    t, c = (geometrie or {}).get('type'), (geometrie or {}).get('coordinates') or []
    if t == 'LineString':
        return [c]
    if t in ('MultiLineString', 'Polygon'):
        return list(c)
    if t == 'MultiPolygon':
        return [anneau for poly in c for anneau in poly]
    return []


def morceaux(points):
    """Un trait coupe en morceaux de MORCEAU points (chacun reprend le dernier point du precedent)."""
    res = []
    for i in range(0, max(len(points) - 1, 1), MORCEAU - 1):
        m = [[round(p[0], 3), round(p[1], 3)] for p in points[i:i + MORCEAU] if len(p) >= 2]
        if len(m) >= 2:
            lons, lats = [p[0] for p in m], [p[1] for p in m]
            res.append([min(lons), min(lats), max(lons), max(lats), coder(m)])
    return res


def garder_route(proprietes):
    """Routes : seulement les grands axes (rang Natural Earth <= 7)."""
    try:
        return int(proprietes.get('scalerank', 99)) <= 7
    except (TypeError, ValueError):
        return False


def compacter(couche, geojson):
    res = []
    for f in (geojson or {}).get('features', []):
        if couche == 'routes' and not garder_route(f.get('properties') or {}):
            continue
        for t in traits(f.get('geometry')):
            res.extend(morceaux(t))
    return res


def compacter_villes(geojson):
    res = []
    for f in (geojson or {}).get('features', []):
        p, g = f.get('properties') or {}, f.get('geometry') or {}
        c = g.get('coordinates') or []
        if g.get('type') != 'Point' or len(c) < 2 or not p.get('name'):
            continue
        try:
            rang, pop = int(p.get('scalerank', 10)), int(p.get('pop_max') or 0)
        except (TypeError, ValueError):
            rang, pop = 10, 0
        res.append([str(p['name'])[:40], round(c[0], 3), round(c[1], 3), rang, pop])
    return res


# ----- extraire ce qui est a l'ecran
def simplifier(points, tol):
    """Garde les points distants d'au moins tol degres (la longitude comptee a sa vraie largeur)."""
    if len(points) <= 2 or tol <= 0:
        return points
    k = math.cos(math.radians(points[0][1]))
    res = [points[0]]
    for p in points[1:-1]:
        if abs(p[0] - res[-1][0]) * k >= tol or abs(p[1] - res[-1][1]) >= tol:
            res.append(p)
    res.append(points[-1])
    return res


def extraire(fond, ouest, sud, est, nord, tol):
    """Les traits de chaque couche dans le cadre (simplifies a tol degres), et les villes principales."""
    res = {}
    for couche in COUCHES:
        lignes = []
        for w, s, e, n, code in fond.get(couche, []):
            if e < ouest or w > est or n < sud or s > nord:
                continue
            lignes.append(simplifier(decoder(code), tol))
        res[couche] = lignes
    villes = [v for v in fond.get('villes', []) if ouest <= v[1] <= est and sud <= v[2] <= nord]
    villes.sort(key=lambda v: (v[3], -v[4]))
    # Pas deux noms l'un sur l'autre : au moins 12 « tolerances » (une douzaine de pixels) entre deux villes
    gardees = []
    for v in villes:
        if all(abs(v[1] - g[1]) * math.cos(math.radians(v[2])) > 12 * tol or abs(v[2] - g[2]) > 6 * tol for g in gardees):
            gardees.append(v)
        if len(gardees) >= MAX_VILLES:
            break
    res['villes'] = [{'nom': v[0], 'lon': v[1], 'lat': v[2]} for v in gardees]
    return res


def lire_fond(fichier, _cache={}):
    """Le fond de carte garde sur la station (relu seulement si le fichier a change), ou {} s'il n'y est pas."""
    try:
        quand = os.path.getmtime(fichier)
    except OSError:
        return {}
    if _cache.get('fichier') != fichier or _cache.get('mtime') != quand:
        try:
            d = json.load(open(fichier, encoding='utf-8'))
        except (OSError, ValueError):
            d = {}
        _cache.update(fichier=fichier, mtime=quand, valeur=d if isinstance(d, dict) else {})
    return _cache['valeur']
