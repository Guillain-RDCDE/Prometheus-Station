#!/usr/bin/env python3
# Prometheus Station - ce que tous les programmes de la station doivent dire de la meme facon (27/11/2026).
#
# Avant, chaque programme avait sa copie : ou sont les fichiers, les reglages et leurs valeurs par defaut,
# comment ecrire un fichier sans risque, combien de personnes sont la, si une mise a jour tourne, quelles
# couleurs sont choisies. Les copies avaient commence a diverger (couleurs « neutre » ici, « ocean » la ;
# deux definitions de « personne connectee » ; fichiers temporaires au meme nom pour deux programmes a la fois).
# Tout est ici, une seule fois. Installe dans /usr/local/lib/prometheus/ (par commun.sh, a chaque etape).
#
# Depuis Python :   import prometheus_commun as pc ; pc.reglage('radio', 'active')
# Depuis bash   :   prometheus-commun reglage radio active      (affiche true / false / la valeur)
#                   prometheus-commun personnes | maj-en-cours | theme | usb-voulu | reappliquer-sobre
#                   prometheus-commun chemin /srv/prometheus/...
#
# PROMETHEUS_RACINE (essais seulement) : tous les chemins partent de ce dossier au lieu de « / ».
import json, os, subprocess, sys, threading

RACINE = os.environ.get('PROMETHEUS_RACINE', '').rstrip('/')


def chemin(absolu):
    """Le vrai chemin d'un fichier de la station (decale sous PROMETHEUS_RACINE pendant les essais)."""
    return RACINE + absolu


SRV = chemin('/srv/prometheus')
WEB = chemin('/var/www/prometheus')
RUN = chemin('/run/prometheus')
ADMIN = os.path.join(SRV, '.admin')
COMMUNAUTE = os.path.join(SRV, 'communaute')
REGLAGES = os.path.join(COMMUNAUTE, 'reglages.json')
RADIO = os.path.join(SRV, 'radio')
RELAIS_PUBLICS = os.path.join(RADIO, 'relais-publics.json')   # liste publique des relais MeshCore (radio_trajet)
FOND_CARTE = os.path.join(RADIO, 'fond-carte.json')     # fond de carte hors ligne du trajet (Natural Earth, radio_fond)
COMMANDE = os.path.join(SRV, 'commande')
THEMES = os.path.join(WEB, 'themes')
THEME_ACTIF = os.path.join(WEB, 'theme.css')
THEME_CHOIX = os.path.join(ADMIN, 'theme')
THEME_DEFAUT = 'neutre'                     # les couleurs d'une station neuve (depuis le 25/11/2026)
JOURNAL_MAJ = os.path.join(WEB, 'ajouter', 'maj-systeme.txt')
WIFI_STATION = 'prometheus-wifi'            # nom de la connexion NetworkManager du wifi de la station

CATEGORIES = ['eau', 'nourriture', 'sante', 'abri', 'energie', 'transport', 'outils', 'competences', 'autre']
# Les reglages de la station (Parametres). Toute fonction nouvelle est eteinte au depart.
DEFAUT = {
    'annonce': {'active': False, 'texte': '', 'couleur': 'info', 'defile': True, 'vitesse': 'normale', 'ecran': False},
    'registre': {'active': False, 'lieu': True},
    'entraide': {'active': False, 'categories': CATEGORIES, 'duree': 72},
    'urgence': {'active': False},
    'recherches': {'epingles': []},     # sujets epingles sur l'accueil : [{titre, lien}]
    # Radio reliee au tableau des messages (programme prometheus-radio)
    'radio': {'active': False, 'qui': 'tous', 'delai': 60, 'ecran_minutes': 0},   # ecran : 0 = pas sur l'ecran e-ink
    # Section Mesh : duree de l'historique (jours, 0 = toujours), administration a distance des autres radios,
    # logiciels de toutes les cartes gardes sur la station (sinon : seulement les cartes deja vues ou cochees),
    # trajet des messages MeshCore (bouton « + trajet » dans Messages ; liste publique des relais par internet)
    'mesh': {'historique_jours': 90, 'distance': False, 'toutes_cartes': False, 'trajet': False},
    # Ecran et clavier branches sur la station (etape 11, la « mallette ») : veille en minutes, 0 = jamais
    'ecran': {'active': False, 'veille': 5},
    # Petit ecran e-ink pose sur le Pi (etape 6) : a desactiver s'il n'est pas branche
    'eink': {'active': True},
    # Balise : un message tout fait envoye seul par radio (toutes les 3 h ; au depart seulement si Urgence est allumee)
    'balise': {'active': False, 'texte': '{nom} : station de savoir hors ligne et messages. Wifi ouvert « {wifi} ». {position}',
               'heures': 3, 'canal': 0, 'urgence_seulement': True},
}


