// Tests de web/commun.js (27/11/2026) : node --test tests/web/*.test.mjs
// commun.js et langue.js sont charges tels quels dans un bac a sable (vm) avec un faux document, une fausse
// horloge (minuteurs avances a la main) et un faux fetch : aucun reseau, aucun navigateur.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import vm from 'node:vm';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const WEB = path.join(path.dirname(fileURLToPath(import.meta.url)), '..', '..', 'installation', 'web');
const LANGUE_JS = fs.readFileSync(path.join(WEB, 'langue.js'), 'utf8');
const COMMUN_JS = fs.readFileSync(path.join(WEB, 'commun.js'), 'utf8');
const MESH_JS = fs.readFileSync(path.join(WEB, 'parametres', 'mesh', 'mesh.js'), 'utf8');

// ----- Un petit monde : document, horloge, fetch
class Element {
  constructor(tag) { this.tagName = tag; this.className = ''; this._texte = ''; this.dataset = {}; this.onclick = null; }
  get textContent() { return this._texte; }
  set textContent(v) { this._texte = String(v); }   // comme le vrai DOM : 0 devient « 0 »
  get classList() {
    const e = this;
    const liste = () => e.className.split(/\s+/).filter(Boolean);
    return {
      contains: c => liste().includes(c),
      add: c => { if (!liste().includes(c)) e.className = liste().concat(c).join(' '); },
      remove: c => { e.className = liste().filter(x => x !== c).join(' '); },
      toggle: (c, oui) => { const a = oui === undefined ? !liste().includes(c) : oui; if (a) e.classList.add(c); else e.classList.remove(c); return a; }
    };
  }
}

function monde({ langue = 'fr', chemin = '/parametres/', fetch, mesh = false } = {}) {
  let horloge = 1_800_000_000_000, numero = 0;
  const minuteurs = new Map();
  const ids = {};
  const location = { pathname: chemin, search: '', hash: '', _href: null, reload() {} };
  Object.defineProperty(location, 'href', { get() { return this._href || chemin; }, set(v) { this._href = v; } });
  const stockage = { langue };
  const ctx = {
    console, Blob, TextEncoder, Headers, encodeURIComponent, decodeURIComponent,
    navigator: { language: langue },
    localStorage: { getItem: k => (k in stockage ? stockage[k] : null), setItem: (k, v) => { stockage[k] = String(v); } },
    location,
    addEventListener() {},
    document: {
      body: null, documentElement: {},
      createElement: tag => new Element(tag),
      getElementById: id => ids[id] || null,
      addEventListener() {}, querySelectorAll: () => []
    },
    setTimeout: (f, ms) => { const id = ++numero; minuteurs.set(id, { f, a: horloge + (ms || 0) }); return id; },
    clearTimeout: id => { minuteurs.delete(id); },
    fetch: (u, o) => fetch(u, o || {})
  };
  ctx.window = ctx;
  vm.createContext(ctx);
  vm.runInContext('Date.now = function () { return ' + 'horlogeMonde(); };', Object.assign(ctx, { horlogeMonde: () => horloge }));
  vm.runInContext(LANGUE_JS, ctx, { filename: 'langue.js' });
  vm.runInContext(COMMUN_JS, ctx, { filename: 'commun.js' });
  if (mesh) vm.runInContext(MESH_JS, ctx, { filename: 'mesh.js' });   // la section Mesh, au-dessus de commun.js
  return {
    ctx, location, minuteurs, ids,
    // Avance l'horloge : fait partir les minuteurs dus, dans l'ordre, en laissant les promesses se resoudre entre deux
    async avancer(ms) {
      const fin = horloge + ms;
      for (;;) {
        await vide();
        let prochain = null;
        for (const [id, m] of minuteurs) if (m.a <= fin && (!prochain || m.a < prochain[1].a)) prochain = [id, m];
        if (!prochain) break;
        minuteurs.delete(prochain[0]); horloge = Math.max(horloge, prochain[1].a); prochain[1].f();
      }
      horloge = fin; await vide();
    },
    poser(id, e) { ids[id] = e; return e; }
  };
}
async function vide() { for (let i = 0; i < 20; i++) await new Promise(r => setImmediate(r)); }
function reponse(corps, statut = 200, entetes = {}) {
  return Promise.resolve(new Response(typeof corps === 'string' ? corps : JSON.stringify(corps), { status: statut, headers: entetes }));
}

