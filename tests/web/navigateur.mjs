// Verification des pages dans un vrai navigateur (Chrome sans fenetre), 27/11/2026.
//   node tests/web/navigateur.mjs [--web DOSSIER] [--captures DOSSIER] [--seulement mot] [--etat fichier.json]
// Un petit serveur sert web/ tel quel et joue la station (reponses realistes de prometheus-admin, etat.json,
// journaux) ; Chrome ouvre chaque page, on releve toute exception ou erreur de la console, on verifie que les
// donnees sont bien affichees (ni « undefined », ni « NaN », ni « … » la ou une donnee etait donnee), et on joue
// quelques gestes (bouton en deux temps, session expiree, station muette). Captures en theme « nuit » a regarder.
// Sort avec le code 1 a la moindre faute. Chrome et le serveur sont arretes a la fin, meme en cas d'erreur.
import http from 'node:http';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawn } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const ICI = path.dirname(fileURLToPath(import.meta.url));
const arg = (nom, defaut) => { const i = process.argv.indexOf('--' + nom); return i > 0 ? process.argv[i + 1] : defaut; };
const WEB = path.resolve(arg('web', path.join(ICI, '..', '..', 'installation', 'web')));
const CAPTURES = path.resolve(arg('captures', path.join(os.tmpdir(), 'prometheus-captures')));
const SEULEMENT = arg('seulement', '');
const ETAT = JSON.parse(fs.readFileSync(arg('etat', path.join(ICI, 'donnees', 'etat.json')), 'utf8'));
const CHROME = process.env.CHROME || '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
fs.mkdirSync(CAPTURES, { recursive: true });
const attendre = ms => new Promise(r => setTimeout(r, ms));
const maintenant = () => Date.now() / 1000;

// ===================================================================== La station, jouee
let sc = {};   // scenario de la page en cours (remis a zero avant chaque page)
function scenarioDeBase() {
  return { theme: 'neutre', radioActive: true, radioEtat: 'ok', reseau: 'meshtastic', sessionExpiree: false, effacerRefuse: false,
    systemeMuet: false, journalMaj: null, lecturesMaj: 0, commandes: [], delaiEcriture: 0, ordres: [], systemeAJour: 0 };
}
function radioPublique() {
  return { active: sc.radioActive, peut: true, qui: 'tous', delai: 60, etat: sc.radioActive ? sc.radioEtat : 'eteinte', nom: 'Prometheus 7a3c',
    attente: 1, reseau: sc.reseau, max: 228, maj: '' };
}
const n = () => Math.round(maintenant());
function reglages() {
  return {
    annonce: { active: true, texte: 'Eau potable à la mairie de 9 h à 12 h.', couleur: 'info', defile: false, ecran: true, vitesse: 'normale' },
    registre: { active: true, lieu: true }, urgence: { active: true },
    entraide: { active: true, categories: ['eau', 'nourriture', 'sante', 'abri', 'energie', 'transport', 'outils', 'competences', 'autre'], duree: 72 },
    radio: { active: sc.radioActive, qui: 'tous', delai: 60, ecran_minutes: 2 }, ecran: { active: false, veille: 5 }, eink: { active: false },
    balise: { active: false, texte: '{nom} · wifi {wifi}', heures: 3, canal: 0, urgence_seulement: true },
    mesh: { historique_jours: 90, distance: true, toutes_cartes: false },
    recherches: { epingles: [{ titre: 'Potabilisation', lien: '/encyclopedies/content/wikipedia_fr_all_maxi/Potabilisation' }] }
  };
}
function radioAdmin() {
  const t = n();
  return {
    maintenant: t, etat: radioPublique(), reseau: { reseau: sc.reseau }, garde_fou: sc.gardeFou || null, mesh: { distance: true },
    details: {
      heure: t - 20, depuis: t - 7170,
      moi: { id: '!a1b2c3d4', nom: 'Prometheus', preset: 'LONG_FAST', region: 'EU_868', lat: 46.5, lon: -1.78, batterie: 101, occupation: 3.2,
             emission: 0.8, materiel: 'TBEAM', version: '2.7.15', cle: 'c3RhdGlvbi1jbGUtcHVibGlxdWU=' },
      noeuds: [
        { id: '!11223344', nom: 'Relais du clocher', court: 'RC', vu: t - 300, snr: 6.5, sauts: 0, lat: 46.51, lon: -1.77, materiel: 'HELTEC_V3', batterie: 87, role: 'ROUTER', cle: 'abc=', allumee: 90000 },
        { id: '!55667788', nom: 'Jeanne', court: 'JN', vu: t - 90000, sauts: 2 }
      ],
      canaux: [{ index: 0, nom: 'LongFast' }]
    },
    journal: [{ sens: 'recu', nom: 'Jeanne', texte: 'Bonjour la station', heure: t - 500, canal: 0, snr: 4.5 }, { sens: 'emis', texte: 'Bien reçu', heure: t - 400, canal: 0 }],
    outil: { sauvegardes: { meshtastic: t - 86400, meshcore: 0 }, versions: { meshtastic: ['2.7.15'], meshcore: ['1.10.0'] }, radios: [] }
  };
}
const SCHEMA = {
  config: { lora: [{ nom: 'region', type: 'choix', valeurs: ['UNSET', 'EU_868'] }, { nom: 'hop_limit', type: 'entier' }, { nom: 'tx_enabled', type: 'bool' }],
            device: [{ nom: 'role', type: 'choix', valeurs: ['CLIENT', 'ROUTER'] }] },
  module: { telemetry: [{ nom: 'device_update_interval', type: 'entier' }], mqtt: [{ nom: 'enabled', type: 'bool' }] },
  drapeaux: {}
};
const LU = {
  proprietaire: { long: 'Prometheus', court: 'PRO', licence: false, muet: false }, position: { fixe: false }, messages_prets: 'Je vais bien|Besoin d’aide',
  config: { lora: { region: 'EU_868', hop_limit: 3, tx_enabled: true }, device: { role: 'CLIENT' } },
  module: { telemetry: { device_update_interval: 900 }, mqtt: { enabled: false } },
  canaux: [{ index: 0, role: 1, reglages: { name: '', psk: 'AQ==', module_settings: { position_precision: 13 } } },
           { index: 1, role: 2, reglages: { name: 'Famille', psk: 'c2VjcmV0LWNsZS1kZS0zMi1vY3RldHMtISEhISEhISE=', module_settings: {} } }],
  url: 'https://meshtastic.org/e/#CgMSAQESBggBQANIAQ'
};
const CATALOGUE = '<?xml version="1.0"?><feed>' + [['wikipedia_fr_all_maxi', 'Wikipédia', 'fra', 2600000], ['mdwiki_en_all_maxi', 'MDWiki', 'eng', 73000], ['wikem_en_all_maxi', 'WikEM', 'eng', 4000]]
  .map(x => `<entry><name>${x[0]}</name><title>${x[1]}</title><summary>Résumé</summary><language>${x[2]}</language><articleCount>${x[3]}</articleCount>` +
    `<link type="text/html" href="/encyclopedies/content/${x[0]}_2026-05"/></entry>`).join('') + '</feed>';

