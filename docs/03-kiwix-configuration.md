# Step 3: Essential Kiwix Configuration

**Goal:** Transform Kiwix from a basic server into a polished, field-ready knowledge station.

**Time Required:** 1-2 hours  
**Difficulty:** ⭐⭐⭐ Medium (HTML/CSS editing, but we explain everything)

**💡 Real experience:** This step transforms the experience from "technical tool" to "professional deployment." Don't skip it!

---

## 📋 What You'll Need

### Prerequisites
- [ ] ✅ Completed [Step 1 - Raspberry Pi Setup](01-raspberry-setup.md)
- [ ] ✅ Completed [Step 2 - Kiwix Installation](02-kiwix-installation.md)
- [ ] SSH access to your Pi
- [ ] Kiwix server running with ZIM files

### Skills
- Basic HTML/CSS understanding (we'll teach you)
- Text editor navigation (nano)
- File management via command line

---

## 🎯 Overview

We'll accomplish:
1. ✅ Verify auto-start configuration
2. ✅ Create custom landing page with big buttons
3. ✅ Add branding (logo in base64)
4. ✅ Configure Apache as reverse proxy
5. ✅ Create connection instructions (printable)
6. ✅ Add offline mode indicators
7. ✅ Setup maintenance scripts
8. ✅ Optimize for field conditions

---

## 🧠 The Big Picture: Why This Matters

**Without this configuration:**
```
User connects to WiFi
  → Types "prometheus-station.local"
    → Sees raw Kiwix interface (confusing)
      → Doesn't know which content to click
        → Gives up or asks for help
```

**With this configuration:**
```
User connects to WiFi
  → Types "prometheus-station.local"
    → Sees beautiful landing page
      → Big buttons: "DISASTER MEDICINE" / "WIKIPEDIA"
        → Clicks, immediately finds what they need
          → Uses offline knowledge successfully! 🎉
```

**Field reality:** In disaster zones or remote areas:
- Users may have low tech literacy
- Devices may be old (slow JavaScript)
- Time is critical (no time for confusion)
- Multiple languages may be needed

**This configuration makes Prometheus Station accessible to everyone.**

---

## Step 1: Verify Auto-Start Configuration (10 minutes)

### Check Kiwix Service Status

```bash
# Connect to Pi
ssh prometheus

# Check if Kiwix service is enabled
systemctl is-enabled kiwix-serve
```

**Expected output:** `enabled`

If it shows `disabled`:
```bash
sudo systemctl enable kiwix-serve
```

---

### Check Service Health

```bash
# Detailed status
sudo systemctl status kiwix-serve
```

**Look for:**
```
● kiwix-serve.service - Kiwix Server - Offline Knowledge Hub
   Loaded: loaded (/etc/systemd/system/kiwix-serve.service; enabled; ✓)
   Active: active (running) since Thu 2025-12-26 14:30:15 CET; 2h 15min ago
```

**Key indicators:**
- ✅ `enabled` in Loaded line
- ✅ `active (running)` in Active line
- ✅ Uptime showing (not constantly restarting)

---

### Test Auto-Start

**The ultimate test - reboot:**

```bash
# Reboot Pi
sudo reboot

# Wait 60 seconds...

# SSH back in
ssh prometheus

# Check if Kiwix started automatically
sudo systemctl status kiwix-serve
```

**Expected:** Active (running) with recent start time.

**If Kiwix didn't start:** See Troubleshooting section.

---

### Check Logs for Boot Issues

```bash
# View boot logs for Kiwix
sudo journalctl -u kiwix-serve -b
```

**What `-b` means:** Show logs from current boot only.

**Look for:**
- ✅ "Listening on port 80"
- ❌ Any ERROR or FAILED messages

**Common boot issues:**
1. Port 80 already in use
2. ZIM files missing/moved
3. Library.xml corrupted
4. Permission issues

---

## Step 2: Install Apache Web Server (15 minutes)

**Why Apache?** We'll use it to:
- Serve our custom landing page
- Reverse proxy to Kiwix (cleaner URLs)
- Handle multiple services elegantly

### Install Apache

```bash
sudo apt update
sudo apt install -y apache2
```

**Installation takes:** ~2 minutes

---

### Enable Required Modules

```bash
# Enable proxy modules (for reverse proxy)
sudo a2enmod proxy
sudo a2enmod proxy_http
sudo a2enmod rewrite

# Restart Apache
sudo systemctl restart apache2
```

**What these modules do:**
- `proxy` - Core proxy functionality
- `proxy_http` - HTTP-specific proxying
- `rewrite` - URL rewriting (clean URLs)

---

### Configure Firewall

**Apache needs port 80, but Kiwix is already using it!**

**Solution:** Move Kiwix to different port, Apache on 80.

**Edit Kiwix service:**
```bash
sudo nano /etc/systemd/system/kiwix-serve.service
```

**Change the ExecStart line:**
```ini
# OLD:
ExecStart=/usr/local/bin/kiwix-serve --port=80 ...

# NEW:
ExecStart=/usr/local/bin/kiwix-serve --port=8080 ...
```

**Full section should look like:**
```ini
ExecStart=/usr/local/bin/kiwix-serve \
    --port=8080 \
    --library=/var/kiwix/library/library.xml \
    --nodatealiases
```

**Save:** Ctrl+X, Y, Enter

**Reload and restart Kiwix:**
```bash
sudo systemctl daemon-reload
sudo systemctl restart kiwix-serve
```

**Verify Kiwix on new port:**
```bash
curl http://localhost:8080
```

Should return HTML content.

---

### Test Apache

```bash
# Should now be running on port 80
curl http://localhost
```

**Expected output:** Apache default page HTML.

**From your laptop browser:**
```
http://prometheus-station.local
```

Should show Apache welcome page.

---

## Step 3: Create Custom Landing Page (30 minutes)

### Design Philosophy

**Field requirements:**
- ✅ Works on old devices (minimal JavaScript)
- ✅ High contrast (readable in sunlight)
- ✅ Touch-friendly (thick fingers, not precise mouse)
- ✅ Fast loading (low bandwidth)
- ✅ Multiple languages
- ✅ Clear offline indicators

---

### Create Web Directory

```bash
# Apache serves from /var/www/html by default
cd /var/www/html

# Backup default page
sudo mv index.html index.html.backup

# Create our custom page
sudo nano index.html
```

---

### Landing Page HTML

**Paste this content:**

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=yes">
    <title>🔥 Prometheus Station - Offline Knowledge Hub</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif;
            background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
            color: #f0f0f0;
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        
        /* Header */
        .header {
            text-align: center;
            margin-bottom: 40px;
            padding: 30px 20px;
            background: rgba(255, 107, 53, 0.1);
            border-radius: 15px;
            border: 2px solid #ff6b35;
        }
        
        .logo {
            width: 120px;
            height: 120px;
            margin: 0 auto 20px;
            display: block;
        }
        
        h1 {
            font-size: 3em;
            color: #ff6b35;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        }
        
        .tagline {
            font-size: 1.3em;
            color: #4ecdc4;
            font-style: italic;
            margin-bottom: 20px;
        }
        
        .offline-badge {
            display: inline-block;
            background: #27ae60;
            color: white;
            padding: 10px 25px;
            border-radius: 25px;
            font-weight: bold;
            font-size: 1.1em;
            margin-top: 15px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        }
        
        .offline-badge::before {
            content: "✓ ";
            font-size: 1.3em;
        }
        
        /* Content Grid */
        .content-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 25px;
            margin-bottom: 40px;
        }
        
        .content-card {
            background: #2a2a2a;
            border-radius: 12px;
            padding: 30px;
            border-left: 6px solid #ff6b35;
            transition: transform 0.2s, box-shadow 0.2s;
            cursor: pointer;
            text-decoration: none;
            color: inherit;
            display: block;
        }
        
        .content-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(255, 107, 53, 0.3);
            border-left-color: #4ecdc4;
        }
        
        .content-card h2 {
            color: #ff6b35;
            font-size: 1.8em;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 12px;
        }
        
        .content-card .icon {
            font-size: 1.5em;
        }
        
        .content-card .description {
            color: #b0b0b0;
            line-height: 1.6;
            margin-bottom: 15px;
            font-size: 1.05em;
        }
        
        .content-card .size {
            color: #4ecdc4;
            font-size: 0.9em;
            font-weight: bold;
        }
        
        .content-card .button {
            display: inline-block;
            background: #ff6b35;
            color: white;
            padding: 15px 35px;
            border-radius: 8px;
            text-decoration: none;
            font-weight: bold;
            margin-top: 15px;
            font-size: 1.1em;
            text-align: center;
            transition: background 0.2s;
            width: 100%;
        }
        
        .content-card .button:hover {
            background: #e55a2b;
        }
        
        /* Info Section */
        .info-section {
            background: rgba(78, 205, 196, 0.1);
            border: 2px solid #4ecdc4;
            border-radius: 12px;
            padding: 25px;
            margin-bottom: 30px;
        }
        
        .info-section h3 {
            color: #4ecdc4;
            font-size: 1.6em;
            margin-bottom: 15px;
        }
        
        .info-section ul {
            list-style: none;
            padding: 0;
        }
        
        .info-section li {
            padding: 10px 0;
            border-bottom: 1px solid rgba(78, 205, 196, 0.2);
            font-size: 1.1em;
        }
        
        .info-section li:last-child {
            border-bottom: none;
        }
        
        .info-section li::before {
            content: "→ ";
            color: #4ecdc4;
            font-weight: bold;
            margin-right: 10px;
        }
        
        /* Footer */
        .footer {
            text-align: center;
            padding: 30px;
            border-top: 2px solid rgba(255, 107, 53, 0.3);
            margin-top: 40px;
            color: #888;
        }
        
        .footer a {
            color: #4ecdc4;
            text-decoration: none;
        }
        
        .footer a:hover {
            text-decoration: underline;
        }
        
        /* Responsive Design */
        @media (max-width: 768px) {
            h1 {
                font-size: 2em;
            }
            
            .tagline {
                font-size: 1em;
            }
            
            .content-card {
                padding: 20px;
            }
            
            .content-card h2 {
                font-size: 1.4em;
            }
            
            .content-grid {
                grid-template-columns: 1fr;
            }
        }
        
        /* Print Styles */
        @media print {
            body {
                background: white;
                color: black;
            }
            
            .content-card {
                break-inside: avoid;
                border: 2px solid #000;
            }
            
            .button {
                display: none;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <!-- Logo will go here (we'll add it in next step) -->
            <h1>🔥 PROMETHEUS STATION</h1>
            <p class="tagline">Bringing Fire to Humanity, One Station at a Time</p>
            <div class="offline-badge">WORKS OFFLINE - NO INTERNET NEEDED</div>
        </div>
        
        <!-- Content Cards -->
        <div class="content-grid">
            <!-- This section will be auto-generated from ZIM files -->
            <!-- For now, we'll add placeholders manually -->
            
            <!-- Card 1: Disaster Medicine -->
            <a href="/kiwix/post-disaster" class="content-card">
                <h2><span class="icon">🚑</span>Disaster Medicine</h2>
                <p class="description">WHO field protocols for mass casualties, emergency response, and disaster medical management. Essential for field teams.</p>
                <p class="size">📦 Size: 615 MB</p>
                <div class="button">OPEN DISASTER PROTOCOLS →</div>
            </a>
            
            <!-- Card 2: Emergency Medicine -->
            <a href="/kiwix/wikem" class="content-card">
                <h2><span class="icon">⚕️</span>Emergency Medicine</h2>
                <p class="description">ER procedures, trauma care, toxicology, and emergency protocols. Complete clinical reference for urgent care.</p>
                <p class="size">📦 Size: 42 MB</p>
                <div class="button">OPEN ER PROTOCOLS →</div>
            </a>
            
            <!-- Card 3: Medical Encyclopedia -->
            <a href="/kiwix/mdwiki" class="content-card">
                <h2><span class="icon">📚</span>Medical Encyclopedia</h2>
                <p class="description">Comprehensive medical reference covering diseases, treatments, procedures, and pharmacology. Updated monthly.</p>
                <p class="size">📦 Size: 2.1 GB</p>
                <div class="button">OPEN MEDICAL REFERENCE →</div>
            </a>
            
            <!-- Card 4: Wikipedia Medicine EN -->
            <a href="/kiwix/wikipedia_en_medicine" class="content-card">
                <h2><span class="icon">🌍</span>Wikipedia Medicine (EN)</h2>
                <p class="description">Medical articles from English Wikipedia. Diseases, anatomy, medical history, and health information.</p>
                <p class="size">📦 Size: 1.9 GB</p>
                <div class="button">OPEN WIKIPEDIA MEDICINE →</div>
            </a>
            
            <!-- Card 5: Wikipedia Medicine FR -->
            <a href="/kiwix/wikipedia_fr_medicine" class="content-card">
                <h2><span class="icon">🇫🇷</span>Wikipédia Médecine (FR)</h2>
                <p class="description">Articles médicaux de Wikipédia en français. Maladies, anatomie, histoire de la médecine et informations santé.</p>
                <p class="size">📦 Size: 1.1 GB</p>
                <div class="button">OUVRIR MÉDECINE →</div>
            </a>
            
            <!-- Card 6: Water Safety -->
            <a href="/kiwix/water" class="content-card">
                <h2><span class="icon">💧</span>Water Purification</h2>
                <p class="description">Water safety protocols, purification methods, and quality testing. Critical for field operations.</p>
                <p class="size">📦 Size: 20 MB</p>
                <div class="button">OPEN WATER GUIDES →</div>
            </a>
            
            <!-- Card 7: Food Safety -->
            <a href="/kiwix/food-prep" class="content-card">
                <h2><span class="icon">🍽️</span>Food Safety</h2>
                <p class="description">Food preparation, storage, and safety protocols. Prevent foodborne illness in field conditions.</p>
                <p class="size">📦 Size: 93 MB</p>
                <div class="button">OPEN FOOD GUIDES →</div>
            </a>
        </div>
        
        <!-- Info Section -->
        <div class="info-section">
            <h3>ℹ️ How to Use This Station</h3>
            <ul>
                <li><strong>No Internet Required:</strong> All content works completely offline</li>
                <li><strong>Search:</strong> Click any content above, then use search within</li>
                <li><strong>Languages:</strong> Content available in English and French</li>
                <li><strong>Mobile Friendly:</strong> Works on phones, tablets, and computers</li>
                <li><strong>Free & Open:</strong> All content is freely accessible</li>
                <li><strong>Updated:</strong> Content refreshed monthly from official sources</li>
            </ul>
        </div>
        
        <!-- System Info -->
        <div class="info-section">
            <h3>🔧 System Information</h3>
            <ul>
                <li><strong>Station Name:</strong> prometheus-station</li>
                <li><strong>Network:</strong> Prometheus-Station WiFi</li>
                <li><strong>Access URL:</strong> http://prometheus-station.local</li>
                <li><strong>Backup IP:</strong> http://192.168.42.1</li>
                <li><strong>Total Content:</strong> ~5.5 GB (7 knowledge bases)</li>
                <li><strong>Last Updated:</strong> December 2025</li>
            </ul>
        </div>
        
        <!-- Footer -->
        <div class="footer">
            <p>Prometheus Station v1.0 | Powered by <a href="https://www.kiwix.org" target="_blank">Kiwix</a></p>
            <p><a href="https://github.com/GuillainM/Prometheus-Station" target="_blank">GitHub Repository</a> | MIT License</p>
            <p><small>Made with 🔥 and ☕ somewhere between "I have no idea what I'm doing" and "Wait, that actually worked!"</small></p>
        </div>
    </div>
</body>
</html>
```

**Save:** Ctrl+X, Y, Enter

---

### Test Landing Page

**From your laptop browser:**
```
http://prometheus-station.local
```

**You should see:** Beautiful landing page with content cards!

**What to check:**
- ✅ Page loads quickly (<2 seconds)
- ✅ All text readable
- ✅ Cards displayed properly
- ✅ Responsive on mobile (try resizing browser)
- ✅ Color scheme visible in sunlight (if testing outdoors)

---

## Step 4: Add Logo/Branding (20 minutes)

### Why Base64?

**Problem:** Logo image needs to load offline.

**Solutions:**
1. ❌ Link to external URL: Requires internet
2. ❌ Local file reference: Need to manage files
3. ✅ **Base64 encode into HTML:** Self-contained, works offline

**Trade-off:** Larger HTML file, but guaranteed to work.

---

### Create or Find Logo

**Option 1: Use existing image**

If you have a logo file (PNG/JPG):

```bash
# Copy to Pi
scp /path/to/logo.png prometheus@prometheus-station.local:/home/prometheus/

# SSH to Pi
ssh prometheus
```

**Option 2: Create simple text logo**

Skip to next section - we'll create CSS-based logo.

---

### Convert Image to Base64

**On Pi:**

```bash
# Install base64 tool (usually pre-installed)
which base64

# Convert image
base64 -w 0 ~/logo.png > ~/logo-base64.txt

# View result
cat ~/logo-base64.txt
```

**Output:** Long string of characters.

**Example:**
```
iVBORw0KGgoAAAANSUhEUgAAASwAAAEsCAYAAAB5fY51AAAACXBIWXMAAA...
```

**Copy this entire string.** We'll use it next.

---

### Add Logo to Landing Page

```bash
sudo nano /var/www/html/index.html
```

**Find the logo placeholder:**
```html
<!-- Logo will go here (we'll add it in next step) -->
```

**Replace with:**
```html
<img src="data:image/png;base64,YOUR_BASE64_STRING_HERE" 
     alt="Prometheus Station Logo" 
     class="logo">
```

**Replace `YOUR_BASE64_STRING_HERE` with the base64 string you copied.**

**Full example:**
```html
<img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAASwAAAEsCAYAAAB5fY51AAAACXBIWXMAAA..." 
     alt="Prometheus Station Logo" 
     class="logo">
```

**Save:** Ctrl+X, Y, Enter

---

### Alternative: CSS-Based Logo (No Image Needed)

If you don't have a logo, use CSS to create one:

**Find this section in HTML:**
```html
<!-- Logo will go here (we'll add it in next step) -->
```

**Replace with:**
```html
<div class="logo-css">
    <div class="flame">🔥</div>
    <div class="station-text">STATION</div>
</div>
```

**Add CSS to `<style>` section:**
```css
.logo-css {
    width: 150px;
    height: 150px;
    margin: 0 auto 20px;
    position: relative;
    text-align: center;
}

.logo-css .flame {
    font-size: 80px;
    animation: flicker 2s infinite;
}

.logo-css .station-text {
    font-size: 14px;
    font-weight: bold;
    color: #4ecdc4;
    letter-spacing: 3px;
    margin-top: -10px;
}

@keyframes flicker {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.8; transform: scale(1.05); }
}
```

**Result:** Animated flame emoji with "STATION" text below.

---

### Test Logo

**Refresh browser:**
```
http://prometheus-station.local
```

**You should see:** Logo in header (image or CSS flame).

---

## Step 5: Configure Apache Reverse Proxy (20 minutes)

**Goal:** Make content URLs cleaner.

**Current (ugly):**
```
http://prometheus-station.local:8080/content/post-disaster/A/Trauma
```

**After (clean):**
```
http://prometheus-station.local/kiwix/post-disaster/A/Trauma
```

---

### Create Apache Configuration

```bash
# Create new site config
sudo nano /etc/apache2/sites-available/prometheus.conf
```

**Add this configuration:**
```apache
<VirtualHost *:80>
    ServerName prometheus-station.local
    ServerAlias prometheus-station
    
    DocumentRoot /var/www/html
    
    # Logging
    ErrorLog ${APACHE_LOG_DIR}/prometheus-error.log
    CustomLog ${APACHE_LOG_DIR}/prometheus-access.log combined
    
    # Main landing page
    <Directory /var/www/html>
        Options -Indexes +FollowSymLinks
        AllowOverride All
        Require all granted
    </Directory>
    
    # Reverse proxy to Kiwix
    ProxyPreserveHost On
    ProxyPass /kiwix http://localhost:8080
    ProxyPassReverse /kiwix http://localhost:8080
    
    # Optional: Redirect /search to Kiwix search
    RewriteEngine On
    RewriteRule ^/search(.*)$ /kiwix/search$1 [P,L]
</VirtualHost>
```

**Save:** Ctrl+X, Y, Enter

---

### Enable Site and Disable Default

```bash
# Disable default Apache site
sudo a2dissite 000-default

# Enable Prometheus site
sudo a2ensite prometheus

# Test configuration
sudo apache2ctl configtest
```

**Expected output:** `Syntax OK`

**If you see warnings:** Note them, but `Syntax OK` means safe to proceed.

**Restart Apache:**
```bash
sudo systemctl restart apache2
```

---

### Update Landing Page Links

**Edit landing page:**
```bash
sudo nano /var/www/html/index.html
```

**Find content card links, for example:**
```html
<a href="/kiwix/post-disaster" class="content-card">
```

**These need to match your actual ZIM file names in Kiwix.**

**To find correct paths:**
```bash
# On Pi, check what Kiwix is serving
curl http://localhost:8080/catalog/v2/entries
```

**Look for `name` fields in output:**
```json
{
  "name": "zimgit-post-disaster_en_2024-05",
  "title": "Post-Disaster Medical Protocols",
  ...
}
```

**Update href to:**
```html
<a href="/kiwix/zimgit-post-disaster_en_2024-05" class="content-card">
```

**Repeat for each content card.**

**Common ZIM URL patterns:**
- Disaster Medicine: `/kiwix/zimgit-post-disaster_en_2024-05`
- Emergency Med: `/kiwix/wikem_en_all_maxi_2021-02`
- Medical Encyclopedia: `/kiwix/mdwiki_en_all_maxi_2025-11`
- Wikipedia Medicine EN: `/kiwix/wikipedia_en_medicine_maxi_2025-09`
- Wikipedia Medicine FR: `/kiwix/wikipedia_fr_medicine_maxi_2025-09`
- Water: `/kiwix/zimgit-water_en_2024-08`
- Food: `/kiwix/zimgit-food-preparation_en_2025-04`

**Save:** Ctrl+X, Y, Enter

---

### Test Reverse Proxy

**From browser:**
```
http://prometheus-station.local/kiwix/
```

**Should show:** Kiwix content library.

**Click on a content card** from landing page.

**Should:** Open that ZIM file directly.

---

## Step 6: Create Auto-Update Script (15 minutes)

**Problem:** When you add new ZIM files, you need to:
1. Update library.xml
2. Update landing page HTML
3. Restart Kiwix

**Solution:** Automate it!

---

### Create Update Script

```bash
nano ~/update-prometheus-content.sh
```

**Add this script:**
```bash
#!/bin/bash
# Prometheus Station - Content Update Script
# Updates Kiwix library and regenerates landing page

set -e  # Exit on error

echo "======================================"
echo " PROMETHEUS STATION - Content Update"
echo "======================================"
echo ""

# Configuration
ZIM_DIR="/var/kiwix/data"
LIBRARY_FILE="/var/kiwix/library/library.xml"
WEB_DIR="/var/www/html"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Step 1: Backup existing library
echo -e "${YELLOW}[1/5] Backing up library...${NC}"
if [ -f "$LIBRARY_FILE" ]; then
    cp "$LIBRARY_FILE" "$LIBRARY_FILE.backup-$(date +%Y%m%d-%H%M%S)"
    echo -e "${GREEN}✓ Library backed up${NC}"
else
    echo -e "${YELLOW}! No existing library found, will create new${NC}"
fi

# Step 2: Rebuild Kiwix library
echo -e "${YELLOW}[2/5] Scanning ZIM files...${NC}"
ZIM_COUNT=$(ls -1 "$ZIM_DIR"/*.zim 2>/dev/null | wc -l)
if [ "$ZIM_COUNT" -eq 0 ]; then
    echo -e "${RED}✗ No ZIM files found in $ZIM_DIR${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Found $ZIM_COUNT ZIM files${NC}"

echo -e "${YELLOW}[3/5] Rebuilding library...${NC}"
# Remove all entries
kiwix-manage "$LIBRARY_FILE" remove "*" 2>/dev/null || true
# Add all ZIM files
kiwix-manage "$LIBRARY_FILE" add "$ZIM_DIR"/*.zim
echo -e "${GREEN}✓ Library updated${NC}"

# Step 3: Get ZIM file information
echo -e "${YELLOW}[4/5] Generating content cards...${NC}"

# Create temporary file for cards
CARDS_HTML="/tmp/prometheus-cards.html"
> "$CARDS_HTML"  # Clear file

# Parse library.xml and generate cards
# This is a simplified version - you may need to adjust based on your XML structure

# For each ZIM file, create a card
for ZIM_FILE in "$ZIM_DIR"/*.zim; do
    if [ ! -f "$ZIM_FILE" ]; then
        continue
    fi
    
    # Extract filename without path and extension
    BASENAME=$(basename "$ZIM_FILE" .zim)
    
    # Get file size in human-readable format
    SIZE=$(du -h "$ZIM_FILE" | cut -f1)
    
    # Determine icon and title based on filename
    ICON="📚"
    TITLE="$BASENAME"
    DESC="Content from ${BASENAME}"
    
    # Custom mapping for known content
    case "$BASENAME" in
        *"post-disaster"*)
            ICON="🚑"
            TITLE="Disaster Medicine"
            DESC="WHO field protocols for mass casualties and disaster medical management"
            ;;
        *"wikem"*)
            ICON="⚕️"
            TITLE="Emergency Medicine"
            DESC="ER procedures, trauma care, and emergency protocols"
            ;;
        *"mdwiki"*)
            ICON="📚"
            TITLE="Medical Encyclopedia"
            DESC="Comprehensive medical reference - diseases, treatments, pharmacology"
            ;;
        *"wikipedia_en_medicine"*)
            ICON="🌍"
            TITLE="Wikipedia Medicine (EN)"
            DESC="Medical articles from English Wikipedia"
            ;;
        *"wikipedia_fr_medicine"*)
            ICON="🇫🇷"
            TITLE="Wikipédia Médecine (FR)"
            DESC="Articles médicaux de Wikipédia en français"
            ;;
        *"water"*)
            ICON="💧"
            TITLE="Water Purification"
            DESC="Water safety protocols and purification methods"
            ;;
        *"food"*)
            ICON="🍽️"
            TITLE="Food Safety"
            DESC="Food preparation and safety protocols"
            ;;
    esac
    
    # Generate card HTML
    cat >> "$CARDS_HTML" << EOF
            <a href="/kiwix/${BASENAME}" class="content-card">
                <h2><span class="icon">${ICON}</span>${TITLE}</h2>
                <p class="description">${DESC}</p>
                <p class="size">📦 Size: ${SIZE}</p>
                <div class="button">OPEN ${TITLE^^} →</div>
            </a>

EOF
done

echo -e "${GREEN}✓ Content cards generated${NC}"

# Step 4: Update landing page
echo -e "${YELLOW}[5/5] Updating landing page...${NC}"

# This would replace the content-grid section
# For safety, we'll just notify user to manually update
echo -e "${YELLOW}! Generated content cards saved to: $CARDS_HTML${NC}"
echo -e "${YELLOW}! Please manually copy cards to $WEB_DIR/index.html${NC}"
echo ""
echo "Or run: sudo cp $CARDS_HTML $WEB_DIR/cards-generated.html"

# Step 5: Restart Kiwix
echo -e "${YELLOW}Restarting Kiwix service...${NC}"
sudo systemctl restart kiwix-serve
sleep 2

if systemctl is-active --quiet kiwix-serve; then
    echo -e "${GREEN}✓ Kiwix restarted successfully${NC}"
else
    echo -e "${RED}✗ Kiwix failed to restart${NC}"
    sudo systemctl status kiwix-serve
    exit 1
fi

echo ""
echo -e "${GREEN}======================================"
echo " ✓ Update Complete!"
echo "======================================${NC}"
echo ""
echo "Summary:"
echo "  - ZIM files scanned: $ZIM_COUNT"
echo "  - Library updated: $LIBRARY_FILE"
echo "  - Cards generated: $CARDS_HTML"
echo "  - Kiwix restarted: OK"
echo ""
echo "Access station at: http://prometheus-station.local"
echo ""
```

**Save:** Ctrl+X, Y, Enter

---

### Make Script Executable

```bash
chmod +x ~/update-prometheus-content.sh
```

---

### Test Update Script

```bash
./update-prometheus-content.sh
```

**Expected output:**
```
======================================
 PROMETHEUS STATION - Content Update
======================================

[1/5] Backing up library...
✓ Library backed up
[2/5] Scanning ZIM files...
✓ Found 7 ZIM files
[3/5] Rebuilding library...
✓ Library updated
[4/5] Generating content cards...
✓ Content cards generated
[5/5] Updating landing page...
! Generated content cards saved to: /tmp/prometheus-cards.html
Restarting Kiwix service...
✓ Kiwix restarted successfully

======================================
 ✓ Update Complete!
======================================

Summary:
  - ZIM files scanned: 7
  - Library updated: /var/kiwix/library/library.xml
  - Cards generated: /tmp/prometheus-cards.html
  - Kiwix restarted: OK

Access station at: http://prometheus-station.local
```

---

### Use Generated Cards

```bash
# View generated cards
cat /tmp/prometheus-cards.html

# Manually copy to landing page
sudo nano /var/www/html/index.html
```

**Find:**
```html
<div class="content-grid">
    <!-- Existing cards here -->
</div>
```

**Replace content between `<div class="content-grid">` and `</div>` with cards from `/tmp/prometheus-cards.html`**

---

## Step 7: Create Printable Connection Instructions (15 minutes)

**Why?** Users need simple, printable instructions to connect.

---

### Create Instructions Page

```bash
sudo nano /var/www/html/connect.html
```

**Add this content:**
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>How to Connect - Prometheus Station</title>
    <style>
        @page {
            margin: 2cm;
        }
        
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.6;
        }
        
        .header {
            text-align: center;
            border-bottom: 4px solid #ff6b35;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }
        
        h1 {
            color: #ff6b35;
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .step {
            background: #f5f5f5;
            padding: 20px;
            margin: 20px 0;
            border-left: 6px solid #4ecdc4;
            break-inside: avoid;
        }
        
        .step h2 {
            color: #4ecdc4;
            margin-top: 0;
        }
        
        .highlight {
            background: #ffffcc;
            padding: 2px 6px;
            font-weight: bold;
            border-radius: 3px;
        }
        
        .important {
            background: #ffe0e0;
            border: 2px solid #ff6b35;
            padding: 15px;
            margin: 20px 0;
            border-radius: 5px;
        }
        
        .qr-placeholder {
            width: 200px;
            height: 200px;
            border: 3px dashed #4ecdc4;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 20px auto;
            font-weight: bold;
            color: #4ecdc4;
        }
        
        @media print {
            body {
                font-size: 12pt;
            }
            
            .no-print {
                display: none;
            }
            
            .step {
                page-break-inside: avoid;
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🔥 PROMETHEUS STATION</h1>
        <h2>Quick Connect Guide</h2>
        <p><strong>Offline Knowledge Hub - No Internet Required</strong></p>
    </div>
    
    <div class="important">
        <h3>⚡ QUICK START (3 Steps)</h3>
        <ol>
            <li>Connect to WiFi: <span class="highlight">Prometheus-Station</span></li>
            <li>Password: <span class="highlight">Knowledge2025</span></li>
            <li>Open browser: <span class="highlight">http://prometheus-station.local</span></li>
        </ol>
    </div>
    
    <div class="step">
        <h2>Step 1: Connect to WiFi Network</h2>
        <p>On your device (phone, tablet, or computer):</p>
        <ol>
            <li>Open WiFi settings</li>
            <li>Look for network named: <span class="highlight">Prometheus-Station</span></li>
            <li>Click/tap to connect</li>
            <li>Enter password: <span class="highlight">Knowledge2025</span></li>
            <li>Wait for "Connected" confirmation</li>
        </ol>
        <p><strong>Note:</strong> You may see a warning "No Internet Access" - this is normal! The station works offline.</p>
    </div>
    
    <div class="step">
        <h2>Step 2: Open Web Browser</h2>
        <p>Use any web browser:</p>
        <ul>
            <li>Chrome, Firefox, Safari, Edge - all work!</li>
            <li>Works on phones, tablets, laptops, desktop computers</li>
        </ul>
    </div>
    
    <div class="step">
        <h2>Step 3: Navigate to Station</h2>
        <p>In the browser address bar, type:</p>
        <p style="text-align: center; font-size: 1.5em; background: #e8f4f8; padding: 15px; border-radius: 5px;">
            <strong>http://prometheus-station.local</strong>
        </p>
        <p><strong>Backup option:</strong> If the above doesn't work, try:</p>
        <p style="text-align: center; font-size: 1.3em;">
            <strong>http://192.168.42.1</strong>
        </p>
        <p>You should see the Prometheus Station welcome page with content options!</p>
    </div>
    
    <div class="step">
        <h2>Available Content</h2>
        <ul>
            <li><strong>🚑 Disaster Medicine:</strong> WHO emergency protocols</li>
            <li><strong>⚕️ Emergency Medicine:</strong> ER procedures and trauma care</li>
            <li><strong>📚 Medical Encyclopedia:</strong> Complete medical reference</li>
            <li><strong>🌍 Wikipedia Medicine:</strong> English & French medical articles</li>
            <li><strong>💧 Water Purification:</strong> Safe water protocols</li>
            <li><strong>🍽️ Food Safety:</strong> Food preparation guides</li>
        </ul>
        <p><strong>Total Content: ~5.5 GB</strong> - All works completely offline!</p>
    </div>
    
    <div class="step">
        <h2>📱 QR Code (Print & Share)</h2>
        <div class="qr-placeholder">
            [QR Code Here]<br>
            Generate at:<br>
            qr-code-generator.com
        </div>
        <p style="text-align: center;">
            <small>Scan to connect automatically (on supported devices)</small>
        </p>
    </div>
    
    <div class="step">
        <h2>❓ Troubleshooting</h2>
        <p><strong>Problem:</strong> Can't see Prometheus-Station WiFi</p>
        <p><strong>Solution:</strong> Check station is powered on, wait 60 seconds after boot</p>
        
        <p><strong>Problem:</strong> Website won't load</p>
        <p><strong>Solutions:</strong></p>
        <ul>
            <li>Verify you're connected to Prometheus-Station WiFi</li>
            <li>Try backup IP: 192.168.42.1</li>
            <li>Clear browser cache and retry</li>
            <li>Try different browser</li>
        </ul>
        
        <p><strong>Problem:</strong> Slow loading</p>
        <p><strong>Solution:</strong> Too many users connected, wait a moment or try again</p>
    </div>
    
    <div class="important">
        <h3>🔒 Security Note</h3>
        <p>This is a <strong>local network only</strong> - your data does not leave this WiFi network. No internet connection means no tracking, no data collection.</p>
    </div>
    
    <hr>
    
    <div style="text-align: center; margin-top: 30px; color: #888;">
        <p><strong>Prometheus Station</strong> - Bringing Fire to Humanity, One Station at a Time</p>
        <p class="no-print">
            <a href="/">← Back to Station</a> | 
            <a href="javascript:window.print()">🖨️ Print These Instructions</a>
        </p>
        <p><small>Open Source Project | MIT License | <a href="https://github.com/GuillainM/Prometheus-Station">GitHub</a></small></p>
    </div>
</body>
</html>
```

**Save:** Ctrl+X, Y, Enter

---

### Add Link from Landing Page

```bash
sudo nano /var/www/html/index.html
```

**Find the info section:**
```html
<div class="info-section">
    <h3>ℹ️ How to Use This Station</h3>
```

**Add at the top of this section:**
```html
<p style="text-align: center; margin-bottom: 20px;">
    <a href="/connect.html" 
       style="display: inline-block; background: #4ecdc4; color: white; padding: 15px 30px; border-radius: 8px; text-decoration: none; font-weight: bold;">
        📋 VIEW CONNECTION INSTRUCTIONS
    </a>
</p>
```

---

### Generate QR Code

**Option 1: Online generator (easiest)**

1. Go to: https://www.qr-code-generator.com/
2. Select "WiFi" type
3. Enter:
   - Network: `Prometheus-Station`
   - Password: `Knowledge2025`
   - Security: WPA/WPA2
4. Download QR code image
5. Convert to base64 (like we did for logo)
6. Add to connect.html

**Option 2: Generate on Pi**

```bash
# Install qrencode
sudo apt install -y qrencode

# Generate QR code for WiFi
qrencode -t PNG -o ~/wifi-qr.png \
  "WIFI:S:Prometheus-Station;T:WPA;P:Knowledge2025;;"

# View file
ls -lh ~/wifi-qr.png
```

Then convert to base64 and add to HTML.

---

### Test Instructions Page

**From browser:**
```
http://prometheus-station.local/connect.html
```

**Try printing:** File → Print → Verify layout looks good

---

## Step 8: Add System Health Monitoring (20 minutes)

**Create health check page** for troubleshooting.

---

### Install PHP (for dynamic content)

```bash
sudo apt install -y php libapache2-mod-php php-cli
```

**Restart Apache:**
```bash
sudo systemctl restart apache2
```

---

### Create Health Status Page

```bash
sudo nano /var/www/html/status.php
```

**Add this content:**
```php
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>System Status - Prometheus Station</title>
    <meta http-equiv="refresh" content="30">
    <style>
        body {
            font-family: 'Courier New', monospace;
            background: #1a1a1a;
            color: #00ff00;
            padding: 20px;
            margin: 0;
        }
        
        .container {
            max-width: 1000px;
            margin: 0 auto;
            background: #0a0a0a;
            padding: 30px;
            border: 2px solid #00ff00;
            border-radius: 10px;
        }
        
        h1 {
            color: #00ff00;
            text-align: center;
            font-size: 2em;
            margin-bottom: 30px;
            text-shadow: 0 0 10px #00ff00;
        }
        
        .status-section {
            margin: 25px 0;
            padding: 15px;
            border: 1px solid #004400;
            background: #0d0d0d;
        }
        
        .status-section h2 {
            color: #00cc00;
            margin-top: 0;
            border-bottom: 1px solid #004400;
            padding-bottom: 10px;
        }
        
        pre {
            background: #000;
            padding: 15px;
            overflow-x: auto;
            border-left: 3px solid #00ff00;
            line-height: 1.5;
        }
        
        .ok { color: #00ff00; }
        .warning { color: #ffcc00; }
        .error { color: #ff0000; }
        
        .timestamp {
            text-align: center;
            color: #666;
            font-size: 0.9em;
            margin-top: 20px;
        }
        
        a {
            color: #00ccff;
            text-decoration: none;
        }
        
        a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔥 PROMETHEUS STATION - SYSTEM STATUS</h1>
        
        <div class="status-section">
            <h2>⚡ System Overview</h2>
            <pre><?php
echo "Hostname:     " . gethostname() . "\n";
echo "Uptime:       " . trim(shell_exec("uptime -p")) . "\n";
echo "Load Average: " . trim(shell_exec("uptime | awk -F'load average:' '{print $2}'")) . "\n";
echo "Date/Time:    " . date("Y-m-d H:i:s T") . "\n";
            ?></pre>
        </div>
        
        <div class="status-section">
            <h2>🌡️ Hardware Status</h2>
            <pre><?php
$temp = shell_exec("vcgencmd measure_temp");
$temp_value = (float)filter_var($temp, FILTER_SANITIZE_NUMBER_FLOAT, FILTER_FLAG_ALLOW_FRACTION);

echo "CPU Temperature:  " . $temp;
if ($temp_value > 70) {
    echo "                  <span class='error'>⚠️ HIGH TEMPERATURE!</span>\n";
} elseif ($temp_value > 60) {
    echo "                  <span class='warning'>⚠ Warm</span>\n";
} else {
    echo "                  <span class='ok'>✓ Normal</span>\n";
}

echo "\nCPU Voltage:      " . shell_exec("vcgencmd measure_volts core");
echo "Throttling:       " . shell_exec("vcgencmd get_throttled");
            ?></pre>
        </div>
        
        <div class="status-section">
            <h2>💾 Memory & Storage</h2>
            <pre><?php
echo "=== Memory Usage ===\n";
system("free -h | grep -E 'Mem|Swap'");

echo "\n\n=== Disk Usage ===\n";
system("df -h / /var/kiwix/data 2>/dev/null | grep -v Filesystem");
            ?></pre>
        </div>
        
        <div class="status-section">
            <h2>🔧 Service Status</h2>
            <pre><?php
function check_service($service_name, $display_name) {
    $status = shell_exec("systemctl is-active $service_name 2>/dev/null");
    $is_running = (trim($status) === "active");
    
    if ($is_running) {
        echo "<span class='ok'>✓</span> $display_name: <span class='ok'>RUNNING</span>\n";
    } else {
        echo "<span class='error'>✗</span> $display_name: <span class='error'>STOPPED</span>\n";
    }
}

check_service("kiwix-serve", "Kiwix Server   ");
check_service("apache2", "Apache Web Server");
check_service("ssh", "SSH Server     ");

// Check if Tailscale is installed
if (file_exists("/usr/bin/tailscale")) {
    check_service("tailscaled", "Tailscale VPN  ");
}
            ?></pre>
        </div>
        
        <div class="status-section">
            <h2>🌐 Network Information</h2>
            <pre><?php
echo "=== IP Addresses ===\n";
system("ip -4 addr show | grep -E 'inet ' | awk '{print $NF \": \" $2}'");

echo "\n\n=== Active Connections ===\n";
$connections = shell_exec("netstat -tn 2>/dev/null | grep ESTABLISHED | wc -l");
echo "TCP Connections: " . trim($connections) . "\n";

echo "\n=== WiFi Status ===\n";
system("iwconfig wlan0 2>/dev/null | grep -E 'ESSID|Bit Rate|Signal level' || echo 'WiFi interface not active'");
            ?></pre>
        </div>
        
        <div class="status-section">
            <h2>📚 Content Library</h2>
            <pre><?php
$zim_dir = "/var/kiwix/data";
if (is_dir($zim_dir)) {
    echo "=== ZIM Files ===\n";
    $files = glob("$zim_dir/*.zim");
    $total_size = 0;
    
    foreach ($files as $file) {
        $size = filesize($file);
        $total_size += $size;
        $size_human = round($size / (1024 * 1024 * 1024), 2) . " GB";
        echo basename($file) . "\n  Size: " . $size_human . "\n\n";
    }
    
    echo "---\n";
    echo "Total ZIM Files: " . count($files) . "\n";
    echo "Total Size: " . round($total_size / (1024 * 1024 * 1024), 2) . " GB\n";
} else {
    echo "<span class='error'>✗ ZIM directory not found!</span>\n";
}
            ?></pre>
        </div>
        
        <div class="status-section">
            <h2>📊 Recent Activity</h2>
            <pre><?php
echo "=== Apache Access Log (Last 10 requests) ===\n";
system("tail -n 10 /var/log/apache2/access.log 2>/dev/null || echo 'No access logs available'");

echo "\n\n=== Kiwix Service Log (Last 5 lines) ===\n";
system("journalctl -u kiwix-serve -n 5 --no-pager 2>/dev/null || echo 'No service logs available'");
            ?></pre>
        </div>
        
        <div class="timestamp">
            <p>Auto-refresh: 30 seconds | <a href="status.php">🔄 Refresh Now</a> | <a href="/">🏠 Back to Home</a></p>
            <p>Last updated: <?php echo date("Y-m-d H:i:s"); ?></p>
        </div>
    </div>
</body>
</html>
```

**Save:** Ctrl+X, Y, Enter

---

### Test Status Page

**From browser:**
```
http://prometheus-station.local/status.php
```

**You should see:**
- System uptime
- Temperature
- Memory usage
- Service status (all green ✓)
- Network info
- ZIM file list
- Recent logs

**Page auto-refreshes every 30 seconds.**

---

### Add Link to Status from Landing Page

```bash
sudo nano /var/www/html/index.html
```

**In the System Information section:**
```html
<div class="info-section">
    <h3>🔧 System Information</h3>
    <ul>
        <li><strong>Station Name:</strong> prometheus-station</li>
        <!-- ... other info ... -->
        <li><strong>System Health:</strong> <a href="/status.php" style="color: #4ecdc4;">View Live Status →</a></li>
    </ul>
</div>
```

---

## Step 9: Optimize for Field Conditions (15 minutes)

### CSS Improvements for Outdoor Use

**Edit landing page:**
```bash
sudo nano /var/www/html/index.html
```

**Add these CSS rules to the `<style>` section:**

```css
/* High contrast mode for sunlight */
@media (prefers-contrast: high) {
    body {
        background: #fff;
        color: #000;
    }
    
    .content-card {
        background: #f0f0f0;
        border: 3px solid #000;
    }
}

/* Large touch targets for field use */
.content-card .button {
    min-height: 60px;
    font-size: 1.2em;
    display: flex;
    align-items: center;
    justify-content: center;
}

/* Offline indicator always visible */
.offline-badge {
    position: sticky;
    top: 10px;
    z-index: 1000;
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.7; }
}

/* Print optimization */
@media print {
    .offline-badge,
    .footer {
        display: none;
    }
    
    .content-card {
        break-inside: avoid;
        page-break-inside: avoid;
    }
    
    .content-card .button {
        display: none;
    }
}
```

---

### Add Favicon

**Create favicon (simple method):**

```bash
# Create simple text-based favicon using ImageMagick
sudo apt install -y imagemagick

# Generate 32x32 favicon
convert -size 32x32 xc:none \
  -fill '#ff6b35' \
  -draw 'circle 16,16 16,4' \
  ~/favicon.png

# Convert to base64
base64 -w 0 ~/favicon.png > ~/favicon-base64.txt
```

**Add to landing page `<head>` section:**
```html
<link rel="icon" type="image/png" href="data:image/png;base64,YOUR_BASE64_HERE">
```

---

### Create Offline Manifest (PWA)

**Why?** Allows users to "install" as app on mobile.

```bash
sudo nano /var/www/html/manifest.json
```

**Add:**
```json
{
  "name": "Prometheus Station",
  "short_name": "Prometheus",
  "description": "Offline Knowledge Hub - Medical & Emergency Information",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#1a1a1a",
  "theme_color": "#ff6b35",
  "orientation": "portrait-primary",
  "icons": [
    {
      "src": "/favicon.png",
      "sizes": "32x32",
      "type": "image/png"
    }
  ]
}
```

**Link in HTML `<head>`:**
```html
<link rel="manifest" href="/manifest.json">
<meta name="theme-color" content="#ff6b35">
```

---

## ✅ Verification Checklist

### Auto-Start
- [ ] Kiwix service enabled: `systemctl is-enabled kiwix-serve`
- [ ] Apache service enabled: `systemctl is-enabled apache2`
- [ ] Services survive reboot: Test with `sudo reboot`

### Landing Page
- [ ] Custom landing page loads: http://prometheus-station.local
- [ ] All content cards visible
- [ ] Logo displays correctly
- [ ] Responsive on mobile (resize browser)
- [ ] Links work to Kiwix content
- [ ] Offline badge visible

### Apache Configuration
- [ ] Reverse proxy works: `/kiwix/` paths load content
- [ ] Landing page served on port 80
- [ ] No errors in Apache logs: `sudo tail /var/log/apache2/error.log`

### Connection Instructions
- [ ] Instructions page loads: http://prometheus-station.local/connect.html
- [ ] Printable (test with browser print preview)
- [ ] QR code present (if generated)

### System Status
- [ ] Status page loads: http://prometheus-station.local/status.php
- [ ] All services show "RUNNING"
- [ ] Temperature reasonable (<65°C)
- [ ] Memory usage acceptable
- [ ] ZIM files listed correctly
- [ ] Auto-refresh works (wait 30 seconds)

### Optimization
- [ ] Touch targets large enough (test on phone)
- [ ] High contrast readable outdoors
- [ ] Favicon displays in browser tab
- [ ] PWA manifest linked

---

## 🛠️ Troubleshooting

### Apache Won't Start

**Error:** `Address already in use`

**Check what's using port 80:**
```bash
sudo netstat -tulpn | grep :80
```

**If Kiwix is on 80:**
- You didn't update Kiwix service to port 8080
- Go back to Step 2 and move Kiwix to 8080

---

### Landing Page Shows Apache Default

**Cause:** prometheus.conf not enabled

**Fix:**
```bash
sudo a2ensite prometheus
sudo a2dissite 000-default
sudo systemctl restart apache2
```

---

### Reverse Proxy Not Working

**Symptom:** `/kiwix/` returns 404

**Check:**
```bash
# Verify proxy modules enabled
apache2ctl -M | grep proxy
```

**Should see:**
```
proxy_module (shared)
proxy_http_module (shared)
```

**If missing:**
```bash
sudo a2enmod proxy proxy_http
sudo systemctl restart apache2
```

---

### Content Cards Not Updating

**After adding new ZIM files, cards don't show new content**

**Solution:**
```bash
# Run update script
./update-prometheus-content.sh

# Manually edit landing page if needed
sudo nano /var/www/html/index.html
```

---

### Status Page Shows PHP Code

**Symptom:** Instead of dynamic content, you see raw PHP

**Cause:** PHP not installed or enabled

**Fix:**
```bash
sudo apt install -y php libapache2-mod-php
sudo systemctl restart apache2
```

---

### Images/Logos Not Displaying

**Base64 encoded images don't show**

**Check:**
1. Base64 string complete (no line breaks in HTML)
2. Correct MIME type: `data:image/png;base64,...`
3. Image file was valid PNG/JPG before encoding

**Re-encode cleanly:**
```bash
base64 -w 0 image.png > image-base64.txt
# Use entire output, no spaces/breaks
```

---

## 📊 Performance Tips

### Reduce Landing Page Size

**Current HTML is ~15-20KB with embedded styles.**

**To optimize:**
1. Move CSS to external file
2. Minify CSS/HTML
3. Compress images more
4. Lazy-load content cards

**For now:** Current size is fine for offline use.

---

### Cache Static Assets

**Add to Apache config:**
```bash
sudo nano /etc/apache2/sites-available/prometheus.conf
```

**Add before `</VirtualHost>`:**
```apache
# Cache static assets
<FilesMatch "\.(jpg|jpeg|png|gif|css|js|ico)$">
    Header set Cache-Control "max-age=2592000, public"
</FilesMatch>
```

**Reload Apache:**
```bash
sudo systemctl reload apache2
```

---

## 🎯 Next Steps

**Your Kiwix installation is now polished and field-ready!**

### Immediate:
- [ ] Print connection instructions
- [ ] Test with real users
- [ ] Note any UI improvements needed
- [ ] Take screenshots for documentation

### Soon:
- [ ] **[Step 4 - System Integration](04-integration.md)** - Combine with Meshtastic
- [ ] Configure WiFi access point (if not done yet)
- [ ] Setup E-Ink status display

### Optional Enhancements:
- [ ] Add more languages to landing page
- [ ] Create usage statistics dashboard
- [ ] Generate QR codes for each content section
- [ ] Add search functionality to landing page
- [ ] Create mobile app icons for PWA

---

## 📚 Maintenance Commands

**Keep these handy for future updates:**

```bash
# Update ZIM files and regenerate content
~/update-prometheus-content.sh

# Restart all services
sudo systemctl restart kiwix-serve apache2

# Check all service status
sudo systemctl status kiwix-serve apache2

# View live logs
sudo journalctl -fu kiwix-serve
sudo tail -f /var/log/apache2/access.log

# Clear Apache cache
sudo rm -rf /var/cache/apache2/*
sudo systemctl restart apache2

# Backup configuration
tar -czf ~/prometheus-backup-$(date +%Y%m%d).tar.gz \
  /var/www/html \
  /etc/apache2/sites-available/prometheus.conf \
  /etc/systemd/system/kiwix-serve.service \
  ~/update-prometheus-content.sh
```

---

## 🎓 What You've Learned

Congratulations! You now know:

✅ **Service management** - Verify auto-start, manage systemd  
✅ **Web server configuration** - Apache reverse proxy, virtual hosts  
✅ **HTML/CSS customization** - Create responsive, accessible interfaces  
✅ **Base64 encoding** - Embed images in HTML  
✅ **PHP scripting** - Dynamic system status pages  
✅ **Shell scripting** - Automation for maintenance  
✅ **UX for field conditions** - High contrast, touch-friendly, offline-first  
✅ **Documentation** - Printable instructions, QR codes  

**These skills transfer to:**
- Any web server deployment
- Field IT infrastructure
- Humanitarian tech projects
- Offline-first applications
- Low-resource computing environments

---

**Next:** [Step 4 - System Integration](04-integration.md) - Bring it all together! 🔥

---

*Last updated: December 2025*  
*Tested on: Raspberry Pi 4 8GB with Apache 2.4, Kiwix 3.x*  
*Total configuration time: 2h 30min*

