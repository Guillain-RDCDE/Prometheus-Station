#!/usr/bin/env python3
# Prometheus Station - radio : reconnaitre le materiel branche (27/11/2026).
#
# Une seule fois pour prometheus-radio, prometheus-radio-outil et prometheus-admin (avant : 4 copies des marques USB,
# 2 de la lecture du numero de serie, 3 de la lecture de « meshtastic --info »).
# Python pur (aucune bibliotheque radio) : installe dans /usr/local/lib/prometheus/ par 10-radio.sh.
import glob, os, re

PAR_ID = '/dev/serial/by-id'
# Puce USB-serie de la T-Beam de la station : 1a86 = CH9102 (WCH), CP210x (Silicon Labs)
MARQUES_STATION = ('1a86', 'CP210', 'Silicon_Labs')
# Identifiants USB (vendeur) : ponts serie (CP210x, CH34x/CH9102, FTDI, PL2303) : en general une carte ESP32
PONTS_SERIE = {'10c4', '1a86', '0403', '067b'}
ESPRESSIF = '303a'
NORDIC = {'239a', '1915'}                        # chargeur Adafruit des nRF52, Nordic
RASPBERRY = '2e8a'
MAC = re.compile(r'MAC:\s+([0-9a-f]{2}(?::[0-9a-f]{2}){5})')


def ports():
    """Les ports serie branches (chemins complets), tries."""
    return sorted(glob.glob(os.path.join(PAR_ID, '*')))


def port_station(note=None, liste=None):
    """Le port de la T-Beam de la station (chemin complet), ou None.
    D'abord le port note par l'outil radio dans reseau.json (le nom porte son numero de serie USB, qui ne change
    pas), sinon le premier port dont la puce USB-serie est celle de la T-Beam. Jamais « le premier port venu » :
    une carte branchee pour l'atelier (T-Echo, autre puce) n'est jamais prise pour la radio de la station.
    Limite connue : tant qu'aucun port n'est note, une carte d'atelier a puce CH9102/CP210x se confond avec la T-Beam."""
    liste = ports() if liste is None else sorted(liste)
    if note:
        p = os.path.join(PAR_ID, os.path.basename(str(note)))
        if p in liste:
            return p
    return next((p for p in liste if any(m in os.path.basename(p) for m in MARQUES_STATION)), None)


def autres_ports(station, liste=None):
    """Les ports branches autres que celui de la station (T-Echo, cartes de l'atelier)."""
    return [p for p in (ports() if liste is None else sorted(liste)) if p != station]


def serie_de(port):
    """Le numero de serie USB d'une carte, lu dans le nom de son port (le meme quel que soit son logiciel)."""
    m = re.search(r'_([0-9A-Fa-f]{12,})-if\d+$', str(port or ''))
    return m.group(1).upper() if m else None


def info_meshtastic(sortie):
    """Ce que dit « meshtastic --info » : {nom, version, materiel} ('' si absent ; nom '' = la radio n'a pas repondu)."""
    sortie = sortie or ''
    m = re.search(r'Owner: (.+?) \(', sortie)
    v = re.search(r'"firmwareVersion": "([^"]+)"', sortie)
    h = re.search(r'"hwModel": "([^"]+)"', sortie)
    return {'nom': m.group(1) if m else '', 'version': v.group(1) if v else '', 'materiel': h.group(1) if h else ''}


def lire_mac(sortie):
    """L'adresse de la puce, lue dans la sortie d'esptool, ou None."""
    m = MAC.search(sortie or '')
    return m.group(1) if m else None


def adresse_ble(mac):
    """Adresse Bluetooth d'un ESP32 : adresse de la puce + 2 (regle des ESP32), en majuscules."""
    n = (int(str(mac).replace(':', ''), 16) + 2) & 0xFFFFFFFFFFFF
    return ':'.join('%02X' % ((n >> s) & 0xFF) for s in range(40, -1, -8))


def partition_donnees(table):
    """(adresse, taille) de la partition de donnees (spiffs ou littlefs) dans une table de partitions ESP32
    (les octets lus a 0x8000), ou None. Une entree fait 32 octets et commence par AA 50."""
    for i in range(0, len(table) - 31, 32):
        e = table[i:i + 32]
        if e[:2] != b'\xaa\x50':
            break
        if e[2] == 1 and e[3] in (0x82, 0x83):      # type donnees ; sous-type spiffs ou littlefs
            return int.from_bytes(e[4:8], 'little'), int.from_bytes(e[8:12], 'little')
    return None
