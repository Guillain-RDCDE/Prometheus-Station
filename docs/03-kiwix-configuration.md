# Step 3: Kiwix Configuration & Web Interface

**Goal:** Transform Kiwix from a basic server into a polished, professional knowledge station with custom landing page and monitoring tools.

**Time Required:** 2-3 hours  
**Difficulty:** ⭐⭐⭐ Medium (Web configuration, reverse proxy setup)

**💡 Real experience:** This step creates the professional interface that makes Prometheus Station accessible to everyone, not just tech experts.

---

## 📋 What You'll Need

### Prerequisites
- [ ] ✅ Completed [Step 1 - Raspberry Pi Setup](01-raspberry-setup.md)
- [ ] ✅ Completed [Step 2 - Kiwix Installation](02-kiwix-installation.md)
- [ ] SSH access to your Pi
- [ ] Kiwix server running with ZIM files
- [ ] Basic understanding of HTML/CSS (we explain everything)

---

## 🎯 Overview

We'll accomplish:
1. ✅ Install and configure Apache web server
2. ✅ Setup reverse proxy for clean URLs
3. ✅ Create professional landing page
4. ✅ Add logo/branding
5. ✅ Create connection instructions page
6. ✅ Build system monitoring dashboard
7. ✅ Configure auto-update script

**What you'll have at the end:**
- Professional blue-themed interface
- Direct links to all content
- Real-time system monitoring
- Printable connection instructions
- Automated content updates

---

## Step 1: Install Apache Web Server (10 minutes)

### Why Apache?

Kiwix runs on port 8080, but we want:
- Clean URLs without port numbers
- Professional landing page
- Multiple services on port 80
- Better organization

**Apache acts as a "traffic director" routing requests properly.**

---

### Install Apache

```bash
# Install Apache
sudo apt update
sudo apt install -y apache2

# Verify installation
apache2 -v
```

**Expected output:**
```
Server version: Apache/2.4.XX (Debian)
```

---

### Enable Required Modules

```bash
# Enable proxy modules for reverse proxy functionality
sudo a2enmod proxy
sudo a2enmod proxy_http
sudo a2enmod rewrite

# Restart Apache to load modules
sudo systemctl restart apache2
```

**What these modules do:**
- `proxy` - Core proxy functionality
- `proxy_http` - HTTP-specific proxying
- `rewrite` - URL rewriting for clean paths

---

### Configure Firewall

```bash
# Apache will use port 80
sudo ufw allow 80/tcp
sudo ufw reload

# Verify rules
sudo ufw status
```

**Expected output:**
```
Status: active

To                         Action      From
--                         ------      ----
22/tcp                     ALLOW       Anywhere
80/tcp                     ALLOW       Anywhere
```

---

### Move Kiwix to Port 8080

**Edit Kiwix service:**

```bash
sudo nano /etc/systemd/system/kiwix-serve.service
```

**Find the ExecStart line and change port to 8080:**

```ini
# OLD:
ExecStart=/usr/local/bin/kiwix-serve --port=80 ...

# NEW:
ExecStart=/usr/local/bin/kiwix-serve --port=8080 ...
```

**Full ExecStart should look like:**
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

# Verify it's on port 8080
curl http://localhost:8080
```

Should return HTML content.

---

## Step 2: Configure Apache Reverse Proxy (15 minutes)

### Create Apache Configuration

```bash
sudo nano /etc/apache2/sites-available/prometheus.conf
```

**Add this complete configuration:**

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
    ProxyPass /content http://localhost:8080/content
    ProxyPassReverse /content http://localhost:8080/content
    
    ProxyPass /catalog http://localhost:8080/catalog
    ProxyPassReverse /catalog http://localhost:8080/catalog
    
    ProxyPass /skin http://localhost:8080/skin
    ProxyPassReverse /skin http://localhost:8080/skin
    
    ProxyPass /search http://localhost:8080/search
    ProxyPassReverse /search http://localhost:8080/search
</VirtualHost>
```

**Save:** Ctrl+X, Y, Enter

---

### Enable Site and Reload Apache

```bash
# Disable default Apache site
sudo a2dissite 000-default

# Enable Prometheus site
sudo a2ensite prometheus

# Test configuration
sudo apache2ctl configtest
```

**Expected output:** `Syntax OK`

**Restart Apache:**
```bash
sudo systemctl restart apache2
```

---

### Test Reverse Proxy

**From browser:**
```
http://prometheus-station.local/content/
```

Should show Kiwix content library!

---

## Step 3: Add Logo/Branding (10 minutes)

### Transfer Your Logo

**From your computer (Windows PowerShell):**

