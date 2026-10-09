#!/bin/bash
# Prometheus Station - etape 1 : systeme de base
# A lancer sur le Pi : sudo bash 01-systeme.sh
set -euo pipefail

echo "== Mise a jour complete du systeme"
export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get -y full-upgrade

echo "== Pays du wifi (France) : debloque la puce wifi"
raspi-config nonint do_wifi_country FR

echo "== Interfaces SPI et I2C (ecran e-ink, capteur de batterie)"
raspi-config nonint do_spi 0
raspi-config nonint do_i2c 0

echo "== Bluetooth coupe (economie d'energie)"
grep -q '^dtoverlay=disable-bt' /boot/firmware/config.txt || echo 'dtoverlay=disable-bt' >> /boot/firmware/config.txt
systemctl disable --now hciuart.service 2>/dev/null || true

echo "== Journal du systeme limite a 50 Mo (menage la carte SD, mais survit a un redemarrage)"
mkdir -p /etc/systemd/journald.conf.d /var/log/journal
cat > /etc/systemd/journald.conf.d/prometheus.conf <<'EOF'
[Journal]
Storage=persistent
SystemMaxUse=50M
EOF

echo "== Mises a jour de securite automatiques quand internet est la"
apt-get -y install unattended-upgrades
dpkg-reconfigure -f noninteractive unattended-upgrades

echo "== Outils utiles"
apt-get -y install aria2 iw rfkill

echo "== Etape 1 terminee. Redemarrer : sudo reboot"
