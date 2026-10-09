#!/bin/bash
# Prometheus Station - etape 8 : securite du reseau
# - pare-feu : sur le wifi ouvert de la station, seules les pages (port 80) sont joignables ;
#   l'administration a distance (SSH) ne passe que par le cable, le wifi de la maison ou Tailscale ;
# - Kiwix n'ecoute plus que la station elle-meme : on passe toujours par les pages (port 80) ;
# - les telephones connectes au wifi de la station ne peuvent pas se contacter entre eux.
# A lancer sur le Pi, depuis le dossier "installation" : sudo bash 08-securite.sh
# Filet : si plus rien ne repond apres le lancement, le pare-feu se coupe tout seul au bout de 5 minutes,
# sauf si on confirme avant avec : sudo systemctl stop prometheus-parefeu-filet.timer
set -euo pipefail
STATION=10.42.0.0/24   # le wifi de la station (adresses donnees aux telephones)

echo "== Kiwix : seulement pour la station elle-meme (127.0.0.1)"
F=/etc/systemd/system/prometheus-kiwix.service
grep -q -- '--address=127.0.0.1' "$F" || sed -i 's|kiwix-serve --port=8080|kiwix-serve --address=127.0.0.1 --port=8080|' "$F"
grep -q -- '--address=127.0.0.1' "$F"
systemctl daemon-reload
systemctl restart prometheus-kiwix

echo "== Telephones isoles les uns des autres sur le wifi de la station"
nmcli connection modify prometheus-wifi 802-11-wireless.ap-isolation 1

echo "== Pare-feu (ufw)"
export DEBIAN_FRONTEND=noninteractive
apt-get -y install ufw
ufw default deny incoming
ufw default allow outgoing
# L'ordre compte : le refus SSH depuis le wifi de la station passe avant l'autorisation generale
ufw deny from "$STATION" to any port 22 proto tcp comment 'pas de SSH depuis le wifi de la station'
ufw allow 22/tcp comment 'SSH : cable, wifi de la maison'
ufw allow in on tailscale0 comment 'Tailscale'
ufw allow 80/tcp comment 'pages de la station'
ufw allow in on wlan0 to any port 67 proto udp comment 'adresses donnees aux telephones (DHCP)'
ufw allow in on wlan0 to any port 53 comment 'noms (DNS) pour le portail'
ufw allow 5353/udp comment 'prometheus-station.local (mDNS)'
ufw logging off   # pas de trace de chaque refus : moins d'ecritures sur la carte

echo "== Filet : coupe le pare-feu dans 5 minutes si on ne confirme pas"
systemctl stop prometheus-parefeu-filet.timer 2>/dev/null || true
systemd-run --unit=prometheus-parefeu-filet --on-active=300 /usr/sbin/ufw disable
ufw --force enable
ufw status verbose

echo "== Etape 8 lancee. Verifier qu'on se reconnecte (SSH, pages), puis CONFIRMER :"
echo "   sudo systemctl stop prometheus-parefeu-filet.timer"
