# Prometheus Station - trajet d'un message MeshCore (27/11/2026). Python pur, sans radio : essais tests/radio.
#
# Un message MeshCore envoye « a tout le monde » garde dans son paquet la liste des relais traverses : chacun y
# ajoute le debut de son identifiant (1, 2 ou 3 octets). La station retrouve qui ils sont, et ou, parmi :
#   - les radios qu'elle a entendues s'annoncer (historique) et ses contacts : source « entendu » ;
#   - la liste publique des relais MeshCore (map.meshcore.dev), gardee dans RELAIS_PUBLICS : source « public ».
# Un debut d'identifiant court peut appartenir a plusieurs relais dans le monde : on garde, parmi toutes les
# chaines possibles, la plus courte de la station jusqu'a l'expediteur (une radio entendue par la station y passe
# un peu avant), et on dit « probable » quand un autre relais etait possible a cette etape.
import json, math, os, time

URL_PUBLIQUE = 'https://map.meshcore.dev/api/v1/nodes'
TYPES_RELAIS = (2, 3)          # MeshCore : 2 = repeteur, 3 = salon (les deux relaient) ; 1 = compagnon, ne relaie pas
FRAICHEUR_JOURS = 60           # un relais public qui ne s'est pas annonce depuis plus longtemps est ignore
SAUT_MAX_KM = 300              # au-dela, un relais n'est pas pris pour l'etape (un saut LoRa depasse rarement 300 km)
BONUS_ENTENDU = 15             # km : une radio entendue par la station passe avant une radio de la liste a peine plus proche
PENALITE_INCONNU = 300         # km : prix d'une etape laissee inconnue alors qu'un relais y etait possible
MAX_CHAINES = 200              # chaines gardees a chaque etape (les plus courtes) : le calcul reste rapide


def km(a, b):
    """Distance a vol d'oiseau entre deux points {lat, lon}, en kilometres."""
    r = math.pi / 180
    dl, dg = (b['lat'] - a['lat']) * r, (b['lon'] - a['lon']) * r
    x = math.sin(dl / 2) ** 2 + math.cos(a['lat'] * r) * math.cos(b['lat'] * r) * math.sin(dg / 2) ** 2
    return 6371 * 2 * math.asin(math.sqrt(min(1, x)))


def decouper(chemin, sauts):
    """« 9547 8738 … » : le chemin (hexadecimal) en identifiants de relais, dans l'ordre (le 1er = pres de l'expediteur)."""
    chemin = (chemin or '').lower()
    if not isinstance(sauts, int) or sauts <= 0 or not chemin or len(chemin) % sauts \
            or any(c not in '0123456789abcdef' for c in chemin):
        return []
    t = len(chemin) // sauts
    if t not in (2, 4, 6):          # 1, 2 ou 3 octets par relais
        return []
    return [chemin[i:i + t] for i in range(0, len(chemin), t)]


def bonne_position(lat, lon):
    return isinstance(lat, (int, float)) and isinstance(lon, (int, float)) and not isinstance(lat, bool) \
        and -90 <= lat <= 90 and -180 <= lon <= 180 and (lat, lon) != (0, 0)


def compacter_publics(noeuds, maintenant=None):
    """La liste publique (58 Mo, 75 000 radios) reduite aux relais places et recents : [[cle, nom, lat, lon, jour], …]."""
    limite = time.strftime('%Y-%m-%d', time.gmtime((maintenant or time.time()) - FRAICHEUR_JOURS * 86400))
    garde = []
    for n in noeuds if isinstance(noeuds, list) else []:
        if not isinstance(n, dict) or n.get('type') not in TYPES_RELAIS:
            continue
        cle, lat, lon, jour = str(n.get('public_key') or '').lower(), n.get('adv_lat'), n.get('adv_lon'), str(n.get('last_advert') or '')[:10]
        if len(cle) < 8 or not bonne_position(lat, lon) or jour < limite:
            continue
        garde.append([cle[:12], str(n.get('adv_name') or '')[:40], round(lat, 5), round(lon, 5), jour])
    return garde


def candidats(ident, connus, publics):
    """Les radios dont l'identifiant commence par ident : celles entendues d'abord (une seule fois par radio)."""
    vus, res = set(), []
    for c in connus:
        if c['cle'].startswith(ident) and c['cle'][:12] not in vus:
            vus.add(c['cle'][:12])
            res.append(c)
    for cle, nom, lat, lon, jour in publics:
        if cle.startswith(ident) and cle[:12] not in vus:
            vus.add(cle[:12])
            res.append({'cle': cle, 'nom': nom, 'lat': lat, 'lon': lon, 'source': 'public', 'vu': jour})
    return res


