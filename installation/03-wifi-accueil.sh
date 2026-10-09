#!/bin/bash
# Prometheus Station - etape 3 : wifi ouvert, portail d'accueil, bibliotheque, page Ajouter
# A lancer sur le Pi, depuis le dossier "installation" : sudo bash 03-wifi-accueil.sh
set -euo pipefail
ICI=$(cd "$(dirname "$0")" && pwd)
WEB=/var/www/prometheus

echo "== Serveur web (nginx)"
export DEBIAN_FRONTEND=noninteractive
apt-get -y install nginx

echo "== Pages de la station"
mkdir -p "$WEB/vendor" "$WEB/bibliotheque" "$WEB/ajouter" "$WEB/encyclopedies"
mkdir -p "$WEB/themes"
cp "$ICI"/web/themes/*.css "$WEB/themes/"
# Jeu de couleurs choisi sur la page Mises a jour (Ocean par defaut) ; garde au fil des reinstallations
THEME=$(cat /srv/prometheus/.admin/theme 2>/dev/null || cat /srv/prometheus/.theme 2>/dev/null || echo ocean)
[ -f "$WEB/themes/$THEME.css" ] || THEME=ocean
cp "$WEB/themes/$THEME.css" "$WEB/theme.css"
cp "$ICI/web/index.html" "$ICI/web/style.css" "$ICI/web/logo.svg" "$ICI/web/connexion.html" "$ICI/web/langue.js" "$ICI/web/panneau.js" "$ICI/web/annonce.js" "$ICI/web/communaute.css" "$WEB/"
# Annonce, Retrouver ses proches, Entraide, Urgence (eteintes au depart, Parametres > Communaute)
for P in registre entraide urgence; do mkdir -p "$WEB/$P"; cp "$ICI/web/$P/index.html" "$WEB/$P/"; done
mkdir -p "$WEB/panneau"
cp "$ICI/web/panneau/index.html" "$WEB/panneau/"
rm -f "$WEB/logo.png"   # ancien logo sur fond blanc, remplace par logo.svg
cp "$ICI/web/bibliotheque/index.html" "$ICI/web/bibliotheque/lire.html" "$WEB/bibliotheque/"
cp "$ICI/web/ajouter/index.html" "$WEB/ajouter/"
rm -f "$WEB/ajouter/maj.html"   # remplacee par /parametres/
mkdir -p "$WEB/parametres"
cp "$ICI/web/parametres/index.html" "$ICI/web/parametres/affiche.html" "$WEB/parametres/"
mkdir -p "$WEB/messages"
cp "$ICI/web/messages/index.html" "$WEB/messages/"
mkdir -p "$WEB/encyclopedies"
cp "$ICI/web/encyclopedies/index.html" "$WEB/encyclopedies/"
# Lecteur de livres EPUB, garde sur la station pour marcher sans internet
curl -fsSL -o "$WEB/vendor/epub.min.js" https://cdn.jsdelivr.net/npm/epubjs@0.3.93/dist/epub.min.js
curl -fsSL -o "$WEB/vendor/jszip.min.js" https://cdn.jsdelivr.net/npm/jszip@3.10.1/dist/jszip.min.js
# QR code de l'affiche a imprimer (Parametres > Affiche), lui aussi garde sur la station
curl -fsSL -o "$WEB/vendor/qrcode.js" https://cdn.jsdelivr.net/npm/qrcode-generator@1.4.4/qrcode.js
chown -R root:root "$WEB"
chown prometheus:prometheus "$WEB/bibliotheque"
find "$WEB" -type f -exec chmod 644 {} +
chown prometheus:prometheus "$WEB/theme.css"   # le serveur du mot de passe change les couleurs
# Choix des couleurs garde par le serveur du mot de passe (ancien emplacement : /srv/prometheus/.theme)
mkdir -p /srv/prometheus/.admin
echo "$THEME" > /srv/prometheus/.admin/theme
chown -R prometheus:prometheus /srv/prometheus/.admin
rm -f /srv/prometheus/.theme

echo "== Dossiers de la bibliotheque et du depot"
mkdir -p /srv/prometheus/bibliotheque /srv/prometheus/depot /srv/prometheus/.envoi
chown prometheus:prometheus /srv/prometheus/bibliotheque
chown www-data:www-data /srv/prometheus/depot /srv/prometheus/.envoi

echo "== Programmes : liste des livres et rangement automatique"
install -m 755 "$ICI/prometheus-index-livres" /usr/local/bin/prometheus-index-livres
install -m 755 "$ICI/prometheus-ranger" /usr/local/bin/prometheus-ranger
install -m 755 "$ICI/prometheus-etat" /usr/local/bin/prometheus-etat
install -m 755 "$ICI/prometheus-commande" /usr/local/bin/prometheus-commande
mkdir -p /srv/prometheus/commande
chown www-data:www-data /srv/prometheus/commande
# Version a jour du programme de telechargement (il appelle aussi la liste des livres)
sed -n "/^cat > \/usr\/local\/bin\/prometheus-telecharger <<'EOF'$/,/^EOF$/p" "$ICI/02-encyclopedies.sh" | sed '1d;$d' > /tmp/prometheus-telecharger
install -m 755 /tmp/prometheus-telecharger /usr/local/bin/prometheus-telecharger
runuser -u prometheus -- /usr/local/bin/prometheus-index-livres

cat > /etc/systemd/system/prometheus-ranger.path <<'EOF'
[Unit]
Description=Prometheus Station - surveille le depot de fichiers

[Path]
DirectoryNotEmpty=/srv/prometheus/depot

[Install]
WantedBy=multi-user.target
EOF
cat > /etc/systemd/system/prometheus-ranger.service <<'EOF'
[Unit]
Description=Prometheus Station - range les fichiers recus

[Service]
Type=oneshot
ExecStart=/usr/local/bin/prometheus-ranger
EOF

echo "== Boutons de la page Mises a jour (un fichier depose = un ordre)"
cat > /etc/systemd/system/prometheus-commande.path <<'EOF'
[Unit]
Description=Prometheus Station - surveille les ordres de la page Mises a jour

[Path]
DirectoryNotEmpty=/srv/prometheus/commande

[Install]
WantedBy=multi-user.target
EOF
cat > /etc/systemd/system/prometheus-commande.service <<'EOF'
[Unit]
Description=Prometheus Station - execute un ordre de la page Mises a jour

[Service]
Type=oneshot
ExecStart=/usr/local/bin/prometheus-commande
EOF

echo "== Mot de passe des pages d'administration (un seul champ, pas d'identifiant)"
install -m 755 "$ICI/prometheus-admin" /usr/local/bin/prometheus-admin
mkdir -p /srv/prometheus/.admin
chown prometheus:prometheus /srv/prometheus/.admin
chmod 700 /srv/prometheus/.admin
rm -f /etc/nginx/prometheus.htpasswd   # ancienne fenetre du navigateur, remplacee
mkdir -p /srv/prometheus/messages        # tableau des messages
chown prometheus:prometheus /srv/prometheus/messages
# Panneau d'accueil (le phare de l'accueil) : un texte de depart, jamais ecrase s'il existe deja
mkdir -p /srv/prometheus/panneau
[ -f /srv/prometheus/panneau/panneau.txt ] || cp "$ICI/panneau-depart.txt" /srv/prometheus/panneau/panneau.txt
chown -R prometheus:prometheus /srv/prometheus/panneau
mkdir -p /srv/prometheus/communaute       # annonce, registre des personnes, entraide
chown -R prometheus:prometheus /srv/prometheus/communaute
cat > /etc/systemd/system/prometheus-admin.service <<'EOF'
[Unit]
Description=Prometheus Station - mot de passe des pages d'administration

[Service]
User=prometheus
ExecStart=/usr/local/bin/prometheus-admin
# Droit de regler l'horloge (heure donnee par le premier telephone quand il n'y a pas internet)
AmbientCapabilities=CAP_SYS_TIME
CapabilityBoundingSet=CAP_SYS_TIME
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF
cat > /usr/local/bin/prometheus-mot-de-passe <<'EOF'
#!/bin/bash
# Mot de passe oublie : sudo prometheus-mot-de-passe
# Efface le mot de passe ; la page de connexion proposera d'en choisir un nouveau.
rm -f /srv/prometheus/.admin/mot-de-passe /srv/prometheus/.admin/sessions.json
echo "Mot de passe efface. Ouvrez la page Ajouter de la station pour en choisir un nouveau."
EOF
chmod 755 /usr/local/bin/prometheus-mot-de-passe

echo "== Encyclopedies : adresses sans date (les raccourcis de la page Urgence survivent aux mises a jour)"
K=/etc/systemd/system/prometheus-kiwix.service
if [ -f "$K" ] && ! grep -q -- '--nodatealiases' "$K"; then
  sed -i 's|kiwix-serve |kiwix-serve --nodatealiases |' "$K"
  systemctl daemon-reload
  systemctl restart prometheus-kiwix
fi

echo "== Configuration du serveur web"
cat > /etc/nginx/sites-available/prometheus <<'EOF'
# Toute adresse inconnue (captive.apple.com, google.com...) renvoie vers l'accueil :
# c'est ce qui fait s'ouvrir la page toute seule sur les telephones.
server {
    listen 80 default_server;
    server_name _;
    return 302 http://$server_addr/;
}

server {
    listen 80;
    server_name ~^[0-9.]+$ prometheus-station.local localhost;
    root /var/www/prometheus;
    index index.html;
    charset utf-8;

    # Notre page Encyclopedies remplace celle de Kiwix
    location = /encyclopedies { return 301 /encyclopedies/; }
    location = /encyclopedies/ { try_files /encyclopedies/index.html =404; }

    # Les articles : Kiwix, plus un bouton flottant pour revenir a la recherche
    # Les couleurs changent depuis la page Mises a jour : jamais de vieille copie en cache
    location ~ ^/(style|theme)\.css$ {
        add_header Cache-Control "no-cache";
    }

    location /encyclopedies/content/ {
        proxy_pass http://127.0.0.1:8080;
        proxy_read_timeout 300s;
        proxy_set_header Accept-Encoding "";
        sub_filter_once on;
        sub_filter '</body>' '<a href="/encyclopedies/" aria-label="Rechercher" style="position:fixed;right:18px;bottom:18px;z-index:2147483647;width:52px;height:52px;border-radius:26px;background:#111;display:flex;align-items:center;justify-content:center;box-shadow:0 6px 20px rgba(0,0,0,.25)"><svg width="22" height="22" viewBox="0 0 20 20" fill="none" stroke="#fff" stroke-width="2.4" stroke-linecap="round"><circle cx="8.5" cy="8.5" r="6.5"/><path d="M13.5 13.5 18 18"/></svg></a><script src="/annonce.js"></script></body>';
    }

    # Le reste de Kiwix (catalogue, recherche, images)
    location /encyclopedies {
        proxy_pass http://127.0.0.1:8080;
        proxy_read_timeout 300s;
    }

    location /bibliotheque/livres/ {
        alias /srv/prometheus/bibliotheque/;
        types { application/epub+zip epub; application/pdf pdf; }
    }

    location /ajouter/ {
        auth_request /_auth;
        error_page 401 = @connexion;
    }

    location /parametres/ {
        auth_request /_auth;
        error_page 401 = @connexion;
    }
    location = /ajouter/maj.html { return 301 /parametres/; }

    # Sauvegardes des reglages (etape 9), a telecharger depuis Parametres > Sauvegarde
    location /parametres/sauvegardes/ {
        auth_request /_auth;
        error_page 401 = @connexion;
        alias /srv/prometheus/sauvegardes/;
        add_header Content-Disposition "attachment";
    }

    location @connexion {
        return 302 /connexion.html?retour=$uri;
    }

    # Verification du mot de passe par le petit serveur prometheus-admin
    location = /_auth {
        internal;
        proxy_pass http://127.0.0.1:8091/verif;
        proxy_pass_request_body off;
        proxy_set_header Content-Length "";
    }

    # Tableau des messages et heure : pour tous les visiteurs
    location /api/ {
        proxy_pass http://127.0.0.1:8091/api/;
        proxy_set_header X-Real-IP $remote_addr;
        client_max_body_size 4k;
    }

    location /admin-api/ {
        proxy_pass http://127.0.0.1:8091/;
        proxy_set_header X-Real-IP $remote_addr;
        client_max_body_size 64k;   # le texte du panneau d'accueil
    }

    location /ajouter/commande/ {
        auth_request /_auth;
        alias /srv/prometheus/commande/;
        dav_methods PUT;
        client_max_body_size 1k;
        limit_except PUT { deny all; }
    }

    location /ajouter/depot/ {
        auth_request /_auth;
        alias /srv/prometheus/depot/;
        dav_methods PUT;
        dav_access user:rw group:r all:r;
        client_max_body_size 0;
        client_body_temp_path /srv/prometheus/.envoi;
        client_body_timeout 1h;
        limit_except PUT { deny all; }
    }
}
EOF
ln -sf /etc/nginx/sites-available/prometheus /etc/nginx/sites-enabled/prometheus
rm -f /etc/nginx/sites-enabled/default
nginx -t

echo "== Wifi ouvert 'Prometheus-Station' qui s'allume tout seul a chaque demarrage"
# (si le script est relance, on ne touche pas au wifi deja cree)
nmcli -t -f NAME connection show | grep -qx prometheus-wifi || \
nmcli connection add type wifi ifname wlan0 con-name prometheus-wifi autoconnect yes \
  ssid Prometheus-Station \
  802-11-wireless.mode ap 802-11-wireless.band bg 802-11-wireless.channel 6 \
  802-11-wireless.powersave 2 \
  ipv4.method shared ipv4.addresses 10.42.0.1/24 ipv6.method disabled

echo "== Portail : toute adresse demandee par un telephone connecte mene a la station"
mkdir -p /etc/NetworkManager/dnsmasq-shared.d
cat > /etc/NetworkManager/dnsmasq-shared.d/prometheus.conf <<'EOF'
address=/#/10.42.0.1
EOF

systemctl daemon-reload
systemctl enable --now prometheus-ranger.path prometheus-commande.path
systemctl enable --now prometheus-admin.service
systemctl restart prometheus-admin.service
systemctl enable nginx
systemctl restart nginx
[ "$(nmcli -g connection.autoconnect connection show prometheus-wifi)" = yes ] && nmcli connection up prometheus-wifi

echo "== Etape 3 terminee. Ouvrir http://<station>/ajouter/ pour choisir le mot de passe."