// ===================================================================== el
test('el : le chiffre 0 s’affiche, null et undefined ne mettent rien', () => {
  const { ctx } = monde();
  assert.equal(ctx.el('dd', 'valeur', 0).textContent, '0');
  assert.equal(ctx.el('dd', 'valeur', '').textContent, '');
  assert.equal(ctx.el('dd', '', null).textContent, '');
  assert.equal(ctx.el('dd').textContent, '');
  assert.equal(ctx.el('p', 'note', 'x').className, 'note');
});

// ===================================================================== duree
test('duree : arrondie une seule fois, jamais « 1 h 60 » ni « 1 j 24 h »', () => {
  const { ctx } = monde();
  const attendu = { 0: '0 min', 59: '1 min', 60: '1 min', 89: '1 min', 90: '2 min', 3599: '1 h', 3600: '1 h', 3660: '1 h 01',
    5400: '1 h 30', 7170: '2 h', 86399: '1 j', 86400: '1 j', 90000: '1 j 1 h', 171000: '2 j', [9 * 86400 + 5 * 3600]: '9 j 5 h' };
  for (const [s, t] of Object.entries(attendu)) assert.equal(ctx.duree(+s), t, 'duree(' + s + ')');
  for (let s = 0; s < 400000; s += 7) {
    const t = ctx.duree(s);
    assert.doesNotMatch(t, /\b60$|\b24 h|NaN|undefined/, 'duree(' + s + ') = ' + t);
    const m = / h (\d\d)$/.exec(t); if (m) assert.ok(+m[1] < 60);
  }
  assert.equal(ctx.duree(-5), '0 min');
  assert.equal(monde({ langue: 'en' }).ctx.duree(90000), '1 d 1 h');
});

// ===================================================================== ilya
test('ilya : minutes et heures entieres, jamais « il y a 60 min »', () => {
  const { ctx } = monde();
  const n = ctx.maintenant();
  assert.equal(ctx.ilya(0), '—');
  assert.equal(ctx.ilya(n - 30), 'à l’instant');
  assert.equal(ctx.ilya(n - 3599), 'il y a 59 min');
  assert.equal(ctx.ilya(n - 86399), 'il y a 23 h');
  assert.equal(ctx.ilya(n - 3 * 86400), 'il y a 3 j');
  assert.doesNotMatch(ctx.ilya(n - 30 * 86400), /il y a/);
});

// ===================================================================== taille
test('taille : une seule regle (1 Go = 1000 Mo), unite choisie apres l’arrondi', () => {
  const { ctx } = monde();
  const attendu = { 0: '0 Ko', 1: '1 Ko', 500: '1 Ko', 1500: '2 Ko', 3039: '3 Ko', 999499: '999 Ko', 999999: '1,0 Mo',
    5300000: '5,3 Mo', 106478034: '106 Mo', 999600000: '1,0 Go', 3652280723: '3,7 Go', 9960000000: '10 Go', 127418087648: '127 Go' };
  for (const [o, t] of Object.entries(attendu)) assert.equal(ctx.taille(+o), t, 'taille(' + o + ')');
  assert.equal(monde({ langue: 'en' }).ctx.taille(3652280723), '3.7 GB');
});