def centre(connus):
    """La region de la station quand sa position n'est pas reglee : le milieu des radios qu'elle a entendues."""
    places = [c for c in connus if bonne_position(c.get('lat'), c.get('lon'))]
    if not places:
        return None
    lats, lons = sorted(c['lat'] for c in places), sorted(c['lon'] for c in places)
    return {'lat': lats[len(lats) // 2], 'lon': lons[len(lons) // 2]}


def retrouver(chemin, sauts, connus, publics, station=None):
    """Le trajet d'un message : une etape par relais, de l'expediteur vers la station.
    connus : [{cle, nom, lat, lon, source: 'entendu'}] ; publics : sortie de compacter_publics ;
    station : {lat, lon} ou None. Chaque etape : {id, nom, lat, lon, source, certitude, km} (inconnue : nom vide).
    Parmi tous les relais possibles a chaque etape, on garde la chaine la plus courte d'un bout a l'autre (un
    message ne fait pas de zigzags de 100 km) ; une radio entendue par la station compte BONUS_ENTENDU km de moins."""
    idents = decouper(chemin, sauts)
    station = station if station and bonne_position(station.get('lat'), station.get('lon')) else None
    depart = station or centre(connus)
    # On remonte depuis la station : l'etape 0 est le dernier relais (celui que la station a entendu)
    etats = [((depart['lat'], depart['lon']), 0.0, None, 0)] if depart else None   # (position, cout, chaine, ecart)
    choix = []          # par etape : la liste des candidats places (pour dire « probable »)
    noms_seuls = []     # par etape : les candidats sans position (on a au moins leur nom)
    for k, ident in enumerate(reversed(idents)):
        tous = candidats(ident, connus, publics)
        places = [c for c in tous if bonne_position(c.get('lat'), c.get('lon'))]
        noms_seuls.append([c for c in tous if c not in places])
        if etats is None:
            # Sans aucun repere (station sans position, rien d'entendu) : on part de tous les candidats
            choix.append(places)
            if places:
                etats = [((c['lat'], c['lon']), 0.0, ((k, c),), 0) for c in places]
            continue
        nouveaux, retenus = [], []
        for c in places:
            meilleur = None
            for pos, cout, ch, ecart in etats:
                d = km({'lat': pos[0], 'lon': pos[1]}, c)
                if d > SAUT_MAX_KM * (ecart + 1):
                    continue
                total = cout + d - (BONUS_ENTENDU if c['source'] == 'entendu' else 0)
                if meilleur is None or total < meilleur[1]:
                    meilleur = ((c['lat'], c['lon']), total, (ch or ()) + ((k, c),), 0)
            if meilleur:
                nouveaux.append(meilleur)
                retenus.append(c)
        choix.append(retenus)
        if nouveaux:
            # Les chaines qui laissent cette etape inconnue restent possibles, mais elles paient PENALITE_INCONNU
            # (sinon, laisser de cote un relais pourtant connu ferait souvent la chaine la plus courte)
            etats = nouveaux + [(pos, cout + PENALITE_INCONNU, ch, ecart + 1) for pos, cout, ch, ecart in etats]
            etats = sorted(etats, key=lambda e: e[1])[:MAX_CHAINES]
        else:
            etats = [(pos, cout, ch, ecart + 1) for pos, cout, ch, ecart in etats]
    # La meilleure chaine : la plus courte (penalites comprises)
    pris = {}
    if etats:
        meilleure = min(etats, key=lambda e: e[1])
        pris = dict(meilleure[2] or ())
    etapes, voisin, ecart = [], depart, 1
    for k, ident in enumerate(reversed(idents)):
        e = {'id': ident, 'nom': '', 'lat': None, 'lon': None, 'source': '', 'certitude': '', 'km': None}
        c = pris.get(k)
        if c:
            # « sur » : aucun autre relais avec ce debut d'identifiant a portee de l'etape voisine retenue
            autres = [x for x in choix[k] if x is not c and (voisin is None or km(voisin, x) <= SAUT_MAX_KM * ecart)]
            e.update(nom=c['nom'], lat=c['lat'], lon=c['lon'], source=c['source'], certitude='probable' if autres else 'sur')
            voisin, ecart = {'lat': c['lat'], 'lon': c['lon']}, 1
        else:
            ecart += 1
        if not c and noms_seuls[k]:
            # Entendu, mais sans position annoncee : on a au moins son nom
            c = noms_seuls[k][0]
            e.update(nom=c['nom'], source=c['source'], certitude='sur' if len(noms_seuls[k]) == 1 and not choix[k] else 'probable')
        etapes.append(e)
    etapes.reverse()
    # Distance depuis l'etape situee precedente
    precedente, total = None, 0.0
    for e in etapes:
        if e['lat'] is None:
            continue
        if precedente:
            e['km'] = round(km(precedente, e), 1)
            total += e['km']
        precedente = e
    return {'etapes': etapes, 'places': sum(1 for e in etapes if e['lat'] is not None),
            'nommes': sum(1 for e in etapes if e['nom']), 'km': round(total), 'station': station}


def lire_publics(fichier, _cache={}):
    """La liste publique gardee sur la station ({quand, relais}), relue seulement si le fichier a change."""
    try:
        quand = os.path.getmtime(fichier)
    except OSError:
        return {'quand': None, 'relais': []}
    if _cache.get('fichier') != fichier or _cache.get('mtime') != quand:
        try:
            d = json.load(open(fichier, encoding='utf-8'))
            relais = [r for r in d.get('relais', []) if isinstance(r, list) and len(r) == 5]
        except (OSError, ValueError, AttributeError):
            relais = []
        _cache.update(fichier=fichier, mtime=quand, valeur={'quand': quand, 'relais': relais})
    return _cache['valeur']
