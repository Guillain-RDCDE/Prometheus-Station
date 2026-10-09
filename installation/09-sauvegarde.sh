#!/bin/bash
# Prometheus Station - etape 9 : sauvegarde des reglages
# Une sauvegarde chaque jour (les 7 dernieres gardees), a telecharger depuis Parametres > Sauvegarde.
# Pour la remettre sur une station reinstallee : sudo prometheus-restaurer <fichier>
# A lancer sur le Pi, depuis le dossier "installation" : sudo bash 09-sauvegarde.sh
set -euo pipefail
ICI=$(cd "$(dirname "$0")" && pwd)

echo "== Programmes de sauvegarde et de restauration"
install -m 755 "$ICI/prometheus-sauvegarde" /usr/local/bin/prometheus-sauvegarde
install -m 755 "$ICI/prometheus-restaurer" /usr/local/bin/prometheus-restaurer

cat > /etc/systemd/system/prometheus-sauvegarde.service <<'EOF'
[Unit]
Description=Prometheus Station - sauvegarde des reglages

[Service]
Type=oneshot
ExecStart=/usr/local/bin/prometheus-sauvegarde
EOF
cat > /etc/systemd/system/prometheus-sauvegarde.timer <<'EOF'
[Unit]
Description=Prometheus Station - sauvegarde des reglages chaque jour

[Timer]
OnBootSec=15min
OnUnitActiveSec=1d
Persistent=true

[Install]
WantedBy=timers.target
EOF
systemctl daemon-reload
systemctl enable --now prometheus-sauvegarde.timer

echo "== Premiere sauvegarde"
/usr/local/bin/prometheus-sauvegarde
/usr/local/bin/prometheus-etat

echo "== Etape 9 terminee"
