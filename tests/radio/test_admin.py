# Prometheus Station - essais de la partie radio de prometheus-admin (la page), sans radio (27/11/2026).
#   cd tests/radio && python3 -m unittest -v
import http.client, json, os, threading, time, unittest
from unittest import mock

import aide

admin = aide.charger('prometheus-admin', 'admin_essai_page')
PAR_ID = '/dev/serial/by-id/'
TBEAM = PAR_ID + 'usb-1a86_USB_Single_Serial_5A7B012345-if00'
TECHO = PAR_ID + 'usb-RAKwireless_TTGO_eink_ABCDEF0123456789-if00'


class Page(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        aide.preparer()
        cls.serveur = admin.ThreadingHTTPServer(('127.0.0.1', 0), admin.Admin)
        threading.Thread(target=cls.serveur.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.serveur.shutdown()

    def setUp(self):
        os.umask(0o022)
        for d in ('ordres', 'reponses'):
            os.makedirs(os.path.join(aide.RADIO, d), exist_ok=True)
        os.makedirs(admin.DOSSIER, exist_ok=True)
        self.jeton = 'jeton-essai'
        with open(admin.SESSIONS, 'w') as f:
            json.dump({self.jeton: time.time() + 3600}, f)

    def poster(self, chemin, donnees):
        c = http.client.HTTPConnection('127.0.0.1', self.serveur.server_address[1], timeout=10)
        c.request('POST', chemin, json.dumps(donnees), {'Content-Type': 'application/json',
                                                         'Cookie': 'prometheus=' + self.jeton})
        rep = c.getresponse()
        return rep.status, rep.read()

    def test_DEFAUT_ordre_lisible_par_tous(self):
        """Un ordre peut porter une cle de canal ou un mot de passe : 0600."""
        with mock.patch.object(admin, 'lire_json', return_value={'id': 'x', 'ok': True}):
            admin.ordre_mesh('canal', {'index': 1, 'psk': 'q83vEjRWeJq83vEjRWeJqw=='})
        fichiers = [os.path.join(aide.RADIO, 'ordres', f) for f in os.listdir(os.path.join(aide.RADIO, 'ordres'))]
        self.assertEqual(len(fichiers), 1)
        self.assertEqual(aide.mode(fichiers[0]), 0o600)

    def test_DEFAUT_code_bluetooth_lisible_par_tous(self):
        code, _ = self.poster('/radio/code', {'code': '123456'})
        self.assertEqual(code, 200)
        f = os.path.join(aide.RADIO, 'code-ble')
        self.assertEqual(aide.lire(f), '123456')
        self.assertEqual(aide.mode(f), 0o600)

    def test_port_station_et_radios_branchees(self):
        with open(os.path.join(aide.RADIO, 'reseau.json'), 'w') as f:
            json.dump({'reseau': 'meshtastic'}, f)
        import glob
        vrai = glob.glob
        faux = lambda m, *a, **k: [TBEAM, TECHO] if m.startswith('/dev/serial') else vrai(m, *a, **k)
        with mock.patch('glob.glob', side_effect=faux):
            self.assertEqual(admin.port_station(), os.path.basename(TBEAM))
        with mock.patch('glob.glob', side_effect=lambda m, *a, **k: [TECHO] if m.startswith('/dev/serial') else vrai(m, *a, **k)):
            self.assertEqual(admin.port_station(), '')

    def test_sauvegardes_mesh(self):
        d = os.path.join(aide.RADIO, 'mesh-sauvegardes')
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, 'meshtastic-2026-11-27-100000.yaml'), 'w') as f:
            f.write('# Prometheus Station - avant : canal 1\nowner: X\n')
        with open(os.path.join(d, 'meshcore-2026-11-27-110000.json'), 'w') as f:
            json.dump({'raison': 'avant : nom'}, f)
        liste = sorted(admin.sauvegardes_mesh(), key=lambda x: x['fichier'])
        self.assertEqual([(x['reseau'], x['raison']) for x in liste],
                         [('meshcore', 'avant : nom'), ('meshtastic', 'avant : canal 1')])

    def test_max_selon_le_reseau(self):
        with open(os.path.join(aide.RADIO, 'etat.json'), 'w') as f:
            json.dump({'etat': 'ok', 'reseau': 'meshcore'}, f)
        with mock.patch.object(admin, 'reglages', return_value={'radio': {'active': True, 'qui': 'tous', 'delai': 60}}):
            self.assertLessEqual(admin.etat_radio(True)['max'], 160)


if __name__ == '__main__':
    unittest.main()
