#!/bin/bash
# Prometheus Station - etape 7 : alimentation et menagement de la carte SD
# Avec une batterie USB, le Pi ne connait pas le niveau de charge : quand elle est vide, elle coupe net.
# On s'eteint proprement si la tension faiblit, et on ecrit le moins possible sur la carte
# pour qu'une coupure brutale reste sans danger.
# Dans Parametres > Energie : un mode sobre et une extinction apres un temps sans visiteur.
# A lancer sur le Pi, depuis le dossier "installation" : sudo bash 07-energie.sh
set -euo pipefail
ICI=$(cd "$(dirname "$0")" && pwd)

echo "== Surveillant de tension (extinction propre si l'alimentation faiblit 30 secondes)"
install -m 755 "$ICI/prometheus-tension" /usr/local/bin/prometheus-tension
cat > /etc/systemd/system/prometheus-tension.service <<'EOF'
[Unit]
Description=Prometheus Station - extinction propre si l'alimentation faiblit

[Service]
ExecStart=/usr/local/bin/prometheus-tension
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
systemctl daemon-reload
systemctl enable prometheus-tension.service
systemctl restart prometheus-tension.service

echo "== Carte SD : les ecritures du systeme regroupees toutes les 30 secondes (au lieu de 5)"
# noatime : ne pas noter chaque lecture de fichier ; commit=30 : regrouper les ecritures
sed -i -E 's|^(PARTUUID=[^ ]+-02[[:space:]]+/[[:space:]]+ext4[[:space:]]+)[^[:space:]]+|\1defaults,noatime,commit=30|' /etc/fstab
grep -q 'noatime,commit=30' /etc/fstab
mount -o remount,noatime,commit=30 /

echo "== Plus aucune trace des visites ecrite sur la carte (et rien a savoir sur les visiteurs)"
# Les pages de la station n'enregistrent plus qui a lu quoi ; les erreurs restent notees
sed -i -E 's|^([[:space:]]*)access_log /var/log/nginx/access.log;|\1access_log off;|' /etc/nginx/nginx.conf
grep -q 'access_log off;' /etc/nginx/nginx.conf
nginx -t
systemctl reload nginx
rm -f /var/log/nginx/access.log*

echo "== Dossier de travail en memoire (/run/prometheus), vide a chaque demarrage"
echo 'd /run/prometheus 0755 prometheus prometheus -' > /etc/tmpfiles.d/prometheus.conf
systemd-tmpfiles --create /etc/tmpfiles.d/prometheus.conf

echo "== Mode sobre (Parametres > Energie) : voyants, processeur au ralenti, USB coupe"
install -m 755 "$ICI/prometheus-sobre" /usr/local/bin/prometheus-sobre
cat > /etc/systemd/system/prometheus-sobre.service <<'EOF'
[Unit]
Description=Prometheus Station - applique le mode sobre ou le mode normal

[Service]
Type=oneshot
ExecStart=/usr/local/bin/prometheus-sobre

[Install]
WantedBy=multi-user.target
EOF
cat > /etc/systemd/system/prometheus-sobre.path <<'EOF'
[Unit]
Description=Prometheus Station - surveille une demande de mode sobre

[Path]
PathExists=/srv/prometheus/.admin/sobre-demande

[Install]
WantedBy=multi-user.target
EOF

echo "== Extinction apres un temps sans visiteur (Parametres > Energie, jamais par defaut)"
install -m 755 "$ICI/prometheus-extinction" /usr/local/bin/prometheus-extinction
cat > /etc/systemd/system/prometheus-extinction.service <<'EOF'
[Unit]
Description=Prometheus Station - extinction apres un temps sans visiteur
After=NetworkManager.service

[Service]
ExecStart=/usr/local/bin/prometheus-extinction
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
systemctl daemon-reload
systemctl enable --now prometheus-sobre.path
systemctl enable prometheus-sobre.service
systemctl start prometheus-sobre.service
systemctl enable prometheus-extinction.service
systemctl restart prometheus-extinction.service

echo "== Etape 7 terminee"
