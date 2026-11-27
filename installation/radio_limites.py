#!/usr/bin/env python3
# Prometheus Station - radio : la taille de ce qui part par radio (27/11/2026).
#
# Une seule fois pour prometheus-radio (qui coupe au moment d'emettre) et prometheus-admin (qui refuse un message
# trop long et montre l'apercu de la balise) : avant, le texte de la balise etait calcule deux fois, a garder pareil
# a la main, et un message mis dans la file sous Meshtastic (228 octets) partait tel quel apres un passage a
# MeshCore (160 octets moins le nom).
# Tout se compte en OCTETS (UTF-8) : un accent en prend 2, un emoji 4. Une coupe ne casse jamais un caractere.
# Python pur (aucune bibliotheque radio) : installe dans /usr/local/lib/prometheus/ par 10-radio.sh.
import time

MAX_MESHTASTIC = 228      # octets par message texte Meshtastic
MAX_MESHCORE = 160        # octets par message MeshCore (MAX_TEXT_LEN) ; sur un canal, « Nom: » part devant
MAX_TEXTE = 500           # un texte recu ou depose n'est jamais garde plus long (caracteres)
# Nom long d'une radio : Meshtastic 40 octets avec le zero final (User.long_name, max_size 40), MeshCore 31
NOM_LONG = {'meshtastic': 39, 'meshcore': 31}
NOM_COURT_MESHTASTIC = 4


def couper(texte, maxi):
    """Le debut du texte qui tient en maxi octets UTF-8, sans couper un caractere en deux."""
    octets = str(texte).encode('utf-8')
    if len(octets) <= maxi:
        return str(texte)
    return octets[:max(0, maxi)].decode('utf-8', 'ignore')


def maxi(reseau, nom=''):
    """Octets au plus dans un message pour le reseau en service. MeshCore met « Nom: » devant un message de canal,
    dans la meme limite : le nom de la station (et ': ') est retire."""
    if reseau == 'meshcore':
        return max(0, MAX_MESHCORE - len(str(nom or '').encode('utf-8')) - 2)
    return MAX_MESHTASTIC


def nom_radio(texte, reseau):
    """Le nom long d'une radio : espaces simplifies, coupe a la limite (en octets) du reseau."""
    return couper(' '.join(str(texte or '').split()), NOM_LONG.get(reseau, NOM_LONG['meshcore']))


def valeurs_balise(moi, nom_secours='', wifi='', heure=None):
    """Les cases que remplit la balise : {nom} {position} {wifi} {heure} {batterie}."""
    moi = moi if isinstance(moi, dict) else {}
    bat = moi.get('batterie')
    return {'nom': moi.get('nom') or nom_secours or '',
            'position': '%.4f, %.4f' % (moi['lat'], moi['lon']) if moi.get('lat') and moi.get('lon') else '',
            'wifi': wifi or '',
            'heure': heure if heure is not None else time.strftime('%H:%M'),
            'batterie': '' if not isinstance(bat, (int, float)) else ('secteur' if bat > 100 else '%d %%' % bat)}


def rendre_balise(texte, limite, moi, nom_secours='', wifi='', heure=None):
    """(texte qui partira, texte entier avant coupe) : cases remplies, espaces simplifies, coupe a limite octets.
    Le meme calcul pour la radio (envoi) et pour la page (apercu des Parametres)."""
    t = str(texte)
    for k, v in valeurs_balise(moi, nom_secours, wifi, heure).items():
        t = t.replace('{%s}' % k, v)
    t = ' '.join(t.split())
    return couper(t, limite), t
