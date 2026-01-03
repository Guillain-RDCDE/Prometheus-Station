# Step 2: Kiwix installation & content strategy

**Goal:** Install Kiwix server and download medical/educational content based on your mission.

**Time Required:** 2-6 hours (depends on content strategy + your internet speed)  
**Difficulty:** ⭐⭐⭐ Medium (downloads take time, but process is straightforward once you know the gotchas)

**💡 Real experience:** The hardest part is managing disk space and dealing with large downloads. This guide includes all the troubleshooting we encountered so you don't have to.

---

## 📋 What you'll need

### Prerequisites
- [ ] ✅ Completed [Step 1 - Raspberry Pi Setup](01-raspberry-setup.md)
- [ ] SSH access to your Pi
- [ ] **Stable internet connection** (for downloading ZIM files)
- [ ] Storage based on your chosen strategy:
  - Medical Pack (Strategy 1): 64GB SD with ~10GB free
  - Full Wikipedia (Strategy 2): 256GB SD with ~170GB free
  - Minimal Kit (Strategy 3): 32GB SD with ~5GB free

### Knowledge
- Basic command line navigation
- Understanding of systemd services (we'll teach you)
- Patience for large downloads 😊

---

## 🎯 Overview

We'll accomplish:
1. ✅ Install Kiwix server software
2. ✅ Choose your content strategy (medical/full/minimal)
3. ✅ Download ZIM files for your mission
4. ✅ **Verify file integrity** (CRITICAL - prevents corruption issues)
5. ✅ **Diagnose and fix disk space problems** (common gotcha)
6. ✅ Configure Kiwix as a systemd service
7. ✅ Test web interface
8. ✅ Verify auto-start on reboot

---

## 📚 Understanding kiwix & zim files

### What is kiwix?
- **Offline content server** - Serves Wikipedia without internet
- **Web interface** - Looks and feels like real Wikipedia
- **Lightweight** - Runs on Raspberry Pi efficiently
- **Open source** - Free, actively maintained

### What are zim files?
- **Compressed archives** - Wikipedia content in optimized format
- **Complete content** - Articles, images, metadata, search index
- **Updated monthly** - Kiwix team maintains current versions
- **Various sources** - Wikipedia, medical encyclopedias, survival guides

### Zim file naming
```
wikipedia_en_all_maxi_2025-08.zim
    │      │   │    │      │
    │      │   │    │      └─ Date (YYYY-MM)
    │      │   │    └──────── Type (maxi = complete with images)
    │      │   └───────────── Subset (all = everything, medicine = filtered)
    │      └───────────────── Language code (en, fr, es, etc.)
    └──────────────────────── Source project
```

---

## ⚠️ Critical: "wikimed" doesn't exist!

**Common mistake found in old guides:**

Many tutorials mention downloading "Wikimed" (~50GB). **This project was discontinued.**

❌ **DON'T look for:**
- `/zim/wikimed/` directory (doesn't exist)
- `wikimed_en_all_maxi_latest.zim` (doesn't exist)

✅ **DO use instead:**
- Real humanitarian medical content in `/zim/other/`
- Wikipedia medicine subsets in `/zim/wikipedia/`
- Specific emergency protocols (see Strategy 1 below)

**Why this matters:** You could waste hours looking for files that don't exist. This guide shows you the **actual** medical content available.

---

## 📦 Choose your content strategy

**Before downloading anything, decide what you need:**

---

### Strategy 1: emergency medical pack (5.5 gb) ⭐ recommended for quick start

**Best for:** Humanitarian missions, disaster response, field medicine, testing

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
- ✅ Perfect for learning/testing before full deployment

---

### Strategy 2: Full Knowledge Base (165-170 GB)

**Best for:** Permanent installations, educational centers, remote schools

**What you get:**
- Complete Wikipedia English (~112 GB)
- Complete Wikipedia French (~52 GB)
- All medical content from Strategy 1 (5.5 GB)

**Download time:** 12-48 hours (depends heavily on connection speed)  
**Storage needed:** 256GB SD card  
**Use cases:** Schools, community centers, long-term deployments

**Why choose this:**
- ✅ Comprehensive general knowledge
- ✅ Multiple languages
- ✅ Suitable for diverse user needs
- ✅ Less frequent updates needed

**⚠️ WARNING:** Wikipedia EN alone is **112GB** and can take **6-20 hours** to download. Make sure you have:
- Stable internet that won't disconnect
- Time for the download to complete
- Sufficient disk space (we'll verify this!)

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

## 🎯 Strategy comparison table

| Aspect | Strategy 1 (Medical) | Strategy 2 (Full) | Strategy 3 (Minimal) |
|--------|---------------------|-------------------|---------------------|
| **Size** | 5.5 GB | 165-170 GB | 750 MB |
| **SD Card** | 64GB (~20€) | 256GB (~35€) | 32GB (~15€) |
| **Download** | 15-45 min | 12-48 hours | 5-15 min |
| **Content** | Medical focused | Everything | Emergency only |
| **Best for** | Field missions | Permanent sites | Testing |
| **Deployment** | Same day | 2-3 days | 1 hour |

**💡 Recommendation:** Start with Strategy 1 (Medical Pack) or Strategy 3 (Minimal) to learn the system. You can always upgrade to full Wikipedia later by swapping to a larger SD card.

---

## Step 1: Install Kiwix server (10 minutes)

### Connect to your Pi

```bash
ssh guillain@prometheus-station
# Or use your configured SSH alias: ssh prometheus
```

---

### Install dependencies

```bash
sudo apt update
sudo apt install -y curl wget
```

---

### Download Kiwix tools

```bash
cd ~
curl -L https://download.kiwix.org/release/kiwix-tools/kiwix-tools_linux-aarch64.tar.gz -o kiwix-tools.tar.gz
```

**⚠️ Note:** URL uses `aarch64` for Raspberry Pi 4 (64-bit ARM). If download fails, check [download.kiwix.org/release/kiwix-tools](https://download.kiwix.org/release/kiwix-tools/) for latest version.

---

### Extract and install

```bash
# Extract
tar -xzf kiwix-tools.tar.gz

# Find the extracted directory name (version may vary)
ls -d kiwix-tools_linux-aarch64-*

# Move kiwix-serve to system path (adjust version number if needed)
sudo mv kiwix-tools_linux-aarch64-*/kiwix-serve /usr/local/bin/

# Make executable
sudo chmod +x /usr/local/bin/kiwix-serve

# Clean up
rm -rf kiwix-tools.tar.gz kiwix-tools_linux-aarch64-*
```

---

### Verify installation

```bash
kiwix-serve --version
```

**Expected output:**
```
kiwix-serve 3.x.x
```

✅ If you see a version number, installation successful!

---

## Step 2: Create Kiwix directory structure (2 minutes)

```bash
# Create directories for ZIM files
sudo mkdir -p /var/kiwix/data

# Set ownership to your user (replace 'guillain' with your username)
sudo chown -R $USER:$USER /var/kiwix

# Verify
ls -ld /var/kiwix/data
```

**Expected output:**
```
drwxr-xr-x 2 guillain guillain 4096 Dec 28 10:00 /var/kiwix/data
```

**What this directory does:**
- `/var/kiwix/data/` - Stores ZIM files (this is where downloads go)

---

## ⚠️ Critical: check disk space before downloading

**This is THE most important step to avoid problems!**

```bash
# Check available space
df -h /

# Look at the '/' (root) filesystem line
```

**What you need to see:**

For **Strategy 1** (Medical - 5.5GB):
```
Filesystem      Size  Used Avail Use% Mounted on
/dev/mmcblk0p2   59G   XX    15G  XX% /
                              ↑ Need at least 10GB free
```

For **Strategy 2** (Full - 170GB):
```
Filesystem      Size  Used Avail Use% Mounted on
/dev/mmcblk0p2  235G   XX   180G  XX% /
                              ↑ Need at least 180GB free
```

**If you DON'T have enough space:**

See **"Troubleshooting: Insufficient Disk Space"** section below BEFORE downloading anything!

---

## Step 3: Download ZIM files (based on your strategy)

**Navigate to data directory:**
```bash
cd /var/kiwix/data
```

**💡 Pro tip for large downloads:** Use `screen` or `tmux` so downloads continue even if SSH disconnects:

```bash
# Install screen
sudo apt install -y screen

# Start a screen session
screen -S kiwix-download

# Now run your downloads inside screen
# If disconnected, reconnect with: screen -r kiwix-download
```

---

### Strategy 1: emergency medical pack (5.5 gb)

**Download time:** 15-45 minutes depending on connection

```bash
cd /var/kiwix/data

# Core Medical Content (2.8 GB total)
echo "Downloading medical content..."

# 1. WHO Disaster Medicine Protocols (615 MB)
wget https://download.kiwix.org/zim/other/zimgit-post-disaster_en_2024-05.zim

# 2. Emergency Medicine Wiki (42 MB)
wget https://download.kiwix.org/zim/other/wikem_en_all_maxi_2021-02.zim

# 3. Medical Encyclopedia (2.1 GB)
wget https://download.kiwix.org/zim/other/mdwiki_en_all_maxi_2025-11.zim

# Survival Essentials (113 MB total)
echo "Downloading survival guides..."

# 4. Water Purification (20 MB)
wget https://download.kiwix.org/zim/other/zimgit-water_en_2024-08.zim

# 5. Food Safety (93 MB)
wget https://download.kiwix.org/zim/other/zimgit-food-preparation_en_2025-04.zim

# Wikipedia Medicine Subsets (3 GB total)
echo "Downloading Wikipedia medicine..."

# 6. Wikipedia Medicine - English (1.9 GB)
wget https://download.kiwix.org/zim/wikipedia/wikipedia_en_medicine_maxi_2025-09.zim

# 7. Wikipedia Medicine - French (1.1 GB)
wget https://download.kiwix.org/zim/wikipedia/wikipedia_fr_medicine_maxi_2025-09.zim
```

**Total size:** ~5.5 GB  
**Files downloaded:** 7 ZIM files

---

### Strategy 2: Full Knowledge Base (165-170 GB)

**Download time:** 12-48 hours (plan accordingly!)

**⚠️ IMPORTANT:** These are MASSIVE files. Read the tips below before starting.

#### First, download Strategy 1 content above (5.5 GB)

Then add full Wikipedia:

```bash
cd /var/kiwix/data

# 8. Wikipedia English - Complete (~112 GB) ⚠️ VERY LARGE
echo "Downloading Wikipedia EN (this will take HOURS)..."
wget -c https://download.kiwix.org/zim/wikipedia/wikipedia_en_all_maxi_2025-08.zim

# 9. Wikipedia French - Complete (~52 GB) ⚠️ LARGE
echo "Downloading Wikipedia FR (this will take hours)..."
wget -c https://download.kiwix.org/zim/wikipedia/wikipedia_fr_all_maxi_2025-06.zim
```

**💡 Critical tips for large downloads:**

1. **Use `-c` flag:** Allows resuming if interrupted
2. **Use `screen` or `tmux`:** Downloads continue if SSH disconnects
3. **Monitor progress:** Downloads show ETA and current speed
4. **Be patient:** 112GB at 50 Mbps = ~5 hours minimum
5. **Check space regularly:** `df -h /` to ensure disk isn't filling unexpectedly

**Total size:** ~170 GB  
**Files downloaded:** 9 ZIM files

---

### Strategy 3: Minimal Emergency Kit (750 MB)

**Download time:** 5-15 minutes

```bash
cd /var/kiwix/data

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

## 💡 Monitoring download progress

While downloads are running:

**In the same terminal:** wget shows progress automatically:
```
wikipedia_en_all_maxi_2025-08.zim
  15% [=======>                    ] 16.8G  5.2MB/s  eta 4h 32m
```

**In another SSH session:**
```bash
# Watch file sizes growing
watch -n 10 'ls -lh /var/kiwix/data/'

# Check network usage
sudo apt install -y vnstat
vnstat -l  # Live traffic monitoring
```

---

## ⚠️ Common download issues & solutions

### Issue 1: download interrupted

**Symptom:** Lost connection, download stopped

**Solution:** Use `-c` flag to resume:
```bash
wget -c https://download.kiwix.org/zim/wikipedia/FILE.zim
```

Wget will continue from where it left off! ✅

---

### Issue 2: "no space left on device"

**Symptom:** Download fails with disk full error

**Solution:** See "Troubleshooting: Insufficient Disk Space" section below

---

### Issue 3: very slow download

**Symptom:** Download at kB/s instead of MB/s

**Solutions:**
- Check your internet speed: `speedtest-cli` (install with `sudo apt install speedtest-cli`)
- Try different time of day (Kiwix servers less busy at night EU time)
- Consider downloading on a PC and transferring via USB (faster for 100GB+ files)

---

### Issue 4: 404 not found

**Symptom:** URL doesn't exist

**Cause:** File was updated to newer version

**Solution:** Browse directory to find latest:
```bash
# For Wikipedia files
curl -s https://download.kiwix.org/zim/wikipedia/ | grep "en_all_maxi"

# For medical content
curl -s https://download.kiwix.org/zim/other/ | grep -i "medical\|disaster\|emergency"
```

Look for most recent date (e.g., `2025-11` is newer than `2025-08`)

---

## Step 4: Critical - verify downloaded files (15 minutes)

**⚠️ DON'T SKIP THIS STEP!** Corrupted files will cause Kiwix to fail.

### Install verification tools

```bash
sudo apt install -y zim-tools
```

---

### Check file sizes

```bash
cd /var/kiwix/data
ls -lh
```

**Compare with expected sizes:**

| File | Expected Size |
|------|---------------|
| zimgit-post-disaster_en_2024-05.zim | ~615 MB |
| wikem_en_all_maxi_2021-02.zim | ~43 MB |
| mdwiki_en_all_maxi_2025-11.zim | ~2.2 GB |
| zimgit-water_en_2024-08.zim | ~20 MB |
| zimgit-food-preparation_en_2025-04.zim | ~94 MB |
| wikipedia_en_medicine_maxi_2025-09.zim | ~1.9 GB |
| wikipedia_fr_medicine_maxi_2025-09.zim | ~1.1 GB |
| wikipedia_en_all_maxi_2025-08.zim | **~112 GB** |
| wikipedia_fr_all_maxi_2025-06.zim | **~52 GB** |

**If sizes don't match:** File may be corrupted. Re-download that specific file.

---

### Verify file integrity with zimdump

**Test each file:**

```bash
cd /var/kiwix/data

# Test small files first
echo "Testing medical files..."
zimdump info wikem_en_all_maxi_2021-02.zim
zimdump info zimgit-post-disaster_en_2024-05.zim
zimdump info mdwiki_en_all_maxi_2025-11.zim

# Test medium files
echo "Testing survival guides..."
zimdump info zimgit-water_en_2024-08.zim
zimdump info zimgit-food-preparation_en_2025-04.zim

# Test large files (if downloaded)
echo "Testing Wikipedia files..."
zimdump info wikipedia_en_all_maxi_2025-08.zim
zimdump info wikipedia_fr_all_maxi_2025-06.zim
```

**What to look for:**

✅ **GOOD output example:**
```
count-entries: 26659463
uuid: fc5f2d86-babf-5e64-7166-cf84aea2362e
cluster count: 206944
checksum: d1c2705e0b56a07d88e394b96806b670
```

❌ **BAD output example:**
```
Exception: Zim file(s) is of bad size or corrupted.
```

**If you see "corrupted":**
1. Note which file is bad
2. Delete it: `rm filename.zim`
3. Re-download: `wget -c https://...`
4. Test again with `zimdump info`

---

### Verify md5 checksums (optional but recommended)

**For critical files like Wikipedia EN (112GB), verify the checksum:**

```bash
# Download checksum file
wget https://download.kiwix.org/zim/wikipedia/wikipedia_en_all_maxi_2025-08.zim.md5

# Verify (this takes 5-10 minutes for 112GB file)
md5sum -c wikipedia_en_all_maxi_2025-08.zim.md5
```

**Expected output:**
```
wikipedia_en_all_maxi_2025-08.zim: OK
```

**If checksum FAILS:**
```
wikipedia_en_all_maxi_2025-08.zim: FAILED
md5sum: WARNING: 1 computed checksum did NOT match
```

**Solution:** File is corrupted. Delete and re-download.

---

## 🔍 Troubleshooting: insufficient disk space

**Symptom:** `df -h` shows less free space than expected, or "No space left on device" errors

### Diagnose what's using space

```bash
# Find largest directories
sudo du -h --max-depth=1 / 2>/dev/null | sort -hr | head -20

# Check your home directory specifically
du -h --max-depth=1 ~ | sort -hr

# Look for duplicate ZIM files
find ~ -name "*.zim" -exec ls -lh {} \;

# Check for wget temp files
find ~ -name "*.tmp" -o -name "*.part" 2>/dev/null
```

---

### Common space wasters

**1. Duplicate ZIM files in home directory**

**Problem:** You downloaded ZIM files to `~` (home) instead of `/var/kiwix/data`

**Check:**
```bash
ls -lh ~/*.zim
```

**If files exist in both places:**
```bash
# Remove duplicates from home (AFTER verifying /var/kiwix/data has good copies)
rm ~/*.zim

# Or MOVE them to the correct location
mv ~/*.zim /var/kiwix/data/
```

---

**2. Corrupted partial downloads**

**Problem:** Multiple failed download attempts left behind large `.tmp` files

**Check:**
```bash
ls -lh /var/kiwix/data/*.tmp 2>/dev/null
ls -lh ~/*.tmp 2>/dev/null
```

**Solution:**
```bash
# Remove temp files
rm /var/kiwix/data/*.tmp
rm ~/*.tmp
```

---

**3. System logs too large**

**Check:**
```bash
sudo du -sh /var/log/*
```

**If logs are huge (>1GB):**
```bash
# Clean journal logs
sudo journalctl --vacuum-size=100M

# Clean old logs
sudo apt clean
```

---

**4. Cached packages**

```bash
# Clean package cache
sudo apt clean
sudo apt autoremove
```

---

### Real-world example (from our build)

**Problem encountered:**
```
Filesystem      Size  Used Avail Use% Mounted on
/dev/mmcblk0p2  235G  217G  7.7G  97% /
```

Only 7.7GB free on a 256GB card - something's wrong!

**Diagnosis:**
```bash
sudo du -h --max-depth=1 / 2>/dev/null | sort -hr | head -10

# Output showed:
163G    /home/guillain
```

**Root cause:** Wikipedia files were downloaded to `/home/guillain/` instead of `/var/kiwix/data/`

**Solution:**
```bash
# Remove corrupted files from /var/kiwix/data/
rm /var/kiwix/data/wikipedia_en_all_maxi_2025-08.zim
rm /var/kiwix/data/wikipedia_fr_all_maxi_2025-06.zim

# MOVE (not copy) good files from home
mv ~/wikipedia_en_all_maxi_2025-08.zim /var/kiwix/data/
mv ~/wikipedia_fr_all_maxi_2025-06.zim /var/kiwix/data/

# Check space recovered
df -h /
```

**Result:**
```
Filesystem      Size  Used Avail Use% Mounted on
/dev/mmcblk0p2  235G  170G   56G  76% /
```

✅ From 7.7GB free (97% full) to 56GB free (76% full)!

---

## Step 5: Test Kiwix manually (5 minutes)

**Before creating a service, test that Kiwix works:**

```bash
cd /var/kiwix/data

# Start Kiwix server manually
kiwix-serve --port=8080 *.zim
```

**⚠️ IMPORTANT:** If you see an error about not being able to add ZIM files, it means the wildcard `*.zim` didn't expand properly. This happens on some systems.

**If wildcard fails, list files explicitly:**
```bash
kiwix-serve --port=8080 \
  mdwiki_en_all_maxi_2025-11.zim \
  wikem_en_all_maxi_2021-02.zim \
  zimgit-food-preparation_en_2025-04.zim \
  zimgit-post-disaster_en_2024-05.zim \
  zimgit-water_en_2024-08.zim
  
# Add these if you downloaded them:
  # wikipedia_en_all_maxi_2025-08.zim \
  # wikipedia_fr_all_maxi_2025-06.zim
```

**Expected output:**
```
The Kiwix server is running and can be accessed in the local network at:
  - http://192.168.1.41:8080
  - http://[::1]:8080
```

**Leave this terminal open!**

---

### Test access

**From your laptop browser:**

Try these URLs (in order of reliability):

1. **Direct IP:** `http://192.168.1.41:8080` (replace with YOUR Pi's IP)
2. **Tailscale** (if configured): `http://prometheus-station:8080`
3. **mDNS:** `http://prometheus-station.local:8080` (works on some networks)

**You should see:** Kiwix welcome page listing all your content! 🎉

**Test functionality:**
- Click on one of your ZIM files
- Try searching for "trauma" or "water purification"
- Open an article and verify images load

---

**If it works:** Press `Ctrl+C` in the Pi terminal to stop the manual test.

**If it doesn't work:** See Troubleshooting section below.

---

## Step 6: Create systemd service (15 minutes)

**Why a systemd service?** So Kiwix starts automatically when Pi boots.

### Create service file

```bash
sudo nano /etc/systemd/system/kiwix-serve.service
```

**⚠️ CRITICAL:** Based on our testing, wildcards (`*.zim`) do NOT work in systemd ExecStart. You must list files explicitly.

**Paste this configuration:**

```ini
[Unit]
Description=Kiwix Server - Offline Knowledge Hub
Documentation=https://github.com/kiwix/kiwix-tools
After=network.target

[Service]
Type=simple
User=guillain
Group=guillain
WorkingDirectory=/var/kiwix/data
ExecStart=/usr/local/bin/kiwix-serve --port=8080 \
    /var/kiwix/data/mdwiki_en_all_maxi_2025-11.zim \
    /var/kiwix/data/wikem_en_all_maxi_2021-02.zim \
    /var/kiwix/data/zimgit-food-preparation_en_2025-04.zim \
    /var/kiwix/data/zimgit-post-disaster_en_2024-05.zim \
    /var/kiwix/data/zimgit-water_en_2024-08.zim
Restart=on-failure
RestartSec=5
StandardOutput=journal
StandardError=journal

# Performance settings
Nice=-5
MemoryMax=4G

[Install]
WantedBy=multi-user.target
```

**If you downloaded Wikipedia EN + FR, add these lines before the closing quote:**
```ini
    /var/kiwix/data/wikipedia_en_all_maxi_2025-08.zim \
    /var/kiwix/data/wikipedia_fr_all_maxi_2025-06.zim
```

**If you downloaded Wikipedia medicine instead, add:**
```ini
    /var/kiwix/data/wikipedia_en_medicine_maxi_2025-09.zim \
    /var/kiwix/data/wikipedia_fr_medicine_maxi_2025-09.zim
```

**Important notes:**
- Replace `guillain` with YOUR username if different
- Each ZIM file path on its own line with backslash `\`
- No backslash on the last file

**Save and exit:** Ctrl+X, Y, Enter

---

### What each setting does

| Setting | Purpose |
|---------|---------|
| `User=guillain` | Run as your user (prevents permission issues) |
| `--port=8080` | Port for web access |
| Explicit file paths | Wildcards don't work in systemd |
| `Restart=on-failure` | Auto-restart if crashes |
| `MemoryMax=4G` | Prevent runaway memory usage |
| `Nice=-5` | Higher priority (faster responses) |

---

### Enable and start service

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
   Loaded: loaded (/etc/systemd/system/kiwix-serve.service; enabled; preset: enabled)
   Active: active (running) since Sun 2025-12-28 11:45:26 CET; 10s ago
     Docs: https://github.com/kiwix/kiwix-tools
 Main PID: 4023 (kiwix-serve)
    Tasks: 1 (limit: 8749)
   Memory: 45.2M (limit: 4.0G)
   CGroup: /system.slice/kiwix-serve.service
           └─4023 /usr/local/bin/kiwix-serve --port=8080 /var/kiwix/data/mdwiki...
```

**Key indicators:**
- ✅ `Active: active (running)` - Service is running
- ✅ `enabled` - Will start on boot
- ✅ No errors in logs

---

### If service fails to start

**Check the logs:**
```bash
sudo journalctl -u kiwix-serve -n 50 --no-pager
```

**Common errors:**

**Error 1: "Unable to add the ZIM file '/var/kiwix/data/*.zim'"**
```
Solution: You used wildcard in ExecStart. Edit service file and list files explicitly.
```

**Error 2: "Permission denied"**
```bash
# Fix permissions
sudo chown -R guillain:guillain /var/kiwix/data
sudo systemctl restart kiwix-serve
```

**Error 3: "Port already in use"**
```bash
# Check what's using port 8080
sudo netstat -tulpn | grep :8080

# Either stop the conflicting service or change Kiwix to different port
```

---

### Configure firewall

**Allow HTTP traffic (port 8080):**
```bash
sudo ufw allow 8080/tcp
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
80/tcp                     ALLOW       Anywhere    (Future Apache)
8080/tcp                   ALLOW       Anywhere    (Kiwix)
Anywhere on tailscale0     ALLOW       Anywhere    (Tailscale VPN)
```

---

## Step 7: Test final setup (10 minutes)

### Test 1: access from browser

**From your laptop, try these URLs:**

1. `http://192.168.1.41:8080` (Direct IP - most reliable)
2. `http://prometheus-station:8080` (Tailscale - if configured)
3. `http://prometheus-station.local:8080` (mDNS - sometimes works)

**You should see:** Kiwix interface with all your ZIM files listed

---

### Test 2: content functionality

**For Strategy 1 (Medical Pack):**
1. Click "Post-Disaster Medical Protocols"
2. Search for "fracture" or "cardiac arrest"
3. Verify article loads with text and images
4. Try searching across all content using main search bar

**For Strategy 2 (Full Wikipedia):**
1. Click "Wikipedia (English)"
2. Search for a random topic
3. Navigate to a few articles
4. Check that images load properly

---

### Test 3: check service logs

**View recent activity:**
```bash
sudo journalctl -u kiwix-serve -n 50
```

**Follow live logs:**
```bash
sudo journalctl -u kiwix-serve -f
```

Press Ctrl+C to stop.

**Look for:**
- ✅ "Listening on port 8080"
- ✅ HTTP requests being served
- ❌ Any ERROR or WARNING messages

---

### Test 4: auto-start on boot

**The ultimate test - reboot:**

```bash
# Reboot Pi
sudo reboot
```

**Wait 60 seconds...**

```bash
# SSH back in
ssh guillain@prometheus-station

# Check if Kiwix started automatically
sudo systemctl status kiwix-serve
```

**Expected:** 
```
Active: active (running) since Sun 2025-12-28 11:XX:XX
```

With uptime of just a few seconds/minutes.

**Test web access:** `http://192.168.1.41:8080`

✅ If everything works after reboot, auto-start is configured correctly!

---

## ✅ Verification checklist

Go through each item to confirm everything works:

### Service status
- [ ] `sudo systemctl status kiwix-serve` shows "active (running)"
- [ ] Service enabled for auto-start: `systemctl is-enabled kiwix-serve` returns "enabled"
- [ ] No errors in logs: `sudo journalctl -u kiwix-serve | grep -i error` returns nothing

### Content access
- [ ] Can access Kiwix from laptop: `http://YOUR_PI_IP:8080` works
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
- [ ] Firewall allows port 8080: `sudo ufw status | grep 8080`
- [ ] Can access from multiple devices on network
- [ ] Connection stable (doesn't drop)

### Persistence
- [ ] Service survives reboot (tested above)
- [ ] All content available after reboot
- [ ] No permission errors in logs

**All boxes checked?** 🎉 Kiwix is fully operational!

---

## 🛠️ Troubleshooting

### Service won't start

**Check logs:**
```bash
sudo journalctl -u kiwix-serve -n 100 --no-pager
```

**Common causes:**

**1. Wildcard didn't expand**
```
Error: Unable to add the ZIM file '/var/kiwix/data/*.zim'
Solution: Edit service file, list all ZIM files explicitly (see Step 6)
```

**2. Port 8080 already in use**
```bash
# Find what's using it
sudo netstat -tulpn | grep :8080

# Either stop that service or change Kiwix to port 8090
```

**3. Permissions wrong**
```bash
# Fix ownership
sudo chown -R guillain:guillain /var/kiwix
sudo systemctl restart kiwix-serve
```

**4. ZIM files corrupted**
```bash
# Test each file
cd /var/kiwix/data
zimdump info filename.zim

# Re-download corrupted files
```

---

### Web interface not loading

**1. Verify service is running:**
```bash
sudo systemctl status kiwix-serve
```

If not running, check logs (see above).

**2. Test locally first:**
```bash
curl http://localhost:8080
```

If this works but browser doesn't, it's a network/firewall issue.

**3. Check firewall:**
```bash
sudo ufw status | grep 8080
```

Should show "ALLOW". If not:
```bash
sudo ufw allow 8080/tcp
sudo ufw reload
```

**4. Try IP instead of hostname:**
```bash
# Find Pi's IP
hostname -I

# Try in browser
http://192.168.1.41:8080  # Use your actual IP
```

**5. Check from Pi itself:**
```bash
# Install text browser
sudo apt install -y lynx

# Test locally
lynx http://localhost:8080
```

If this works, problem is network-related.

---

### Search not working

**Symptoms:** Search returns no results or times out

**Solutions:**

**1. ZIM file indexing incomplete**

Some ZIM files take time to index on first use. Wait 2-3 minutes and try again.

**2. Check specific ZIM file:**
```bash
# Test the file directly
cd /var/kiwix/data
zimdump info problematic-file.zim

# If corrupted, re-download
rm problematic-file.zim
wget https://download.kiwix.org/zim/...
```

**3. Memory issues:**
```bash
# Check memory usage
free -h

# If swap is active, disable it (see Step 1 guide)
sudo swapoff -a
```

---

### Slow performance

**Symptoms:** Pages load slowly (>5 seconds), searches timeout

**Diagnose:**

**1. Check CPU/temperature:**
```bash
vcgencmd measure_temp
htop  # Press F10 to quit
```

If temp >70°C or CPU constantly at 100%, you have a cooling problem.

**2. Check SD card performance:**
```bash
sudo hdparm -t /dev/mmcblk0
```

Should be >40 MB/s. If much slower:
- SD card is bottleneck (upgrade to A2 class)
- Card may be failing

**3. Too many concurrent users:**

Kiwix can handle ~10-20 concurrent users on Pi 4. If more, consider:
- Upgrade to Pi 5
- Add additional Pi servers
- Limit concurrent connections

**4. Check system load:**
```bash
uptime
```

Load average should be <1.0 for responsive system.

---

### Content missing after adding new zim

**Problem:** Downloaded new ZIM file but it doesn't appear in Kiwix

**Solution:**

**Edit service file to add new ZIM:**
```bash
sudo nano /etc/systemd/system/kiwix-serve.service

# Add new file path to ExecStart section
# Save and exit

# Reload and restart
sudo systemctl daemon-reload
sudo systemctl restart kiwix-serve
```

---

## 📊 Performance metrics

**Document your system for future reference:**

### Typical resource usage

**Strategy 1 (Medical Pack - 7 ZIM files):**
- **RAM:** 500MB - 1.5GB
- **CPU:** 10-30% idle, 40-70% during searches
- **Temp:** 45-55°C idle, 55-65°C under load
- **Disk I/O:** Low (~5-10 MB/s during reads)

**Strategy 2 (Full Wikipedia - 9 ZIM files):**
- **RAM:** 1-2.5GB
- **CPU:** 15-40% idle, 50-80% during searches
- **Temp:** 50-60°C idle, 60-70°C under load
- **Disk I/O:** Medium (~10-30 MB/s during reads)

**With 5 concurrent users:**
- **CPU:** +20-40%
- **RAM:** +300-500MB
- **Temp:** +5-10°C

---

### Search performance

**Test search speed:**
```bash
time curl -s "http://localhost:8080/search?content=mdwiki&pattern=fracture" > /dev/null
```

**Expected results:**
- Medical content: <1 second
- Wikipedia medicine: <2 seconds
- Full Wikipedia: 2-5 seconds (depending on complexity)

---

### Concurrent user capacity

**Pi 4 8GB typically handles:**
- **Light use** (browsing): 20-30 users
- **Heavy use** (searching): 10-15 users
- **Mixed use:** 15-20 users

**Signs of overload:**
- Search times >10 seconds
- Pages taking >5 seconds to load
- System load >2.0

---

## 🎯 Next steps

**Kiwix is now running!** What's next?

### Immediate:
- [ ] Document your ZIM file list (for future updates)
- [ ] Test with real users
- [ ] Note any performance issues
- [ ] Plan for content updates (monthly)

### Soon:
- [ ] **[Step 3 - Kiwix Configuration](03-kiwix-configuration.md)** - Custom landing page, branding
- [ ] **[Step 4 - WiFi Access Point](04-wifi-access-point.md)** - Transform Pi into wireless hotspot
- [ ] **[Step 5 - System Maintenance](05-maintenance-updates.md)** - Health monitoring, automated updates
- [ ] **Step 6 - Solar Power** (coming soon) - Autonomous operation
- [ ] **Step 7 - Meshtastic Setup** (coming soon) - Add long-range messaging

### Optional enhancements:
- [ ] Setup automatic content updates
- [ ] Create download/backup scripts
- [ ] Add usage statistics
- [ ] Configure HTTPS with self-signed cert
- [ ] Setup multiple language interfaces

---

## 📚 Content maintenance

### Updating zim files

Wikipedia ZIM files are updated monthly. To update:

**1. Download new version:**
```bash
cd /var/kiwix/data
wget https://download.kiwix.org/zim/wikipedia/wikipedia_en_medicine_maxi_2025-12.zim
```

**2. Update service file:**
```bash
sudo nano /etc/systemd/system/kiwix-serve.service

# Change old filename to new filename in ExecStart
# Save and exit
```

**3. Reload and restart:**
```bash
sudo systemctl daemon-reload
sudo systemctl restart kiwix-serve
```

**4. Test new content:**
```bash
# Access in browser
http://YOUR_PI_IP:8080

# Verify new file appears
```

**5. Delete old file:**
```bash
cd /var/kiwix/data
rm wikipedia_en_medicine_maxi_2025-09.zim
```

**Frequency:** Check for updates every 2-3 months for critical content.

---

## 💡 Field deployment tips

### Before going offline:

- [ ] Download all content you need
- [ ] **Test EVERYTHING works**
- [ ] Document access methods (IP, URLs)
- [ ] Create simple connection instructions for users
- [ ] Backup service configuration
- [ ] Note file sizes for verification
- [ ] Test auto-start after reboot
- [ ] Verify all ZIM files with zimdump

### Connection instructions template:

```
PROMETHEUS STATION - OFFLINE KNOWLEDGE

1. Connect to WiFi:
   Network: Prometheus-Station
   Password: [YOUR PASSWORD]

2. Open browser, go to:
   http://192.168.42.1:8080
   or
   http://prometheus-station.local:8080

3. Content available:
   - Disaster Medicine Protocols
   - Emergency Medical Encyclopedia
   - Wikipedia Medicine (EN + FR)
   - Water Purification Guides
   - Food Safety Information

No internet needed. Everything works offline.
```

---

## 📖 Additional resources

### Kiwix documentation:
- [Official Wiki](https://wiki.kiwix.org/)
- [Server Documentation](https://wiki.kiwix.org/wiki/Kiwix-serve)
- [ZIM File Library](https://library.kiwix.org/)
- [Performance Tuning](https://wiki.kiwix.org/wiki/Kiwix-serve#Performance)

### Medical content sources:
- [WHO Publications](https://www.who.int/publications)
- [MSF Field Guides](https://medicalguidelines.msf.org/)
- [WikiEM Emergency Medicine](https://wikem.org/)

### Community:
- [Kiwix GitHub](https://github.com/kiwix)
- [Discussion Forum](https://forum.kiwix.org/)

---

## 🎓 What you've learned

Congratulations! You now know how to:

✅ **Install and configure Kiwix server**  
✅ **Choose appropriate content for different missions**  
✅ **Download and verify ZIM files properly**  
✅ **Diagnose and fix disk space issues**  
✅ **Detect and handle corrupted files**  
✅ **Create systemd services with explicit file paths**  
✅ **Configure firewall for services**  
✅ **Test and verify auto-start functionality**  
✅ **Optimize performance for Raspberry Pi**  
✅ **Troubleshoot common issues systematically**  
✅ **Maintain and update offline content**

**These skills transfer to:**
- Any offline content deployment
- Systemd service management
- Raspberry Pi web server optimization
- Field IT support for humanitarian missions
- Large file management and verification
- Disk space troubleshooting

---

## ⏱️ Actual time breakdown

**From real build experience:**

| Phase | Expected | Actual | Notes |
|-------|----------|--------|-------|
| Install Kiwix tools | 10 min | 12 min | Straightforward |
| Download Strategy 1 | 15-45 min | 30 min | On 50 Mbps connection |
| Download Wikipedia EN | 6-20 hours | 18 hours | 112GB on 50 Mbps |
| Verify files | 15 min | 25 min | MD5 check took longer |
| **Disk space debugging** | - | **2 hours** | Finding duplicate files |
| Create systemd service | 15 min | 45 min | Wildcard issue troubleshooting |
| Test and verify | 10 min | 20 min | Thorough testing |
| **Total (Strategy 1)** | **1-2 hours** | **3.5 hours** | Including troubleshooting |
| **Total (Strategy 2)** | **12-24 hours** | **21 hours** | Mostly waiting for downloads |

**Key takeaway:** Budget extra time for troubleshooting. This updated guide should eliminate most delays!

---

**Next:** [Step 3 - Kiwix Configuration](03-kiwix-configuration.md) - Create custom landing page and polish the interface! 🔥

---

*Last updated: December 2025*  
*Tested on: Raspberry Pi 4 8GB with 256GB A2 SD card*  
*Real-world build time: 21 hours (18 hours downloads, 3 hours active work)*  
*Documented issues encountered and solutions verified*

---

## 🙏 Acknowledgments

This guide incorporates lessons learned from:
- Real-world deployment issues encountered
- Community troubleshooting sessions
- Field testing with large ZIM files
- Disk space management challenges
- Systemd service configuration gotchas

**Special thanks to:** The open-source community for Kiwix, systemd documentation, and the Raspberry Pi Foundation.
