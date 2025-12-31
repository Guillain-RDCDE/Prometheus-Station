# Step 5: System Maintenance & Updates

**Goal:** Establish maintenance routines to keep Prometheus Station healthy, secure, and up-to-date.

**Time Required:** 
- Initial setup: 2 hours
- Monthly maintenance: 30-45 minutes
- ZIM updates: 2-6 hours (mostly downloading)

**Difficulty:** ⭐⭐⭐ Medium (systematic procedures, nothing complex)

**💡 Real experience:** A well-maintained station runs for months without issues. Neglect maintenance and you'll face corrupted files, full disks, and mysterious crashes.

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
1. ✅ Create health monitoring dashboard
2. ✅ Setup automated log rotation
3. ✅ Build ZIM update system
4. ✅ Configure system update procedures
5. ✅ Create backup/restore scripts
6. ✅ Setup automated alerts
7. ✅ Build monthly maintenance checklist

**What you'll have at the end:**
- Automated health checks
- Safe update procedures
- Content update workflow
- Emergency recovery tools
- Maintenance calendar

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
sudo ufw status | grep -q "Status: active"
check_status $? "Firewall (UFW)"

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

---

### Step 1.3: Schedule daily health checks

```bash
# Create log directory
sudo mkdir -p /var/log/prometheus
sudo chown $USER:$USER /var/log/prometheus

# Add to crontab
crontab -e
```

**Add this line at the end:**
```
# Daily health check at 3 AM
0 3 * * * /home/guillain/health-check.sh >> /var/log/prometheus/health-$(date +\%Y-\%m).log 2>&1
```

**What this does:**
- Runs health check every day at 3 AM
- Logs output to monthly file
- Keeps history for troubleshooting

**Save and exit:** ESC, :wq, Enter (if vim) or Ctrl+X, Y, Enter (if nano)

---

## 🗂️ Part 2: Log Management (20 minutes)

### Step 2.1: Configure log rotation

**Create rotation config for Prometheus logs:**

```bash
sudo nano /etc/logrotate.d/prometheus
```

**Paste:**

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
- Rotates logs weekly
- Keeps 8 weeks of history
- Compresses old logs
- Creates new log files with correct permissions

**Save:** Ctrl+X, Y, Enter

---

### Step 2.2: Limit journal size

```bash
sudo nano /etc/systemd/journald.conf
```

**Find and modify these lines:**

```ini
[Journal]
SystemMaxUse=500M
RuntimeMaxUse=100M
```

**What this does:**
- Limits systemd journal to 500MB
- Prevents logs from filling disk

**Save and restart:**
```bash
sudo systemctl restart systemd-journald
```

---

### Step 2.3: Clean old logs now

```bash
# Clean journal logs older than 30 days
sudo journalctl --vacuum-time=30d

# Clean old Apache logs
sudo find /var/log/apache2/ -name "*.gz" -mtime +60 -delete

# Check reclaimed space
df -h /
```

**Expected:** Should free up 100MB-1GB depending on uptime

---

## 🔄 Part 3: ZIM File Updates (40 minutes setup)

### Step 3.1: Create ZIM update script

```bash
nano ~/update-zim-files.sh
```

**Paste this COMPLETE script:**

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

# Test with zimdump
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

# You need to manually update the systemd service file
echo ""
echo -e "${RED}IMPORTANT:${NC} You must update the Kiwix service file:"
echo ""
echo "  sudo nano /etc/systemd/system/kiwix-serve.service"
echo ""
echo "Update the ExecStart line to include:"
echo "  /var/kiwix/data/$ZIM_FILENAME"
echo ""
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

**Save:** Ctrl+X, Y, Enter

**Make executable:**
```bash
chmod +x ~/update-zim-files.sh
```

---

### Step 3.2: Create ZIM version tracker

```bash
nano ~/list-zim-versions.sh
```

**Paste:**

```bash
#!/bin/bash
# List all ZIM files with versions and dates

echo "╔════════════════════════════════════════════════════════╗"
echo "║     INSTALLED ZIM FILES                                ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

cd /var/kiwix/data

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

## 🔧 Part 4: System Updates (30 minutes)

### Step 4.1: Create safe update script

```bash
nano ~/safe-system-update.sh
```

**Paste:**

```bash
#!/bin/bash
# Prometheus Station - Safe System Update
# Updates OS packages with safety checks

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

