# Prometheus Station - essais de prometheus-radio-outil (root), sans radio ni commande du systeme (27/11/2026).
#   cd tests/radio && python3 -m unittest -v
# Chaque essai marque DEFAUT echoue sur l'ancien code et passe sur le nouveau.
import glob, json, os, sys, threading, time, types, unittest
from unittest import mock

import aide

o = aide.charger('prometheus-radio-outil', 'outil_essai')
PAR_ID = '/dev/serial/by-id/'
TECHO = PAR_ID + 'usb-RAKwireless_TTGO_eink_ABCDEF0123456789-if00'
CLE_PRIVEE = 'base64:' + 'S' * 43 + '='
CLE_PUBLIQUE = 'base64:' + 'P' * 43 + '='


class Faux:
    returncode, stdout, stderr = 0, '', ''


class Base(unittest.TestCase):
    def setUp(self):
        aide.preparer()
        self.dit = []
        o.dire = lambda *m: self.dit.append(' '.join(str(x) for x in m))
        self.ecrire_reseau({'reseau': 'meshtastic', 'port': 'usb-1a86_x-if00'})

    def ecrire_reseau(self, r):
        with open(os.path.join(aide.RADIO, 'reseau.json'), 'w') as f:
            json.dump(r, f)


class Journal(Base):
    def test_DEFAUT_le_journal_cache_les_liens_et_les_cles(self):
        chemin = os.path.join(aide.RACINE, 'var/www/prometheus/ajouter/radio-outil.txt')
        j = o.Journal(chemin)
        j('   Setting channel url to https://meshtastic.org/e/#CgcSAQE6AggNEg4IARA4QANIAVAe')
        j('   Preferences: { "security": { "privateKey": "c2VjcmV0c2VjcmV0c2VjcmV0c2VjcmV0c2VjcmV0c2U=" } }')
        j("   {'index': 1, 'nom': 'Equipe', 'secret': '00112233445566778899aabbccddeeff'}")
        j('   Set security.private_key to base64:c2VjcmV0c2VjcmV0')
        j.f.close()
        texte = aide.lire(chemin)
        for secret in ('CgcSAQE6', 'c2VjcmV0', '0011223344'):
            self.assertNotIn(secret, texte)


class Delais(Base):
    def test_DEFAUT_chaque_commande_a_un_delai(self):
        appels = []

        def run(*a, **k):
            appels.append((a, k))
            return Faux()
        with mock.patch('subprocess.run', side_effect=run), mock.patch('time.sleep'):
            o.arreter_service()
            o.relancer_service()
            o.bluetooth(True)
            o.bluetooth(False)
        self.assertEqual(len(appels), 4)
        for a, k in appels:
            self.assertTrue(k.get('timeout'), 'sans delai : %s' % (a,))

    def test_DEFAUT_echange_meshcore_borne(self):
        """Une radio MeshCore qui ne repond jamais ne bloque plus l'outil (et donc toute la page Radio)."""
        self.ecrire_reseau({'reseau': 'meshcore', 'ble': 'AA:BB:CC:DD:EE:03'})
        with open(os.path.join(aide.RADIO, 'mesh-sauvegardes', 'meshcore-2026-11-27-100000.json'), 'w') as f:
            json.dump({'nom': 'Station', 'canaux': [], 'contacts': []}, f)

        async def jamais(*a, **k):
            await __import__('asyncio').sleep(3600)
        fin = {}

        def lancer():
            try:
                o.action_restaurer(json.dumps({'fichier': 'meshcore-2026-11-27-100000.json'}))
            except Exception as e:
                fin['erreur'] = e
        with mock.patch.object(o, 'meshcore_connecter', jamais), mock.patch.object(o, 'arreter_service'), \
                mock.patch.object(o, 'relancer_service'), mock.patch.object(o, 'bluetooth'), \
                mock.patch.object(o, 'DELAI_MESHCORE', 1, create=True):
            fil = threading.Thread(target=lancer, daemon=True)
            fil.start()
            fil.join(8)
        self.assertFalse(fil.is_alive(), 'l’outil attend sans fin une radio MeshCore muette')
        self.assertIsInstance(fin.get('erreur'), o.Echec)


