// Prometheus Station - ce que toutes les pages partagent (27/11/2026). Necessite /langue.js (T, TE, LANGUE), charge avant.
// Une regle = un seul endroit. Ce fichier remplace les copies qui s'etaient multipliees dans les pages et qui avaient
// fini par se contredire :
//  - $ et el (5 versions ; certaines n'affichaient pas le chiffre 0) ;
//  - les echanges avec la station : 5 copies de « poster », et des lectures qui ignoraient les erreurs (une session
//    expiree affichait « undefined °C » au lieu de ramener a la connexion) ;
//  - le bouton en deux temps (11 copies : 3 delais, 2 marques, des minuteurs jamais arretes qui remettaient
//    « Écrire dans la radio » pendant l'ecriture) ;
//  - les durees, heures et tailles (2 regles pour les Mo, « 1 h 60 » affiche) ;
//  - le texte de l'etat de la radio (5 textes qui disaient « démarrage », « ne répond pas » et « désactivée »
//    pour la meme radio) ;
//  - le suivi d'une operation longue par son journal (2 copies, dont une restait bloquee sans reseau).
// annonce.js reste a part : nginx l'injecte dans les pages de Kiwix, ou ce fichier n'est pas charge.

// ===================================================================== Page
function $(id) { return document.getElementById(id); }
// el('dd', 'valeur', 0) affiche bien « 0 » : seuls undefined et null ne mettent pas de texte
function el(tag, classe, texte) {
  var e = document.createElement(tag);
  if (classe) e.className = classe;
  if (texte !== undefined && texte !== null) e.textContent = texte;
  return e;
}

// ===================================================================== Echanges avec la station
// Une seule porte pour parler a la station :
//   lire(url)                     -> promesse des donnees JSON ; rejetee (Error avec .code) si la station refuse ou se tait
//   lireTexte(url)                -> promesse du texte ; rejetee de meme
//   lireJournal(url)              -> promesse du texte d'un journal : '' s'il n'existe pas, null si la station se tait
//   envoyer(url, donnees, methode)-> promesse {ok, code, d, erreur, heure}, jamais rejetee : erreur est deja une phrase
//                                    a montrer (traduite) ; heure = heure de la station (en-tete Date, en secondes).
//                                    donnees : un objet part en JSON ; un texte ou un fichier part tel quel (PUT des ordres)
// Session expiree sur une page d'administration (/parametres/, /ajouter/ : 401, ou nginx qui renvoie vers la
// connexion) : on va a la page de connexion, qui ramene ici ensuite (?retour=, verifie par connexion.html).
// Une page des visiteurs peut demander une adresse d'administration pour voir (l'ecran de la station montre la
// temperature si l'administrateur est connecte) : un refus y reste un simple refus, sans renvoi. Sur la page de
// connexion, un 401 veut dire « mauvais mot de passe ».
function stationMuette() { return T('La station ne répond pas.', 'The station does not respond.'); }
function allerConnexion() {
  location.href = '/connexion.html?retour=' + encodeURIComponent(location.pathname + location.search + location.hash);
}
function sessionPerdue(r) {
  var refus = r.status === 401 || (r.redirected && /\/connexion\.html/.test(r.url || ''));
  return refus && /^\/(parametres|ajouter)\//.test(location.pathname);
}
function echangeStation(url, options, enTexte) {
  options.cache = 'no-store';
  return fetch(url, options).then(function (r) {
    var heure = Date.parse((r.headers && r.headers.get('Date')) || '') / 1000 || 0;
    if (sessionPerdue(r)) {
      allerConnexion();
      return { ok: false, code: 401, d: {}, erreur: TE('Connectez-vous d’abord.'), heure: heure };
    }
    return r.text().then(function (texte) {
      var d = texte;
      if (!enTexte) { try { d = texte ? JSON.parse(texte) : {}; } catch (e) { d = {}; } }
      var erreur = '';
      if (!r.ok) erreur = TE((d && d.erreur) || '') || (r.status >= 500 ? stationMuette() : T('Erreur ', 'Error ') + r.status + '.');
      return { ok: r.ok, code: r.status, d: d, erreur: erreur, heure: heure };
    });
  }).catch(function () { return { ok: false, code: 0, d: {}, erreur: stationMuette(), heure: 0 }; });
}
function refusStation(x) { var e = new Error(x.erreur); e.code = x.code; return e; }
function lire(url) { return echangeStation(url, {}).then(function (x) { if (!x.ok) throw refusStation(x); return x.d; }); }
function lireTexte(url) { return echangeStation(url, {}, true).then(function (x) { if (!x.ok) throw refusStation(x); return x.d; }); }
function lireJournal(url) {
  return lireTexte(url + (url.indexOf('?') < 0 ? '?' : '&') + Date.now()).catch(function (e) { return e.code ? '' : null; });
}
function envoyer(url, donnees, methode) {
  var o = { method: methode || 'POST' };
  if (donnees !== null && typeof donnees === 'object' && !(typeof Blob !== 'undefined' && donnees instanceof Blob)) {
    o.headers = { 'Content-Type': 'application/json' }; o.body = JSON.stringify(donnees);
  } else if (donnees !== undefined) o.body = donnees;
  return echangeStation(url, o);
}

