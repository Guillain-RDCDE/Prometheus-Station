#!/bin/bash
# Prometheus Station - ce que chaque etape d'installation fait de la meme facon (27/11/2026).
# Lu au debut de chaque etape (. "$ICI/commun.sh") : installe le module commun des programmes, la table des
# dossiers et la liste de ce qui est sauvegarde ; a la fin de l'etape, appliquer_dossiers remet chaque dossier
# a son proprietaire et a ses droits (table prometheus-dossiers.conf). Relancer une etape seule ne casse plus rien.
# shellcheck disable=SC2034  # ICI est fixe par l'etape qui lit ce fichier
installer_commun() {
  install -d -m 755 /usr/local/lib/prometheus
  install -m 644 "$ICI/prometheus_commun.py" /usr/local/lib/prometheus/prometheus_commun.py
  local m
  for m in "$ICI"/radio_*.py; do
    [ -f "$m" ] && install -m 644 "$m" /usr/local/lib/prometheus/
  done
  install -m 755 "$ICI/prometheus-commun" /usr/local/bin/prometheus-commun
  install -m 644 "$ICI/prometheus-sauvegarde.liste" /usr/local/lib/prometheus/sauvegarde.liste
  install -m 644 "$ICI/prometheus-dossiers.conf" /etc/tmpfiles.d/prometheus.conf
}

appliquer_dossiers() {
  # Avant l'etape 2, l'utilisateur « prometheus » n'existe pas encore : rien a appliquer
  id prometheus >/dev/null 2>&1 || return 0
  echo "== Dossiers : proprietaires et droits (table /etc/tmpfiles.d/prometheus.conf)"
  systemd-tmpfiles --create /etc/tmpfiles.d/prometheus.conf
}

installer_commun
