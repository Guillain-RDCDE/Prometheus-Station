# Prometheus Station - essais de prometheus-radio (le service), sans radio (27/11/2026).
#   cd tests/radio && python3 -m unittest -v
# Chaque essai marque DEFAUT reproduit un defaut releve par la revue du 27/11 : il echoue sur l'ancien code
# (RADIO_PROGRAMMES=<copie de l'ancien code>) et passe sur le nouveau.
import asyncio, glob, json, os, time, unittest
from unittest import mock

import aide

r = aide.charger('prometheus-radio', 'radio_essai')
PAR_ID = '/dev/serial/by-id/'
TBEAM = PAR_ID + 'usb-1a86_USB_Single_Serial_5A7B012345-if00'
TECHO = PAR_ID + 'usb-RAKwireless_TTGO_eink_ABCDEF0123456789-if00'
ORDRES = os.path.join(aide.RADIO, 'ordres')
REPONSES = os.path.join(aide.RADIO, 'reponses')
GARDE_FOU = os.path.join(aide.RADIO, 'garde-fou.json')


def faux_glob(ports):
    vrai = glob.glob

    def g(motif, *a, **k):
        if motif.rstrip('*').rstrip('/') == '/dev/serial/by-id':
            return list(ports)
        return vrai(motif, *a, **k)
    return mock.patch('glob.glob', side_effect=g)


def deposer_ordre(ident, action, p):
    with open(os.path.join(ORDRES, '%d-%s.json' % (time.time() * 1000, ident)), 'w') as f:
        json.dump({'id': ident, 'action': action, 'p': p, 'heure': time.time()}, f)


def reponse(ident):
    with open(os.path.join(REPONSES, ident + '.json')) as f:
        return json.load(f)


def lire(chemin, defaut=None):
    try:
        with open(chemin) as f:
            return json.load(f)
    except OSError:
        return defaut


class Base(unittest.TestCase):
    def setUp(self):
        aide.preparer()
        os.umask(0o022)
        r.journal.clear()
        r.ETAT_ACTUEL = None
        r.derniere_emission = 0
        self.horloge = None
        if hasattr(r, 'GARDE'):
            r.GARDE.horloge = time.time

    def station_meshcore(self, nom='Station'):
        st = r.StationMeshCore('AA:BB:CC:DD:EE:01')
        st.mc = aide.FauxMeshCore(nom)
        st.nom = nom
        return st

    def ordres_meshcore(self, st):
        async def tout():
            await st.traiter_ordres()
            await asyncio.gather(*list(st.taches))
        aide.courir(tout())


class Fichiers(Base):
    def test_DEFAUT_reponse_lisible_par_tous(self):
        """Une reponse peut porter la cle privee (lecture des reglages) : 0600, jamais 0644."""
        r.repondre({'id': 'abc123'}, True, {'config': {'security': {'private_key': 'c2VjcmV0'}}})
        self.assertEqual(aide.mode(os.path.join(REPONSES, 'abc123.json')), 0o600)

    def test_reponse_refus_garde_le_format(self):
        r.repondre({'id': 'x/../1'}, False, erreur='Non')
        self.assertEqual(reponse('x1')['erreur'], 'Non')
        self.assertFalse(reponse('x1')['ok'])


class Port(Base):
    def test_DEFAUT_pas_de_t_beam_jamais_une_carte_d_atelier(self):
        with faux_glob([TECHO]):
            self.assertIsNone(r.trouver_port())

    def test_t_beam_trouvee(self):
        with faux_glob([TECHO, TBEAM]):
            self.assertEqual(r.trouver_port(), TBEAM)


