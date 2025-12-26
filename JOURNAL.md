# ðŸ“” Prometheus Station - Build Journal

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

**Hardware acquired:** âœ…
- Raspberry Pi 4 (8GB RAM)
- SanDisk Extreme 256GB microSD (A2 class)
- LILYGO T-Beam 868MHz LoRa module
- Anker Solix PS30 solar panel (30W)
- Anker PowerCore 737 battery (24,000mAh)
- Spiderbeam 7m fiberglass mast
- All cables and accessories

**Total investment:** ~570â‚¬

**Documentation created:**
- README.md (project overview)
- HARDWARE.md (complete bill of materials)
- Installation guides structure
- This journal!

**Mindset:** Excited and slightly nervous. I've never built anything like this before, but the guides seem clear. Let's see if I can actually do this!

---

## Day 1 - December 26, 2025 (Afternoon)

### âœ… Step 1: Raspberry Pi Setup - COMPLETED

**Total time:** ~1 hour 45 minutes  
**Difficulty experienced:** â­â­â˜†â˜†â˜† Easy (as promised!)

---

### Phase 1: SD Card Preparation (30 minutes)

#### What I did:

1. **Downloaded Raspberry Pi Imager v2.0.0**
   - Source: https://www.raspberrypi.com/software/
   - File size: ~25 MB
   - Installation: 2 minutes

2. **Flashed Raspberry Pi OS Lite (64-bit)**
   - Path: Choose OS â†’ Raspberry Pi OS (other) â†’ Raspberry Pi OS Lite (64-bit)
   - Target: SanDisk Extreme 256GB microSD
   - Download size: ~483 MB

3. **Configured headless setup** (the "magic" part!)
   - Clicked NEXT â†’ EDIT SETTINGS
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
- âœ… Enable SSH
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

**Alternative I could have used:**
```powershell
ping prometheus-station.local
```
(Works on Windows 10+, would have shown IP)

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

**SUCCESS!** ðŸŽ‰

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

**INSTANT CONNECTION. NO PASSWORD.** ðŸš€

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

1. **Advanced Options â†’ Expand Filesystem**
   - Made entire 256GB available (was limited to ~2GB)
   - Critical for Wikipedia files later

2. **Performance Options â†’ GPU Memory**
   - Set to 16 MB (minimum)
   - Why: Headless server doesn't need GPU RAM
   - Freed up ~240 MB for Kiwix

3. **Interface Options â†’ SSH**
   - Verified enabled (already was from Imager config)

4. **Reboot to apply changes**
   ```bash
   sudo reboot
   ```

Waited 30 seconds, reconnected:
```powershell
ssh prometheus
```

Still works! âœ…

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

Perfect! âœ…

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

Swap: 0B âœ…

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
- âœ… Can SSH into Pi: `ssh prometheus` (instant, no password!)
- âœ… Filesystem expanded: `df -h` shows 233G total
- âœ… System updated: `sudo apt update` shows 0 updates

**Configuration:**
- âœ… Hostname correct: `hostname` returns `Prometheus-Station`
- âœ… GPU memory: `vcgencmd get_mem gpu` returns `gpu=16M`
- âœ… SSH enabled: `systemctl status ssh` shows "active (running)"

**Security:**
- âœ… Firewall active: `sudo ufw status` shows "Status: active"
- âœ… SSH allowed: Port 22 in rules
- âœ… Kiwix port ready: Port 80 in rules

**Performance:**
- âœ… Swap disabled: `free -h` shows Swap: 0B
- âœ… Bluetooth disabled: `systemctl status bluetooth` shows "inactive (dead)"
- âœ… Monitoring script works: `~/system_status.sh` runs perfectly

**System Health:**
- âœ… Temperature: 42.8Â°C (excellent, well under 60Â°C limit)
- âœ… Free RAM: 7.4 GB (tons of headroom)
- âœ… CPU load: 0.08 (basically idle)

**ALL CHECKBOXES TICKED!** âœ…

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
- Pi 4 runs cool (42Â°C idle with fan)
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
**Cups of coffee:** 2 â˜•â˜•

---

### Next Steps

**Completed today:**
- âœ… Raspberry Pi OS installed and configured
- âœ… SSH access working (with key auth!)
- âœ… System updated and optimized
- âœ… Firewall configured
- âœ… Monitoring tools in place

