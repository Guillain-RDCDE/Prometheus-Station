# Prometheus Station - fond de carte du trajet des messages, hors ligne (27/11/2026). Python pur : essais tests/radio.
#
# Les donnees de Natural Earth (domaine public, naturalearthdata.com) : terres et lacs (surfaces coloriees), cotes,
# frontieres, regions, fleuves, routes principales ; et les villes de plus de 5000 habitants de GeoNames
# (geonames.org, CC BY 4.0 : la carte le cite). Telechargees une fois (internet, ~120 Mo), reduites dans FOND_CARTE.
# Les surfaces sont decoupees en carreaux (decouper_surfaces) : un contour comme celui de l'Europe n'est jamais
# relu en entier, seuls les carreaux a l'ecran le sont. Les traits :
# chaque trait est coupe en petits morceaux (MORCEAU points), chacun avec son cadre, et ecrit en « polyline »
# (le codage de Google, au millieme de degre, ~100 m) : la station ne decode que les morceaux a l'ecran, et ne
# garde que les points distants d'au moins un pixel. Aucune tuile, aucun serveur de cartes : tout reste ici.
import json, math, os

SOURCE = 'https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/'
# couche -> fichier Natural Earth (10 m : le plus detaille)
COUCHES = {'cotes': 'ne_10m_coastline', 'frontieres': 'ne_10m_admin_0_boundary_lines_land',
           'regions': 'ne_10m_admin_1_states_provinces_lines', 'fleuves': 'ne_10m_rivers_lake_centerlines',
           'routes': 'ne_10m_roads'}
SURFACES = {'terres': 'ne_10m_land', 'lacs': 'ne_10m_lakes'}
VILLES_SOURCE = 'https://download.geonames.org/export/dump/cities5000.zip'
MORCEAU = 64            # points par morceau de trait
PRECISION = 1000        # millieme de degre
MAX_VILLES = 18
VERSION = 2              # a augmenter quand le contenu du fond change : les stations le refont d'elles-memes
CARREAU_POINTS = 1500   # un carreau de surface est recoupe en deux tant qu'il a plus de points (ou plus d'un degre)


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


def couper_anneau(anneau, axe, valeur, dessous):
    """Sutherland-Hodgman : la partie d'un contour ferme du cote voulu de la droite axe = valeur (0 = lon, 1 = lat)."""
    res = []
    n = len(anneau)
    for i in range(n):
        a, b = anneau[i - 1], anneau[i]
        dedans_a = (a[axe] <= valeur) if dessous else (a[axe] >= valeur)
        dedans_b = (b[axe] <= valeur) if dessous else (b[axe] >= valeur)
        if dedans_b:
            if not dedans_a:
                res.append(_croisement(a, b, axe, valeur))
            res.append(b)
        elif dedans_a:
            res.append(_croisement(a, b, axe, valeur))
    return res


def _croisement(a, b, axe, valeur):
    t = (valeur - a[axe]) / (b[axe] - a[axe])
    p = [a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1])]
    p[axe] = valeur
    return p


def decouper_surfaces(geojson):
    """Les surfaces (polygones) coupees en carreaux : [[ouest, sud, est, nord, [contour code, ...]], ...]."""
    res = []
    for f in (geojson or {}).get('features', []):
        g = f.get('geometry') or {}
        if g.get('type') == 'Polygon':
            polys = [g.get('coordinates') or []]
        elif g.get('type') == 'MultiPolygon':
            polys = g.get('coordinates') or []
        else:
            polys = []
        for poly in polys:
            anneaux = [[[float(p[0]), float(p[1])] for p in a if len(p) >= 2] for a in poly]
            anneaux = [a for a in anneaux if len(a) >= 3]
            if not anneaux:
                continue
            lons = [p[0] for p in anneaux[0]]
            lats = [p[1] for p in anneaux[0]]
            _carreaux(anneaux, min(lons), min(lats), max(lons), max(lats), res)
    return res


def _carreaux(anneaux, w, s, e, n, res):
    pile = [(anneaux, w, s, e, n)]
    while pile:
        anneaux, w, s, e, n = pile.pop()
        total = sum(len(a) for a in anneaux)
        largeur, hauteur = (e - w) * math.cos(math.radians((s + n) / 2)), n - s    # en degres « vrais »
        # On coupe le cote le plus long ; jamais sans fin (pres d'un pole, un carreau peut n'avoir aucune largeur)
        axe = 0 if largeur >= hauteur else 1
        m = (w + e) / 2 if axe == 0 else (s + n) / 2
        fini = total <= CARREAU_POINTS and max(largeur, hauteur) <= 1 or total <= 8 or max(largeur, hauteur) < 0.01
        if fini or m in ((w, e) if axe == 0 else (s, n)):
            codes = [coder([[round(p[0], 3), round(p[1], 3)] for p in a]) for a in anneaux]
            res.append([round(w, 3), round(s, 3), round(e, 3), round(n, 3), codes])
            continue
        for dessous in (True, False):
            parts = [couper_anneau(a, axe, m, dessous) for a in anneaux]
            parts = [p for p in parts if len(p) >= 3]
            if not parts:
                continue
            if axe == 0:
                pile.append((parts, w, s, m, n) if dessous else (parts, m, s, e, n))
            else:
                pile.append((parts, w, s, e, m) if dessous else (parts, w, m, e, n))


def compacter_geonames(texte):
    """cities5000.txt de GeoNames (colonnes separees par des tabulations) : [[nom, lon, lat, 0, population], ...]."""
    res = []
    for ligne in texte.splitlines():
        c = ligne.split('\t')
        if len(c) < 15 or not c[1]:
            continue
        try:
            res.append([c[1][:40], round(float(c[5]), 3), round(float(c[4]), 3), 0, int(c[14] or 0)])
        except ValueError:
            continue
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
    for couche in SURFACES:
        res[couche] = [[simplifier(decoder(code), tol) for code in codes]
                       for w, s, e, n, codes in fond.get(couche, []) if not (e < ouest or w > est or n < sud or s > nord)]
    villes = [v for v in fond.get('villes', []) if ouest <= v[1] <= est and sud <= v[2] <= nord]
    villes.sort(key=lambda v: (v[3], -v[4]))
    # Pas deux noms l'un sur l'autre (tol = un pixel) : 45 pixels de cote ou 12 de haut entre deux villes
    gardees = []
    for v in villes:
        if all(abs(v[1] - g[1]) * math.cos(math.radians(v[2])) > 45 * tol or abs(v[2] - g[2]) > 12 * tol for g in gardees):
            gardees.append(v)
        if len(gardees) >= MAX_VILLES:
            break
    res['villes'] = [{'nom': v[0], 'lon': v[1], 'lat': v[2], 'habitants': v[4]} for v in gardees]
    return res


def a_refaire(fichier):
    """Le fond manque, ou il date d'une version precedente (avant le 27/11/2026 au soir : ni terres ni villes GeoNames)."""
    try:
        with open(fichier, encoding='utf-8') as f:
            debut = f.read(200)
    except OSError:
        return True
    return '"version": %d' % VERSION not in debut


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
