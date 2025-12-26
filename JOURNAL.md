# Prometheus Station - Build Journal

**Builder:** Guillain d'Erceville  
**Project Start:** December 26, 2025  
**Location:** France  
**Goal:** Build a solar-powered offline knowledge hub with LoRa mesh networking

---

## Day 0 - December 26, 2025 (Morning)

### Project Kickoff

**What happened today:**
- Received all hardware components (see HARDWARE.md)
- Organized workspace
- Set up GitHub repository
- Created initial documentation structure

**Hardware acquired:** ✅
- Raspberry Pi 4 (8GB RAM)
- SanDisk Extreme 256GB microSD (A2 class)
- LILYGO T-Beam 868MHz LoRa module
- Anker Solix PS30 solar panel (30W)
- Anker PowerCore 737 battery (24,000mAh)
- Spiderbeam 7m fiberglass mast
- All cables and accessories

**Total investment:** ~570€

**Documentation created:**
- README.md (project overview)
- HARDWARE.md (complete bill of materials)
- Installation guides structure
- This journal!

**Mindset:** Excited and slightly nervous. I've never built anything like this before, but the guides seem clear. Let's see if I can actually do this!

---

## Day 1 - December 26, 2025 (Afternoon)

### ✅ Step 1: Raspberry Pi Setup - COMPLETED

**Total time:** ~1 hour 45 minutes  
**Difficulty experienced:** ⭐⭐☆☆☆ Easy (as promised!)

---

### Phase 1: SD Card Preparation (30 minutes)

#### What I did:

1. **Downloaded Raspberry Pi Imager v2.0.0**
   - Source: https://www.raspberrypi.com/software/
   - File size: ~25 MB
   - Installation: 2 minutes

2. **Flashed Raspberry Pi OS Lite (64-bit)**
   - Path: Choose OS → Raspberry Pi OS (other) → Raspberry Pi OS Lite (64-bit)
   - Target: SanDisk Extreme 256GB microSD
   - Download size: ~483 MB

3. **Configured headless setup** (the "magic" part!)
   - Clicked NEXT → EDIT SETTINGS
   - New tabbed interface in Imager v2.0 (cleaner than expected!)

**Settings configured:**

**Hostname tab:**
- Hostname: `prometheus-station`
- Why: Easier to remember than IP address

**User tab:**
- Username: `guillain` (personal choice, not "prometheus" from guide)
- Password: [strong password set]
- Why custom username: Better security than default

**Wi-Fi tab:**
- SSID: [my home network]
- Password: [configured]
- Country: FR (France)
- Result: Pi will connect to WiFi on first boot automatically

**Localisation tab:**
- Timezone: Europe/Paris
- Keyboard: fr (AZERTY)

**Remote access tab:**
- ✅ Enable SSH
- Authentication: Use password
- Critical: Without this, I'd need monitor/keyboard forever

#### Time breakdown:
- Download Imager: 2 min
- Configure all settings: 8 min
- Write to SD card: 12 min
- Verification: 5 min
- Safe eject: 1 min
- **Total: 28 minutes**

#### Notes:
- SanDisk Extreme A2 writes fast (12 min for 483MB + verification)
- Imager v2.0 interface is very intuitive
- Headless config saved SO MUCH TIME (no monitor/keyboard setup needed)

---

### Phase 2: First Boot & SSH Connection (20 minutes)

#### Hardware setup:

1. Inserted microSD card into Raspberry Pi 4
   - Card slot on underside (spring-loaded)
   - Clicked into place perfectly

2. Connected official USB-C power supply (5V 3A)
   - No power button, just plug and go
   - Red LED: steady (power good)
   - Green LED: blinking (reading SD card)

3. Waited for boot
   - ~30 seconds: Green LED rapid blinking
   - ~60 seconds: Green LED occasional flashes (boot complete)
   - Total boot time: About 45 seconds

#### Finding the Pi's IP address:

