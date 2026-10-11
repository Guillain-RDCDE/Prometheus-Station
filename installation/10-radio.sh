#!/bin/bash
# Prometheus Station - etape 10 : la radio Meshtastic reliee au tableau des messages
# Une carte radio Meshtastic (LILYGO T-Beam) branchee en USB : ce qui est ecrit sur le tableau part par radio
# (case « Envoyer aussi par radio »), ce qui arrive par radio s'affiche sur le tableau.
# Desactivee au depart : Parametres > Radio. Necessite internet pendant l'installation (bibliotheque Meshtastic).
# A lancer sur le Pi, depuis le dossier "installation" : sudo bash 10-radio.sh
set -euo pipefail
ICI=$(cd "$(dirname "$0")" && pwd)

echo "== Bibliotheque Meshtastic (environnement a part, dans /opt/prometheus-radio)"
apt-get install -y -qq python3-venv >/dev/null
[ -x /opt/prometheus-radio/bin/python3 ] || python3 -m venv /opt/prometheus-radio
/opt/prometheus-radio/bin/pip install -q --upgrade meshtastic

echo "== Programme et dossiers d'echange"
install -m 755 "$ICI/prometheus-radio" /usr/local/bin/prometheus-radio
install -d -o prometheus -g prometheus -m 755 /srv/prometheus/radio \
  /srv/prometheus/radio/a-envoyer /srv/prometheus/radio/partis /srv/prometheus/radio/recus

cat > /etc/systemd/system/prometheus-radio.service <<'EOF'
[Unit]
Description=Prometheus Station - radio Meshtastic reliee au tableau des messages
After=network.target

[Service]
User=prometheus
# Le droit d'ouvrir la carte radio branchee en USB
SupplementaryGroups=dialout
ExecStart=/usr/local/bin/prometheus-radio
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable prometheus-radio.service
systemctl restart prometheus-radio.service
echo "== Radio installee (desactivee tant qu'elle n'est pas activee dans Parametres > Radio)"
