// Prometheus Station - langue des pages (francais / anglais).
// Choix propre a chaque appareil (garde dans le navigateur). Par defaut : la langue du telephone.
// Dans les pages : <span data-en="English text">Texte francais</span>, data-en-ph pour un texte d'aide (placeholder),
// data-en-aria pour une etiquette d'accessibilite ; dans le code : T('francais', 'english').
(function () {
  var L = null;
  try { L = localStorage.getItem('langue'); } catch (e) {}
  if (L !== 'fr' && L !== 'en') L = (navigator.language || 'fr').slice(0, 2) === 'fr' ? 'fr' : 'en';
  window.LANGUE = L;
  window.T = function (fr, en) { return L === 'en' ? en : fr; };
  // Messages d'erreur envoyes en francais par la station
  var ERREURS = {
    'Mot de passe incorrect.': 'Wrong password.', 'Trop d’essais. Attendez une minute.': 'Too many attempts. Wait a minute.',
    'Au moins 4 caractères.': 'At least 4 characters.', 'Le mot de passe est déjà choisi.': 'The password is already set.',
    'Ancien mot de passe incorrect.': 'Current password is wrong.', 'Entre 1 et 32 caractères.': 'Between 1 and 32 characters.',
    'Couleurs inconnues.': 'Unknown colors.', 'Connectez-vous d’abord.': 'Please sign in first.',
    'Message vide.': 'Empty message.', 'Réglage invalide.': 'Invalid setting.', 'Texte trop long.': 'Text too long.',
    'Cette fonction est désactivée.': 'This feature is turned off.', 'Indiquez un nom.': 'Please enter a name.', 'Effacement refusé.': 'Deletion refused.', 'Huit sujets au plus.': 'Eight topics at most.', 'Attendez quelques secondes avant le message suivant.': 'Wait a few seconds before the next message.',
    'Réservé à l’administrateur.': 'For the administrator only.', 'Trop long pour la radio.': 'Too long for the radio.', 'Lettres minuscules, chiffres et tirets seulement.': 'Lowercase letters, digits and hyphens only.',
    'Un seul message radio à la fois : réessayez dans un moment.': 'One radio message at a time: try again in a moment.',
    'Six chiffres.': 'Six digits.'
  };
  window.TE = function (msg) { return (L === 'en' && ERREURS[msg]) || msg; };

  function appliquer() {
    document.documentElement.lang = L;
    document.querySelectorAll('[data-en]').forEach(function (e) {
      if (e.dataset.fr === undefined) e.dataset.fr = e.textContent;
      e.textContent = L === 'en' ? e.dataset.en : e.dataset.fr;
    });
    document.querySelectorAll('[data-en-ph]').forEach(function (e) {
      if (e.dataset.frPh === undefined) e.dataset.frPh = e.placeholder;
      e.placeholder = L === 'en' ? e.dataset.enPh : e.dataset.frPh;
    });
    document.querySelectorAll('[data-en-aria]').forEach(function (e) {
      if (e.dataset.frAria === undefined) e.dataset.frAria = e.getAttribute('aria-label');
      e.setAttribute('aria-label', L === 'en' ? e.dataset.enAria : e.dataset.frAria);
    });
    document.querySelectorAll('[data-langue]').forEach(function (b) {
      b.classList.toggle('choisi', b.dataset.langue === L);
      b.onclick = function () { choisirLangue(b.dataset.langue); };
    });
  }

  window.choisirLangue = function (l) {
    try { localStorage.setItem('langue', l); } catch (e) {}
    if (l !== L) location.reload();
  };

  document.addEventListener('DOMContentLoaded', appliquer);
  // Bouton « retour » : si la langue a change entre-temps, on recharge la page
  addEventListener('pageshow', function (e) {
    var l = null;
    try { l = localStorage.getItem('langue'); } catch (x) {}
    if (e.persisted && l && l !== L) location.reload();
  });
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
