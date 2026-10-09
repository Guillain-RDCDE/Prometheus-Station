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
    'Message vide.': 'Empty message.', 'Réglage invalide.': 'Invalid setting.', 'Texte trop long.': 'Text too long.', 'Attendez quelques secondes avant le message suivant.': 'Wait a few seconds before the next message.'
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
