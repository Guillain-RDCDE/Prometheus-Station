#!/usr/bin/env python3
"""Essais du module commun des programmes (installation/prometheus_commun.py) et des regles « un seul endroit ».

    python3 -m unittest discover -s tests -p 'test_*.py'
"""
import importlib, json, os, re, stat, subprocess, sys, tempfile, threading, unittest

ICI = os.path.dirname(os.path.abspath(__file__))
INSTALLATION = os.path.join(os.path.dirname(ICI), 'installation')
sys.path.insert(0, INSTALLATION)


def lire(p):
    with open(p, encoding='utf-8', errors='replace') as f:
        return f.read()


def charger(racine):
    os.environ['PROMETHEUS_RACINE'] = racine
    import prometheus_commun
    return importlib.reload(prometheus_commun)


class Module(unittest.TestCase):
    def setUp(self):
        self.racine = tempfile.mkdtemp(prefix='essai-commun-')
        self.pc = charger(self.racine)
        for d in (self.pc.ADMIN, self.pc.COMMUNAUTE, self.pc.THEMES, os.path.dirname(self.pc.JOURNAL_MAJ)):
            os.makedirs(d, exist_ok=True)

    def test_chemins_sous_la_racine_d_essai(self):
        self.assertEqual(self.pc.SRV, self.racine + '/srv/prometheus')
        self.assertEqual(self.pc.chemin('/run/x'), self.racine + '/run/x')

    def test_reglages_par_defaut_et_completes(self):
        self.assertIs(self.pc.reglage('radio', 'active'), False)
        self.assertEqual(self.pc.reglage('ecran', 'veille'), 5)
        json.dump({'radio': {'active': True, 'inconnue': 1}, 'ecran': 'abime'}, open(self.pc.REGLAGES, 'w'))
        r = self.pc.reglages()
        self.assertIs(r['radio']['active'], True)
        self.assertNotIn('inconnue', r['radio'])
        self.assertEqual(r['ecran'], {'active': False, 'veille': 5})
        with self.assertRaises(KeyError):
            self.pc.reglage('radio', 'nexistepas')

    def test_reglages_illisibles(self):
        open(self.pc.REGLAGES, 'w').write('{pas du json')
        self.assertEqual(self.pc.reglages(), json.loads(json.dumps(self.pc.DEFAUT)))
        open(self.pc.REGLAGES, 'w').write('[1, 2]')
        self.assertEqual(self.pc.reglage('eink', 'active'), True)

    def test_defaut_jamais_modifie(self):
        r = self.pc.reglages()
        r['entraide']['categories'].append('licorne')
        self.assertNotIn('licorne', self.pc.DEFAUT['entraide']['categories'])

    def test_ecriture_sure_et_mode(self):
        f = os.path.join(self.pc.ADMIN, 'secret')
        self.pc.ecrire_texte(f, 'abc', 0o600)
        self.assertEqual(open(f).read(), 'abc')
        self.assertEqual(stat.S_IMODE(os.stat(f).st_mode), 0o600)
        self.pc.ecrire_json(f + '.json', {'a': 'é'})
        self.assertEqual(stat.S_IMODE(os.stat(f + '.json').st_mode), 0o644)
        self.assertEqual(self.pc.lire_json(f + '.json'), {'a': 'é'})
        self.assertEqual([x for x in os.listdir(self.pc.ADMIN) if x.endswith('.tmp')], [])

    def test_ecriture_echouee_ne_laisse_rien(self):
        f = os.path.join(self.pc.ADMIN, 'x.json')
        with self.assertRaises(TypeError):
            self.pc.ecrire_json(f, {'objet': object()})
        self.assertEqual(os.listdir(self.pc.ADMIN), [])

    def test_ecrivains_simultanes(self):
        f = os.path.join(self.pc.COMMUNAUTE, 'partage.json')
        erreurs = []

        def ecrire(n):
            try:
                for i in range(50):
                    self.pc.ecrire_json(f, {'n': n, 'i': i, 'bourrage': 'x' * 5000})
            except Exception as e:      # pragma: no cover
                erreurs.append(e)
        fils = [threading.Thread(target=ecrire, args=(n,)) for n in range(6)]
        [t.start() for t in fils]
        [t.join() for t in fils]
        self.assertEqual(erreurs, [])
        self.assertEqual(self.pc.lire_json(f)['bourrage'], 'x' * 5000)

    def test_lire_json_defaut(self):
        self.assertEqual(self.pc.lire_json('/nexiste/pas', {'d': 1}), {'d': 1})
        self.assertEqual(self.pc.lire_texte('/nexiste/pas', 'z'), 'z')

    def test_theme(self):
        self.assertEqual(self.pc.theme(), 'neutre')
        open(os.path.join(self.pc.THEMES, 'nuit.css'), 'w').write('')
        open(self.pc.THEME_CHOIX, 'w').write('nuit\n')
        self.assertEqual(self.pc.theme(), 'nuit')
        open(self.pc.THEME_CHOIX, 'w').write('../../etc/passwd')
        self.assertEqual(self.pc.theme(), 'neutre')
        open(self.pc.THEME_CHOIX, 'w').write('ocean')          # un theme qui n'est plus installe
        self.assertEqual(self.pc.theme(), 'neutre')

    def test_maj_en_cours(self):
        self.assertFalse(self.pc.maj_en_cours())               # jamais lancee
        open(self.pc.JOURNAL_MAJ, 'w').write('== x\n### FIN 0\n')
        self.assertFalse(self.pc.maj_en_cours())               # finie

    def test_sobre(self):
        self.pc.reappliquer_sobre()
        f = os.path.join(self.pc.ADMIN, 'sobre-demande')
        self.assertEqual(open(f).read(), 'non')
        self.assertEqual(stat.S_IMODE(os.stat(f).st_mode), 0o600)
        os.remove(f)
        open(os.path.join(self.pc.ADMIN, 'sobre'), 'w').write('oui\n')
        self.pc.reappliquer_sobre()
        self.assertEqual(open(f).read(), 'oui')
        self.assertFalse(self.pc.usb_voulu())
        json.dump({'ecran': {'active': True}}, open(self.pc.REGLAGES, 'w'))
        self.assertTrue(self.pc.usb_voulu())

    def test_ligne_de_commande(self):
        env = dict(os.environ, PROMETHEUS_RACINE=self.racine)
        prog = os.path.join(INSTALLATION, 'prometheus_commun.py')
        sortie = lambda *a: subprocess.run([sys.executable, prog, *a], capture_output=True, text=True, env=env)
        self.assertEqual(sortie('reglage', 'radio', 'active').stdout.strip(), 'false')
        self.assertEqual(sortie('reglage', 'ecran', 'veille').stdout.strip(), '5')
        self.assertEqual(sortie('reglage', 'radio', 'zz').returncode, 2)
        self.assertEqual(sortie('theme').stdout.strip(), 'neutre')
        self.assertEqual(sortie('maj-en-cours').returncode, 1)
        self.assertEqual(sortie('n-importe-quoi').returncode, 2)


