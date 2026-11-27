# Prometheus Station - essais des modules radio_*.py (Python pur), sans radio (27/11/2026).
#   cd tests/radio && python3 -m unittest -v
import json, os, sys, unittest

import aide  # noqa: F401  (chemins, faux dossier de la station)
import radio_gardefou as gf
import radio_limites as lim
import radio_materiel as mat
import radio_sauvegarde as sauv
import radio_surete as sur
import radio_trajet as traj

PAR_ID = '/dev/serial/by-id/'
TBEAM = PAR_ID + 'usb-1a86_USB_Single_Serial_5A7B012345-if00'
TBEAM_CP = PAR_ID + 'usb-Silicon_Labs_CP2102_USB_to_UART_Bridge_Controller_0001-if00-port0'
TECHO = PAR_ID + 'usb-RAKwireless_TTGO_eink_ABCDEF0123456789-if00'
NRF = PAR_ID + 'usb-Adafruit_NRF52_DK_0011223344556677-if00'


class Limites(unittest.TestCase):
    def test_couper_ne_casse_pas_un_caractere(self):
        self.assertEqual(lim.couper('abc', 10), 'abc')
        self.assertEqual(lim.couper('été', 2), 'é')          # é = 2 octets
        self.assertEqual(lim.couper('été', 3), 'ét')
        self.assertEqual(lim.couper('a😀b', 4), 'a')          # l'emoji (4 octets) ne tient pas entier
        self.assertEqual(lim.couper('a😀b', 5), 'a😀')
        for n in range(12):
            t = lim.couper('éà😀ç ü', n)
            self.assertLessEqual(len(t.encode()), n)
            t.encode('utf-8').decode('utf-8')                  # jamais de caractere casse

    def test_maxi_par_reseau(self):
        self.assertEqual(lim.maxi('meshtastic'), 228)
        self.assertEqual(lim.maxi('meshtastic', 'Un nom long'), 228)
        self.assertEqual(lim.maxi('meshcore', 'Station'), 160 - 7 - 2)
        self.assertEqual(lim.maxi('meshcore', 'Stäti'), 160 - 6 - 2)   # le nom se compte en octets

    def test_nom_radio_en_octets(self):
        self.assertEqual(len(lim.nom_radio('é' * 30, 'meshtastic').encode()), 38)   # 19 « é » = 38 <= 39
        self.assertEqual(lim.nom_radio('  Ma   station ', 'meshcore'), 'Ma station')
        self.assertLessEqual(len(lim.nom_radio('x' * 50, 'meshcore').encode()), 31)
        self.assertEqual(len(lim.nom_radio('x' * 50, 'meshtastic').encode()), 39)

    def test_balise(self):
        moi = {'nom': 'Prométhée', 'lat': 45.123456, 'lon': 5.5, 'batterie': 87}
        t, entier = lim.rendre_balise('{nom} :  {wifi} {position} {batterie} {heure}', 228, moi, '', 'Wifi', '12:00')
        self.assertEqual(t, 'Prométhée : Wifi 45.1235, 5.5000 87 % 12:00')
        self.assertEqual(t, entier)
        t, entier = lim.rendre_balise('é' * 100, 25, {}, 'Secours')
        self.assertEqual(len(t.encode()), 24)
        self.assertEqual(len(entier.encode()), 200)
        self.assertEqual(lim.rendre_balise('{nom} {batterie}', 228, {'batterie': 101}, 'Secours')[0], 'Secours secteur')


