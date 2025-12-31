# Step 5: System Maintenance & Updates

**Goal:** Establish maintenance routines to keep Prometheus Station healthy, secure, and up-to-date.

**Time Required:** 
- Initial setup: 2-3 hours
- Monthly maintenance: 30-45 minutes
- ZIM updates: 2-6 hours (mostly downloading)

**Difficulty:** ⭐⭐⭐ Medium (systematic procedures, nothing complex)

**💡 Real experience:** A well-maintained station runs for months without issues. Neglect maintenance and you'll face corrupted files, full disks, and mysterious crashes. This guide includes all the fixes discovered during real-world testing.

---

## 📋 Prerequisites

- [ ] ✅ Completed [Step 1 - Raspberry Pi Setup](01-raspberry-setup.md)
- [ ] ✅ Completed [Step 2 - Kiwix Installation](02-kiwix-installation.md)
- [ ] ✅ Completed [Step 3 - Kiwix Configuration](03-kiwix-configuration.md)
- [ ] ✅ Completed [Step 4 - WiFi Access Point](04-wifi-access-point.md)
- [ ] SSH access to your Pi
- [ ] At least 20GB free space on SD card
- [ ] Internet connection (for updates)

---

## 🎯 Overview

We'll accomplish:
1. ✅ Install required tools (bc, ufw)
2. ✅ Create health monitoring dashboard
3. ✅ Setup automated log rotation
4. ✅ Build ZIM update system
5. ✅ Configure system update procedures
6. ✅ Create backup/restore scripts
7. ✅ Setup automated alerts
8. ✅ Configure cron automation
9. ✅ Build monthly maintenance checklist

**What you'll have at the end:**
- Automated health checks
- Safe update procedures
- Content update workflow
- Emergency recovery tools
- Maintenance calendar
- Everything running automatically

---

## 🔧 Part 0: Install Required Tools (5 minutes)

**Before we start, we need two essential tools that might be missing.**

### Step 0.1: Install bc (calculator)

**What is bc?** A command-line calculator needed for comparing temperatures and CPU loads.

```bash
sudo apt update
sudo apt install -y bc
```

**Test it works:**
```bash
echo "70 > 60" | bc
```

**Expected output:** `1` (meaning "true")

---

### Step 0.2: Install and configure UFW (firewall)

**What is UFW?** Uncomplicated Firewall - protects your Pi from unwanted connections.

**⚠️ CRITICAL: We must add SSH rule BEFORE enabling the firewall, or we'll be locked out!**

```bash
# Install UFW
sudo apt install -y ufw

# FIRST: Allow SSH (port 22) - CRITICAL!
sudo ufw allow 22/tcp

# Allow Apache web server
sudo ufw allow 80/tcp

# Allow Kiwix
sudo ufw allow 8080/tcp

# Allow Tailscale VPN (if installed)
sudo ufw allow in on tailscale0

# NOW we can safely enable the firewall
sudo ufw --force enable

# Verify configuration
sudo ufw status verbose
```

**Expected output:**
```
Status: active
Logging: on (low)
Default: deny (incoming), allow (outgoing), disabled (routed)
New profiles: skip

To                         Action      From
--                         ------      ----
22/tcp                     ALLOW IN    Anywhere
80/tcp                     ALLOW IN    Anywhere
8080/tcp                   ALLOW IN    Anywhere
Anywhere on tailscale0     ALLOW IN    Anywhere
22/tcp (v6)                ALLOW IN    Anywhere (v6)
80/tcp (v6)                ALLOW IN    Anywhere (v6)
8080/tcp (v6)              ALLOW IN    Anywhere (v6)
```

**Why this order matters:**
- ❌ **WRONG:** Enable firewall → Add SSH rule → Locked out, need keyboard/monitor
- ✅ **RIGHT:** Add SSH rule → Enable firewall → SSH continues working

---

## 📊 Part 1: Health Monitoring Dashboard (30 minutes)

### Step 1.1: Create system health script

```bash
nano ~/health-check.sh
```

**Paste this COMPLETE script:**

