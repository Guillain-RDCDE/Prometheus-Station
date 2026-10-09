#!/bin/bash
# Prometheus Station - etape 2 : les encyclopedies (Kiwix)
# A lancer sur le Pi : sudo bash 02-encyclopedies.sh
set -euo pipefail

echo "== Utilisateur systeme 'prometheus' (fait tourner les services)"
id prometheus >/dev/null 2>&1 || useradd --system --home-dir /srv/prometheus --shell /usr/sbin/nologin prometheus

echo "== Dossiers"
mkdir -p /srv/prometheus/encyclopedies /srv/prometheus/bibliotheque
chown -R prometheus:prometheus /srv/prometheus

echo "== Kiwix (paquet Debian)"
export DEBIAN_FRONTEND=noninteractive
apt-get -y install kiwix-tools curl

echo "== Liste des contenus a telecharger (le plus petit d'abord)"
cat > /srv/prometheus/contenus.txt <<'EOF'
# Un contenu par ligne : nom Kiwix sans date. La station prend toujours la version la plus recente.
# Liste complete : https://library.kiwix.org
zimgit-water_en
zimgit-food-preparation_en
zimgit-post-disaster_en
wikem_en_all_maxi
mdwiki_en_all_maxi
ifixit_fr_all
wikipedia_fr_all_maxi
gutenberg_fr_all
wikipedia_en_all_maxi
EOF
chown prometheus:prometheus /srv/prometheus/contenus.txt

echo "== Programme de telechargement"
cat > /usr/local/bin/prometheus-telecharger <<'EOF'
#!/bin/bash
# Telecharge (ou met a jour) chaque contenu de /srv/prometheus/contenus.txt.
# Reprend la ou il s'etait arrete. Verifie chaque fichier. Sans internet, ne fait rien.
DIR=/srv/prometheus/encyclopedies
LISTE=/srv/prometheus/contenus.txt

if ! curl -sI -m 15 https://download.kiwix.org >/dev/null; then
  echo "Pas d'internet : rien a faire."
  exit 0
fi

grep -vE '^\s*(#|$)' "$LISTE" | while read -r NOM; do
  # Le lien sans date renvoie vers la version la plus recente
  FINAL=$(curl -sIL -m 60 -o /dev/null -w '%{url_effective}' "https://download.kiwix.org/zim/$NOM.zim")
  CHEMIN=${FINAL#*/zim/}
  FICHIER=$(basename "$CHEMIN")
  if [ -z "$CHEMIN" ] || [ "$FICHIER" = "$NOM.zim" ]; then
    echo "!! $NOM : introuvable chez Kiwix, ignore."
    continue
  fi
  if [ -f "$DIR/$FICHIER" ] && [ ! -f "$DIR/$FICHIER.aria2" ]; then
    echo "-- $FICHIER : deja a jour."
    continue
  fi
  # Garde-fou : ne jamais remplir la carte (on garde 5 Go de marge pour le systeme)
  TAILLE=$(curl -sIL -m 60 "$FINAL" | tr -d '\r' | awk 'tolower($1)=="content-length:"{t=$2} END{print t+0}')
  DEJA=$(stat -c %s "$DIR/$FICHIER" 2>/dev/null || echo 0)
  LIBRE=$(df --output=avail -B1 "$DIR" | tail -1)
  if [ "$TAILLE" -gt 0 ] && [ $((TAILLE - DEJA + 5000000000)) -gt "$LIBRE" ]; then
    echo "!! $FICHIER : pas assez de place ($((TAILLE/1000000000)) Go necessaires, $((LIBRE/1000000000)) Go libres). Ignore."
    continue
  fi
  echo ">> $FICHIER : telechargement..."
  if aria2c --dir="$DIR" --continue=true --check-integrity=true \
       --max-connection-per-server=4 --split=4 --file-allocation=falloc \
       --show-console-readout=false --summary-interval=60 --console-log-level=warn \
       --follow-metalink=mem "https://download.kiwix.org/zim/$CHEMIN.meta4"; then
    echo "OK $FICHIER"
    # Efface les anciennes versions du meme contenu
    for VIEUX in "$DIR/${NOM}"_[0-9][0-9][0-9][0-9]-[0-9][0-9].zim; do
      [ -e "$VIEUX" ] && [ "$(basename "$VIEUX")" != "$FICHIER" ] && rm -f "$VIEUX" && echo "   ancienne version effacee : $(basename "$VIEUX")"
    done
    prometheus-catalogue
    [ -x /usr/local/bin/prometheus-index-livres ] && /usr/local/bin/prometheus-index-livres
  else
    echo "!! $FICHIER : echec, on reessaiera au prochain passage."
  fi
done
# Toujours remettre a jour la liste de la Bibliotheque (elle montre aussi Gutenberg)
[ -x /usr/local/bin/prometheus-index-livres ] && /usr/local/bin/prometheus-index-livres
exit 0
EOF
chmod 755 /usr/local/bin/prometheus-telecharger

echo "== Programme qui refait le catalogue Kiwix a partir des fichiers presents"
cat > /usr/local/bin/prometheus-catalogue <<'EOF'
#!/bin/bash
DIR=/srv/prometheus/encyclopedies
TMP="$DIR/.library.xml.tmp"
rm -f "$TMP"
for Z in "$DIR"/*.zim; do
  [ -e "$Z" ] || continue
  [ -e "$Z.aria2" ] && continue   # encore en cours de telechargement
  kiwix-manage "$TMP" add "$Z" >/dev/null 2>&1 || echo "!! fichier illisible : $Z"
done
[ -f "$TMP" ] || echo '<library version="20110515"></library>' > "$TMP"
chmod 644 "$TMP"
mv -f "$TMP" "$DIR/library.xml"
EOF
chmod 755 /usr/local/bin/prometheus-catalogue
runuser -u prometheus -- prometheus-catalogue

echo "== Service de telechargement (lance a la demande)"
cat > /etc/systemd/system/prometheus-telechargement.service <<'EOF'
[Unit]
Description=Prometheus Station - telechargement des encyclopedies
Wants=network-online.target
After=network-online.target

[Service]
Type=oneshot
User=prometheus
Nice=10
IOSchedulingClass=idle
ExecStart=/usr/local/bin/prometheus-telecharger
EOF

echo "== Reprise automatique : 5 min apres chaque demarrage, puis chaque jour"
cat > /etc/systemd/system/prometheus-telechargement.timer <<'EOF'
[Unit]
Description=Prometheus Station - reprise et mise a jour des telechargements

[Timer]
OnBootSec=5min
OnUnitInactiveSec=1d

[Install]
WantedBy=timers.target
EOF

echo "== Service Kiwix (les encyclopedies, port 8080)"
cat > /etc/systemd/system/prometheus-kiwix.service <<'EOF'
[Unit]
Description=Prometheus Station - encyclopedies (Kiwix)
After=network.target

[Service]
User=prometheus
ExecStartPre=/usr/local/bin/prometheus-catalogue
ExecStart=/usr/bin/kiwix-serve --nodatealiases --address=127.0.0.1 --port=8080 --urlRootLocation=/encyclopedies --monitorLibrary --library /srv/prometheus/encyclopedies/library.xml
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
# prometheus-catalogue ecrit library.xml : il doit pouvoir le faire en tant que prometheus
chown prometheus:prometheus /srv/prometheus/encyclopedies

systemctl daemon-reload
systemctl enable --now prometheus-kiwix.service
systemctl enable prometheus-telechargement.timer
systemctl start --no-block prometheus-telechargement.service

echo "== Etape 2 terminee. Telechargements lances (suivre : journalctl -fu prometheus-telechargement)"