// ===================================================================== texteRadio
test('texteRadio : chaque etat, et « eteinte » d’une radio activee = demarrage', () => {
  const { ctx } = monde();
  const t = d => { const x = ctx.texteRadio(d); return [x.court, x.genre]; };
  assert.deepEqual(t({ active: false, etat: 'eteinte' }), ['Désactivée', 'eteinte']);
  assert.deepEqual(t({ active: false, etat: 'ok' }), ['Désactivée', 'eteinte']);
  assert.deepEqual(t({ active: true, etat: 'ok', nom: 'Station' }), ['En marche', 'bien']);
  assert.equal(ctx.texteRadio({ active: true, etat: 'ok', nom: 'Station' }).detail, 'Station');
  assert.equal(ctx.texteRadio({ active: true, etat: 'ok' }).detail, 'radio branchée');
  assert.deepEqual(t({ active: true, etat: 'absente' }), ['Débranchée', 'alerte']);
  assert.deepEqual(t({ active: true, etat: 'muette' }), ['Ne répond pas', 'alerte']);
  assert.deepEqual(t({ active: true, etat: 'eteinte' }), ['Démarrage…', 'attente']);
  assert.deepEqual(t({ active: true }), ['Démarrage…', 'attente']);
  assert.deepEqual(t(null), ['Désactivée', 'eteinte']);
  for (const d of [{ active: true, etat: 'ok' }, { active: true, etat: 'muette' }, { active: true, etat: 'eteinte' }, {}]) {
    const x = ctx.texteRadio(d);
    for (const v of [x.court, x.detail]) assert.ok(v && !/undefined/.test(v));
  }
});