```bash
#!/bin/bash
# Prometheus Station - System Health Check
# Run this daily or when troubleshooting

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     PROMETHEUS STATION - HEALTH CHECK                 ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
echo ""
date
echo ""

# Function to check status with colored output
check_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓${NC} $2"
    else
        echo -e "${RED}✗${NC} $2"
    fi
}

# Function to show warning
show_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# ============================================
# SYSTEM RESOURCES
# ============================================
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}SYSTEM RESOURCES${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Temperature
TEMP=$(vcgencmd measure_temp | cut -d'=' -f2 | cut -d"'" -f1)
echo -n "Temperature: ${TEMP}°C "
if (( $(echo "$TEMP > 70" | bc -l) )); then
    echo -e "${RED}(TOO HOT!)${NC}"
elif (( $(echo "$TEMP > 60" | bc -l) )); then
    echo -e "${YELLOW}(Warm)${NC}"
else
    echo -e "${GREEN}(OK)${NC}"
fi

# CPU Load
LOAD=$(uptime | awk -F'load average:' '{print $2}' | awk '{print $1}' | tr -d ',')
echo -n "CPU Load (1min): $LOAD "
if (( $(echo "$LOAD > 2.0" | bc -l) )); then
    echo -e "${RED}(HIGH!)${NC}"
elif (( $(echo "$LOAD > 1.0" | bc -l) )); then
    echo -e "${YELLOW}(Elevated)${NC}"
else
    echo -e "${GREEN}(OK)${NC}"
fi

# Memory
MEM_USED=$(free -m | awk 'NR==2{printf "%.0f", $3}')
MEM_TOTAL=$(free -m | awk 'NR==2{printf "%.0f", $2}')
MEM_PERCENT=$(awk "BEGIN {printf \"%.0f\", ($MEM_USED/$MEM_TOTAL)*100}")
echo -n "Memory: ${MEM_USED}MB / ${MEM_TOTAL}MB (${MEM_PERCENT}%) "
if [ $MEM_PERCENT -gt 90 ]; then
    echo -e "${RED}(CRITICAL!)${NC}"
elif [ $MEM_PERCENT -gt 75 ]; then
    echo -e "${YELLOW}(High)${NC}"
else
    echo -e "${GREEN}(OK)${NC}"
fi

# Disk Space
DISK_USED=$(df -h / | awk 'NR==2{print $5}' | tr -d '%')
DISK_AVAIL=$(df -h / | awk 'NR==2{print $4}')
echo -n "Disk: ${DISK_USED}% used, ${DISK_AVAIL} available "
if [ $DISK_USED -gt 90 ]; then
    echo -e "${RED}(CRITICAL!)${NC}"
elif [ $DISK_USED -gt 80 ]; then
    echo -e "${YELLOW}(Filling up)${NC}"
else
    echo -e "${GREEN}(OK)${NC}"
fi

# Uptime
echo "Uptime: $(uptime -p)"

echo ""

# ============================================
# CRITICAL SERVICES
# ============================================
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}CRITICAL SERVICES${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Kiwix
systemctl is-active --quiet kiwix-serve
check_status $? "Kiwix Server"

# Apache
systemctl is-active --quiet apache2
check_status $? "Apache Web Server"

# SSH
systemctl is-active --quiet ssh
check_status $? "SSH Access"

# Tailscale (if installed)
if command -v tailscale &> /dev/null; then
    tailscale status &> /dev/null
    check_status $? "Tailscale VPN"
fi

# UFW Firewall
if command -v ufw &> /dev/null; then
    sudo ufw status | grep -q "Status: active"
    check_status $? "Firewall (UFW)"
else
    echo -e "${YELLOW}⚠${NC} Firewall (UFW) - Not installed"
fi

echo ""

# ============================================
# WIFI STATUS
# ============================================
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}WIFI STATUS${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Check if in hotspot mode
if systemctl is-active --quiet hostapd; then
    echo -e "${GREEN}Mode: HOTSPOT (Field)${NC}"
    
    # Connected clients
    CLIENTS=$(iw dev wlan0 station dump 2>/dev/null | grep Station | wc -l)
    echo "Connected clients: $CLIENTS"
    
    # Show active DHCP leases
    if [ -f /var/lib/misc/dnsmasq.leases ]; then
        LEASES=$(wc -l < /var/lib/misc/dnsmasq.leases)
        echo "DHCP leases: $LEASES"
    fi
    
    # Hostapd status
    systemctl is-active --quiet hostapd
    check_status $? "hostapd (AP)"
    
    # Dnsmasq status
    systemctl is-active --quiet dnsmasq
    check_status $? "dnsmasq (DHCP/DNS)"
else
    echo -e "${GREEN}Mode: CLIENT (Home)${NC}"
    
    # Show connection
    SSID=$(iwgetid -r)
    if [ -n "$SSID" ]; then
        echo "Connected to: $SSID"
        IP=$(ip -4 addr show wlan0 | grep -oP '(?<=inet\s)\d+(\.\d+){3}')
        echo "IP Address: $IP"
    else
        echo -e "${RED}Not connected to WiFi${NC}"
    fi
fi

echo ""

# ============================================
# CONTENT STATUS
# ============================================
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}CONTENT STATUS${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# ZIM files
if [ -d /var/kiwix/data ]; then
    ZIM_COUNT=$(ls -1 /var/kiwix/data/*.zim 2>/dev/null | wc -l)
    ZIM_SIZE=$(du -sh /var/kiwix/data 2>/dev/null | cut -f1)
    echo "ZIM files: $ZIM_COUNT"
    echo "Total size: $ZIM_SIZE"
    
    # Check for very old files (>6 months)
    OLD_ZIMS=$(find /var/kiwix/data -name "*.zim" -mtime +180 2>/dev/null | wc -l)
    if [ $OLD_ZIMS -gt 0 ]; then
        show_warning "$OLD_ZIMS ZIM file(s) older than 6 months - consider updating"
    fi
else
    echo -e "${RED}ZIM directory not found!${NC}"
fi

echo ""

# ============================================
# SECURITY CHECKS
# ============================================
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}SECURITY STATUS${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Check for system updates
UPDATES=$(apt list --upgradable 2>/dev/null | grep -c upgradable)
if [ $UPDATES -gt 0 ]; then
    show_warning "$UPDATES packages need updating"
else
    echo -e "${GREEN}✓${NC} System packages up to date"
fi

# Check last update
if [ -f /var/log/apt/history.log ]; then
    LAST_UPDATE=$(grep "Start-Date" /var/log/apt/history.log | tail -1 | cut -d' ' -f2)
    echo "Last system update: $LAST_UPDATE"
else
    show_warning "Cannot determine last update date"
fi

# Failed login attempts
FAILED_LOGINS=$(grep "Failed password" /var/log/auth.log 2>/dev/null | wc -l)
if [ $FAILED_LOGINS -gt 10 ]; then
    show_warning "$FAILED_LOGINS failed login attempts detected"
fi

echo ""

# ============================================
# STORAGE DETAILS
# ============================================
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}STORAGE BREAKDOWN${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Top 5 space consumers
echo "Largest directories:"
sudo du -h --max-depth=1 / 2>/dev/null | sort -hr | head -6 | tail -5

echo ""

# ============================================
# LOG FILES SIZE
# ============================================
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}LOG FILES${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

LOG_SIZE=$(du -sh /var/log 2>/dev/null | cut -f1)
echo "Total log size: $LOG_SIZE"

# Large log files
LARGE_LOGS=$(find /var/log -type f -size +10M 2>/dev/null | wc -l)
if [ $LARGE_LOGS -gt 0 ]; then
    show_warning "$LARGE_LOGS log file(s) larger than 10MB - consider rotation"
fi

echo ""

# ============================================
# RECOMMENDATIONS
# ============================================
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}RECOMMENDATIONS${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

ISSUES=0

# Temperature warning
if (( $(echo "$TEMP > 65" | bc -l) )); then
    echo "• Improve cooling (temp: ${TEMP}°C)"
    ((ISSUES++))
fi

# Disk space warning
if [ $DISK_USED -gt 85 ]; then
    echo "• Free up disk space (${DISK_USED}% used)"
    ((ISSUES++))
fi

# Updates available
if [ $UPDATES -gt 10 ]; then
    echo "• Run system updates ($UPDATES packages)"
    ((ISSUES++))
fi

# Old ZIM files
if [ $OLD_ZIMS -gt 0 ]; then
    echo "• Update ZIM files ($OLD_ZIMS old files)"
    ((ISSUES++))
fi

if [ $ISSUES -eq 0 ]; then
    echo -e "${GREEN}✓ No issues detected - system healthy!${NC}"
fi

echo ""
echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
echo ""
```

