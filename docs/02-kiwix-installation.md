# 📚 Step 2: Kiwix Installation & Wikipedia Deployment

**What you'll accomplish:** Transform your Raspberry Pi into an offline Wikipedia server accessible via web browser.

**Time required:** 3-6 hours (mostly download time for Wikipedia files)  
**Difficulty:** ⭐⭐⭐☆☆ Medium (patience required for large downloads)  
**Skills learned:** Package management, systemd services, web servers, large file handling

---

## 🎯 What Success Looks Like

By the end of this guide, you'll have:
- ✅ Kiwix server software installed and running
- ✅ Wikipedia content (English and/or French) downloaded and accessible
- ✅ Wikimed medical encyclopedia available offline
- ✅ Web interface accessible from any device on your network
- ✅ Kiwix configured to start automatically on boot
- ✅ Firewall configured for secure access

**The moment of victory:** When you open `http://prometheus-station.local` in your browser and search Wikipedia—completely offline. 🎉

---

## 📋 Pre-Flight Checklist

Before we start, verify you have:

### Prerequisites Completed:
- [ ] **Step 1: Raspberry Pi Setup** (completed successfully)
- [ ] **SSH access working** (you can connect to your Pi)
- [ ] **System updated** (`sudo apt update && sudo apt upgrade` run recently)
- [ ] **At least 200GB free** on your SD card (check with `df -h`)

### Network Requirements:
- [ ] **Stable internet connection** (preferably unlimited data or high cap)
- [ ] **Several hours available** for downloads to complete
- [ ] **Your laptop on the same network** as the Pi (for testing)

### What You'll Download:
- [ ] **Kiwix server software** (~10MB)
- [ ] **Wikipedia ZIM files** (90GB+ per language)
- [ ] **Wikimed ZIM files** (50GB+ per language)

**Warning:** The ZIM file downloads are HUGE. If you have limited data or slow internet, consider:
- Starting with just one language
- Downloading on a faster connection and transferring via USB
- Using a smaller ZIM file (like Wikipedia "nopic" versions without images)

**Ready?** Let's bring Wikipedia offline! 🚀

---

## 📖 The Big Picture: Understanding Kiwix

Before diving into commands, let's understand what we're building:

```
┌────────────────────────────────────────────────────────┐
│                    KIWIX SYSTEM                        │
│                                                        │
│  ┌──────────────┐         ┌─────────────┐            │
│  │  ZIM Files   │────────▶│   Kiwix     │            │
│  │              │         │   Server    │            │
│  │ • Wikipedia  │         │ (software)  │            │
│  │ • Wikimed    │         │             │            │
│  │ • Others     │         └──────┬──────┘            │
│  └──────────────┘                │                    │
│   (compressed                    │                    │
│    archives)                     ▼                    │
│                         ┌─────────────────┐           │
│                         │  Web Interface  │           │
│                         │  (port 80)      │           │
│                         └────────┬────────┘           │
│                                  │                    │
└──────────────────────────────────┼────────────────────┘
                                   │
                                   ▼
                          ┌─────────────────┐
                          │  Your Browser   │
                          │                 │
                          │ • Search        │
                          │ • Read articles │
                          │ • Browse        │
                          └─────────────────┘
```

**In simple terms:**
1. **ZIM files** = Compressed Wikipedia dumps (think: entire Wikipedia in a .zip file)
2. **Kiwix server** = Software that reads ZIM files and serves them as websites
3. **Your browser** = Access point (just like accessing regular Wikipedia)

**The magic:** Once set up, it works EXACTLY like Wikipedia.org, but 100% offline.

---

## 🧠 Understanding ZIM Files

