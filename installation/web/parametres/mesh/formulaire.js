// Prometheus Station - section Mesh : formulaires de reglages generes a partir du schema de la radio
// (schema.json, ecrit par prometheus-radio a partir de la bibliotheque Meshtastic) et expliques par champs.js.
// Aucun reglage n'est oublie : ceux que champs.js ne connait pas s'affichent dans la version complete.

// Adresse IP rangee par Meshtastic dans un entier (premier octet = poids faible)
function ipTexte(n) { n = Number(n) >>> 0; return [n & 255, (n >>> 8) & 255, (n >>> 16) & 255, n >>> 24].join('.'); }
function ipNombre(t) {
  var p = String(t).trim().split('.');
  if (p.length !== 4 || p.some(function (x) { return !/^\d{1,3}$/.test(x) || +x > 255; })) return null;
  return ((+p[0]) | (+p[1] << 8) | (+p[2] << 16) | (+p[3] << 24)) >>> 0;
}

// Un formulaire pour une section (« config.lora », « module.mqtt ») ; renvoie {zone, changements(), visibles}
function sectionFormulaire(cle, schemaChamps, valeurs, drapeaux, ouverte) {
  var info = SECTIONS[cle] || [cle, cle, '', ''];
  var det = el('details', 'section-config');
  if (ouverte) det.open = true;
  var resume = el('summary'); resume.appendChild(el('b', '', T(info[0], info[1])));
  var compte = el('span'); resume.appendChild(compte);
  det.appendChild(resume);
  if (info[2]) det.appendChild(el('p', 'note', T(info[2], info[3])));
  var lecteurs = [];      // fonctions qui renvoient [nom, valeur, changee]
  var nbLeger = 0, nbTout = 0;

  function champ(parent, prefixe, c, actuel, lire) {
    var k = prefixe + '.' + c.nom, o = optionsChamp(k);
    nbTout++; if (o.leger) nbLeger++;
    var bloc = el('div', 'champ-cfg' + (o.leger ? '' : ' complet-seul'));
    var tete = el('div', 'tete');
    var lab = el('label', '', nomChamp(k)); tete.appendChild(lab);
    tete.appendChild(el('span', 'code complet-seul', c.nom));
    var id = 'c-' + k.replace(/\./g, '-'); lab.htmlFor = id;
    var aide = aideChamp(k);
    var entree, lireValeur, montrer;
    if (c.type === 'groupe' && !c.repete) {
      bloc.appendChild(tete);
      if (aide) bloc.appendChild(el('p', 'explique', aide));
      var sous = el('div', 'sous-groupe'); bloc.appendChild(sous);
      var lecteursSous = [];
      (c.champs || []).forEach(function (s) {
        champ(sous, k, s, (actuel || {})[s.nom], function (f) { lecteursSous.push(f); });
      });
      // Un sous-groupe s'ecrit en entier (la radio remplace tout le groupe)
      lire(function () {
        var tout = {}, change = false;
        lecteursSous.forEach(function (f) { var x = f(); tout[x[0]] = x[1]; change = change || x[2]; });
        return [c.nom, Object.assign({}, actuel || {}, tout), change];
      });
      parent.appendChild(bloc);
      return;
    }
    if (c.type === 'bool' && !c.repete) {
      bloc.classList.add('bascule');
      var coche = el('input', 'case'); coche.type = 'checkbox'; coche.id = id; coche.checked = !!actuel;
      var gauche = el('div', 'tete'); gauche.appendChild(lab); gauche.appendChild(el('span', 'code complet-seul', c.nom));
      var col = el('div'); col.style.flex = '1'; col.appendChild(gauche);
      if (aide) col.appendChild(el('p', 'explique', aide));
      bloc.appendChild(col); bloc.appendChild(coche);
      entree = coche; lireValeur = function () { return coche.checked; };
    } else {
      bloc.appendChild(tete);
      if (aide) bloc.appendChild(el('p', 'explique', aide));
      var dr = drapeaux && drapeaux[k];
      if (dr) {
        // Des cases dont la somme fait le nombre enregistre
        var zone = el('div', 'drapeaux'), cases = [];
        Object.keys(dr).forEach(function (nom) {
          if (!dr[nom]) return;
          var l = el('label'), x = el('input', 'case'); x.type = 'checkbox'; x.checked = (Number(actuel) & dr[nom]) !== 0; x.dataset.v = dr[nom];
          l.appendChild(x); l.appendChild(document.createTextNode(nom.replace(/_/g, ' ').toLowerCase())); zone.appendChild(l); cases.push(x);
        });
        bloc.appendChild(zone);
        entree = zone;
        lireValeur = function () { return cases.reduce(function (s, x) { return s + (x.checked ? +x.dataset.v : 0); }, 0); };
      } else if (c.type === 'choix' && !c.repete) {
        var s = el('select', 'champ'); s.id = id;
        (c.valeurs || []).forEach(function (v) { var op = el('option', '', nomValeur(k, v)); op.value = v; s.appendChild(op); });
        if (actuel !== undefined && !(c.valeurs || []).includes(actuel)) { var op = el('option', '', String(actuel)); op.value = actuel; s.appendChild(op); }
        s.value = actuel === undefined ? (c.valeurs || [''])[0] : actuel;
        bloc.appendChild(s); entree = s; lireValeur = function () { return s.value; };
      } else if (c.repete) {
        // Liste : une valeur par ligne (cles en base64, numeros) ; liste d'objets : JSON
        var t = el('textarea', 'champ'); t.id = id; t.rows = 3;
        if (c.type === 'groupe') {
          t.value = JSON.stringify(actuel || [], null, 1);
          lireValeur = function () { try { return JSON.parse(t.value || '[]'); } catch (e) { throw new Error(nomChamp(k) + T(' : JSON illisible.', ': unreadable JSON.')); } };
        } else {
          t.value = (actuel || []).join('\n');
          lireValeur = function () {
            return t.value.split(/[\n,]+/).map(function (x) { return x.trim(); }).filter(Boolean)
              .map(function (x) { return c.type === 'entier' || c.type === 'decimal' ? Number(x) : x; });
          };
        }
        if (o.masque) t.style.webkitTextSecurity = 'disc';
        bloc.appendChild(t); entree = t;
      } else {
        var i = el('input', 'champ'); i.id = id; i.autocomplete = 'off';
        if (c.type === 'ip') { i.value = actuel ? ipTexte(actuel) : ''; i.placeholder = '10.0.0.20'; }
        else i.value = actuel === undefined || actuel === null ? '' : String(actuel);
        if (c.type === 'entier' || c.type === 'decimal') i.inputMode = c.type === 'decimal' ? 'decimal' : 'numeric';
        if (o.unite) i.placeholder = o.unite.trim();
        lireValeur = function () {
          var v = i.value.trim();
          if (c.type === 'ip') { if (!v) return 0; var n = ipNombre(v); if (n === null) throw new Error(nomChamp(k) + T(' : adresse invalide.', ': invalid address.')); return n; }
          if (c.type === 'entier') {
            if (!/^-?\d+$/.test(v || '0')) throw new Error(nomChamp(k) + T(' : un nombre entier.', ': a whole number.'));
            if (!c.signe && v.charAt(0) === '-') throw new Error(nomChamp(k) + T(' : pas de nombre négatif.', ': no negative number.'));
            // Les grands nombres (64 bits) voyagent en texte
            return Math.abs(Number(v || 0)) > 9007199254740991 || typeof actuel === 'string' ? String(v || '0') : Number(v || 0);
          }
          if (c.type === 'decimal') { var d = Number((v || '0').replace(',', '.')); if (isNaN(d)) throw new Error(nomChamp(k) + T(' : un nombre.', ': a number.')); return d; }
          return i.value;
        };
        if (o.masque) {
          // Secret : cache par defaut, « Afficher » pour le lire
          i.type = 'password';
          var sec = el('div', 'secret'); sec.appendChild(i);
          var voir = el('button', 'bouton secondaire', T('Afficher', 'Show')); voir.type = 'button';
          voir.onclick = function () { i.type = i.type === 'password' ? 'text' : 'password'; voir.textContent = i.type === 'password' ? T('Afficher', 'Show') : T('Cacher', 'Hide'); };
          sec.appendChild(voir); bloc.appendChild(sec);
        } else bloc.appendChild(i);
        entree = i;
      }
    }
    if (o.risque && RISQUES[o.risque]) {
      var r = el('p', 'risque', T(RISQUES[o.risque][0], RISQUES[o.risque][1]));
      r.hidden = true; bloc.appendChild(r); bloc.risque = r;
    }
    var depart = JSON.stringify(normaliser(actuel, c));
    function normaliser(v, c) { if (c.repete) return v || []; if (c.type === 'ip') return Number(v || 0) >>> 0; return v === undefined ? null : v; }
    function suivre() {
      var change;
      try { change = JSON.stringify(lireValeur()) !== depart; } catch (e) { change = true; }
      bloc.classList.toggle('change', change);
      if (bloc.risque) bloc.risque.hidden = !change;
      majCompte();
    }
    entree.addEventListener('input', suivre); entree.addEventListener('change', suivre);
    lire(function () { var v = lireValeur(); return [c.nom, v, JSON.stringify(v) !== depart, o.risque]; });
    parent.appendChild(bloc);
  }
  schemaChamps.forEach(function (c) { champ(det, cle, c, (valeurs || {})[c.nom], function (f) { lecteurs.push(f); }); });
  if (!nbLeger) det.classList.add('complet-seul');
  function majCompte() {
    var n = 0;
    lecteurs.forEach(function (f) { try { if (f()[2]) n++; } catch (e) { n++; } });
    compte.textContent = (n ? n + (n > 1 ? T(' changés · ', ' changed · ') : T(' changé · ', ' changed · ')) : '') + (function (x) { return x + (x > 1 ? T(' réglages', ' settings') : T(' réglage', ' setting')); })(MODE === 'complet' ? nbTout : nbLeger);
  }
  majCompte();
  document.addEventListener('mode', majCompte);
  return {
    zone: det, cle: cle,
    // {nom: valeur} des reglages changes ; risques : la liste des genres de risque touches
    changements: function () {
      var r = {}, risques = [];
      lecteurs.forEach(function (f) { var x = f(); if (x[2]) { r[x[0]] = x[1]; if (x[3]) risques.push(x[3]); } });
      return { valeurs: r, risques: risques };
    }
  };
}