**Save:** Ctrl+X, Y, Enter

---

### Step 1.2: Make executable and test

```bash
chmod +x ~/health-check.sh
~/health-check.sh
```

**Expected output:** Complete health report with colored indicators

**What to look for:**
- ✅ All green checkmarks for services
- ✅ Temperature under 65°C
- ✅ Disk usage under 80%
- ✅ No critical warnings
- ✅ NO errors about `bc: command not found`
- ✅ NO errors about `ufw: command not found`

**If you see errors:** Go back to Part 0 and install missing tools.

---

## 🗂️ Part 2: Log Management (20 minutes)

### Step 2.1: Configure log rotation for Prometheus logs

```bash
sudo nano /etc/logrotate.d/prometheus
```

**Paste this configuration:**

```
/var/log/prometheus/*.log {
    weekly
    rotate 8
    compress
    delaycompress
    missingok
    notifempty
    create 0644 guillain guillain
}
```

**What this does:**
- `weekly` - Rotates logs every week
- `rotate 8` - Keeps 8 weeks of history (2 months)
- `compress` - Compresses old logs to save space
- `delaycompress` - Doesn't compress the most recent rotated log
- `missingok` - No error if log file is missing
- `notifempty` - Doesn't rotate empty files
- `create 0644 guillain guillain` - Creates new log file with correct permissions

**Save:** Ctrl+X, Y, Enter

---

### Step 2.2: Limit systemd journal size

```bash
sudo nano /etc/systemd/journald.conf
```

**Find the `[Journal]` section and modify (or add if missing):**

```ini
[Journal]
SystemMaxUse=500M
RuntimeMaxUse=100M
```

**What this does:**
- Limits system journal to 500MB maximum
- Limits runtime journal to 100MB maximum
- Prevents journal from filling your disk

**Save and restart:**
```bash
sudo systemctl restart systemd-journald
```

---

### Step 2.3: Clean old logs NOW

```bash
# Clean journal logs older than 30 days
sudo journalctl --vacuum-time=30d

# Clean old Apache logs (if any)
sudo find /var/log/apache2/ -name "*.gz" -mtime +60 -delete 2>/dev/null

# Check reclaimed space
df -h /
```

**Expected:** Should free up 100MB-1GB depending on system uptime

---

### Step 2.4: Test log rotation

```bash
# Test the configuration (dry run)
sudo logrotate -d /etc/logrotate.d/prometheus
```

**Expected output:**
```
rotating pattern: /var/log/prometheus/*.log  weekly (8 rotations)
empty log files are not rotated, old logs are removed
```

---

## 📝 Part 3: ZIM Inventory System (15 minutes)

### Step 3.1: Create ZIM version tracker

```bash
nano ~/list-zim-versions.sh
```

**Paste this script:**

```bash
#!/bin/bash
# List all ZIM files with versions and dates

echo "╔════════════════════════════════════════════════════════╗"
echo "║     INSTALLED ZIM FILES                                ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

cd /var/kiwix/data 2>/dev/null || {
    echo "Error: /var/kiwix/data not found"
    exit 1
}

for zim in *.zim; do
    if [ -f "$zim" ]; then
        SIZE=$(du -h "$zim" | cut -f1)
        MODIFIED=$(stat -c %y "$zim" | cut -d' ' -f1)
        
        # Extract version from filename if present
        VERSION=$(echo "$zim" | grep -oP '\d{4}-\d{2}' || echo "unknown")
        
        echo "File: $zim"
        echo "  Size: $SIZE"
        echo "  Version: $VERSION"
        echo "  Modified: $MODIFIED"
        echo ""
    fi
done

echo "Total ZIM files: $(ls -1 *.zim 2>/dev/null | wc -l)"
echo "Total storage: $(du -sh . | cut -f1)"
```

**Save and make executable:**
```bash
chmod +x ~/list-zim-versions.sh
```

---

### Step 3.2: Test the inventory

```bash
~/list-zim-versions.sh
```

**Expected output:**
```
╔════════════════════════════════════════════════════════╗
║     INSTALLED ZIM FILES                                ║
╚════════════════════════════════════════════════════════╝

File: mdwiki_en_all_maxi_2025-11.zim
  Size: 2.2G
  Version: 2025-11
  Modified: 2025-11-13

File: wikipedia_en_all_maxi_2025-08.zim
  Size: 112G
  Version: 2025-08
  Modified: 2025-08-24

[... other files ...]

Total ZIM files: 7
Total storage: 166G
```

**This tells you:**
- Which files you have
- How old they are
- Which ones might need updating

---

## 💾 Part 4: Backup & Restore System (25 minutes)

### Step 4.1: Create configuration backup script

```bash
nano ~/backup-config.sh
```

**Paste this COMPLETE script:**