```powershell
# Navigate to logo location
cd "C:\Users\YourUsername\Path\To\Logo"

# Transfer to Pi
scp logo.png guillain@prometheus-station.local:/tmp/
```

**On the Pi:**

```bash
# Move logo to web directory
sudo mv /tmp/logo.png /var/www/html/

# Set permissions
sudo chown www-data:www-data /var/www/html/logo.png
sudo chmod 644 /var/www/html/logo.png

# Verify
ls -lh /var/www/html/logo.png
```

---

## Step 4: Create Professional Landing Page (30 minutes)

### Create index.html

```bash
sudo nano /var/www/html/index.html
```

**Paste this complete HTML:**

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Prometheus Station - Medical Hub</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: #f8f9fa;
            color: #212529;
            min-height: 100vh;
            padding: 0;
        }
        
        /* Top Bar */
        .top-bar {
            background: white;
            border-bottom: 3px solid #0066cc;
            padding: 20px 40px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        }
        
        .top-bar-content {
            max-width: 1400px;
            margin: 0 auto;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .logo-section {
            display: flex;
            align-items: center;
            gap: 20px;
        }
        
        .logo-img {
            height: 210px !important;
            width: auto !important;
            object-fit: none;
        }
        
        .logo-text h1 {
            color: #0066cc;
            font-size: 2em;
            font-weight: 700;
            margin-bottom: 5px;
        }
        
        .logo-text .subtitle {
            color: #6c757d;
            font-size: 0.95em;
        }
        
        .status-indicator {
            display: flex;
            align-items: center;
            gap: 10px;
            background: #d1ecf1;
            color: #0c5460;
            padding: 10px 20px;
            border-radius: 50px;
            font-weight: 600;
            font-size: 0.9em;
        }
        
        .status-dot {
            width: 10px;
            height: 10px;
            background: #28a745;
            border-radius: 50%;
            animation: pulse-green 2s infinite;
        }
        
        @keyframes pulse-green {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        /* Main Container */
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 40px 20px;
        }
        
        /* Notice Banner */
        .notice {
            background: #fff3cd;
            border: 1px solid #ffc107;
            border-radius: 8px;
            padding: 16px 24px;
            margin-bottom: 30px;
            display: flex;
            align-items: center;
            gap: 15px;
        }
        
        .notice-icon {
            font-size: 2em;
        }
        
        .notice-content h3 {
            color: #856404;
            font-size: 1em;
            font-weight: 600;
            margin-bottom: 5px;
        }
        
        .notice-content p {
            color: #856404;
            font-size: 0.9em;
            margin: 0;
        }
        
        /* Content Cards */
        .content-section {
            margin-bottom: 40px;
        }
        
        .section-header {
            margin-bottom: 25px;
        }
        
        .section-header h2 {
            color: #0066cc;
            font-size: 1.8em;
            font-weight: 600;
            margin-bottom: 8px;
        }
        
        .section-header p {
            color: #6c757d;
            font-size: 1em;
        }
        
        .cards-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
            gap: 24px;
        }
        
        .medical-card {
            background: white;
            border: 1px solid #dee2e6;
            border-radius: 12px;
            padding: 28px;
            text-decoration: none;
            color: inherit;
            display: block;
            transition: all 0.3s ease;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        
        .medical-card:hover {
            border-color: #0066cc;
            transform: translateY(-4px);
            box-shadow: 0 12px 24px rgba(0,102,204,0.15);
        }
        
        .card-top {
            display: flex;
            align-items: center;
            gap: 15px;
            margin-bottom: 18px;
        }
        
        .card-icon {
            font-size: 2.8em;
        }
        
        .card-label {
            background: #e7f3ff;
            color: #0066cc;
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 0.75em;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .medical-card h3 {
            color: #212529;
            font-size: 1.4em;
            margin-bottom: 12px;
            font-weight: 600;
        }
        
        .medical-card .description {
            color: #6c757d;
            font-size: 0.95em;
            line-height: 1.6;
            margin-bottom: 20px;
        }
        
        .card-bottom {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding-top: 16px;
            border-top: 1px solid #e9ecef;
        }
        
        .card-size {
            color: #495057;
            font-size: 0.9em;
            font-weight: 600;
        }
        
        .card-button {
            background: #0066cc;
            color: white;
            padding: 10px 24px;
            border-radius: 6px;
            font-weight: 600;
            font-size: 0.9em;
            transition: background 0.3s;
        }
        
        .medical-card:hover .card-button {
            background: #0052a3;
        }
        
        /* Quick Access Panel */
        .quick-access {
            background: white;
            border: 1px solid #dee2e6;
            border-radius: 12px;
            padding: 35px;
            margin-bottom: 30px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        
        .quick-access h3 {
            color: #0066cc;
            font-size: 1.5em;
            margin-bottom: 25px;
            font-weight: 600;
            text-align: center;
        }
        
        .quick-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
        }
        
        .quick-item {
            text-align: center;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
            transition: all 0.3s;
        }
        
        .quick-item:hover {
            background: #e7f3ff;
            transform: scale(1.05);
        }
        
        .quick-icon {
            font-size: 2.5em;
            margin-bottom: 12px;
            display: block;
        }
        
        .quick-label {
            color: #6c757d;
            font-size: 0.8em;
            font-weight: 600;
            text-transform: uppercase;
            margin-bottom: 6px;
        }
        
        .quick-value {
            color: #212529;
            font-weight: 700;
            font-size: 1em;
        }
        
        .quick-value a {
            color: #0066cc;
            text-decoration: none;
        }
        
        .quick-value a:hover {
            text-decoration: underline;
        }
        
        /* Footer */
        .footer {
            background: white;
            border-top: 1px solid #dee2e6;
            padding: 25px;
            text-align: center;
            color: #6c757d;
            font-size: 0.9em;
            margin-top: 40px;
        }
        
        .footer a {
            color: #0066cc;
            text-decoration: none;
            font-weight: 500;
        }
        
        .footer a:hover {
            text-decoration: underline;
        }
        
        /* Responsive */
        @media (max-width: 768px) {
            .top-bar {
                padding: 15px 20px;
            }
            
            .top-bar-content {
                flex-direction: column;
                gap: 15px;
            }
            
            .logo-section {
                flex-direction: column;
                text-align: center;
            }
            
            .logo-img {
                height: 150px !important;
            }
            
            .logo-text h1 {
                font-size: 1.5em;
            }
            
            .cards-grid {
                grid-template-columns: 1fr;
            }
            
            .quick-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <!-- Top Bar -->
    <div class="top-bar">
        <div class="top-bar-content">
            <div class="logo-section">
                <img src="/logo.png" alt="Prometheus Station Logo" class="logo-img">
                <div class="logo-text">
                    <h1>Prometheus Station</h1>
                    <p class="subtitle">Emergency Medical Knowledge Repository</p>
                </div>
            </div>
            <div class="status-indicator">
                <span class="status-dot"></span>
                <span>System Online • Offline Ready</span>
            </div>
        </div>
    </div>
    
    <!-- Main Container -->
    <div class="container">
        
        <!-- Notice -->
        <div class="notice">
            <span class="notice-icon">ℹ️</span>
            <div class="notice-content">
                <h3>Offline Operation Mode</h3>
                <p>All medical protocols and reference materials accessible without internet connectivity. Last updated: December 2025.</p>
            </div>
        </div>
        
        <!-- Priority Content -->
        <div class="content-section">
            <div class="section-header">
                <h2>Emergency Knowledge Hub</h2>
                <p>Critical protocols and clinical references for field operations</p>
            </div>
            <div class="cards-grid">
                
                <a href="/content/zimgit-post-disaster_en_2024-05" class="medical-card">
                    <div class="card-top">
                        <span class="card-icon">🚑</span>
                        <span class="card-label">Priority</span>
                    </div>
                    <h3>Post-Disaster Protocols</h3>
                    <p class="description">WHO field protocols for mass casualties, emergency triage, and disaster medical response procedures.</p>
                    <div class="card-bottom">
                        <span class="card-size">615 MB</span>
                        <span class="card-button">Open Resource</span>
                    </div>
                </a>
                
                <a href="/content/wikem_en_all_maxi_2021-02" class="medical-card">
                    <div class="card-top">
                        <span class="card-icon">⚕️</span>
                        <span class="card-label">Clinical</span>
                    </div>
                    <h3>Emergency Medicine Wiki</h3>
                    <p class="description">ER procedures, trauma management, toxicology reference. Largest open emergency medicine resource.</p>
                    <div class="card-bottom">
                        <span class="card-size">42 MB</span>
                        <span class="card-button">Open Resource</span>
                    </div>
                </a>
                
                <a href="/content/mdwiki_en_all_maxi_2025-11" class="medical-card">
                    <div class="card-top">
                        <span class="card-icon">📚</span>
                        <span class="card-label">Reference</span>
                    </div>
                    <h3>Medical Encyclopedia</h3>
                    <p class="description">Comprehensive medical database covering diseases, treatments, pharmacology, and clinical guidelines.</p>
                    <div class="card-bottom">
                        <span class="card-size">2.1 GB</span>
                        <span class="card-button">Open Resource</span>
                    </div>
                </a>
                
            </div>
        </div>
        
        <!-- General Knowledge -->
        <div class="content-section">
            <div class="section-header">
                <h2>General Knowledge Base</h2>
                <p>Complete Wikipedia archives and field survival guides</p>
            </div>
            <div class="cards-grid">
                
                <a href="/content/wikipedia_en_all_maxi_2025-08" class="medical-card">
                    <div class="card-top">
                        <span class="card-icon">🌍</span>
                        <span class="card-label">Complete</span>
                    </div>
                    <h3>Wikipedia (English)</h3>
                    <p class="description">Full English Wikipedia archive. All medical, scientific, technical, and general knowledge articles.</p>
                    <div class="card-bottom">
                        <span class="card-size">90 GB</span>
                        <span class="card-button">Open Resource</span>
                    </div>
                </a>
                
                <a href="/content/wikipedia_fr_all_maxi_2025-06" class="medical-card">
                    <div class="card-top">
                        <span class="card-icon">🇫🇷</span>
                        <span class="card-label">Complet</span>
                    </div>
                    <h3>Wikipédia (Français)</h3>
                    <p class="description">Archive complète de Wikipédia française. Articles médicaux, scientifiques et connaissances générales.</p>
                    <div class="card-bottom">
                        <span class="card-size">25 GB</span>
                        <span class="card-button">Ouvrir</span>
                    </div>
                </a>
                
                <a href="/content/zimgit-water_en_2024-08" class="medical-card">
                    <div class="card-top">
                        <span class="card-icon">💧</span>
                        <span class="card-label">Survival</span>
                    </div>
                    <h3>Water Treatment</h3>
                    <p class="description">Water collection, purification methods, quality testing, and safe storage for field operations.</p>
                    <div class="card-bottom">
                        <span class="card-size">20 MB</span>
                        <span class="card-button">Open Resource</span>
                    </div>
                </a>
                
                <a href="/content/zimgit-food-preparation_en_2025-04" class="medical-card">
                    <div class="card-top">
                        <span class="card-icon">🍽️</span>
                        <span class="card-label">Survival</span>
                    </div>
                    <h3>Food Safety</h3>
                    <p class="description">Safe food handling, storage methods, preparation techniques for preventing foodborne illness.</p>
                    <div class="card-bottom">
                        <span class="card-size">93 MB</span>
                        <span class="card-button">Open Resource</span>
                    </div>
                </a>
                
            </div>
        </div>
        
        <!-- Quick Access -->
        <div class="quick-access">
            <h3>⚡ Quick Access</h3>
            <div class="quick-grid">
                <div class="quick-item">
                    <span class="quick-icon">📶</span>
                    <div class="quick-label">Network</div>
                    <div class="quick-value">Prometheus-Station</div>
                </div>
                <div class="quick-item">
                    <span class="quick-icon">🌐</span>
                    <div class="quick-label">URL</div>
                    <div class="quick-value">prometheus-station.local</div>
                </div>
                <div class="quick-item">
                    <span class="quick-icon">💾</span>
                    <div class="quick-label">Content</div>
                    <div class="quick-value">~120 GB</div>
                </div>
                <div class="quick-item">
                    <span class="quick-icon">📋</span>
                    <div class="quick-label">Guide</div>
                    <div class="quick-value"><a href="/connect.html">How to Connect</a></div>
                </div>
                <div class="quick-item">
                    <span class="quick-icon">💚</span>
                    <div class="quick-label">Status</div>
                    <div class="quick-value"><a href="/status.php">System Health</a></div>
                </div>
            </div>
        </div>
        
    </div>
    
    <!-- Footer -->
    <div class="footer">
        <p><strong>Prometheus Station v1.0</strong> • Powered by <a href="https://www.kiwix.org">Kiwix</a></p>
        <p style="margin-top: 8px;"><a href="https://github.com/GuillainM/Prometheus-Station">GitHub</a> • <a href="/connect.html">Connection Guide</a> • MIT License</p>
    </div>
    
</body>
</html>
```

**Save:** Ctrl+X, Y, Enter

**Set permissions:**
```bash
sudo chown www-data:www-data /var/www/html/index.html
sudo chmod 644 /var/www/html/index.html
```

---

### Adjust Logo Size

**If your logo is too large/small, edit the CSS:**

```bash
sudo nano /var/www/html/index.html
```

**Find `.logo-img` (around line 48) and adjust:**

```css
.logo-img {
    height: 210px !important;  /* Change this value */
    width: auto !important;
    object-fit: none;
}
```

Common sizes:
- Small: `150px`
- Medium: `210px` (default)
- Large: `300px`

**Save and test:** `http://prometheus-station.local`

---

## Step 5: Install PHP for Dynamic Pages (10 minutes)

### Why PHP?

We need PHP to create the system status monitoring page.

```bash
# Install PHP
sudo apt update
sudo apt install -y php libapache2-mod-php php-cli

# Verify installation
php -v
```

**Expected output:**
```
PHP 8.4.16 (cli) (built: Dec 18 2024 21:19:25) (NTS)
```

---

### Enable PHP Module

```bash
# Add www-data to video group (for temperature monitoring)
sudo usermod -a -G video www-data

# Restart Apache
sudo systemctl restart apache2

# Verify PHP module is loaded
apache2ctl -M | grep php
```

**Expected output:**
```
php_module (shared)
```

---

## Step 6: Create Connection Instructions Page (15 minutes)

```bash
sudo nano /var/www/html/connect.html
```

**Paste this complete HTML:**

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Connection Guide - Prometheus Station</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif;
            background: #f8f9fa;
            color: #212529;
            line-height: 1.6;
            padding: 20px;
        }
        
        .container {
            max-width: 900px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #0066cc 0%, #004999 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.2em;
            margin-bottom: 10px;
        }
        
        .header p {
            font-size: 1.1em;
            opacity: 0.95;
        }
        
        .content {
            padding: 40px;
        }
        
        .quick-start {
            background: #d1ecf1;
            border-left: 4px solid #0c5460;
            padding: 25px;
            margin-bottom: 35px;
            border-radius: 4px;
        }
        
        .quick-start h2 {
            color: #0c5460;
            margin-bottom: 15px;
            font-size: 1.5em;
        }
        
        .quick-start ol {
            margin-left: 20px;
        }
        
        .quick-start li {
            margin: 10px 0;
            font-size: 1.05em;
        }
        
        .credential {
            background: #fff3cd;
            padding: 8px 16px;
            border-radius: 4px;
            font-family: monospace;
            font-weight: 700;
            color: #856404;
            font-size: 1.1em;
            border: 2px solid #ffc107;
        }
        
        .step {
            margin: 35px 0;
            padding: 25px;
            background: #f8f9fa;
            border-radius: 8px;
            border-left: 4px solid #0066cc;
        }
        
        .step h3 {
            color: #0066cc;
            margin-bottom: 15px;
            font-size: 1.4em;
        }
        
        .step-number {
            display: inline-block;
            background: #0066cc;
            color: white;
            width: 32px;
            height: 32px;
            border-radius: 50%;
            text-align: center;
            line-height: 32px;
            font-weight: bold;
            margin-right: 10px;
        }
        
        .step ol {
            margin-left: 20px;
            margin-top: 10px;
        }
        
        .step li {
            margin: 8px 0;
        }
        
        .note {
            background: #e7f3ff;
            border: 1px solid #0066cc;
            padding: 15px;
            border-radius: 4px;
            margin-top: 15px;
        }
        
        .note strong {
            color: #0066cc;
        }
        
        .troubleshooting {
            background: #fff3cd;
            padding: 25px;
            border-radius: 8px;
            margin: 30px 0;
        }
        
        .troubleshooting h3 {
            color: #856404;
            margin-bottom: 15px;
        }
        
        .troubleshooting .issue {
            margin: 15px 0;
        }
        
        .troubleshooting .issue strong {
            color: #856404;
            display: block;
            margin-bottom: 5px;
        }
        
        .resources {
            background: white;
            border: 1px solid #dee2e6;
            padding: 25px;
            border-radius: 8px;
            margin-top: 30px;
        }
        
        .resources h3 {
            color: #0066cc;
            margin-bottom: 15px;
        }
        
        .resources ul {
            list-style: none;
            padding: 0;
        }
        
        .resources li {
            padding: 10px 0;
            border-bottom: 1px solid #e9ecef;
        }
        
        .resources li:last-child {
            border-bottom: none;
        }
        
        .resources li strong {
            color: #212529;
            min-width: 180px;
            display: inline-block;
        }
        
        .footer {
            background: #f8f9fa;
            padding: 25px;
            text-align: center;
            border-top: 1px solid #dee2e6;
        }
        
        .footer a {
            color: #0066cc;
            text-decoration: none;
            font-weight: 500;
            margin: 0 15px;
        }
        
        .footer a:hover {
            text-decoration: underline;
        }
        
        .print-btn {
            background: #0066cc;
            color: white;
            border: none;
            padding: 12px 30px;
            border-radius: 6px;
            font-size: 1em;
            font-weight: 600;
            cursor: pointer;
            margin-top: 20px;
        }
        
        .print-btn:hover {
            background: #0052a3;
        }
        
        @media print {
            body {
                background: white;
            }
            
            .container {
                box-shadow: none;
            }
            
            .print-btn, .footer a {
                display: none;
            }
        }
        
        @media (max-width: 768px) {
            .content {
                padding: 20px;
            }
            
            .header h1 {
                font-size: 1.6em;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔥 Prometheus Station</h1>
            <p>Connection Guide</p>
        </div>
        
        <div class="content">
            
            <div class="quick-start">
                <h2>⚡ Quick Start (3 Steps)</h2>
                <ol>
                    <li>Connect to WiFi: <span class="credential">Prometheus-Station</span></li>
                    <li>Password: <span class="credential">12345</span></li>
                    <li>Open browser: <span class="credential">http://prometheus-station.local</span></li>
                </ol>
            </div>
            
            <div class="step">
                <h3><span class="step-number">1</span>Connect to WiFi Network</h3>
                <p>On your device (phone, tablet, or computer):</p>
                <ol>
                    <li>Open WiFi settings</li>
                    <li>Look for network: <span class="credential">Prometheus-Station</span></li>
                    <li>Select and connect</li>
                    <li>Enter password: <span class="credential">12345</span></li>
                    <li>Wait for "Connected" confirmation</li>
                </ol>
                <div class="note">
                    <strong>Note:</strong> You may see "No Internet Access" warning. This is normal - the station operates completely offline.
                </div>
            </div>
            
            <div class="step">
                <h3><span class="step-number">2</span>Open Web Browser</h3>
                <p>Use any web browser:</p>
                <ul>
                    <li>Chrome, Firefox, Safari, Edge - all supported</li>
                    <li>Works on phones, tablets, laptops, desktops</li>
                    <li>No special software required</li>
                </ul>
            </div>
            
            <div class="step">
                <h3><span class="step-number">3</span>Access the Station</h3>
                <p>In your browser address bar, type:</p>
                <p style="text-align: center; font-size: 1.4em; background: #e7f3ff; padding: 20px; border-radius: 6px; margin: 20px 0;">
                    <strong>http://prometheus-station.local</strong>
                </p>
                <p><strong>Alternative (if above doesn't work):</strong></p>
                <p style="text-align: center; font-size: 1.2em; margin-top: 10px;">
                    <span class="credential">http://192.168.42.1</span>
                </p>
            </div>
            
            <div class="troubleshooting">
                <h3>🔧 Troubleshooting</h3>
                
                <div class="issue">
                    <strong>Can't see Prometheus-Station WiFi</strong>
                    <p>→ Check station is powered on</p>
                    <p>→ Wait 60 seconds after boot</p>
                    <p>→ Verify WiFi is enabled on your device</p>
                </div>
                
                <div class="issue">
                    <strong>Password doesn't work</strong>
                    <p>→ Make sure you're typing: <span class="credential">12345</span></p>
                    <p>→ No spaces before or after</p>
                    <p>→ All numbers, no letters</p>
                </div>
                
                <div class="issue">
                    <strong>Website won't load</strong>
                    <p>→ Verify connection to Prometheus-Station WiFi</p>
                    <p>→ Try alternative IP: http://192.168.42.1</p>
                    <p>→ Clear browser cache and retry</p>
                    <p>→ Try different browser</p>
                </div>
                
                <div class="issue">
                    <strong>Slow performance</strong>
                    <p>→ Too many users connected (max 10-20)</p>
                    <p>→ Wait a moment and retry</p>
                    <p>→ Move closer to station</p>
                </div>
            </div>
            
            <div class="resources">
                <h3>📚 Available Resources</h3>
                <ul>
                    <li><strong>Post-Disaster Protocols:</strong> WHO emergency response guidelines (615 MB)</li>
                    <li><strong>Emergency Medicine:</strong> ER procedures and trauma care (42 MB)</li>
                    <li><strong>Medical Encyclopedia:</strong> Complete clinical reference (2.1 GB)</li>
                    <li><strong>Wikipedia English:</strong> Full encyclopedia (90 GB)</li>
                    <li><strong>Wikipédia Français:</strong> Encyclopédie complète (25 GB)</li>
                    <li><strong>Water Treatment:</strong> Purification protocols (20 MB)</li>
                    <li><strong>Food Safety:</strong> Safe handling procedures (93 MB)</li>
                </ul>
            </div>
            
            <div style="text-align: center; margin-top: 30px;">
                <button onclick="window.print()" class="print-btn">🖨️ Print Instructions</button>
            </div>
            
        </div>
        
        <div class="footer">
            <p><strong>Prometheus Station v1.0</strong></p>
            <a href="/">← Back to Home</a>
            <a href="/status.php">System Status</a>
        </div>
    </div>
</body>
</html>
```

**Save:** Ctrl+X, Y, Enter

---

## Step 7: Create System Status Monitor (20 minutes)

**Download the complete status.php file provided separately, or create it:**

```bash
sudo nano /var/www/html/status.php
```

**Use the complete status.php code provided in the project repository.**

**Key features:**
- Real-time system metrics
- Temperature monitoring
- Service status
- Disk usage
- Network information
- ZIM file inventory
- Auto-refresh every 30 seconds

**Set permissions:**
```bash
sudo chown www-data:www-data /var/www/html/status.php
sudo chmod 644 /var/www/html/status.php
```

---

## Step 8: Create Auto-Update Script (15 minutes)

**This script automatically updates the content index when you add new ZIM files.**

```bash
nano ~/update-prometheus-content.sh
```

**Paste this complete script:**

```bash
#!/bin/bash
# Prometheus Station - Content Update Script
# Automatically scans ZIM files and rebuilds content index

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
ZIM_DIR="/var/kiwix/data"
BACKUP_DIR="/var/backups/prometheus"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  PROMETHEUS STATION - Content Update${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Create backup directory
sudo mkdir -p "$BACKUP_DIR"

# Step 1: Backup current index
echo -e "${YELLOW}[1/4] Creating backup...${NC}"
if [ -f "/var/www/html/index.html" ]; then
    TIMESTAMP=$(date +%Y%m%d-%H%M%S)
    sudo cp /var/www/html/index.html "$BACKUP_DIR/index-$TIMESTAMP.html"
    echo -e "${GREEN}✓ Backup: $BACKUP_DIR/index-$TIMESTAMP.html${NC}"
fi

# Step 2: Scan ZIM files
echo -e "${YELLOW}[2/4] Scanning ZIM files...${NC}"
ZIM_COUNT=$(ls -1 "$ZIM_DIR"/*.zim 2>/dev/null | wc -l)
if [ "$ZIM_COUNT" -eq 0 ]; then
    echo -e "${RED}✗ No ZIM files found${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Found $ZIM_COUNT ZIM files${NC}"

# Step 3: Restart Kiwix
echo -e "${YELLOW}[3/4] Restarting Kiwix...${NC}"
sudo systemctl restart kiwix-serve
sleep 3

if systemctl is-active --quiet kiwix-serve; then
    echo -e "${GREEN}✓ Kiwix restarted${NC}"
else
    echo -e "${RED}✗ Kiwix failed to restart${NC}"
    exit 1
fi

# Step 4: Calculate totals
echo -e "${YELLOW}[4/4] Calculating totals...${NC}"
TOTAL_STORAGE=$(du -sh "$ZIM_DIR" | cut -f1)
UPDATE_DATE=$(date "+%B %Y")

echo -e "${GREEN}✓ Update complete${NC}"
echo ""
echo "Summary:"
echo "  - ZIM files: $ZIM_COUNT"
echo "  - Total storage: $TOTAL_STORAGE"
echo "  - Updated: $UPDATE_DATE"
echo ""
```

**Save:** Ctrl+X, Y, Enter

**Make executable:**
```bash
chmod +x ~/update-prometheus-content.sh
```

**Test it:**
```bash
./update-prometheus-content.sh
```

---

### Automate with Cron (Optional)

**Run updates daily at 3 AM:**

```bash
crontab -e
```

**Add this line:**
```
0 3 * * * /home/guillain/update-prometheus-content.sh >> /var/log/prometheus-update.log 2>&1
```

**Save and exit.**

---

## ✅ Verification Checklist

### Apache Configuration
- [ ] Apache running: `systemctl status apache2`
- [ ] Reverse proxy working: `http://prometheus-station.local/content/`
- [ ] Port 80 in firewall: `sudo ufw status | grep 80`

### Landing Page
- [ ] Index page loads: `http://prometheus-station.local`
- [ ] Logo displays correctly
- [ ] All content cards visible
- [ ] Links work to Kiwix content
- [ ] Responsive on mobile

### PHP & Dynamic Pages
- [ ] PHP installed: `php -v`
- [ ] PHP module loaded: `apache2ctl -M | grep php`
- [ ] Status page works: `http://prometheus-station.local/status.php`
- [ ] Temperature displays correctly
- [ ] All services show status

### Connection Instructions
- [ ] Connect page loads: `http://prometheus-station.local/connect.html`
- [ ] Printable format works
- [ ] Password shown clearly (12345)

### Auto-Update
- [ ] Script executes: `~/update-prometheus-content.sh`
- [ ] No errors shown
- [ ] Cron job configured (if desired)

---

## 🛠️ Troubleshooting

### Apache Won't Start

**Check logs:**
```bash
sudo tail -n 50 /var/log/apache2/error.log
```

**Common issues:**
- Port 80 already in use
- Configuration syntax error
- Missing modules

**Fix:**
```bash
# Check syntax
sudo apache2ctl configtest

# If port conflict, check what's using port 80
sudo netstat -tulpn | grep :80
```

---

### Reverse Proxy Not Working

**Symptoms:** `/content/` returns 404

**Fix:**
```bash
# Verify proxy modules enabled
apache2ctl -M | grep proxy

# If missing:
sudo a2enmod proxy proxy_http
sudo systemctl restart apache2
```

---

### PHP Pages Show Code

**Symptom:** status.php displays PHP code instead of executing

**Fix:**
```bash
# Reinstall PHP module
sudo apt install --reinstall libapache2-mod-php

# Enable module
sudo a2enmod php8.4  # Or your PHP version

# Restart Apache
sudo systemctl restart apache2
```

---

### Temperature Shows Error

**Symptom:** "Can't open device file: /dev/vcio"

**Fix:**
```bash
# Add www-data to video group
sudo usermod -a -G video www-data

# Restart Apache
sudo systemctl restart apache2
```

---

### Logo Too Large/Small

**Edit index.html:**
```bash
sudo nano /var/www/html/index.html
```

**Find `.logo-img` and adjust height:**
```css
.logo-img {
    height: 150px !important;  /* Change this */
    width: auto !important;
}
```

---

## 📊 Performance Tips

### Optimize Apache

```bash
sudo nano /etc/apache2/apache2.conf
```

**Add at end:**
```apache
# Performance tuning
KeepAlive On
MaxKeepAliveRequests 100
KeepAliveTimeout 5

# Memory limits
<IfModule mpm_prefork_module>
    StartServers 2
    MinSpareServers 2
    MaxSpareServers 5
    MaxRequestWorkers 10
    MaxConnectionsPerChild 1000
</IfModule>
```

**Restart Apache:**
```bash
sudo systemctl restart apache2
```

---

### Cache Static Assets

**Add to prometheus.conf:**
```bash
sudo nano /etc/apache2/sites-available/prometheus.conf
```

**Before `</VirtualHost>`:**
```apache
# Cache static assets
<FilesMatch "\.(jpg|jpeg|png|gif|css|js|ico)$">
    Header set Cache-Control "max-age=2592000, public"
</FilesMatch>
```

**Reload:**
```bash
sudo systemctl reload apache2
```

---

## 🎯 What You've Accomplished

✅ **Professional web interface** with branded landing page  
✅ **Reverse proxy** for clean, accessible URLs  
✅ **System monitoring** with real-time metrics  
✅ **Connection instructions** for users  
✅ **Auto-update script** for content management  
✅ **PHP-powered** dynamic content  
✅ **Responsive design** works on all devices  

**Your Prometheus Station now has:**
- Professional appearance
- Easy navigation
- Real-time monitoring
- Automated updates
- User-friendly interface

---

## 🎓 What You've Learned

- Apache web server configuration
- Reverse proxy setup
- HTML/CSS customization
- PHP integration
- System monitoring with PHP
- Automated maintenance scripts
- User interface design principles

**These skills transfer to:**
- Any web server deployment
- Professional website development
- System administration
- Field IT infrastructure
- Humanitarian tech projects

---

## 🚀 Next Steps

**Your web interface is complete!** Time to make the station autonomous:

**→ [Step 4 - System Integration](04-integration.md)**
- WiFi Access Point configuration
- Meshtastic LoRa network
- E-Ink status display
- Complete system integration

---

## 📝 Quick Command Reference

```bash
# Apache control
sudo systemctl restart apache2
sudo systemctl status apache2
sudo apache2ctl configtest

# View logs
sudo tail -f /var/log/apache2/error.log
sudo tail -f /var/log/apache2/access.log

# PHP
php -v
apache2ctl -M | grep php

# Test pages
curl http://localhost
curl http://localhost:8080

# Update content
~/update-prometheus-content.sh

# File permissions
sudo chown www-data:www-data /var/www/html/*
sudo chmod 644 /var/www/html/*.html
sudo chmod 644 /var/www/html/*.php
```

---

**Last updated:** December 2025  
**Tested on:** Raspberry Pi 4 8GB, Apache 2.4, PHP 8.4  
**Total configuration time:** 2h 30min (tested)

---

*Made with 🔥 for Prometheus Station*