LOG_FILE="/var/log/prometheus/system-updates.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     SYSTEM UPDATE - SAFETY PROCEDURE                  ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
echo ""

log "Starting safe system update"

# ============================================
# Pre-update checks
# ============================================
echo -e "${YELLOW}[1/6] Pre-update safety checks...${NC}"

# Check disk space
DISK_FREE=$(df / | awk 'NR==2{print $4}')
if [ $DISK_FREE -lt 1000000 ]; then
    echo -e "${RED}✗ Insufficient disk space (less than 1GB free)${NC}"
    echo "Free up space before updating"
    exit 1
fi
echo -e "${GREEN}✓ Disk space: OK${NC}"

# Check internet
if ! ping -c 1 8.8.8.8 &> /dev/null; then
    echo -e "${RED}✗ No internet connection${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Internet: OK${NC}"

# Check critical services
CRITICAL_SERVICES="kiwix-serve apache2 ssh"
for service in $CRITICAL_SERVICES; do
    if ! systemctl is-active --quiet $service; then
        echo -e "${YELLOW}⚠ Warning: $service is not running${NC}"
    fi
done

echo ""

# ============================================
# Backup current state
# ============================================
echo -e "${YELLOW}[2/6] Creating backup marker...${NC}"

BACKUP_FILE="/var/backups/prometheus/pre-update-$(date +%Y%m%d-%H%M%S).txt"
sudo mkdir -p /var/backups/prometheus

{
    echo "System state before update: $(date)"
    echo ""
    echo "=== Installed packages ==="
    dpkg -l
    echo ""
    echo "=== Critical services ==="
    systemctl status kiwix-serve apache2 ssh --no-pager
} | sudo tee "$BACKUP_FILE" > /dev/null

echo -e "${GREEN}✓ Backup marker created: $BACKUP_FILE${NC}"
log "Created backup marker: $BACKUP_FILE"

echo ""

# ============================================
# Update package lists
# ============================================
echo -e "${YELLOW}[3/6] Updating package lists...${NC}"

sudo apt update

UPDATES=$(apt list --upgradable 2>/dev/null | grep upgradable | wc -l)
echo "Updates available: $UPDATES packages"

if [ $UPDATES -eq 0 ]; then
    echo -e "${GREEN}✓ System already up to date!${NC}"
    log "System already up to date"
    exit 0
fi

echo ""

# ============================================
# Show what will be updated
# ============================================
echo -e "${YELLOW}[4/6] Packages to be updated:${NC}"
apt list --upgradable 2>/dev/null | grep upgradable | head -20
if [ $UPDATES -gt 20 ]; then
    echo "... and $((UPDATES - 20)) more"
fi

echo ""
echo -e "${YELLOW}⚠ WARNING: System will restart if kernel is updated${NC}"
echo ""
read -p "Continue with update? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Update cancelled."
    log "Update cancelled by user"
    exit 0
fi

# ============================================
# Perform update
# ============================================
echo -e "${YELLOW}[5/6] Installing updates...${NC}"
echo "This may take 10-30 minutes..."
echo ""

sudo apt upgrade -y 2>&1 | tee -a "$LOG_FILE"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Updates installed successfully${NC}"
    log "Updates installed successfully ($UPDATES packages)"
else
    echo -e "${RED}✗ Update failed!${NC}"
    log "ERROR: Update failed"
    exit 1
fi

echo ""

# ============================================
# Post-update verification
# ============================================
echo -e "${YELLOW}[6/6] Post-update verification...${NC}"

# Check critical services still running
ALL_OK=true
for service in $CRITICAL_SERVICES; do
    if systemctl is-active --quiet $service; then
        echo -e "${GREEN}✓ $service${NC}"
    else
        echo -e "${RED}✗ $service (not running!)${NC}"
        ALL_OK=false
    fi
done

# Check if reboot needed
if [ -f /var/run/reboot-required ]; then
    echo ""
    echo -e "${YELLOW}⚠ REBOOT REQUIRED${NC}"
    echo "Reason: $(cat /var/run/reboot-required.pkgs)"
    echo ""
    read -p "Reboot now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log "System rebooting after updates"
        sudo reboot
    else
        echo "Remember to reboot later!"
        log "Reboot postponed by user"
    fi
fi

echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     UPDATE COMPLETE                                    ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
echo ""

if $ALL_OK; then
    echo -e "${GREEN}All services running normally${NC}"
    log "Update completed successfully - all services OK"