```bash
#!/bin/bash
# Prometheus Station - Configuration Backup
# Backs up config files (NOT ZIM files - too large)

set -e

BACKUP_DIR="/var/backups/prometheus/configs"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
BACKUP_FILE="prometheus-config-$TIMESTAMP.tar.gz"

echo "╔════════════════════════════════════════════════════════╗"
echo "║     CONFIGURATION BACKUP                               ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# Create backup directory
sudo mkdir -p "$BACKUP_DIR"

echo "Creating backup: $BACKUP_FILE"
echo ""

# What to backup
FILES_TO_BACKUP=(
    "/etc/systemd/system/kiwix-serve.service"
    "/etc/apache2/sites-available/prometheus.conf"
    "/etc/hostapd/hostapd.conf"
    "/etc/dnsmasq.conf"
    "/var/www/html/index.html"
    "/var/www/html/status.php"
    "/var/www/html/connect.html"
    "/home/$USER/.ssh/authorized_keys"
)

# Add all .sh scripts separately (wildcard fix)
for script in /home/$USER/*.sh; do
    if [ -f "$script" ]; then
        FILES_TO_BACKUP+=("$script")
    fi
done

# Create temp directory for staging
TEMP_DIR=$(mktemp -d)

# Copy files preserving directory structure
for file in "${FILES_TO_BACKUP[@]}"; do
    if [ -e "$file" ]; then
        # Create parent directory in temp
        DIR=$(dirname "$file")
        mkdir -p "$TEMP_DIR$DIR"
        
        # Copy file
        if [ -d "$file" ]; then
            cp -r "$file" "$TEMP_DIR$DIR/"
        else
            cp "$file" "$TEMP_DIR$DIR/"
        fi
        
        echo "✓ $(basename $file)"
    else
        echo "⚠ Skipped (not found): $file"
    fi
done

# Create ZIM file list (not the files themselves)
echo "Creating ZIM inventory..."
ls -lh /var/kiwix/data/*.zim > "$TEMP_DIR/zim-inventory.txt" 2>/dev/null || true

# Add system info
{
    echo "=== System Info ==="
    uname -a
    echo ""
    echo "=== Backup Date ==="
    date
    echo ""
    echo "=== Installed Packages ==="
    dpkg -l | grep -E 'kiwix|apache|hostapd|dnsmasq'
} > "$TEMP_DIR/system-info.txt"

# Create tarball
cd "$TEMP_DIR"
sudo tar -czf "$BACKUP_DIR/$BACKUP_FILE" .

# Cleanup
cd /
rm -rf "$TEMP_DIR"

echo ""
echo "✓ Backup created: $BACKUP_DIR/$BACKUP_FILE"

# Show backup size
SIZE=$(du -h "$BACKUP_DIR/$BACKUP_FILE" | cut -f1)
echo "  Size: $SIZE"

# List all backups
echo ""
echo "All configuration backups:"
ls -lh "$BACKUP_DIR" | tail -5

# Delete backups older than 30 days
OLD_BACKUPS=$(find "$BACKUP_DIR" -name "*.tar.gz" -mtime +30 2>/dev/null | wc -l)
if [ $OLD_BACKUPS -gt 0 ]; then
    echo ""
    echo "Cleaning up $OLD_BACKUPS backup(s) older than 30 days..."
    find "$BACKUP_DIR" -name "*.tar.gz" -mtime +30 -delete
fi

echo ""
echo "To restore: tar -xzf $BACKUP_DIR/$BACKUP_FILE -C /"
echo ""
```

**Save and make executable:**
```bash
chmod +x ~/backup-config.sh
```

---

### Step 4.2: Create restore script

```bash
nano ~/restore-config.sh
```

**Paste:**

```bash
#!/bin/bash
# Prometheus Station - Configuration Restore

set -e

BACKUP_DIR="/var/backups/prometheus/configs"

echo "╔════════════════════════════════════════════════════════╗"
echo "║     CONFIGURATION RESTORE                              ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# List available backups
echo "Available backups:"
ls -lht "$BACKUP_DIR"/*.tar.gz 2>/dev/null | nl

echo ""
read -p "Enter backup number to restore (or 'cancel'): " BACKUP_NUM

if [ "$BACKUP_NUM" = "cancel" ]; then
    echo "Restore cancelled."
    exit 0
fi

# Get backup file
BACKUP_FILE=$(ls -t "$BACKUP_DIR"/*.tar.gz | sed -n "${BACKUP_NUM}p")

if [ -z "$BACKUP_FILE" ]; then
    echo "Invalid selection."
    exit 1
fi

echo ""
echo "Selected: $(basename $BACKUP_FILE)"
echo ""
echo "⚠ WARNING: This will overwrite current configuration!"
echo ""
read -p "Continue? (type 'yes' to confirm): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo "Restore cancelled."
    exit 0
fi

# Extract backup
echo "Restoring configuration..."
sudo tar -xzf "$BACKUP_FILE" -C /

echo ""
echo "✓ Configuration restored"
echo ""
echo "You should now:"
echo "  1. Verify services: sudo systemctl status kiwix-serve apache2"
echo "  2. Restart services: sudo systemctl restart kiwix-serve apache2"
echo "  3. Test access: http://prometheus-station.local"
echo ""
```

**Save and make executable:**
```bash
chmod +x ~/restore-config.sh
```

---

### Step 4.3: Test backup

```bash
~/backup-config.sh
```

**Expected output:**
```
╔════════════════════════════════════════════════════════╗
║     CONFIGURATION BACKUP                               ║
╚════════════════════════════════════════════════════════╝

Creating backup: prometheus-config-20251231-123456.tar.gz

✓ kiwix-serve.service
✓ prometheus.conf
✓ hostapd.conf
✓ dnsmasq.conf
✓ index.html
✓ status.php
✓ connect.html
✓ authorized_keys
✓ health-check.sh
✓ backup-config.sh
✓ list-zim-versions.sh
[... all your scripts ...]
Creating ZIM inventory...

✓ Backup created: /var/backups/prometheus/configs/prometheus-config-20251231-123456.tar.gz
  Size: 24K
```

**Verify the backup:**
```bash
# List contents
tar -tzf /var/backups/prometheus/configs/prometheus-config-*.tar.gz | head -20

# Test extraction to temp directory
mkdir -p ~/restore-test
tar -xzf /var/backups/prometheus/configs/prometheus-config-*.tar.gz -C ~/restore-test
ls -R ~/restore-test
rm -rf ~/restore-test
```

---

## 📧 Part 5: Automated Alert System (20 minutes)

### Step 5.1: Create alert checker script

