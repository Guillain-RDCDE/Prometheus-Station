#!/bin/bash
# Prometheus Station - etape 12 : carte batterie Geekworm X728 (V2.x) avec ses accus 18650
# La station lit la charge de ses accus, sait si le secteur est branche, s'eteint proprement quand les accus
# sont presque vides, puis la carte coupe le courant. Le bouton de la carte : court = redemarrer, long = eteindre.
# Sans carte X728, le programme ne fait rien. A lancer sur le Pi, depuis le dossier "installation" :
#   sudo bash 12-batterie.sh
set -euo pipefail
ICI=$(cd "$(dirname "$0")" && pwd)

echo "== Bibliotheques (bus I2C de la jauge, broches)"
export DEBIAN_FRONTEND=noninteractive
apt-get -y install python3-smbus2 python3-lgpio
# Le bus I2C est deja active par l'etape 1 (dtparam=i2c_arm=on)
grep -q '^dtparam=i2c_arm=on' /boot/firmware/config.txt || echo "ATTENTION : I2C pas active (etape 1), puis redemarrer"

echo "== Programme de la carte batterie"
install -m 755 "$ICI/prometheus-batterie" /usr/local/bin/prometheus-batterie
cat > /etc/systemd/system/prometheus-batterie.service <<'UNIT'
[Unit]
Description=Prometheus Station - carte batterie X728 (charge, extinction propre, bouton)

[Service]
ExecStart=/usr/local/bin/prometheus-batterie
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
UNIT

echo "== A la toute fin d'une extinction, la carte coupe le courant (sinon elle garderait le Pi eteint sous tension)"
mkdir -p /usr/lib/systemd/system-shutdown
cat > /usr/lib/systemd/system-shutdown/prometheus-batterie <<'CROCHET'
#!/bin/sh
# Lance par systemd quand tout est deja ecrit et les disques en lecture seule. Seulement pour une extinction :
# une impulsion de 4 s sur la broche 26 (comme un appui long) demande a la X728 de couper le courant.
[ "$1" = poweroff ] || exit 0
pinctrl set 26 op dh
sleep 4
pinctrl set 26 op dl
CROCHET
chmod 755 /usr/lib/systemd/system-shutdown/prometheus-batterie

systemctl daemon-reload
systemctl enable prometheus-batterie.service
systemctl restart prometheus-batterie.service

echo "== Etape 12 terminee (Parametres > Etat de la station : charge des accus)"
