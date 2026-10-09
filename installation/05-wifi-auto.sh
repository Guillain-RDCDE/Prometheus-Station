#!/bin/bash
# Prometheus Station - etape 5 : wifi automatique
# Un wifi connu (maison) est a portee -> la station s'y connecte (pilotage a distance, mises a jour).
# Aucun wifi connu -> la station ouvre son propre wifi "Prometheus-Station".
# A lancer sur le Pi : sudo bash 05-wifi-auto.sh
set -euo pipefail

echo "== Le wifi de la station n'est plus allume par NetworkManager lui-meme, mais par le surveillant"
nmcli connection modify prometheus-wifi connection.autoconnect no

echo "== Commande pour ajouter un wifi de la maison"
cat > /usr/local/bin/prometheus-wifi-maison <<'EOF'
#!/bin/bash
# Ajouter un wifi connu : sudo prometheus-wifi-maison
set -e
read -r -p "Nom du wifi (exactement comme sur le telephone) : " SSID
read -r -s -p "Mot de passe du wifi : " PSK; echo
[ -n "$SSID" ] && [ -n "$PSK" ] || { echo "Nom ou mot de passe vide. Rien n'a change."; exit 1; }
nmcli connection delete "maison-$SSID" >/dev/null 2>&1 || true
nmcli connection add type wifi ifname wlan0 con-name "maison-$SSID" ssid "$SSID" \
  wifi-sec.key-mgmt wpa-psk wifi-sec.psk "$PSK" \
  connection.autoconnect yes connection.autoconnect-priority 10 >/dev/null
echo "C'est fait. La station s'y connectera des que ce wifi sera a portee (au plus tard dans 10 minutes)."
EOF
chmod 755 /usr/local/bin/prometheus-wifi-maison

echo "== Renommer le wifi de la station depuis la page Mises a jour"
cat > /usr/local/bin/prometheus-ssid <<'EOF'
#!/bin/bash
# Applique le nom demande sur la page (fichier ecrit par prometheus-admin).
DEMANDE=/srv/prometheus/.admin/ssid-demande
# On boucle : une demande arrivee pendant qu'on traitait la precedente n'est pas perdue
while [ -s "$DEMANDE" ]; do
  NOM=$(head -c 32 "$DEMANDE")
  rm -f "$DEMANDE"
  [ -n "$NOM" ] || continue
  [ "$NOM" = "$(nmcli -g 802-11-wireless.ssid connection show prometheus-wifi)" ] && continue
  nmcli connection modify prometheus-wifi 802-11-wireless.ssid "$NOM" || continue
  echo "Wifi de la station renomme : $NOM"
  # S'il est ouvert en ce moment, on le relance avec son nouveau nom
  if [ "$(nmcli -g GENERAL.CONNECTION device show wlan0)" = prometheus-wifi ]; then
    nmcli connection up prometheus-wifi >/dev/null 2>&1
  fi
done
EOF
chmod 755 /usr/local/bin/prometheus-ssid
cat > /etc/systemd/system/prometheus-ssid.path <<'EOF'
[Unit]
Description=Prometheus Station - surveille une demande de nouveau nom de wifi

[Path]
PathExists=/srv/prometheus/.admin/ssid-demande

[Install]
WantedBy=multi-user.target
EOF
cat > /etc/systemd/system/prometheus-ssid.service <<'EOF'
[Unit]
Description=Prometheus Station - renomme le wifi de la station

[Service]
Type=oneshot
ExecStart=/usr/local/bin/prometheus-ssid
EOF

echo "== Le surveillant du wifi"
cat > /usr/local/bin/prometheus-wifi-auto <<'EOF'
#!/bin/bash
# Surveille le wifi en permanence.
# - wifi de la maison connecte : rien a faire ;
# - plus aucune connexion : ouvre le wifi de la station ;
# - wifi de la station ouvert, personne dessus, un wifi connu existe : toutes les 10 minutes,
#   coupe 20 secondes pour regarder si le wifi de la maison est revenu.
AP=prometheus-wifi
DERNIER_ESSAI=$(date +%s)   # pas de coup d oeil vers la maison dans les 10 premieres minutes

actif() { nmcli -g GENERAL.CONNECTION device show wlan0 2>/dev/null; }
wifis_connus() { nmcli -t -f NAME,TYPE connection show | awk -F: '$2=="802-11-wireless" && $1!="'$AP'" {print $1}'; }
clients() { iw dev wlan0 station dump 2>/dev/null | grep -c '^Station'; }

ouvrir_station() {
  echo "Aucun wifi connu : ouverture du wifi de la station"
  nmcli connection up "$AP" >/dev/null 2>&1 || echo "!! impossible d'ouvrir le wifi de la station"
  # Le prochain coup d'oeil vers la maison n'aura lieu que dans 10 minutes
  DERNIER_ESSAI=$(date +%s)
}

chercher_maison() {
  [ -n "$(wifis_connus)" ] || return 1
  nmcli device wifi rescan >/dev/null 2>&1
  sleep 8
  VUS=$(nmcli -t -f SSID device wifi list 2>/dev/null)
  while IFS= read -r C; do
    SSID=$(nmcli -g 802-11-wireless.ssid connection show "$C")
    if printf '%s\n' "$VUS" | grep -qxF "$SSID"; then
      echo "Wifi connu a portee : $SSID"
      nmcli connection up "$C" >/dev/null 2>&1 && return 0
    fi
  done < <(wifis_connus)
  return 1
}

# Au demarrage : on laisse 45 secondes a NetworkManager pour trouver le wifi de la maison
sleep 45
[ -n "$(actif)" ] || chercher_maison || ouvrir_station

while true; do
  sleep 30
  A=$(actif)
  if [ -z "$A" ]; then
    chercher_maison || ouvrir_station
  elif [ "$A" = "$AP" ] && [ -n "$(wifis_connus)" ] && [ "$(clients)" -eq 0 ] \
       && [ $(( $(date +%s) - DERNIER_ESSAI )) -ge 600 ]; then
    DERNIER_ESSAI=$(date +%s)
    nmcli connection down "$AP" >/dev/null 2>&1
    chercher_maison || ouvrir_station
  fi
done
EOF
chmod 755 /usr/local/bin/prometheus-wifi-auto

cat > /etc/systemd/system/prometheus-wifi-auto.service <<'EOF'
[Unit]
Description=Prometheus Station - wifi automatique (maison ou station)
After=NetworkManager.service
Wants=NetworkManager.service

[Service]
ExecStart=/usr/local/bin/prometheus-wifi-auto
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable --now prometheus-wifi-auto.service prometheus-ssid.path

echo "== Etape 5 terminee. Ajouter le wifi de la maison : sudo prometheus-wifi-maison"
