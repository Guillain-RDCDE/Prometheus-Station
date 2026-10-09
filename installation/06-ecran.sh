#!/bin/bash
# Prometheus Station - etape 6 : ecran e-ink Waveshare 2.13" (version V4), pose sur les broches du Pi
# A lancer sur le Pi, depuis le dossier "installation" : sudo bash 06-ecran.sh
set -euo pipefail
ICI=$(cd "$(dirname "$0")" && pwd)

echo "== Bibliotheques Python (images, QR code, police)"
export DEBIAN_FRONTEND=noninteractive
apt-get -y install python3-pil python3-qrcode python3-spidev python3-gpiozero python3-lgpio fonts-dejavu-core

echo "== Pilote Waveshare (seulement les fichiers utiles, depuis le depot officiel)"
mkdir -p /opt/prometheus/waveshare_epd
B=https://raw.githubusercontent.com/waveshareteam/e-Paper/master/RaspberryPi_JetsonNano/python/lib/waveshare_epd
for F in __init__.py epdconfig.py epd2in13_V4.py; do
  curl -fsSL -o /opt/prometheus/waveshare_epd/$F $B/$F
done

echo "== Programme d'affichage"
install -m 755 "$ICI/prometheus-ecran" /usr/local/bin/prometheus-ecran
cat > /etc/systemd/system/prometheus-ecran.service <<'EOF'
[Unit]
Description=Prometheus Station - ecran e-ink
After=NetworkManager.service

[Service]
ExecStart=/usr/local/bin/prometheus-ecran
# A l'extinction (pas au redemarrage) : « Station eteinte, rebranchez la batterie »
ExecStopPost=/usr/local/bin/prometheus-ecran --si-extinction
Restart=always
RestartSec=30

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable prometheus-ecran.service
systemctl restart prometheus-ecran.service

echo "== Etape 6 terminee"
