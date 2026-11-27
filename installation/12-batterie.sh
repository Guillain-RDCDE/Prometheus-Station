#!/bin/bash
# Prometheus Station - etape 12 : carte batterie Geekworm X728 (V2.x) avec ses accus 18650
# La station lit la charge de ses accus, sait si le secteur est branche, s'eteint proprement quand les accus
# sont presque vides, puis la carte coupe le courant. Le bouton de la carte : court = redemarrer, long = eteindre.
# L'horloge de la carte garde l'heure station eteinte : la station est a l'heure au demarrage, meme sans Internet.
# Sans carte X728, le programme ne fait rien. A lancer sur le Pi, depuis le dossier "installation" :
#   sudo bash 12-batterie.sh
set -euo pipefail
ICI=$(cd "$(dirname "$0")" && pwd)
# Module commun des programmes, table des dossiers, liste de la sauvegarde : commun.sh (le meme pour chaque etape)
. "$ICI/commun.sh"

echo "== Bibliotheques (bus I2C de la jauge, broches)"
export DEBIAN_FRONTEND=noninteractive
apt-get -y install python3-smbus2 python3-lgpio util-linux-extra   # util-linux-extra : hwclock
# Le bus I2C est deja active par l'etape 1 (dtparam=i2c_arm=on)
grep -q '^dtparam=i2c_arm=on' /boot/firmware/config.txt || echo "ATTENTION : I2C pas active (etape 1), puis redemarrer"

echo "== Horloge de la carte (puce DS1307, adresse 0x68) : prise en compte au prochain redemarrage"
REDEMARRER=non
if ! grep -q '^dtoverlay=i2c-rtc,ds1307' /boot/firmware/config.txt; then
    cp /boot/firmware/config.txt "/boot/firmware/config.txt.bak_$(date +%Y%m%d)"
    printf '\n# Horloge de la carte batterie X728 (Prometheus Station, etape 12)\ndtoverlay=i2c-rtc,ds1307\n' >> /boot/firmware/config.txt
    REDEMARRER=oui
fi
install -m 755 "$ICI/prometheus-horloge" /usr/local/bin/prometheus-horloge
cat > /etc/systemd/system/prometheus-horloge.service <<'UNIT'
[Unit]
Description=Prometheus Station - mise a l'heure par l'horloge de la carte batterie
DefaultDependencies=no
# Apres systemd-timesyncd : a l'extinction on s'arrete donc AVANT lui, quand sa marque « synchronized » existe encore
# (elle disparait avec lui). Au demarrage le reseau n'est pas encore la : il n'a pas pu prendre l'heure avant nous.
After=systemd-modules-load.service systemd-udevd.service local-fs.target systemd-timesyncd.service
Before=time-set.target sysinit.target shutdown.target
Wants=time-set.target
# Sans les dependances par defaut, rien n'arreterait ce service a l'extinction : ExecStop ne tournerait jamais
Conflicts=shutdown.target

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/usr/local/bin/prometheus-horloge --demarrage
# A l'extinction : la derniere heure d'Internet dans la carte
ExecStop=/usr/local/bin/prometheus-horloge --ecrire

[Install]
WantedBy=sysinit.target
UNIT
cat > /etc/systemd/system/prometheus-horloge-ecrire.service <<'UNIT'
[Unit]
Description=Prometheus Station - recopie l'heure d'Internet dans l'horloge de la carte batterie

[Service]
Type=oneshot
ExecStart=/usr/local/bin/prometheus-horloge --ecrire
UNIT
cat > /etc/systemd/system/prometheus-horloge-ecrire.timer <<'UNIT'
[Unit]
Description=Prometheus Station - heure d'Internet vers la carte batterie, chaque heure

[Timer]
OnBootSec=5min
OnUnitActiveSec=1h

[Install]
WantedBy=timers.target
UNIT

echo "== Programme de la carte batterie"
install -m 755 "$ICI/prometheus-batterie" /usr/local/bin/prometheus-batterie
cat > /etc/systemd/system/prometheus-batterie.service <<'UNIT'
[Unit]
Description=Prometheus Station - carte batterie X728 (charge, extinction propre, bouton)
# A l'heure avant de noter quoi que ce soit dans le journal
After=prometheus-horloge.service

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
systemctl enable prometheus-horloge.service prometheus-horloge-ecrire.timer prometheus-batterie.service
systemctl start prometheus-horloge-ecrire.timer
systemctl restart prometheus-batterie.service
[ "$REDEMARRER" = oui ] && echo "ATTENTION : redemarrer la station pour que l'horloge de la carte soit vue (/dev/rtc0)"

echo "== Etape 12 terminee (Parametres > Etat de la station : charge des accus)"
