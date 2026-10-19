#!/bin/bash
# Prometheus Station - etape 11 : un ecran et un clavier branches sur la station (la « mallette »), sans telephone
# Un ecran HDMI ou l'ecran tactile officiel affiche les pages de la station en plein ecran : un navigateur en mode
# kiosque (Chromium dans « cage », une seule fenetre, sans bureau), clavier francais (AZERTY), tactile.
# L'ecran se met en veille seul (reglable). Desactive au depart : Parametres > Ecran et clavier.
# Necessite internet pendant l installation (environ 1 Go avec Chromium). A lancer sur le Pi : sudo bash 11-ecran-local.sh
set -euo pipefail
ICI=$(cd "$(dirname "$0")" && pwd)

echo "== Affichage minimal et navigateur (cage, Chromium, mise en veille de l'ecran)"
export DEBIAN_FRONTEND=noninteractive
apt-get install -y -qq --no-install-recommends cage chromium swayidle wlr-randr fonts-dejavu-core fonts-noto-color-emoji >/dev/null

echo "== Utilisateur du navigateur (sans mot de passe, sans acces au reste de la station)"
id kiosque >/dev/null 2>&1 || useradd --system --create-home --home-dir /var/lib/prometheus-kiosque --shell /usr/sbin/nologin kiosque
for G in video render input; do getent group "$G" >/dev/null && usermod -aG "$G" kiosque; done
install -d -o kiosque -g kiosque -m 700 /var/lib/prometheus-kiosque

echo "== Programmes"
install -m 755 "$ICI/prometheus-kiosque" /usr/local/bin/prometheus-kiosque
install -m 755 "$ICI/prometheus-ecran-local" /usr/local/bin/prometheus-ecran-local

# Une session de connexion pour l'utilisateur du navigateur (droit sur l'ecran et le clavier), sans mot de passe
cat > /etc/pam.d/prometheus-kiosque <<'EOF'
auth    required pam_unix.so nullok
account required pam_unix.so
session required pam_unix.so
session required pam_systemd.so
EOF

cat > /etc/systemd/system/prometheus-kiosque.service <<'EOF'
[Unit]
Description=Prometheus Station - ecran de la station (pages en plein ecran)
After=systemd-user-sessions.service nginx.service
Wants=dbus.socket systemd-logind.service
After=dbus.socket systemd-logind.service
Conflicts=getty@tty7.service

[Service]
User=kiosque
PAMName=prometheus-kiosque
TTYPath=/dev/tty7
TTYReset=yes
TTYVHangup=yes
TTYVTDisallocate=yes
StandardInput=tty-fail
StandardOutput=journal
UtmpIdentifier=tty7
UtmpMode=user
# Clavier francais ; « cage » n'affiche qu'une fenetre, plein ecran, et s'arrete avec elle
Environment=XKB_DEFAULT_LAYOUT=fr
ExecStart=/usr/bin/cage -d -- /usr/local/bin/prometheus-kiosque
Restart=always
RestartSec=5
EOF

# Le reglage de la page (Parametres > Ecran et clavier) allume ou eteint l'ecran : on surveille le fichier des reglages
# Lance aussi a chaque demarrage : le service du navigateur n'est jamais active d'office, c'est ce programme qui le lance
cat > /etc/systemd/system/prometheus-ecran-local.service <<'EOF'
[Unit]
Description=Prometheus Station - applique le reglage de l'ecran de la station
After=nginx.service

[Service]
Type=oneshot
ExecStart=/usr/local/bin/prometheus-ecran-local

[Install]
WantedBy=multi-user.target
EOF
cat > /etc/systemd/system/prometheus-ecran-local.path <<'EOF'
[Unit]
Description=Prometheus Station - surveille le reglage de l'ecran de la station

[Path]
PathChanged=/srv/prometheus/communaute/reglages.json

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable prometheus-ecran-local.service
systemctl enable --now prometheus-ecran-local.path
/usr/local/bin/prometheus-ecran-local
echo "== Ecran de la station installe (desactive tant qu'il n'est pas active dans Parametres > Ecran et clavier)"
