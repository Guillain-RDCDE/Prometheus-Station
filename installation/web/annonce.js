// Prometheus Station - bandeau d'annonce, en haut de toutes les pages (articles des encyclopedies compris).
// Allume et regle dans Parametres > Annonce. Autonome : ses styles sont ici, il ne depend d'aucune autre feuille.
(function () {
  var COULEURS = { info: ['#1d6fd6', '#ffffff'], important: ['#d9750a', '#ffffff'], urgent: ['#c92a2a', '#ffffff'] };
  var VITESSES = { lente: 40, normale: 70, rapide: 110 };   // pixels par seconde

  function poser(a) {
    var ancien = document.getElementById('prometheus-annonce');
    if (ancien) ancien.remove();
    if (!a || !a.active || !a.texte) return;
    var c = COULEURS[a.couleur] || COULEURS.info;

    if (!document.getElementById('prometheus-annonce-style')) {
      var st = document.createElement('style');
      st.id = 'prometheus-annonce-style';
      st.textContent =
        '#prometheus-annonce{position:sticky;top:0;z-index:2147483646;display:flex;align-items:center;gap:10px;' +
        'padding:10px 16px;font:600 15px/1.35 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;' +
        'cursor:pointer;-webkit-tap-highlight-color:transparent}' +
        '#prometheus-annonce .pa-icone{flex:none;width:24px;height:30px;border-radius:50%;' +
        'display:flex;align-items:center;justify-content:center}' +
        '#prometheus-annonce .pa-icone svg{width:17px;height:17px}' +
        '#prometheus-annonce .pa-fenetre{flex:1;min-width:0;overflow:hidden;' +
        '-webkit-mask-image:linear-gradient(90deg,transparent,#000 14px,#000 calc(100% - 14px),transparent);' +
        'mask-image:linear-gradient(90deg,transparent,#000 14px,#000 calc(100% - 14px),transparent)}' +
        '#prometheus-annonce .pa-ruban{display:inline-flex;white-space:nowrap;will-change:transform;animation:pa-defile var(--pa-duree) linear infinite}' +
        '#prometheus-annonce .pa-ruban span{padding-right:4em}' +
        '#prometheus-annonce.pa-fixe .pa-ruban,#prometheus-annonce.pa-ouverte .pa-ruban{animation:none;white-space:normal;display:block}' +
        '#prometheus-annonce.pa-fixe .pa-ruban span+span,#prometheus-annonce.pa-ouverte .pa-ruban span+span{display:none}' +
        '#prometheus-annonce.pa-fixe .pa-fenetre,#prometheus-annonce.pa-ouverte .pa-fenetre{-webkit-mask-image:none;mask-image:none}' +
        '#prometheus-annonce.pa-urgent .pa-icone{animation:pa-pouls 1.6s ease-in-out infinite}' +
        '@keyframes pa-defile{from{transform:translateX(0)}to{transform:translateX(-50%)}}' +
        '@keyframes pa-pouls{0%,100%{box-shadow:0 0 0 0 rgba(255,255,255,.55)}50%{box-shadow:0 0 0 7px rgba(255,255,255,0)}}' +
        '@media (prefers-reduced-motion:reduce){#prometheus-annonce .pa-ruban{animation:none;white-space:normal;display:block}' +
        '#prometheus-annonce .pa-ruban span+span{display:none}#prometheus-annonce .pa-fenetre{-webkit-mask-image:none;mask-image:none}}' +
        '@media print{#prometheus-annonce{display:none}}';
      document.head.appendChild(st);
    }

    var b = document.createElement('div');
    b.id = 'prometheus-annonce';
    b.setAttribute('role', 'status');
    b.className = (a.defile ? '' : 'pa-fixe') + (a.couleur === 'urgent' ? ' pa-urgent' : '');
    b.style.background = c[0];
    b.style.color = c[1];
    b.title = a.texte;
    b.innerHTML = '<span class="pa-icone"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">' +
      '<path d="M3 11v2a1 1 0 0 0 1 1h3l5 4V6L7 10H4a1 1 0 0 0-1 1z"/><path d="M16 9a4 4 0 0 1 0 6"/><path d="M19 6a8 8 0 0 1 0 12"/></svg></span>' +
      '<div class="pa-fenetre"><div class="pa-ruban"><span></span><span aria-hidden="true"></span></div></div>';
    var parts = b.querySelectorAll('.pa-ruban span');
    parts[0].textContent = a.texte;
    parts[1].textContent = a.texte;   // deux copies a la suite : le defilement boucle sans trou
    // Toucher le bandeau l'arrete et montre le texte en entier ; toucher encore le relance
    b.onclick = function () { if (a.defile) b.classList.toggle('pa-ouverte'); };
    document.body.insertBefore(b, document.body.firstChild);

    // Duree d'un tour proportionnelle a la longueur du texte : la vitesse reste la meme
    var largeur = parts[0].getBoundingClientRect().width || 300;
    b.querySelector('.pa-ruban').style.setProperty('--pa-duree', Math.max(6, largeur / (VITESSES[a.vitesse] || 70)) + 's');
  }

  var actuelle = null;
  function charger() {
    fetch('/api/reglages', { cache: 'no-store' }).then(function (r) { return r.json(); }).then(function (d) {
      var j = JSON.stringify(d.annonce);
      if (j !== actuelle) { actuelle = j; poser(d.annonce); }   // on ne redessine que si l'annonce a change
    }).catch(function () {});
  }
  window.prometheusAnnonce = charger;   // les Parametres l'appellent apres un changement
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', charger); else charger();
  setInterval(charger, 60000);   // une nouvelle annonce arrive sans recharger la page
  addEventListener('pageshow', function (e) { if (e.persisted) charger(); });
})();