function api(meth, u, corps) {
  const t = n(), p = u.pathname, q = u.searchParams;
  if (sc.sessionExpiree && p.startsWith('/admin-api/') && p !== '/admin-api/etat') return [401, { erreur: 'Connectez-vous d’abord.' }];
  switch (p) {
    case '/api/reglages': return [200, reglages()];
    case '/api/radio': return [200, radioPublique()];
    case '/api/panneau': return [200, { texte: '# Bienvenue\nLa station est **ouverte** à tous.\n- Eau à la mairie\n- Soins au gymnase' }];
    case '/api/heure': case '/api/recherche': return [200, {}];
    case '/api/messages': return meth === 'POST' ? [200, { id: 'm3' }] : [200, { maintenant: t, admin: false, radio: radioPublique(), messages: [
      { id: 'm2', nom: 'Lucie', texte: 'Quelqu’un a du lait pour bébé ?', heure: t - 600, radio: 'attente' }, { id: 'm1', nom: '', texte: 'Bonjour à tous', heure: t - 90000 }] }];
    case '/api/messages/vider': return [200, { annules: 1 }];
    case '/api/registre': return meth === 'POST' ? [200, { id: 'f9', cle: 'k9' }] : [200, { active: true, lieu: true, admin: false, fiches: [
      { id: 'f1', type: 'sauf', nom: 'Marie Dupont', lieu: 'Gymnase', message: 'Je vais bien.', heure: t - 3600 },
      { id: 'f2', type: 'cherche', nom: 'Paul Martin', lieu: '', message: 'Vu près du pont.', heure: t - 7200 }] }];
    case '/api/entraide': return meth === 'POST' ? [200, { id: 'a9', cle: 'k9' }] : [200, { active: true, duree: 72, maintenant: t, admin: false,
      categories: ['eau', 'nourriture', 'sante'], annonces: [{ id: 'a1', type: 'propose', categorie: 'eau', texte: 'Je peux filtrer de l’eau.', nom: 'Jean', contact: 'tente 4', heure: t - 1800 }] }];
    case '/api/registre/effacer': case '/api/entraide/effacer': return sc.effacerRefuse ? [403, { erreur: 'Effacement refusé.' }] : [200, {}];
    case '/api/registre/vider': case '/api/entraide/vider': return [200, {}];
    case '/admin-api/etat': return [200, { connecte: false, defini: true }];
    case '/admin-api/sante': return [200, { temperature: 52, tension: 'ok', allumee: 200000, personnes: 3, batterie: { pourcent: 76, tension: 4.1, secteur: false, restant: 27000 } }];
    case '/admin-api/energie': return [200, { sobre: false, ecran_installe: false, extinction: 120, restant: 7170 }];
    case '/admin-api/recherches': return [200, { epingles: reglages().recherches.epingles, sujets: [{ titre: 'Potabilisation', lien: '/encyclopedies/content/wikipedia_fr_all_maxi/Potabilisation', n: 12 }] }];
    case '/admin-api/balise': return [200, { apercu: 'Prometheus · wifi Prometheus-Station', octets: 36, max: 228, coupe: false, position: false, derniere: t - 3000, canaux: [{ index: 0, nom: 'Principal' }] }];
    case '/admin-api/radio': return [200, radioAdmin()];
    case '/admin-api/mesh/schema': return [200, SCHEMA];
    case '/admin-api/mesh/resultats': return [200, { resultats: [] }];
    case '/admin-api/mesh/sauvegardes': return [200, { sauvegardes: [{ reseau: 'meshtastic', fichier: 'meshtastic-2026-11-26-1200.yaml', raison: 'avant : région', heure: t - 86400 }] }];
    case '/admin-api/mesh/atelier': return [200, { maintenant: t, ports: ['/dev/ttyACM0'], station: '/dev/ttyACM0', atelier: { radios: [], disques: [], vues: {} },
      outil: { versions: { meshtastic: ['2.7.15'], meshcore: ['1.10.0'] } }, catalogue: {}, suivies: { meshtastic: [], meshcore: [] }, toutes_cartes: false }];
    case '/admin-api/mesh/historique': {
      const quoi = q.get('quoi');
      if (quoi === 'stats') return [200, { donnees: [0, 1, 2, 3].map(i => ({ source: 'station', heure: t - 3600 * (4 - i), emission: 0.5 + i / 10, occupation: 3 + i, entendus_1h: 2 + i, tension: 4.1 }))
        .concat([{ source: 'radio', heure: t - 600, noiseFloor: -112 }]) }];
      if (quoi === 'comptes') return [200, { donnees: { par_genre: [{ port: 'TEXT_MESSAGE_APP', sens: 'recu', n: 12 }, { port: 'POSITION_APP', sens: 'emis', n: 3 }],
        par_radio: [{ id: '!11223344', nom: 'Relais du clocher', n: 30, snr: 5.5, vu: t - 300 }], par_tranche: [{ sens: 'recu', heure: t - 7200, n: 5 }, { sens: 'recu', heure: t - 3600, n: 8 }],
        pas: 3600, total: 123, premier: t - 3 * 86400, taille: 2400000 } }];
      if (quoi === 'paquets') return [200, { donnees: [{ heure: t - 100, sens: 'recu', port: 'TEXT_MESSAGE_APP', de: '!11223344', nom: 'Relais du clocher', a: '^all', snr: 5, rssi: -90, sauts: 0, canal: 0, resume: { texte: 'Bonjour' } }] }];
      return [200, { donnees: [] }];
    }
    case '/admin-api/mesh/ordre': {
      sc.ordres.push(corps.action);
      if (corps.action === 'config-lire') return [200, { ok: true, r: LU }];
      if (corps.action === 'config-ecrire') return [200, { ok: true, r: { sauvegarde: 'meshtastic-2026-11-27.yaml', redemarre: true } }, sc.delaiEcriture];
      return [200, { ok: true, r: {} }];
    }
    case '/admin-api/theme': case '/admin-api/reglages': case '/admin-api/wifi': case '/admin-api/energie': return [200, {}];
  }
  return null;
}
function fichierStation(meth, u, req, res) {
  const p = u.pathname;
  if (sc.sessionExpiree && /^\/(ajouter|parametres)\//.test(p) && !/\.(html|js|css)$/.test(p) && !p.endsWith('/')) {
    res.writeHead(302, { Location: '/connexion.html?retour=' + p }); res.end(); return true;
  }
  if (p.startsWith('/ajouter/commande/')) {
    // Ordre numerote <ordre>@<numero> : la station repond dans /ajouter/resultats/<numero>.json (prometheus-commande)
    const [ordre, numero] = decodeURIComponent(p.slice(18)).split('@');
    sc.commandes.push(ordre);
    if (sc.systemeMuet && ordre === 'systeme') { req.socket.destroy(); return true; }
    if (ordre === 'systeme' && sc.journalMaj) sc.lecturesMaj = 0, sc.majLancee = true;
    if (numero) (sc.resultats = sc.resultats || {})[numero] = { ordre, etat: /^(systeme|mettre-a-jour|radio-)/.test(ordre) ? 'lance' : 'fait', message: '' };
    res.writeHead(201); res.end(); return true;
  }
  if (p.startsWith('/ajouter/resultats/')) {
    const r = (sc.resultats || {})[p.slice(19).replace(/\.json$/, '')];
    if (!r) { res.writeHead(404); res.end(); return true; }   // pas encore ecrit : la page relit
    res.writeHead(200, { 'Content-Type': 'application/json' }); res.end(JSON.stringify(r)); return true;
  }
  const texte = (code, t, type = 'text/plain; charset=utf-8') => { res.writeHead(code, { 'Content-Type': type, Date: new Date().toUTCString() }); res.end(t); return true; };
  if (p === '/ajouter/etat.json') {
    const e = JSON.parse(JSON.stringify(ETAT)); e.horodatage = maintenant(); e.systeme.a_jour = sc.systemeAJour; e.systeme.paquets = sc.systemeAJour ? ['nginx', 'firmware-brcm80211'] : [];
    return texte(200, JSON.stringify(e), 'application/json');
  }
  if (p === '/ajouter/maj-systeme.txt') {
    if (!sc.journalMaj) return texte(200, '== 20/11/2026 10:00 mise à jour\nRien à faire.\n### FIN 0\n');
    const etapes = sc.majLancee ? sc.journalMaj.apres : sc.journalMaj.avant;
    return texte(200, etapes[Math.min(sc.lecturesMaj++, etapes.length - 1)]);
  }
  if (p === '/ajouter/radio-outil.txt') return texte(200, '== 26/11/2026 12:00 sauvegarde\nRéglages gardés.\n### FIN 0\n');
  if (p === '/ajouter/doublons.json') return texte(200, JSON.stringify({ groupes: [{ garder: 'Candide - Voltaire.pdf', doublons: ['Candide - Voltaire (1).pdf'], taille: 3039000, empreinte: 'e1' }] }), 'application/json');
  if (p === '/bibliotheque/livres.json') return texte(200, JSON.stringify([{ titre: 'Candide', auteur: 'Voltaire', format: 'PDF', lien: '/bibliotheque/lire-pdf.html?l=1' },
    { titre: 'Projet Gutenberg', auteur: 'Classiques', format: 'ZIM', lien: '/encyclopedies/content/gutenberg_fr_all_2026-01/' }]), 'application/json');
  if (p.startsWith('/encyclopedies/catalog/')) return texte(200, CATALOGUE, 'application/xml');
  if (p.startsWith('/encyclopedies/suggest')) return texte(200, JSON.stringify([{ kind: 'path', path: 'Potabilisation', value: 'Potabilisation de l’eau' }]), 'application/json');
  if (p === '/theme.css') return texte(200, fs.readFileSync(path.join(WEB, 'themes', sc.theme + '.css')), 'text/css');
  // vendor/ est telecharge a l'installation (03-wifi-accueil.sh), absent du depot : un QR code de remplacement
  if (p === '/vendor/qrcode.js' && !fs.existsSync(path.join(WEB, 'vendor', 'qrcode.js')))
    return texte(200, 'window.qrcode = function () { return { addData: function () {}, make: function () {}, createSvgTag: function () { return \'<svg viewBox="0 0 1 1"></svg>\'; }, getModuleCount: function () { return 21; }, isDark: function () { return false; } }; };' +
      ' qrcode.stringToBytesFuncs = { \'UTF-8\': function (s) { return s; } };', 'text/javascript');
  return false;
}
const TYPES = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript; charset=utf-8', '.css': 'text/css', '.svg': 'image/svg+xml', '.png': 'image/png', '.ico': 'image/x-icon', '.mjs': 'text/javascript' };
const serveur = http.createServer((req, res) => {
  const u = new URL(req.url, 'http://station'), meth = req.method;
  let corps = '';
  req.on('data', c => { corps += c; });
  req.on('end', () => {
    let d = {}; try { d = corps ? JSON.parse(corps) : {}; } catch (e) { d = corps; }
    const r = (u.pathname.startsWith('/api/') || u.pathname.startsWith('/admin-api/')) && api(meth, u, d);
    if (r) {
      const envoi = () => { res.writeHead(r[0], { 'Content-Type': 'application/json', Date: new Date().toUTCString() }); res.end(JSON.stringify(r[1])); };
      return r[2] ? setTimeout(envoi, r[2]) : envoi();
    }
    if (fichierStation(meth, u, req, res)) return;
    let f = path.join(WEB, decodeURIComponent(u.pathname));
    if (!f.startsWith(WEB)) { res.writeHead(403); return res.end(); }
    if (fs.existsSync(f) && fs.statSync(f).isDirectory()) f = path.join(f, 'index.html');
    if (!fs.existsSync(f)) { res.writeHead(404); return res.end('introuvable'); }
    res.writeHead(200, { 'Content-Type': TYPES[path.extname(f)] || 'application/octet-stream', 'Cache-Control': 'no-store' });
    res.end(fs.readFileSync(f));
  });
});