**Ready for tomorrow:**
- â­ï¸ **Step 2: Kiwix Installation**
  - Install Kiwix server software
  - Download Wikipedia EN (~90GB) - this will take a while!
  - Configure systemd service
  - Test web interface

**Optional (considering):**
- Install Tailscale for remote access (Step 3.3b)
  - Would let me access Pi from anywhere
  - Seems very useful for monitoring during deployment
  - Only takes 5 minutes according to guide

**Questions for next session:**
- Should I download Wikipedia on Pi or on my PC and transfer?
- How long will 90GB download take? (my connection: ~50 Mbps down)
- Can Kiwix serve one ZIM file while downloading others?

---

### Photos & Documentation

**Photos taken today:** ðŸ“· None  
**Should have photographed:**
- [ ] Raspberry Pi hardware setup
- [ ] SD card inserted
- [ ] First SSH connection (screenshot)
- [ ] System status output

**Action:** Take photos during Step 2 for documentation

---

### Personal Notes

**Mood:** ðŸ˜ƒ Very satisfied!

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
- Getting Wikipedia running (the "wow" moment)
- Testing LoRa mesh network (Step 3)
- Solar power setup (Step 5)
- First field deployment (Step 6)

---

**End of Day 1**  
**Time invested today:** 1h 45min  
**Progress:** Step 1/6 complete (17%)  
**Status:** âœ… On track, feeling good!

**Tomorrow's goal:** Get Kiwix serving Wikipedia  
**Estimated time:** 3-4 hours (mostly downloading)

---

*Journal entry completed at 15:30, December 26, 2025*

---

## Day 2 - December 26, 2025 (Evening)

### 📚 Content Strategy Research & Guide Updates

**Total time:** ~2 hours  
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

1. **Checked main ZIM directory:**
   ```bash
   curl -s https://download.kiwix.org/zim/ | grep -i "med"
   ```
   Result: No `/wikimed/` directory

2. **Found Wikipedia medicine subsets instead:**
   ```
   wikipedia_en_medicine_maxi_2025-09.zim (~1.9 GB) ✅
   wikipedia_fr_medicine_maxi_2025-09.zim (~1.1 GB) ✅
   ```

3. **Explored `/zim/other/` directory:**
   ```bash
   curl -s https://download.kiwix.org/zim/other/ | grep -E "med|disaster"
   ```
   
   **JACKPOT!** Found actual humanitarian medical content:
   ```
   zimgit-post-disaster_en_2024-05.zim (615 MB) ✅
   mdwiki_en_all_maxi_2025-11.zim (2.1 GB) ✅
   wikem_en_all_maxi_2021-02.zim (42 MB) ✅
   ```

**Lesson learned:** Don't trust old documentation blindly. Always verify file locations directly on Kiwix servers.

---

### Phase 2: Understanding Medical Content Sources (30 minutes)

Did research on what each medical ZIM actually contains:

#### **zimgit-post-disaster** (615 MB)
- **Source:** WHO/Medical field guides
- **Content:** Disaster medicine, mass casualties, field conditions
- **Used by:** MSF, ICRC, Red Cross field teams
- **Last updated:** 2024-05
- **Perfect for:** Emergency response scenarios

#### **WikEM** (42 MB)
- **Source:** Emergency physicians community
- **Content:** ER protocols, trauma care, toxicology
- **Used by:** Emergency departments, field medics
- **Last updated:** 2021 (protocols stable)
- **Perfect for:** Acute medical emergencies

#### **MDWiki** (2.1 GB)
- **Source:** Medical community wiki
- **Content:** Comprehensive medical encyclopedia
- **Used by:** Medical education, reference
- **Last updated:** Monthly (2025-11 latest)
- **Perfect for:** Detailed medical knowledge

#### **Wikipedia Medicine** (1.9 GB EN + 1.1 GB FR)
- **Source:** Wikipedia editors
- **Content:** Filtered medical articles only
- **Last updated:** Monthly (2025-09 latest)
- **Perfect for:** General medical knowledge

#### **Bonus finds:**
```
zimgit-water_en_2024-08.zim (20 MB) - Water purification
zimgit-food-preparation_en_2025-04.zim (93 MB) - Food safety
librepathology_en_all_maxi_2025-09.zim (76 MB) - Pathology
```

**Total medical pack:** ~5.5 GB (way more practical than imaginary 50GB Wikimed!)