// ===================================================================== Bouton en deux temps
// Pour ce qui coupe, efface ou remplace : le 1er toucher arme le bouton (classe « confirmer », texte de confirmation),
// un 2e toucher dans le delai fait l'action ; sinon le bouton revient seul a son texte. Le minuteur est arrete des
// le 2e toucher : le texte que l'action met ensuite (« Écriture… ») n'est plus jamais ecrase.
//   if (!deuxTemps(b, {texte: ...})) return;   au debut d'un gestionnaire (clic ou envoi de formulaire)
//   deuxTemps(b, {texte: ..., action: f})     pose lui-meme b.onclick
// o : texte (bouton arme), delai (ms), si (faut-il confirmer ? valeur ou fonction ; par defaut oui),
//     avertir() au 1er toucher, retour() quand le delai passe sans 2e toucher, action() (voir plus haut).
// Delai : 5 s partout ; 8 s pour un reglage risque de la radio (DELAI_RISQUE) : il faut d'abord lire l'avertissement
// ecrit sous le bouton (plusieurs phrases quand plusieurs reglages risques changent).
var DELAI_DEUX_TEMPS = 5000, DELAI_RISQUE = 8000;
function deuxTemps(b, o) {
  if (o.action) {
    b.onclick = function (ev) { if (armerOuConfirmer(b, o)) o.action.call(b, ev); };
    return;
  }
  return armerOuConfirmer(b, o);
}
function armerOuConfirmer(b, o) {
  var si = typeof o.si === 'function' ? o.si() : o.si;
  var arme = b._deuxTemps;
  if (arme) {   // 2e toucher (ou plus besoin de confirmer) : on desarme et on laisse faire
    clearTimeout(arme.minuteur); b._deuxTemps = null;
    b.classList.remove('confirmer'); b.textContent = arme.texte;
    return true;
  }
  if (o.si !== undefined && !si) return true;
  arme = b._deuxTemps = { texte: b.textContent };
  b.classList.add('confirmer');
  if (o.texte) b.textContent = o.texte;
  if (o.avertir) o.avertir();
  arme.minuteur = setTimeout(function () {
    if (b._deuxTemps !== arme) return;
    b._deuxTemps = null; b.classList.remove('confirmer'); b.textContent = arme.texte;
    if (o.retour) o.retour();
  }, o.delai || DELAI_DEUX_TEMPS);
  return false;
}