```bash
nano ~/check-alerts.sh
```

**Paste this script:**

```bash
#!/bin/bash
# Prometheus Station - Alert Checker
# Run this regularly to catch problems early

ALERT_LOG="/var/log/prometheus/alerts.log"
ALERT_TRIGGERED=false

log_alert() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ALERT: $1" | tee -a "$ALERT_LOG"
    ALERT_TRIGGERED=true
}

# Temperature check
TEMP=$(vcgencmd measure_temp | cut -d'=' -f2 | cut -d"'" -f1)
if (( $(echo "$TEMP > 70" | bc -l) )); then
    log_alert "High temperature: ${TEMP}°C"
fi

# Disk space check
DISK_USED=$(df / | awk 'NR==2{print $5}' | tr -d '%')
if [ $DISK_USED -gt 90 ]; then
    log_alert "Disk nearly full: ${DISK_USED}% used"
fi

# Service checks
SERVICES="kiwix-serve apache2 ssh"
for service in $SERVICES; do
    if ! systemctl is-active --quiet $service; then
        log_alert "Service down: $service"
    fi
done

# Memory check
MEM_PERCENT=$(free | awk 'NR==2{printf "%.0f", ($3/$2)*100}')
if [ $MEM_PERCENT -gt 90 ]; then
    log_alert "High memory usage: ${MEM_PERCENT}%"
fi

# Failed logins
FAILED=$(grep "Failed password" /var/log/auth.log 2>/dev/null | tail -10 | wc -l)
if [ $FAILED -gt 5 ]; then
    log_alert "Multiple failed login attempts: $FAILED in last 10 lines"
fi

# If any alerts triggered, display them
if [ "$ALERT_TRIGGERED" = true ]; then
    echo "⚠ ALERTS DETECTED - Check $ALERT_LOG"
    tail -10 "$ALERT_LOG"
    exit 1
else
    echo "✓ No alerts - system healthy"
    exit 0
fi
```

**Save and make executable:**
```bash
chmod +x ~/check-alerts.sh
```

---

### Step 5.2: Test the alert system

```bash
~/check-alerts.sh
```

**Expected output:**
```
✓ No alerts - system healthy
```

**If you see alerts:** Investigate and fix the issues before automating.

---

## ⏰ Part 6: Automation with Cron (15 minutes)

### Step 6.1: Create log directory

```bash
sudo mkdir -p /var/log/prometheus
sudo chown $USER:$USER /var/log/prometheus
```

---

### Step 6.2: Configure cron jobs

```bash
crontab -e
```

**If this is your first time, select editor:**
- Choose `1` for nano (easiest)

**Add these lines AT THE END:**

```bash
# Prometheus Station - Automated Maintenance

# Daily health check at 3 AM
0 3 * * * /home/guillain/health-check.sh >> /var/log/prometheus/health-$(date +\%Y-\%m).log 2>&1

# Weekly config backup on Sunday at 2 AM
0 2 * * 0 /home/guillain/backup-config.sh >> /var/log/prometheus/backup.log 2>&1

# Alert check every 6 hours
0 */6 * * * /home/guillain/check-alerts.sh 2>&1 | grep -q "ALERT" && echo "$(date): Alerts detected" >> /var/log/prometheus/alerts.log
```

**Important notes:**
- Replace `guillain` with YOUR username if different
- The `\%` is needed in crontab (escapes the % character)
- Each task runs automatically at scheduled time

**Save:** Ctrl+X, Y, Enter

---

### Step 6.3: Verify cron configuration

```bash
# List your cron jobs
crontab -l

# Test that logging works
~/health-check.sh >> /var/log/prometheus/health-test.log 2>&1

# Check the log was created
ls -lh /var/log/prometheus/
cat /var/log/prometheus/health-test.log
```

**Expected:** Should see complete health report in the log file.

---

### Step 6.4: Understanding the automation

**What will happen automatically:**

**Every day at 3:00 AM:**
- Health check runs
- Results logged to `/var/log/prometheus/health-YYYY-MM.log`
- One log file per month (automatic)

**Every Sunday at 2:00 AM:**
- Configuration backup created
- Stored in `/var/backups/prometheus/configs/`
- Old backups (>30 days) automatically deleted

**Every 6 hours (0:00, 6:00, 12:00, 18:00):**
- Alert check runs
- Only logs if problems detected
- Check `/var/log/prometheus/alerts.log` for issues

---

## 🔄 Part 7: ZIM Update System (Optional)

**This part is optional but recommended when you want to update your content.**

### Step 7.1: Create ZIM update script

```bash
nano ~/update-zim-files.sh
```

**Paste this script:**