**Method used:** Router admin page
- Logged into router at 192.168.1.1
- Found device list
- Spotted "prometheus-station" immediately
- IP assigned: `192.168.1.41`

#### First SSH connection:

```powershell
ssh guillain@prometheus-station
```

**First-time security prompt:**
```
The authenticity of host 'prometheus-station (192.168.1.41)' can't be established.
ED25519 key fingerprint is SHA256:fIhIFX6kZYXAXoLgxPbqDLquacySa9GKz05kdrLtXaA.
Are you sure you want to continue connecting (yes/no/[fingerprint])?
```

Typed: `yes`

Entered password.

**SUCCESS!** 🎉

```
Linux Prometheus-Station 6.12.47+rpt-rpi-v8 #1 SMP PREEMPT Debian 1:6.12.47-1+rpt1 (2025-09-16) aarch64

guillain@Prometheus-Station:~ $
```

**First impressions:**
- Headless setup worked PERFECTLY
- No monitor needed at any point
- Hostname resolution worked immediately
- Modern kernel (6.12.47, newer than guide mentioned!)

---

### Phase 3: SSH Key Authentication Setup (10 minutes)

#### The problem:
Typing password for every SSH connection is annoying. I knew I'd be connecting dozens of times during this build.

#### The solution: SSH keys

**What I learned:**
- SSH keys use public/private key cryptography
- Private key stays on my PC (secret)
- Public key goes on the Pi (shareable)
- More secure than passwords AND more convenient

#### Step-by-step what I did:

**1. Generated SSH key pair on Windows:**

```powershell
ssh-keygen -t ed25519 -C "guillain@prometheus-station"
```

- Chose ED25519 (modern, secure, fast)
- Saved to default location: `C:\Users\loutr\.ssh\id_ed25519`
- No passphrase (for convenience)
- Generated in ~2 seconds

**2. Copied public key to Pi:**

```powershell
type $env:USERPROFILE\.ssh\id_ed25519.pub | ssh guillain@prometheus-station "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys"
```

- Had to type password ONE LAST TIME
- Command creates `.ssh` folder on Pi and adds my public key

**3. Secured permissions on Pi:**

Connected via SSH, then:

```bash
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
```

Why: Prevents other users from reading my authorized keys

**4. Created SSH alias for ultra-fast connection:**

On Windows, created file: `C:\Users\loutr\.ssh\config`

```powershell
notepad $env:USERPROFILE\.ssh\config
```

Added this content:
```
Host prometheus
    HostName prometheus-station
    User guillain
    IdentityFile C:\Users\loutr\.ssh\id_ed25519
```

**5. Tested the magic:**

```powershell
ssh prometheus
```

**INSTANT CONNECTION. NO PASSWORD.** 🚀

**Time saved:**
- Before: `ssh guillain@prometheus-station` + type password (10 seconds)
- After: `ssh prometheus` + instant (2 seconds)
- Over 100+ connections during build: ~13 minutes saved!

**Why this is brilliant:**
- More secure (2048-bit key vs guessable password)
- Faster (no typing)
- Works with scp, rsync, git, etc.
- Industry standard (how professionals work)

---

### Phase 4: Initial System Configuration (45 minutes)

#### System updates:

```bash
sudo apt update
sudo apt upgrade -y
```

**Results:**
- 47 packages needed updating
- Download size: ~68.2 MB
- Time: ~35 minutes (my internet is decent but not amazing)

**What was updated:**
- Security patches
- Kernel stayed at 6.12.47 (already latest)
- Various system libraries
- Debian base packages

**Observation:** First update always takes longest. Future updates will be faster.

#### raspi-config settings:

```bash
sudo raspi-config
```

**Changes made:**

1. **Advanced Options → Expand Filesystem**
   - Made entire 256GB available (was limited to ~2GB)
   - Critical for Wikipedia files later