# ----- Lire et ecrire un fichier
def lire_json(chemin_fichier, defaut=None):
    """Un fichier JSON, ou la valeur par defaut s'il manque ou s'il est abime."""
    try:
        with open(chemin_fichier, encoding='utf-8') as f:
            return json.load(f)
    except (OSError, ValueError):
        return defaut


def lire_texte(chemin_fichier, defaut=''):
    try:
        with open(chemin_fichier, encoding='utf-8', errors='replace') as f:
            return f.read().strip()
    except OSError:
        return defaut


def ecrire_texte(chemin_fichier, texte, mode=0o644):
    """Ecrit d'un coup : un lecteur voit l'ancien fichier ou le nouveau, jamais un fichier a moitie ecrit.
    Le fichier temporaire porte le numero du programme et du fil : deux ecrivains a la fois ne se melangent pas.
    mode 0o600 pour tout ce qui porte un secret (cles, mots de passe, sessions)."""
    tmp = '%s.%d-%d.tmp' % (chemin_fichier, os.getpid(), threading.get_ident())
    try:
        fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, mode)
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            f.write(texte)
        os.chmod(tmp, mode)          # le umask ne doit pas changer le mode demande
        os.replace(tmp, chemin_fichier)
    except BaseException:
        try:
            os.remove(tmp)
        except OSError:
            pass
        raise


def ecrire_json(chemin_fichier, donnees, mode=0o644):
    ecrire_texte(chemin_fichier, json.dumps(donnees, ensure_ascii=False), mode)


# ----- Les reglages
def reglages():
    """Tous les reglages : ceux enregistres, completes par les valeurs par defaut (une cle inconnue est ignoree)."""
    r = json.loads(json.dumps(DEFAUT))
    lu = lire_json(REGLAGES, {})
    if not isinstance(lu, dict):
        lu = {}
    for section, valeurs in r.items():
        if isinstance(lu.get(section), dict):
            for k in valeurs:
                if k in lu[section]:
                    valeurs[k] = lu[section][k]
    return r


def reglage(section, cle):
    """Un seul reglage. Une section ou une cle qui n'existe pas est une erreur de programmation : KeyError."""
    return reglages()[section][cle]


# ----- Les couleurs
def theme():
    """Le nom des couleurs choisies (un theme qui n'existe plus redevient celui par defaut)."""
    nom = os.path.basename(lire_texte(THEME_CHOIX, THEME_DEFAUT)) or THEME_DEFAUT
    return nom if os.path.isfile(os.path.join(THEMES, nom + '.css')) else THEME_DEFAUT


# ----- Le mode sobre
def reappliquer_sobre():
    """Le mode sobre coupe les prises USB, sauf quand la radio ou l'ecran de la station est active : quand l'un des deux
    change, on lui fait reappliquer le choix en cours (prometheus-sobre le lit, par sobre-demande)."""
    v = lire_texte(os.path.join(ADMIN, 'sobre-demande')) or lire_texte(os.path.join(ADMIN, 'sobre'), 'non')
    ecrire_texte(os.path.join(ADMIN, 'sobre-demande'), 'oui' if v == 'oui' else 'non', 0o600)