class Emission(Base):
    def test_DEFAUT_message_trop_long_apres_passage_a_meshcore(self):
        """Mis dans la file sous Meshtastic (228 octets), il ne doit pas partir trop long sous MeshCore."""
        st = self.station_meshcore('Station')
        with open(os.path.join(aide.RADIO, 'a-envoyer', '1-m1.json'), 'w') as f:
            json.dump({'id': 'm1', 'texte': 'é' * 114, 'canal': 0, 'a': ''}, f)
        aide.courir(st.emettre())
        envoi = [a for a in st.mc.appels if a[0] == 'send_chan_msg']
        self.assertEqual(len(envoi), 1)
        texte = envoi[0][1][1]
        self.assertLessEqual(len(texte.encode()), 160 - len('Station: '.encode()))
        self.assertTrue(texte and set(texte) == {'é'})       # coupe entre deux caracteres
        self.assertEqual(r.journal[-1]['texte'], texte)


class GardeFouMeshCore(Base):
    def test_DEFAUT_code_bluetooth_arme_le_garde_fou(self):
        """MeshCore : changer le code Bluetooth peut couper la liaison -> sauvegarde, garde-fou, remise demandee."""
        st = self.station_meshcore()
        deposer_ordre('o1', 'config-ecrire', {'valeurs': {'code': 123456}})
        self.ordres_meshcore(st)
        rep = reponse('o1')
        self.assertTrue(rep['ok'], rep)
        sauvegarde = rep['r']['sauvegarde']
        self.assertTrue(os.path.exists(os.path.join(aide.RADIO, 'mesh-sauvegardes', sauvegarde)))
        self.assertIn('set_devicepin', st.mc.noms())
        g = lire(GARDE_FOU)
        self.assertIsNotNone(g, 'pas de garde-fou sous MeshCore')
        self.assertEqual(g['fichier'], sauvegarde)
        # la sauvegarde a bien ete prise AVANT le changement
        self.assertLess(st.mc.noms().index('export_private_key'), st.mc.noms().index('set_devicepin'))

    def test_silence_180_s_une_seule_demande_puis_retour(self):
        st = self.station_meshcore()
        deposer_ordre('o2', 'config-ecrire', {'valeurs': {'radio': {'freq': 869.525, 'bw': 250, 'sf': 11, 'cr': 5}}})
        self.ordres_meshcore(st)
        sauvegarde = reponse('o2')['r']['sauvegarde']
        maintenant = [time.time()]
        r.GARDE.horloge = lambda: maintenant[0]
        commande = os.path.join(aide.COMMANDE, 'radio-restaurer')
        for _ in range(170):
            maintenant[0] += 1
            r.verifier_garde_fou(False)
        self.assertFalse(os.path.exists(commande))
        for _ in range(300):
            maintenant[0] += 1
            r.verifier_garde_fou(False)
        self.assertEqual(aide.lire_json(commande)['fichier'], sauvegarde)
        self.assertEqual(aide.mode(commande), 0o600)
        self.assertEqual(lire(GARDE_FOU)['demandes'], 1)                 # une seule demande
        self.assertEqual(glob.glob(os.path.join(aide.COMMANDE, '*.tmp')), [])
        maintenant[0] += 5
        r.verifier_garde_fou(True)
        self.assertIsNone(lire(GARDE_FOU))

    def test_reglage_sans_risque_sauvegarde_sans_garde_fou(self):
        st = self.station_meshcore()
        deposer_ordre('o3', 'config-ecrire', {'valeurs': {'name': 'Nouveau nom'}})
        self.ordres_meshcore(st)
        rep = reponse('o3')
        self.assertTrue(rep['ok'], rep)
        self.assertTrue(rep['r']['sauvegarde'].startswith('meshcore-'))
        self.assertIsNone(lire(GARDE_FOU))

    def test_ordre_meshtastic_seulement(self):
        st = self.station_meshcore()
        deposer_ordre('o4', 'canaux-lien', {'url': 'https://meshtastic.org/e/#abc'})
        deposer_ordre('o5', 'nimporte', {})
        self.ordres_meshcore(st)
        self.assertIn('Pas possible sous MeshCore', reponse('o4')['erreur'])
        self.assertIn('inconnue', reponse('o5')['erreur'])

    def test_sauvegarde_meshcore_complete(self):
        st = self.station_meshcore()
        deposer_ordre('o6', 'action', {'quoi': 'sauvegarder'})
        self.ordres_meshcore(st)
        nom = reponse('o6')['r']['sauvegarde']
        s = lire(os.path.join(aide.RADIO, 'mesh-sauvegardes', nom))
        self.assertEqual(s['raison'], 'à la demande')
        self.assertEqual(s['autres']['multi_acks'], 1)