class Materiel(unittest.TestCase):
    def test_station_notee_dabord(self):
        self.assertEqual(mat.port_station('usb-1a86_USB_Single_Serial_5A7B012345-if00', [TECHO, TBEAM_CP, TBEAM]), TBEAM)

    def test_station_par_sa_puce(self):
        self.assertEqual(mat.port_station(None, [TECHO, TBEAM]), TBEAM)
        self.assertEqual(mat.port_station('usb-absente-if00', [TECHO, TBEAM_CP]), TBEAM_CP)

    def test_pas_de_station_jamais_une_carte_d_atelier(self):
        self.assertIsNone(mat.port_station(None, [TECHO, NRF]))
        self.assertIsNone(mat.port_station('usb-absente-if00', [TECHO]))
        self.assertIsNone(mat.port_station(None, []))

    def test_autres_ports(self):
        self.assertEqual(mat.autres_ports(TBEAM, [TBEAM, TECHO, NRF]), [NRF, TECHO])
        self.assertEqual(mat.autres_ports(None, [TECHO]), [TECHO])

    def test_serie(self):
        self.assertEqual(mat.serie_de(TECHO), 'ABCDEF0123456789')
        self.assertIsNone(mat.serie_de(TBEAM))                 # 10 chiffres : trop court pour un numero de serie
        self.assertIsNone(mat.serie_de('/dev/serial/by-id/usb-1a86_USB_Single_Serial_5A7B0123-if00'))
        self.assertEqual(mat.serie_de('x_0011223344aa-if02'), '0011223344AA')
        self.assertIsNone(mat.serie_de(None))

    def test_info_meshtastic(self):
        sortie = ('Connected to radio\nOwner: Prometheus Station (Prom)\nMy info: {"myNodeNum": 1}\n'
                  'Metadata: { "firmwareVersion": "2.7.11.ee68575", "hwModel": "TBEAM" }\n')
        self.assertEqual(mat.info_meshtastic(sortie), {'nom': 'Prometheus Station', 'version': '2.7.11.ee68575',
                                                       'materiel': 'TBEAM'})
        self.assertEqual(mat.info_meshtastic('Error: timed out')['nom'], '')

    def test_adresse_ble_mac_plus_2(self):
        self.assertEqual(mat.adresse_ble('24:6f:28:aa:bb:cc'), '24:6F:28:AA:BB:CE')
        self.assertEqual(mat.adresse_ble('24:6f:28:aa:bb:ff'), '24:6F:28:AA:BC:01')   # retenue
        self.assertEqual(mat.adresse_ble('ff:ff:ff:ff:ff:ff'), '00:00:00:00:00:01')   # tour complet
        self.assertEqual(mat.lire_mac('Chip is ESP32\nMAC: 24:6f:28:aa:bb:cc\n'), '24:6f:28:aa:bb:cc')

    def test_table_des_partitions(self):
        def entree(type_, sous, adresse, taille, nom):
            return b'\xaa\x50' + bytes([type_, sous]) + adresse.to_bytes(4, 'little') + taille.to_bytes(4, 'little') \
                + nom.encode().ljust(16, b'\0') + b'\0' * 4
        table = entree(1, 2, 0x9000, 0x5000, 'nvs') + entree(0, 0x10, 0x10000, 0x300000, 'app0') \
            + entree(1, 0x82, 0x310000, 0xF0000, 'spiffs') + b'\xff' * 32
        self.assertEqual(mat.partition_donnees(table), (0x310000, 0xF0000))
        self.assertEqual(mat.partition_donnees(entree(1, 0x83, 0x3A0000, 0x60000, 'littlefs')), (0x3A0000, 0x60000))
        self.assertIsNone(mat.partition_donnees(entree(1, 2, 0x9000, 0x5000, 'nvs') + b'\xff' * 64))
        self.assertIsNone(mat.partition_donnees(b''))