// ===================================================================== Chrome, par le protocole DevTools
async function lancerChrome() {
  const profil = fs.mkdtempSync(path.join(os.tmpdir(), 'prometheus-chrome-'));
  const chrome = spawn(CHROME, ['--headless=new', '--remote-debugging-port=0', '--user-data-dir=' + profil, '--no-first-run',
    '--no-default-browser-check', '--hide-scrollbars', '--lang=fr-FR', 'about:blank'], { stdio: 'ignore' });
  // Chrome ecrit son port quand il est pret : jusqu'a 60 s (la machine de GitHub est parfois lente a le lancer).
  // Le fichier peut exister encore vide : on attend qu'il contienne un numero.
  const fichierPort = path.join(profil, 'DevToolsActivePort');
  let port = '';
  for (let i = 0; i < 600 && !/^\d+$/.test(port); i++) {
    await attendre(100);
    try { port = fs.readFileSync(fichierPort, 'utf8').split('\n')[0].trim(); } catch (e) { port = ''; }
    if (chrome.exitCode !== null) throw new Error('Chrome s’est arrete au demarrage (code ' + chrome.exitCode + ')');
  }
  if (!/^\d+$/.test(port)) throw new Error('Chrome n’a pas donne son port en 60 s');
  return { chrome, profil, port };
}
async function ouvrirOnglet(port) {
  const t = await (await fetch(`http://127.0.0.1:${port}/json/new?about:blank`, { method: 'PUT' })).json();
  const ws = new WebSocket(t.webSocketDebuggerUrl);
  await new Promise((ok, ko) => { ws.onopen = ok; ws.onerror = ko; });
  let id = 0; const attente = new Map(), ecoutes = [];
  ws.onmessage = e => {
    const m = JSON.parse(e.data);
    if (m.id && attente.has(m.id)) { attente.get(m.id)(m); attente.delete(m.id); }
    else if (m.method) ecoutes.forEach(f => f(m));
  };
  const cmd = (method, params = {}) => new Promise((ok, ko) => {
    const i = ++id; attente.set(i, m => (m.error ? ko(new Error(method + ' : ' + m.error.message)) : ok(m.result)));
    ws.send(JSON.stringify({ id: i, method, params }));
  });
  return { cmd, ecouter: f => ecoutes.push(f), fermer: async () => { ws.close(); await fetch(`http://127.0.0.1:${port}/json/close/${t.id}`); } };
}