---

### Phase 3: Content Strategy Development (45 minutes)

Realized that **different missions need different content**. Created three deployment strategies:

#### 🏥 **Strategy 1: Emergency Medical Pack (5.5 GB)**
**Target:** Humanitarian missions, disaster zones
- Post-disaster protocols
- Emergency medicine wiki
- Medical encyclopedia
- Water & food safety
- Wikipedia medicine (EN + FR)

**Rationale:** MSF/ICRC don't need full Wikipedia, they need **focused medical content**.

#### 📚 **Strategy 2: Full Knowledge Base (120-150 GB)**
**Target:** Permanent installations, educational centers
- Complete Wikipedia (EN + FR)
- All medical content from Strategy 1
- Comprehensive resources

**Rationale:** Remote schools/communities benefit from full encyclopedia.

#### 🎒 **Strategy 3: Minimal Emergency Kit (750 MB)**
**Target:** Rapid deployment, testing
- Core disaster medicine
- Emergency procedures
- Water safety

**Rationale:** Sometimes you need to deploy **fast** with limited storage.

---

### Phase 4: Documentation Updates (45+ minutes)

Updated three key documents to reflect this research:

#### **02-kiwix-installation.md** - Complete rewrite
- ✅ Removed references to non-existent "Wikimed"
- ✅ Added three deployment strategies with exact URLs
- ✅ Created comparison tables
- ✅ Added "How to Find Latest ZIM Files" section
- ✅ Added medical content usage guidelines
- ✅ Legal/ethical disclaimers

**New sections:**
- Content Strategy selection guide
- Medical sources comparison table
- Download monitoring commands
- Verification procedures

#### **README.md** - Mission-focused rewrite
- ✅ Changed focus from "remote areas" to "disaster zones"
- ✅ Added medical content front and center
- ✅ Created content strategies overview
- ✅ Added real-world impact section (Haiti, Syria, etc.)
- ✅ Medical content notice and usage guidelines
- ✅ Special license for humanitarian organizations

**Key change:** Entire tone shifted from "cool tech project" to "this saves lives in emergencies."

#### **HARDWARE.md** - Added content strategy section
- ✅ New "Content Strategy First" section at top
- ✅ Updated MicroSD card recommendations:
  - 64GB for medical pack (~20€)
  - 256GB for full Wikipedia (~35€)
  - 32GB for minimal kit (~15€)
- ✅ Updated cost breakdown with SD options
- ✅ Added decision tables for SD card selection

**Cost optimization discovered:**
- Medical mission: 64GB SD = saves 15€
- Full knowledge: 256GB SD required
- Minimal deploy: 32GB SD = saves 20€

---

### Problems Encountered

#### 1. Wikimed Doesn't Exist
**Issue:** Original guide referenced `/zim/wikimed/` directory  
**Impact:** Wasted 20 minutes looking for non-existent files  
**Root cause:** Old documentation, project was discontinued/renamed  
**Solution:** Found actual medical content in `/zim/other/`  
**Lesson:** Always verify URLs directly, don't trust old guides

#### 2. Confusing File Naming Conventions
**Issue:** ZIM files use inconsistent naming  
**Examples:**
- `wikipedia_en_all_maxi_2025-08.zim` (date-based)
- `mdwiki_en_all_maxi_2025-11.zim` (date-based)
- `zimgit-post-disaster_en_2024-05.zim` (different format)

**Impact:** Hard to know which files are current  
**Solution:** 
- Browse directories directly: `curl -s https://download.kiwix.org/zim/other/`
- Look for most recent dates (YYYY-MM format)
- Use Kiwix Library search: https://library.kiwix.org/

**Lesson:** File naming isn't standardized across projects

#### 3. Finding "What MSF Actually Uses"
**Issue:** No official list of "humanitarian mission content"  
**Impact:** Had to research and infer from file descriptions  
**Solution:** 
- Searched for keywords: "disaster", "emergency", "post", "field"
- Cross-referenced with WHO/MSF documentation mentions
- Found zimgit-post-disaster specifically designed for this

**Lesson:** Medical/humanitarian content exists but isn't well-advertised

---

### Discoveries & Observations