class UnSeulEndroit(unittest.TestCase):
    """Les regles rangees a un seul endroit le 27/11/2026 ne doivent pas revenir en copies."""
    def programmes(self):
        for f in sorted(os.listdir(INSTALLATION)):
            p = os.path.join(INSTALLATION, f)
            if os.path.isfile(p) and (f.startswith('prometheus-') or f.endswith('.sh')):
                yield f, lire(p)

    def test_reglages_lus_par_le_module(self):
        for f, s in self.programmes():
            if f == 'prometheus-admin':
                continue
            self.assertNotIn("reglages.json')", s, '%s relit reglages.json a la main : prometheus_commun / prometheus-commun' % f)

    def test_couleurs_par_defaut(self):
        for f, s in self.programmes():
            self.assertNotRegex(s, r"echo ocean|'ocean'", '%s : les couleurs par defaut sont dans prometheus_commun (THEME_DEFAUT)' % f)

    def test_droits_des_dossiers(self):
        """Proprietaires et droits des dossiers de la station : seulement prometheus-dossiers.conf."""
        motif = re.compile(r'^\s*(chown|chgrp|chmod)\b[^#\n]*\s/srv/prometheus(/[\w.-]+)*/?\s*($|[;&#])', re.M)
        for f, s in self.programmes():
            for m in motif.finditer(s):
                if re.search(r'\.(txt|json|css)\b', m.group(0)):
                    continue        # un fichier (son contenu), pas un dossier
                self.fail('%s : « %s » -> table prometheus-dossiers.conf' % (f, m.group(0).strip()))

    def test_liste_de_sauvegarde(self):
        for f in ('prometheus-sauvegarde', 'prometheus-restaurer'):
            s = lire(os.path.join(INSTALLATION, f))
            self.assertIn('sauvegarde.liste', s)
            self.assertNotIn('srv/prometheus/messages', s, '%s : la liste est dans prometheus-sauvegarde.liste' % f)

    def test_un_seul_controle_de_connexion(self):
        s = lire(os.path.join(INSTALLATION, 'prometheus-admin'))
        self.assertEqual(s.count("return self.repondre(401, {'erreur': 'Connectez-vous d’abord.'})"), 0,
                         'les adresses reservees sont dans ROUTES_ADMIN (un seul controle)')

    def test_le_module_commun_jamais_masque(self):
        """Une variable locale du meme nom que le module (« pc », le pourcentage...) le cache : l'erreur n'apparait
        qu'en marche (prometheus-batterie, 27/11/2026, vu a la mise en ligne). Aucun programme ne doit le faire."""
        import ast
        for f in sorted(os.listdir(INSTALLATION)):
            p = os.path.join(INSTALLATION, f)
            if not os.path.isfile(p) or not (f.endswith('.py') or lire(p).startswith(('#!/usr/bin/env python3', '#!/opt/'))):
                continue
            arbre = ast.parse(lire(p))
            noms = {a.asname or a.name for n in ast.walk(arbre) if isinstance(n, ast.Import) for a in n.names
                    if a.name == 'prometheus_commun' or a.name.startswith('radio_')}
            for n in ast.walk(arbre):
                cibles = []
                if isinstance(n, (ast.Assign, ast.AugAssign, ast.AnnAssign, ast.For, ast.comprehension, ast.With)):
                    cibles = [x for x in ast.walk(n) if isinstance(x, ast.Name) and isinstance(x.ctx, ast.Store)]
                if isinstance(n, (ast.FunctionDef, ast.Lambda)):
                    cibles = [ast.Name(id=a.arg) for a in n.args.args]
                for c in cibles:
                    self.assertNotIn(c.id, noms, '%s : « %s » cache le module du meme nom' % (f, c.id))

    def test_table_des_dossiers_bien_formee(self):
        for n, l in enumerate(lire(os.path.join(INSTALLATION, 'prometheus-dossiers.conf')).splitlines(), 1):
            if not l.strip() or l.startswith('#'):
                continue
            champs = l.split()
            self.assertEqual(len(champs), 6, 'ligne %d : %r' % (n, l))
            self.assertIn(champs[0], ('d', 'Z'))
            self.assertTrue(champs[1].startswith('/'))
            self.assertRegex(champs[2], r'^(-|[0-7]{4})$')


if __name__ == '__main__':
    unittest.main()