// ===================================================================== envoyer / lire
test('envoyer : reponse acceptee, objet envoye en JSON', async () => {
  let vu = null;
  const { ctx } = monde({ fetch: (u, o) => { vu = [u, o]; return reponse({ id: 'a1' }, 200, { Date: 'Fri, 27 Nov 2026 10:00:00 GMT' }); } });
  const r = await ctx.envoyer('/api/registre', { nom: 'Ana' });
  assert.equal(r.ok, true); assert.equal(r.code, 200); assert.equal(r.d.id, 'a1'); assert.equal(r.erreur, '');
  assert.equal(r.heure, Date.parse('2026-11-27T10:00:00Z') / 1000);
  assert.equal(vu[1].method, 'POST'); assert.equal(vu[1].headers['Content-Type'], 'application/json'); assert.equal(vu[1].body, '{"nom":"Ana"}');
});
test('envoyer : un texte part tel quel (ordre PUT), une reponse vide donne {}', async () => {
  let vu = null;
  const { ctx } = monde({ fetch: (u, o) => { vu = o; return reponse('', 201); } });
  const r = await ctx.envoyer('/ajouter/commande/systeme', '', 'PUT');
  assert.equal(r.ok, true); assert.deepEqual({ ...r.d }, {});
  assert.equal(vu.method, 'PUT'); assert.equal(vu.body, ''); assert.equal(vu.headers, undefined);
});
test('envoyer : 400 avec {erreur} -> la phrase de la station, traduite', async () => {
  const fr = monde({ fetch: () => reponse({ erreur: 'Message vide.' }, 400) });
  const r = await fr.ctx.envoyer('/api/messages', { texte: '' });
  assert.equal(r.ok, false); assert.equal(r.code, 400); assert.equal(r.erreur, 'Message vide.');
  const en = monde({ langue: 'en', fetch: () => reponse({ erreur: 'Message vide.' }, 400) });
  assert.equal((await en.ctx.envoyer('/api/messages', {})).erreur, 'Empty message.');
  const sans = monde({ fetch: () => reponse('<html>', 404) });
  assert.equal((await sans.ctx.envoyer('/api/x', {})).erreur, 'Erreur 404.');
});
test('envoyer : 401 sur une page d’administration -> page de connexion avec retour', async () => {
  const m = monde({ chemin: '/parametres/mesh/config.html', fetch: () => reponse({ erreur: 'Connectez-vous d’abord.' }, 401) });
  m.location.hash = '#x';
  const r = await m.ctx.envoyer('/admin-api/mesh/ordre', { action: 'x' });
  assert.equal(r.ok, false); assert.equal(r.code, 401);
  assert.equal(m.location._href, '/connexion.html?retour=' + encodeURIComponent('/parametres/mesh/config.html#x'));
});
test('envoyer : 401 d’une adresse publique sur une page publique -> pas de redirection, le message', async () => {
  const m = monde({ chemin: '/messages/', fetch: () => reponse({ erreur: 'Connectez-vous d’abord.' }, 401) });
  const r = await m.ctx.envoyer('/api/messages/effacer', { id: 1 });
  assert.equal(m.location._href, null); assert.equal(r.erreur, 'Connectez-vous d’abord.');
});
test('lire : une page des visiteurs qui demande une adresse d’administration (ecran) -> simple refus, pas de renvoi', async () => {
  const m = monde({ chemin: '/ecran/', fetch: () => reponse({ erreur: 'Connectez-vous d’abord.' }, 401) });
  await assert.rejects(m.ctx.lire('/admin-api/sante'), e => e.code === 401);
  assert.equal(m.location._href, null);
});
test('envoyer : sur la page de connexion, 401 = mauvais mot de passe (pas de boucle)', async () => {
  const m = monde({ chemin: '/connexion.html', fetch: () => reponse({ erreur: 'Mot de passe incorrect.' }, 401) });
  const r = await m.ctx.envoyer('/admin-api/connexion', { mdp: 'x' });
  assert.equal(m.location._href, null); assert.equal(r.erreur, 'Mot de passe incorrect.');
});
test('envoyer : station muette -> message lisible, jamais d’exception', async () => {
  const m = monde({ langue: 'en', fetch: () => Promise.reject(new TypeError('Failed to fetch')) });
  const r = await m.ctx.envoyer('/admin-api/wifi', { nom: 'x' });
  assert.equal(r.ok, false); assert.equal(r.code, 0); assert.equal(r.erreur, 'The station does not respond.');
});
test('lire : donnees, refus avec code, session perdue derriere nginx (renvoi vers connexion.html)', async () => {
  const ok = monde({ fetch: () => reponse({ temperature: 51 }) });
  assert.equal((await ok.ctx.lire('/admin-api/sante')).temperature, 51);
  const ko = monde({ fetch: () => reponse('<html>Bad gateway</html>', 502) });
  await assert.rejects(ko.ctx.lire('/admin-api/sante'), e => e.code === 502 && e.message === 'La station ne répond pas.');
  const nginx = monde({ chemin: '/parametres/', fetch: () => Promise.resolve({
    status: 200, redirected: true, url: 'http://station.local/connexion.html?retour=/ajouter/etat.json', headers: new Headers(), text: () => Promise.resolve('<!doctype html>') }) });
  await assert.rejects(nginx.ctx.lire('/ajouter/etat.json'), e => e.code === 401);
  assert.equal(nginx.location._href, '/connexion.html?retour=%2Fparametres%2F');
  const s401 = monde({ chemin: '/parametres/', fetch: () => reponse({ erreur: 'Connectez-vous d’abord.' }, 401) });
  await assert.rejects(s401.ctx.lire('/admin-api/sante'));
  assert.match(s401.location._href, /^\/connexion\.html\?retour=/);
});
test('lireJournal : texte, \'\' s’il manque, null si la station se tait', async () => {
  assert.equal(await monde({ fetch: () => reponse('== 1\nabc') }).ctx.lireJournal('/ajouter/maj-systeme.txt'), '== 1\nabc');
  assert.equal(await monde({ fetch: () => reponse('', 404) }).ctx.lireJournal('/ajouter/maj-systeme.txt'), '');
  assert.equal(await monde({ fetch: () => Promise.reject(new Error()) }).ctx.lireJournal('/ajouter/maj-systeme.txt'), null);
});

