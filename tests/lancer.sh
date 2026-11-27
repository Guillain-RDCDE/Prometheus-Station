#!/bin/bash
# Prometheus Station - lance tous les essais (27/11/2026). Depuis la racine du depot :  bash tests/lancer.sh
# Sur un Mac, un Linux ou la station elle-meme ; ce qui demande un outil absent est saute, et dit.
#   - essais Python : module commun, regles « un seul endroit », radio (sans radio branchee)
#   - banc de l'admin : chaque adresse, connecte ou non, compare a la reference tests/reference/admin.json
#   - banc des ordres (prometheus-commande) : Linux seulement (stat -c)
#   - essais des pages (Node) et, si Chrome est la, chaque page ouverte dans un vrai navigateur
set -u
cd "$(dirname "$0")/.." || exit 1
ECHECS=""
etape() { echo; echo "== $1"; }
resultat() { if [ "$1" -eq 0 ]; then echo "   -> ok"; else echo "   -> ECHEC"; ECHECS="$ECHECS $2"; fi; }

etape "Python : module commun et regles « un seul endroit »"
python3 -m unittest discover -s tests -p 'test_*.py' 2>&1 | tail -3
resultat "${PIPESTATUS[0]}" "python"

if [ -d tests/radio ]; then
  etape "Python : la radio (sans radio branchee)"
  (cd tests/radio && python3 -m unittest 2>&1 | tail -3; exit "${PIPESTATUS[0]}")
  resultat $? "radio"
fi

etape "Banc de l'admin (compare a tests/reference/admin.json)"
SORTIE=$(mktemp)
if python3 tests/banc_admin.py installation/prometheus-admin "$SORTIE"; then
  if diff -u tests/reference/admin.json "$SORTIE"; then resultat 0 admin
  else echo "   (une difference voulue ? mettre a jour : python3 tests/banc_admin.py installation/prometheus-admin tests/reference/admin.json)"; resultat 1 admin; fi
else
  resultat 1 admin
fi
rm -f "$SORTIE"

etape "Banc des ordres (prometheus-commande)"
if stat -c %U . >/dev/null 2>&1; then
  bash tests/banc_commande.sh installation/prometheus-commande
  resultat $? commande
else
  echo "   saute : il faut un Linux (stat -c) ; il passe sur la station et sur GitHub"
fi

if command -v node >/dev/null && [ -d tests/web ]; then
  etape "Pages : essais (Node)"
  node --test tests/web/*.test.mjs 2>&1 | grep -E '^(ℹ|#) (tests|pass|fail)'
  resultat "${PIPESTATUS[0]}" "pages"
  CHROME=${CHROME:-}
  for c in "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" "$(command -v google-chrome 2>/dev/null)" \
           "$(command -v chromium 2>/dev/null)"; do
    [ -z "$CHROME" ] && [ -n "$c" ] && [ -x "$c" ] && CHROME=$c
  done
  if [ -n "$CHROME" ] && [ -f tests/web/navigateur.mjs ]; then
    etape "Pages : chaque page dans un vrai navigateur"
    CHROME="$CHROME" node tests/web/navigateur.mjs
    resultat $? "navigateur"
  else
    echo "   (pas de Chrome : essai dans le navigateur saute)"
  fi
else
  echo; echo "== Pages : saute (pas de Node)"
fi

echo
if [ -z "$ECHECS" ]; then echo "TOUT EST BON"; else echo "ECHECS :$ECHECS"; exit 1; fi
