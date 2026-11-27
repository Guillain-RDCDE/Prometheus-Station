#!/usr/bin/env python3
"""Banc d'essai de prometheus-admin, par sa porte HTTP (cree le 27/11/2026, revue d'architecture).

    python3 tests/banc_admin.py installation/prometheus-admin [sortie.json]

Le programme est charge tel quel, ses chemins (/srv/prometheus, /var/www/prometheus, /run/prometheus) sont
detournes vers un dossier temporaire, puis on joue des scenarios : chaque adresse sans etre connecte, puis
connecte avec des valeurs absurdes et des valeurs justes. Le resultat (code HTTP, cles de la reponse, fichiers
ecrits et leurs droits) est imprime en JSON stable : on compare celui de l'ancien code et celui du nouveau.
Marche aussi bien avec l'ancien programme (constantes en dur) qu'avec le nouveau (PROMETHEUS_RACINE)."""
import http.client, importlib.machinery, importlib.util, json, os, re, shutil, stat, sys, tempfile, threading, time

PROG = os.path.abspath(sys.argv[1])
os.umask(0o022)   # comme les services de la station : le resultat ne depend pas du compte qui lance le banc
RACINE = tempfile.mkdtemp(prefix='banc-admin-')
os.environ['PROMETHEUS_RACINE'] = RACINE
RACINES = ('/srv/prometheus', '/var/www/prometheus', '/run/prometheus')
for r in RACINES:
    os.makedirs(RACINE + r, exist_ok=True)
# Les dossiers que creent les scripts d'installation (etapes 3 et 10)
for d in ('radio/a-envoyer', 'radio/partis', 'radio/recus', 'radio/ordres', 'radio/reponses', 'messages',
          'communaute', 'panneau', '.admin', 'commande'):
    os.makedirs(RACINE + '/srv/prometheus/' + d, exist_ok=True)
# Quelques themes, comme sur la station
os.makedirs(RACINE + '/var/www/prometheus/themes')
for t in ('neutre', 'nuit'):
    open(RACINE + '/var/www/prometheus/themes/%s.css' % t, 'w').write(':root{--t:%s}' % t)

sys.path.insert(0, os.path.dirname(PROG))
chargeur = importlib.machinery.SourceFileLoader('admin_banc', PROG)
spec = importlib.util.spec_from_loader('admin_banc', chargeur)
admin = importlib.util.module_from_spec(spec)
chargeur.exec_module(admin)
# Ancien code : on detourne a la main chaque chemin ecrit en dur (le nouveau le fait deja par PROMETHEUS_RACINE)
for nom, v in list(vars(admin).items()):
    if isinstance(v, str) and v.startswith(RACINES):
        setattr(admin, nom, RACINE + v)
# Pas de vraie commande systeme pendant le banc (heure, nmcli, vcgencmd...)
class Faux:
    returncode, stdout, stderr = 1, '', ''
admin.subprocess.run = lambda *a, **k: Faux()
os.makedirs(admin.DOSSIER, exist_ok=True)

serveur = admin.ThreadingHTTPServer(('127.0.0.1', 0), admin.Admin)
PORT = serveur.server_address[1]
threading.Thread(target=serveur.serve_forever, daemon=True).start()

COOKIE = ''
resultats = []
VOLATILES = re.compile(r'^(id|cle|heure|maintenant|allumee|restant|verifie|temperature|t|ms)$')


def forme(v, prof=0):
    """Ce qui compte dans une reponse : les cles, les types, les valeurs stables (pas les heures ni les numeros)."""
    if isinstance(v, dict):
        return {k: ('<variable>' if VOLATILES.match(k) else forme(x, prof + 1)) for k, x in sorted(v.items())}
    if isinstance(v, list):
        return [forme(x, prof + 1) for x in v[:5]] + (['… %d' % len(v)] if len(v) > 5 else [])
    return v


def appel(methode, chemin, donnees=None, connecte=True, nom=None, ip='10.42.0.9'):
    c = http.client.HTTPConnection('127.0.0.1', PORT, timeout=40)
    corps = json.dumps(donnees).encode() if donnees is not None else None
    h = {'X-Real-IP': ip, 'Content-Type': 'application/json'}
    if connecte and COOKIE:
        h['Cookie'] = COOKIE
    c.request(methode, chemin, body=corps, headers=h)
    try:
        r = c.getresponse()
    except (http.client.HTTPException, OSError) as e:
        resultats.append({'scenario': nom or '%s %s' % (methode, chemin), 'code': 'PLANTE', 'reponse': type(e).__name__})
        return 0, {}, None
    brut = r.read()
    try:
        d = json.loads(brut or b'{}')
    except ValueError:
        d = brut.decode(errors='replace')
    resultats.append({'scenario': nom or '%s %s%s' % (methode, chemin, '' if connecte else ' (sans connexion)'),
                      'code': r.status, 'reponse': forme(d)})
    return r.status, d, r.getheader('Set-Cookie')


