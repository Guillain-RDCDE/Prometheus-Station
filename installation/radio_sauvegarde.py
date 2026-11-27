#!/usr/bin/env python3
# Prometheus Station - radio : les sauvegardes des reglages des radios (27/11/2026).
#
# Avant : deux facons de ranger (prometheus-radio : 30 copies ; l'outil : 10 copies et un « -dernier ») et deux
# formats MeshCore (celui de l'outil oubliait « autres » : telemetrie, accuses multiples, ajout manuel des contacts,
# que la remise sait pourtant remettre). Ici une seule fonction pour ranger, un seul format, une regle par dossier :
#
#   mesh-sauvegardes/  (utilisateur prometheus, 0700) HISTORIQUE DES CHANGEMENTS : prometheus-radio y range les
#                      reglages pris avant chaque changement fait depuis la section Mesh (et le garde-fou en remet une).
#                      30 copies datees par reseau ; la page les liste (liste()) et peut en remettre une.
#   sauvegardes/       (root seulement, 0700) IDENTITE DES RADIOS : l'outil radio y garde, pour chaque radio, de quoi
#                      la refaire a l'identique apres un effacement (changement de reseau, T-Echo, cartes de l'atelier).
#                      <radio>-dernier.<ext> (celle qu'on remet) + 10 copies datees par radio.
# Chaque fichier est en 0600 : il contient la cle privee de la radio et les secrets de ses canaux.
# Python pur : la lecture d'une radio MeshCore (lire_meshcore) n'importe meshcore qu'au moment de l'appel.
import glob, json, os, time

import prometheus_commun as pc

MESH = os.path.join(pc.RADIO, 'mesh-sauvegardes')
OUTIL = os.path.join(pc.RADIO, 'sauvegardes')
# dossier -> (copies datees gardees par radio, ecrire aussi <radio>-dernier.<ext>)
REGLES = {'mesh-sauvegardes': (30, False), 'sauvegardes': (10, True)}
ENTETE = '# Prometheus Station - '
# MeshCore : reglages « divers » que set_other_params_from_infos sait remettre
AUTRES = ('manual_add_contacts', 'telemetry_mode_base', 'telemetry_mode_loc', 'telemetry_mode_env', 'adv_loc_policy',
          'multi_acks')


def horodatage(quand=None):
    return time.strftime('%Y-%m-%d-%H%M%S', time.localtime(quand))


def ranger(dossier, base, ext, contenu, raison=''):
    """Range une sauvegarde ; renvoie le nom du fichier date. contenu : texte (YAML Meshtastic : la raison devient
    une premiere ligne « # Prometheus Station - <raison> ») ou dictionnaire (JSON : cle « raison »)."""
    garder, dernier = REGLES[os.path.basename(os.path.normpath(dossier))]
    os.makedirs(dossier, mode=0o700, exist_ok=True)
    if isinstance(contenu, dict):
        contenu = dict(contenu, raison=raison) if raison else contenu
        texte = json.dumps(contenu, ensure_ascii=False, indent=1)
    else:
        texte = (ENTETE + raison + '\n' if raison else '') + str(contenu)
    nom = '%s-%s.%s' % (base, horodatage(), ext)
    n = 1
    while os.path.exists(os.path.join(dossier, nom)):     # deux sauvegardes dans la meme seconde
        nom = '%s-%s-%d.%s' % (base, horodatage(), n, ext)
        n += 1
    pc.ecrire_texte(os.path.join(dossier, nom), texte, 0o600)
    if dernier:
        pc.ecrire_texte(os.path.join(dossier, '%s-dernier.%s' % (base, ext)), texte, 0o600)
    for vieux in datees(dossier, base, ext)[:-garder]:
        try:
            os.remove(vieux)
        except OSError:
            pass
    return nom


def datees(dossier, base, ext):
    """Les copies datees d'une radio, de la plus ancienne a la plus recente."""
    return sorted(f for f in glob.glob(os.path.join(dossier, '%s-2*.%s' % (glob.escape(base), ext)))
                  if os.path.basename(f)[len(base) + 1:len(base) + 18].replace('-', '').isdigit())


def raison_de(chemin):
    if chemin.endswith('.json'):
        d = pc.lire_json(chemin, {})
        return d.get('raison', '') if isinstance(d, dict) else ''
    try:
        with open(chemin, encoding='utf-8', errors='replace') as f:
            premiere = f.readline().strip()
    except OSError:
        return ''
    return premiere[len(ENTETE):] if premiere.startswith(ENTETE) else ''


def liste(dossier=MESH):
    """Les sauvegardes d'un dossier, les plus recentes d'abord : [{fichier, heure, raison, reseau}]."""
    res = []
    for f in glob.glob(os.path.join(dossier, '*')):
        nom = os.path.basename(f)
        if nom.endswith('.tmp') or not nom.endswith(('.yaml', '.json')) or not os.path.isfile(f):
            continue
        try:
            heure = os.path.getmtime(f)
        except OSError:
            continue
        res.append({'fichier': nom, 'heure': heure, 'raison': raison_de(f),
                    'reseau': 'meshcore' if nom.startswith('meshcore') else 'meshtastic'})
    return sorted(res, key=lambda x: -x['heure'])


# ----- Le format MeshCore (un seul : prometheus-radio et l'outil radio)
def meshcore(moi, cle, canaux, contacts):
    """Tout ce qu'il faut pour remettre une radio MeshCore comme elle etait (identite comprise).
    moi : SELF_INFO ; cle : cle privee en hexadecimal ('' si la radio la refuse) ; canaux : [{index, nom, secret}]."""
    moi = moi or {}
    return {'nom': moi.get('name', ''), 'freq': moi.get('radio_freq'), 'bw': moi.get('radio_bw'),
            'sf': moi.get('radio_sf'), 'cr': moi.get('radio_cr'), 'tx': moi.get('tx_power'),
            'lat': moi.get('adv_lat'), 'lon': moi.get('adv_lon'),
            'autres': {k: moi.get(k) for k in AUTRES},
            'cle': cle or '', 'canaux': list(canaux or []), 'contacts': list(contacts or [])}


async def lire_meshcore(mc):
    """Lit une radio MeshCore connectee et renvoie sa sauvegarde (format meshcore())."""
    from meshcore import EventType
    r = await mc.commands.send_appstart()
    moi = (r.payload or {}) if r is not None and r.type == EventType.SELF_INFO else (mc.self_info or {})
    cle = await mc.commands.export_private_key()
    info = await mc.commands.send_device_query()
    canaux = []
    for i in range(min(40, (info.payload or {}).get('max_channels') or 8) if info.type == EventType.DEVICE_INFO else 8):
        c = await mc.commands.get_channel(i)
        if c.type == EventType.CHANNEL_INFO and c.payload.get('channel_name'):
            canaux.append({'index': i, 'nom': c.payload['channel_name'], 'secret': c.payload['channel_secret'].hex()})
    contacts = await mc.commands.get_contacts()
    return meshcore(moi, cle.payload.get('private_key').hex() if cle.type == EventType.PRIVATE_KEY else '', canaux,
                    contacts.payload.values() if contacts.type == EventType.CONTACTS else [])


def autres_a_remettre(infos, autres):
    """Les reglages divers a envoyer (set_other_params_from_infos) : ceux de la radio, remplaces par ceux sauvegardes."""
    infos = dict(infos or {})
    infos.update({k: v for k, v in (autres or {}).items() if k in AUTRES and v is not None})
    infos['manual_add_contacts'] = bool(infos.get('manual_add_contacts'))
    return infos