class GardeFouMeshtastic(Base):
    """Le chemin commun sous Meshtastic (fonctions de la bibliotheque remplacees : pas de radio)."""

    def setUp(self):
        super().setUp()
        if not hasattr(r, 'PILOTE_MESHTASTIC'):
            self.skipTest('ancien code : pas de chemin commun')
        self.appels = []
        self.vrai = dict(r.ACTIONS_MESHTASTIC)
        r.ACTIONS_MESHTASTIC['config-ecrire'] = lambda p: self.appels.append(('ecrire', p)) or {'redemarre': True}
        r.radio = object()
        self.sauve = mock.patch.object(r, 'sauvegarder_meshtastic_ici',
                                       side_effect=lambda raison: self.appels.append(('sauve', raison)) or 'meshtastic-x.yaml')
        self.sauve.start()

    def tearDown(self):
        self.sauve.stop()
        r.ACTIONS_MESHTASTIC.update(self.vrai)
        r.radio = None

    def test_reglage_risque_sauvegarde_garde_fou_une_demande(self):
        deposer_ordre('t1', 'config-ecrire', {'sections': {'config.device': {'serial_enabled': False, 'role': 'CLIENT'}}})
        r.traiter_ordres_meshtastic()
        rep = reponse('t1')
        self.assertTrue(rep['ok'], rep)
        self.assertEqual([a[0] for a in self.appels], ['sauve', 'ecrire'])
        self.assertEqual(sorted(rep['r']['risques']), ['config.device.role', 'config.device.serial_enabled'])
        g = lire(GARDE_FOU)
        self.assertEqual(g['fichier'], 'meshtastic-x.yaml')
        self.assertFalse(g['en_cours'])
        maintenant = [g['heure']]
        r.GARDE.horloge = lambda: maintenant[0]
        for _ in range(600):
            maintenant[0] += 1
            r.verifier_garde_fou(False)
        self.assertEqual(lire(GARDE_FOU)['demandes'], 1)
        self.assertTrue(aide.lire_json(os.path.join(aide.COMMANDE, 'radio-restaurer'))['auto'])

    def test_delai_d_un_ordre(self):
        r.ACTIONS_MESHTASTIC['position'] = lambda p: time.sleep(3)
        with mock.patch.object(r, 'DELAI_ORDRE', 0.5):
            debut = time.time()
            deposer_ordre('t2', 'position', {'fixe': False})
            r.traiter_ordres_meshtastic()
        self.assertLess(time.time() - debut, 2.5)
        self.assertIn('délai', reponse('t2')['erreur'])

    def test_refus_apres_sauvegarde(self):
        def refuse(p):
            raise r.Refus('Nom de canal : 11 octets au plus.')
        r.ACTIONS_MESHTASTIC['canal'] = refuse
        deposer_ordre('t3', 'canal', {'index': 1, 'nom': 'x' * 20})
        r.traiter_ordres_meshtastic()
        self.assertEqual(reponse('t3')['erreur'], 'Nom de canal : 11 octets au plus.')
        self.assertIsNone(lire(GARDE_FOU))

    def test_radio_absente(self):
        r.radio = None
        deposer_ordre('t4', 'config-lire', {})
        r.traiter_ordres_meshtastic()
        self.assertEqual(reponse('t4')['erreur'], 'La radio ne répond pas.')