// ===================================================================== Les pages
// Le texte de la page sans scripts ni styles : on y cherche « undefined », « NaN », « [object »
const TEXTE_PAGE = `(() => { const c = document.body.cloneNode(true); c.querySelectorAll('script,style,template').forEach(x => x.remove());
  const t = c.textContent, f = []; const m = /.{0,40}\\b(undefined|NaN|\\[object \\w+\\])\\b.{0,40}/.exec(t); if (m) f.push('texte suspect : « ' + m[0].replace(/\\s+/g, ' ') + ' »');
  document.querySelectorAll('input,textarea').forEach(i => { if (/undefined|NaN/.test(i.value)) f.push('champ ' + (i.id || i.name) + ' = ' + i.value); });
  return f; })()`;
const remplis = sels => `(() => { const f = []; ${JSON.stringify(sels)}.forEach(s => { const e = document.querySelectorAll(s); if (!e.length) f.push(s + ' : absent');
  e.forEach(x => { const t = x.textContent.trim(); if (!t || t === '…') f.push(s + ' : vide (« ' + t + ' »)'); }); }); return f; })()`;
// v : expression qui doit valoir vrai ; texte : ce qu'on attendait
const vrai = (expr, texte) => `(() => { try { return (${expr}) ? [] : [${JSON.stringify(texte)} + ' — trouvé : ' + JSON.stringify(String((() => { try { return ${expr.split('===')[0]}; } catch (e) { return e.message; } })()).slice(0, 120))]; } catch (e) { return [${JSON.stringify(texte)} + ' — ' + e.message]; } })()`;
const txt = s => `(document.querySelector(${JSON.stringify(s)}) || {}).textContent`;

