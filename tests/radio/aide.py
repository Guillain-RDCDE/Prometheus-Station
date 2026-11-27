# Prometheus Station - essais de la pile radio : ce que tous les essais partagent (27/11/2026).
#
# Les programmes (prometheus-radio, prometheus-radio-outil, prometheus-admin) sont charges comme des modules,
# leurs chemins (/srv/prometheus, /var/www/prometheus, /run) detournes vers un dossier temporaire.
# Aucune radio, aucune commande du systeme : les essais tournent sur le Mac (python du systeme, fausses
# bibliotheques meshtastic / meshcore) et sur le Pi (environnement /opt/prometheus-radio, vraies bibliotheques).
#
# RADIO_PROGRAMMES=<dossier> : le dossier des programmes a essayer (par defaut ../../installation). Sert a jouer
# les memes essais sur l'ancien code (« avant ») : un essai qui reproduit un defaut doit y echouer.
import asyncio, importlib.machinery, importlib.util, json, os, shutil, sys, tempfile, types

ICI = os.path.dirname(os.path.abspath(__file__))
PROGRAMMES = os.path.abspath(os.environ.get('RADIO_PROGRAMMES') or os.path.join(ICI, '..', '..', 'installation'))
RACINE = os.environ.get('PROMETHEUS_RACINE') or tempfile.mkdtemp(prefix='essai-radio-')
if not os.environ.get('PROMETHEUS_RACINE'):
    import atexit, shutil
    atexit.register(shutil.rmtree, RACINE, True)   # rien ne reste dans /tmp apres les essais
os.environ['PROMETHEUS_RACINE'] = RACINE
if PROGRAMMES not in sys.path:
    sys.path.insert(0, PROGRAMMES)
DETOURNES = ('/srv/prometheus', '/var/www/prometheus', '/run/')
RADIO = RACINE + '/srv/prometheus/radio'
COMMANDE = RACINE + '/srv/prometheus/commande'


def preparer():
    """Remet a neuf l'arborescence de la station dans le dossier temporaire."""
    for d in ('/srv/prometheus', '/var/www/prometheus', '/run'):
        shutil.rmtree(RACINE + d, ignore_errors=True)
    for d in ('srv/prometheus/radio/a-envoyer', 'srv/prometheus/radio/partis', 'srv/prometheus/radio/recus',
              'srv/prometheus/radio/ordres', 'srv/prometheus/radio/reponses', 'srv/prometheus/radio/mesh-sauvegardes',
              'srv/prometheus/radio/sauvegardes', 'srv/prometheus/communaute', 'srv/prometheus/commande',
              'srv/prometheus/.admin', 'srv/prometheus/messages', 'var/www/prometheus/ajouter', 'run/prometheus'):
        os.makedirs(os.path.join(RACINE, d), exist_ok=True)


# ----- Fausses bibliotheques (seulement si les vraies manquent : sur le Pi, les vraies servent)
def _faux_meshcore():
    import importlib.util
    if importlib.util.find_spec('meshcore'):
        return
    import enum
    m = types.ModuleType('meshcore')
    m.EventType = enum.Enum('EventType', 'CONTACTS SELF_INFO CONTACT_MSG_RECV CHANNEL_MSG_RECV BATTERY DEVICE_INFO '
                                         'MSG_SENT NEW_CONTACT ACK LOGIN_SUCCESS LOGIN_FAILED STATUS_RESPONSE TRACE_DATA '
                                         'RX_LOG_DATA TELEMETRY_RESPONSE ACL_RESPONSE CUSTOM_VARS STATS_CORE STATS_RADIO '
                                         'STATS_PACKETS CHANNEL_INFO PATH_RESPONSE PRIVATE_KEY TUNING_PARAMS '
                                         'NEIGHBOURS_RESPONSE ALLOWED_REPEAT_FREQ DEFAULT_FLOOD_SCOPE AUTOADD_CONFIG '
                                         'CONTACT_URI OK ERROR')
    m.MeshCore = object
    sys.modules['meshcore'] = m


_faux_meshcore()
import meshcore  # noqa: E402
EventType = meshcore.EventType


class Ev:
    def __init__(self, type_, payload=None):
        self.type, self.payload = type_, payload if payload is not None else {}


class FauxMeshCore:
    """Une radio MeshCore sans radio : chaque commande est notee ; les reponses utiles a une sauvegarde sont fournies."""

    def __init__(self, nom='Station'):
        self.appels = []
        self.self_info = {'name': nom, 'public_key': 'ab' * 32, 'radio_freq': 869.618, 'radio_bw': 62.5, 'radio_sf': 8,
                          'radio_cr': 8, 'tx_power': 22, 'adv_lat': 0, 'adv_lon': 0, 'manual_add_contacts': 1,
                          'telemetry_mode_base': 2, 'telemetry_mode_loc': 0, 'telemetry_mode_env': 1,
                          'adv_loc_policy': 0, 'multi_acks': 1}
        self.contacts = {}
        self.is_connected = True
        faux = self
        reponses = {
            'send_appstart': lambda: Ev(EventType.SELF_INFO, dict(faux.self_info)),
            'export_private_key': lambda: Ev(EventType.PRIVATE_KEY, {'private_key': bytes(range(64))}),
            'send_device_query': lambda: Ev(EventType.DEVICE_INFO, {'max_channels': 2, 'ver': 'v1.11'}),
            'get_channel': lambda i: Ev(EventType.CHANNEL_INFO, {'channel_name': 'Public' if i == 0 else '',
                                                                  'channel_secret': bytes([i + 1] * 16), 'channel_hash': i}),
            'get_contacts': lambda: Ev(EventType.CONTACTS, {'k1': {'public_key': 'cd' * 32, 'adv_name': 'Ami'}}),
            'get_bat': lambda: Ev(EventType.BATTERY, {'level': 4000}),
            'send_chan_msg': lambda canal, texte: Ev(EventType.MSG_SENT, {}),
        }

        class Commandes:
            def __getattr__(self, nom):
                async def commande(*a, **k):
                    faux.appels.append((nom, a, k))
                    return reponses[nom](*a, **k) if nom in reponses else Ev(EventType.OK, {})
                return commande
        self.commands = Commandes()

    async def ensure_contacts(self, **_):
        return True

    async def disconnect(self):
        self.is_connected = False

    def noms(self):
        return [a[0] for a in self.appels]


# ----- Charger un programme
def charger(nom_programme, alias):
    """Le programme comme module, ses chemins detournes vers RACINE (l'ancien code les ecrit en dur)."""
    chemin = os.path.join(PROGRAMMES, nom_programme)
    chargeur = importlib.machinery.SourceFileLoader(alias, chemin)
    spec = importlib.util.spec_from_loader(alias, chargeur)
    module = importlib.util.module_from_spec(spec)
    chargeur.exec_module(module)
    for k, v in list(vars(module).items()):
        if isinstance(v, str) and v.startswith(DETOURNES) and not v.startswith(RACINE):
            setattr(module, k, RACINE + v)
    return module


def lire(chemin):
    with open(chemin, encoding='utf-8') as f:
        return f.read()


def lire_json(chemin):
    return json.loads(lire(chemin))


def ecrire(chemin, texte):
    with open(chemin, 'w', encoding='utf-8') as f:
        f.write(texte)


def mode(chemin):
    return os.stat(chemin).st_mode & 0o777


def courir(coroutine, delai=10):
    return asyncio.run(asyncio.wait_for(coroutine, delai))