**What are ZIM files?**
- Compressed archives containing entire websites
- Include all articles, images, formatting, metadata
- Updated monthly by the Kiwix team
- Downloaded from [download.kiwix.org](https://download.kiwix.org)

**Why ZIM format?**
- Highly compressed (90GB Wikipedia vs 500GB+ raw HTML)
- Indexed for fast searches
- Includes full-text search capability
- Optimized for offline use

**Available content:**

| Content | Language | Size | Articles | Description |
|---------|----------|------|----------|-------------|
| Wikipedia | English | ~90GB | 6M+ | Full Wikipedia with images |
| Wikipedia | French | ~25GB | 2.5M+ | Full Wikipedia with images |
| Wikimed | English | ~50GB | Medical | Medical encyclopedia |
| Wikimed | French | ~6GB | Medical | Medical encyclopedia |
| Wikipedia (nopic) | English | ~50GB | 6M+ | Wikipedia WITHOUT images (saves space) |

**For this guide, we'll install:**
- Wikipedia English (full with images)
- Wikipedia French (full with images)
- Wikimed English

**Estimated total:** ~165GB (be patient!)

---

## 🔧 Part 1: Installing Kiwix Server

### Step 1.1: Check Available Disk Space

Before downloading anything, verify you have enough room:

```bash
# Check free space on SD card
df -h /

# Expected output should show 200GB+ available
# Example:
# Filesystem      Size  Used Avail Use% Mounted on
# /dev/root       233G   15G  207G   7% /
```

**If you have less than 200GB available:**
- Your filesystem might not be expanded → Re-run `sudo raspi-config` → Advanced → Expand Filesystem
- Your SD card is smaller than expected → Check if it's fake/mislabeled
- You already filled the card → Clean up unwanted files with `sudo apt clean`

---

### Step 1.2: Install Required Dependencies

```bash
# Update package lists
sudo apt update

# Install dependencies
sudo apt install -y curl wget tar
```

**What each package does:**
- `curl` - Downloads files from URLs (used for Kiwix installer)
- `wget` - Alternative downloader (used for ZIM files)
- `tar` - Extracts compressed archives

**Expected output:**
```
Reading package lists... Done
Building dependency tree... Done
curl is already the newest version
wget is already the newest version
tar is already the newest version
0 upgraded, 0 newly installed, 0 to remove
```

If they're already installed (like above), that's perfect! ✅

---

### Step 1.3: Download and Install Kiwix Server

**Important:** Raspberry Pi 4 uses ARM64 architecture. We need the `aarch64` version for optimal performance.

```bash
# Go to home directory
cd ~

# Download kiwix-tools (ARM64/aarch64 version for Raspberry Pi 4)
curl -L https://download.kiwix.org/release/kiwix-tools/kiwix-tools_linux-aarch64.tar.gz -o kiwix-tools.tar.gz
```

**What's happening:**
- `-L` flag follows redirects (Kiwix might redirect to a mirror)
- `-o` specifies output filename
- Download size: ~10MB (quick download)
- **aarch64** = ARM 64-bit architecture (optimal for Pi 4)

**While downloading, you'll see:**
```
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100 10.2M  100 10.2M    0     0  5024k      0  0:00:02  0:00:02 --:--:-- 5024k
```

---

### Step 1.4: Extract Kiwix Tools

```bash
# Extract the archive
tar -xzf kiwix-tools.tar.gz

# List contents to see what was extracted
ls -la
```

**You should see:**
```
drwxrwxr-x 2 prometheus prometheus  4096 Dec 26 16:01 kiwix-tools_linux-aarch64-3.8.1/
-rw-r--r-- 1 prometheus prometheus 10.2M Dec 26 16:00 kiwix-tools.tar.gz
```

**Check what's inside the extracted folder:**
```bash
ls -la kiwix-tools_linux-aarch64-*/
```

**You should see:**
```
-rwxr-xr-x 1 prometheus prometheus 17029904 Dec  2 07:11 kiwix-manage
-rwxr-xr-x 1 prometheus prometheus 16139928 Dec  2 07:11 kiwix-search
-rwxr-xr-x 1 prometheus prometheus 17407016 Dec  2 07:11 kiwix-serve
```

**Understanding the extraction:**
- `tar -xzf` = eXtract, using gZip compression, from File
- Creates a directory like `kiwix-tools_linux-aarch64-3.8.1`
- Contains three programs **directly in the folder** (not in a bin/ subdirectory):
  - `kiwix-serve` - The web server we'll use
  - `kiwix-manage` - Tool to manage the library catalog
  - `kiwix-search` - Command-line search tool

---

### Step 1.5: Install to System Path

Now we need to move Kiwix to a location where the system can find it:

```bash
# Move kiwix-serve to system path
sudo mv kiwix-tools_linux-aarch64-*/kiwix-serve /usr/local/bin/

# Move kiwix-manage (we'll need this later)
sudo mv kiwix-tools_linux-aarch64-*/kiwix-manage /usr/local/bin/

# Make both executable
sudo chmod +x /usr/local/bin/kiwix-serve
sudo chmod +x /usr/local/bin/kiwix-manage

# Clean up downloaded files
rm kiwix-tools.tar.gz
rm -rf kiwix-tools_linux-aarch64-*/
```

**Why /usr/local/bin?**
- System-wide programs go here
- Automatically in PATH (accessible from anywhere)
- Standard Unix convention

**What the wildcard `*` does:**
- `kiwix-tools_linux-aarch64-*/` matches any version number
- Works with `kiwix-tools_linux-aarch64-3.8.1/` or future versions
- Saves you from typing exact version number

---

### Step 1.6: Verify Installation

```bash
# Check Kiwix version
kiwix-serve --version
```

**Expected output:**
```
kiwix-serve 3.5.0

Copyright 2021 Wikimedia CH
License GPLv3+: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>
```

**If you see the version number, SUCCESS!** ✅ Kiwix is installed.

**If you see "command not found":**
- Check if file exists: `ls -la /usr/local/bin/kiwix-serve`
- Verify permissions: Should be `-rwxr-xr-x` (executable)
- Try running directly: `/usr/local/bin/kiwix-serve --version`

---

## 📦 Part 2: Creating Directory Structure

### Step 2.1: Create Kiwix Directories

We need organized locations for ZIM files and configuration:

```bash
# Create data directory (for ZIM files)
sudo mkdir -p /var/kiwix/data

# Create library directory (for catalog/index)
sudo mkdir -p /var/kiwix/library

# Check they were created
ls -la /var/kiwix/
```

**Expected output:**
```
drwxr-xr-x 4 root root 4096 Dec 26 10:35 .
drwxr-xr-x 14 root root 4096 Dec 26 10:35 ..
drwxr-xr-x 2 root root 4096 Dec 26 10:35 data
drwxr-xr-x 2 root root 4096 Dec 26 10:35 library
```

**Directory structure explained:**
```
/var/kiwix/
├── data/           ← ZIM files live here (Wikipedia, Wikimed, etc.)
└── library/        ← library.xml catalog file (indexes all ZIM files)
```

---

### Step 2.2: Set Correct Permissions

**Important:** Kiwix will run as your user, so we need proper ownership:

```bash
# Change ownership to your user (replace 'prometheus' with YOUR username)
sudo chown -R $USER:$USER /var/kiwix

# Verify permissions
ls -la /var/kiwix/
```

**Expected output (with correct ownership):**
```
drwxr-xr-x 4 prometheus prometheus 4096 Dec 26 10:35 .
drwxr-xr-x 14 root root 4096 Dec 26 10:35 ..
drwxr-xr-x 2 prometheus prometheus 4096 Dec 26 10:35 data
drwxr-xr-x 2 prometheus prometheus 4096 Dec 26 10:35 library
```

**Why this matters:**
- Kiwix server will run as your user (not root - security best practice)
- Needs read/write access to these directories
- Wrong permissions = "Permission denied" errors later

---

### Step 2.3: Create Library Catalog File

```bash
# Create empty library.xml file
touch /var/kiwix/library/library.xml

# Verify it exists
ls -la /var/kiwix/library/
```

**Expected output:**
```
-rw-r--r-- 1 prometheus prometheus    0 Dec 26 10:36 library.xml
```

**What is library.xml?**
- XML catalog of all available ZIM files
- Kiwix reads this to know what content to serve
- We'll populate it after downloading ZIM files

---

## 📥 Part 3: Downloading ZIM Files (The Long Part)

**⚠️ CRITICAL WARNINGS BEFORE DOWNLOADING:**

1. **Downloads are HUGE:** 90GB+ per Wikipedia language
2. **Takes HOURS:** On 50Mbps connection, expect 4-6 hours per file
3. **Can be resumed:** If interrupted, wget can continue where it left off
4. **Check data caps:** 165GB total - make sure your ISP allows this!
5. **SD card wear:** Lots of writes - use quality A2 card
6. **Filenames change monthly:** ZIM files are updated every month with new dates

**Strategy options:**

- **Option A:** Download directly on Pi (easiest, but slow)
- **Option B:** Download on fast PC, transfer via USB (faster, more complex)
- **Option C:** Start with French Wikipedia (smaller, 25GB vs 90GB)

We'll use **Option A** in this guide, starting with **Option C** (French first).

---

### Step 3.1: Find Current ZIM File URLs

**Important:** ZIM files are updated monthly and filenames include dates (like `wikipedia_en_all_maxi_2024-12.zim`). The URLs in this guide will become outdated!

**Method 1: Browse the Kiwix Download Directory (Recommended)**

1. **On your laptop**, open a web browser
2. Go to: **https://download.kiwix.org/zim/wikipedia/**
3. You'll see a directory listing of ALL Wikipedia ZIM files

**What you're looking for:**

| Content | Filename Pattern | Typical Size |
|---------|------------------|--------------|
| Wikipedia English (full) | `wikipedia_en_all_maxi_YYYY-MM.zim` | ~90GB |
| Wikipedia English (no pics) | `wikipedia_en_all_nopic_YYYY-MM.zim` | ~50GB |
| Wikipedia French (full) | `wikipedia_fr_all_maxi_YYYY-MM.zim` | ~25GB |
| Wikipedia French (no pics) | `wikipedia_fr_all_nopic_YYYY-MM.zim` | ~15GB |

**Example from December 2024:**
- `wikipedia_en_all_maxi_2024-12.zim` (90.2 GB)
- `wikipedia_fr_all_maxi_2024-12.zim` (25.8 GB)

**How to identify the latest version:**
- Look for the **most recent date** (YYYY-MM format)
- Files are usually updated around the 15th of each month
- Bigger file size often indicates newer dumps (more content)

**4. Right-click on the filename → Copy link address**

---

**Method 2: Use the Kiwix Library (Alternative)**

1. Go to: **https://library.kiwix.org/**
2. Search for "Wikipedia"
3. Filter by language (EN, FR, etc.)
4. Click "Download" → This gives you the direct `.zim` link
5. Copy the URL

---

**Method 3: Command Line Search (Advanced)**

From your Pi, you can search directly:

```bash
# List all Wikipedia English files with dates
curl -s https://download.kiwix.org/zim/wikipedia/ | grep "wikipedia_en_all_maxi" | grep -o 'href="[^"]*' | cut -d'"' -f2

# List all Wikipedia French files
curl -s https://download.kiwix.org/zim/wikipedia/ | grep "wikipedia_fr_all_maxi" | grep -o 'href="[^"]*' | cut -d'"' -f2
```

This shows all available files - pick the one with the latest date.

---

### Step 3.2: Download Your First ZIM File

**Now that you have the correct URL, let's download!**

**For this guide, we'll start with Wikipedia French (smaller, faster to test):**

```bash
# Navigate to data directory
cd /var/kiwix/data

# Download Wikipedia French (REPLACE URL WITH CURRENT ONE FROM STEP 3.1)
# Example with December 2024 version:
wget -c https://download.kiwix.org/zim/wikipedia/wikipedia_fr_all_maxi_2024-12.zim
```

**⚠️ IMPORTANT:** Replace `2024-12` with the **current month's version** you found in Step 3.1!

**Understanding wget flags:**
- `-c` = Continue interrupted downloads (CRITICAL for large files!)
- If download stops, just run the SAME command again - it resumes!

**While downloading, you'll see:**
```
--2025-12-26 16:10:15--  https://download.kiwix.org/zim/wikipedia/...
Resolving download.kiwix.org (download.kiwix.org)... 51.159.101.162
Connecting to download.kiwix.org|51.159.101.162|:443... connected.
HTTP request sent, awaiting response... 200 OK
Length: 27726458912 (25.8G) [application/octet-stream]
Saving to: 'wikipedia_fr_all_maxi_2024-12.zim'

wikipedia_fr_all_ma  2%[>                   ] 523M  5.23MB/s    eta 1h 25m
```

**Progress indicators:**
- `2%` = Percentage complete
- `523M` = Amount downloaded so far
- `5.23MB/s` = Current download speed
- `eta 1h 25m` = Estimated time remaining

**This download takes 1-3 hours on decent connection (25GB file).**

**☕ Perfect time for:**
- Coffee break
- Lunch
- Read ahead in the guide
- Learn about systemd services
- Browse the Prometheus Station documentation

**If download fails:**
- Check internet: `ping 8.8.8.8`
- Check disk space: `df -h` (need 30GB+ free)
- Run the SAME wget command again (it resumes automatically!)

---

### Step 3.3: Monitor Download Progress (Optional)

**Open a SECOND SSH session** (keep first one running wget):

```bash
# From your laptop, open new terminal window
ssh guillain@prometheus-station

# Watch file size grow in real-time (updates every 10 seconds)
watch -n 10 'du -h /var/kiwix/data/*'
```

**What you'll see:**
```
Every 10.0s: du -h /var/kiwix/data/*

2.1G    /var/kiwix/data/wikipedia_fr_all_maxi_2024-12.zim
```

The number increases every 10 seconds as download progresses!

**To stop watching:** Press `Ctrl + C`

**Alternative monitoring:**
```bash
# Show percentage complete
ls -lh /var/kiwix/data/

# Compare to expected final size (25.8G for French Wikipedia)
```

---

### Step 3.4: Download Additional ZIM Files

**Once French Wikipedia completes successfully**, you can add more content:

**Wikipedia English (Full - LARGE):**
```bash
cd /var/kiwix/data

# Find current URL at https://download.kiwix.org/zim/wikipedia/
# Look for: wikipedia_en_all_maxi_YYYY-MM.zim (~90GB)

# Download (REPLACE with current URL!)
wget -c https://download.kiwix.org/zim/wikipedia/wikipedia_en_all_maxi_2024-12.zim
```

**⏱️ Time estimate:** 4-8 hours on 50Mbps connection

---

**Wikimed English (Medical Encyclopedia):**
```bash
cd /var/kiwix/data

# Find current URL at https://download.kiwix.org/zim/wikimed/
# Look for: wikimed_en_all_YYYY-MM.zim (~50GB)

# Download (REPLACE with current URL!)
wget -c https://download.kiwix.org/zim/wikimed/wikimed_en_all_2024-12.zim
```

**⏱️ Time estimate:** 2-4 hours on 50Mbps connection

---

**Wikimed French (Medical Encyclopedia):**
```bash
cd /var/kiwix/data

# Download (REPLACE with current URL!)
wget -c https://download.kiwix.org/zim/wikimed/wikimed_fr_all_2024-12.zim
```

**⏱️ Time estimate:** 30-60 minutes (~6GB)

---

**CRITICAL: Download ONE at a time!** 
- Prevents connection saturation
- Easier to troubleshoot if issues arise
- Better use of bandwidth

**If download is interrupted:**
- Don't panic! ✅
- Run the SAME wget command again
- The `-c` flag resumes from where it stopped
- Example: 50GB downloaded, connection drops → Resume gets remaining 40GB

---

### Step 3.5: Alternative - Smaller Downloads (Save Space)

**If 165GB is too much, consider these space-saving alternatives:**

**Wikipedia WITHOUT images (saves ~40% space):**
```bash
# English without images (~50GB instead of 90GB)
wget -c https://download.kiwix.org/zim/wikipedia/wikipedia_en_all_nopic_2024-12.zim

# French without images (~15GB instead of 25GB)
wget -c https://download.kiwix.org/zim/wikipedia/wikipedia_fr_all_nopic_2024-12.zim
```

**Just one language:**
```bash
# Only French Wikipedia + Wikimed (~31GB total)
wget -c https://download.kiwix.org/zim/wikipedia/wikipedia_fr_all_maxi_2024-12.zim
wget -c https://download.kiwix.org/zim/wikimed/wikimed_fr_all_2024-12.zim
```

**Trade-offs:**
- ✅ Saves significant space (40-60% reduction)
- ✅ Faster downloads (less data)
- ✅ Faster searches (smaller index)
- ❌ No images in articles (text-only for "nopic" versions)
- ❌ Less impressive demonstration
- ❌ Medical diagrams missing in Wikimed "nopic"

**My recommendation:** 
- **Start with:** French Wikipedia (full with images) - 25GB
- **Test everything works** before committing to 90GB English download
- **Upgrade later** if you have space and time

---

### Step 3.6: Verify Downloaded Files

**After EACH download completes:**

```bash
# Check file size and name
ls -lh /var/kiwix/data/
```

**Expected output (example with December 2024 versions):**
```
-rw-r--r-- 1 guillain guillain  90G Dec 26 22:42 wikipedia_en_all_maxi_2024-12.zim
-rw-r--r-- 1 guillain guillain  25G Dec 26 18:15 wikipedia_fr_all_maxi_2024-12.zim
-rw-r--r-- 1 guillain guillain  50G Dec 27 02:47 wikimed_en_all_2024-12.zim
```

**Verification checklist:**
- [ ] Files are 10GB+ each (not a few KB = download failed)
- [ ] Filenames end in `.zim` (correct format)
- [ ] File sizes roughly match expected values above
- [ ] No error messages during download
- [ ] Filenames include year-month (like `2024-12`)

**Optional: Verify file integrity (takes 10-30 minutes per file):**

**Most ZIM files include MD5 checksums.** To verify:

```bash
# Check if .md5 file exists for your download
ls -la /var/kiwix/data/*.md5

# If checksum file exists, verify integrity
md5sum -c wikipedia_fr_all_maxi_2024-12.zim.md5
```

**Expected output:**
```
wikipedia_fr_all_maxi_2024-12.zim: OK
```

**If no .md5 file exists:**
- This is normal - not all ZIM files have checksums
- If file downloaded without errors and is the right size, it's probably fine
- You'll know for sure when Kiwix tries to open it

**If checksum says "FAILED":**
- File is corrupted during download
- Delete it: `rm wikipedia_fr_all_maxi_2024-12.zim`
- Re-download with wget (it should start fresh)

---

## ⚙️ Part 4: Configuring Kiwix Server

### Step 4.1: Create Kiwix Library Catalog

Now we tell Kiwix about all our downloaded ZIM files:

```bash
# Add all ZIM files to library
kiwix-manage /var/kiwix/library/library.xml add /var/kiwix/data/*.zim
```

**What's happening:**
- `kiwix-manage` = Tool for managing the library catalog
- `library.xml` = The catalog file we're updating
- `add` = Command to add files
- `*.zim` = Wildcard matching all ZIM files in data directory

**Expected output:**
```
/var/kiwix/data/wikipedia_en_all_maxi_latest.zim  added
/var/kiwix/data/wikipedia_fr_all_maxi_latest.zim  added
/var/kiwix/data/wikimed_en_all_maxi_latest.zim  added
/var/kiwix/data/wikipedia_en_simple_all_maxi_latest.zim  added
```

---

### Step 4.2: Verify Library Contents

```bash
# Display library contents
cat /var/kiwix/library/library.xml
```

**You should see XML like:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<library version="20110515">
  <book id="wikipedia_en_all_maxi_2025-12"
        name="wikipedia_en_all_maxi"
        title="Wikipedia (English)"
        description="Wikipedia - English"
        language="eng"
        ...>
  </book>
  <book id="wikipedia_fr_all_maxi_2025-12"
        ...>
  </book>
</library>
```

**If file is empty or malformed:**
- Re-run the `kiwix-manage add` command
- Check file permissions on library.xml
- Verify ZIM files exist in /var/kiwix/data/

---

### Step 4.3: Test Kiwix Manually

**Before creating a service, let's test Kiwix manually:**

```bash
# Start Kiwix server on port 8080 (test port)
kiwix-serve --port=8080 --library /var/kiwix/library/library.xml
```

**Expected output:**
```
Listening on 0.0.0.0:8080
```

**This means Kiwix is running!** ✅

**The terminal is now "blocked" (Kiwix is running in foreground). This is normal.**

---

### Step 4.4: Test Access from Browser

**On your laptop** (not on the Pi), open a web browser and go to:

```
http://prometheus-station.local:8080
```

**Or use the IP address:**
```
http://192.168.1.42:8080
```
(Replace with YOUR Pi's IP)

**You should see:**
- Kiwix welcome page
- List of available content (Wikipedia EN, FR, Wikimed, etc.)
- A search bar

**🎉 SUCCESS MOMENT:** Click on "Wikipedia (English)" → Search for "Raspberry Pi" → Article loads!

**If page doesn't load:**
- Check Pi's IP: `hostname -I` on Pi
- Verify firewall: `sudo ufw status` (port 8080 might be blocked)
- Try from Pi itself: `curl http://localhost:8080` should show HTML

---

### Step 4.5: Stop Test Server

**Back in your SSH terminal** where Kiwix is running:

Press `Ctrl + C`

**You'll see:**
```
^C
prometheus@prometheus-station:~ $
```

Server stopped. We'll make it permanent in the next section.

---

## 🔧 Part 5: Creating Systemd Service (Auto-Start)

**Goal:** Make Kiwix start automatically when Pi boots.

### Step 5.1: Create Service File

```bash
# Create systemd service file
sudo nano /etc/systemd/system/kiwix-serve.service
```

**Nano editor opens.** Paste this configuration:

```ini
[Unit]
Description=Kiwix Server - Offline Wikipedia
Documentation=https://www.kiwix.org
After=network.target

[Service]
Type=simple
User=prometheus
Group=prometheus
WorkingDirectory=/var/kiwix
ExecStart=/usr/local/bin/kiwix-serve \
    --port=80 \
    --library=/var/kiwix/library/library.xml \
    --nodatealiases \
    --verbose
Restart=on-failure
RestartSec=10
StandardOutput=journal
StandardError=journal

# Resource limits
MemoryLimit=4G
Nice=10

[Install]
WantedBy=multi-user.target
```

**Understanding this configuration:**

| Line | What It Does |
|------|--------------|
| `User=prometheus` | Run as your user (replace with YOUR username!) |
| `--port=80` | Use standard HTTP port (no :8080 needed) |
| `--library=...` | Path to our library catalog |
| `--nodatealiases` | Don't create date-based aliases (simpler URLs) |
| `Restart=on-failure` | Auto-restart if crashes |
| `MemoryLimit=4G` | Don't use more than 4GB RAM (leaves room for OS) |

**⚠️ CRITICAL:** Change `User=prometheus` and `Group=prometheus` to YOUR username if different!

**Save the file:**
1. Press `Ctrl + X`
2. Press `Y` (yes, save)
3. Press `Enter` (confirm filename)

---

### Step 5.2: Enable and Start Service

```bash
# Reload systemd (recognize new service)
sudo systemctl daemon-reload

# Enable service (start on boot)
sudo systemctl enable kiwix-serve

# Start service NOW
sudo systemctl start kiwix-serve
```

**Expected output:**
```
Created symlink /etc/systemd/system/multi-user.target.wants/kiwix-serve.service → /etc/systemd/system/kiwix-serve.service.
```

This means service is enabled! ✅

---

### Step 5.3: Check Service Status

```bash
# Check if Kiwix is running
sudo systemctl status kiwix-serve
```

**Expected output (healthy service):**
```
● kiwix-serve.service - Kiwix Server - Offline Wikipedia
     Loaded: loaded (/etc/systemd/system/kiwix-serve.service; enabled; preset: enabled)
     Active: active (running) since Thu 2025-12-26 11:15:42 GMT; 5s ago
       Docs: https://www.kiwix.org
   Main PID: 1234 (kiwix-serve)
      Tasks: 5 (limit: 8946)
        CPU: 523ms
     CGroup: /system.slice/kiwix-serve.service
             └─1234 /usr/local/bin/kiwix-serve --port=80 --library=/var/kiwix/library/library.xml

Dec 26 11:15:42 prometheus-station systemd[1]: Started kiwix-serve.service - Kiwix Server - Offline Wikipedia.
Dec 26 11:15:42 prometheus-station kiwix-serve[1234]: Listening on 0.0.0.0:80
```

**Key indicators of success:**
- `Active: active (running)` ← Service is running
- `enabled` ← Will start on boot
- `Listening on 0.0.0.0:80` ← Server started successfully

**If status shows `failed` or `inactive`:**
- Check logs: `sudo journalctl -u kiwix-serve -n 50`
- Common issues:
  - Port 80 already in use
  - Wrong username in service file
  - Permission issues with library files

---

### Step 5.4: Configure Firewall

```bash
# Allow HTTP traffic (port 80)
sudo ufw allow 80/tcp

# Verify firewall rules
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

Both SSH (22) and HTTP (80) are now allowed! ✅

---

### Step 5.5: Test Final Access

**From your laptop's web browser:**

```
http://prometheus-station.local
```

**Or using IP:**
```
http://192.168.1.42
```

**You should see Kiwix WITHOUT needing to specify :8080!**

**Test everything:**
1. **Search Wikipedia:** Type "Raspberry Pi" → Article loads
2. **Check images:** Open any article with photos → Images display
3. **Test French:** Click Wikipedia (French) → Search "Paris" → Français content
4. **Browse Wikimed:** Click Wikimed → Search "Diabetes" → Medical articles

**🎉 If all four work: CONGRATULATIONS! Wikipedia is fully offline and accessible!**

---

## 🔄 Part 6: Verification & Testing

### Step 6.1: Test Auto-Start on Boot

**Let's verify Kiwix starts automatically:**

```bash
# Reboot the Pi
sudo reboot
```

**Your SSH connection will drop.** This is expected.

**Wait 60 seconds**, then:
1. Reconnect via SSH: `ssh prometheus@prometheus-station`
2. Check Kiwix status: `sudo systemctl status kiwix-serve`

**Should show:**
```
Active: active (running) since Thu 2025-12-26 11:20:15 GMT; 1min 23s ago
```

**And in browser:** `http://prometheus-station.local` should load immediately.

If Kiwix is running after reboot: **Auto-start works!** ✅

---

### Step 6.2: Performance Testing

**Search Speed Test:**

1. Open Wikipedia (English)
2. Search for: "Quantum Physics"
3. Note how long results appear

**Typical performance:**
- On 8GB Pi: <1 second
- On 4GB Pi: 1-3 seconds
- On 2GB Pi: 3-5 seconds

**If searches are slow (>5 seconds):**
- Check RAM: `free -h` (should have 2GB+ free)
- Check CPU: `htop` (should be <50% during search)
- Check temperature: `vcgencmd measure_temp` (should be <70°C)

---

### Step 6.3: Monitor Resource Usage

```bash
# Install htop if not already installed
sudo apt install -y htop

# Launch htop
htop
```

**While Kiwix is running and someone is browsing:**

**Look for:**
- **kiwix-serve process** in list (should be near top)
- **CPU usage:** Typically 10-30% per search
- **Memory usage:** 500MB-2GB depending on searches
- **Temperature:** Should stay under 60°C

**Press F10 to quit htop**

---

### Step 6.4: Test from Multiple Devices

**Connect different devices to your network:**

- [ ] **Laptop:** Browse to `http://prometheus-station.local`
- [ ] **Phone:** Same URL (should work on mobile!)
- [ ] **Tablet:** Same URL
- [ ] **Second laptop:** Test concurrent access

**All devices should:**
- Load pages quickly
- Show same content
- Allow simultaneous searches

**This proves the mesh network concept works!** Any device on WiFi = access to Wikipedia.

---

## 📊 Part 7: Monitoring & Maintenance

### Step 7.1: View Kiwix Logs

**To see what Kiwix is doing:**

```bash
# View recent logs
sudo journalctl -u kiwix-serve -n 50

# Follow logs in real-time
sudo journalctl -u kiwix-serve -f
```

**Press Ctrl+C to stop following logs**

**What to look for:**
- `Listening on 0.0.0.0:80` ← Server started
- HTTP requests from devices
- No error messages

**Common log entries:**
```
Dec 26 11:25:34 kiwix-serve[1234]: 192.168.1.50 - - [26/Dec/2025:11:25:34] "GET /wikipedia_en_all_maxi/A/Raspberry_Pi HTTP/1.1" 200 54321
```

This shows: Someone from 192.168.1.50 accessed "Raspberry Pi" article successfully (code 200).

---

### Step 7.2: Update ZIM Files (Future Maintenance)

**Wikipedia is updated monthly.** New versions are released around the 15th of each month with updated article content.

**To get latest content:**

```bash
# 1. Find the newest version
# Browse to https://download.kiwix.org/zim/wikipedia/
# Look for the latest date (e.g., 2025-01 if you currently have 2024-12)

# 2. Navigate to data directory
cd /var/kiwix/data

# 3. Download newer version (REPLACE with actual current URL)
wget -c https://download.kiwix.org/zim/wikipedia/wikipedia_fr_all_maxi_2025-01.zim

# 4. Stop Kiwix service
sudo systemctl stop kiwix-serve

# 5. Remove old file from library
kiwix-manage /var/kiwix/library/library.xml remove wikipedia_fr_all_maxi

# 6. Add new file to library
kiwix-manage /var/kiwix/library/library.xml add /var/kiwix/data/wikipedia_fr_all_maxi_2025-01.zim

# 7. Start Kiwix
sudo systemctl start kiwix-serve

# 8. Verify it's working
# Browse to http://prometheus-station.local and check French Wikipedia loads

# 9. Delete old file (once verified new one works)
rm wikipedia_fr_all_maxi_2024-12.zim
```

**Recommendation:** 
- Update every 3-6 months for fresh content
- Don't need to update monthly unless you want bleeding-edge articles
- Medical content (Wikimed) updates less frequently - check twice a year

**Smart updating strategy:**
- Keep both old and new until verified (safety!)
- Update during low-usage times
- Check disk space before downloading new version
- Always update library.xml after file changes

---

### Step 7.3: Disk Space Monitoring

```bash
# Check space usage
df -h /

# Check Kiwix directory size
du -sh /var/kiwix/data/
```

**If running low on space:**
- Delete test files (Simple English Wikipedia)
- Remove old ZIM backups
- Consider "nopic" versions instead of full

---

## ✅ Final Verification Checklist

Go through this list to confirm everything works:

**Installation:**
- [ ] Kiwix server installed: `kiwix-serve --version` shows version
- [ ] Directories created: `/var/kiwix/data` and `/var/kiwix/library` exist
- [ ] Permissions correct: `ls -la /var/kiwix` shows your username as owner

**Content:**
- [ ] ZIM files downloaded: `ls -lh /var/kiwix/data/*.zim` shows files
- [ ] Library catalog created: `cat /var/kiwix/library/library.xml` shows XML
- [ ] All ZIM files in catalog: `kiwix-manage /var/kiwix/library/library.xml show` lists content

**Service:**
- [ ] Systemd service created: `systemctl status kiwix-serve` shows service
- [ ] Service running: Status shows "active (running)"
- [ ] Service enabled: Shows "enabled" in status
- [ ] Auto-starts on boot: Tested by rebooting

**Network:**
- [ ] Firewall allows HTTP: `sudo ufw status` shows port 80 allowed
- [ ] Accessible by hostname: `http://prometheus-station.local` loads
- [ ] Accessible by IP: `http://192.168.1.x` loads (use your IP)

**Functionality:**
- [ ] Search works: Can search and find articles
- [ ] Images load: Articles with photos display correctly
- [ ] Multiple languages: Both English and French content accessible
- [ ] Mobile works: Phone/tablet can browse

**Performance:**
- [ ] Searches fast: <3 seconds for results
- [ ] Pages load quickly: <2 seconds for articles
- [ ] System stable: No crashes or freezes
- [ ] Temperature good: <65°C under load

**If ALL boxes checked: 🎉 PROMETHEUS STATION IS LIVE! 🎉**

---

## 🛠️ Troubleshooting

### Problem: Service Won't Start

**Symptom:** `systemctl status kiwix-serve` shows "failed"

**Check logs:**
```bash
sudo journalctl -u kiwix-serve -n 100
```

**Common causes:**

**1. Port 80 already in use**
```bash
# Check what's using port 80
sudo netstat -tulpn | grep :80

# Or use lsof
sudo lsof -i :80
```

**Solution:** Stop conflicting service or change Kiwix port to 8080 in service file.

**2. Wrong username in service file**
```bash
# Check your actual username
whoami

# Edit service file
sudo nano /etc/systemd/system/kiwix-serve.service

# Change User= and Group= to match your username
# Save, then:
sudo systemctl daemon-reload
sudo systemctl restart kiwix-serve
```

**3. Permission issues**
```bash
# Fix permissions
sudo chown -R $USER:$USER /var/kiwix
sudo systemctl restart kiwix-serve
```

---

### Problem: Web Interface Not Loading

**Symptom:** Browser shows "Can't connect" or timeout

**Troubleshooting steps:**

**1. Is Kiwix running?**
```bash
sudo systemctl status kiwix-serve
```

Should show "active (running)". If not, check previous troubleshooting section.

**2. Can Pi access itself?**
```bash
curl http://localhost
```

Should return HTML. If yes, Kiwix works but network issue.

**3. Is firewall blocking?**
```bash
sudo ufw status
```

Should show `80/tcp ALLOW Anywhere`. If not:
```bash
sudo ufw allow 80/tcp
```

**4. Wrong IP address?**
```bash
hostname -I
```

Use this IP in browser instead of hostname.

**5. Network issue?**
```bash
# Can you ping the Pi?
ping prometheus-station.local

# From your laptop
```

---

### Problem: Search Returns No Results

**Symptom:** Can load Kiwix but searches return empty

**Causes:**

**1. ZIM file incomplete/corrupted**
```bash
# Check file size
ls -lh /var/kiwix/data/

# Should be GBs, not KBs
```

**Solution:** Re-download ZIM file.

**2. Library not updated**
```bash
# Rebuild library
kiwix-manage /var/kiwix/library/library.xml remove wikipedia_en_all_maxi
kiwix-manage /var/kiwix/library/library.xml add /var/kiwix/data/*.zim

# Restart service
sudo systemctl restart kiwix-serve
```

**3. Wrong ZIM file selected**
- Check you clicked correct Wikipedia in Kiwix interface
- Some content has search disabled

---

### Problem: Slow Performance

**Symptom:** Searches take >10 seconds, pages load slowly

**Diagnostics:**

```bash
# Check RAM
free -h

# Check CPU
htop

# Check temperature
vcgencmd measure_temp

# Check disk I/O
iostat 1 5
```

**Solutions:**

**1. Not enough free RAM**
```bash
# Disable services
sudo systemctl stop bluetooth
sudo systemctl stop cups  # If printer service installed

# Restart Kiwix
sudo systemctl restart kiwix-serve
```

**2. Overheating (>70°C)**
- Add heatsink
- Improve airflow
- Add fan
- Check `vcgencmd get_throttled` (should show `0x0`)

**3. Slow SD card**
```bash
# Test SD card speed
sudo dd if=/dev/zero of=/tmp/testfile bs=1M count=100 oflag=direct

# Should show >30 MB/s write speed
# If slower, SD card might be fake or failing
```

**4. Too many concurrent users**
- Limit to 5-10 users maximum on Pi 4
- Consider faster hardware for more users

---

### Problem: Images Not Loading

**Symptom:** Articles load but images show broken icon

**Causes:**

**1. Using "nopic" version**
- Check filename: `ls /var/kiwix/data/`
- If says "nopic", that's expected (no images in that version)

**2. Network issue**
- Try different article
- Check browser console (F12) for errors

**3. ZIM file corrupted**
```bash
# Verify integrity
cd /var/kiwix/data
md5sum wikipedia_en_all_maxi_latest.zim
```

Compare with checksum from download.kiwix.org

---

### Problem: Can't Access After Reboot

**Symptom:** Worked before reboot, now doesn't load

**Check service started:**
```bash
sudo systemctl status kiwix-serve
```

**If not running:**
```bash
sudo systemctl start kiwix-serve

# Check why it didn't auto-start
sudo journalctl -u kiwix-serve -b
```

**If IP changed:**
```bash
hostname -I
```

Use new IP in browser, or stick to `prometheus-station.local` hostname.

---

## 🎯 Performance Benchmarks

**Document your results for future reference:**

**Hardware:** Raspberry Pi 4 (8GB)  
**SD Card:** SanDisk Extreme 256GB A2

**Search Performance:**
- Simple query ("Paris"): _______ seconds
- Complex query ("Quantum Physics"): _______ seconds
- Multi-word ("Raspberry Pi Foundation"): _______ seconds

**Page Load Times:**
- Text article: _______ seconds
- Article with images: _______ seconds
- Long article (>10,000 words): _______ seconds

**Concurrent Users:**
- Max tested: _______ users
- Performance degraded at: _______ users

**Resource Usage (under load):**
- CPU: _______% average
- RAM: _______ GB used
- Temperature: _______°C

**Startup Time:**
- Service start after boot: _______ seconds
- First search response: _______ seconds

---

## 🎓 What You've Learned

Congratulations! You've just:

✅ **Installed a web server** (Kiwix)  
✅ **Downloaded massive datasets** (165GB+ Wikipedia)  
✅ **Managed disk space** (verified capacity, organized files)  
✅ **Created systemd services** (auto-start configuration)  
✅ **Configured firewall rules** (allowed HTTP traffic)  
✅ **Troubleshot network issues** (hostname vs IP, ports)  
✅ **Monitored system resources** (RAM, CPU, logs)  
✅ **Deployed a real web application** (accessible by multiple devices)

**These skills are directly transferable to:**
- Any web server deployment
- Cloud computing (same systemd concepts)
- DevOps workflows
- Self-hosting services (Nextcloud, Plex, etc.)

**You're now a sysadmin AND a digital librarian!** 📚🎉

---

## 📚 Useful Commands Reference

**Service Management:**
```bash
sudo systemctl status kiwix-serve      # Check status
sudo systemctl start kiwix-serve       # Start service
sudo systemctl stop kiwix-serve        # Stop service
sudo systemctl restart kiwix-serve     # Restart service
sudo systemctl enable kiwix-serve      # Enable auto-start
sudo systemctl disable kiwix-serve     # Disable auto-start
```

**Monitoring:**
```bash
sudo journalctl -u kiwix-serve -f      # Follow logs live
sudo journalctl -u kiwix-serve -n 100  # Last 100 log lines
htop                                    # Resource monitor
df -h                                   # Disk space
free -h                                 # RAM usage
vcgencmd measure_temp                   # CPU temperature
```

**Kiwix Management:**
```bash
kiwix-serve --version                                    # Check version
kiwix-manage library.xml show                            # List content
kiwix-manage library.xml add file.zim                    # Add ZIM file
kiwix-manage library.xml remove content_id               # Remove content
```

**Network:**
```bash
hostname -I                             # Show IP address
sudo ufw status                         # Firewall rules
sudo ufw allow 80/tcp                   # Open port 80
sudo netstat -tulpn | grep :80          # Check port 80 usage
```

**File Management:**
```bash
ls -lh /var/kiwix/data/                 # List ZIM files
du -sh /var/kiwix/data/                 # Total size
md5sum file.zim                         # Verify integrity
wget -c URL                             # Resume download
```

---

## 🚀 Next Steps

**Your Prometheus Station now has offline knowledge!**

**What's next:**

**→ [03 - Meshtastic Setup](03-meshtastic-setup.md)**

In Step 3, you'll:
- Install LoRa mesh networking hardware
- Configure long-range communication (1-15km+)
- Connect T-Beam and T-Echo devices
- Test mesh messaging
- Integrate with Raspberry Pi

**Estimated time:** 1-2 hours

**Or, if you want to test what you have first:**
- Add more content (TED Talks, Gutenberg books, Stack Exchange)
- Optimize performance (caching, compression)
- Setup remote access (Tailscale to access from anywhere)
- Create custom landing page

See you in Step 3! 🔥

---

## 📖 Additional Resources

**Official Documentation:**
- [Kiwix Documentation](https://wiki.kiwix.org/)
- [ZIM File Library](https://library.kiwix.org/)
- [Kiwix on GitHub](https://github.com/kiwix)

**Download More Content:**
- [All ZIM Files](https://download.kiwix.org/zim/)
- [Wikipedia Downloads](https://download.kiwix.org/zim/wikipedia/)
- [Project Gutenberg](https://download.kiwix.org/zim/gutenberg/)
- [TED Talks](https://download.kiwix.org/zim/ted/)
- [Stack Exchange](https://download.kiwix.org/zim/stack_exchange/)

**Community:**
- [Kiwix on Reddit](https://reddit.com/r/kiwix)
- [Offline Content Discussion](https://reddit.com/r/DataHoarder)

**Performance Tuning:**
- [Kiwix Server Optimization](https://wiki.kiwix.org/wiki/Kiwix-serve)
- [Raspberry Pi Performance Tips](https://www.raspberrypi.com/documentation/computers/config_txt.html)

---

**Last updated:** December 2025  
**Tested on:** Raspberry Pi 4 (8GB), Raspberry Pi OS Lite (64-bit), Kiwix 3.5.0  
**Written by:** Guillain d'Erceville (Prometheus Station Project)

*Questions? Found an error? Open an issue on [GitHub](https://github.com/GuillainM/Prometheus-Station/issues)!*

---

**🔥 You're bringing fire to humanity, one ZIM file at a time! 🔥**