def fichiers():
    """Les fichiers ecrits par le programme, avec leurs droits (pas leur contenu : il porte des heures)."""
    vus = {}
    for d, _, fs in os.walk(RACINE):
        for f in fs:
            p = os.path.join(d, f)
            if '/themes/' in p:
                continue
            vus[re.sub(r'/[0-9a-f]{16}\.json$', '/<numero>.json', p[len(RACINE):])] = oct(stat.S_IMODE(os.stat(p).st_mode))
    return dict(sorted(vus.items()))


GET = ['/verif', '/etat', '/energie', '/sante', '/recherches', '/radio', '/balise', '/mesh/reponse?id=abc',
       '/mesh/resultats?depuis=0', '/mesh/historique?quoi=stats', '/mesh/schema', '/mesh/sauvegardes', '/mesh/atelier',
       '/mesh/trajet?sauts=2&chemin=ec462667',
       '/api/messages', '/api/radio', '/api/panneau', '/api/reglages', '/api/registre', '/api/entraide', '/inconnue']
POST = ['/api/messages/effacer', '/api/messages/vider', '/api/registre/vider', '/api/entraide/vider',
        '/changer', '/theme', '/wifi', '/adresse', '/recherches/epingler', '/recherches/vider', '/radio/envoyer',
        '/mesh/ordre', '/mesh/atelier/suivies', '/radio/code', '/effacer-ecrits', '/reglages', '/panneau', '/energie',
        '/inconnue']

# 1. Sans etre connecte : toute adresse d'administration doit refuser
for p in GET:
    appel('GET', p, connecte=False)
for p in POST:
    appel('POST', p, {}, connecte=False)

# 2. Premier mot de passe, connexion
appel('POST', '/premier', {'nouveau': 'abc'}, nom='premier : trop court')
code, _, cookie = appel('POST', '/premier', {'nouveau': 'essai-du-banc'}, nom='premier : bon')
COOKIE = cookie.split(';')[0] if cookie else ''
appel('POST', '/premier', {'nouveau': 'autre-essai'}, nom='premier : deja choisi')
appel('POST', '/connexion', {'mdp': 'faux'}, connecte=False, nom='connexion : faux', ip='10.42.0.50')
code, _, cookie = appel('POST', '/connexion', {'mdp': 'essai-du-banc'}, connecte=False, nom='connexion : bonne')
COOKIE = cookie.split(';')[0] if cookie else COOKIE

# 3. Connecte : chaque adresse avec une valeur absurde, puis une juste
for p in GET:
    appel('GET', p)
absurdes = {'/changer': {'ancien': 'faux', 'nouveau': 'x'}, '/theme': {'nom': '../../etc/passwd'},
            '/wifi': {'nom': 'x' * 40}, '/adresse': {'nom': 'Pas Bon!'}, '/radio/code': {'code': '12ab'},
            '/reglages': {'section': 'radio', 'valeurs': {'delai': 7}}, '/energie': {'extinction': -3},
            '/panneau': {'texte': 'x' * 20001}, '/mesh/ordre': {'action': 'rm -rf', 'p': {}},
            '/radio/envoyer': {'texte': ''}, '/recherches/epingler': {'lien': 'http://ailleurs', 'titre': 'x'},
            '/mesh/atelier/suivies': {'cartes': 'pas une liste'}}
for p, d in absurdes.items():
    appel('POST', p, d, nom='absurde %s' % p)
justes = [('/theme', {'nom': 'nuit'}), ('/wifi', {'nom': 'Station du banc'}), ('/adresse', {'nom': 'station-banc'}),
          ('/radio/code', {'code': '123456'}), ('/panneau', {'texte': 'Bienvenue *banc*'}),
          ('/energie', {'extinction': 30}), ('/energie', {'sobre': True, 'extinction': 0}),
          ('/reglages', {'section': 'registre', 'valeurs': {'active': True}}),
          ('/reglages', {'section': 'entraide', 'valeurs': {'active': True, 'duree': 24}}),
          ('/reglages', {'section': 'radio', 'valeurs': {'active': True, 'delai': 30}}),
          ('/reglages', {'section': 'ecran', 'valeurs': {'veille': 15}})]