const PAGES = [
  // ----- Pages des visiteurs
  { nom: 'accueil', url: '/', verifs: [vrai(`!document.getElementById('porte-registre').hidden`, 'la porte du registre est ouverte')] },
  { nom: 'connexion', url: '/connexion.html' },
  { nom: 'panneau', url: '/panneau/', verifs: [remplis(['#panneau'])] },
  { nom: 'urgence', url: '/urgence/', verifs: [vrai(`document.querySelectorAll('#urgences a').length > 0`, 'des raccourcis d’urgence')] },
  { nom: 'messages', url: '/messages/', verifs: [vrai(`document.querySelectorAll('#fil .msg').length === 2`, '2 messages'), remplis(['#fil .date'])] },
  { nom: 'ecran', url: '/ecran/', attente: 1500, verifs: [remplis(['#heure', '#date']),
    vrai(`[...document.querySelectorAll('.pave .info')].some(x => /Meshtastic/.test(x.textContent))`, 'l’état de la radio sur un pavé')] },
  { nom: 'ajouter', url: '/ajouter/', verifs: [vrai(`/3,0 Mo/.test(${txt('#doublons')})`, 'la taille du doublon en Mo (règle des 1000)')],
    gestes: async p => {
      await p.eval(`document.querySelector('#doublons .bouton').click()`);
      return [await p.verif(vrai(`document.querySelector('#doublons .bouton').classList.contains('confirmer') && /Toucher encore/.test(${txt('#doublons .bouton')})`, '1er toucher : bouton armé'))];
    } },
  { nom: 'encyclopedies', url: '/encyclopedies/', verifs: [vrai(`document.querySelectorAll('#liste li').length === 3`, '3 encyclopédies')],
    gestes: async p => {
      await p.eval(`const r = document.getElementById('recherche'); r.value = 'eau'; r.dispatchEvent(new Event('input'))`); await attendre(800);
      return [await p.verif(vrai(`document.querySelectorAll('#resultats li').length >= 1`, 'des résultats de recherche'))];
    } },
  { nom: 'bibliotheque', url: '/bibliotheque/', verifs: [vrai(`document.querySelectorAll('#livres li').length === 2`, '2 livres')] },
  { nom: 'registre (effacement refusé)', url: '/registre/', avant: `localStorage.setItem('cles-registre', JSON.stringify({ f1: 'cle-f1' }))`,
    scenario: { effacerRefuse: true }, erreursPermises: [/status of 403/],
    verifs: [vrai(`document.querySelectorAll('.fiche').length === 2`, '2 fiches')],
    gestes: async p => {
      const b = `document.querySelector('.fiche .effacer')`;   // seule la fiche f1 a sa cle sur ce telephone
      const f = [await p.verif(vrai(`/ma fiche/.test(${b}.textContent)`, '« Effacer ma fiche » sur la fiche de ce téléphone'))];
      await p.eval(`${b}.click()`);
      f.push(await p.verif(vrai(`/Toucher encore/.test(${b}.textContent)`, '1er toucher : « Toucher encore »')));
      await p.eval(`${b}.click()`); await attendre(800);
      f.push(await p.verif(vrai(`JSON.parse(localStorage.getItem('cles-registre')).f1 === 'cle-f1'`, 'la clé reste sur le téléphone quand la station refuse')));
      f.push(await p.verif(vrai(`/Effacement refusé/.test(document.body.textContent)`, 'le refus est dit')));
      return f;
    } },
  { nom: 'entraide (effacement accepté)', url: '/entraide/', avant: `localStorage.setItem('cles-entraide', JSON.stringify({ a1: 'cle-a1' }))`,
    verifs: [vrai(`document.querySelectorAll('.fiche').length === 1`, '1 annonce')],
    gestes: async p => {
      const b = `document.querySelector('.fiche .effacer')`;
      await p.eval(`${b}.click()`); await p.eval(`${b}.click()`); await attendre(800);
      return [await p.verif(vrai(`!JSON.parse(localStorage.getItem('cles-entraide')).a1`, 'la clé est retirée après un effacement réussi'))];
    } },
  // ----- Parametres
  { nom: 'parametres accueil (nuit, radio qui démarre)', url: '/parametres/', theme: 'nuit', largeur: 1100, capture: 'parametres-accueil-nuit.png',
    scenario: { radioEtat: 'eteinte' }, attente: 2500,
    verifs: [remplis(['#etat-texte', '.tuile-chiffre', '#val-stockage', '#val-energie', '#sante-allumee']),
      vrai(`${txt('#val-radio')} === 'Démarrage…'`, 'la ligne Radio dit « Démarrage… »'),
      vrai(`${txt('#tuile-radio .tuile-chiffre')} === 'Démarrage…' && !document.getElementById('tuile-radio').classList.contains('alerte')`, 'la tuile Radio dit « Démarrage… », sans alerte'),
      vrai(`/allumée depuis 2 j 8 h/.test(${txt('#etat-texte')})`, 'durée d’allumage « 2 j 8 h »'),
      vrai(`/extinction 2 h/.test(${txt('#val-energie')}) && /Extinction dans 2 h si/.test(${txt('#note-extinction')})`, 'extinction « 2 h » (7170 s : plus « 1 h 60 »)')] },
  { nom: 'parametres accueil (neutre, mobile)', url: '/parametres/', largeur: 400, capture: 'parametres-accueil-neutre.png', attente: 3000,
    verifs: [vrai(`${txt('#val-radio')} === 'Prometheus 7a3c'`, 'la ligne Radio donne le nom de la radio'), vrai(`${txt('#tuile-radio .tuile-chiffre')} === 'En marche'`, 'tuile Radio « En marche »')] },
  { nom: 'parametres stockage (nuit)', url: '/parametres/#stockage', theme: 'nuit', largeur: 1100, capture: 'parametres-stockage-nuit.png', attente: 2000,
    verifs: [remplis(['#legende-place small', '#liste-fichiers .sous', '#sauvegarde-date']), vrai(`/127 Go/.test(${txt('#legende-place')})`, 'taille « 127 Go »'),
      vrai(`/3 Ko/.test(${txt('#sauvegarde-date')})`, 'sauvegarde « 3 Ko »')],
    gestes: async p => {
      const b = `document.querySelector('#liste-fichiers .supprimer')`;
      await p.eval(`${b}.click()`);
      const f = [await p.verif(vrai(`${b}.classList.contains('confirmer') && ${b}.textContent === 'Confirmer'`, '1er toucher arme « Supprimer »'))];
      await p.capture('parametres-stockage-arme-nuit.png');
      await attendre(5300);
      f.push(await p.verif(vrai(`${b}.textContent === 'Supprimer' && !${b}.classList.contains('confirmer')`, 'revient seul après 5 s')));
      return f;
    } },
  { nom: 'parametres confirmation « tout effacer » (nuit)', url: '/parametres/#effacer', theme: 'nuit', largeur: 420, attente: 1500, capture: 'parametres-effacer-nuit.png',
    gestes: async p => {
      await p.eval(`document.getElementById('bouton-effacer-tout').click()`); await attendre(300);
      await p.capture('parametres-effacer-nuit.png');
      return [await p.verif(vrai(`getComputedStyle(document.getElementById('confirmation-effacer')).backgroundColor !== 'rgb(255, 245, 245)'`, 'le fond de la confirmation suit le thème nuit'))];
    } },
  { nom: 'parametres mise à jour : station muette', url: '/parametres/#logiciels', scenario: { systemeMuet: true, systemeAJour: 2 }, attente: 1500,
    erreursPermises: [/ERR_EMPTY_RESPONSE|Failed to fetch|ERR_CONNECTION/],
    gestes: async p => {
      await p.eval(`document.getElementById('bouton-systeme').click()`); await attendre(1500);
      return [await p.verif(vrai(`!document.getElementById('bouton-systeme').disabled && ${txt('#bouton-systeme')} === 'Mettre à jour'`, 'le bouton ne reste pas sur « Lancement… »')),
              await p.verif(vrai(`/ne répond pas/.test(${txt('#resultat-maj')}) && !document.getElementById('resultat-maj').hidden`, 'la panne est dite'))];
    } },
  { nom: 'parametres mise à jour : bilan en clair', url: '/parametres/#logiciels', scenario: { systemeAJour: 2, journalMaj: {
      avant: ['== 20/11/2026 10:00 mise à jour\nRien.\n### FIN 0\n'],
      apres: ['== 27/11/2026 10:00 mise à jour\nUnpacking nginx (1.26)', '== 27/11/2026 10:00 mise à jour\nUnpacking nginx (1.26)\nSetting up nginx (1.26)\nSetting up firmware-brcm80211 (1)\n### FIN 0\n'] } },
    attente: 1500,
    gestes: async p => {
      await p.eval(`document.getElementById('bouton-systeme').click()`); await attendre(7000);
      return [await p.verif(vrai(`/Tout s’est bien passé/.test(${txt('#resultat-maj')}) && /2 programmes mis à jour \\(serveur web, pilotes du wifi et du Bluetooth\\)/.test(${txt('#resultat-maj')})`, 'bilan en clair sous le détail')),
              await p.verif(vrai(`/Setting up nginx/.test(${txt('#console-maj')})`, 'le détail reste affiché'))];
    } },
  { nom: 'parametres session expirée', url: '/parametres/', scenario: { sessionExpiree: true }, attente: 2500, erreursPermises: [/status of 401/], sansTexte: true,
    verifs: [vrai(`location.pathname === '/connexion.html' && new URLSearchParams(location.search).get('retour') === '/parametres/'`, 'retour à la connexion avec l’adresse de retour')] },
  { nom: 'affiche', url: '/parametres/affiche.html', attente: 1200 },
  // ----- Section Mesh
  { nom: 'mesh vue d’ensemble (nuit)', url: '/parametres/mesh/', theme: 'nuit', capture: 'mesh-ensemble-nuit.png', attente: 2000,
    verifs: [remplis(['#reseau', '#etat dd']), vrai(`/Connectée depuis/.test(${txt('#etat')}) && /2 h(?! 60)/.test(${txt('#etat')})`, 'connectée depuis « 2 h » (7170 s)')] },
  { nom: 'mesh vue d’ensemble (radio qui démarre)', url: '/parametres/mesh/', scenario: { radioEtat: 'eteinte' }, attente: 1500,
    verifs: [vrai(`/se connecte à la radio/.test(${txt('#reseau')})`, 'la ligne du haut dit que la radio démarre'),
      vrai(`/Démarrage…/.test(${txt('#etat')})`, 'l’état dit « Démarrage… »')] },
  { nom: 'mesh vue d’ensemble (garde-fou abandonné)', url: '/parametres/mesh/', attente: 1500,
    scenario: { gardeFou: { etat: 'abandon', heure: n() - 1900, raison: 'région', fichier: 'meshtastic-2026-11-27.yaml', demandes: 3 } },
    verifs: [vrai(`/rebranchez-la/.test(${txt('#garde-fou')}) && document.getElementById('garde-fou').className === 'avertir' && !document.getElementById('garde-fou').hidden`, 'abandon : la consigne, en orange'),
      vrai(`/ne revient pas/.test(${txt('#reseau')})`, 'la ligne du haut le dit')] },
  { nom: 'mesh noeuds', url: '/parametres/mesh/noeuds.html', attente: 1500, verifs: [vrai(`document.querySelectorAll('#liste .ligne-m').length === 2`, '2 radios')] },
  { nom: 'mesh messages', url: '/parametres/mesh/messages.html', attente: 1500, verifs: [vrai(`/Bonjour la station/.test(${txt('#journal')})`, 'le journal radio')] },
  { nom: 'mesh canaux', url: '/parametres/mesh/canaux.html', attente: 1500, verifs: [vrai(`/Famille/.test(${txt('#contenu')})`, 'les canaux')],
    gestes: async p => {
      const b = `[...document.querySelectorAll('.lien.danger')][0]`;
      await p.eval(`${b}.click()`);
      return [await p.verif(vrai(`${b}.classList.contains('confirmer')`, 'supprimer un canal : 1er toucher arme'))];
    } },
  { nom: 'mesh configuration (écriture longue)', url: '/parametres/mesh/config.html', scenario: { delaiEcriture: 9500 }, attente: 1500,
    verifs: [remplis(['#contenu .section-config summary b'])],
    gestes: async p => {
      await p.eval(`const s = document.getElementById('c-config-lora-region'); s.value = 'UNSET'; s.dispatchEvent(new Event('change'))`);
      const b = `[...document.querySelectorAll('.barre-ecrire .bouton')].find(x => !x.classList.contains('secondaire'))`;
      await p.eval(`${b}.click()`);
      const f = [await p.verif(vrai(`${b}.classList.contains('confirmer') && /Attention/.test(${txt('#ecr-res')})`, 'réglage risqué : avertissement et 2e toucher demandé'))];
      await p.eval(`${b}.click()`); await attendre(8800);
      f.push(await p.verif(vrai(`${b}.textContent === 'Écriture…' && ${b}.disabled`, 'pendant une écriture de plus de 8 s, le bouton dit toujours « Écriture… »')));
      await attendre(1500);
      f.push(await p.verif(vrai(`${b}.textContent === 'Écrire dans la radio' && /Fait/.test(${txt('#ecr-res')})`, 'après l’écriture : « Fait » et le bouton revient')));
      return f;
    } },
  { nom: 'mesh modules', url: '/parametres/mesh/modules.html', attente: 1500, verifs: [remplis(['#contenu .section-config summary b'])] },
  { nom: 'mesh statistiques', url: '/parametres/mesh/stats.html', attente: 1500, verifs: [vrai(`/2,4 Mo/.test(${txt('#resume')})`, 'taille de l’historique « 2,4 Mo »')] },
  { nom: 'mesh atelier', url: '/parametres/mesh/atelier.html', attente: 1500 },
  { nom: 'mesh à distance', url: '/parametres/mesh/distance.html?id=!11223344', attente: 1500 },
  { nom: 'mesh journal technique', url: '/parametres/mesh/technique.html', attente: 1500, verifs: [vrai(`/Bonjour/.test(${txt('#paquets')})`, 'un paquet')] }
];