// ===================================================================== deuxTemps
test('deuxTemps : 1er toucher arme, 2e confirme et arrete le minuteur', async () => {
  const m = monde(), b = new Element('button');
  b.textContent = 'Écrire dans la radio';
  const o = { texte: 'Toucher encore pour écrire' };
  assert.equal(m.ctx.deuxTemps(b, o), false);
  assert.ok(b.classList.contains('confirmer')); assert.equal(b.textContent, 'Toucher encore pour écrire');
  assert.equal(m.minuteurs.size, 1);
  assert.equal(m.ctx.deuxTemps(b, o), true);
  assert.ok(!b.classList.contains('confirmer')); assert.equal(b.textContent, 'Écrire dans la radio');
  assert.equal(m.minuteurs.size, 0, 'minuteur arrete');
  // L'action met son texte ; une longue ecriture ne le voit plus remplace (le bogue des 8 s)
  b.textContent = 'Écriture…';
  await m.avancer(20000);
  assert.equal(b.textContent, 'Écriture…');
});
test('deuxTemps : sans 2e toucher, le bouton revient seul (5 s), puis se rearme', async () => {
  const m = monde(), b = new Element('button');
  b.textContent = 'Supprimer';
  let retours = 0, avertis = 0;
  const o = { texte: 'Confirmer', retour: () => retours++, avertir: () => avertis++ };
  m.ctx.deuxTemps(b, o);
  await m.avancer(4900); assert.equal(b.textContent, 'Confirmer');
  await m.avancer(200); assert.equal(b.textContent, 'Supprimer'); assert.ok(!b.classList.contains('confirmer'));
  assert.equal(retours, 1); assert.equal(avertis, 1);
  assert.equal(m.ctx.deuxTemps(b, o), false, 'apres le delai, il faut de nouveau deux touchers');
  assert.equal(m.ctx.deuxTemps(b, o), true);
  m.ctx.deuxTemps(b, { texte: 'x', delai: m.ctx.DELAI_RISQUE });
  await m.avancer(7000); assert.equal(b.textContent, 'x');
  await m.avancer(1100); assert.equal(b.textContent, 'Supprimer');
});
test('deuxTemps : « si » faux -> pas de confirmation ; « action » pose le clic', async () => {
  const m = monde(), b = new Element('button');
  b.textContent = 'Importer';
  assert.equal(m.ctx.deuxTemps(b, { texte: 'Toucher encore', si: false }), true);
  assert.equal(m.ctx.deuxTemps(b, { texte: 'Toucher encore', si: () => false }), true);
  assert.equal(m.minuteurs.size, 0);
  let fait = 0;
  m.ctx.deuxTemps(b, { texte: 'Toucher encore', action: () => fait++ });
  b.onclick(); assert.equal(fait, 0); assert.equal(b.textContent, 'Toucher encore');
  b.onclick(); assert.equal(fait, 1); assert.equal(b.textContent, 'Importer');
});