else
    echo -e "${YELLOW}Some services may need attention${NC}"
    log "Update completed but some services need attention"
fi

echo ""
```

**Save and make executable:**
```bash
chmod +x ~/safe-system-update.sh
```

---

### Step 4.2: Test the update script

```bash
~/safe-system-update.sh
```

**What it does:**
1. Checks prerequisites (disk space, internet)
2. Creates backup marker
3. Shows what will be updated
4. Asks for confirmation
5. Installs updates
6. Verifies services still work
7. Prompts for reboot if needed

**Expected:** Should complete successfully if updates available

---

## 💾 Part 5: Backup & Restore (25 minutes)

### Step 5.1: Create configuration backup script

```bash
nano ~/backup-config.sh
```

**Paste:**

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
    "/home/$USER/*.sh"
)

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
OLD_BACKUPS=$(find "$BACKUP_DIR" -name "*.tar.gz" -mtime +30 | wc -l)
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

### Step 5.2: Create restore script

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

### Step 5.3: Test backup

```bash
~/backup-config.sh
```

**Expected:** Creates tarball with all config files

**Verify:**
```bash
ls -lh /var/backups/prometheus/configs/
```

Should show your backup file (~few KB to few MB)

---

## 📧 Part 6: Automated Alerts (20 minutes)

### Step 6.1: Create alert checker

```bash
nano ~/check-alerts.sh
```

**Paste:**

```bash
#!/bin/bash
# Prometheus Station - Alert Checker
# Run this daily to catch problems early

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
    echo ""
    echo "⚠ ALERTS DETECTED - Check $ALERT_LOG"
    echo ""
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

### Step 6.2: Schedule alert checks

```bash
crontab -e
```

**Add:**
```
# Alert check every 6 hours
0 */6 * * * /home/guillain/check-alerts.sh
```

**Save and exit**

---

## 📅 Part 7: Monthly Maintenance Checklist (10 minutes)

### Step 7.1: Create maintenance script

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

echo "☐ 2. System Updates"
echo "   Run: ~/safe-system-update.sh"
echo ""

echo "☐ 3. Check ZIM Updates"
echo "   Run: ~/list-zim-versions.sh"
echo "   Visit: https://download.kiwix.org/zim/"
echo "   Update if newer versions available: ~/update-zim-files.sh"
echo ""

echo "☐ 4. Configuration Backup"
echo "   Run: ~/backup-config.sh"
echo ""

echo "☐ 5. Log Cleanup"
echo "   Check: du -sh /var/log"
echo "   Clean if >1GB: sudo journalctl --vacuum-size=500M"
echo ""

echo "☐ 6. Verify Services"
echo "   Check: systemctl status kiwix-serve apache2 ssh"
echo ""

echo "☐ 7. Security Audit"
echo "   Failed logins: sudo grep 'Failed password' /var/log/auth.log | wc -l"
echo "   Firewall: sudo ufw status"
echo ""

echo "☐ 8. Performance Review"
echo "   Temperature: vcgencmd measure_temp"
echo "   Load average: uptime"
echo "   Memory: free -h"
echo ""

echo "☐ 9. Test Functionality"
echo "   WiFi hotspot: ~/switch-to-field.sh"
echo "   Web access: http://192.168.42.1"
echo "   Search: Test article search in Kiwix"
echo "   Switch back: ~/switch-to-home.sh"
echo ""

echo "☐ 10. Update Documentation"
echo "   Note any issues in: /var/log/prometheus/maintenance-notes.txt"
echo ""

echo "════════════════════════════════════════════════════════"
echo ""
echo "Estimated time: 30-45 minutes"
echo ""
echo "Record completion:"
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

### Step 7.2: Create maintenance notes file

```bash
touch /var/log/prometheus/maintenance-notes.txt
echo "=== Prometheus Station Maintenance Log ===" > /var/log/prometheus/maintenance-notes.txt
echo "" >> /var/log/prometheus/maintenance-notes.txt
echo "Started: $(date)" >> /var/log/prometheus/maintenance-notes.txt
echo "" >> /var/log/prometheus/maintenance-notes.txt
```

---

## ✅ Part 8: Complete Testing (20 minutes)

### Test each script

**1. Health check:**
```bash
~/health-check.sh
```
✅ Should show complete system status

---

**2. List ZIM versions:**
```bash
~/list-zim-versions.sh
```
✅ Should show all installed ZIM files with dates

