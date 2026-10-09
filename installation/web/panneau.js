// Prometheus Station - mise en forme du panneau d'accueil (texte ecrit dans Parametres > Panneau d'accueil).
// Signes reconnus : # Titre, ## Sous-titre, **gras**, *italique*, __souligne__, - liste (ou • liste).
// Tout le reste est du texte simple : aucun HTML ecrit par l'auteur n'est jamais interprete.
function miseEnForme(texte) {
  function echapper(s) { return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;'); }
  function styles(s) {
    return echapper(s)
      .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
      .replace(/__(.+?)__/g, '<u>$1</u>')
      .replace(/\*(.+?)\*/g, '<em>$1</em>');
  }
  var html = '', paragraphe = [], liste = false;
  function finParagraphe() { if (paragraphe.length) { html += '<p>' + paragraphe.join('<br>') + '</p>'; paragraphe = []; } }
  function finListe() { if (liste) { html += '</ul>'; liste = false; } }
  (texte || '').split('\n').forEach(function (l) {
    var t = l.trim(), m;
    if (!t) { finParagraphe(); finListe(); return; }
    if ((m = t.match(/^(#{1,2})\s+(.*)$/))) {
      finParagraphe(); finListe();
      var n = m[1].length === 1 ? 'h2' : 'h3';
      html += '<' + n + '>' + styles(m[2]) + '</' + n + '>';
    } else if ((m = t.match(/^[-•*]\s+(.*)$/))) {
      finParagraphe();
      if (!liste) { html += '<ul>'; liste = true; }
      html += '<li>' + styles(m[1]) + '</li>';
    } else {
      finListe();
      paragraphe.push(styles(t));
    }
  });
  finParagraphe(); finListe();
  return html;
}