class Sauvegarde(unittest.TestCase):
    def setUp(self):
        aide.preparer()

    def test_format_meshcore_aller_retour(self):
        s = aide.courir(sauv.lire_meshcore(aide.FauxMeshCore('Station')))
        self.assertEqual(s['nom'], 'Station')
        self.assertEqual(s['autres']['telemetry_mode_base'], 2)          # « autres » garde (l'outil l'oubliait)
        self.assertEqual(s['autres']['multi_acks'], 1)
        self.assertEqual(s['cle'], bytes(range(64)).hex())
        self.assertEqual(s['canaux'], [{'index': 0, 'nom': 'Public', 'secret': '01' * 16}])
        self.assertEqual(len(s['contacts']), 1)
        nom = sauv.ranger(sauv.MESH, 'meshcore', 'json', s, 'avant : essai')
        f = os.path.join(sauv.MESH, nom)
        self.assertEqual(aide.mode(f), 0o600)
        relu = aide.lire_json(f)
        self.assertEqual(dict(relu, raison=None), dict(s, raison=None))
        self.assertEqual(relu['raison'], 'avant : essai')
        infos = sauv.autres_a_remettre({'name': 'X', 'multi_acks': 0, 'manual_add_contacts': 0}, relu['autres'])
        self.assertEqual(infos['multi_acks'], 1)
        self.assertIs(infos['manual_add_contacts'], True)
        self.assertEqual(infos['name'], 'X')

    def test_ranger_une_regle_par_dossier(self):
        for i in range(35):
            sauv.ranger(sauv.MESH, 'meshtastic', 'yaml', 'owner: X\n', 'avant : %d' % i)
        self.assertEqual(len(sauv.datees(sauv.MESH, 'meshtastic', 'yaml')), 30)
        self.assertFalse(os.path.exists(os.path.join(sauv.MESH, 'meshtastic-dernier.yaml')))
        liste = sauv.liste(sauv.MESH)
        self.assertEqual(len(liste), 30)
        self.assertTrue(all(x['reseau'] == 'meshtastic' and x['raison'].startswith('avant : ') for x in liste))
        for i in range(12):
            sauv.ranger(sauv.OUTIL, 'meshtastic', 'yaml', 'owner: X\n')
            sauv.ranger(sauv.OUTIL, 't-echo-ABC-meshtastic', 'yaml', 'owner: T\n')
        self.assertEqual(len(sauv.datees(sauv.OUTIL, 'meshtastic', 'yaml')), 10)
        self.assertEqual(len(sauv.datees(sauv.OUTIL, 't-echo-ABC-meshtastic', 'yaml')), 10)
        self.assertEqual(aide.lire(os.path.join(sauv.OUTIL, 'meshtastic-dernier.yaml')), 'owner: X\n')
        self.assertEqual(aide.mode(os.path.join(sauv.OUTIL, 'meshtastic-dernier.yaml')), 0o600)

    def test_liste_ignore_les_temporaires(self):
        sauv.ranger(sauv.MESH, 'meshcore', 'json', {'nom': 'A'}, 'avant : nom')
        aide.ecrire(os.path.join(sauv.MESH, 'meshcore-2026.json.123-4.tmp'), '{')
        self.assertEqual([x['raison'] for x in sauv.liste(sauv.MESH)], ['avant : nom'])


class Surete(unittest.TestCase):
    CLE = 'base64:' + 'A' * 43 + '='

    def test_masquer_sorties_reelles(self):
        cas = {
            # meshtastic --configure (2.7.11)
            'Setting channel url to https://meshtastic.org/e/#CgcSAQE6AggNEg4IARA4QANIAVAeaAHABgE': 'CgcSAQE6',
            # meshtastic --info
            'Primary channel URL: https://meshtastic.org/e/#CgMSAQESBggBQANIAQ': 'CgMSAQ',
            'Complete URL (includes all channels): https://meshtastic.org/e/?add=true#CgMSAQESBg': 'CgMSAQESBg',
            'Preferences: { "security": { "publicKey": "Zm9vYmFyYmF6cXV4Zm9vYmFyYmF6cXV4Zm9vYmFyYmE=", '
            '"privateKey": "c2VjcmV0c2VjcmV0c2VjcmV0c2VjcmV0c2VjcmV0c2U=", "adminKey": '
            '["YWRtaW5hZG1pbmFkbWluYWRtaW5hZG1pbmFkbWluYWQ=", "YmJiYmJiYmJiYmJiYmJiYmJiYmJiYmJiYmJiYmJiYmI="] } }':
                'c2VjcmV0',
            '  Index 1: SECONDARY psk=secret { "psk": "q83vEjRWeJq83vEjRWeJqw==", "name": "Equipe" }': 'q83vEjRW',
            # meshtastic --export-config (YAML)
            'security:\n  privateKey: base64:c2VjcmV0c2VjcmV0c2VjcmV0\n  adminKey:\n  - base64:YWRtaW5hZG1pbg==': 'c2VjcmV0',
            'channel_url: https://meshtastic.org/e/#CgcSAQE6AggN': 'CgcSAQE6',
            # meshtastic --set
            'Set security.private_key to base64:c2VjcmV0c2VjcmV0': 'c2VjcmV0',
            # MeshCore (dictionnaires imprimes)
            "{'index': 1, 'nom': 'Equipe', 'secret': '00112233445566778899aabbccddeeff'}": '0011223344',
            "{'channel_name': 'Equipe', 'channel_secret': b'\\x01\\x02\\x03'}": 'x01',
            "{'cle': '" + 'ab' * 64 + "'}": 'abab',
            'cle privee ' + 'cd' * 64: 'cdcd',
            # repeteur MeshCore
            'password motdepasse123': 'motdepasse123',
            # contact Meshtastic
            'Contact URL: https://meshtastic.org/v/#CgsKCSE0ZGRm': 'CgsKCSE0',
        }
        for texte, secret in cas.items():
            masque = sur.masquer(texte)
            self.assertNotIn(secret, masque, texte)
            self.assertIn(sur.MASQUE, masque, texte)

    def test_masquer_laisse_le_reste(self):
        for t in ('Setting device owner to Prometheus Station', '== Remise de la sauvegarde meshtastic-2026.yaml',
                  'radio : 869.618 MHz, 62.5 kHz, SF8, CR8', 'Owner: Station (Prom)', 'Connected to radio',
                  'canal 0 : LongFast'):
            self.assertEqual(sur.masquer(t), t)

    def test_ecrire_prive(self):
        aide.preparer()
        f = os.path.join(aide.RADIO, 'prive.json')
        os.umask(0o022)
        sur.ecrire_prive(f, {'cle': b'\x01', 'n': 1})
        self.assertEqual(aide.mode(f), 0o600)
        self.assertEqual(aide.lire_json(f)['n'], 1)

    def test_executer_a_toujours_un_delai(self):
        code, sortie = sur.executer([sys.executable, '-c', 'import time; time.sleep(5)'], 0.5)
        self.assertIsNone(code)
        self.assertIn('délai dépassé', sortie)
        self.assertEqual(sur.executer([sys.executable, '-c', 'print(1)'], 10), (0, '1\n'))
        self.assertIsNone(sur.executer(['/nexiste/pas'], 5)[0])

    def test_courir_a_un_delai(self):
        import asyncio

        async def sans_fin():
            await asyncio.sleep(100)
        with self.assertRaises(asyncio.TimeoutError):
            sur.courir(sans_fin(), 0.2)