for p, d in justes:
    appel('POST', p, d, nom='juste %s %s' % (p, json.dumps(d, sort_keys=True)))

# 4. Les visiteurs : messages, registre, entraide, recherches
appel('POST', '/api/messages', {'texte': ''}, connecte=False, nom='message vide')
appel('POST', '/api/messages', {'nom': 'Ana', 'texte': 'Bonjour'}, connecte=False, nom='message', ip='10.42.0.11')
appel('POST', '/api/messages', {'nom': 'Ana', 'texte': 'Encore'}, connecte=False, nom='message trop tot', ip='10.42.0.11')
appel('POST', '/api/messages', {'nom': 'Bob', 'texte': 'é' * 200, 'radio': True}, connecte=False,
      nom='message radio trop long', ip='10.42.0.12')
appel('POST', '/api/messages', {'nom': 'Bob', 'texte': 'Par radio', 'radio': True}, connecte=False,
      nom='message radio', ip='10.42.0.13')
code, d, _ = appel('POST', '/api/registre', {'type': 'sauf', 'nom': 'Chloé', 'lieu': 'Mairie', 'message': 'ok'},
                   connecte=False, nom='registre : fiche', ip='10.42.0.14')
cle = d.get('cle', '') if isinstance(d, dict) else ''
ident = d.get('id', '') if isinstance(d, dict) else ''
appel('POST', '/api/registre', {'type': 'autre', 'nom': 'X'}, connecte=False, nom='registre : invalide', ip='10.42.0.15')
appel('POST', '/api/registre/effacer', {'id': ident, 'cle': 'mauvaise'}, connecte=False, nom='registre : effacer, mauvaise cle')
appel('POST', '/api/registre/effacer', {'id': ident, 'cle': cle}, connecte=False, nom='registre : effacer, sa cle')
appel('POST', '/api/entraide', {'type': 'propose', 'categorie': 'eau', 'texte': 'Bidons', 'nom': 'D'}, connecte=False,
      nom='entraide : annonce', ip='10.42.0.16')
appel('POST', '/api/entraide', {'type': 'propose', 'categorie': 'licorne', 'texte': 'x'}, connecte=False,
      nom='entraide : categorie inconnue', ip='10.42.0.17')
appel('POST', '/api/recherche', {'titre': 'Eau potable', 'lien': '/encyclopedies/content/wikipedia_fr/Eau'},
      connecte=False, nom='recherche comptee')
appel('POST', '/api/recherche', {'titre': 'x', 'lien': 'http://ailleurs'}, connecte=False, nom='recherche refusee')
for p in ('/api/messages', '/api/registre', '/api/entraide', '/recherches', '/api/reglages', '/energie'):
    appel('GET', p, nom='apres : GET %s' % p)

# 5. Section Mesh : un ordre, avec une fausse radio qui repond
def fausse_radio():
    dossier = os.path.join(admin.RADIO, 'ordres')
    fin = time.time() + 15
    while time.time() < fin:
        for f in (os.listdir(dossier) if os.path.isdir(dossier) else []):
            o = json.load(open(os.path.join(dossier, f)))
            os.makedirs(os.path.join(admin.RADIO, 'reponses'), exist_ok=True)
            json.dump({'id': o['id'], 'ok': True, 'r': {'action': o['action']}, 'erreur': '', 'heure': time.time()},
                      open(os.path.join(admin.RADIO, 'reponses', o['id'] + '.json'), 'w'))
            os.remove(os.path.join(dossier, f))
            return
        time.sleep(0.1)
threading.Thread(target=fausse_radio, daemon=True).start()
appel('POST', '/mesh/ordre', {'action': 'config-lire', 'p': {}}, nom='mesh : ordre avec reponse')

# 6. Tout effacer, changer le mot de passe
appel('POST', '/effacer-ecrits', {}, nom='effacer les ecrits')
appel('POST', '/changer', {'ancien': 'essai-du-banc', 'nouveau': 'nouveau-banc'}, nom='changer le mot de passe')

sortie = {'resultats': resultats, 'fichiers': fichiers()}
texte = json.dumps(sortie, ensure_ascii=False, indent=1, sort_keys=True)
if len(sys.argv) > 2:
    open(sys.argv[2], 'w').write(texte)
else:
    print(texte)
serveur.shutdown()
shutil.rmtree(RACINE, ignore_errors=True)
print('banc admin : %d scenarios, %d fichiers' % (len(resultats), len(sortie['fichiers'])), file=sys.stderr)
