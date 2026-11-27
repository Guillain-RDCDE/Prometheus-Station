// Verrou « une regle = un seul endroit » (27/11/2026) : node --test tests/web/*.test.mjs
// Parcourt toutes les pages et scripts de web/ et echoue si une page refait a sa facon ce que web/commun.js fait
// (ou ce que les couleurs du theme disent). Pas exclus : vendor/ (bibliotheques d'autres projets) et annonce.js,
// injecte par nginx dans les pages de Kiwix ou commun.js n'est pas charge : il doit rester autonome.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const WEB = path.join(path.dirname(fileURLToPath(import.meta.url)), '..', '..', 'installation', 'web');
const EXCLUS = ['vendor', 'annonce.js'];

function fichiers(dossier) {
  return fs.readdirSync(dossier, { withFileTypes: true }).flatMap(e => {
    const p = path.join(dossier, e.name), rel = path.relative(WEB, p);
    if (EXCLUS.includes(rel)) return [];
    if (e.isDirectory()) return fichiers(p);
    return /\.(html|js|css)$/.test(e.name) ? [rel] : [];
  });
}
const TOUS = fichiers(WEB);
// Les lignes d'un fichier, sans les commentaires de fin de ligne (« // ... ») : un commentaire peut citer fetch(
function lignes(rel) {
  return fs.readFileSync(path.join(WEB, rel), 'utf8').split('\n').map((l, i) => [i + 1, l.replace(/(^|[^:'"\\])\/\/.*$/, '$1')]);
}
function chercher(motif, autorise = () => false) {
  const trouve = [];
  for (const rel of TOUS) {
    if (rel === 'commun.js') continue;
    for (const [n, l] of lignes(rel)) if (motif.test(l) && !autorise(rel, l)) trouve.push(rel + ':' + n + '  ' + l.trim().slice(0, 140));
  }
  return trouve;
}

test('il y a bien des pages a verifier, et commun.js', () => {
  assert.ok(TOUS.includes('commun.js'));
  assert.ok(TOUS.length > 25, TOUS.length + ' fichiers');
});

test('aucune page ne redefinit les outils de commun.js', () => {
  const noms = ['\\$', 'el', 'duree', 'poids', 'mo', 'taille', 'ilya', 'heure', 'octets', 'lire', 'envoyer', 'poster', 'deuxTemps', 'texteRadio', 'suivreJournal', 'lireJournal', 'maintenant', 'virgule'];
  const motif = new RegExp('function\\s+(' + noms.join('|') + ')\\s*\\(');
  assert.deepEqual(chercher(motif), []);
});

// fetch( n'apparait que dans commun.js. Liste d'exceptions (vide aujourd'hui) : ce qui DOIT parler a la station
// autrement. Pas de fetch donc pas dans la liste, mais a savoir : navigator.sendBeacon (encyclopedies, compte un
// article ouvert pendant que la page s'en va : seul envoi qui survit au depart) et XMLHttpRequest (ajouter : la
// barre d'avancement d'un envoi de livre, que fetch ne donne pas).
const FETCH_PERMIS = [];
test('aucun fetch( en dehors de commun.js', () => {
  assert.deepEqual(chercher(/\bfetch\s*\(/, (rel, l) => FETCH_PERMIS.some(p => p[0] === rel && l.includes(p[1]))), []);
});

test('aucun bouton en deux temps fait a la main', () => {
  assert.deepEqual(chercher(/classList\.add\(\s*'confirmer'|dataset\.confirmer/), []);
});

test('le choix fr-FR / en-GB des dates est fait une seule fois (LOC)', () => {
  assert.deepEqual(chercher(/'en-GB'/), []);
});

// Les etats (bien, a surveiller, danger) viennent du theme (--vert, --orange, --rouge-urgence, --rouge-pale...) :
// le theme sombre « nuit » les eclaircit. Restent permises les couleurs qui sont des DONNEES, pas des etats :
// la couleur de chaque famille de reglages (--f), les tranches du stockage, les pastilles des themes a choisir,
// et la definition des themes eux-memes.
const COULEURS_ETAT = /#(2f9e44|2b8a3e|c92a2a|d62828|fff5f5|8a1c1c|d9480f)\b/i;
function palette(rel, l) {
  if (rel === 'style.css' || rel.startsWith('themes/')) return true;               // la definition des couleurs
  if (rel === 'parametres/index.html' && /--f:\s*#|COULEURS_PLACE|\['braise'/.test(l)) return true;
  return false;
}
test('aucune couleur d’etat ecrite en dur (le theme nuit doit pouvoir la changer)', () => {
  assert.deepEqual(chercher(COULEURS_ETAT, palette), []);
});

test('chaque page qui utilise commun.js le charge, apres langue.js', () => {
  const OUTILS = /(^|[^.\w])(\$|el|lire|lireTexte|lireJournal|envoyer|deuxTemps|duree|ilya|taille|texteRadio|suivreJournal)\(/;
  const fautes = [];
  for (const rel of TOUS.filter(r => r.endsWith('.html'))) {
    const src = fs.readFileSync(path.join(WEB, rel), 'utf8');
    const scripts = [...src.matchAll(/<script src="([^"]+)"/g)].map(m => m[1]);
    const enLigne = [...src.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m => m[1]).join('\n');
    const viaMesh = scripts.includes('mesh.js');
    if (!OUTILS.test(enLigne) && !viaMesh) continue;
    const c = scripts.indexOf('/commun.js'), lg = scripts.indexOf('/langue.js');
    if (c < 0 || lg < 0 || c < lg || (viaMesh && scripts.indexOf('mesh.js') < c)) fautes.push(rel + ' : ' + scripts.join(', '));
  }
  assert.deepEqual(fautes, []);
});