class Horloge:
    def __init__(self):
        self.t = 1_800_000_000.0

    def __call__(self):
        return self.t


class GardeFou(unittest.TestCase):
    """La machine a etats du garde-fou (horloge factice) ; la meme pour les deux reseaux."""

    def setUp(self):
        aide.preparer()
        self.h = Horloge()
        self.demandes = []
        self.accepte = True
        self.g = gf.GardeFou(os.path.join(aide.RADIO, 'garde-fou.json'), self.demander, self.h, dire=lambda *a: None)

    def demander(self, ordre, contenu):
        self.demandes.append((ordre, json.loads(contenu)))
        return self.accepte

    def avancer(self, secondes, repond, pas=1):
        fin = self.h.t + secondes
        while self.h.t < fin:
            self.h.t += pas
            self.g.verifier(repond)

    def test_les_deux_reseaux_silence_puis_une_seule_demande(self):
        for reseau, fichier in (('meshtastic', 'meshtastic-2026-11-27-100000.yaml'),
                                ('meshcore', 'meshcore-2026-11-27-100000.json')):
            self.demandes.clear()
            self.g.armer(fichier, 'risque', reseau)
            self.avancer(30, False)                 # ecriture en cours : rien
            self.g.confirmer()
            self.avancer(179, False)
            self.assertEqual(self.demandes, [], reseau)
            self.avancer(5, False)
            self.assertEqual(len(self.demandes), 1, reseau)
            self.assertEqual(self.demandes[0][0], 'restaurer')
            self.assertEqual(self.demandes[0][1]['fichier'], fichier)
            self.assertTrue(self.demandes[0][1]['auto'])
            self.avancer(300, False)                # pas de deuxieme demande tout de suite
            self.assertEqual(len(self.demandes), 1, reseau)
            g = self.g.lire()
            self.assertEqual(g['etat'], 'restauration-demandee')
            self.assertTrue(gf.attend_remise(g, fichier, self.demandes[0][1]['garde_fou']))
            self.avancer(5, True)                   # la radio revient : on oublie
            self.assertIsNone(self.g.lire())
            self.assertFalse(gf.attend_remise(self.g.lire(), fichier))

    def test_radio_revenue_on_oublie(self):
        self.g.armer('meshcore-x.json', 'code Bluetooth', 'meshcore')
        self.g.confirmer()
        self.avancer(10, True)                      # elle redemarre peut-etre encore : on attend RETOUR s
        self.assertIsNotNone(self.g.lire())
        self.avancer(15, True)
        self.assertIsNone(self.g.lire())
        self.avancer(400, False)
        self.assertEqual(self.demandes, [])

    def test_demande_non_deposee_reste_et_se_redemande(self):
        self.accepte = False
        self.g.armer('meshtastic-x.yaml', 'config.device.serial_enabled', 'meshtastic')
        self.g.confirmer()
        self.avancer(200, False)
        self.assertEqual(len(self.demandes), 1)
        self.assertEqual(self.g.lire()['etat'], 'surveille')    # rien d'oublie
        self.avancer(61, False)
        self.assertEqual(len(self.demandes), 2)                  # reessai une minute plus tard
        self.accepte = True
        self.avancer(61, False)
        self.assertEqual(len(self.demandes), 3)
        self.assertEqual(self.g.lire()['etat'], 'restauration-demandee')

    def test_remise_sans_effet_redemandee_puis_abandon(self):
        self.g.armer('meshtastic-x.yaml', 'risque', 'meshtastic')
        self.g.confirmer()
        self.avancer(185, False)
        self.assertEqual(len(self.demandes), 1)
        self.avancer(gf.REDEMANDER + 5, False)
        self.assertEqual(len(self.demandes), 2)
        self.avancer(2 * (gf.REDEMANDER + 5), False)
        self.assertEqual(len(self.demandes), 3)
        self.avancer(gf.REDEMANDER + 5, False)
        self.assertEqual(len(self.demandes), 3)
        self.assertEqual(self.g.lire()['etat'], 'abandon')      # garde pour la page
        self.avancer(30, True)
        self.assertIsNone(self.g.lire())

    def test_en_cours_trop_longtemps_devient_surveille(self):
        self.g.armer('meshtastic-x.yaml', 'risque', 'meshtastic')    # programme arrete pendant l'ecriture
        self.avancer(gf.EN_COURS_MAX + gf.ATTENTE + 5, False)
        self.assertEqual(len(self.demandes), 1)


