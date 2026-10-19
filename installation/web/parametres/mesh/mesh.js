// Prometheus Station - section Mesh : ce que toutes ses pages partagent (plan Mesh, 19/10/2026).
// Navigation, version legere / complete, ordres a la radio (prometheus-admin -> prometheus-radio), outil radio
// (operations longues, detail qui defile), petits graphiques. Necessite /langue.js (T, LANGUE, TE).
function $(id) { return document.getElementById(id); }
function el(tag, classe, texte) { var e = document.createElement(tag); if (classe) e.className = classe; if (texte !== undefined && texte !== null) e.textContent = texte; return e; }
var LOC = LANGUE === 'en' ? 'en-GB' : 'fr-FR';
var ecart = 0;   // heure de la station - heure du telephone (secondes)
function maintenant() { return Date.now() / 1000 + ecart; }
function virgule(x, n) { return (typeof x === 'number' ? x.toFixed(n === undefined ? 1 : n) : String(x)).replace('.', T(',', '.')); }

// « il y a 4 min » ; au-dela d'un jour, la date
function ilya(t) {
  if (!t) return '—';
  var s = Math.max(0, maintenant() - t);
  if (s < 60) return T('à l’instant', 'just now');
  if (s < 3600) return T('il y a ', '') + Math.round(s / 60) + T(' min', ' min ago');
  if (s < 86400) return T('il y a ', '') + Math.round(s / 3600) + T(' h', ' h ago');
  return new Date(t * 1000).toLocaleDateString(LOC, { day: 'numeric', month: 'short' });
}
function heure(t) {
  var d = new Date(t * 1000), auj = new Date(maintenant() * 1000).toDateString() === d.toDateString();
  return (auj ? '' : d.toLocaleDateString(LOC, { day: 'numeric', month: 'short' }) + ' ') + d.toLocaleTimeString(LOC, { hour: '2-digit', minute: '2-digit' });
}
function heureSec(t) { return new Date(t * 1000).toLocaleTimeString(LOC, { hour: '2-digit', minute: '2-digit', second: '2-digit' }); }
function dateCourte(t) { return t ? new Date(t * 1000).toLocaleString(LOC, { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' }) : T('aucun', 'none'); }
function duree(s) {
  if (s < 3600) return Math.round(s / 60) + ' min';
  if (s < 86400) return Math.floor(s / 3600) + ' h ' + String(Math.round(s % 3600 / 60)).padStart(2, '0');
  return Math.floor(s / 86400) + T(' j ', ' d ') + Math.round(s % 86400 / 3600) + ' h';
}
// Distance et direction entre deux positions GPS (sans carte : « 2,3 km au nord-est »)
function distance(a, b) {
  var R = 6371, r = Math.PI / 180, dLat = (b.lat - a.lat) * r, dLon = (b.lon - a.lon) * r;
  var h = Math.sin(dLat / 2) * Math.sin(dLat / 2) + Math.cos(a.lat * r) * Math.cos(b.lat * r) * Math.sin(dLon / 2) * Math.sin(dLon / 2);
  var km = 2 * R * Math.asin(Math.sqrt(h));
  var y = Math.sin(dLon) * Math.cos(b.lat * r), x = Math.cos(a.lat * r) * Math.sin(b.lat * r) - Math.sin(a.lat * r) * Math.cos(b.lat * r) * Math.cos(dLon);
  var cap = (Math.atan2(y, x) / r + 360) % 360;
  var DIR = LANGUE === 'en' ? ['north', 'north-east', 'east', 'south-east', 'south', 'south-west', 'west', 'north-west']
                             : ['au nord', 'au nord-est', 'à l’est', 'au sud-est', 'au sud', 'au sud-ouest', 'à l’ouest', 'au nord-ouest'];
  var txt = km < 1 ? Math.round(km * 1000) + ' m' : virgule(km) + ' km';
  return txt + ' ' + DIR[Math.round(cap / 45) % 8];
}
function sauts(n) {
  if (n === null || n === undefined) return '';
  return n === 0 ? T('en direct', 'direct') : n + T(' relais', n > 1 ? ' hops' : ' hop');
}
function octets(t) { return new TextEncoder().encode(t).length; }
function ligneEtat(nom, valeur, classe) {
  var d = el('div'); d.appendChild(el('dt', '', nom)); d.appendChild(el('dd', classe || '', valeur)); return d;
}
var RESEAUX = { meshtastic: 'Meshtastic', meshcore: 'MeshCore' };

// ----- Version legere / complete : la complete montre tout, meme ce qui sert rarement (memorisee par appareil)
var MODE = 'leger';
try { MODE = localStorage.getItem('mesh-mode') === 'complet' ? 'complet' : 'leger'; } catch (e) {}
function choisirMode(m) {
  MODE = m;
  try { localStorage.setItem('mesh-mode', m); } catch (e) {}
  document.body.classList.toggle('complet', m === 'complet');
  document.querySelectorAll('.mode button').forEach(function (b) { b.classList.toggle('choisi', b.dataset.mode === m); });
  document.dispatchEvent(new Event('mode'));
}

var PAGES = [['index', 'Vue d’ensemble', 'Overview'], ['noeuds', 'Nœuds', 'Nodes'], ['messages', 'Messages', 'Messages'],
             ['canaux', 'Canaux', 'Channels'], ['config', 'Configuration', 'Settings'], ['modules', 'Modules', 'Modules', true],
             ['stats', 'Statistiques', 'Statistics'], ['atelier', 'Atelier', 'Workshop'],
             ['distance', 'À distance', 'Remote', true], ['technique', 'Journal technique', 'Technical log', true]];

// En haut de chaque page : retour, titre, navigation, reseau en service, bascule legere / complete
function entete(page, titreFr, titreEn) {
  var z = $('entete');
  var retour = el('a', 'retour', T('← Paramètres', '← Settings')); retour.href = '/parametres/#radio'; z.appendChild(retour);
  z.appendChild(el('h1', '', T(titreFr, titreEn)));
  var nav = el('nav', 'navmesh');
  PAGES.forEach(function (p) {
    var a = el('a', (p[0] === page ? 'ici' : '') + (p[3] ? ' complet-seul' : ''), T(p[1], p[2]));
    a.href = p[0] === 'index' ? './' : p[0] + '.html';
    nav.appendChild(a);
  });
  z.appendChild(nav);
  var barre = el('div', 'barre-mode');
  barre.appendChild(el('p', 'reseau', '…')).id = 'reseau';
  var m = el('div', 'mode');
  [['leger', T('Léger', 'Light')], ['complet', T('Complet', 'Full')]].forEach(function (x) {
    var b = el('button', '', x[1]); b.type = 'button'; b.dataset.mode = x[0];
    b.title = x[0] === 'leger' ? T('L’essentiel seulement', 'Only the essentials') : T('Tous les détails, même ceux qui servent rarement', 'Every detail, even the rarely used ones');
    b.onclick = function () { choisirMode(x[0]); };
    m.appendChild(b);
  });
  barre.appendChild(m);
  z.appendChild(barre);
  choisirMode(MODE);
  document.title = T(titreFr, titreEn) + ' · Mesh';
}

// L'aide « ? » : deplie une explication de deux phrases
function aides(racine) {
  (racine || document).querySelectorAll('[data-aide]').forEach(function (b) {
    if (b.dataset.lie) return;
    b.dataset.lie = '1';
    b.onclick = function () { var a = $(b.dataset.aide); a.hidden = !a.hidden; b.setAttribute('aria-expanded', String(!a.hidden)); };
  });
}
function titreAvecAide(parent, fr, en, aideFr, aideEn, classe) {
  var id = 'aide-' + Math.random().toString(36).slice(2, 8);
  var h = el('h2', 'avec-aide' + (classe ? ' ' + classe : ''));
  h.appendChild(el('span', '', T(fr, en)));
  var b = el('button', 'aide-bouton', '?'); b.type = 'button'; b.dataset.aide = id; b.setAttribute('aria-expanded', 'false');
  h.appendChild(b);
  parent.appendChild(h);
  var p = el('p', 'aide', T(aideFr, aideEn)); p.id = id; p.hidden = true;
  parent.appendChild(p);
  aides(parent);
  return h;
}

// ----- Echanges avec la station
function api(chemin) {
  return fetch('/admin-api' + chemin, { cache: 'no-store' }).then(function (r) {
    if (r.status === 401) { location.href = '/connexion.html?retour=' + encodeURIComponent(location.pathname); throw new Error('401'); }
    return r.json().then(function (d) { if (!r.ok) throw new Error(TE(d.erreur) || T('Erreur.', 'Error.')); return d; });
  });
}
// Un ordre a la radio : la reponse vient en general tout de suite ; sinon on la redemande (2 minutes au plus)
function ordre(action, p) {
  return fetch('/admin-api/mesh/ordre', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ action: action, p: p || {} }) })
    .then(function (r) {
      if (r.status === 401) { location.href = '/connexion.html?retour=' + encodeURIComponent(location.pathname); throw new Error('401'); }
      return r.json().then(function (d) { return { code: r.status, d: d }; });
    }).then(function (x) {
      if (x.code === 202) return attendreReponse(x.d.id, Date.now() + 120000);
      if (x.code !== 200) throw new Error(TE(x.d.erreur) || T('Refusé.', 'Refused.'));
      return x.d.r || {};
    });
}
function attendreReponse(id, fin) {
  return new Promise(function (ok, ko) {
    (function tour() {
      api('/mesh/reponse?id=' + id).then(function (d) {
        if (!d.attente) { if (d.ok) ok(d.r || {}); else ko(new Error(TE(d.erreur) || T('Refusé.', 'Refused.'))); return; }
        if (Date.now() > fin) { ko(new Error(T('La radio ne répond pas.', 'The radio does not answer.'))); return; }
        setTimeout(tour, 1500);
      }).catch(ko);
    })();
  });
}
// Etat de la radio (le meme que la page Radio d'avant) : etat, details, reseau, reglages Mesh, garde-fou
var station = null;
function chargerStation() {
  return api('/radio').then(function (d) {
    station = d; ecart = d.maintenant - Date.now() / 1000;
    var e = d.etat, moi = (d.details || {}).moi || {}, r = (d.reseau || {}).reseau || 'meshtastic';
    var txt = !e.active ? T('La radio est désactivée dans les Paramètres.', 'The radio is turned off in Settings.')
      : e.etat !== 'ok' ? RESEAUX[r] + ' · ' + ({ absente: T('radio pas branchée', 'radio not plugged in'), muette: T('la radio ne répond pas', 'the radio does not answer'), eteinte: T('désactivée', 'turned off') }[e.etat] || e.etat)
      : [RESEAUX[r], moi.preset, moi.region].filter(Boolean).join(' · ');
    if ($('reseau')) { $('reseau').textContent = txt; $('reseau').className = 'reseau' + (e.active && e.etat !== 'ok' ? ' alerte' : ''); }
    document.body.classList.toggle('sous-meshcore', r === 'meshcore');
    if (d.garde_fou && $('reseau')) $('reseau').textContent += T(' · réglage risque en cours de vérification', ' · risky setting being checked');
    return d;
  });
}
function reseauActuel() { return station ? (station.reseau || {}).reseau || 'meshtastic' : 'meshtastic'; }
function radioPrete() { return station && station.etat.active && station.etat.etat === 'ok'; }

