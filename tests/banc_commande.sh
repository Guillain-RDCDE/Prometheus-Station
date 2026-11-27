#!/bin/bash
# Banc d'essai de prometheus-commande (27/11/2026). A lancer sur la station ou un Linux (stat -c, sudo pour
# l'essai « ordre depose par le service radio ») :  bash tests/banc_commande.sh installation/prometheus-commande
# Tout se passe dans un dossier jetable, avec de faux programmes : rien n'est vraiment execute.
set -u
PROG=$(realpath "$1")
T=$(mktemp -d /tmp/banc-commande.XXXX)
chmod 755 "$T"
export PROMETHEUS_RACINE=$T/r PROMETHEUS_BIN=$T/bin
mkdir -p "$T/r/srv/prometheus/commande" "$T/r/srv/prometheus/commande-attente" "$T/r/srv/prometheus/bibliotheque" \
  "$T/r/var/www/prometheus/ajouter/resultats" "$T/bin" "$T/path"
chmod 777 "$T/r/srv/prometheus/commande"
JOURNAL=$T/journal; : > "$JOURNAL"
for p in prometheus-etat prometheus-sauvegarde prometheus-radio-outil prometheus-doublons prometheus-index-livres \
         prometheus-catalogue prometheus-restaurer; do
  printf '#!/bin/sh\necho "%s $*" >> %s\n' "$p" "$JOURNAL" > "$T/bin/$p"
done
ln -s "$PROG" "$T/bin/prometheus-commande"
printf '#!/bin/sh\necho "systemd-run $*" >> %s\n' "$JOURNAL" > "$T/path/systemd-run"
# systemctl is-active prometheus-radio-outil : « occupe » si le fichier $T/occupe existe
printf '#!/bin/sh\ncase "$*" in *is-active*radio-outil*) [ -e %s/occupe ] ;; *) echo "systemctl $*" >> %s ;; esac\n' "$T" "$JOURNAL" > "$T/path/systemctl"
printf '#!/bin/sh\nshift 3; exec "$@"\n' > "$T/path/runuser"
chmod +x "$T"/bin/* "$T"/path/*
export PATH=$T/path:$PATH
D=$T/r/srv/prometheus/commande; RES=$T/r/var/www/prometheus/ajouter/resultats
ECHECS=0; N=0
verifier() {   # verifier <description> <commande de test>
  N=$((N + 1))
  if eval "$2"; then echo "  ok   $1"; else echo "  ECHEC $1"; ECHECS=$((ECHECS + 1)); fi
}
etat() { python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["etat"])' "$RES/$1.json" 2>/dev/null; }
lancer() { bash "$PROG" >> "$T/sortie" 2>&1; }

printf '' > "$D/sauvegarder@a1"; lancer
verifier "sauvegarder : resultat fait" '[ "$(etat a1)" = fait ] && grep -q "prometheus-sauvegarde" "$JOURNAL"'
printf '' > "$D/nimportequoi@a2"; lancer
verifier "ordre inconnu : resultat inconnu" '[ "$(etat a2)" = inconnu ]'
printf '../../etc/passwd' > "$D/supprimer-1@a3"; lancer
verifier "supprimer un chemin : refuse" '[ "$(etat a3)" = refuse ]'
echo livre > "$T/r/srv/prometheus/bibliotheque/Livre.pdf"; printf 'Livre.pdf' > "$D/supprimer-2@a4"; lancer
verifier "supprimer un livre : fait, fichier parti" '[ "$(etat a4)" = fait ] && [ ! -e "$T/r/srv/prometheus/bibliotheque/Livre.pdf" ]'
printf '{}' > "$D/radio-detecter@a5"; lancer
verifier "radio libre : lancee, reprise prevue a la fin" '[ "$(etat a5)" = lance ] && grep -q "ExecStopPost=$T/bin/prometheus-commande --reprendre" "$JOURNAL"'
touch "$T/occupe"; printf '{"fichier":"x"}' > "$D/radio-restaurer@a6"; lancer
verifier "radio occupee : l'ordre attend, il n'est pas perdu" '[ "$(etat a6)" = attente ] && ls "$T/r/srv/prometheus/commande-attente" | grep -q "_radio-restaurer@a6$"'
rm -f "$T/occupe"; bash "$PROG" --reprendre >> "$T/sortie" 2>&1
verifier "fin de l'operation : l'ordre en attente revient, avec son contenu" '[ "$(cat "$D/radio-restaurer@a6")" = "{\"fichier\":\"x\"}" ] && [ -z "$(ls "$T/r/srv/prometheus/commande-attente")" ]'
lancer
verifier "puis il part" '[ "$(etat a6)" = lance ] && [ ! -e "$D/radio-restaurer@a6" ]'
printf 'x' > "$D/radio-restaurer.123-4.tmp"; lancer
verifier "fichier pas fini d'ecrire (.tmp) : laisse tranquille" '[ -e "$D/radio-restaurer.123-4.tmp" ]'
rm -f "$D/radio-restaurer.123-4.tmp"
if id prometheus >/dev/null 2>&1 && sudo -n true 2>/dev/null; then
  sudo -u prometheus sh -c "printf '' > '$D/eteindre@a7'"; lancer
  verifier "le service radio ne peut pas eteindre la station" '[ "$(etat a7)" = refuse ] && ! grep -q "poweroff" "$JOURNAL"'
  sudo -u prometheus sh -c "printf '{}' > '$D/radio-restaurer@a8'"; lancer
  verifier "le service radio peut demander sa remise (garde-fou)" '[ "$(etat a8)" = lance ]'
else
  echo "  (pas d'utilisateur prometheus ou pas de sudo : essais du service radio sautes)"
fi
printf '' > "$D/verifier"; lancer
verifier "ordre sans numero : execute, aucun resultat ecrit" '[ ! -e "$D/verifier" ] && [ "$(ls "$RES" | wc -l)" -le 8 ]'
echo "banc commande : $((N - ECHECS))/$N"
[ "$ECHECS" -eq 0 ] && rm -rf "$T"
[ "$ECHECS" -eq 0 ]