// ===================================================================== Deroulement
let fautesTotal = 0;
const { chrome, profil, port } = await lancerChrome();
await new Promise(r => serveur.listen(0, '127.0.0.1', r));
const BASE = 'http://127.0.0.1:' + serveur.address().port;
try {
  for (const page of PAGES) {
    if (SEULEMENT && !page.nom.includes(SEULEMENT)) continue;
    sc = Object.assign(scenarioDeBase(), page.scenario || {}, { theme: page.theme || 'neutre' });
    const o = await ouvrirOnglet(port), fautes = [];
    o.ecouter(m => {
      const permis = t => (page.erreursPermises || []).some(r => r.test(t));
      if (m.method === 'Runtime.exceptionThrown') {
        const d = m.params.exceptionDetails, t = ((d.exception && d.exception.description) || d.text) + ' @' + (d.url || '') + ':' + d.lineNumber;
        if (!permis(t)) fautes.push('exception : ' + t.split('\n')[0]);
      }
      if (m.method === 'Runtime.consoleAPICalled' && m.params.type === 'error') {
        const t = m.params.args.map(a => a.value || a.description).join(' ');
        if (!permis(t)) fautes.push('console.error : ' + t);
      }
      if (m.method === 'Log.entryAdded' && m.params.entry.level === 'error') {
        const t = m.params.entry.text + ' ' + (m.params.entry.url || '');
        if (!permis(t)) fautes.push('console : ' + t);
      }
    });
    await o.cmd('Runtime.enable'); await o.cmd('Log.enable'); await o.cmd('Page.enable');
    // Les pages suivent la langue du navigateur : --lang ne suffit pas partout (Chrome de GitHub, sous Linux, reste
    // en anglais). Les verifications sont ecrites en francais : on donne le francais a chaque page, quelle que soit la machine.
    await o.cmd('Page.addScriptToEvaluateOnNewDocument', { source: "try { if (!localStorage.getItem('langue')) localStorage.setItem('langue', 'fr'); } catch (e) {}" });
    await o.cmd('Emulation.setDeviceMetricsOverride', { width: page.largeur || 420, height: 900, deviceScaleFactor: 1, mobile: false });
    if (page.avant) await o.cmd('Page.addScriptToEvaluateOnNewDocument', { source: `if (location.origin === '${BASE}') { ${page.avant} }` });
    await o.cmd('Page.navigate', { url: BASE + page.url });
    await attendre(page.attente || 1200);
    const p = {
      eval: async e => { const r = await o.cmd('Runtime.evaluate', { expression: e, awaitPromise: true, returnByValue: true }); if (r.exceptionDetails) throw new Error(r.exceptionDetails.exception ? r.exceptionDetails.exception.description : r.exceptionDetails.text); return r.result.value; },
      // Une verification est rejouee (toutes les 250 ms, 8 s au plus) tant qu'elle echoue : la machine peut etre
      // chargee, on n'attend jamais un temps fixe pour conclure qu'une chose ne s'est pas faite
      verif: async (e, delai = 8000) => {
        const fin = Date.now() + delai; let r;
        for (;;) {
          try { r = (await p.eval(e)) || []; } catch (x) { r = ['verification impossible : ' + x.message.split('\n')[0]]; }
          if (!r.length || Date.now() > fin) return r;
          await attendre(250);
        }
      },
      capture: async nom => { const r = await o.cmd('Page.captureScreenshot', { format: 'png', captureBeyondViewport: true }); fs.writeFileSync(path.join(CAPTURES, nom), Buffer.from(r.data, 'base64')); }
    };
    try {
      await p.verif(`document.readyState === 'complete' ? [] : ['page pas encore chargee']`, 10000);
      if (!page.sansTexte) fautes.push(...await p.verif(TEXTE_PAGE));
      for (const v of page.verifs || []) fautes.push(...await p.verif(v));
      if (page.gestes) (await page.gestes(p)).forEach(x => fautes.push(...x));
      if (!page.sansTexte) fautes.push(...await p.verif(TEXTE_PAGE));
      if (page.capture && !/effacer/.test(page.capture)) await p.capture(page.capture);
    } catch (e) { fautes.push('verification impossible : ' + e.message.split('\n')[0]); }
    await o.fermer();
    fautesTotal += fautes.length;
    console.log((fautes.length ? '✖ ' : '✔ ') + page.nom + (page.capture ? '  [' + path.join(CAPTURES, page.capture) + ']' : ''));
    [...new Set(fautes)].forEach(f => console.log('    - ' + f));
  }
} finally {
  chrome.kill(); serveur.close();
  await attendre(500);
  fs.rmSync(profil, { recursive: true, force: true });
}
console.log(fautesTotal ? `\n${fautesTotal} faute(s).` : '\nAucune faute.');
process.exit(fautesTotal ? 1 : 0);
