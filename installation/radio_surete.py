#!/usr/bin/env python3
# Prometheus Station - radio : la seule porte pour lancer une commande et pour les secrets (27/11/2026).
#
# Utilise par prometheus-radio (service, utilisateur prometheus), prometheus-radio-outil (root) et prometheus-admin.
#   executer(cmd, delai)     toute commande du systeme a une minuterie (regle du projet) ; jamais d'exception
#   courir(coroutine, delai) un echange asynchrone (MeshCore, Bluetooth) a une duree maximale, lui aussi
#   masquer(texte)           ce qui part dans un journal lisible : jamais une cle, un secret, un lien de canaux
#   ecrire_prive(chemin, d)  un fichier qui peut porter une cle (reponses, ordres) : 0600
# Python pur (aucune bibliotheque radio) : installe dans /usr/local/lib/prometheus/ par 10-radio.sh.
import asyncio, json, re, subprocess

import prometheus_commun as pc

MASQUE = '[masqué]'


# ----- Les commandes
def executer(cmd, delai=30):
    """(code, sortie et erreurs). code None : la commande n'a pas pu etre lancee ou a depasse le delai."""
    try:
        p = subprocess.run(list(cmd), capture_output=True, text=True, errors='replace', timeout=delai)
        return p.returncode, (p.stdout or '') + (p.stderr or '')
    except subprocess.TimeoutExpired:
        return None, 'délai dépassé (%d s) : %s' % (delai, ' '.join(str(c) for c in cmd)[:120])
    except (OSError, subprocess.SubprocessError, ValueError) as e:
        return None, str(e)


def courir(coroutine, delai):
    """Lance un echange asynchrone avec une duree maximale. Leve TimeoutError si elle est depassee
    (l'echange est alors annule : ses « finally » ferment la liaison)."""
    return asyncio.run(asyncio.wait_for(coroutine, delai))


# ----- Les secrets
# Ce que les bibliotheques et la radio ecrivent, et qu'il faut cacher (verifie sur meshtastic 2.7.11, 27/11/2026) :
#   meshtastic --configure : « Setting channel url to https://meshtastic.org/e/#<canaux et leurs cles> »
#   meshtastic --info      : « Primary channel URL: … », « Complete URL (includes all channels): … »,
#                            « Preferences: {… "privateKey": "…", "adminKey": ["…"] …} »
#   meshtastic --export-config (YAML) : privateKey: base64:…, adminKey: [- base64:…], channel_url: …
#   meshtastic --set       : « Set security.private_key to … »
#   MeshCore (dictionnaires imprimes) : 'channel_secret': b'…', 'secret': '…', 'private_key': '…'
_CLES = r'(?:(?:private|public|admin|session)_?(?:key|passkey)s?|password|mot_de_passe|psk|(?:channel_)?secret|cle)'
_MOTIFS = (
    # un lien Meshtastic de canaux (/e/) ou de contact (/v/) porte les cles dans ce qui suit le #
    (re.compile(r'(meshtastic\.org/[ev]/#?)[^\s"\'<>,;)\]}]+', re.I), r'\1' + MASQUE),
    # nom: valeur, nom=valeur, nom to valeur, "nom": "valeur", 'nom': b'…', nom: [ "…" ] (premier element)
    (re.compile(r'''(["']?\b''' + _CLES + r'''\b["']?)(\s*(?:[:=]|\bto\b)\s*)'''
                r'''(\[?\s*(?:b?"[^"]*"|b?'[^']*'|[^\s,}\]'"]+))''', re.I), r'\1\2' + MASQUE),
    # ligne de commande d'un repeteur MeshCore : « password <mot> »
    (re.compile(r'\b(password)(\s+)(?![:=]|to\b)(\S+)', re.I), r'\1\2' + MASQUE),
    # valeurs seules : base64:… (YAML de Meshtastic), longues suites hexadecimales (cle privee MeshCore : 128),
    # longues chaines base64 entre guillemets (cles dans une liste JSON)
    (re.compile(r'base64:[A-Za-z0-9+/=_-]+'), MASQUE),
    (re.compile(r'\b[0-9a-fA-F]{96,}\b'), MASQUE),
    (re.compile(r'''(["'])[A-Za-z0-9+/]{40,}={0,2}\1'''), r'\1' + MASQUE + r'\1'),
)


def masquer(texte):
    """Le texte sans ses secrets (cles, mots de passe, liens de canaux)."""
    t = str(texte)
    for motif, remplacement in _MOTIFS:
        t = motif.sub(remplacement, t)
    return t


def ecrire_prive(chemin, donnees):
    """Un fichier JSON lisible par son seul proprietaire (0600), ecrit d'un coup."""
    pc.ecrire_texte(chemin, json.dumps(donnees, ensure_ascii=False, default=str), 0o600)