---

**3. Configuration backup:**
```bash
~/backup-config.sh
```
✅ Should create backup tarball

---

**4. Alert check:**
```bash
~/check-alerts.sh
```
✅ Should report "No alerts - system healthy"

---

**5. Monthly checklist:**
```bash
~/monthly-maintenance.sh
```
✅ Should display complete checklist

---

### Verify automated tasks

**Check crontab:**
```bash
crontab -l
```

**Should show:**
```
# Daily health check at 3 AM
0 3 * * * /home/guillain/health-check.sh >> /var/log/prometheus/health-$(date +\%Y-\%m).log 2>&1

# Alert check every 6 hours
0 */6 * * * /home/guillain/check-alerts.sh
```

---

## 📊 Usage Guide

### Daily

**Nothing!** Automated tasks run in background.

**Optional:** Quick check
```bash
~/health-check.sh | tail -20
```

---

### Weekly

**Check logs:**
```bash
tail -50 /var/log/prometheus/alerts.log
```

If alerts present, investigate.

---

### Monthly

**Run maintenance checklist:**
```bash
~/monthly-maintenance.sh
```

Follow each step carefully.

---

### When updating ZIM files

**1. Check for updates:**
```bash
~/list-zim-versions.sh
```

**2. Visit Kiwix library:**
- Medical: https://download.kiwix.org/zim/other/
- Wikipedia: https://download.kiwix.org/zim/wikipedia/

**3. Download and install:**
```bash
~/update-zim-files.sh
```

**4. Update service file:**
```bash
sudo nano /etc/systemd/system/kiwix-serve.service
```

Add new ZIM file path, remove old one.

**5. Restart:**
```bash
sudo systemctl daemon-reload
sudo systemctl restart kiwix-serve
```

**6. Test:**
```
http://prometheus-station.local
```

---

### When doing system updates

**Run safe update script:**
```bash
~/safe-system-update.sh
```

**After reboot (if required):**
```bash
~/health-check.sh
```

Verify all services running.

---

## 🛠️ Troubleshooting

### Health check shows errors

**High temperature:**
- Add cooling (heatsinks, fan)
- Improve ventilation
- Reduce load (fewer concurrent users)

**High disk usage:**
- Clean old logs: `sudo journalctl --vacuum-size=500M`
- Remove old ZIM backups: `ls /var/backups/prometheus/zim-backups/`
- Check largest directories: `sudo du -h --max-depth=1 / | sort -hr | head -10`

**Service down:**
- Check status: `sudo systemctl status SERVICE_NAME`
- Check logs: `sudo journalctl -u SERVICE_NAME -n 50`
- Restart: `sudo systemctl restart SERVICE_NAME`

---

### ZIM update fails

**Download interrupted:**
- Resume with `wget -c URL`
- Or start update script again (it will resume)

**File corrupted:**
- Delete partial file: `rm /var/kiwix/temp/FILENAME.zim`
- Download again

**Kiwix won't start after update:**
- Check service file syntax: `sudo nano /etc/systemd/system/kiwix-serve.service`
- Verify file paths are correct
- Test manually: `/usr/local/bin/kiwix-serve --port=8080 /var/kiwix/data/*.zim`

---

### Backup restore doesn't work

**Permissions wrong after restore:**
```bash
sudo chown -R guillain:guillain /home/guillain
sudo chown -R www-data:www-data /var/www/html
```

**Services won't start:**
```bash
sudo systemctl daemon-reload
sudo systemctl restart kiwix-serve apache2
```

---

## 📝 Maintenance Calendar

### Create reminder

**Option 1: Phone calendar**
- Title: "Prometheus Station Maintenance"
- Repeat: Monthly
- Alert: 1 day before
- Notes: Run `~/monthly-maintenance.sh`

**Option 2: Email reminder**
- Use Google Calendar / Outlook
- Recurring event
- Email notification

**Option 3: Desktop reminder**
Add to your personal todo system.

---

## 🎓 What You've Learned

Congratulations! You now know how to:

✅ **Monitor system health** automatically  
✅ **Manage log files** to prevent disk full  
✅ **Update ZIM content** safely  
✅ **Apply system updates** without breaking things  
✅ **Backup and restore** configurations  
✅ **Set up automated alerts** for problems  
✅ **Follow maintenance checklists** systematically  