```bash
#!/bin/bash
# Prometheus Station - ZIM Update Manager
# Safely download and replace ZIM files

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
ZIM_DIR="/var/kiwix/data"
TEMP_DIR="/var/kiwix/temp"
BACKUP_DIR="/var/backups/prometheus/zim-backups"
LOG_FILE="/var/log/prometheus/zim-updates.log"

# Create directories
sudo mkdir -p "$TEMP_DIR" "$BACKUP_DIR"
sudo chown $USER:$USER "$TEMP_DIR" "$BACKUP_DIR"

# Logging function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     PROMETHEUS STATION - ZIM UPDATE MANAGER           ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
echo ""

log "Starting ZIM update check"

# ============================================
# Check current ZIM files
# ============================================
echo -e "${YELLOW}[1/5] Scanning current ZIM files...${NC}"

cd "$ZIM_DIR"
for zim in *.zim; do
    if [ -f "$zim" ]; then
        SIZE=$(du -h "$zim" | cut -f1)
        DATE=$(stat -c %y "$zim" | cut -d' ' -f1)
        echo "  $zim ($SIZE, modified: $DATE)"
    fi
done

echo ""
read -p "Do you want to check for updates? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Update cancelled."
    exit 0
fi

# ============================================
# List available updates
# ============================================
echo -e "${YELLOW}[2/5] Checking Kiwix library for updates...${NC}"
echo ""
echo "Visit these URLs to check for newer versions:"
echo ""
echo "  Medical Content:"
echo "  https://download.kiwix.org/zim/other/"
echo ""
echo "  Wikipedia:"
echo "  https://download.kiwix.org/zim/wikipedia/"
echo ""
echo "Look for files with newer dates (YYYY-MM format in filename)"
echo ""

read -p "Enter URL of ZIM file to download (or 'skip'): " ZIM_URL

if [ "$ZIM_URL" = "skip" ]; then
    echo "No updates selected."
    exit 0
fi

# ============================================
# Download new ZIM
# ============================================
echo -e "${YELLOW}[3/5] Downloading new ZIM file...${NC}"

ZIM_FILENAME=$(basename "$ZIM_URL")
echo "Downloading: $ZIM_FILENAME"
echo "To: $TEMP_DIR/"

cd "$TEMP_DIR"

# Download with resume capability
wget -c "$ZIM_URL"

if [ $? -ne 0 ]; then
    echo -e "${RED}✗ Download failed!${NC}"
    log "ERROR: Download failed for $ZIM_URL"
    exit 1
fi

echo -e "${GREEN}✓ Download complete${NC}"
log "Downloaded: $ZIM_FILENAME"

# ============================================
# Verify integrity
# ============================================
echo -e "${YELLOW}[4/5] Verifying file integrity...${NC}"

# Check file size is reasonable
SIZE=$(stat -c%s "$ZIM_FILENAME")
if [ $SIZE -lt 1000000 ]; then
    echo -e "${RED}✗ File too small ($SIZE bytes) - likely corrupted${NC}"
    rm "$ZIM_FILENAME"
    exit 1
fi

# Test with zimdump (if available)
if command -v zimdump &> /dev/null; then
    zimdump info "$ZIM_FILENAME" > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ File integrity verified${NC}"
    else
        echo -e "${RED}✗ File appears corrupted${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}⚠ zimdump not available, skipping verification${NC}"
fi

# ============================================
# Install new ZIM
# ============================================
echo -e "${YELLOW}[5/5] Installing new ZIM file...${NC}"

# Check if replacing existing file
EXISTING_BASE=$(echo "$ZIM_FILENAME" | sed 's/_[0-9]\{4\}-[0-9]\{2\}\.zim/.zim/')
OLD_FILE=$(ls "$ZIM_DIR"/$EXISTING_BASE* 2>/dev/null | head -1)

if [ -n "$OLD_FILE" ]; then
    echo "Found old version: $(basename $OLD_FILE)"
    
    # Backup old file
    OLD_BASENAME=$(basename "$OLD_FILE")
    echo "Backing up to: $BACKUP_DIR/$OLD_BASENAME"
    sudo cp "$OLD_FILE" "$BACKUP_DIR/"
    
    # Remove old file
    echo "Removing old version..."
    sudo rm "$OLD_FILE"
    
    log "Replaced: $OLD_BASENAME with $ZIM_FILENAME"
else
    log "New file: $ZIM_FILENAME"
fi

# Move new file to ZIM directory
echo "Installing new file..."
sudo mv "$ZIM_FILENAME" "$ZIM_DIR/"
sudo chown $USER:$USER "$ZIM_DIR/$ZIM_FILENAME"

echo -e "${GREEN}✓ Installation complete${NC}"

# ============================================
# Update Kiwix service
# ============================================
echo ""
echo -e "${YELLOW}Updating Kiwix configuration...${NC}"

echo ""
echo -e "${RED}IMPORTANT:${NC} You must update the Kiwix service file:"
echo ""
echo "  sudo nano /etc/systemd/system/kiwix-serve.service"
echo ""
echo "Update the ExecStart line to include:"
echo "  /var/kiwix/data/$ZIM_FILENAME"
echo ""
if [ -n "$OLD_FILE" ]; then
    echo "And remove the old file:"
    echo "  /var/kiwix/data/$(basename $OLD_FILE)"
    echo ""
fi
echo "Then restart Kiwix:"
echo "  sudo systemctl daemon-reload"
echo "  sudo systemctl restart kiwix-serve"
echo ""

read -p "Press Enter when you've updated the service file..." 

# Restart Kiwix
sudo systemctl daemon-reload
sudo systemctl restart kiwix-serve

# Verify Kiwix started
sleep 3
if systemctl is-active --quiet kiwix-serve; then
    echo -e "${GREEN}✓ Kiwix restarted successfully${NC}"
    log "Kiwix restarted with updated content"
else
    echo -e "${RED}✗ Kiwix failed to start - check logs${NC}"
    log "ERROR: Kiwix failed to restart"
    exit 1
fi

# ============================================
# Summary
# ============================================
echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     UPDATE COMPLETE                                    ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "New ZIM file: $ZIM_FILENAME"
echo "Location: $ZIM_DIR/"
if [ -n "$OLD_FILE" ]; then
    echo "Old backup: $BACKUP_DIR/$(basename $OLD_FILE)"
fi
echo ""
echo "Test access: http://prometheus-station.local"
echo ""

log "ZIM update completed successfully"
```

**Save and make executable:**
```bash
chmod +x ~/update-zim-files.sh
```

**Note:** This script is for manual use when you want to update content. You'll use it when `list-zim-versions.sh` shows old files.

---

## 📅 Part 8: Monthly Maintenance Checklist (10 minutes)

### Step 8.1: Create maintenance checklist script

```bash
nano ~/monthly-maintenance.sh
```

**Paste:**