2. **Performance Options → GPU Memory**
   - Set to 16 MB (minimum)
   - Why: Headless server doesn't need GPU RAM
   - Freed up ~240 MB for Kiwix

3. **Interface Options → SSH**
   - Verified enabled (already was from Imager config)

4. **Reboot to apply changes**
   ```bash
   sudo reboot
   ```

Waited 30 seconds, reconnected:
```powershell
ssh prometheus
```

Still works! ✅

#### Essential packages installed:

```bash
sudo apt install -y git curl wget vim htop ufw
```

**What each does:**
- `git`: Download code from GitHub
- `curl` / `wget`: Download files
- `vim`: Text editor (I prefer it over nano)
- `htop`: Beautiful process monitor
- `ufw`: Firewall (security)

**Installation time:** ~2 minutes

#### Firewall configuration:

```bash
# Allow SSH (critical to do this FIRST!)
sudo ufw allow 22/tcp

# Allow Kiwix web server (for later)
sudo ufw allow 80/tcp

# Enable firewall
sudo ufw enable
```

**Checked status:**
```bash
sudo ufw status
```

```
Status: active

To                         Action      From
--                         ------      ----
22/tcp                     ALLOW       Anywhere
80/tcp                     ALLOW       Anywhere
```

Perfect! ✅

**Why allow port 22 first?**
If I enabled UFW without allowing SSH, my connection would drop and I'd be locked out. Always allow SSH before enabling firewall!

#### Performance optimizations:

**1. Disabled swap:**

```bash
sudo dphys-swapfile swapoff
sudo systemctl disable dphys-swapfile
```

Why: SD cards wear out from constant writing. With 8GB RAM, we don't need swap.

Verified:
```bash
free -h
```
```
              total        used        free      shared  buff/cache   available
Mem:          7.8Gi       156Mi       7.4Gi       8.0Mi       287Mi       7.5Gi
Swap:            0B          0B          0B
```

Swap: 0B ✅

**2. Disabled unnecessary services:**

```bash
sudo systemctl disable bluetooth.service
sudo systemctl disable hciuart.service
sudo systemctl disable alsa-state.service
```

**RAM saved:** ~50-100 MB  
**Boot time saved:** ~2-3 seconds  
**Why:** Headless server doesn't need Bluetooth or audio

#### Created system monitoring script:

```bash
nano ~/system_status.sh
```

Pasted the monitoring script from guide, saved.

```bash
chmod +x ~/system_status.sh
```

**Tested:**
```bash
~/system_status.sh
```

**Output:**
```
======================================
 PROMETHEUS STATION - System Status
======================================

Uptime:
 14:23:14 up 45 min,  1 user,  load average: 0.08, 0.12, 0.09

CPU Temperature:
temp=42.8'C

Memory Usage:
               total        used        free      shared  buff/cache   available
Mem:           7.8Gi       156Mi       7.4Gi       8.0Mi       287Mi       7.5Gi
Swap:             0B          0B          0B

Disk Usage:
/dev/root       233G  2.1G  220G   1% /

Network Interfaces:
lo               UNKNOWN        127.0.0.1/8 ::1/128 
wlan0            UP             192.168.1.41/24 

Active SSH Connections:
guillain pts/0        2025-12-26 14:23 (192.168.1.50)

======================================
```

**This is SO useful!** Quick health check anytime.

---

### Final Verification Checklist

Going through the guide's checklist:

**System Access:**
- ✅ Can SSH into Pi: `ssh prometheus` (instant, no password!)
- ✅ Filesystem expanded: `df -h` shows 233G total
- ✅ System updated: `sudo apt update` shows 0 updates

**Configuration:**
- ✅ Hostname correct: `hostname` returns `Prometheus-Station`
- ✅ GPU memory: `vcgencmd get_mem gpu` returns `gpu=16M`
- ✅ SSH enabled: `systemctl status ssh` shows "active (running)"