def usb_voulu():
    """Le mode sobre doit-il laisser les prises USB allumees (radio ou ecran de la station actifs) ?"""
    r = reglages()
    return r['radio']['active'] is True or r['ecran']['active'] is True


# ----- Les commandes du systeme
def lancer(*commande, delai=10):
    """La sortie d'une commande, ou '' si elle echoue ou depasse le delai (jamais d'exception)."""
    try:
        return subprocess.run(commande, capture_output=True, text=True, timeout=delai).stdout
    except (OSError, subprocess.SubprocessError):
        return ''


def maj_en_cours():
    """Une mise a jour du systeme tourne-t-elle ? Son detail finit par « ### FIN <code> » quand elle est finie,
    meme si l'on est appele par la mise a jour elle-meme, juste avant qu'elle s'arrete."""
    lignes = lire_texte(JOURNAL_MAJ).splitlines()
    if not lignes or lignes[-1].startswith('### FIN'):
        return False
    return lancer('systemctl', 'is-active', 'prometheus-maj-systeme').strip() in ('active', 'activating')


def wifi_station_ouvert():
    return lancer('nmcli', '-g', 'GENERAL.CONNECTION', 'device', 'show', 'wlan0').strip() == WIFI_STATION


def personnes():
    """Combien d'appareils utilisent la station en ce moment (page Parametres ET extinction automatique) :
    les telephones accroches au wifi de la station quand il est ouvert, plus les appareils qui ont une connexion
    ouverte vers une page (port 80) ou a distance (SSH, port 22) et qui ne sont pas sur ce wifi (maison, Tailscale).
    Chaque page interroge la station toutes les minutes : sa connexion reste ouverte entre deux appels."""
    n = 0
    station = wifi_station_ouvert()
    if station:
        n = sum(1 for l in lancer('/usr/sbin/iw', 'dev', 'wlan0', 'station', 'dump').splitlines() if l.startswith('Station'))
    adresses = set()
    for l in lancer('ss', '-Htn', 'state', 'established', '( sport = :80 or sport = :22 )').splitlines():
        champs = l.split()
        if len(champs) >= 4:
            ip = champs[3].rsplit(':', 1)[0].strip('[]')
            if ip.startswith('::ffff:'):
                ip = ip[7:]
            if ip in ('127.0.0.1', '::1') or (station and ip.startswith('10.42.0.')):
                continue        # la station elle-meme, ou un telephone deja compte par le wifi
            adresses.add(ip)
    return n + len(adresses)


# ----- Depuis bash
def principal(args):
    if args[:1] == ['reglage'] and len(args) == 3:
        try:
            v = reglage(args[1], args[2])
        except KeyError:
            print('Reglage inconnu : %s %s' % (args[1], args[2]), file=sys.stderr)
            return 2
        print(json.dumps(v) if isinstance(v, (bool, list, dict)) or v is None else v)
        return 0
    if args == ['personnes']:
        print(personnes())
        return 0
    if args == ['maj-en-cours']:
        return 0 if maj_en_cours() else 1
    if args == ['reappliquer-sobre']:
        reappliquer_sobre()
        return 0
    if args == ['usb-voulu']:
        return 0 if usb_voulu() else 1
    if args == ['theme']:
        print(theme())
        return 0
    if args[:1] == ['chemin'] and len(args) == 2:
        print(chemin(args[1]))
        return 0
    print('Usage : prometheus-commun reglage <section> <cle> | personnes | maj-en-cours | theme | usb-voulu | '
          'reappliquer-sobre | chemin <absolu>',
          file=sys.stderr)
    return 2


if __name__ == '__main__':
    sys.exit(principal(sys.argv[1:]))
