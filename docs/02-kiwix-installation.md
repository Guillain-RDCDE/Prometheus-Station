# 02 - Kiwix Installation

**Goal:** Install Kiwix server and load medical/educational offline content for disaster response.

**Time Required:** 1-4 hours (depends on download strategy)  
**Difficulty:** ⭐⭐ Medium

---

## 📋 What You'll Need

### Prerequisites
- [ ] Completed [01 - Raspberry Pi Setup](01-raspberry-setup.md)
- [ ] SSH access to your Pi
- [ ] At least 10GB free on SD card (minimal), 200GB recommended (full)
- [ ] Stable internet connection (for downloading ZIM files)

### Knowledge
- Basic command line navigation
- Understanding of systemd services (we'll teach you)

---

## 🎯 Overview

We'll accomplish:
1. Install Kiwix server package
2. Choose content strategy (Emergency Medical vs Full Knowledge)
3. Download ZIM files based on mission needs
4. Configure Kiwix as a systemd service
5. Test local access
6. Configure for external access

---

## 📚 Understanding Kiwix

**What is Kiwix?**
- Offline content server
- Serves ZIM files (compressed Wikipedia dumps and other content)
- Web interface (like accessing real Wikipedia)
- Lightweight and efficient

**What are ZIM files?**
- Compressed offline content archives
- Include all articles, images, metadata
- Updated monthly by Kiwix team
- Available at [download.kiwix.org](https://download.kiwix.org)

---

## Step 1: Install Kiwix

### Method A: Official Package (Recommended)

```bash
# Add Kiwix repository
sudo apt update
sudo apt install -y curl

# Download and install kiwix-tools
curl -L https://download.kiwix.org/release/kiwix-tools/kiwix-tools_linux-armhf.tar.gz -o kiwix-tools.tar.gz

# Extract
tar -xzf kiwix-tools.tar.gz

# Move to system path
sudo mv kiwix-tools_linux-armhf-*/kiwix-serve /usr/local/bin/
sudo chmod +x /usr/local/bin/kiwix-serve

# Verify installation
kiwix-serve --version
```

### Method B: Build from Source (Advanced)

*Skip this unless you need the absolute latest version*

```bash
# Install dependencies
sudo apt install -y git build-essential libtool pkg-config autoconf automake

# Clone repository
git clone https://github.com/kiwix/kiwix-tools.git
cd kiwix-tools

# Build (this takes a while)
./autogen.sh
./configure
make
sudo make install
```

---

## Step 2: Create Kiwix Directory Structure

```bash
# Create directories
sudo mkdir -p /var/kiwix/data
sudo mkdir -p /var/kiwix/library

# Set permissions
sudo chown -R prometheus:prometheus /var/kiwix

# Create library XML (we'll populate this later)
touch /var/kiwix/library/library.xml
```

---

## Step 3: Download ZIM Files

### 🎯 Content Strategy for Prometheus Station

Prometheus Station is designed for **emergency/disaster response** scenarios. This guide provides three download strategies based on your needs and storage capacity.

---

### 📦 Strategy 1: Emergency Medical Pack (⭐ Recommended for Disaster Response)

**Total Size:** ~5.5 GB  
**Download Time:** 1-3 hours  
**Best for:** Medical emergencies, disaster zones, humanitarian missions

```bash
cd /var/kiwix/data

# ============================================
# CRITICAL MEDICAL CONTENT (Priority 1)
# ============================================

# Post-Disaster Medical Guide - protocols for catastrophes
# Used by: MSF, ICRC, WHO field teams
wget -c https://download.kiwix.org/zim/other/zimgit-post-disaster_en_2024-05.zim

# Emergency Medicine Wiki - ER protocols, trauma care
# Used by: Emergency physicians, field medics
wget -c https://download.kiwix.org/zim/other/wikem_en_all_maxi_2021-02.zim

# Medical Encyclopedia - comprehensive reference
# Complete medical knowledge base
wget -c https://download.kiwix.org/zim/other/mdwiki_en_all_maxi_2025-11.zim

# ============================================
# SURVIVAL GUIDES (Priority 2)
# ============================================

# Water purification and sanitation
# Critical for preventing waterborne diseases
wget -c https://download.kiwix.org/zim/other/zimgit-water_en_2024-08.zim

# Food preparation in crisis situations
# Safe food handling in field conditions
wget -c https://download.kiwix.org/zim/other/zimgit-food-preparation_en_2025-04.zim

# ============================================
# GENERAL KNOWLEDGE (Priority 3)
# ============================================

# Wikipedia Medicine subset - filtered medical articles (~1.9 GB)
wget -c https://download.kiwix.org/zim/wikipedia/wikipedia_en_medicine_maxi_2025-09.zim

# Wikipedia Medicine French subset (~1.1 GB)
wget -c https://download.kiwix.org/zim/wikipedia/wikipedia_fr_medicine_maxi_2025-09.zim
```

**What you get:**
- ✅ Post-disaster medical protocols (615 MB)
- ✅ Emergency medicine procedures (42 MB)
- ✅ Complete medical encyclopedia (2.1 GB)
- ✅ Water and food safety guides (113 MB)
- ✅ Medical knowledge in EN + FR (3 GB)

**This pack is what humanitarian organizations use in the field.**

---

### 📦 Strategy 2: Full Knowledge Base

**Total Size:** ~120-150 GB  
**Download Time:** 8-24 hours  
**Best for:** Permanent installations, educational outreach, remote communities

```bash
cd /var/kiwix/data

# ============================================
# COMPLETE WIKIPEDIA (Latest versions)
# ============================================

# Check https://download.kiwix.org/zim/wikipedia/ for current dates
# Files follow pattern: wikipedia_[lang]_all_maxi_YYYY-MM.zim

# Wikipedia English (~90 GB) - Find latest version
wget -c https://download.kiwix.org/zim/wikipedia/wikipedia_en_all_maxi_2025-08.zim

# Wikipedia French (~25 GB) - Find latest version
wget -c https://download.kiwix.org/zim/wikipedia/wikipedia_fr_all_maxi_2025-06.zim

# ============================================
# MEDICAL CONTENT (from Strategy 1)
# ============================================

wget -c https://download.kiwix.org/zim/other/zimgit-post-disaster_en_2024-05.zim
wget -c https://download.kiwix.org/zim/other/wikem_en_all_maxi_2021-02.zim
wget -c https://download.kiwix.org/zim/other/mdwiki_en_all_maxi_2025-11.zim
wget -c https://download.kiwix.org/zim/other/zimgit-water_en_2024-08.zim
wget -c https://download.kiwix.org/zim/other/zimgit-food-preparation_en_2025-04.zim
```

**What you get:**
- ✅ ALL of Wikipedia (EN + FR)
- ✅ Complete medical library
- ✅ Survival guides
- ✅ Educational content for communities

---

### 📦 Strategy 3: Minimal Emergency Kit

**Total Size:** ~750 MB  
**Download Time:** 15-45 minutes  
**Best for:** Limited storage, quick deployment, testing

```bash
cd /var/kiwix/data

# Core emergency medical guides (small but essential)
wget -c https://download.kiwix.org/zim/other/zimgit-post-disaster_en_2024-05.zim  # 615 MB
wget -c https://download.kiwix.org/zim/other/zimgit-medicine_en_2024-08.zim        # 67 MB
wget -c https://download.kiwix.org/zim/other/wikem_en_all_maxi_2021-02.zim         # 42 MB
wget -c https://download.kiwix.org/zim/other/zimgit-water_en_2024-08.zim           # 20 MB
```

**What you get:**
- ✅ Disaster medicine protocols
- ✅ General medical guide
- ✅ Emergency procedures
- ✅ Water safety

**Perfect for rapid deployment or testing the system.**

---

### 🔍 How to Find Latest ZIM Files

ZIM files are updated monthly. The URLs above use specific dates. To find the most recent versions:

**Method 1: Browse the directories**
```bash
# View available Wikipedia files
curl -s https://download.kiwix.org/zim/wikipedia/ | grep "wikipedia_en_all_maxi"

# View available medical files
curl -s https://download.kiwix.org/zim/other/ | grep -E "medical|mdwiki|wikem|disaster"
```

**Method 2: Use Kiwix Library website**
1. Visit: https://library.kiwix.org/
2. Search for content (e.g., "medicine", "wikipedia")
3. Click "Download" to get the current URL
4. Use that URL in your wget command

**Method 3: Check the directory listing manually**
- Wikipedia: https://download.kiwix.org/zim/wikipedia/
- Medical/Other: https://download.kiwix.org/zim/other/
- Look for files with recent dates (YYYY-MM format)

---

### 📋 Understanding Medical Content Sources

| File | Source | Use Case | Size | Updated |
|------|--------|----------|------|---------|
| **zimgit-post-disaster** | WHO/Medical guides | Disaster medicine, mass casualties, field conditions | 615 MB | Annually |
| **WikEM** | Emergency physicians | ER protocols, trauma, toxicology, acute care | 42 MB | 2021* |
| **MDWiki** | Medical community | Comprehensive medical encyclopedia | 2.1 GB | Monthly |
| **zimgit-medicine** | Medical textbooks | General medicine, diagnostics, treatments | 67 MB | Annually |
| **wikipedia_medicine** | Wikipedia editors | Filtered medical articles from Wikipedia | 1.9 GB | Monthly |
| **zimgit-water** | WHO/CDC | Water purification, sanitation, hygiene | 20 MB | Annually |
| **zimgit-food** | WHO/FAO | Food safety, nutrition, preparation | 93 MB | Annually |

*Note: WikEM hasn't been updated since 2021, but emergency medicine protocols are relatively stable.

---

### ⚠️ Important Notes

**Download Tips:**
- Use `wget -c` to resume interrupted downloads
- Downloads run independently - one failure won't stop others
- Download overnight or during off-peak hours
- Check available storage: `df -h /var/kiwix/data`

**Which strategy should you choose?**

| Your Mission | Recommended Strategy | Reason |
|--------------|---------------------|---------|
| 🏥 Humanitarian/disaster response | Strategy 1 (Emergency Medical) | Focused medical content, rapid deployment |
| 🏫 Educational project | Strategy 2 (Full Knowledge) | Complete encyclopedia for learning |
| 🎒 Portable/field testing | Strategy 3 (Minimal Kit) | Lightweight, quick to deploy |
| 💾 Limited storage (<10GB) | Strategy 3 (Minimal Kit) | Essential content only |
| 🌍 Permanent installation | Strategy 2 (Full Knowledge) | Maximum content availability |

---

### 📥 Alternative: Download on Another Computer

If your internet connection is faster elsewhere:

1. Download ZIM files on your main computer
2. Transfer to Pi via:
   - **USB drive** (easiest for large files)
   - **SCP:** `scp file.zim prometheus@prometheus-station.local:/var/kiwix/data/`
   - **SFTP client** (FileZilla, WinSCP)

### Monitor Download Progress

```bash
# In another terminal, watch file sizes
watch -n 60 'du -sh /var/kiwix/data/*'

# Or check network usage
vnstat -l

# See progress of current download
ls -lh /var/kiwix/data/*.zim
```

---

## Step 4: Verify ZIM Files

```bash
# Check downloaded files
ls -lh /var/kiwix/data/

# Verify integrity (optional but recommended)
md5sum /var/kiwix/data/*.zim
```

Compare checksums with [download.kiwix.org](https://download.kiwix.org/zim/)

**Expected output example:**
```
-rw-r--r-- 1 prometheus prometheus  615M zimgit-post-disaster_en_2024-05.zim
-rw-r--r-- 1 prometheus prometheus   42M wikem_en_all_maxi_2021-02.zim
-rw-r--r-- 1 prometheus prometheus  2.1G mdwiki_en_all_maxi_2025-11.zim
```

---

## Step 5: Configure Kiwix Server

### Create Kiwix Library

```bash
# Create library from ZIM files
kiwix-manage /var/kiwix/library/library.xml add /var/kiwix/data/*.zim

# Verify library
cat /var/kiwix/library/library.xml
```

You should see XML entries for each ZIM file.

### Test Manual Start

```bash
# Start Kiwix manually
kiwix-serve --port=8080 --library /var/kiwix/library/library.xml

# Keep this terminal open
```

**Test access:**
- On Pi: `curl http://localhost:8080`
- On your computer: Browse to `http://prometheus-station.local:8080`

You should see the Kiwix welcome page! 🎉

Press `Ctrl+C` to stop the test server.

---

## Step 6: Create Systemd Service

### Create Service File

```bash
sudo nano /etc/systemd/system/kiwix-serve.service
```

Add this configuration:
```ini
[Unit]
Description=Kiwix Server - Offline Medical & Educational Content
After=network.target

[Service]
Type=simple
User=prometheus
Group=prometheus
ExecStart=/usr/local/bin/kiwix-serve \
    --port=80 \
    --library=/var/kiwix/library/library.xml \
    --nodatealiases
Restart=on-failure
RestartSec=5
MemoryLimit=4G

[Install]
WantedBy=multi-user.target
```

### Enable and Start Service

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service (start on boot)
sudo systemctl enable kiwix-serve

# Start service now
sudo systemctl start kiwix-serve

# Check status
sudo systemctl status kiwix-serve
```

**Expected output:**
```
● kiwix-serve.service - Kiwix Server - Offline Medical & Educational Content
   Loaded: loaded (/etc/systemd/system/kiwix-serve.service; enabled)
   Active: active (running) since...
```

---

## Step 7: Configure Firewall

```bash
# Allow HTTP traffic (port 80)
sudo ufw allow 80/tcp

# Reload firewall
sudo ufw reload

# Verify rules
sudo ufw status
```

---

## Step 8: Test Access

### From Your Computer

Browse to: `http://prometheus-station.local`

You should see:
- Kiwix welcome page
- List of available content
- Search functionality

### Test Medical Content

1. Click on "Post-Disaster Medical Guide"
2. Search for "trauma" or "fracture"
3. Verify article loads with images (if applicable)

### Test Wikipedia Medicine

1. Click on "Wikipedia Medicine (English)"
2. Search for "diabetes" or "malaria"
3. Verify comprehensive articles load

### Check Logs

```bash
# View Kiwix logs
sudo journalctl -u kiwix-serve -f

# Check for errors
sudo journalctl -u kiwix-serve --no-pager | grep -i error
```

---

## Step 9: Performance Optimization

### Enable Compression

Edit the service file:
```bash
sudo nano /etc/systemd/system/kiwix-serve.service
```

Modify ExecStart to add compression:
```ini
ExecStart=/usr/local/bin/kiwix-serve \
    --port=80 \
    --library=/var/kiwix/library/library.xml \
    --nodatealiases \
    --compressionlevel=9
```

Reload and restart:
```bash
sudo systemctl daemon-reload
sudo systemctl restart kiwix-serve
```

---

## ✅ Verification Checklist

- [ ] Kiwix service running (`sudo systemctl status kiwix-serve`)
- [ ] All ZIM files downloaded and verified
- [ ] Library.xml populated with all files
- [ ] Web interface accessible on port 80
- [ ] Search functionality works
- [ ] Medical content loads correctly
- [ ] Service starts on boot
- [ ] No errors in logs
- [ ] Firewall allows port 80

Test service restart:
```bash
sudo systemctl restart kiwix-serve
# Wait 10 seconds
sudo systemctl status kiwix-serve
```

---

## 🛠 Troubleshooting

### Service Won't Start

**Check logs:**
```bash
sudo journalctl -u kiwix-serve -n 50
```

**Common issues:**
- Port 80 already in use: `sudo netstat -tulpn | grep :80`
- Permissions wrong: `sudo chown -R prometheus:prometheus /var/kiwix`
- ZIM files corrupted: Verify checksums, re-download if needed
- kiwix-serve not executable: `sudo chmod +x /usr/local/bin/kiwix-serve`

### Web Interface Not Loading

**Verify service:**
```bash
sudo systemctl status kiwix-serve
```

**Test locally first:**
```bash
curl http://localhost
```

**Check firewall:**
```bash
sudo ufw status
```

**Check if port is listening:**
```bash
sudo netstat -tulpn | grep :80
```

### Search Not Working

**Symptoms:** Search returns no results

**Solutions:**
1. Verify ZIM files are complete: `ls -lh /var/kiwix/data/`
2. Check library.xml has all files: `cat /var/kiwix/library/library.xml`
3. Restart service: `sudo systemctl restart kiwix-serve`
4. Check ZIM file isn't corrupted: Try re-downloading

### Low Performance

**Symptoms:** Slow page loads, timeouts

**Solutions:**
1. Check CPU temp: `vcgencmd measure_temp` (should be <70°C)
2. Monitor memory: `free -h` (should have free RAM)
3. Check disk I/O: `iostat -x 1`
4. Reduce concurrent users
5. Enable compression (if not already)
6. Use faster SD card (A2 class minimum)

### Downloads Interrupted

**Resume downloads:**
```bash
cd /var/kiwix/data
wget -c <URL>  # The -c flag resumes partial downloads
```

---

## 📊 Performance Metrics

Document your system performance:

**Search response time:**
- Medical content: ___ seconds
- Wikipedia: ___ seconds

**Page load time:**
- With images: ___ seconds
- Text only: ___ seconds

**Concurrent users tested:** ___

**Resource usage:**
```bash
# While using Kiwix
htop

# Average stats
top -bn1 | grep "Cpu(s)"
free -h
```

---

## 🎯 Next Steps

With Kiwix running, you're ready to add LoRa mesh networking:

**→ [03 - Meshtastic Setup](03-meshtastic-setup.md)**

This will enable long-range communication between Prometheus Stations and mobile devices.

---

## 📚 Additional Resources

- [Kiwix Documentation](https://wiki.kiwix.org/)
- [ZIM File Library](https://library.kiwix.org/)
- [Kiwix GitHub](https://github.com/kiwix)
- [Performance Tuning Guide](https://wiki.kiwix.org/wiki/Kiwix-serve)
- [WikEM Emergency Medicine](https://wikem.org/)
- [WHO Disaster Medicine](https://www.who.int/health-topics/emergencies)

---

## 🏥 Medical Content Usage Guidelines

**Important Legal Notice:**
- Medical content is for **reference and educational purposes**
- Not a replacement for professional medical care
- In emergencies, seek qualified medical personnel when possible
- Content may not reflect latest medical guidelines
- Always verify critical information from multiple sources

**Recommended Usage:**
- ✅ Emergency reference when no internet available
- ✅ Training and education for field medics
- ✅ Preparedness planning for disaster scenarios
- ✅ Community health education
- ❌ NOT for self-diagnosis or self-treatment
- ❌ NOT a replacement for medical professionals

---

*Last updated: December 2025  
Tested on: Raspberry Pi 4 8GB with 256GB SD card  
Content verified with: Médecins Sans Frontières field deployment guidelines*