**Skills gained:**
- System administration best practices
- Preventive maintenance procedures
- Backup/restore strategies
- Log management
- Automated monitoring
- Safe update procedures

---

## 🎯 Next Steps

**Your maintenance system is complete!** Now you can:

### Option A: Field deployment
- Test 24-48 hours continuously
- Switch to hotspot mode
- Verify all services survive reboot
- Document any issues

### Option B: Advanced features
- Add Meshtastic (long-range communication)
- Solar power integration
- E-Ink status display
- Additional monitoring

### Option C: Documentation
- Create user guides
- Print connection instructions
- Document your specific setup
- Share improvements with community

---

## 📚 Quick Reference Card

**Print this and keep near your station:**

```
╔════════════════════════════════════════════════════════╗
║     PROMETHEUS STATION - MAINTENANCE QUICK REF         ║
╚════════════════════════════════════════════════════════╝

DAILY (automated):
  • Health check (3 AM)
  • Alert monitoring (every 6 hours)

WEEKLY:
  ~/health-check.sh
  tail /var/log/prometheus/alerts.log

MONTHLY:
  ~/monthly-maintenance.sh
  (Follow complete checklist)

SYSTEM UPDATE:
  ~/safe-system-update.sh

ZIM UPDATE:
  ~/list-zim-versions.sh
  ~/update-zim-files.sh

BACKUP:
  ~/backup-config.sh

EMERGENCY:
  ~/health-check.sh
  sudo systemctl restart kiwix-serve apache2

LOGS:
  /var/log/prometheus/

HELP:
  https://github.com/GuillainM/Prometheus-Station
```

---

## ⏱️ Time Breakdown

**From tested real-world setup:**

| Phase | Time | Notes |
|-------|------|-------|
| Health dashboard | 30 min | Copy-paste scripts |
| Log management | 20 min | Configuration |
| ZIM update system | 40 min | Includes testing |
| System updates | 30 min | Script + test run |
| Backup/restore | 25 min | Both scripts |
| Alerts | 20 min | Setup automation |
| Checklist | 10 min | Documentation |
| Testing | 20 min | Verify everything |
| **TOTAL** | **3h 15min** | One-time setup |

**Monthly maintenance:** 30-45 minutes

---

## 🔐 Security Notes

### Regular security tasks

**Monthly:**
- Check failed login attempts
- Audit firewall rules
- Review SSH authorized keys
- Update all packages

**Quarterly:**
- Change WiFi password (if compromised)
- Review Tailscale access
- Check for unusual network activity

**Annually:**
- Full security audit
- Review all user accounts
- Update emergency procedures

---

## 💡 Pro Tips

### Efficiency tricks

**1. Alias common commands**
```bash
echo "alias health='~/health-check.sh'" >> ~/.bashrc
echo "alias maint='~/monthly-maintenance.sh'" >> ~/.bashrc
source ~/.bashrc
```

Now just type `health` or `maint`!

---

**2. Quick service restart**
```bash
nano ~/restart-all.sh
```

```bash
#!/bin/bash
sudo systemctl restart kiwix-serve apache2 hostapd dnsmasq
echo "All services restarted"
```

```bash
chmod +x ~/restart-all.sh
```

---

**3. Monitoring widget** (if you have desktop)

```bash
watch -n 60 -c ~/health-check.sh
```

Live updating dashboard!

---

## 📖 Additional Resources

### Official documentation
- [Kiwix Updates](https://library.kiwix.org/)
- [Raspberry Pi System Maintenance](https://www.raspberrypi.org/documentation/)
- [Ubuntu Server Guide](https://ubuntu.com/server/docs)

### Tools
- [htop](https://htop.dev/) - Interactive process viewer
- [ncdu](https://dev.yorhel.nl/ncdu) - Disk usage analyzer
- [glances](https://nicolargo.github.io/glances/) - System monitor

### Community
- [Prometheus Station GitHub](https://github.com/GuillainM/Prometheus-Station)
- [r/raspberry_pi](https://reddit.com/r/raspberry_pi)
- [Kiwix Forum](https://forum.kiwix.org/)

---

**Last updated:** December 30, 2025  
**Tested on:** Raspberry Pi 4 8GB, Raspberry Pi OS Lite (64-bit)  
**Scripts tested:** All scripts verified working  
**Maintenance schedule:** Proven over 6+ months continuous operation

---

*Made with 🔥 for Prometheus Station - Keep your knowledge hub healthy!*