**Security:**
- ✅ Firewall active: `sudo ufw status` shows "Status: active"
- ✅ SSH allowed: Port 22 in rules
- ✅ Kiwix port ready: Port 80 in rules

**Performance:**
- ✅ Swap disabled: `free -h` shows Swap: 0B
- ✅ Bluetooth disabled: `systemctl status bluetooth` shows "inactive (dead)"
- ✅ Monitoring script works: `~/system_status.sh` runs perfectly

**System Health:**
- ✅ Temperature: 42.8°C (excellent, well under 60°C limit)
- ✅ Free RAM: 7.4 GB (tons of headroom)
- ✅ CPU load: 0.08 (basically idle)

**ALL CHECKBOXES TICKED!** ✅

---

### What I Learned Today

**Technical skills acquired:**
- Flashing OS to SD card with preconfiguration
- Headless Raspberry Pi setup (no monitor needed!)
- SSH key generation and public key authentication
- Linux firewall configuration (UFW)
- System service management (systemd)
- Performance tuning (swap, GPU memory, services)

**Concepts understood:**
- Why SSH keys beat passwords (security + convenience)
- How headless setup saves massive time
- Importance of proper permissions (chmod 700/600)
- Firewall rules and port management
- RAM vs swap trade-offs

**Commands I'm now comfortable with:**
- `ssh` / `ssh-keygen` (remote access)
- `sudo apt update/upgrade` (package management)
- `sudo systemctl` (service control)
- `sudo ufw` (firewall)
- `chmod` (file permissions)
- `free` / `df` / `htop` (system monitoring)

---

### Problems Encountered

#### 1. SSH Password Annoyance
**Issue:** Having to type password for every connection  
**Impact:** Wasted ~10 seconds per connection  
**Solution:** SSH key authentication  
**Time to fix:** 10 minutes  
**Result:** Now connects in 2 seconds, no password  
**Lesson:** Industry best practice exists for a reason!

#### 2. PowerShell vs Bash Syntax
**Issue:** Git commands from guide used `&&` (Bash syntax)  
**Impact:** PowerShell threw errors  
**Solution:** Use `;` instead of `&&` in PowerShell  
**Example:**
```powershell
# Wrong (Bash):
git add . && git commit -m "msg" && git push

# Right (PowerShell):
git add . ; git commit -m "msg" ; git push
```
**Lesson:** Windows != Linux, syntax differs

#### 3. Markdown Confusion
**Issue:** Copied ``` markdown formatters into PowerShell  
**Impact:** PowerShell tried to execute ```, **Ajoute, etc.  
**Solution:** Only copy actual commands, not formatting  
**Lesson:** Triple backticks are for documentation display, not execution!

---

### Discoveries & Observations

**What worked brilliantly:**
- Headless setup is AMAZING (never touched monitor/keyboard)
- Raspberry Pi Imager v2.0 interface is very polished
- Hostname resolution works perfectly on Windows
- Native SSH in Windows PowerShell (no PuTTY needed)
- Boot time is fast (~45 seconds cold start)

**Hardware observations:**
- Pi 4 runs cool (42°C idle with fan)
- No "low voltage" warnings (good power supply matters!)
- WiFi signal excellent (-45 dBm, Pi is 5m from router)
- SanDisk Extreme A2 is noticeably fast

**Unexpected discoveries:**
- Kernel is 6.12.47 (guide mentioned 6.1.x - OS is actively updated!)
- Raspberry Pi OS is Debian-based (familiar territory)
- UFW is simpler than iptables (thank goodness)

---

### Time Analysis

| Phase | Guide Estimate | Actual Time | Difference |
|-------|----------------|-------------|------------|
| SD Card Prep | 15-20 min | 28 min | +8 min (first time, learning interface) |
| First Boot & IP | 2-5 min | 20 min | +15 min (exploring router, testing) |
| SSH Key Setup | Not in guide | 10 min | New addition (worth it!) |
| System Config | 30-45 min | 45 min | Right on target |
| **TOTAL** | **~50-70 min** | **1h 45min** | **Reasonable for first build** |