// Ecran de la station (etape 11, navigateur en plein ecran, sans barre) : deux boutons ronds en bas a gauche,
// Retour et Accueil. Seulement sur cet ecran : il ouvre l'accueil avec ?kiosque=1, que le navigateur retient.
// Le meme bloc est dans langue.js (pages de la station) et annonce.js (articles des encyclopedies).
(function () {
  if (window.prometheusKiosque) return;
  window.prometheusKiosque = true;
  var oui = false;
  try {
    if (/[?&]kiosque=1/.test(location.search)) localStorage.setItem('kiosque', '1');
    oui = localStorage.getItem('kiosque') === '1';
  } catch (e) {}
  if (!oui) return;
  function poser() {
    // L'accueil en paves (/ecran/) a son propre bouton retour
    if (document.getElementById('prometheus-kiosque') || location.pathname.indexOf('/ecran') === 0) return;
    var en = (document.documentElement.lang || '').slice(0, 2) === 'en';
    var z = document.createElement('div');
    z.id = 'prometheus-kiosque';
    z.style.cssText = 'position:fixed;left:16px;bottom:16px;z-index:2147483646;display:flex;gap:12px';
    [['M15 5l-7 7 7 7', en ? 'Back' : 'Retour', function () { history.back(); }],
     ['M4 11l8-7 8 7M6 9.5V20h12V9.5', en ? 'Home' : 'Accueil', function () { location.href = '/ecran/'; }]].forEach(function (b) {
      var x = document.createElement('button');
      x.type = 'button';
      x.setAttribute('aria-label', b[1]);
      x.title = b[1];
      x.style.cssText = 'width:56px;height:56px;border-radius:28px;border:0;background:#111;opacity:.82;display:flex;align-items:center;justify-content:center;cursor:pointer;padding:0';
      x.innerHTML = '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="' + b[0] + '"/></svg>';
      x.onclick = b[2];
      z.appendChild(x);
    });
    document.body.appendChild(z);
  }
  if (document.body) poser(); else document.addEventListener('DOMContentLoaded', poser);
})();