class GardeFouAncien(Base):
    def test_DEFAUT_remise_demandee_le_garde_fou_n_oublie_pas(self):
        """Avant : garde-fou.json efface avant meme que la demande soit acceptee (demande perdue = radio perdue)."""
        with open(GARDE_FOU, 'w') as f:
            json.dump({'id': 'g1', 'etat': 'surveille', 'heure': time.time() - 400, 'fichier': 'meshtastic-x.yaml',
                       'raison': 'config.device.serial_enabled', 'reseau': 'meshtastic', 'demandes': 0}, f)
        os.chmod(aide.COMMANDE, 0o500)                  # la demande ne peut pas etre deposee
        try:
            r.verifier_garde_fou(False)
        finally:
            os.chmod(aide.COMMANDE, 0o755)
        self.assertIsNotNone(lire(GARDE_FOU), 'garde-fou oublie alors que la remise n’a pas ete demandee')
        r.verifier_garde_fou(False)                     # tout de suite : pas de rafale de demandes
        if hasattr(r, 'GARDE'):
            r.GARDE.horloge = lambda: time.time() + 70
        r.verifier_garde_fou(False)
        self.assertTrue(os.path.exists(os.path.join(aide.COMMANDE, 'radio-restaurer')))
        self.assertIsNotNone(lire(GARDE_FOU))


@unittest.skipUnless(os.environ.get('ESSAI_PROTOBUF') or __import__('importlib').util.find_spec('meshtastic'),
                     'bibliotheque meshtastic absente (essai fait sur le Pi)')
class VraiProtobufMeshtastic(Base):
    """Sur le Pi : mt_ecrire_config avec les vrais reglages protobuf (la radio, elle, est remplacee)."""

    def test_ecriture_risque_meshtastic(self):
        from meshtastic.protobuf import localonly_pb2

        class Noeud:
            localConfig = localonly_pb2.LocalConfig()
            moduleConfig = localonly_pb2.LocalModuleConfig()
            envoyes = []

            def beginSettingsTransaction(self):
                pass

            def commitSettingsTransaction(self):
                pass

            def _sendAdmin(self, a):
                self.envoyes.append(a)
        n = Noeud()
        r.radio = type('Radio', (), {'localNode': n})()
        try:
            with mock.patch.object(r, 'sauvegarder_meshtastic_ici', return_value='meshtastic-v.yaml'):
                deposer_ordre('p1', 'config-ecrire', {'sections': {'config.security': {'serial_enabled': False}}})
                r.traiter_ordres_meshtastic()
        finally:
            r.radio = None
        rep = reponse('p1')
        self.assertTrue(rep['ok'], rep)
        self.assertEqual(rep['r']['risques'], ['config.security.serial_enabled'])
        self.assertEqual(len(n.envoyes), 1)
        self.assertFalse(n.localConfig.security.serial_enabled)
        self.assertEqual(lire(GARDE_FOU)['fichier'], 'meshtastic-v.yaml')


class Balise(Base):
    def test_balise_identique_pour_la_radio_et_la_page(self):
        admin = aide.charger('prometheus-admin', 'admin_essai')
        with open(os.path.join(aide.RADIO, 'details.json'), 'w') as f:
            json.dump({'moi': {'nom': 'Prométhée', 'lat': 45.1234567, 'lon': 5.9, 'batterie': 77}, 'canaux': []}, f)
        with open(os.path.join(aide.RADIO, 'etat.json'), 'w') as f:
            json.dump({'etat': 'ok', 'nom': 'Prométhée', 'reseau': 'meshcore', 'max': 61}, f)

        class Faux:
            returncode, stdout, stderr = 0, 'Wifi « Été »\n', ''
        r.balise_ssid[0] = 0
        texte = '{nom} — station hors ligne, wifi « {wifi} » {position} {batterie} {heure} ' + 'é' * 40
        with mock.patch('subprocess.run', return_value=Faux()):
            radio = r.rendre_balise(texte, 61)
            page = admin.apercu_balise(texte)
        self.assertEqual(radio, page['apercu'])
        self.assertLessEqual(len(radio.encode()), 61)
        self.assertTrue(page['coupe'])
        self.assertEqual(page['max'], 61)


if __name__ == '__main__':
    unittest.main()
