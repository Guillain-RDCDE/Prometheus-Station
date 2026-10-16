#!/bin/bash
# Prometheus Station - etape 10 : la radio Meshtastic reliee au tableau des messages
# Une carte radio Meshtastic (LILYGO T-Beam) branchee en USB : ce qui est ecrit sur le tableau part par radio
# (case « Envoyer aussi par radio »), ce qui arrive par radio s'affiche sur le tableau.
# Desactivee au depart : Parametres > Radio. Necessite internet pendant l'installation (bibliotheque Meshtastic).
# A lancer sur le Pi, depuis le dossier "installation" : sudo bash 10-radio.sh
set -euo pipefail
ICI=$(cd "$(dirname "$0")" && pwd)

echo "== Bibliotheques Meshtastic et MeshCore, outil d'ecriture des radios (environnement a part, /opt/prometheus-radio)"
apt-get install -y -qq python3-venv bluez >/dev/null
[ -x /opt/prometheus-radio/bin/python3 ] || python3 -m venv /opt/prometheus-radio
# adafruit-nrfutil : installer un T-Echo par son port serie quand son disque de mise a jour n'apparait pas
/opt/prometheus-radio/bin/pip install -q --upgrade meshtastic meshcore esptool adafruit-nrfutil

echo "== Programmes et dossiers d'echange"
install -m 755 "$ICI/prometheus-radio" /usr/local/bin/prometheus-radio
install -m 755 "$ICI/prometheus-radio-outil" /usr/local/bin/prometheus-radio-outil
install -d -o prometheus -g prometheus -m 755 /srv/prometheus/radio \
  /srv/prometheus/radio/a-envoyer /srv/prometheus/radio/partis /srv/prometheus/radio/recus
# Logiciels des radios (telecharges par l'outil) et sauvegardes des reglages (identite des radios : root seulement)
install -d -m 755 /srv/prometheus/radio/logiciels
install -d -m 700 /srv/prometheus/radio/sauvegardes

cat > /etc/systemd/system/prometheus-radio.service <<'EOF'
[Unit]
Description=Prometheus Station - radio (Meshtastic ou MeshCore) reliee au tableau des messages
After=network.target

[Service]
User=prometheus
# Le droit d'ouvrir la carte radio branchee en USB
SupplementaryGroups=dialout
# Sur MeshCore, la radio se pilote par Bluetooth : on l'allume (en root : le « + »). Eteint sur Meshtastic.
ExecStartPre=+/bin/sh -c 'if grep -q "\"meshcore\"" /srv/prometheus/radio/reseau.json 2>/dev/null; then /usr/sbin/rfkill unblock bluetooth; systemctl start bluetooth; fi'
ExecStart=/usr/local/bin/prometheus-radio
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Chaque jour, quand il y a internet : telecharger les nouvelles versions des logiciels des radios.
# L'installation dans une radio reste un bouton de la page Radio (une radio se coupe pendant sa mise a jour).
cat > /etc/systemd/system/prometheus-radio-chercher.service <<'EOF'
[Unit]
Description=Prometheus Station - recherche des nouveaux logiciels des radios
After=network-online.target

[Service]
Type=oneshot
ExecStart=/usr/local/bin/prometheus-radio-outil chercher-auto
EOF
cat > /etc/systemd/system/prometheus-radio-chercher.timer <<'EOF'
[Unit]
Description=Prometheus Station - recherche quotidienne des logiciels des radios

[Timer]
OnBootSec=20min
OnUnitActiveSec=1d
RandomizedDelaySec=1h
Persistent=true

[Install]
WantedBy=timers.target
EOF

systemctl daemon-reload
systemctl enable prometheus-radio.service
systemctl enable --now prometheus-radio-chercher.timer
systemctl restart prometheus-radio.service

echo "== Logiciels des radios gardes sur la station (Meshtastic et MeshCore, derniere version stable)"
# Pour changer de reseau et mettre les radios a jour sans internet. Sans internet ici : a refaire depuis la page Radio.
/usr/local/bin/prometheus-radio-outil chercher || echo "(pas d'internet : page Radio > Logiciels des radios > Chercher, plus tard)"
echo "== Radio installee (desactivee tant qu'elle n'est pas activee dans Parametres > Radio)"