// ===================================================================== suivreJournal
function journal(etapes) {
  // etapes : textes successifs du journal ; chaque lecture avance d'une etape (la derniere reste)
  let i = 0;
  return u => {
    if (!/\.txt/.test(u)) return reponse('');
    const t = etapes[Math.min(i++, etapes.length - 1)];
    return t instanceof Error ? Promise.reject(t) : reponse(t);
  };
}
test('suivreJournal : lancement, detail qui defile, FIN 0', async () => {
  const lu = [];
  let fin = null, lance = 0;
  const m = monde({ fetch: journal(['== ancien\n### FIN 0\n', '== nouveau\nLecture…', '== nouveau\nLecture…\nFait\n### FIN 0\n']) });
  m.ctx.suivreJournal('/ajouter/maj-systeme.txt', {
    lancer: () => { lance++; return m.ctx.envoyer('/ajouter/commande/systeme', '', 'PUT'); },
    surTexte: t => lu.push(t), surFin: (c, t) => { fin = [c, t]; }
  });
  await m.avancer(10000);
  assert.equal(lance, 1);
  assert.deepEqual(fin && fin[0], 0);
  assert.ok(lu.length >= 1 && lu.every(t => t.startsWith('== nouveau')), 'le journal d’avant n’est pas montre');
});
test('suivreJournal : FIN 1 -> echec', async () => {
  let fin = null;
  const m = monde({ fetch: journal(['== ancien\n### FIN 0', '== nouveau\nErreur\n### FIN 1\n']) });
  m.ctx.suivreJournal('/x.txt', { lancer: () => m.ctx.envoyer('/ajouter/commande/x', '', 'PUT'), surFin: c => { fin = c; } });
  await m.avancer(10000);
  assert.equal(fin, 1);
});
test('suivreJournal : rien n’a demarre dans le delai -> surRien(pas-demarre)', async () => {
  let rien = null, fin = null;
  const m = monde({ fetch: journal(['== ancien\n### FIN 0']) });
  m.ctx.suivreJournal('/x.txt', { lancer: () => m.ctx.envoyer('/ajouter/commande/x', '', 'PUT'), surRien: r => { rien = r; }, surFin: c => { fin = c; } });
  await m.avancer(29000); assert.equal(rien, null);
  await m.avancer(5000); assert.equal(rien, 'pas-demarre'); assert.equal(fin, null);
});
test('suivreJournal : reprise a l’ouverture d’une operation deja finie -> surRien(deja-fini)', async () => {
  let rien = null, textes = 0;
  const m = monde({ fetch: journal(['== hier\n### FIN 0']) });
  m.ctx.suivreJournal('/x.txt', { debutAvant: null, surRien: r => { rien = r; }, surTexte: () => textes++ });
  await m.avancer(1000);
  assert.equal(rien, 'deja-fini'); assert.equal(textes, 0);
});
test('suivreJournal : lancement sans reseau -> surPanne (le bouton ne reste pas sur « Lancement… »)', async () => {
  let panne = null, fin = null;
  const m = monde({ fetch: u => /commande/.test(u) ? Promise.reject(new TypeError('Failed to fetch')) : reponse('== ancien\n### FIN 0') });
  m.ctx.suivreJournal('/x.txt', { lancer: () => m.ctx.envoyer('/ajouter/commande/systeme', '', 'PUT'), surPanne: t => { panne = t; }, surFin: c => { fin = c; } });
  await m.avancer(5000);
  assert.equal(panne, 'La station ne répond pas.'); assert.equal(fin, null);
  // Un lancer qui leve une exception aboutit aussi a surPanne
  let panne2 = null;
  const m2 = monde({ fetch: () => reponse('') });
  m2.ctx.suivreJournal('/x.txt', { lancer: () => { throw new Error('x'); }, surPanne: t => { panne2 = t; } });
  await m2.avancer(1000);
  assert.equal(panne2, 'La station ne répond pas.');
});
test('suivreJournal : coupures pendant le suivi -> on reessaie, puis la fin arrive', async () => {
  let fin = null;
  const m = monde({ fetch: journal(['== ancien\n### FIN 0', new TypeError('coupure'), new TypeError('coupure'), '== nouveau\nok\n### FIN 0']) });
  m.ctx.suivreJournal('/x.txt', { lancer: () => m.ctx.envoyer('/ajouter/commande/x', '', 'PUT'), surFin: c => { fin = c; } });
  await m.avancer(15000);
  assert.equal(fin, 0);
});

// ===================================================================== Garde-fou de la radio (mesh.js)
test('texteGardeFou : suit l’etat ecrit par radio_gardefou.py', () => {
  const { ctx } = monde({ mesh: true });
  assert.equal(ctx.texteGardeFou(null), null);
  const g = { heure: ctx.maintenant() - 120, raison: 'région', fichier: 'x.yaml' };
  const s = ctx.texteGardeFou({ ...g, etat: 'surveille' });
  assert.equal(s.genre, 'surveille'); assert.match(s.court, /vérification/); assert.match(s.texte, /il y a 2 min \(région\)/);
  assert.equal(ctx.texteGardeFou(g).genre, 'surveille', 'sans etat (ancien fichier) : surveille');
  const r = ctx.texteGardeFou({ ...g, etat: 'restauration-demandee', demandes: 1 });
  assert.equal(r.genre, 'remise'); assert.match(r.court, /remise des réglages d’avant/); assert.match(r.texte, /remet ses réglages d’avant/);
  const e = ctx.texteGardeFou({ ...g, etat: 'surveille', en_cours: true });
  assert.equal(e.genre, 'ecriture'); assert.match(e.court, /en cours d’écriture/);
  assert.equal(ctx.texteGardeFou({ ...g, etat: 'surveille', en_cours: false }).genre, 'surveille');
  const a = ctx.texteGardeFou({ ...g, etat: 'abandon', demandes: 3 });
  assert.equal(a.genre, 'abandon');
  assert.equal(a.texte, 'La radio ne revient pas : remettez une sauvegarde depuis Sauvegardes, ou rebranchez-la.');
  for (const x of [s, r, a, e]) assert.doesNotMatch(x.court + x.texte, /undefined|NaN/);
  assert.equal(monde({ mesh: true, langue: 'en' }).ctx.texteGardeFou({ etat: 'abandon' }).court, ' · the radio does not come back');
});