class CleSurLaLigneDeCommande(Base):
    def test_DEFAUT_la_cle_privee_n_est_pas_dans_ps(self):
        fichier = os.path.join(aide.RADIO, 'sauvegardes', 'meshtastic-dernier.yaml')
        with open(fichier, 'w') as f:
            f.write('owner: Station\nconfig:\n  security:\n    privateKey: %s\n    publicKey: %s\n' % (CLE_PRIVEE, CLE_PUBLIQUE))
        commandes = []

        def mt(*args, **k):
            commandes.append(args)
            return 0, 'security:\n  publicKey: %s\n' % CLE_PUBLIQUE
        with mock.patch.object(o, 'mt', side_effect=mt), mock.patch.object(o, 'attendre_meshtastic', return_value='X'), \
                mock.patch('time.sleep'), mock.patch.object(o, 'poser_cle_privee', create=True) as poser:
            o.restaurer_meshtastic(fichier=fichier)
        for c in commandes:
            self.assertFalse(any(CLE_PRIVEE in str(x) or 'S' * 43 in str(x) for x in c), c)
        poser.assert_called_once()
        self.assertEqual(poser.call_args[0][1], CLE_PRIVEE)

    def test_poser_cle_privee_dans_le_programme(self):
        if not hasattr(o, 'poser_cle_privee'):
            self.fail('ancien code : la cle passe par la ligne de commande')
        ecrit = []

        class Securite:
            private_key = b''

        class Config:
            security = Securite()

            def ListFields(self):
                return [1]

        class Noeud:
            localConfig = Config()

            def writeConfig(self, nom):
                ecrit.append((nom, Noeud.localConfig.security.private_key))

        class Interface:
            def __init__(self, devPath, timeout):
                self.localNode = Noeud()
                self.port = devPath

            def close(self):
                ecrit.append('ferme')
        import base64
        faux = types.ModuleType('meshtastic')
        faux.serial_interface = types.SimpleNamespace(SerialInterface=Interface)
        faux.util = types.SimpleNamespace(fromStr=lambda v: base64.b64decode(v[7:]) if v.startswith('base64:') else v)
        with mock.patch.dict(sys.modules, {'meshtastic': faux, 'meshtastic.serial_interface': faux.serial_interface,
                                           'meshtastic.util': faux.util}):
            o.poser_cle_privee('/dev/ttyACM0', CLE_PRIVEE)
        self.assertEqual(ecrit, [('security', base64.b64decode(CLE_PRIVEE[7:])), 'ferme'])
        with mock.patch.dict(sys.modules, {'meshtastic': faux, 'meshtastic.serial_interface': faux.serial_interface,
                                           'meshtastic.util': faux.util}):
            with self.assertRaises(o.Echec):
                o.poser_cle_privee('/dev/ttyACM0', 'base64:AAAA')     # pas 32 octets


class Restaurer(Base):
    def preparer_restauration(self):
        nom = 'meshtastic-2026-11-27-100000.yaml'
        with open(os.path.join(aide.RADIO, 'mesh-sauvegardes', nom), 'w') as f:
            f.write('owner: Station\n')
        self.faits = []
        self.patches = [mock.patch.object(o, 'arreter_service', side_effect=lambda: self.faits.append('arret')),
                        mock.patch.object(o, 'relancer_service', side_effect=lambda: self.faits.append('relance')),
                        mock.patch.object(o, 'attendre_meshtastic', return_value='Station'),
                        mock.patch.object(o, 'restaurer_meshtastic',
                                          side_effect=lambda **k: self.faits.append(('remise', os.path.basename(k['fichier']))))]
        for p in self.patches:
            p.start()
        return nom

    def tearDown(self):
        for p in getattr(self, 'patches', []):
            p.stop()

    def test_DEFAUT_remise_du_garde_fou_rejouee_apres_retour_de_la_radio(self):
        """Une demande du garde-fou rejouee en retard (radio revenue entre-temps) ne defait pas le nouveau reglage."""
        nom = self.preparer_restauration()
        o.action_restaurer(json.dumps({'fichier': nom, 'auto': True, 'garde_fou': 'g1'}))
        self.assertEqual(self.faits, [])

    def test_remise_du_garde_fou_attendue(self):
        nom = self.preparer_restauration()
        with open(os.path.join(aide.RADIO, 'garde-fou.json'), 'w') as f:
            json.dump({'id': 'g1', 'etat': 'restauration-demandee', 'fichier': nom, 'heure': time.time()}, f)
        o.action_restaurer(json.dumps({'fichier': nom, 'auto': True, 'garde_fou': 'g1'}))
        self.assertEqual(self.faits, ['arret', ('remise', nom), 'relance'])

    def test_remise_demandee_par_la_page(self):
        nom = self.preparer_restauration()
        o.action_restaurer(json.dumps({'fichier': nom}))
        self.assertEqual(self.faits, ['arret', ('remise', nom), 'relance'])


class Divers(Base):
    def test_adresse_ble(self):
        self.ecrire_reseau({'reseau': 'meshtastic', 'mac': '24:6f:28:aa:bb:ff'})
        self.assertEqual(o.adresse_ble(), '24:6F:28:AA:BC:01')

    def test_DEFAUT_sauvegarde_meshcore_de_l_outil_garde_autres(self):
        s = aide.courir(o.meshcore_lire(aide.FauxMeshCore('Station')))
        self.assertEqual(s.get('autres', {}).get('telemetry_mode_base'), 2)

    def test_meshcore_ecrire_remet_autres_et_coupe_le_nom(self):
        mc = aide.FauxMeshCore('X')
        s = {'nom': 'N' * 39, 'freq': 869.6, 'bw': 62.5, 'sf': 8, 'cr': 8, 'canaux': [], 'contacts': [],
             'autres': {'multi_acks': 0, 'telemetry_mode_base': 1, 'manual_add_contacts': None}}
        aide.courir(o.meshcore_ecrire(mc, s))
        nom = [a for a in mc.appels if a[0] == 'set_name'][0][1][0]
        self.assertLessEqual(len(nom.encode()), 31)
        autres = [a for a in mc.appels if a[0] == 'set_other_params_from_infos']
        self.assertEqual(len(autres), 1)
        self.assertEqual(autres[0][1][0]['multi_acks'], 0)

    def test_port_station_jamais_une_carte_d_atelier(self):
        self.ecrire_reseau({'reseau': 'meshtastic'})
        vrai = glob.glob
        with mock.patch('glob.glob', side_effect=lambda m, *a, **k: [TECHO] if m.startswith('/dev/serial') else vrai(m, *a, **k)):
            with self.assertRaises(o.Echec):
                o.port_station()


if __name__ == '__main__':
    unittest.main()