if __name__ == '__main__':
    unittest.main()


class Trajet(unittest.TestCase):
    # Positions fictives (une region de 400 km de large) et deux homonymes lointains
    CONNUS = [{'cle': '8784aa', 'nom': 'Relais-Nord', 'lat': 47.579, 'lon': 1.342, 'source': 'entendu'},
              {'cle': '2667bb', 'nom': 'Relais-Ville', 'lat': 46.669, 'lon': 1.568, 'source': 'entendu'},
              {'cle': 'a204cc', 'nom': 'Relais-Est', 'lat': 46.793, 'lon': 2.153, 'source': 'entendu'},
              {'cle': 'd45cdd', 'nom': 'Sans position', 'lat': None, 'lon': None, 'source': 'entendu'}]
    PUBLICS = [['ec4611', 'Relais-Cap', 48.4237, -1.481, '2026-11-27'],
               ['984022', 'Relais-Mont', 48.4214, -0.84729, '2026-11-27'],
               ['8784ee', 'Homonyme-Loin', 45.9281, 9.0188, '2026-11-26'],     # meme debut que Relais-Nord, a 600 km
               ['2667ff', 'Homonyme-Tres-Loin', 37.7736, -81.2187, '2026-11-15']]  # meme debut que Relais-Ville, sur un autre continent

    def test_decouper(self):
        self.assertEqual(traj.decouper('95a28226', 4), ['95', 'a2', '82', '26'])
        self.assertEqual(traj.decouper('9547873887', 5), ['95', '47', '87', '38', '87'])
        self.assertEqual(traj.decouper('95478738', 2), ['9547', '8738'])
        self.assertEqual(traj.decouper('954787', 1), ['954787'])          # 3 octets par relais
        self.assertEqual(traj.decouper('', 3), [])
        self.assertEqual(traj.decouper('95a2', 0), [])
        self.assertEqual(traj.decouper('95a28', 2), [])          # longueur impossible
        self.assertEqual(traj.decouper('zz', 1), [])            # pas de l'hexadecimal
        self.assertEqual(traj.decouper('9547873887', 1), [])    # 5 octets par relais : impossible

    def test_retrouve_le_plus_proche_et_le_dit(self):
        r = traj.retrouver('ec469840d45c8784a2042667', 6, self.CONNUS, self.PUBLICS)
        noms = [e['nom'] for e in r['etapes']]
        self.assertEqual(noms, ['Relais-Cap', 'Relais-Mont', 'Sans position', 'Relais-Nord', 'Relais-Est', 'Relais-Ville'])
        e = {x['nom']: x for x in r['etapes']}
        self.assertEqual(e['Relais-Nord']['source'], 'entendu')        # pas l'homonyme lointain
        self.assertEqual(e['Relais-Nord']['certitude'], 'sur')         # l'homonyme est a plus de 300 km
        self.assertEqual(e['Relais-Mont']['source'], 'public')
        self.assertIsNone(e['Sans position']['lat'])
        self.assertEqual(r['places'], 5)
        self.assertEqual(r['nommes'], 6)
        self.assertIsNone(r['etapes'][0]['km'])                      # le premier : pas de distance
        self.assertAlmostEqual(e['Relais-Mont']['km'], 47, delta=2)
        self.assertGreater(r['km'], 250)

    def test_homonymes_proches_probable(self):
        publics = self.PUBLICS + [['2667ab', 'Autre relais proche', 46.70, 1.6, '2026-11-27']]
        r = traj.retrouver('2667', 1, self.CONNUS, publics)
        self.assertEqual(r['etapes'][0]['nom'], 'Relais-Ville')     # le plus proche du centre des radios entendues
        self.assertEqual(r['etapes'][0]['certitude'], 'probable')

    def test_pas_de_zigzag(self):
        # Identifiants d'un octet : « b8 » est une radio entendue a 150 km de la route, ou un relais public sur la route
        connus = self.CONNUS + [{'cle': 'b8aa', 'nom': 'Entendu loin', 'lat': 47.9, 'lon': 3.4, 'source': 'entendu'}]
        r = traj.retrouver('87b826', 3, connus, [['b8bb', 'Sur la route', 47.15, 1.45, '2026-11-27']])
        self.assertEqual([e['nom'] for e in r['etapes']], ['Relais-Nord', 'Sur la route', 'Relais-Ville'])
        self.assertEqual(r['etapes'][1]['certitude'], 'probable')   # l'autre restait a portee

    def test_inconnu_trop_loin(self):
        r = traj.retrouver('99', 1, self.CONNUS, [['99aa', 'Tres loin', 10.0, 10.0, '2026-11-27']])
        self.assertEqual(r['etapes'][0]['nom'], '')
        self.assertEqual(r['places'], 0)

    def test_position_de_la_station(self):
        # La station reglee loin de la region : des deux relais « 2667 », c'est celui pres d'elle
        r = traj.retrouver('2667', 1, [], self.PUBLICS + [['2667cc', 'Pres de la station', 48.4, -1.4, '2026-11-27']],
                           {'lat': 48.39, 'lon': -1.49})
        self.assertEqual(r['etapes'][0]['nom'], 'Pres de la station')
        self.assertEqual(r['station'], {'lat': 48.39, 'lon': -1.49})

    def test_compacter_publics(self):
        noeuds = [{'public_key': 'AABBCCDDEEFF0011', 'type': 2, 'adv_name': 'Relais', 'adv_lat': 46.1, 'adv_lon': -1.1,
                   'last_advert': '2026-11-20T10:00:00.000Z'},
                  {'public_key': 'aabbccdd00', 'type': 1, 'adv_name': 'Compagnon', 'adv_lat': 46.1, 'adv_lon': -1.1,
                   'last_advert': '2026-11-20T10:00:00.000Z'},                      # ne relaie pas
                  {'public_key': 'aabbccdd11', 'type': 2, 'adv_name': 'Sans place', 'adv_lat': 0, 'adv_lon': 0,
                   'last_advert': '2026-11-20T10:00:00.000Z'},
                  {'public_key': 'aabbccdd22', 'type': 3, 'adv_name': 'Vieux', 'adv_lat': 46.1, 'adv_lon': -1.1,
                   'last_advert': '2025-01-01T10:00:00.000Z'},
                  'pas un dict']
        maintenant = 1795800000   # 27/11/2026
        self.assertEqual(traj.compacter_publics(noeuds, maintenant), [['aabbccddeeff', 'Relais', 46.1, -1.1, '2026-11-20']])
        self.assertEqual(traj.compacter_publics({'pas': 'une liste'}), [])

    def test_lire_publics(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            f = os.path.join(d, 'relais.json')
            self.assertEqual(traj.lire_publics(f), {'quand': None, 'relais': []})
            json.dump({'relais': [['aa', 'x', 1.0, 2.0, '2026-11-27'], ['mauvais']]}, open(f, 'w'))
            self.assertEqual(traj.lire_publics(f)['relais'], [['aa', 'x', 1.0, 2.0, '2026-11-27']])