// Message de resultat sous un formulaire
function dire(zone, ok, texte) {
  if (typeof zone === 'string') zone = $(zone);
  if (!zone) return;
  zone.className = ok ? 'note' : 'erreur';
  zone.textContent = texte;
}
function apresEcriture(r) {
  var t = T('Fait.', 'Done.');
  if (r && r.sauvegarde) t += T(' Réglages d’avant gardés (', ' Previous settings kept (') + r.sauvegarde + ').';
  if (r && r.redemarre) t += T(' La radio redémarre : environ 30 secondes sans radio.', ' The radio restarts: about 30 seconds without radio.');
  if (r && r.risques && r.risques.length) t += T(' Réglage risqué : si la radio ne revient pas d’ici 3 minutes, la station remet seule ses réglages d’avant.', ' Risky setting: if the radio does not come back within 3 minutes, the station puts its previous settings back by itself.');
  return t;
}

// Bouton en deux temps (toucher, puis confirmer) pour ce qui coupe ou efface
function deuxTemps(b, texteConfirmer, action) {
  b.onclick = function () {
    if (!b.classList.contains('confirmer')) {
      b.dataset.texte = b.textContent;
      b.classList.add('confirmer'); b.textContent = texteConfirmer;
      setTimeout(function () { if (b.classList.contains('confirmer')) { b.classList.remove('confirmer'); b.textContent = b.dataset.texte; } }, 6000);
      return;
    }
    b.classList.remove('confirmer'); b.textContent = b.dataset.texte;
    action();
  };
}