**Reflection:** 
- First-time builds always take longer (learning curve)
- Guide estimates seem accurate for repeat builds
- Extra time spent on SSH keys will save time throughout project
- No major blockers, just learning as I go

---

### Statistics

**Commands run:** ~35  
**Packages installed:** 53 (47 updates + 6 new)  
**Data downloaded:** ~68 MB (updates) + ~483 MB (OS) = ~551 MB  
**SSH connections made:** ~15  
**Reboots:** 2  
**Errors encountered:** 0 (everything worked!)  
**Cups of coffee:** 2 ☕☕

---

### Next Steps

**Completed today:**
- ✅ Raspberry Pi OS installed and configured
- ✅ SSH access working (with key auth!)
- ✅ System updated and optimized
- ✅ Firewall configured
- ✅ Monitoring tools in place

**Ready for tomorrow:**
- ⭐ **Step 2: Kiwix Installation**
  - Install Kiwix server software
  - Download medical content (Strategy 1: Emergency Medical Pack)
  - Configure systemd service
  - Test web interface

**Questions for next session:**
- Should I download ZIM files on Pi or on my PC and transfer?
- How long will 5.5GB download take? (my connection: ~50 Mbps down)
- Can Kiwix serve one ZIM file while downloading others?

---

### Personal Notes

**Mood:** 😃 Very satisfied!

**Highlights:**
- Everything worked on first try (amazing feeling!)
- SSH keys are a game-changer
- Headless setup saves SO much hassle
- Documentation was clear and accurate

**Challenges:**
- Minor confusion with PowerShell syntax (expected)
- Copied markdown formatting by mistake (embarrassing but funny)

**Confidence level:**
- Before: 6/10 (nervous about Linux)
- After: 8/10 (I can do this!)

**What surprised me:**
- How easy headless setup actually is
- How fast the Pi boots
- How well Windows SSH works
- How useful the monitoring script is

**Looking forward to:**
- Getting medical content running (the humanitarian mission!)
- Testing LoRa mesh network (Step 3)
- Solar power setup (Step 5)
- First field deployment (Step 6)

---

**End of Day 1**  
**Time invested today:** 1h 45min  
**Progress:** Step 1/6 complete (17%)  
**Status:** ✅ On track, feeling good!

**Tomorrow's goal:** Get Kiwix serving medical content  
**Estimated time:** 2-3 hours (download + configuration)

---

*Journal entry completed at 15:30, December 26, 2025*

---

## Day 2 - December 26, 2025 (Evening)

### 📚 Content Strategy Research & Guide Updates

**Total time:** ~2 hours 45 minutes  
**Difficulty experienced:** ⭐⭐⭐☆☆ Medium (navigating ZIM files structure)

---

### What Happened Today

After completing the Pi setup yesterday, I started researching **what content to actually download** for Prometheus Station. This turned into a deep dive into medical content for disaster response.

**Key realization:** The original guide suggested downloading "Wikimed" (~50GB) but that project **doesn't exist in the Kiwix directory structure!** 

This sent me on a hunt through Kiwix's servers to find the **actual medical content** used by humanitarian organizations.

---

### Phase 1: The Wikimed Wild Goose Chase (45 minutes)

#### Initial confusion:

Started by browsing: `https://download.kiwix.org/zim/wikipedia/`

Looking for files like:
```
wikimed_en_all_maxi_YYYY-MM.zim  ❌ DOESN'T EXIST
wikimed_fr_all_maxi_YYYY-MM.zim  ❌ DOESN'T EXIST
```

**Problem:** The guide (and many online sources) reference "Wikimed" but it's not in the `/zim/wikimed/` directory because **that directory doesn't exist**!

#### Investigation steps:

1. **Checked main ZIM direc