#!/bin/bash
# Prometheus Station - etape 4 : Tailscale (depanner la station a distance quand elle a internet)
# A lancer sur le Pi : sudo bash 04-tailscale.sh
# Necessite un compte Tailscale gratuit : https://login.tailscale.com
set -euo pipefail

echo "== Installation de Tailscale (script officiel)"
curl -fsSL https://tailscale.com/install.sh | sh

echo "== Connexion : ouvrez le lien qui s'affiche et connectez-vous a votre compte Tailscale"
tailscale up --ssh=false --hostname=prometheus-station

echo "== Etape 4 terminee. Adresse Tailscale :"
tailscale ip -4
