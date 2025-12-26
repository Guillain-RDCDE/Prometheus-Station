# 📟 Step 1: Raspberry Pi Setup

**What you'll accomplish:** Transform a blank Raspberry Pi into a configured Linux server ready for Kiwix.

**Time required:** 1-2 hours (mostly waiting for downloads)  
**Difficulty:** ⭐⭐☆☆☆ Easy (even if you've never done this before)  
**Skills learned:** Linux basics, SSH, headless configuration, system administration

---

## 🎯 What Success Looks Like

By the end of this guide, you'll have:
- ✅ Raspberry Pi OS installed on your microSD card
- ✅ Ability to SSH into your Pi from your laptop (no monitor needed)
- ✅ System updated and secured
- ✅ Essential software installed
- ✅ Pi optimized for running Kiwix

**The moment of victory:** When you type `ssh prometheus@192.168.x.x` on your laptop and land in the Raspberry Pi terminal. 🎉

---

## 📋 Pre-Flight Checklist

Before we start, gather everything:

### Hardware You Need:
- [ ] **Raspberry Pi 4** (ideally 8GB RAM, but 4GB works)
- [ ] **MicroSD card** (256GB minimum, A2 class rating)
- [ ] **USB-C power supply** (official 5V 3A, or quality equivalent)
- [ ] **Your laptop/computer** (Windows, Mac, or Linux)
- [ ] **SD card reader** (built-in or USB adapter)
- [ ] **Ethernet cable** (optional, but helpful for initial setup)

### Optional (Makes Life Easier):
- [ ] **HDMI cable + monitor** (for troubleshooting if SSH fails)
- [ ] **USB keyboard** (same reason)

### Software You'll Download:
- [ ] **Raspberry Pi Imager** (official tool, free)
- [ ] **SSH client** (probably already on your computer)

### Network Requirements:
- [ ] **WiFi network name (SSID)** you'll connect the Pi to
- [ ] **WiFi password**
- [ ] **Your laptop connected to same network**

**Ready?** Let's build! 🚀

---

## 📖 The Big Picture: What We're Doing

Before jumping into commands, let's understand the process:

```
┌────────────────────────────────────────────────────────────┐
│  YOUR LAPTOP                                               │
│                                                            │
│  1. Download Raspberry Pi Imager                          │
│  2. Insert microSD card                                   │
│  3. Write operating system to card                        │
│  4. Configure WiFi + SSH settings                         │
│  5. Eject card safely                                     │
│                                                            │
└────────────────────────────────────────────────────────────┘
                          │
                          │ [Insert card into Pi]
                          ▼
┌────────────────────────────────────────────────────────────┐
│  RASPBERRY PI                                              │
│                                                            │
│  6. Pi boots from microSD card                            │
│  7. Connects to WiFi automatically                        │
│  8. SSH server starts                                     │
│                                                            │
└────────────────────────────────────────────────────────────┘
                          │
                          │ [SSH connection]
                          ▼
┌────────────────────────────────────────────────────────────┐
│  YOUR LAPTOP (again)                                       │
│                                                            │
│  9. SSH into Pi: "ssh prometheus@192.168.x.x"             │
│  10. Update system, install packages                      │
│  11. Configure settings                                   │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

**Key insight:** We're doing 90% of the work on your laptop BEFORE the Pi even boots. This is called "headless setup" and it's way easier than fiddling with monitors and keyboards.

---

## 🔧 Part 1: Preparing the MicroSD Card

### Step 1.1: Download Raspberry Pi Imager

**What is it?** Official software from Raspberry Pi Foundation that writes operating systems to SD cards.

**Why not just copy files?** Operating systems need special formatting and boot sectors. The Imager handles all the technical stuff automatically.

#### For Windows:
1. Go to: https://www.raspberrypi.com/software/
2. Click **"Download for Windows"**
3. Run the downloaded `.exe` file
4. Install like any Windows program (Next → Next → Install)

#### For macOS:
1. Same URL: https://www.raspberrypi.com/software/
2. Click **"Download for macOS"**
3. Open the `.dmg` file
4. Drag Raspberry Pi Imager to Applications
5. Launch from Applications folder

#### For Linux:
```bash
# Ubuntu/Debian
sudo apt install rpi-imager

# Fedora
sudo dnf install rpi-imager

# Arch
sudo pacman -S rpi-imager
```

**Verification:** Launch the app. You should see a simple interface with three buttons: "Choose OS", "Choose Storage", "Write".

---

### Step 1.2: Insert Your MicroSD Card

1. **Find your SD card reader**
   - Built into laptop? Usually on the side
   - USB adapter? Plug it in first

2. **Insert the microSD card**
   - Metal contacts face down (usually)
   - Should click into place

3. **Wait for your computer to recognize it**
   - Windows: Check "This PC" → Should see new drive
   - macOS: Check Finder → Should see mounted volume
   - Linux: Run `lsblk` → Should see new device (like `/dev/sdb`)

⚠️ **CRITICAL WARNING:** We're about to ERASE this card completely. Make sure:
- It's the RIGHT card (not your phone's SD card, not your camera's)
- Any important data is backed up elsewhere
- You're 100% certain before proceeding

---

### Step 1.3: Choose the Operating System

**Launch Raspberry Pi Imager** and click **"Choose OS"**

You'll see many options. Here's what to pick:

#### Recommended: Raspberry Pi OS Lite (64-bit)

**Path:** 
```
Choose OS
  → Raspberry Pi OS (other) 
    → Raspberry Pi OS Lite (64-bit)
```

**Why this one?**
- ✅ **No desktop environment** → Saves ~500MB RAM for Kiwix
- ✅ **Headless-optimized** → Designed for SSH access
- ✅ **64-bit** → Better performance on Pi 4
- ✅ **Smaller download** → ~500MB vs 1.1GB
- ✅ **Faster boot** → Less stuff to load

**"But I'm scared of command line!"**
Don't be. You'll type maybe 20 commands total. We'll explain every single one.

#### Alternative: Raspberry Pi OS with Desktop

**Path:**
```
Choose OS
  → Raspberry Pi OS (other)
    → Raspberry Pi OS (64-bit)
```

**When to choose this:**
- You want a visual desktop (like Windows/Mac)
- You plan to connect a monitor permanently
- You're very uncomfortable with command line

**Trade-offs:**
- Uses more RAM (~1.5GB vs ~500MB)
- Slower boot time
- Same functionality for Prometheus Station

**My recommendation:** Start with Lite. If you hate it, you can always re-flash with Desktop version later. It's not permanent.

---

### Step 1.4: Choose Your MicroSD Card

Click **"Choose Storage"**

You should see your microSD card listed. It might show as:
- "Generic Mass Storage" (Windows)
- "SD Card Reader" (macOS)
- "31.9 GB Device" (shows actual capacity)

**How to be SURE it's the right one:**
- Check the size (256GB should show as ~238GB actual)
- If multiple drives appear, eject others temporarily
- When in doubt, only have ONE SD card connected

Click your microSD card to select it.

---

### Step 1.5: Configure Settings (Raspberry Pi Imager v2.0+)

After choosing your OS and storage, you'll see a button **"NEXT"** at the bottom right.

**Click "NEXT"**

A popup appears asking: **"Would you like to apply OS customisation settings?"**

**Click "EDIT SETTINGS"** (or "MODIFIER LES RÉGLAGES" in French)

---

#### Now you'll see a customization window with several tabs on the left:

**📝 Configure Each Tab:**

---

#### Tab 1: "Hostname"

- ✅ Hostname: `prometheus-station`
- What it does: This is your Pi's name on the network
- Why: Easier to remember than an IP address

**Example:** Your input should look like the image - `Prometheus-Station`

---

#### Tab 2: "User"

- ✅ Username: `prometheus` (or your choice, but remember it!)
- ✅ Password: Choose something STRONG (you'll type it a lot)
  - Good: `Pr0m3th3us!Station`
  - Bad: `password123`

**Why a custom username?**
- Old default was `pi` (everyone knew this)
- Security best practice: unique username
- Makes brute-force attacks harder

---

#### Tab 3: "Wi-Fi"

- ✅ SSID: **Exactly** as your WiFi network name appears
  - Case-sensitive! "MyWiFi" ≠ "mywifi"
  - Include spaces if your network has them
- ✅ Password: Your WiFi password (also case-sensitive)
- ✅ Wireless LAN country: Select your country
  - France = FR
  - USA = US
  - Critical for legal radio frequencies

**Why this matters:** The Pi will connect to WiFi on first boot, automatically.

---

#### Tab 4: "Localisation"

- ✅ Time zone: Your timezone (e.g., `Europe/Paris`)
- ✅ Keyboard layout: Your keyboard type (e.g., `fr` or `us`)

**Why:** Makes dates/logs readable, typing behaves correctly

---

#### Tab 5: "Remote access"

**This is CRITICAL for headless setup!**

- ✅ Enable SSH: **CHECK THIS BOX**
- Choose: **"Use password authentication"**

**What it does:** Allows you to control the Pi remotely from your laptop

**Without this:** You'd need to connect a monitor and keyboard every time

---

#### Tab 6: "Raspberry Pi Connect" (optional)

- Leave unchecked for now (we're using Tailscale instead)

---

### After Configuring All Tabs:

1. **Click "SAVE"** (bottom right)
2. You're back to the main screen
3. **Click "YES"** when asked "Would you like to apply OS customisation settings?"
4. **Confirm the warning:** "All existing data will be erased"
5. **Click "YES"** to start writing

---

### Step 1.6: Write the OS to SD Card

Now that all settings are configured:

1. **Review the summary:**
   - OS: Raspberry Pi OS Lite (64-bit) ✅
   - Storage: Your 256GB microSD ✅
   - Customisation applied ✅

2. **Click "YES"** to proceed with writing

3. **Final confirmation:**
   - "All existing data on [your SD card] will be erased"
   - Click "YES" (you backed up anything important, right?)

4. **Wait for the magic:**
   
   **Progress stages:**
   ```
   Downloading Raspberry Pi OS... [0-30%]
   ├─ ~500MB download
   ├─ Speed depends on your internet
   └─ Coffee break time ☕
   
   Writing to SD card... [30-70%]
   ├─ Actual OS installation
   ├─ Takes 5-10 minutes
   └─ Don't eject the card!
   
   Verifying... [70-100%]
   ├─ Checks everything wrote correctly
   ├─ Takes 2-5 minutes
   └─ This is important, don't skip!
   ```

5. **Success message appears:**
   ```
   Write Successful
   You can now remove the SD card
   ```

6. **Eject the SD card safely:**
   - Windows: Right-click → "Eject"
   - macOS: Drag to trash (becomes eject icon)
   - Linux: `sudo umount /dev/sdX` (replace X with your device)

**If the write fails:**
- Check SD card isn't write-protected (tiny switch on adapter)
- Try a different SD card reader
- Re-download the OS (might be corrupted)
- Check if SD card is fake (common with cheap ones)

---

## 🚀 Part 2: First Boot

### Step 2.1: Insert Card and Power On

1. **Remove the microSD card** from your computer
2. **Find the card slot** on Raspberry Pi (underside, spring-loaded)
3. **Insert card** (metal contacts facing the board)
   - Push until it clicks
   - Should be flush with the board
4. **Connect power cable** (USB-C)
5. **Power on** (no power button, just plug it in)

**What happens next:**
```
[0-10 seconds]
- Green LED starts blinking (reading SD card)
- Pi is booting up

[10-30 seconds]
- OS loading
- WiFi connecting
- Services starting

[30-60 seconds]
- System ready
- SSH server active
- Green LED blinks occasionally (normal activity)
```

**How do you know it's ready?**
- Green LED stops rapid blinking
- Settles into occasional flashes
- Wait 60 seconds total to be safe

**If red LED turns on but green LED does nothing:**
- Bad SD card write → Re-flash
- Incompatible SD card → Try different brand
- Power supply insufficient → Use official 3A supply

---

### Step 2.2: Find Your Pi's IP Address

Your Pi is now on your network, but where? You need its IP address to SSH in.

#### Method 1: Check Your Router (Easiest)

1. **Open your router's admin page:**
   - Common addresses: `192.168.1.1` or `192.168.0.1`
   - Or check sticker on router
   
2. **Login:**
   - Default credentials often on router
   - Or you set them up before

3. **Find "Connected Devices" or "DHCP Clients"**

4. **Look for:**
   - Hostname: `prometheus-station`
   - Or manufacturer: "Raspberry Pi Foundation"
   - Note the IP address (like `192.168.1.42`)

#### Method 2: Ping by Hostname (macOS/Linux)

```bash
ping prometheus-station.local

# Expected output:
# PING prometheus-station.local (192.168.1.42): 56 data bytes
# 64 bytes from 192.168.1.42: icmp_seq=0 ttl=64 time=2.4 ms
```

The IP address is right there! (`192.168.1.42` in this example)

**On Windows:**
```cmd
ping prometheus-station.local
```

If it works, you'll see the IP.

#### Method 3: Network Scanner App

**For Android:** Download "Fing" from Play Store
**For iOS:** Download "Fing" from App Store
**For Desktop:** Download "Angry IP Scanner"

1. Open the app
2. Scan your network
3. Look for "Raspberry Pi" or "prometheus-station"
4. Note the IP address

#### Method 4: Connect Monitor (Last Resort)

1. Connect HDMI cable to Pi and monitor
2. Connect USB keyboard
3. Pi will show login screen
4. Type command: `hostname -I`
5. It will print the IP address
6. Write it down

**For the rest of this guide, I'll use `192.168.1.42` as an example. Replace it with YOUR actual IP.**

---

### Step 2.3: SSH Into Your Raspberry Pi

**This is the moment.** You're about to control your Pi remotely for the first time.

#### On Windows (PowerShell or Command Prompt):

1. **Open PowerShell:**
   - Press `Win + X`
   - Select "Windows PowerShell" or "Terminal"

2. **Type this command:**
   ```powershell
   ssh prometheus@192.168.1.42
   ```
   (Replace `192.168.1.42` with YOUR Pi's IP address)

3. **First-time connection warning:**
   ```
   The authenticity of host '192.168.1.42' can't be established.
   ECDSA key fingerprint is SHA256:xxxxxxxxxxxxx
   Are you sure you want to continue connecting (yes/no)?
   ```
   
   - Type: `yes` and press Enter
   - This is normal and only happens once
   - It's SSH's way of saying "I've never met this device before"

4. **Enter password:**
   - Type the password you set in Raspberry Pi Imager
   - **You won't see characters as you type** (security feature)
   - Just type it and press Enter

5. **Success looks like:**
   ```
   Linux prometheus-station 6.1.0-rpi7-rpi-v8 #1 SMP PREEMPT Debian 1:6.1.63-1+rpt1 (2023-11-24) aarch64
   
   prometheus@prometheus-station:~ $
   ```

**You're in!** 🎉

#### On macOS/Linux (Terminal):

1. **Open Terminal:**
   - macOS: `Cmd + Space` → type "Terminal"
   - Linux: `Ctrl + Alt + T`

2. **Same SSH command:**
   ```bash
   ssh prometheus@192.168.1.42
   ```

3. **Same first-time warning:**
   - Type `yes`
   - Enter password
   - You're connected!

---

### 🧠 What Just Happened? (SSH Explained)

```
Your Laptop                           Raspberry Pi
    │                                      │
    │  "Hey, I want to control you"       │
    ├─────────────────────────────────────>│
    │                                      │
    │  "Prove you're the owner"           │
    │<─────────────────────────────────────┤
    │                                      │
    │  [Sends password]                    │
    ├─────────────────────────────────────>│
    │                                      │
    │  "OK, you're in. Here's a shell"    │
    │<─────────────────────────────────────┤
    │                                      │
    │  [You type commands]                 │
    ├─────────────────────────────────────>│
    │                                      │
    │  [Pi executes and sends results]    │
    │<─────────────────────────────────────┤
```

Everything you type now runs ON THE RASPBERRY PI, not your laptop.

**Mind-blowing realization:** You could be in a coffee shop in Paris, SSHing into a Pi in Tokyo, and it would work exactly the same way. That's the power of SSH.

---

## 🔄 Part 3: System Configuration

Now that you're logged in, let's configure the Pi properly.

### Step 3.1: Update the System

**Why?** Your OS image was created weeks/months ago. Security patches and bug fixes have been released since then.

```bash
sudo apt update && sudo apt upgrade -y
```

**Let's decode this command:**
- `sudo` = "Run as administrator" (super user do)
- `apt` = Package manager (like App Store for Linux)
- `update` = Refresh the list of available packages
- `upgrade -y` = Install all updates (-y means "yes to all prompts")
- `&&` = "Run second command only if first succeeds"

**What you'll see:**
```
Hit:1 http://deb.debian.org/debian bookworm InRelease
Get:2 http://deb.debian.org/debian-security bookworm-security InRelease [48.0 kB]
...
Reading package lists... Done
Building dependency tree... Done
...
47 upgraded, 0 newly installed, 0 to remove and 0 not upgraded.
Need to get 68.2 MB of archives.
After this operation, 124 kB of additional disk space will be used.
```

**How long?** 5-15 minutes depending on internet speed and number of updates.

**Coffee break time ☕**

**When it finishes:**
```
prometheus@prometheus-station:~ $
```
You're back at the prompt, ready for the next command.

---

### Step 3.2: Configure Raspberry Pi Settings

```bash
sudo raspi-config
```

**What is this?** A text-based menu for configuring Pi-specific settings.

**You'll see a blue screen with options:**

```
┌─────────────┤ Raspberry Pi Software Configuration Tool ├──────────────┐
│                                                                        │
│    1 System Options       Configure system settings                   │
│    2 Display Options      Configure display settings                  │
│    3 Interface Options    Configure connections to peripherals        │
│    4 Performance Options  Configure performance settings              │
│    5 Localisation Options Configure language and regional settings    │
│    6 Advanced Options     Configure advanced settings                 │
│    8 Update               Update this tool to the latest version      │
│    9 About raspi-config   Information about this configuration tool   │
│                                                                        │
│                  <Select>                  <Finish>                    │
└────────────────────────────────────────────────────────────────────────┘
```

**Navigation:**
- Use **arrow keys** to move up/down
- Press **Enter** to select
- Press **Tab** to move between buttons (<Select> / <Finish>)
- Press **Esc** twice to exit

---

#### Setting 1: Expand Filesystem

**Path:** `6 Advanced Options` → `A1 Expand Filesystem`

**What it does:** Makes the entire SD card available (by default, only 2GB is used)

**Why:** We need all 256GB for Wikipedia files

**Action:**
1. Select `6 Advanced Options`
2. Select `A1 Expand Filesystem`
3. Press Enter on "OK"
4. You're back at main menu

---

#### Setting 2: Set Memory Split (Headless Optimization)

**Path:** `4 Performance Options` → `P2 GPU Memory`

**What it does:** Allocates RAM between CPU and GPU

**Why:** We're headless (no monitor), so GPU doesn't need much RAM

**Action:**
1. Select `4 Performance Options`
2. Select `P2 GPU Memory`
3. Enter: `16` (minimum for GPU)
4. Press Enter
5. Back to main menu

**What this gives you:** 16MB saved for CPU/Kiwix = faster searches

---

#### Setting 3: Enable SSH (Verify)

**Path:** `3 Interface Options` → `I2 SSH`

**What it does:** Ensures SSH is enabled (should already be from Imager settings)

**Why:** Double-check it's on

**Action:**
1. Select `3 Interface Options`
2. Select `I2 SSH`
3. Should say "SSH server is enabled"
4. If not, select "Yes" to enable
5. Back to main menu

---

#### Setting 4: Configure Hostname (Optional)

**Path:** `1 System Options` → `S4 Hostname`

**What it does:** Change the network name

**Why:** If you didn't set it in Imager, or want to change it

**Action:**
1. Select `1 System Options`
2. Select `S4 Hostname`
3. Enter: `prometheus-station`
4. Press Enter

---

#### Finish and Reboot

1. Press **Tab** until `<Finish>` is highlighted
2. Press **Enter**
3. It will ask: "Would you like to reboot now?"
4. Select **Yes**

**Your SSH session will disconnect.** This is normal.

**Wait 30 seconds**, then reconnect:
```bash
ssh prometheus@192.168.1.42
```

(Use the same IP as before)

---

### Step 3.3: Install Essential Packages

Now we'll install tools that Prometheus Station needs.

```bash
sudo apt install -y git curl wget vim htop ufw
```

**What each package does:**

| Package | Purpose | Why We Need It |
|---------|---------|----------------|
| `git` | Version control system | Download code from GitHub |
| `curl` | Download files from URLs | Scripting, API calls |
| `wget` | Alternative file downloader | Backup for curl |
| `vim` | Text editor | Edit config files (alternative to nano) |
| `htop` | Process monitor | See what's using CPU/RAM |
| `ufw` | Firewall | Security (block unwanted connections) |

**Installation takes:** ~2 minutes

---

### Step 3.3b: Install Tailscale (HIGHLY RECOMMENDED) 🌟

**What is Tailscale?** A VPN that lets you access your Pi from ANYWHERE in the world, securely.

#### 🧠 Why This Changes Everything

**Without Tailscale:**
- You can SSH into Pi only when on same WiFi network
- If you're at a coffee shop, you can't access your Pi at home
- Port forwarding is complicated and insecure
- Dynamic IP addresses are a nightmare

**With Tailscale:**
- Access Pi from anywhere: home, work, coffee shop, another country
- No port forwarding needed (works through firewalls)
- Encrypted connection (VPN-grade security)
- Works even if your home IP changes
- Free for personal use (up to 100 devices)

**Real-world scenario:**
```
You're in a café in Paris.
Your Pi is at home in Lyon.
Type: ssh prometheus@100.x.x.x (Tailscale IP)
→ You're connected instantly. Securely. Magically.
```

**Think of it as:** Your Pi gets a permanent phone number that works globally.

---

#### Installation Steps

**1. Install Tailscale:**

```bash
curl -fsSL https://tailscale.com/install.sh | sh
```

**What this does:**
- Downloads official Tailscale installer
- Installs Tailscale daemon (background service)
- Configures system integration

**Takes:** ~30 seconds

---

**2. Start Tailscale and Authenticate:**

```bash
sudo tailscale up
```

**You'll see:**
```
To authenticate, visit:

  https://login.tailscale.com/a/xxxxxxxxxxxx

```

**What to do:**
1. **Copy that URL** (the one starting with https://login.tailscale.com/)
2. **Open it in your web browser** (on your laptop, not the Pi)
3. **Sign in with:**
   - Google account (easiest)
   - GitHub account
   - Microsoft account
   - Or create Tailscale account

4. **Authorize the device:**
   - You'll see "prometheus-station wants to join your network"
   - Click "Connect"

5. **Back in your SSH session**, you'll see:
   ```
   Success.
   ```

**Congratulations!** Your Pi is now on your Tailscale network. 🎉

---

**3. Find Your Tailscale IP:**

```bash
tailscale ip -4
```

**Example output:**
```
100.84.123.45
```

**Write this down!** This is your Pi's permanent address.

---

**4. Test It:**

From your laptop (open a NEW terminal, don't disconnect your current SSH):

```bash
ping 100.84.123.45
```

(Use YOUR Tailscale IP, not this example)

**Expected:**
```
PING 100.84.123.45: 56 data bytes
64 bytes from 100.84.123.45: icmp_seq=0 ttl=64 time=12.4 ms
```

**It works!** Even though you're on the same network now, this will work from ANYWHERE.

---

**5. SSH via Tailscale:**

Try connecting through Tailscale:

```bash
ssh prometheus@100.84.123.45
```

**If it works:** You can now access your Pi from anywhere! 🌍

---

#### 🔒 Tailscale Security Configuration

**Optional but Recommended: Disable Key Expiry**

By default, Tailscale keys expire after 180 days (you'd need to re-authenticate).

**To disable expiry:**
1. Go to: https://login.tailscale.com/admin/machines
2. Find "prometheus-station"
3. Click the "..." menu
4. Select "Disable key expiry"
5. Confirm

**Now your Pi stays connected forever.** No re-authentication needed.

---

**Optional: Set a Friendly Hostname**

In the Tailscale admin panel:
1. Click on "prometheus-station"
2. Under "Machine name" → Edit
3. Set to: `prometheus` (short and easy)
4. Save

**Now you can SSH with:**
```bash
ssh prometheus@prometheus
```

**Even cleaner!** (Tailscale handles the .ts.net domain automatically)

---

#### 🎯 How to Use Tailscale Going Forward

**From now on, you have TWO ways to access your Pi:**

**Method 1: Local Network (when at home)**
```bash
ssh prometheus@192.168.1.42
# Fast, direct connection
```

**Method 2: Tailscale (from anywhere)**
```bash
ssh prometheus@100.84.123.45
# or
ssh prometheus@prometheus.ts.net
# Works globally, encrypted
```

**Best practice:** Use Tailscale for EVERYTHING. It works locally AND remotely.

---

#### 💡 Tailscale Bonus Features

**1. MagicDNS (automatic)**
- Your Pi is accessible at: `prometheus-station.your-tailnet-name.ts.net`
- No need to remember IPs

**2. File sharing:**
```bash
# On Pi, share a file
tailscale file cp /path/to/file.txt YOUR_LAPTOP_NAME:

# On laptop, receive it
tailscale file get
```

**3. Exit node (advanced):**
- Route ALL your laptop's internet through your Pi
- Useful for accessing home network resources remotely

---

#### 🆘 Tailscale Troubleshooting

**Problem: "curl: command not found"**
```bash
# Install curl first
sudo apt install curl
# Then retry Tailscale install
```

**Problem: "tailscale up" hangs**
- Press Ctrl+C
- Check internet: `ping 8.8.8.8`
- Retry: `sudo tailscale up`

**Problem: Can't access auth URL**
- URL is ONLY for your laptop's browser, not the Pi
- Copy-paste the ENTIRE URL (including the long code)

**Problem: Tailscale IP doesn't ping**
- Check Tailscale status: `tailscale status`
- Restart Tailscale: `sudo systemctl restart tailscaled`
- Check firewall allows Tailscale: `sudo ufw allow in on tailscale0`

---

#### ⚠️ Important Firewall Update (If Using Tailscale)

If you installed Tailscale, allow it through the firewall:

```bash
# Allow all traffic on Tailscale interface
sudo ufw allow in on tailscale0
```

**Why:** Tailscale creates its own network interface. UFW needs to know it's safe.

---

#### 📊 Check Tailscale Status Anytime

```bash
# See connected devices
tailscale status

# See your IPs
tailscale ip -4

# Test connection to another device
tailscale ping OTHER_DEVICE_NAME
```

---

#### 🎓 What You Just Learned

By installing Tailscale, you've:
- ✅ Created a global VPN for your Pi
- ✅ Eliminated the need for port forwarding
- ✅ Made your Pi accessible from anywhere
- ✅ Added military-grade encryption to all connections
- ✅ Future-proofed your deployment (works even if you move)

**This is POWERFUL.** You can now manage Prometheus Station from literally anywhere on Earth with internet. 🌍

---

**Skip Tailscale?** You can, but you'll regret it when you want to check on your Pi remotely and can't. **Just install it now.** Takes 2 minutes, saves hours of frustration later.

---

### Step 3.4: Configure Firewall (Security)

**Why a firewall?** Your Pi is on your network. A firewall blocks unwanted connections.

#### Enable UFW and Set Rules

```bash
# Allow SSH (port 22) - CRITICAL, or you'll lock yourself out!
sudo ufw allow 22/tcp

# Allow Kiwix web server (port 80)
sudo ufw allow 80/tcp

# Enable firewall
sudo ufw enable
```

**You'll see:**
```
Command may disrupt existing ssh connections. Proceed with operation (y|n)?
```

Type `y` and press Enter.

**Why port 22 FIRST?** If you enable UFW without allowing SSH, your connection drops and you can't get back in. Always allow SSH before enabling.

**Check firewall status:**
```bash
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

✅ Perfect! Firewall is protecting you while allowing necessary services.

---

### Step 3.5: Optimize System Performance

#### Disable Swap (Optional but Recommended)

**What is swap?** When RAM fills up, the system uses SD card as "fake RAM" (swap space).

**Problem:** SD cards are SLOW and wear out from constant writing.

**Solution:** Disable swap (we have 8GB RAM, plenty for our needs).

```bash
# Turn off swap
sudo dphys-swapfile swapoff

# Disable swap service
sudo systemctl disable dphys-swapfile

# Check it's off
free -h
```

**Expected output:**
```
               total        used        free      shared  buff/cache   available
Mem:           7.8Gi       124Mi       7.5Gi       8.0Mi       213Mi       7.6Gi
Swap:             0B          0B          0B
```

See that `Swap: 0B`? Perfect. ✅

**If you have 4GB RAM:** Consider keeping swap enabled (comment out the commands above).

---

#### Disable Unnecessary Services

**What are services?** Background programs that start automatically.

**Problem:** Some are useless for a headless server and waste resources.

```bash
# Bluetooth (we're not using it)
sudo systemctl disable bluetooth.service

# Bluetooth modem (related to above)
sudo systemctl disable hciuart.service

# Audio (no speakers on a headless server)
sudo systemctl disable alsa-state.service

# Verify they're disabled
sudo systemctl status bluetooth.service
```

**Expected:** `Loaded: loaded (/lib/systemd/system/bluetooth.service; disabled;`

**RAM saved:** ~50-100MB  
**Boot time saved:** ~2-3 seconds

---

### Step 3.6: Create a System Monitoring Script

This is a handy script to check system health at any time.

```bash
# Create the script
nano ~/system_status.sh
```

**Nano editor opens.** Paste this script:

```bash
#!/bin/bash
# Prometheus Station System Status

echo "======================================"
echo " PROMETHEUS STATION - System Status"
echo "======================================"
echo ""

# System uptime
echo "Uptime:"
uptime
echo ""

# Temperature
echo "CPU Temperature:"
vcgencmd measure_temp
echo ""

# Memory usage
echo "Memory Usage:"
free -h
echo ""

# Disk usage
echo "Disk Usage:"
df -h / | grep -v Filesystem
echo ""

# Network interfaces
echo "Network Interfaces:"
ip -brief addr
echo ""

# Active connections
echo "Active SSH Connections:"
who
echo ""

echo "======================================"
```

**Save the file:**
1. Press `Ctrl + X`
2. Press `Y` (yes, save)
3. Press `Enter` (confirm filename)

**Make it executable:**
```bash
chmod +x ~/system_status.sh
```

**Test it:**
```bash
~/system_status.sh
```

**You'll see:**
```
======================================
 PROMETHEUS STATION - System Status
======================================

Uptime:
 08:23:14 up 15 min,  1 user,  load average: 0.08, 0.12, 0.09

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
eth0             DOWN           
wlan0            UP             192.168.1.42/24 

Active SSH Connections:
prometheus pts/0        2025-12-26 08:08 (192.168.1.100)

======================================
```

**Bookmark this!** You'll use it constantly to check on your Pi.

---

## ✅ Verification Checklist

Before moving to Step 2 (Kiwix), verify everything works:

### System Access:
- [ ] Can SSH into Pi from laptop: `ssh prometheus@192.168.1.42`
- [ ] (If installed) Can SSH via Tailscale: `ssh prometheus@100.x.x.x`
- [ ] Filesystem expanded (df -h shows full SD card capacity)
- [ ] System updated (`sudo apt update` shows no pending updates)

### Configuration:
- [ ] Hostname set correctly (`hostname` returns `prometheus-station`)
- [ ] GPU memory set to 16MB (`vcgencmd get_mem gpu` returns `gpu=16M`)
- [ ] SSH enabled (`sudo systemctl status ssh` shows "active (running)")
- [ ] (If installed) Tailscale running (`tailscale status` shows connected devices)

### Security:
- [ ] Firewall active (`sudo ufw status` shows "Status: active")
- [ ] SSH port allowed (port 22 in firewall rules)
- [ ] Kiwix port allowed (port 80 in firewall rules)
- [ ] (If installed) Tailscale allowed (`tailscale0` interface in ufw rules)

### Performance:
- [ ] Swap disabled (`free -h` shows Swap: 0B)
- [ ] Bluetooth disabled (`systemctl status bluetooth` shows "disabled")
- [ ] System monitoring script works (`~/system_status.sh` runs without errors)

### System Health:
- [ ] Temperature under 60°C (`vcgencmd measure_temp`)
- [ ] Free RAM > 6GB (`free -h`)
- [ ] CPU load average < 1.0 (`uptime`)

**All checkboxes ticked?** 🎉 **You're ready for Step 2!**

---

## 🆘 Troubleshooting

### Problem: Can't SSH into Pi

**Symptom:** `ssh: connect to host 192.168.1.42 port 22: Connection refused`

**Possible causes:**
1. **Wrong IP address**
   - Solution: Re-scan network, find correct IP
   
2. **Pi didn't connect to WiFi**
   - Solution: Connect monitor, check `ifconfig`
   - Verify WiFi SSID/password in imager were correct
   
3. **SSH not enabled**
   - Solution: Re-flash SD card, ensure SSH enabled in imager settings
   
4. **Firewall blocking (on your laptop)**
   - Windows: Check Windows Defender Firewall
   - macOS: Check System Preferences → Security
   
5. **Pi not booted yet**
   - Solution: Wait 2 full minutes after power-on

---

### Problem: SSH Connection Drops Immediately

**Symptom:** Connects, then disconnects within seconds

**Possible causes:**
1. **Power supply insufficient**
   - Solution: Use official 3A power supply
   - Check for "low voltage" icon on Pi (lightning bolt)
   
2. **SD card corruption**
   - Solution: Re-flash SD card, use quality A2 card
   
3. **Overheating**
   - Solution: Add heatsinks, improve ventilation
   - Check temp: `vcgencmd measure_temp` (should be <80°C)

---

### Problem: `sudo apt update` Fails

**Symptom:** `Failed to fetch... Could not resolve 'deb.debian.org'`

**Cause:** No internet connection

**Solutions:**
1. **Check WiFi connection:**
   ```bash
   iwconfig
   # Should show wlan0 connected
   ```

2. **Verify DNS working:**
   ```bash
   ping 8.8.8.8
   # Should get responses
   ```

3. **Reconnect WiFi:**
   ```bash
   sudo raspi-config
   # Navigate to: System Options → Wireless LAN
   # Re-enter SSID and password
   ```

---

### Problem: Filesystem Not Expanded

**Symptom:** `df -h` shows only 2GB available

**Solution:**
```bash
# Expand manually
sudo raspi-config
# Navigate to: Advanced Options → Expand Filesystem
# Reboot
sudo reboot
```

---

### Problem: Temperature Too High

**Symptom:** `vcgencmd measure_temp` shows >70°C

**Immediate action:**
```bash
# Check what's using CPU
htop
# Press F10 to quit
```

**Long-term solutions:**
- Add heatsink to CPU
- Add fan (if you have POE HAT)
- Improve airflow around Pi
- Don't run in enclosed space

**Critical:** If temp hits 80°C+, Pi will throttle (slow down). At 85°C, it will shut down to protect itself.

---

### Problem: Can't Remember Password

**Symptom:** SSH asks for password, but you forgot what you set

**Solution (requires monitor + keyboard):**
1. Connect monitor and keyboard to Pi
2. At login: username = `prometheus`, try common passwords
3. If locked out completely:
   - Re-flash SD card
   - Set new password in Imager
   - Start over (sorry, no password recovery on Linux)

**Prevention:** Write down your password somewhere safe!

---

## 🎓 What You've Learned

Congratulations! You've just:

✅ **Installed an operating system** from scratch  
✅ **Configured headless access** (no monitor needed)  
✅ **Secured a Linux system** (firewall, SSH hardening)  
✅ **Optimized performance** (disabled swap, unnecessary services)  
✅ **Learned basic Linux commands** (sudo, apt, systemctl)  
✅ **Troubleshot network issues** (finding IP, SSH debugging)  

**These skills transfer to:**
- Any Raspberry Pi project
- Linux server administration
- IoT device management
- Cloud computing (same principles)

**You're now a sysadmin.** 🎉 (Well, baby sysadmin. But still!)

---

## 📚 Useful Commands Reference

Keep these handy:

```bash
# System information
uname -a                    # Kernel version
cat /etc/os-release         # OS version
vcgencmd measure_temp       # CPU temperature
free -h                     # RAM usage
df -h                       # Disk usage

# Network
ip addr                     # Show IP addresses
ping google.com             # Test internet
iwconfig                    # WiFi status

# Tailscale (if installed)
tailscale status            # See all connected devices
tailscale ip -4             # Show your Tailscale IP
tailscale ping DEVICE       # Test connection to another device
sudo tailscale up           # Connect to Tailscale network
sudo tailscale down         # Disconnect from Tailscale

# Process management
htop                        # Visual process monitor
ps aux                      # List all processes
kill <PID>                  # Kill a process

# Services
sudo systemctl status <name>   # Check service status
sudo systemctl start <name>    # Start service
sudo systemctl stop <name>     # Stop service
sudo systemctl restart <name>  # Restart service
sudo systemctl enable <name>   # Auto-start on boot
sudo systemctl disable <name>  # Disable auto-start

# File operations
ls -la                      # List files (detailed)
cd /path/to/directory       # Change directory
nano filename               # Edit file
cat filename                # Display file contents
chmod +x filename           # Make file executable

# System maintenance
sudo apt update             # Update package list
sudo apt upgrade            # Upgrade packages
sudo apt clean              # Clean package cache
sudo reboot                 # Reboot system
sudo shutdown -h now        # Shutdown immediately
```

**Pro tip:** Bookmark this section. You'll reference it constantly.

---

## 🚀 Next Steps

**Your Raspberry Pi is now ready for Kiwix!**

Head to: **[Step 2: Kiwix Installation](02-kiwix-installation.md)**

In Step 2, you'll:
- Install Kiwix server software
- Download Wikipedia ZIM files (~171GB)
- Configure Kiwix as a systemd service
- Access Wikipedia through your browser

**Estimated time:** 3-4 hours (mostly downloading)

See you there! 🔥

---

**Last updated:** December 2025  
**Tested on:** Raspberry Pi 4 (8GB), Raspberry Pi OS Lite (64-bit)  
**Written by:** Guillain d'Erceville

*Questions? Open an issue on GitHub!*