**What I learned about Kiwix ecosystem:**
- `/zim/wikipedia/` = Wikipedia projects (full + subsets)
- `/zim/other/` = Third-party content (medical, tech, education)
- Projects come and go (Wikimed disappeared, others emerged)
- Monthly updates for active projects
- Some projects frozen (WikEM stuck at 2021)

**Content size realities:**
- "Full Wikipedia" marketing (50GB Wikimed) was **never accurate**
- Real medical pack is **~5.5 GB** (10x smaller!)
- Minimal deployment can be **<1 GB**
- Storage requirements much more flexible than thought

**ZIM file ecosystem insights:**
- Wikipedia = largest consumer (90GB+ per language)
- Medical content = surprisingly compact (hundreds of MB, not tens of GB)
- Survival guides = tiny but critical (20-100 MB)
- Specialty wikis = variable (1-10 GB)

**Best practices discovered:**
1. Always check directory listings directly
2. Sort by date to find latest versions
3. Use `curl -s URL | grep KEYWORD` for quick searches
4. Kiwix Library website is more reliable than old guides
5. Start with medical pack, add Wikipedia later if needed

---

### Time Analysis

| Task | Estimated | Actual | Notes |
|------|-----------|--------|-------|
| Find Wikimed | 5 min | 45 min | Doesn't exist! Had to search |
| Research medical content | 20 min | 30 min | Found better alternatives |
| Develop strategies | 15 min | 45 min | Created 3 complete strategies |
| Update documentation | 30 min | 45 min | Rewrote 3 major documents |
| **TOTAL** | **70 min** | **2h 45min** | Deep research worth it |

**Reflection:**
- Research phase took longer than expected but was essential
- Finding **what actually exists** vs what's documented is critical
- Creating strategies now will save time for others
- Documentation updates benefit the entire community

---

### Strategic Decisions Made

#### 1. Default to Medical Pack Strategy
**Decision:** Recommend Strategy 1 (Medical Pack) as default  
**Reasoning:**
- Humanitarian mission focus
- Compact size (5.5 GB vs 150 GB)
- Faster download (1-3 hours vs 8-24 hours)
- Focused content = easier to navigate
- Can always add full Wikipedia later

#### 2. Separate SD Card Recommendations
**Decision:** Recommend 64GB for medical, 256GB for full  
**Reasoning:**
- Saves 15€ for medical missions
- Most users won't need full Wikipedia immediately
- Easier to justify budget to organizations
- Can upgrade SD card later if needed

#### 3. Document Three Distinct Strategies
**Decision:** Don't just offer "download everything" option  
**Reasoning:**
- Different missions have different needs
- Storage/budget constraints vary
- Download time is a real factor in emergencies
- Choice empowers users to optimize for their case

---

### Statistics

**Websites browsed:** ~15 (Kiwix directories, library, docs)  
**ZIM files researched:** ~30 different medical/survival files  
**Documentation pages updated:** 3 (README, HARDWARE, Kiwix guide)  
**New content strategies created:** 3  
**Total size of recommended medical pack:** 5.5 GB (vs 50 GB imagined)  
**Cost savings discovered:** 15€ (64GB vs 256GB SD card)  
**Lines of documentation written:** ~800  
**Cups of coffee:** 2 ☕☕

---

### Content Strategy Breakdown

**Strategy 1: Emergency Medical Pack** (~5.5 GB)
```
Post-disaster protocols:    615 MB
Emergency medicine wiki:     42 MB
Medical encyclopedia:       2.1 GB
Water purification:          20 MB
Food safety:                 93 MB
Wikipedia medicine EN:      1.9 GB
Wikipedia medicine FR:      1.1 GB
────────────────────────────────
TOTAL:                      5.5 GB
```

**Strategy 2: Full Knowledge Base** (~120-150 GB)
```
Wikipedia English:          ~90 GB
Wikipedia French:           ~25 GB
Medical pack (Strategy 1):   5.5 GB
────────────────────────────────
TOTAL:                   ~120 GB
```

**Strategy 3: Minimal Emergency Kit** (~750 MB)
```
Post-disaster protocols:    615 MB
General medicine guide:      67 MB
Emergency procedures:        42 MB
Water safety:                20 MB
────────────────────────────────
TOTAL:                      744 MB
```

---

### Next Steps

