#!/bin/bash
# Prometheus Station - etape 10 : la radio Meshtastic reliee au tableau des messages
# Une carte radio Meshtastic (LILYGO T-Beam) branchee en USB : ce qui est ecrit sur le tableau part par radio
# (case « Envoyer aussi par radio »), ce qui arrive par radio s'affiche sur le tableau.
# Desactivee au depart : Parametres > Radio. Necessite internet pendant l'installation (bibliotheque Meshtastic).
# A lancer sur le Pi, depuis le dossier "installation" : sudo bash 10-radio.sh
set -euo pipefail
ICI=$(cd "$(dirname "$0")" && pwd)
# Module commun des programmes, table des dossiers, liste de la sauvegarde : commun.sh (le meme pour chaque etape)
. "$ICI/commun.sh"

echo "== Bibliotheques Meshtastic et MeshCore, outil d'ecriture des radios (environnement a part, /opt/prometheus-radio)"
apt-get install -y -qq python3-venv bluez >/dev/null
[ -x /opt/prometheus-radio/bin/python3 ] || python3 -m venv /opt/prometheus-radio
# adafruit-nrfutil : installer un T-Echo par son port serie quand son disque de mise a jour n'apparait pas
/opt/prometheus-radio/bin/pip install -q --upgrade meshtastic meshcore esptool adafruit-nrfutil

echo "== Programmes et dossiers d'echange"
install -m 755 "$ICI/prometheus-radio" /usr/local/bin/prometheus-radio
install -m 755 "$ICI/prometheus-radio-outil" /usr/local/bin/prometheus-radio-outil
install -m 755 "$ICI/prometheus-horloge" /usr/local/bin/prometheus-horloge
# Modules partages par la radio, l'outil radio et la page (materiel, tailles, sauvegardes, garde-fou, secrets) :
# Python pur, installes a cote de prometheus_commun.py par commun.sh (plus haut)
# Dossiers d'echange (messages, ordres et reponses prives, sauvegardes, logiciels) et le droit du garde-fou de deposer
# un ordre : table des dossiers (prometheus-dossiers.conf)
appliquer_dossiers

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

# L'heure par la radio : sans Internet ni horloge de carte, quand les radios entendues s'accordent sur l'heure,
# prometheus-radio (sans droits) depose une demande ; prometheus-horloge (root) reverifie et met la station a l'heure.
cat > /etc/systemd/system/prometheus-horloge-radio.path <<'EOF'
[Unit]
Description=Prometheus Station - heure donnee par les radios entendues

[Path]
PathChanged=/run/prometheus/heure-radio.json

[Install]
WantedBy=multi-user.target
EOF
cat > /etc/systemd/system/prometheus-horloge-radio.service <<'EOF'
[Unit]
Description=Prometheus Station - mise a l'heure par la radio

[Service]
Type=oneshot
ExecStart=/usr/local/bin/prometheus-horloge --radio
EOF

systemctl daemon-reload
systemctl enable prometheus-radio.service
systemctl enable --now prometheus-radio-chercher.timer
systemctl enable --now prometheus-horloge-radio.path
systemctl restart prometheus-radio.service

echo "== Vos cartes radio (cartes.txt) : leurs logiciels seront gardes pour l'atelier"
# Une carte par ligne ; ajoutees a celles deja cochees dans Mesh > Atelier > Mes cartes (rien n'est retire)
if grep -qvE '^[[:space:]]*(#|$)' "$ICI/cartes.txt" 2>/dev/null; then
  /opt/prometheus-radio/bin/python3 - "$ICI/cartes.txt" <<'EOF'
import json, re, sys
noms = [l.split('#')[0].strip() for l in open(sys.argv[1], encoding='utf-8')]
noms = [n for n in noms if re.fullmatch(r'[\w.+-]{1,60}', n)]
f = '/srv/prometheus/radio/cartes-suivies.json'
try:
    s = json.load(open(f))
except (OSError, ValueError):
    s = {}
# Le meme nom est essaye dans les deux catalogues : seul celui qui le connait telecharge quelque chose
for k in ('meshtastic', 'meshcore'):
    s[k] = sorted(set(s.get(k, [])) | set(noms))
json.dump(s, open(f, 'w'))
print('   cartes :', ', '.join(noms))
EOF
  chown prometheus:prometheus /srv/prometheus/radio/cartes-suivies.json
else
  echo "   aucune (la radio de la station et les cartes branchees sont suivies d'office)"
fi

echo "== Logiciels des radios gardes sur la station (Meshtastic et MeshCore, derniere version stable)"
# Pour changer de reseau et mettre les radios a jour sans internet. Sans internet ici : a refaire depuis la page Radio.
/usr/local/bin/prometheus-radio-outil chercher || echo "(pas d'internet : page Radio > Logiciels des radios > Chercher, plus tard)"
echo "== Radio installee (desactivee tant qu'elle n'est pas activee dans Parametres > Radio)"