```bash
#!/bin/bash
# Prometheus Station - Monthly Maintenance Checklist

echo "╔════════════════════════════════════════════════════════╗"
echo "║     MONTHLY MAINTENANCE CHECKLIST                      ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""
echo "Run these tasks once per month:"
echo ""

echo "☐ 1. System Health Check"
echo "   Run: ~/health-check.sh"
echo ""

echo "☐ 2. Review Health Logs"
echo "   Check: cat /var/log/prometheus/health-$(date +%Y-%m).log | tail -100"
echo ""

echo "☐ 3. Check ZIM Updates"
echo "   Run: ~/list-zim-versions.sh"
echo "   Visit: https://download.kiwix.org/zim/"
echo "   Update if newer versions available: ~/update-zim-files.sh"
echo ""

echo "☐ 4. Verify Backups"
echo "   Check: ls -lh /var/backups/prometheus/configs/"
echo "   Should have recent backups"
echo ""

echo "☐ 5. Check Alerts Log"
echo "   Review: cat /var/log/prometheus/alerts.log"
echo "   Should be mostly empty (only issues logged)"
echo ""

echo "☐ 6. Log Cleanup Check"
echo "   Size: du -sh /var/log"
echo "   Clean if >1GB: sudo journalctl --vacuum-size=500M"
echo ""

echo "☐ 7. Disk Space Review"
echo "   Check: df -h /"
echo "   Should have >20GB free"
echo ""

echo "☐ 8. Temperature Check"
echo "   Max temp: grep Temperature /var/log/prometheus/health-*.log | sort | tail -10"
echo "   Should stay under 60°C"
echo ""

echo "☐ 9. Test Functionality"
echo "   WiFi hotspot: Test connection"
echo "   Web access: http://prometheus-station.local"
echo "   Search: Test article search in Kiwix"
echo ""

echo "☐ 10. Update Documentation"
echo "   Note any issues in: /var/log/prometheus/maintenance-notes.txt"
echo ""

echo "════════════════════════════════════════════════════════"
echo ""
echo "Estimated time: 30-45 minutes"
echo ""

# Record completion
read -p "Mark this checklist as complete? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "[$(date)] Monthly maintenance completed" >> /var/log/prometheus/maintenance-notes.txt
    echo "✓ Recorded in maintenance log"
fi
```

**Save and make executable:**
```bash
chmod +x ~/monthly-maintenance.sh
```

---

### Step 8.2: Create maintenance notes file

```bash
touch /var/log/prometheus/maintenance-notes.txt
echo "=== Prometheus Station Maintenance Log ===" > /var/log/prometheus/maintenance-notes.txt
echo "" >> /var/log/prometheus/maintenance-notes.txt
echo "Started: $(date)" >> /var/log/prometheus/maintenance-notes.txt
echo "" >> /var/log/prometheus/maintenance-notes.txt
```

---

## ✅ Part 9: Final Testing & Verification (15 minutes)

### Step 9.1: Test all scripts

**Test each script once:**

```bash
# 1. Health check
~/health-check.sh

# 2. List ZIM versions
~/list-zim-versions.sh

# 3. Backup configuration
~/backup-config.sh

# 4. Check alerts
~/check-alerts.sh

# 5. Monthly checklist (just display it)
~/monthly-maintenance.sh
```

**All should run without errors.**

---

### Step 9.2: Verify automation

```bash
# Check cron jobs are configured
crontab -l

# Should show 3 tasks:
# - Daily health check (3 AM)
# - Weekly backup (Sunday 2 AM)
# - Alert check (every 6 hours)
```

---

### Step 9.3: Verify log rotation

```bash
# Test logrotate configuration
sudo logrotate -d /etc/logrotate.d/prometheus

# Check systemd journal limits
grep -E "^SystemMaxUse|^RuntimeMaxUse" /etc/systemd/journald.conf

# Should show:
# SystemMaxUse=500M
# RuntimeMaxUse=100M
```

---

### Step 9.4: Complete system check

```bash
echo "=== FINAL VERIFICATION ==="
echo ""
echo "1. Cron Jobs:"
crontab -l | grep -v "^#" | grep -v "^$"
echo ""
echo "2. Log Directory:"
ls -lh /var/log/prometheus/
echo ""
echo "3. Backups:"
ls -lh /var/backups/prometheus/configs/ | tail -3
echo ""
echo "4. Disk Space:"
df -h / | tail -1
echo ""
echo "5. Services:"
systemctl is-active kiwix-serve apache2 ssh && echo "All critical services: ✓ Running"
echo ""
echo "6. Firewall:"
sudo ufw status | grep "Status:"
echo ""
echo "=== VERIFICATION COMPLETE ==="
```

---

## ✅ Verification Checklist

Go through each item to confirm everything works:

### Installation
- [ ] bc installed: `bc --version` shows version
- [ ] UFW installed and configured: `sudo ufw status` shows active
- [ ] All ports allowed: 22, 80, 8080, tailscale0

### Scripts Created & Tested
- [ ] `health-check.sh` runs without errors
- [ ] `list-zim-versions.sh` shows all ZIM files
- [ ] `backup-config.sh` creates backup successfully
- [ ] `check-alerts.sh` reports "No alerts"
- [ ] `monthly-maintenance.sh` displays checklist

### Log Management
- [ ] `/etc/logrotate.d/prometheus` exists
- [ ] systemd journal limited to 500M
- [ ] `/var/log/prometheus/` directory exists

### Automation
- [ ] Cron jobs configured: `crontab -l` shows 3 tasks
- [ ] Health check at 3 AM
- [ ] Backup on Sunday at 2 AM
- [ ] Alert check every 6 hours

### Verification Tests
- [ ] Manual health check logged: `/var/log/prometheus/health-test.log` exists
- [ ] Backup file created: `/var/backups/prometheus/configs/` has files
- [ ] No critical alerts: `~/check-alerts.sh` returns OK

---

## 📊 What You've Accomplished

**Automated Systems:**
✅ Daily health monitoring (3 AM)  
✅ Weekly configuration backups (Sunday 2 AM)  
✅ Regular alert checking (every 6 hours)  
✅ Automatic log rotation (weekly)  
✅ Automatic cleanup (old logs, old backups)  

**Manual Tools:**
✅ ZIM version inventory  
✅ ZIM update system  
✅ Configuration restore  
✅ Monthly maintenance checklist  

**Your Prometheus Station is now:**
- Self-monitoring
- Self-backing-up
- Self-alerting
- Self-cleaning
- Low maintenance!

---

## 🛠️ Troubleshooting

### Health check shows errors

**"bc: command not found"**
```bash
sudo apt install -y bc
```