**Completed today:**
- ✅ Researched actual medical content availability
- ✅ Found zimgit-post-disaster (the real humanitarian content!)
- ✅ Developed three deployment strategies
- ✅ Updated README.md with humanitarian focus
- ✅ Updated HARDWARE.md with storage strategies
- ✅ Completely rewrote 02-kiwix-installation.md

**Ready for tomorrow:**
- ⏳ **Actually download medical pack** (Strategy 1)
  - Test download from `/zim/other/` directory
  - Verify file integrity
  - Estimate real download time on my connection
- ⏳ **Install Kiwix server**
  - Follow updated guide
  - Configure systemd service
  - Test medical content serving
- ⏳ **Document performance**
  - Search speed with medical content
  - RAM usage
  - User experience

**Questions answered:**
- ✅ What medical content actually exists? → Found 7 relevant ZIM files
- ✅ How much storage needed? → 5.5 GB for medical, not 50 GB
- ✅ What do humanitarian orgs use? → zimgit-post-disaster + WikEM
- ✅ Should I download full Wikipedia? → No, medical pack first

**New questions:**
- How fast will 5.5 GB download? (estimate: 15-45 min on my connection)
- Can Kiwix search across multiple ZIM files simultaneously?
- How much RAM does medical encyclopedia need?
- What's the user experience difference between strategies?

---

### Documentation Improvements Made

**README.md:**
- Added "disaster zone" language throughout
- Created content strategies section
- Added real-world impact examples (Haiti 2010, Syria, etc.)
- Medical content notice with legal disclaimers
- Special license permission for NGOs

**HARDWARE.md:**
- New "Content Strategy First" section
- SD card recommendations by mission type
- Cost breakdown with 3 price points
- Decision tables for hardware selection

**02-kiwix-installation.md:**
- Complete rewrite of Step 3 (Download ZIM Files)
- Three strategies with exact file lists and URLs
- "How to Find Latest ZIM Files" tutorial
- Medical content sources comparison table
- Download monitoring commands
- Medical usage guidelines

**Impact:**
- Documentation now mission-focused
- Clear choice framework for users
- Accurate file locations and sizes
- Legal/ethical considerations covered

---

### Personal Notes

**Mood:** 🤔 → 😊 (Started confused, ended satisfied)

**Highlights:**
- Found the **real** medical content (zimgit-post-disaster)!
- Discovered content is way more compact than expected (5.5 GB vs 50 GB)
- Created useful framework (3 strategies) for others
- Documentation is now much more accurate and helpful

**Challenges:**
- Wikimed wild goose chase was frustrating
- ZIM file naming inconsistency confusing
- Hard to find "official" humanitarian content lists
- Balancing detail vs readability in docs

**Confidence level:**
- Before: 8/10 (knew Pi setup, uncertain about content)
- After: 9/10 (understand Kiwix ecosystem now)

**What surprised me:**
- How much smaller real medical pack is (10x less than thought)
- zimgit-post-disaster specifically designed for disasters
- Wikipedia medicine subsets are well-maintained
- Kiwix has survival content (water, food) beyond just wikis
- 64GB SD card is totally sufficient for medical missions

**Proud of:**
- Not giving up when Wikimed didn't exist
- Researching actual humanitarian use cases
- Creating clear strategy framework
- Updating documentation for community benefit
- Finding cost optimization (64GB vs 256GB)

**Lessons learned:**
1. **Verify everything** - Old docs are often wrong
2. **Browse directories directly** - Don't trust guides blindly
3. **Research end users** - What does MSF actually use?
4. **Optimize for mission** - Not everyone needs full Wikipedia
5. **Document discoveries** - Help next person avoid same confusion

**Looking forward to:**
- Testing medical pack download tomorrow
- Seeing Kiwix serve actual humanitarian content
- Measuring real-world performance
- Getting feedback from humanitarian community

---

**End of Day 2**  
**Time invested today:** 2h 45min  
**Progress:** Content strategy complete, ready for downloads  
**Status:** ✅ Research phase complete, implementation next!

**Tomorrow's goal:** Download and test medical pack (Strategy 1)  
**Estimated time:** 2-3 hours (download + configuration + testing)

**Documentation status:**
- README.md: ✅ Updated (humanitarian focus)
- HARDWARE.md: ✅ Updated (storage strategies)
- 02-kiwix-installation.md: ✅ Rewritten (accurate content)
- JOURNAL.md: ✅ This entry

---

*Journal entry completed at 21:15, December 26, 2025*
