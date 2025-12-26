# Step 2: Kiwix Installation & Content Strategy

**Goal:** Install Kiwix server and download medical/educational content based on your mission.

**Time Required:** 2-4 hours (depends on content strategy chosen)  
**Difficulty:** ⭐⭐☆☆☆ Medium (downloads take time, but process is straightforward)

**💡 Real experience:** The hardest part is waiting for downloads. Everything else "just works."

---

## 📋 What You'll Need

### Prerequisites
- [ ] ✅ Completed [Step 1 - Raspberry Pi Setup](01-raspberry-setup.md)
- [ ] SSH access to your Pi
- [ ] Stable internet connection (for downloading ZIM files)
- [ ] Storage based on your chosen strategy:
  - Medical Pack (Strategy 1): 64GB SD with ~10GB free
  - Full Wikipedia (Strategy 2): 256GB SD with ~130GB free
  - Minimal Kit (Strategy 3): 32GB SD with ~5GB free

### Knowledge
- Basic command line navigation
- Understanding of systemd services (we'll teach you)

---

## 🎯 Overview

We'll accomplish:
1. ✅ Install Kiwix server software
2. ✅ Choose your content strategy (medical/full/minimal)
3. ✅ Download ZIM files for your mission
4. ✅ Configure Kiwix as a systemd service
5. ✅ Test web interface
6. ✅ Optimize performance

---

## 📚 Understanding Kiwix & ZIM Files

### What is Kiwix?
- **Offline content server** - Serves Wikipedia without internet
- **Web interface** - Looks and feels like real Wikipedia
- **Lightweight** - Runs on Raspberry Pi efficiently
- **Open source** - Free, actively maintained

### What are ZIM files?
- **Compressed archives** - Wikipedia content in optimized format
- **Complete content** - Articles, images, metadata, search index
- **Updated monthly** - Kiwix team maintains current versions
- **Various sources** - Wikipedia, medical encyclopedias, survival guides

### ZIM File Naming
```
wikipedia_en_all_maxi_2025-09.zim
    │      │   │    │      │
    │      │   │    │      └─ Date (YYYY-MM)
    │      │   │    └──────── Type (maxi = complete with images)
    │      │   └───────────── Subset (all = everything, medicine = filtered)
    │      └───────────────── Language code (en, fr, es, etc.)
    └──────────────────────── Source project
```

---

## ⚠️ CRITICAL: "Wikimed" Doesn't Exist!

**Common mistake found in old guides:**

Many tutorials mention downloading "Wikimed" (~50GB). **This project was discontinued.**

❌ **DON'T look for:**
- `/zim/wikimed/` directory (doesn't exist)
- `wikimed_en_all_maxi_latest.zim` (doesn't exist)

✅ **DO use instead:**
- Real humanitarian medical content in `/zim/other/`
- Wikipedia medicine subsets in `/zim/wikipedia/`
- Specific emergency protocols (see Strategy 1 below)

**Why this matters:** You could waste hours looking for files that don't exist (I did!). This guide shows you the **actual** medical content available.

---

## 📦 Choose Your Content Strategy

**Before downloading anything, decide what you need:**

---

### Strategy 1: Emergency Medical Pack (5.5 GB) ⭐ RECOMMENDED

**Best for:** Humanitarian missions, disaster response, field medicine

**What you get:**
- WHO disaster medicine protocols
- Emergency medical encyclopedia
- ER procedures and toxicology
- Water purification guides
- Food safety information
- Wikipedia medicine (EN + FR)

**Download time:** 15-45 minutes (on 50 Mbps connection)  
**Storage needed:** 64GB SD card  
**Use cases:** MSF/Red Cross missions, remote clinics, disaster zones

**Why choose this:**
- ✅ Focused, practical content for emergencies
- ✅ Fast to download and deploy
- ✅ Cost-effective (64GB SD ~20€ vs 256GB ~35€)
- ✅ Easier to navigate (less content to search through)

---

### Strategy 2: Full Knowledge Base (120-150 GB)

**Best for:** Permanent installations, educational centers, remote schools

**What you get:**
- Complete Wikipedia English (~90 GB)
- Complete Wikipedia French (~25 GB)
- All medical content from Strategy 1 (5.5 GB)

**Download time:** 8-24 hours (depends on connection)  
**Storage needed:** 256GB SD card  
**Use cases:** Schools, community centers, long-term deployments

**Why choose this:**
- ✅ Comprehensive general knowledge
- ✅ Multiple languages
- ✅ Suitable for diverse user needs
- ✅ Less frequent updates needed

---

### Strategy 3: Minimal Emergency Kit (750 MB)

**Best for:** Quick deployment, testing, proof of concept

**What you get:**
- Core disaster medicine protocols
- Emergency procedures
- Water safety essentials

**Download time:** 5-15 minutes  
**Storage needed:** 32GB SD card  
**Use cases:** Rapid deployment testing, workshops, demonstrations

**Why choose this:**
- ✅ Ultra-fast setup
- ✅ Minimal storage requirements
- ✅ Good for learning/testing before full deployment

---

## 🎯 Strategy Comparison Table

| Aspect | Strategy 1 (Medical) | Strategy 2 (Full) | Strategy 3 (Minimal) |
|--------|---------------------|-------------------|---------------------|
| **Size** | 5.5 GB | 120-150 GB | 750 MB |
| **SD Card** | 64GB (~20€) | 256GB (~35€) | 32GB (~15€) |
| **Download** | 15-45 min | 8-24 hours | 5-15 min |
| **Content** | Medical focused | Everything | Emergency only |
| **Best for** | Field missions | Permanent sites | Testing |
| **Deployment** | Same day | Weekend | 1 hour |

**💡 Recommendation:** Start with Strategy 1 (Medical Pack). You can always add full Wikipedia later by swapping to a larger SD card.

---

## Step 1: Install Kiwix Server (10 minutes)

### Method A: Official Package (Recommended)

**Connect to your Pi:**
```bash
ssh prometheus  # or ssh prometheus@YOUR_PI_IP
```

**Install dependencies:**
```bash
sudo apt update
sudo apt install -y curl wget
```

**Download Kiwix tools:**
```bash
cd ~
curl -L https://download.kiwix.org/release/kiwix-tools/kiwix-tools_linux-aarch64.tar.gz -o kiwix-tools.tar.gz
```

**⚠️ Note:** URL uses `aarch64` for Raspberry Pi 4 (64-bit ARM). If download fails, check [download.kiwix.org/release/kiwix-tools](https://download.kiwix.org/release/kiwix-tools/) for latest version.

**Extract and install:**
```bash
# Extract
tar -xzf kiwix-tools.tar.gz

# Find the extracted directory name
ls -d kiwix-tools_linux-aarch64-*

# Move kiwix-serve to system path (adjust version number if needed)
sudo mv kiwix-tools_linux-aarch64-*/kiwix-serve /usr/local/bin/

# Make executable
sudo chmod +x /usr/local/bin/kiwix-serve

# Clean up
rm -rf kiwix-tools.tar.gz kiwix-tools_linux-aarch64-*
```

**Verify installation:**
```bash
kiwix-serve --version
```

**Expected output:**
```
kiwix-serve 3.x.x
```

✅ If you see a version number, installation successful!

---

### Method B: Build from Source (Advanced - Skip Unless Needed)

*Only use this if the official package doesn't work or you need bleeding-edge features.*

```bash
# Install build dependencies
sudo apt install -y git build-essential libtool pkg-config autoconf automake

# Clone repository
git clone https://github.com/kiwix/kiwix-tools.git
cd kiwix-tools

# Build (takes 10-20 minutes)
./autogen.sh
./configure
make
sudo make install
```

---

## Step 2: Create Kiwix Directory Structure (2 minutes)

```bash
# Create directories for ZIM files and library
sudo mkdir -p /var/kiwix/data
sudo mkdir -p /var/kiwix/library

# Set ownership to your user (replace 'prometheus' if you used different username)
sudo chown -R $USER:$USER /var/kiwix

# Verify
ls -ld /var/kiwix/*
```

**Expected output:**
```
drwxr-xr-x 2 prometheus prometheus 4096 Dec 26 10:00 /var/kiwix/data
drwxr-xr-x 2 prometheus prometheus 4096 Dec 26 10:00 /var/kiwix/library
```

**What these directories do:**
- `/var/kiwix/data/` - Stores ZIM files
- `/var/kiwix/library/` - Stores library.xml (catalog of available content)

---

## Step 3: Download ZIM Files (Based on Your Strategy)

**Navigate to data directory:**
```bash
cd /var/kiwix/data
```

---

### Strategy 1: Emergency Medical Pack (5.5 GB)

**Download time:** 15-45 minutes depending on connection

#### Core Medical Content:

**1. WHO Disaster Medicine Protocols (615 MB)**
```bash
wget https://download.kiwix.org/zim/other/zimgit-post-disaster_en_2024-05.zim
```
**What it is:** WHO field guides for mass casualties, disaster response  
**Used by:** MSF, ICRC, Red Cross field teams

**2. Emergency Medicine Wiki (42 MB)**
```bash
wget https://download.kiwix.org/zim/other/wikem_en_all_maxi_2021-02.zim
```
**What it is:** ER protocols, trauma care, toxicology  
**Used by:** Emergency physicians, field medics

**3. Medical Encyclopedia (2.1 GB)**
```bash
wget https://download.kiwix.org/zim/other/mdwiki_en_all_maxi_2025-11.zim
```
**What it is:** Comprehensive medical reference  
**Updated:** Monthly

#### Survival Essentials:

**4. Water Purification (20 MB)**
```bash
wget https://download.kiwix.org/zim/other/zimgit-water_en_2024-08.zim
```

**5. Food Safety (93 MB)**
```bash
wget https://download.kiwix.org/zim/other/zimgit-food-preparation_en_2025-04.zim
```

#### Wikipedia Medicine Subsets:

**6. Wikipedia Medicine - English (1.9 GB)**
```bash
wget https://download.kiwix.org/zim/wikipedia/wikipedia_en_medicine_maxi_2025-09.zim
```

**7. Wikipedia Medicine - French (1.1 GB)**
```bash
wget https://download.kiwix.org/zim/wikipedia/wikipedia_fr_medicine_maxi_2025-09.zim
```

**Total size:** ~5.5 GB  
**Files downloaded:** 7 ZIM files

---

### Strategy 2: Full Knowledge Base (120-150 GB)

**Download time:** 8-24 hours (start overnight!)

#### First, download Strategy 1 content above (5.5 GB)

#### Then, add Full Wikipedia:

**8. Wikipedia English - Complete (~90 GB)**
```bash
wget https://download.kiwix.org/zim/wikipedia/wikipedia_en_all_maxi_2025-09.zim
```
**Note:** This is HUGE. Ensure you have:
- Stable internet connection
- At least 100GB free space
- Time (6-20 hours depending on speed)

**9. Wikipedia French - Complete (~25 GB)**
```bash
wget https://download.kiwix.org/zim/wikipedia/wikipedia_fr_all_maxi_2025-09.zim
```

**💡 Tip for large downloads:**
```bash
# Use wget with resume capability
wget -c https://download.kiwix.org/zim/wikipedia/wikipedia_en_all_maxi_2025-09.zim

# The -c flag means "continue" - if download is interrupted, you can resume!
```

**Total size:** ~120-150 GB  
**Files downloaded:** 9 ZIM files

---

### Strategy 3: Minimal Emergency Kit (750 MB)

**Download time:** 5-15 minutes

```bash
# Disaster medicine protocols
wget https://download.kiwix.org/zim/other/zimgit-post-disaster_en_2024-05.zim

# Emergency procedures  
wget https://download.kiwix.org/zim/other/wikem_en_all_maxi_2021-02.zim

# Water safety
wget https://download.kiwix.org/zim/other/zimgit-water_en_2024-08.zim
```

**Total size:** ~677 MB  
**Files downloaded:** 3 ZIM files

---

## 💡 How to Find Latest ZIM Files

**ZIM files are updated monthly.** The URLs above may have newer versions available.

### Method 1: Browse Kiwix Library (Easiest)

Visit: [library.kiwix.org](https://library.kiwix.org)

1. Search for content (e.g., "disaster medicine")
2. Click "Download" → Copy link address
3. Use that URL in your `wget` command

### Method 2: Browse Directories Directly

**For Wikipedia projects:**
```bash
curl -s https://download.kiwix.org/zim/wikipedia/ | grep -i "medicine.*2025"
```

**For medical/other content:**
```bash
curl -s https://download.kiwix.org/zim/other/ | grep -E "disaster|medical|emergency"
```

**Look for latest dates:** `2025-11` is newer than `2025-09`

### Method 3: Use Kiwix's Auto-Update URLs

Some ZIM files have `_latest.zim` symlinks:
```bash
# ⚠️ Not all files have this - check first!
wget https://download.kiwix.org/zim/wikipedia/wikipedia_en_medicine_maxi_latest.zim
```

---

## 📊 Monitor Download Progress

While downloads are running, you can monitor in another terminal:

**Option 1: Watch file sizes:**
```bash
# Open new SSH session
ssh prometheus

# Watch data directory
watch -n 10 'du -sh /var/kiwix/data/*'
```

Updates every 10 seconds with file sizes.

**Option 2: Check network usage:**
```bash
# Install vnstat if not present
sudo apt install -y vnstat

# Watch live traffic
vnstat -l
```

Press Ctrl+C to stop monitoring.

**Option 3: Use wget's built-in progress:**

Wget shows progress automatically:
```
wikipedia_en_medicine_maxi_2025-09.zim
  15% [=======>                    ] 285M  5.2MB/s  eta 4m 32s
```

---

## ⚠️ Common Download Issues

### 1. Download Interrupted

**Problem:** Lost connection, download stopped

**Solution:** Use `-c` flag to resume:
```bash
wget -c https://download.kiwix.org/zim/wikipedia/FILE.zim
```

Wget will continue from where it left off!

### 2. "No space left on device"

**Problem:** SD card full

**Solution:** Check available space:
```bash
df -h /var/kiwix/data
```

If full, either:
- Delete unnecessary files
- Use smaller SD card strategy
- Upgrade to larger SD card

### 3. Very Slow Download

**Problem:** Download at kB/s instead of MB/s

**Solutions:**
- Check your internet speed: `speedtest-cli` (install with `sudo apt install speedtest-cli`)
- Try different time of day (Kiwix servers less busy)
- Use alternate mirror if available
- Download on PC and transfer via USB

### 4. 404 Not Found

**Problem:** URL doesn't exist

**Cause:** File was updated to newer version

**Solution:** Browse directory to find latest:
```bash
curl -s https://download.kiwix.org/zim/other/ | grep "disaster"
```

Look for most recent date.

---

## Step 4: Verify ZIM Files (5 minutes)

**Check what you downloaded:**
```bash
cd /var/kiwix/data
ls -lh
```

**Expected output (Strategy 1 example):**
```
total 5.3G
-rw-r--r-- 1 prometheus prometheus  93M Dec 26 11:23 zimgit-food-preparation_en_2025-04.zim
-rw-r--r-- 1 prometheus prometheus 615M Dec 26 11:15 zimgit-post-disaster_en_2024-05.zim
-rw-r--r-- 1 prometheus prometheus  20M Dec 26 11:25 zimgit-water_en_2024-08.zim
-rw-r--r-- 1 prometheus prometheus 2.1G Dec 26 11:45 mdwiki_en_all_maxi_2025-11.zim
-rw-r--r-- 1 prometheus prometheus  42M Dec 26 11:12 wikem_en_all_maxi_2021-02.zim
-rw-r--r-- 1 prometheus prometheus 1.9G Dec 26 12:10 wikipedia_en_medicine_maxi_2025-09.zim
-rw-r--r-- 1 prometheus prometheus 1.1G Dec 26 12:35 wikipedia_fr_medicine_maxi_2025-09.zim
```

**Verify file integrity (optional but recommended):**

Kiwix provides MD5 checksums. To verify:

```bash
# Download checksum file
wget https://download.kiwix.org/zim/other/zimgit-post-disaster_en_2024-05.zim.md5

# Check file
md5sum -c zimgit-post-disaster_en_2024-05.zim.md5
```

**Expected output:**
```
zimgit-post-disaster_en_2024-05.zim: OK
```

**If checksum fails:** Re-download the file (it was corrupted).

**💡 Skip checksums for faster setup:** If downloads completed without errors and file sizes match, checksums are optional.

---

## Step 5: Configure Kiwix Server (10 minutes)

### Create Kiwix Library

**What is library.xml?** A catalog file telling Kiwix which ZIM files to serve.

```bash
# Create library from all ZIM files in data directory
kiwix-manage /var/kiwix/library/library.xml add /var/kiwix/data/*.zim
```

**Expected output:**
```
Added: Post-Disaster Medical Protocols
Added: WikEM Emergency Medicine
Added: MDWiki Medical Encyclopedia
Added: Water Purification
Added: Food Safety
Added: Wikipedia Medicine (English)
Added: Wikipedia Medicine (French)
```

**Verify library:**
```bash
cat /var/kiwix/library/library.xml
```

You should see XML content listing all your ZIM files.

---

### Test Manual Start

**Before creating a service, test that Kiwix works:**

```bash
kiwix-serve --port=8080 --library /var/kiwix/library/library.xml
```

**Expected output:**
```
Kiwix server is running on port 8080
Ready to serve content!
```

**Leave this terminal open!**

---

### Test Access

**From your Pi (in a new SSH session):**
```bash
curl http://localhost:8080
```

Should return HTML content.

**From your laptop:**

Open browser, navigate to:
```
http://prometheus-station.local:8080
```

or

```
http://YOUR_PI_IP:8080
```

(Replace `YOUR_PI_IP` with actual IP, e.g., `192.168.1.42`)

**You should see:** Kiwix welcome page listing all your content! 🎉

**Test search:** Click on one of your ZIM files, try searching for a medical term.

---

**If it works:** Press `Ctrl+C` in the terminal to stop the test server.

**If it doesn't work:** See Troubleshooting section below.

---

## Step 6: Create Systemd Service (15 minutes)

**Why a systemd service?** So Kiwix starts automatically when Pi boots.

### Create Service File

```bash
sudo nano /etc/systemd/system/kiwix-serve.service
```

**Add this configuration:**
```ini
[Unit]
Description=Kiwix Server - Offline Knowledge Hub
Documentation=https://github.com/kiwix/kiwix-tools
After=network.target

[Service]
Type=simple
User=prometheus
Group=prometheus
WorkingDirectory=/var/kiwix
ExecStart=/usr/local/bin/kiwix-serve \
    --port=80 \
    --library=/var/kiwix/library/library.xml \
    --nodatealiases
Restart=on-failure
RestartSec=5
StandardOutput=journal
StandardError=journal

# Performance settings
Nice=-5
MemoryLimit=4G

[Install]
WantedBy=multi-user.target
```

**Save and exit:** Ctrl+X, Y, Enter

**What each setting does:**

| Setting | Purpose |
|---------|---------|
| `User=prometheus` | Run as your user (replace if different) |
| `--port=80` | Default HTTP port (no :8080 in URLs) |
| `--nodatealiases` | Prevents duplicate content listings |
| `Restart=on-failure` | Auto-restart if crashes |
| `MemoryLimit=4G` | Prevents runaway memory usage |
| `Nice=-5` | Higher priority (faster responses) |

---

### Enable and Start Service

```bash
# Reload systemd to recognize new service
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
● kiwix-serve.service - Kiwix Server - Offline Knowledge Hub
   Loaded: loaded (/etc/systemd/system/kiwix-serve.service; enabled; vendor preset: enabled)
   Active: active (running) since Thu 2025-12-26 14:30:15 CET; 3s ago
 Main PID: 1234 (kiwix-serve)
   Memory: 45.2M
   CGroup: /system.slice/kiwix-serve.service
           └─1234 /usr/local/bin/kiwix-serve --port=80 --library=/var/kiwix/library/library.xml

Dec 26 14:30:15 Prometheus-Station systemd[1]: Started Kiwix Server - Offline Knowledge Hub.
```

**Key indicators:**
- ✅ `Active: active (running)` - Service is running
- ✅ `enabled` - Will start on boot
- ✅ No errors in logs

**If you see errors:** Check Troubleshooting section.

---

### Configure Firewall

**Allow HTTP traffic (port 80):**
```bash
sudo ufw allow 80/tcp
sudo ufw reload
```

**Verify firewall rules:**
```bash
sudo ufw status
```

**Expected:**
```
Status: active

To                         Action      From
--                         ------      ----
22/tcp                     ALLOW       Anywhere    (SSH)
80/tcp                     ALLOW       Anywhere    (Kiwix)
```

---

## Step 7: Test Final Setup (5 minutes)

### From Your Laptop

**Open browser, navigate to:**
```
http://prometheus-station.local
```

or

```
http://YOUR_PI_IP
```

**You should see:** Kiwix welcome page (now on port 80, no :8080 needed!)

### Test Each ZIM File

**For Strategy 1 (Medical Pack):**
1. Click "Post-Disaster Medical Protocols"
2. Search for "fracture" or "trauma"
3. Verify article loads with text and images

**Repeat for other ZIM files.**

### Test Search Functionality

1. Use main search bar
2. Type "cardiac arrest" or "water purification"
3. Should search across all ZIM files
4. Results should load quickly (A2 SD card = fast!)

---

### Check Logs

**View recent Kiwix logs:**
```bash
sudo journalctl -u kiwix-serve -n 50
```

**Follow live logs:**
```bash
sudo journalctl -u kiwix-serve -f
```

Press Ctrl+C to stop.

**Look for:**
- ✅ "Listening on port 80"
- ✅ Content requests being served
- ❌ Error messages (if any)

---

## Step 8: Performance Optimization (Optional)

### Adjust Memory Limits

If you have 8GB RAM and serving many users:

```bash
sudo nano /etc/systemd/system/kiwix-serve.service
```

Change:
```ini
MemoryLimit=6G  # Up from 4G
```

**Save, then:**
```bash
sudo systemctl daemon-reload
sudo systemctl restart kiwix-serve
```

---

### Enable Compression

For slower networks, enable compression:

```bash
sudo nano /etc/systemd/system/kiwix-serve.service
```

Add to ExecStart:
```ini
ExecStart=/usr/local/bin/kiwix-serve \
    --port=80 \
    --library=/var/kiwix/library/library.xml \
    --nodatealiases \
    --compressionlevel=9
```

**Reload and restart:**
```bash
sudo systemctl daemon-reload
sudo systemctl restart kiwix-serve
```

**Trade-off:**
- ✅ Faster over WiFi (less data transferred)
- ❌ Slightly more CPU usage on Pi

---

## ✅ Verification Checklist

Go through each item to confirm everything works:

### Service Status
- [ ] `sudo systemctl status kiwix-serve` shows "active (running)"
- [ ] Service enabled for auto-start: `systemctl is-enabled kiwix-serve` returns "enabled"
- [ ] No errors in logs: `sudo journalctl -u kiwix-serve | grep -i error` returns nothing

### Content Access
- [ ] Can access Kiwix from laptop: `http://prometheus-station.local` works
- [ ] All downloaded ZIM files appear in content list
- [ ] Can open and read articles from each ZIM file
- [ ] Search functionality works across all content
- [ ] Images load correctly in articles

### Performance
- [ ] Articles load within 2-3 seconds
- [ ] Search results appear within 1-2 seconds
- [ ] No lag when browsing between articles
- [ ] Pi temperature stays under 60°C: `vcgencmd measure_temp`
- [ ] Memory usage reasonable: `free -h` shows <2GB used

### Network
- [ ] Firewall allows port 80: `sudo ufw status | grep 80`
- [ ] Can access from multiple devices on network
- [ ] Connection stable (doesn't drop)

### Persistence
- [ ] Service survives reboot:
  ```bash
  sudo reboot
  # Wait 60 seconds
  # Try accessing http://prometheus-station.local again
  ```

**All boxes checked?** 🎉 Kiwix is fully operational!

---

## 🛠️ Troubleshooting

### Service Won't Start

**Check logs:**
```bash
sudo journalctl -u kiwix-serve -n 100 --no-pager
```

**Common causes:**

**1. Port 80 already in use**
```bash
sudo netstat -tulpn | grep :80
```

**Solution:** Another service (Apache, nginx) is using port 80.
- Stop conflicting service: `sudo systemctl stop apache2`
- Or change Kiwix port in service file to 8080

**2. Permissions wrong**
```bash
ls -l /var/kiwix/data
```

**Solution:**
```bash
sudo chown -R prometheus:prometheus /var/kiwix
```

**3. ZIM files corrupted**

Re-download the file that's causing issues.

---

### Web Interface Not Loading

**1. Verify service is running:**
```bash
sudo systemctl status kiwix-serve
```

**2. Test locally first:**
```bash
curl http://localhost
```

If this works but browser doesn't, it's a network issue.

**3. Check firewall:**
```bash
sudo ufw status | grep 80
```

Should show "ALLOW". If not:
```bash
sudo ufw allow 80/tcp
sudo ufw reload
```

**4. Try IP instead of hostname:**
```bash
# Find Pi's IP
hostname -I

# Try in browser
http://192.168.1.42  # Use your actual IP
```

---

### Search Not Working

**Symptoms:** Search returns no results

**Causes & Solutions:**

**1. ZIM files incomplete**
- Verify file sizes match expected sizes
- Re-download if too small

**2. Library.xml not updated**
```bash
# Rebuild library
kiwix-manage /var/kiwix/library/library.xml remove "*"
kiwix-manage /var/kiwix/library/library.xml add /var/kiwix/data/*.zim

# Restart service
sudo systemctl restart kiwix-serve
```

**3. Index corrupted**

Delete and re-add ZIM file to library.

---

### Slow Performance

**Symptoms:** Pages load slowly (>5 seconds), searches timeout

**Solutions:**

**1. Check CPU/temperature:**
```bash
vcgencmd measure_temp
htop
```

If temp >70°C or CPU 100%, improve cooling.

**2. Check SD card class:**
```bash
sudo hdparm -t /dev/mmcblk0
```

Should be >40 MB/s. If much slower, SD card is bottleneck (get A2 class).

**3. Reduce memory limit:**
```bash
sudo nano /etc/systemd/system/kiwix-serve.service
# Change MemoryLimit=2G (from 4G or 6G)
```

**4. Check concurrent users:**

Too many users accessing at once. Kiwix can handle ~10-20 concurrent users on Pi 4.

---

### Content Missing

**Symptom:** Downloaded ZIM files don't appear in Kiwix

**Solution:**
```bash
# Verify files exist
ls -lh /var/kiwix/data/

# Check library
cat /var/kiwix/library/library.xml

# Rebuild library if needed
kiwix-manage /var/kiwix/library/library.xml add /var/kiwix/data/*.zim

# Restart
sudo systemctl restart kiwix-serve
```

---

## 📊 Performance Metrics

**Document your system for future reference:**

### Search Response Time

Test with:
```bash
time curl -s "http://localhost/search?content=post-disaster&pattern=trauma" > /dev/null
```

**Expected:** <2 seconds

### Page Load Time

Open browser dev tools (F12) → Network tab

**Expected:** 1-3 seconds for article with images

### Concurrent Users

**Test:**
- Open Kiwix on multiple devices
- All search/browse simultaneously
- Note when it starts slowing down

**Pi 4 8GB typically handles:** 10-20 concurrent users comfortably

### Resource Usage

```bash
# While users are accessing content
htop

# Memory
free -h

# Disk I/O
iostat -x 1
```

**Typical usage (Strategy 1, 5 users):**
- CPU: 20-40%
- RAM: 500MB-1.5GB
- Temp: 50-55°C

---

## 🎯 Next Steps

**Kiwix is now running!** What's next?

### Immediate:
- [ ] Share WiFi details with users
- [ ] Create simple instructions for connecting
- [ ] Test with real users
- [ ] Document any issues you find

### Soon:
- [ ] **[Step 3 - Meshtastic Setup](03-meshtastic-setup.md)** - Add long-range messaging
- [ ] Configure WiFi access point (integrate Kiwix)
- [ ] Setup E-Ink status display

### Future:
- [ ] Solar power optimization
- [ ] Field deployment testing
- [ ] Content updates (monthly Wikipedia refreshes)
- [ ] User feedback integration

---

## 📚 Content Maintenance

### Updating ZIM Files

Wikipedia ZIM files are updated monthly. To update:

**1. Download new version:**
```bash
cd /var/kiwix/data
wget https://download.kiwix.org/zim/wikipedia/wikipedia_en_medicine_maxi_2025-12.zim
```

**2. Remove old from library:**
```bash
kiwix-manage /var/kiwix/library/library.xml remove "Wikipedia Medicine (English) 2025-09"
```

**3. Add new to library:**
```bash
kiwix-manage /var/kiwix/library/library.xml add wikipedia_en_medicine_maxi_2025-12.zim
```

**4. Restart Kiwix:**
```bash
sudo systemctl restart kiwix-serve
```

**5. Delete old file:**
```bash
rm wikipedia_en_medicine_maxi_2025-09.zim
```

**Frequency:** Check for updates every 2-3 months for medical content.

---

## 💡 Tips for Field Deployment

### Before Going Offline:

- [ ] Download all content you need
- [ ] Test everything works
- [ ] Document WiFi password
- [ ] Create simple connection instructions
- [ ] Backup library.xml file
- [ ] Note file sizes for verification

### Connection Instructions Template:

```
PROMETHEUS STATION - OFFLINE KNOWLEDGE

1. Connect to WiFi:
   Network: Prometheus-Station
   Password: [YOUR PASSWORD]

2. Open browser, go to:
   http://prometheus-station.local
   or
   http://192.168.42.1

3. Content available:
   - Disaster Medicine Protocols
   - Emergency Medical Encyclopedia
   - Water Purification Guides
   - Wikipedia Medicine (EN + FR)

No internet needed. Everything works offline.
```

---

## 📖 Additional Resources

### Kiwix Documentation:
- [Official Wiki](https://wiki.kiwix.org/)
- [Server Documentation](https://wiki.kiwix.org/wiki/Kiwix-serve)
- [ZIM File Library](https://library.kiwix.org/)
- [Performance Tuning](https://wiki.kiwix.org/wiki/Kiwix-serve#Performance)

### Medical Content Sources:
- [WHO Publications](https://www.who.int/publications)
- [MSF Field Guides](https://medicalguidelines.msf.org/)
- [WikiEM Emergency Medicine](https://wikem.org/)

### Community:
- [Kiwix GitHub](https://github.com/kiwix)
- [Discussion Forum](https://forum.kiwix.org/)

---

## 🎓 What You've Learned

Congratulations! You now know how to:

✅ **Install and configure Kiwix server**  
✅ **Choose appropriate content for different missions**  
✅ **Download and verify ZIM files**  
✅ **Create systemd services for auto-start**  
✅ **Optimize performance for Raspberry Pi**  
✅ **Troubleshoot common issues**  
✅ **Maintain and update offline content**

**These skills transfer to:**
- Any offline content deployment
- Systemd service management
- Raspberry Pi web server optimization
- Field IT support for humanitarian missions

---

**Next:** [Step 3 - Meshtastic Setup](03-meshtastic-setup.md) - Add long-range communication! 📡

---

*Last updated: December 2025*  
*Tested on: Raspberry Pi 4 8GB with Strategy 1 (Medical Pack)*  
*Total build time: 2h 15min (1h 45min downloading)*