**"ufw: command not found"**
```bash
sudo apt install -y ufw
# Then configure as shown in Part 0
```

**High temperature warning**
- Add heatsink/fan
- Improve ventilation
- Check for dust

**High disk usage**
```bash
# Clean logs
sudo journalctl --vacuum-size=500M

# Check what's using space
sudo du -h --max-depth=1 / | sort -hr | head -10
```

---

### Cron jobs not running

**Check cron service:**
```bash
sudo systemctl status cron
```

**Check cron logs:**
```bash
grep CRON /var/log/syslog | tail -20
```

**Verify crontab syntax:**
```bash
crontab -l
# Should have exactly 3 task lines
```

---

### Backup fails

**Permission issues:**
```bash
sudo chown -R $USER:$USER /var/backups/prometheus
```

**Directory doesn't exist:**
```bash
sudo mkdir -p /var/backups/prometheus/configs
sudo chown $USER:$USER /var/backups/prometheus/configs
```

---

## 📅 Maintenance Schedule

### Daily (Automated)
- Health check runs at 3 AM
- Review only if you see issues

### Weekly (Automated)
- Configuration backup on Sunday 2 AM
- No action needed

### Monthly (Manual - 30-45 min)
```bash
~/monthly-maintenance.sh
```

Follow the checklist step by step.

### Quarterly
- Review ZIM file versions
- Update old content if needed
- Check system updates

### Yearly
- Full system audit
- Consider SD card replacement (preventive)
- Update documentation

---

## 💡 Pro Tips

### Create command aliases

Add to `~/.bashrc`:

```bash
echo "# Prometheus Station aliases" >> ~/.bashrc
echo "alias health='~/health-check.sh'" >> ~/.bashrc
echo "alias zimlist='~/list-zim-versions.sh'" >> ~/.bashrc
echo "alias backup='~/backup-config.sh'" >> ~/.bashrc
echo "alias maint='~/monthly-maintenance.sh'" >> ~/.bashrc
source ~/.bashrc
```

Now just type `health` instead of `~/health-check.sh`!

---

### Quick service restart

```bash
nano ~/restart-all.sh
```

```bash
#!/bin/bash
sudo systemctl restart kiwix-serve apache2
echo "All services restarted"
```

```bash
chmod +x ~/restart-all.sh
```

---

### Monitor in real-time

```bash
watch -n 60 -c ~/health-check.sh
```

Live updating dashboard every 60 seconds!

---

## 🎓 What You've Learned

**Skills gained:**
- System monitoring automation
- Log management and rotation
- Backup/restore strategies
- Cron job scheduling
- Alert system configuration
- Maintenance best practices
- Troubleshooting methodology

**These skills transfer to:**
- Any Raspberry Pi project
- Linux server administration
- System maintenance in general
- IT infrastructure management

---

## 📚 Quick Command Reference

```bash
# Health & Monitoring
~/health-check.sh                    # Full system health report
~/check-alerts.sh                    # Check for critical issues
~/list-zim-versions.sh               # Show ZIM file inventory

# Maintenance
~/backup-config.sh                   # Backup configuration
~/monthly-maintenance.sh             # Monthly checklist
~/update-zim-files.sh               # Update ZIM content

# Logs
tail -f /var/log/prometheus/health-$(date +%Y-%m).log   # Watch health logs
cat /var/log/prometheus/alerts.log                      # View alerts
sudo journalctl -u kiwix-serve -f                       # Watch Kiwix logs

# System
df -h /                              # Check disk space
free -h                              # Check memory
vcgencmd measure_temp                # Check temperature
systemctl status kiwix-serve         # Check Kiwix status

# Cron
crontab -l                           # List cron jobs
crontab -e                           # Edit cron jobs

# Cleanup
sudo journalctl --vacuum-size=500M   # Clean system logs
sudo apt clean                       # Clean package cache
```

---

## 🎯 Next Steps

**Your maintenance system is complete!** 

**Option A:** Continue with additional features
- Meshtastic LoRa network (long-range communication)
- Solar power integration
- E-Ink status display

**Option B:** Deploy to the field
- Test 24-48 hours continuously
- Switch to hotspot mode
- Verify everything works offline
- Document any issues in maintenance log

**Option C:** Optimize further
- Fine-tune alert thresholds
- Add custom monitoring
- Create additional automation

---

## 📖 Additional Resources

### Official Documentation
- [Cron HowTo](https://help.ubuntu.com/community/CronHowto)
- [Logrotate](https://linux.die.net/man/8/logrotate)
- [Systemd Journal](https://www.freedesktop.org/software/systemd/man/journald.conf.html)

### Community
- [Prometheus Station GitHub](https://github.com/GuillainM/Prometheus-Station)
- [r/raspberry_pi](https://reddit.com/r/raspberry_pi)

---

## ⏱️ Time Breakdown

**From tested real-world setup:**

| Phase | Time | Notes |
|-------|------|-------|
| Part 0: Install tools | 5 min | bc + UFW |
| Part 1: Health dashboard | 30 min | Script creation + testing |
| Part 2: Log management | 20 min | Configuration |
| Part 3: ZIM inventory | 15 min | List versions |
| Part 4: Backup system | 25 min | Both scripts + testing |
| Part 5: Alert system | 20 min | Script + testing |
| Part 6: Cron automation | 15 min | Setup + verification |
| Part 7: ZIM updates | 40 min | Script (use as needed) |
| Part 8: Maintenance checklist | 10 min | Documentation |
| Part 9: Final testing | 15 min | Complete verification |
| **TOTAL SETUP** | **3h 15min** | One-time configuration |

**Monthly maintenance:** 30-45 minutes

---

**Last updated:** December 31, 2025  
**Tested on:** Raspberry Pi 4 8GB, Raspberry Pi OS Lite (64-bit)  
**All scripts tested:** ✅ Verified working  
**Real-world deployment:** 6+ months continuous operation  

---

*Made with 🔥 for Prometheus Station - Tested, debugged, and perfected through real-world use!*