// ===================================================================== ordres numerotes (prometheus-commande)
function station({ resultat, journal: etapes = ['== ancien\n### FIN 0'] }) {
  // resultat : la reponse que la station ecrira dans /ajouter/resultats/<numero>.json (null : jamais)
  const deposes = [];
  let i = 0;
  return {
    deposes,
    fetch: (u, o) => {
      if (/\/ajouter\/commande\//.test(u)) { deposes.push(decodeURIComponent(u)); return reponse(''); }
      if (/\/ajouter\/resultats\//.test(u)) return resultat ? reponse(resultat) : reponse('', 404);
      return reponse(etapes[Math.min(i++, etapes.length - 1)]);
    }
  };
}
test('commander : l’ordre porte un numero, la reponse de la station est lue par ce numero', async () => {
  const s = station({ resultat: { ordre: 'sauvegarder', etat: 'fait', message: 'Sauvegarde faite.' } });
  const m = monde({ fetch: s.fetch });
  let r = null, res = null;
  m.ctx.commander('sauvegarder').then(x => { r = x; return m.ctx.resultatOrdre(x.id); }).then(x => { res = x; });
  await m.avancer(3000);
  assert.ok(r.ok);
  assert.match(s.deposes[0], /^\/ajouter\/commande\/sauvegarder@[a-z0-9]{8,}$/);
  assert.ok(s.deposes[0].endsWith('@' + r.id));
  assert.equal(res.etat, 'fait');
  assert.equal(m.ctx.ordreRefuse(res), false);
});
test('resultatOrdre : pas de reponse dans le delai -> null (la page continue comme avant)', async () => {
  const s = station({ resultat: null });
  const m = monde({ fetch: s.fetch });
  let res;
  m.ctx.resultatOrdre('abc', 5000).then(x => { res = x; });
  await m.avancer(4000); assert.equal(res, undefined);
  await m.avancer(3000); assert.equal(res, null);
});
test('suivreJournal : ordre refuse par la station -> surPanne avec sa phrase, plus rien ne tourne', async () => {
  const s = station({ resultat: { etat: 'refuse', message: 'Une mise à jour tourne déjà.' } });
  const m = monde({ fetch: s.fetch });
  let panne = null, rien = null;
  m.ctx.suivreJournal('/ajouter/maj-systeme.txt', { lancer: () => m.ctx.commander('systeme'), surPanne: t => { panne = t; }, surRien: r => { rien = r; } });
  await m.avancer(60000);
  assert.equal(panne, 'Une mise à jour tourne déjà.');
  assert.equal(rien, null, 'pas de second message « n’a pas demarre »');
});
test('suivreJournal : operation radio en attente -> surAttente, et on attend au-dela de 30 s', async () => {
  const s = station({ resultat: { etat: 'attente', message: 'Une opération radio est en cours : celle-ci partira juste après.' },
                      journal: ['== ancien\n### FIN 0'] });
  const m = monde({ fetch: s.fetch });
  let attente = null, rien = null;
  m.ctx.suivreJournal('/ajouter/radio-outil.txt', { lancer: () => m.ctx.commander('radio-detecter', '{}'),
    surAttente: t => { attente = t; }, surRien: r => { rien = r; } });
  await m.avancer(120000);
  assert.match(attente, /partira juste après/);
  assert.equal(rien, null, 'toujours en attente apres 2 minutes');
});
test('mesh.js : l’outil radio est lance par un ordre numerote', async () => {
  const s = station({ resultat: { etat: 'lance', message: 'Opération radio lancée.' } });
  const m = monde({ fetch: s.fetch, mesh: true });
  for (const id of ['resultat-outil', 'console-outil']) m.poser(id, Object.assign(new Element('div'), { hidden: true, scrollIntoView() {} }));
  m.ctx.boutonsOutil = () => {};
  m.ctx.lancerOutil('detecter', '{}');
  await m.avancer(3000);
  assert.match(s.deposes[0] || '', /^\/ajouter\/commande\/radio-detecter@/);
});