// ----- Resultats arrives par radio (traceroute, telemetrie, reglages lus a distance...)
function suivreResultats(rappel, periode) {
  var depuis = maintenant() - 5;
  (function tour() {
    api('/mesh/resultats?depuis=' + depuis).then(function (d) {
      (d.resultats || []).forEach(function (r) { depuis = Math.max(depuis, r.heure); rappel(r); });
    }).catch(function () {}).then(function () { setTimeout(tour, periode || 3000); });
  })();
}

// ----- Outil radio : operations longues (flashage, reseau, remise de sauvegarde), un ordre a la fois
var occupe = false;
function blocOutil(parent) {
  var html = '<p class="resultat-outil" id="resultat-outil" hidden></p><p class="consigne" id="consigne" hidden></p>' +
    '<form class="code-ble" id="form-code" hidden><label for="code">' + T('Code affiché sur l’écran de la radio de la station', 'Code shown on the screen of the station\'s radio') +
    '</label><div class="ligne-code"><input class="champ" id="code" inputmode="numeric" maxlength="6" autocomplete="off" placeholder="123456"><button class="bouton">' + T('Envoyer', 'Send') + '</button></div></form>' +
    '<pre class="console" id="console-outil" hidden></pre><button class="lien-detail" id="voir-outil" type="button" hidden>' + T('Voir le détail de la dernière opération', 'Show the details of the last operation') + '</button>';
  var d = el('div'); d.innerHTML = html; parent.appendChild(d);
  $('form-code').onsubmit = function (ev) {
    ev.preventDefault();
    var code = $('code').value.replace(/\D/g, '');
    if (code.length !== 6) return;
    fetch('/admin-api/radio/code', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ code: code }) })
      .then(function () { $('code').value = ''; $('form-code').hidden = true; });
  };
  $('voir-outil').onclick = function () { lireOutil().then(function (t) { if (t) montrerOutil(t); }); };
  lireOutil().then(function (t) {
    if (t && !/### FIN -?\d+\s*$/.test(t)) suivreOutil(null);
    else if (t) $('voir-outil').hidden = false;
  });
}
function lireOutil() {
  return fetch('/ajouter/radio-outil.txt?' + Date.now(), { cache: 'no-store' })
    .then(function (r) { return r.ok ? r.text() : ''; }).catch(function () { return null; });
}
function montrerOutil(texte) {
  var c = $('console-outil'), enBas = c.scrollTop + c.clientHeight >= c.scrollHeight - 30;
  c.hidden = false; $('voir-outil').hidden = true;
  c.textContent = texte.replace(/\n?### FIN -?\d+\s*$/, '') || T('Lancement…', 'Starting…');
  if (enBas) c.scrollTop = c.scrollHeight;
  var attend = /CODE À TAPER/.test(texte) && !/code reçu|### FIN/.test(texte.slice(texte.lastIndexOf('CODE À TAPER')));
  if (attend && $('form-code').hidden) { $('form-code').hidden = false; $('code').focus(); }
  if (!attend) $('form-code').hidden = true;
  // L'outil attend un geste sur la radio (« APPUYEZ … ») : la consigne, en clair, au-dessus du detail
  var lignes = texte.split('\n'), derniere = '';
  lignes.forEach(function (l) { if (/APPUYEZ|BRANCHEZ|MAINTENEZ/.test(l)) derniere = l; });
  var faite = derniere && lignes.slice(lignes.indexOf(derniere) + 1).some(function (l) { return /mode mise à jour|répond|écrit|reconnue|^== /.test(l); });
  $('consigne').hidden = !derniere || faite || /### FIN/.test(texte);
  if (!$('consigne').hidden) $('consigne').textContent = consigne(derniere);
}
// Le geste demande par l'outil, en clair (l'outil l'ecrit en majuscules dans son detail)
function consigne(l) {
  var techo = /T-ECHO/.test(l);
  if (/DEUX FOIS/.test(l)) return techo ? T('Appuyez deux fois rapidement sur le bouton reset du T-Echo (en haut à gauche) : son écran se fige.', 'Press the T-Echo\'s reset button twice quickly (top left): its screen freezes.')
    : T('Appuyez deux fois rapidement sur le bouton reset de la carte : elle passe en mode mise à jour (souvent une diode qui pulse).', 'Press the board\'s reset button twice quickly: it enters update mode (often a pulsing LED).');
  if (/UNE FOIS/.test(l)) return techo ? T('Appuyez une fois sur le bouton reset du T-Echo (en haut à gauche).', 'Press the T-Echo\'s reset button once (top left).')
    : T('Appuyez une fois sur le bouton reset de la carte.', 'Press the board\'s reset button once.');
  if (/MAINTENEZ/.test(l)) return T('Débranchez la carte, maintenez son bouton BOOT enfoncé, rebranchez-la, puis relâchez le bouton.', 'Unplug the board, hold its BOOT button, plug it back in, then release the button.');
  if (/BRANCHEZ/.test(l)) return T('Branchez la carte sur une prise USB de la station.', 'Plug the board into a USB port of the station.');
  return l.replace(/^==\s*/, '');
}
function boutonsOutil() {
  document.querySelectorAll('[data-outil]').forEach(function (b) { b.disabled = occupe || b.dataset.bloque === '1'; });
  document.dispatchEvent(new Event('outil'));
}
function resultatOutil(ok, texte) {
  var r = $('resultat-outil'); r.hidden = false; r.className = 'resultat-outil ' + (ok ? 'bien' : 'alerte'); r.textContent = texte;
}
var finOutil = null;
function suivreOutil(debutAvant) {
  occupe = true; boutonsOutil();
  $('resultat-outil').hidden = true;
  var depart = Date.now(), vueEnCours = false;
  (function tour() {
    lireOutil().then(function (texte) {
      if (texte === null) { setTimeout(tour, 3000); return; }
      var nouveau = texte.split('\n')[0] !== debutAvant, fin = nouveau && /### FIN (-?\d+)\s*$/.exec(texte);
      if (fin && debutAvant === null && !vueEnCours) { occupe = false; boutonsOutil(); return; }
      if (!fin) vueEnCours = vueEnCours || nouveau;
      if (nouveau) montrerOutil(texte);
      if (!fin) {
        if (!nouveau && Date.now() - depart > 30000) {
          occupe = false; boutonsOutil();
          resultatOutil(false, T('L’opération n’a pas démarré (une autre est peut-être en cours). Réessayez dans un moment.', 'The operation did not start (another one may be running). Try again in a moment.'));
          return;
        }
        setTimeout(tour, 2000); return;
      }
      occupe = false; boutonsOutil();
      resultatOutil(fin[1] === '0', fin[1] === '0' ? T('Terminé.', 'Done.') : T('Échec : le détail est ci-dessous.', 'Failed: details below.'));
      if (finOutil) finOutil(fin[1] === '0');
    });
  })();
}
function lancerOutil(ordre_, corps) {
  if (occupe) return;
  occupe = true; boutonsOutil();
  lireOutil().then(function (texte) {
    var debutAvant = (texte || '').split('\n')[0];
    $('console-outil').textContent = T('Lancement…', 'Starting…'); $('console-outil').hidden = false;
    $('console-outil').scrollIntoView({ behavior: 'smooth', block: 'center' });
    fetch('/ajouter/commande/radio-' + ordre_, { method: 'PUT', body: corps || '' })
      .then(function () { suivreOutil(debutAvant); })
      .catch(function () { occupe = false; boutonsOutil(); resultatOutil(false, T('La station ne répond pas.', 'The station does not respond.')); });
  });
}

// ----- Petits graphiques : une mesure par graphique, une seule echelle, bulle au survol
// points : [{x: heure, y: valeur}] ; o : {min, max, limite, format(y), barres, largeur (secondes d'une barre)}
function graphe(zone, points, o) {
  o = o || {};
  zone.innerHTML = '';
  zone.className = 'graphe';
  var pts = points.filter(function (p) { return typeof p.y === 'number' && !isNaN(p.y); });
  if (!pts.length) { zone.appendChild(el('p', 'rien', T('Pas encore de relevé sur cette période.', 'No reading yet for this period.'))); return; }
  // Dessine a la largeur reelle : pas d'etirement, le texte garde sa forme
  var L = Math.max(280, Math.round(zone.getBoundingClientRect().width) || 640), H = 150, g = 36, b = 20, h = 6;
  var x0 = o.debut || pts[0].x, x1 = o.fin || pts[pts.length - 1].x;
  if (x1 <= x0) x1 = x0 + 1;
  var ys = pts.map(function (p) { return p.y; });
  var min = o.min !== undefined ? o.min : Math.min.apply(null, ys), max = o.max !== undefined ? o.max : Math.max.apply(null, ys);
  if (o.limite !== undefined) max = Math.max(max, o.limite * 1.15);
  if (max <= min) max = min + 1;
  var X = function (x) { return g + (x - x0) / (x1 - x0) * (L - g - 6); }, Y = function (y) { return h + (1 - (y - min) / (max - min)) * (H - h - b); };
  var f = o.format || function (y) { return virgule(y); };
  var ns = 'http://www.w3.org/2000/svg', svg = document.createElementNS(ns, 'svg');
  svg.setAttribute('viewBox', '0 0 ' + L + ' ' + H); svg.setAttribute('preserveAspectRatio', 'none');
  svg.setAttribute('role', 'img'); svg.setAttribute('aria-label', o.titre || '');
  function n(tag, attrs, texte) { var e = document.createElementNS(ns, tag); for (var k in attrs) e.setAttribute(k, attrs[k]); if (texte !== undefined) e.textContent = texte; svg.appendChild(e); return e; }
  n('line', { x1: g, x2: L - 6, y1: H - b, y2: H - b, class: 'axe' });
  [min, max].forEach(function (v) { n('text', { x: g - 6, y: Y(v) + 4, 'text-anchor': 'end' }, f(v)); });
  n('text', { x: g, y: H - 4 }, heure(x0));
  n('text', { x: L - 6, y: H - 4, 'text-anchor': 'end' }, heure(x1));
  if (o.limite !== undefined) {
    n('line', { x1: g, x2: L - 6, y1: Y(o.limite), y2: Y(o.limite), class: 'limite' });
    n('text', { x: L - 8, y: Y(o.limite) - 4, 'text-anchor': 'end' }, o.texteLimite || f(o.limite));
  }
  if (o.barres) {
    var larg = Math.max(2, (X(x0 + (o.largeur || 3600)) - X(x0)) - 2);
    pts.forEach(function (p) {
      var y = Y(Math.max(min, p.y)), hb = Math.max(1, H - b - y);
      n('rect', { x: X(p.x), y: H - b - hb, width: larg, height: hb, rx: Math.min(2, larg / 2), class: 'barre' });
    });
  } else {
    // La courbe s'interrompt sur un trou (pas de releve) au lieu de tirer un trait ; peu de points : on les montre
    var trou = Math.max((x1 - x0) / 40, 600);
    n('path', { d: pts.map(function (p, i) { return (i && p.x - pts[i - 1].x < trou ? 'L' : 'M') + X(p.x).toFixed(1) + ' ' + Y(p.y).toFixed(1); }).join(' '), class: 'courbe' });
    if (pts.length < 80) pts.forEach(function (p) { n('circle', { cx: X(p.x), cy: Y(p.y), r: 2.5, class: 'point' }); });
  }
  var viseur = n('line', { x1: 0, x2: 0, y1: h, y2: H - b, class: 'viseur', visibility: 'hidden' });
  var point = n('circle', { r: 4, class: 'point', visibility: 'hidden' });
  zone.appendChild(svg);
  var bulle = el('div', 'bulle'); bulle.hidden = true; zone.appendChild(bulle);
  function montrer(ev) {
    var r = svg.getBoundingClientRect(), cx = (ev.touches ? ev.touches[0].clientX : ev.clientX) - r.left;
    var xv = x0 + (cx / r.width * L - g) / (L - g - 6) * (x1 - x0), proche = pts[0];
    pts.forEach(function (p) { if (Math.abs(p.x - xv) < Math.abs(proche.x - xv)) proche = p; });
    var px = X(proche.x + (o.barres ? (o.largeur || 3600) / 2 : 0));
    viseur.setAttribute('x1', px); viseur.setAttribute('x2', px); viseur.setAttribute('visibility', 'visible');
    point.setAttribute('cx', px); point.setAttribute('cy', Y(proche.y)); point.setAttribute('visibility', o.barres ? 'hidden' : 'visible');
    bulle.hidden = false; bulle.textContent = heure(proche.x) + ' · ' + f(proche.y) + (o.unite || '');
    bulle.style.left = (px / L * r.width) + 'px'; bulle.style.top = (Y(proche.y) / H * r.height) + 'px';
  }
  function cacher() { viseur.setAttribute('visibility', 'hidden'); point.setAttribute('visibility', 'hidden'); bulle.hidden = true; }
  svg.addEventListener('mousemove', montrer); svg.addEventListener('touchstart', montrer, { passive: true });
  svg.addEventListener('touchmove', montrer, { passive: true }); svg.addEventListener('mouseleave', cacher);
}