// ===================================================================== Durees, heures, tailles
// Ici plutot que dans langue.js : langue.js ne fait que choisir la langue et traduire ; ces formats en dependent
// (T, LOC) mais servent aux donnees de la station. Le francais ou l'anglais britannique (jour/mois, 24 h).
var LOC = LANGUE === 'en' ? 'en-GB' : 'fr-FR';
var ecart = 0;   // heure de la station - heure du telephone (secondes) ; les pages le posent a chaque lecture
function maintenant() { return Date.now() / 1000 + ecart; }
function virgule(x, n) { return (typeof x === 'number' ? x.toFixed(n === undefined ? 1 : n) : String(x)).replace('.', T(',', '.')); }
function deuxChiffres(n) { return (n < 10 ? '0' : '') + n; }
// « 45 min », « 2 h 05 », « 3 j 4 h ». On arrondit UNE fois (a la minute, ou a l'heure au-dela d'un jour), puis on
// decoupe : jamais « 1 h 60 » ni « 1 j 24 h ». Moins d'une minute mais pas zero : « 1 min ».
function duree(s) {
  s = Math.max(0, +s || 0);
  var m = Math.round(s / 60);
  if (s > 0 && !m) m = 1;
  if (m < 60) return m + ' min';
  if (m < 1440) return Math.floor(m / 60) + ' h' + (m % 60 ? ' ' + deuxChiffres(m % 60) : '');
  var h = Math.round(s / 3600);
  return Math.floor(h / 24) + T(' j', ' d') + (h % 24 ? ' ' + h % 24 + ' h' : '');
}
// « il y a 4 min » (on compte les minutes entieres ecoulees : jamais « il y a 60 min ») ; au-dela d'une semaine, la date
function ilya(t) {
  if (!t) return '—';
  var s = Math.max(0, maintenant() - t);
  if (s < 60) return T('à l’instant', 'just now');
  if (s < 3600) return T('il y a ', '') + Math.floor(s / 60) + T(' min', ' min ago');
  if (s < 86400) return T('il y a ', '') + Math.floor(s / 3600) + T(' h', ' h ago');
  if (s < 7 * 86400) return T('il y a ', '') + Math.floor(s / 86400) + T(' j', ' d ago');
  return new Date(t * 1000).toLocaleDateString(LOC, { day: 'numeric', month: 'short' });
}
// L'heure ; la date devant si ce n'est pas aujourd'hui (jour de la station)
function heure(t) {
  var d = new Date(t * 1000), auj = new Date(maintenant() * 1000).toDateString() === d.toDateString();
  return (auj ? '' : d.toLocaleDateString(LOC, { day: 'numeric', month: 'short' }) + ' ') + d.toLocaleTimeString(LOC, { hour: '2-digit', minute: '2-digit' });
}
function heureSec(t) { return new Date(t * 1000).toLocaleTimeString(LOC, { hour: '2-digit', minute: '2-digit', second: '2-digit' }); }
function dateCourte(t) { return t ? new Date(t * 1000).toLocaleString(LOC, { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' }) : T('aucun', 'none'); }
// Tailles de fichiers : 1 Go = 1 000 000 000 octets, comme la place sur la carte que la station donne (en Go de
// 1000 Mo) : les tailles des fichiers et de la carte s'additionnent sans ecart. « 3,4 Go », « 127 Go », « 850 Ko ».
// Une decimale sous 10 ; l'unite est choisie APRES l'arrondi (jamais « 1000 Ko » ni « 10,0 Go »).
function taille(o) {
  o = Math.max(0, +o || 0);
  var k = Math.round(o / 1e3);
  if (k < 1000) return (o && !k ? 1 : k) + T(' Ko', ' KB');
  var unites = [[1e6, T(' Mo', ' MB')], [1e9, T(' Go', ' GB')], [1e12, T(' To', ' TB')]];
  for (var i = 0; i < unites.length; i++) {
    var x = o / unites[i][0], r = Math.round(x * 10) / 10;
    if (Math.round(x) < 1000 || i === unites.length - 1) return (r < 10 ? virgule(r, 1) : String(Math.round(x))) + unites[i][1];
  }
}
// Taille d'un texte en octets (UTF-8) : la limite des messages radio se compte ainsi
function octets(t) { return new TextEncoder().encode(t).length; }

// ===================================================================== Etat de la radio
// d : l'etat donne par la station (/api/radio, ou .etat de /admin-api/radio) : {active, etat, nom}.
// -> {court : un ou deux mots, detail : une precision, genre : 'bien' | 'alerte' | 'attente' | 'eteinte'}
// La station dit « eteinte » pendant la dizaine de secondes qui suit l'activation (etat pas encore connu) :
// la radio est alors en train de demarrer, partout pareil.
function texteRadio(d) {
  d = d || {};
  if (!d.active) return { court: T('Désactivée', 'Off'), detail: T('messages par radio désactivés', 'radio messages turned off'), genre: 'eteinte' };
  if (d.etat === 'ok') return { court: T('En marche', 'On'), detail: d.nom || T('radio branchée', 'radio plugged in'), genre: 'bien' };
  if (d.etat === 'absente') return { court: T('Débranchée', 'Unplugged'), detail: T('radio pas branchée', 'radio not plugged in'), genre: 'alerte' };
  if (d.etat === 'muette') return { court: T('Ne répond pas', 'Not answering'), detail: T('radio branchée mais muette', 'radio plugged in but silent'), genre: 'alerte' };
  return { court: T('Démarrage…', 'Starting…'), detail: T('la station se connecte à la radio', 'the station is connecting to the radio'), genre: 'attente' };
}

// ===================================================================== Operation longue suivie par son journal
// Une operation (mise a jour du systeme, outil radio) ecrit son detail dans un journal qui finit par « ### FIN <code> ».
// suivreJournal(url, o) relit le journal toutes les 2 s jusqu'a la fin.
// o : lancer() -> promesse {ok, erreur} (un envoyer(...)) : on note d'abord le debut du journal d'avant, puis on lance ;
//     debutAvant : sans lancer, 1re ligne du journal d'avant (null : reprise a l'ouverture de la page) ;
//     surTexte(texte) a chaque nouveau texte, surFin(code, texte) a la fin (code 0 = reussi),
//     surRien(raison) : 'deja-fini' (reprise, mais c'etait fini) ou 'pas-demarre' (rien de nouveau dans le delai),
//     surPanne(message) : le lancement n'a pas abouti (station muette, refus) ; delaiDemarrage (ms, 30 s).
// ----- Les ordres des boutons (prometheus-commande, 27/11/2026) : chaque ordre porte un numero et la station
// repond dans /ajouter/resultats/<numero>.json : {etat: fait | lance | attente | refuse | inconnu, message}.
// « attente » : une operation radio tourne deja, celle-ci partira juste apres (rien n'est perdu).
function commander(nom, contenu) {
  var id = Date.now().toString(36) + Math.random().toString(36).slice(2, 10);
  return envoyer('/ajouter/commande/' + nom + '@' + id, contenu || '', 'PUT').then(function (r) { r.id = id; return r; });
}
// La reponse d'un ordre, ou null si elle n'est pas venue dans le delai (la page continue alors comme avant)
function resultatOrdre(id, delai) {
  var fin = Date.now() + (delai || 20000);
  return new Promise(function (ok) {
    (function tour() {
      echangeStation('/ajouter/resultats/' + id + '.json', {}).then(function (x) {
        if (x.ok && x.d && x.d.etat) { ok(x.d); return; }
        if (Date.now() > fin) { ok(null); return; }
        setTimeout(tour, 1000);
      });
    })();
  });
}
function ordreRefuse(res) { return !!res && (res.etat === 'refuse' || res.etat === 'inconnu'); }

var FIN_JOURNAL = /### FIN (-?\d+)\s*$/;
function suivreJournal(url, o) {
  var ordre_ = { attente: false, stop: false };
  if (o.lancer) {
    lireJournal(url).then(function (texte) {
      var debut = (texte || '').split('\n')[0];
      return Promise.resolve(o.lancer()).then(function (r) {
        if (r && r.ok === false) { if (o.surPanne) o.surPanne(r.erreur || stationMuette()); return; }
        // Un ordre numerote : la station dit s'il est refuse, ou s'il attend la fin d'une autre operation
        if (r && r.id) resultatOrdre(r.id, 15000).then(function (res) {
          if (ordreRefuse(res)) { ordre_.stop = true; if (o.surPanne) o.surPanne(res.message); }
          else if (res && res.etat === 'attente') { ordre_.attente = true; if (o.surAttente) o.surAttente(res.message); }
        });
        suivre(debut);
      });
    }).catch(function () { if (o.surPanne) o.surPanne(stationMuette()); });
    return;
  }
  suivre(o.debutAvant === undefined ? null : o.debutAvant);

  function suivre(debutAvant) {
    var depart = Date.now(), vueEnCours = false;
    (function tour() {
      if (ordre_.stop) return;
      lireJournal(url).then(function (texte) {
        if (texte === null) { setTimeout(tour, 3000); return; }   // la station se tait un moment : on reessaie
        var nouveau = texte.split('\n')[0] !== debutAvant, fin = nouveau && FIN_JOURNAL.exec(texte);
        if (fin && debutAvant === null && !vueEnCours) { if (o.surRien) o.surRien('deja-fini'); return; }
        if (!fin) vueEnCours = vueEnCours || nouveau;
        if (nouveau && o.surTexte) o.surTexte(texte);
        if (fin) { if (o.surFin) o.surFin(+fin[1], texte); return; }
        // En attente d'une autre operation radio : elle partira ensuite, on laisse 30 min au lieu de 30 s
        if (!nouveau && Date.now() - depart > (ordre_.attente ? 1800000 : o.delaiDemarrage || 30000)) { if (o.surRien) o.surRien('pas-demarre'); return; }
        setTimeout(tour, 2000);
      });
    })();
  }
}
