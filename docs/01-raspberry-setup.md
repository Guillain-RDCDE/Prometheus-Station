# Step 1: Raspberry Pi setup

**What you'll accomplish:** Transform a blank Raspberry Pi into a configured Linux server ready for Kiwix.

**Time required:** 1h 45min (tested actual time - first build with learning)  
**Difficulty:** ⭐⭐☆☆☆ Easy (headless setup works perfectly)  
**Skills learned:** Linux basics, SSH keys, headless configuration, system optimization

**💡 Real experience:** Everything worked on first try. Headless setup is amazing - never needed monitor or keyboard!

---

## 🎯 What success looks like

By the end of this guide, you'll have:
- ✅ Raspberry Pi OS installed on your microSD card
- ✅ Ability to SSH into your Pi from your laptop (no monitor needed)
- ✅ System updated and secured
- ✅ Essential software installed
- ✅ Pi optimized for running Kiwix

**The moment of victory:** When you type `ssh prometheus` on your laptop and connect instantly with no password. 🎉

---

## 📋 Pre-flight checklist

Before we start, gather everything:

### Hardware you need
- [ ] **Raspberry Pi 4** (ideally 8GB RAM, but 4GB works)

### 💾 Choose your storage (based on mission):

**Option 1: Medical Mission Pack** (~64GB needed)
- **SD Card:** 64GB A2 class (~20€)
- **Content:** 5.5GB humanitarian medical pack
- **Best for:** Field missions, disaster response
- **Why:** Cost-effective, faster downloads

**Option 2: Full Knowledge Base** (~256GB needed)
- **SD Card:** 256GB A2 class (~35€)
- **Content:** Complete Wikipedia EN + FR (120GB+)
- **Best for:** Permanent installations, educational centers

**Option 3: Minimal Test** (~32GB needed)
- **SD Card:** 32GB A2 class (~15€)
- **Content:** 750MB emergency protocols only
- **Best for:** Prototyping, quick deployment testing

⚠️ **CRITICAL:** Must be **A2 class** rating! A1 or lower = painfully slow searches.

💡 **Tip:** Start with 64GB. You can always upgrade SD card later if needed.

### Other hardware
- [ ] **USB-C power supply** (official 5V 3A, or quality equivalent - **don't cheap out!**)
- [ ] **Your laptop/computer** (Windows, Mac, or Linux)
- [ ] **SD card reader** (built-in or USB adapter)
- [ ] **Ethernet cable** (optional, but helpful for initial setup)

### Optional (makes life easier):
- [ ] **HDMI cable + monitor** (for troubleshooting if SSH fails)
- [ ] **USB keyboard** (same reason)

### Software you'll download
- [ ] **Raspberry Pi Imager** (official tool, free)
- [ ] **SSH client** (probably already on your computer)

### Network requirements
- [ ] **WiFi network name (SSID)** you'll connect the Pi to - **case sensitive!**
- [ ] **WiFi password**
- [ ] **Your laptop connected to same network**

**Ready?** Let's build! 🚀

---

## 📖 The big picture: what we're doing

Before jumping into commands, let's understand the process:

```
┌──────────────────────────────────────────────────────────┐
│  YOUR LAPTOP                                             │
│                                                          │
│  1. Download Raspberry Pi Imager                        │
│  2. Insert microSD card                                 │
│  3. Write operating system to card                      │
│  4. Configure WiFi + SSH settings                       │
│  5. Eject card safely                                   │
│                                                          │
└──────────────────────────────────────────────────────────┘
                          │
                          │ [Insert card into Pi]
                          ▼
┌──────────────────────────────────────────────────────────┐
│  RASPBERRY PI                                            │
│                                                          │
│  6. Pi boots from microSD card                          │
│  7. Connects to WiFi automatically                      │
│  8. SSH server starts                                   │
│                                                          │
└──────────────────────────────────────────────────────────┘
                          │
                          │ [SSH connection]
                          ▼
┌──────────────────────────────────────────────────────────┐
│  YOUR LAPTOP (again)                                     │
│                                                          │
│  9. SSH into Pi: "ssh prometheus@192.168.x.x"           │
│  10. Update system, install packages                    │
│  11. Configure settings                                 │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

**Key insight:** We're doing 90% of the work on your laptop BEFORE the Pi even boots. This is called "headless setup" and it's way easier than fiddling with monitors and keyboards.

---

## ðŸ”§ Part 1: Preparing the MicroSD Card

### Step 1.1: Download Raspberry Pi Imager

**What is it?** Official software from Raspberry Pi Foundation that writes operating systems to SD cards.

**Why not just copy files?** Operating systems need special formatting and boot sectors. The Imager handles all the technical stuff automatically.

#### For Windows
1. Go to: https://www.raspberrypi.com/software/
2. Click **"Download for Windows"**
3. Run the downloaded `.exe` file
4. Install like any Windows program (Next â†’ Next â†’ Install)

#### For macOS
1. Same URL: https://www.raspberrypi.com/software/
2. Click **"Download for macOS"**
3. Open the `.dmg` file
4. Drag Raspberry Pi Imager to Applications
5. Launch from Applications folder

#### For Linux
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

### Step 1.2: Insert your microSD card

1. **Find your SD card reader**
   - Built into laptop? Usually on the side
   - USB adapter? Plug it in first

2. **Insert the microSD card**
   - Metal contacts face down (usually)
   - Should click into place

3. **Wait for your computer to recognize it**
   - Windows: Check "This PC" â†’ Should see new drive
   - macOS: Check Finder â†’ Should see mounted volume
   - Linux: Run `lsblk` â†’ Should see new device (like `/dev/sdb`)

âš ï¸ **CRITICAL WARNING:** We're about to ERASE this card completely. Make sure:
- It's the RIGHT card (not your phone's SD card, not your camera's)
- Any important data is backed up elsewhere
- You're 100% certain before proceeding

---

### Step 1.3: Choose the operating system

**Launch Raspberry Pi Imager** and click **"Choose OS"**

You'll see many options. Here's what to pick:

#### Recommended: Raspberry Pi OS Lite (64-bit)

**Path:** 
```
Choose OS
  â†’ Raspberry Pi OS (other) 
    â†’ Raspberry Pi OS Lite (64-bit)
```

**Why this one?**
- âœ… **No desktop environment** â†’ Saves ~500MB RAM for Kiwix
- âœ… **Headless-optimized** â†’ Designed for SSH access
- âœ… **64-bit** â†’ Better performance on Pi 4
- âœ… **Smaller download** â†’ ~500MB vs 1.1GB
- âœ… **Faster boot** â†’ Less stuff to load

**"But I'm scared of command line!"**
Don't be. You'll type maybe 20 commands total. We'll explain every single one.

#### Alternative: Raspberry Pi OS with desktop

**Path:**
```
Choose OS
  â†’ Raspberry Pi OS (other)
    â†’ Raspberry Pi OS (64-bit)
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

### Step 1.4: Choose your microSD card

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

### Step 1.5: Configure settings (Raspberry Pi Imager v2.0+)

After choosing your OS and storage, you'll see a button **"NEXT"** at the bottom right.

**Click "NEXT"**

A popup appears asking: **"Would you like to apply OS customisation settings?"**

**Click "EDIT SETTINGS"** (or "MODIFIER LES RÃ‰GLAGES" in French)

---

#### Now you'll see a customization window with several tabs on the left:

**ðŸ“ Configure Each Tab:**

---

#### Tab 1: "Hostname"

- âœ… Hostname: `prometheus-station`
- What it does: This is your Pi's name on the network
- Why: Easier to remember than an IP address

**Example:** Your input should look like the image - `Prometheus-Station`

---

#### Tab 2: "User"

- âœ… Username: `prometheus` (or your choice, but remember it!)
- âœ… Password: Choose something STRONG (you'll type it a lot)
  - Good: `Pr0m3th3us!Station`
  - Bad: `password123`

**Why a custom username?**
- Old default was `pi` (everyone knew this)
- Security best practice: unique username
- Makes brute-force attacks harder

---

#### Tab 3: "Wi-Fi"

- âœ… SSID: **Exactly** as your WiFi network name appears
  - Case-sensitive! "MyWiFi" â‰  "mywifi"
  - Include spaces if your network has them
- âœ… Password: Your WiFi password (also case-sensitive)
- âœ… Wireless LAN country: Select your country
  - France = FR
  - USA = US
  - Critical for legal radio frequencies

**Why this matters:** The Pi will connect to WiFi on first boot, automatically.

---

#### Tab 4: "Localisation"

- âœ… Time zone: Your timezone (e.g., `Europe/Paris`)
- âœ… Keyboard layout: Your keyboard type (e.g., `fr` or `us`)

**Why:** Makes dates/logs readable, typing behaves correctly

---

#### Tab 5: "Remote access"

**This is CRITICAL for headless setup!**

- âœ… Enable SSH: **CHECK THIS BOX**
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

### Step 1.6: Write the OS to SD card

Now that all settings are configured:

1. **Review the summary:**
   - OS: Raspberry Pi OS Lite (64-bit) âœ…
   - Storage: Your 256GB microSD âœ…
   - Customisation applied âœ…

2. **Click "YES"** to proceed with writing

3. **Final confirmation:**
   - "All existing data on [your SD card] will be erased"
   - Click "YES" (you backed up anything important, right?)

4. **Wait for the magic:**
   
   **Progress stages:**
   ```
   Downloading Raspberry Pi OS... [0-30%]
   â”œâ”€ ~500MB download
   â”œâ”€ Speed depends on your internet
   â””â”€ Coffee break time â˜•
   
   Writing to SD card... [30-70%]
   â”œâ”€ Actual OS installation
   â”œâ”€ Takes 5-10 minutes
   â””â”€ Don't eject the card!
   
   Verifying... [70-100%]
   â”œâ”€ Checks everything wrote correctly
   â”œâ”€ Takes 2-5 minutes
   â””â”€ This is important, don't skip!
   ```

5. **Success message appears:**
   ```
   Write Successful
   You can now remove the SD card
   ```

6. **Eject the SD card safely:**
   - Windows: Right-click â†’ "Eject"
   - macOS: Drag to trash (becomes eject icon)
   - Linux: `sudo umount /dev/sdX` (replace X with your device)

**If the write fails:**
- Check SD card isn't write-protected (tiny switch on adapter)
- Try a different SD card reader
- Re-download the OS (might be corrupted)
- Check if SD card is fake (common with cheap ones)

---



---


## ðŸš€ Part 2: First Boot

### Step 2.1: Insert card and power on

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
- Bad SD card write â†’ Re-flash
- Incompatible SD card â†’ Try different brand
- Power supply insufficient â†’ Use official 3A supply

---

### Step 2.2: Find your Pi's IP address

Your Pi is now on your network, but where? You need its IP address to SSH in.

#### Method 1: Check your router (easiest)

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

#### Method 2: Ping by hostname (macOS/Linux)

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

#### Method 3: Network scanner app

**For Android:** Download "Fing" from Play Store
**For iOS:** Download "Fing" from App Store
**For Desktop:** Download "Angry IP Scanner"

1. Open the app
2. Scan your network
3. Look for "Raspberry Pi" or "prometheus-station"
4. Note the IP address

#### Method 4: Connect monitor (last resort)

1. Connect HDMI cable to Pi and monitor
2. Connect USB keyboard
3. Pi will show login screen
4. Type command: `hostname -I`
5. It will print the IP address
6. Write it down

**For the rest of this guide, I'll use `192.168.1.42` as an example. Replace it with YOUR actual IP.**

---

### Step 2.3: SSH into your Raspberry Pi

**This is the moment.** You're about to control your Pi remotely for the first time.

#### On Windows (PowerShell or Command Prompt)

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

**You're in!** ðŸŽ‰

#### On macOS/Linux (Terminal)

1. **Open Terminal:**
   - macOS: `Cmd + Space` â†’ type "Terminal"
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

### ðŸ§  What Just Happened? (SSH Explained)

```
Your Laptop                           Raspberry Pi
    â”‚                                      â”‚
    â”‚  "Hey, I want to control you"       â”‚
    â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€>â”‚
    â”‚                                      â”‚
    â”‚  "Prove you're the owner"           â”‚
    â”‚<â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
    â”‚                                      â”‚
    â”‚  [Sends password]                    â”‚
    â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€>â”‚
    â”‚                                      â”‚
    â”‚  "OK, you're in. Here's a shell"    â”‚
    â”‚<â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
    â”‚                                      â”‚
    â”‚  [You type commands]                 â”‚
    â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€>â”‚
    â”‚                                      â”‚
    â”‚  [Pi executes and sends results]    â”‚
    â”‚<â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
```

Everything you type now runs ON THE RASPBERRY PI, not your laptop.

**Mind-blowing realization:** You could be in a coffee shop in Paris, SSHing into a Pi in Tokyo, and it would work exactly the same way. That's the power of SSH.

---


---

### Phase 3: SSH key authentication setup (10 minutes)

**⚠️ HIGHLY RECOMMENDED - Don't Skip This!**

**The problem:** Typing password for every SSH connection gets old fast. You'll connect 50+ times during this build.

**The solution:** SSH keys = instant, secure, password-free login.

**What you'll gain:**
- ✅ 2-second connections (vs 10 seconds with password)
- ✅ More secure (2048-bit key vs guessable password)
- ✅ Works with scp, rsync, git automatically
- ✅ Industry standard practice

**💡 Real experience:** This saved me ~13 minutes over 100+ connections. Worth the 10min setup!

---

#### For Windows (PowerShell)

**1. Generate SSH key pair:**

```powershell
ssh-keygen -t ed25519 -C "your-email@example.com"
```

**Prompts you'll see:**
```
Generating public/private ed25519 key pair.
Enter file in which to save the key (C:\Users\YourName/.ssh/id_ed25519):
```
- Press **Enter** (accept default location)

```
Enter passphrase (empty for no passphrase):
```
- Press **Enter** for no passphrase (or set one for extra security)
- Press **Enter** again to confirm

**Result:** Key generated in ~2 seconds!

---

**2. Copy public key to Pi:**

```powershell
type $env:USERPROFILE\.ssh\id_ed25519.pub | ssh prometheus@YOUR_PI_IP "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys"
```

Replace `YOUR_PI_IP` with your actual IP (e.g., `192.168.1.42`)

- **You'll be asked for password ONE LAST TIME**
- Type it and press Enter
- This command creates `.ssh` folder on Pi and adds your public key

---

**3. Secure permissions on Pi:**

```bash
ssh prometheus@YOUR_PI_IP
# Once connected:
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
exit
```

**Why:** Prevents other users from reading your authorized keys.

---

**4. Create SSH alias (optional but amazing):**

```powershell
notepad $env:USERPROFILE\.ssh\config
```

If file doesn't exist, Notepad will ask "Do you want to create?" - click **Yes**.

**Add this content:**
```
Host prometheus
    HostName YOUR_PI_IP_OR_HOSTNAME
    User prometheus
    IdentityFile C:\Users\YOUR_USERNAME\.ssh\id_ed25519
```

Replace:
- `YOUR_PI_IP_OR_HOSTNAME` with IP or `prometheus-station.local`
- `YOUR_USERNAME` with your Windows username

**Save and close** (File → Save, then close Notepad)

---

**5. Test the magic:**

```powershell
ssh prometheus
```

**INSTANT CONNECTION. NO PASSWORD!** 🚀

From now on, just type `ssh prometheus` - that's it!

---

#### For macOS/Linux

**1. Generate SSH key:**

```bash
ssh-keygen -t ed25519 -C "your-email@example.com"
```

Press Enter for all prompts (accept defaults, no passphrase).

---

**2. Copy to Pi:**

```bash
ssh-copy-id prometheus@YOUR_PI_IP
```

Replace `YOUR_PI_IP` with your Pi's IP address.

- Enter password when prompted
- Key is automatically copied and permissions set

---

**3. Test:**

```bash
ssh prometheus@YOUR_PI_IP
```

Should connect without password! ✅

**Optional alias (same as Windows):**
```bash
nano ~/.ssh/config
```

Add:
```
Host prometheus
    HostName YOUR_PI_IP
    User prometheus
```

Save (Ctrl+X, Y, Enter)

Now: `ssh prometheus` works!

---

#### What just happened?

Your laptop has two keys:
- **Private key** (`id_ed25519`) - stays on your laptop, NEVER share
- **Public key** (`id_ed25519.pub`) - copied to Pi

When you SSH:
1. Pi says: "Prove you have the private key"
2. Your laptop uses private key to create signature
3. Pi verifies with public key
4. Connection allowed - no password needed!

**More secure than password:** Even if someone sees your username, they can't login without your private key file.

---

## ðŸ”„ Part 3: System Configuration

Now that you're logged in, let's configure the Pi properly.

### Step 3.1: Update the system

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

**Coffee break time â˜•**

**When it finishes:**
```
prometheus@prometheus-station:~ $
```
You're back at the prompt, ready for the next command.

---

### Step 3.2: Configure Raspberry Pi settings

```bash
sudo raspi-config
```

**What is this?** A text-based menu for configuring Pi-specific settings.

You'll see a blue screen with options:

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤ Raspberry Pi Software Configuration Tool â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚                                                                        â”‚
â”‚    1 System Options       Configure system settings                   â”‚
â”‚    2 Display Options      Configure display settings                  â”‚
â”‚    3 Interface Options    Configure connections to peripherals        â”‚
â”‚    4 Performance Options  Configure performance settings              â”‚
â”‚    5 Localisation Options Configure language and regional settings    â”‚
â”‚    6 Advanced Options     Configure advanced settings                 â”‚
â”‚    8 Update               Update this tool to the latest version      â”‚
â”‚    9 About raspi-config   Information about this configuration tool   â”‚
â”‚                                                                        â”‚
â”‚                  <Select>                  <Finish>                    â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

**Navigation:**
- Use **arrow keys** to move up/down
- Press **Enter** to select
- Press **Tab** to move between buttons (`<Select>` / `<Finish>`)
- Press **Esc** twice to exit

---

#### Setting 1: Expand filesystem

Path: `6 Advanced Options` â†’ `A1 Expand Filesystem`

What it does: Makes the entire SD card available (by default, only 2GB is used)

Why: We need all 256GB for Wikipedia files

**Action:**
1. Select `6 Advanced Options`
2. Select `A1 Expand Filesystem`
3. Press Enter on "OK"
4. You're back at main menu

---

#### Setting 2: GPU memory split (may not exist on newer OS) (may not be available)

Path: `4 Performance Options` â†’ `P2 GPU Memory` (if available)

**Important Note:** On newer Raspberry Pi OS versions (late 2024+), this option **may not exist**. GPU memory is now **automatically managed** by the system.

**If you see "P2 GPU Memory":**

What it does: Allocates RAM between CPU and GPU

Why: We're headless (no monitor), so GPU doesn't need much RAM

**Action:**
1. Select `4 Performance Options`
2. Select `P2 GPU Memory`
3. Enter: `16` (minimum for GPU)
4. Press Enter
5. Back to main menu

**What this gives you:** ~16MB saved for CPU/Kiwix = faster searches

**If you DON'T see this option:**
- Your system already manages GPU memory automatically
- This is normal on newer OS versions
- **Skip to Setting 3** - your system is already optimized!

---

#### Setting 3: Enable SSH (verify)

Path: `3 Interface Options` â†’ `I2 SSH`

What it does: Ensures SSH is enabled (should already be from Imager settings)

Why: Double-check it's on

**Action:**
1. Select `3 Interface Options`
2. Select `I2 SSH`
3. Should say "SSH server is enabled"
4. If not, select "Yes" to enable
5. Back to main menu

---

#### Setting 4: Configure hostname (optional)

Path: `1 System Options` â†’ `S4 Hostname`

What it does: Change the network name

Why: If you didn't set it in Imager, or want to change it

**Action:**
1. Select `1 System Options`
2. Select `S4 Hostname`
3. Enter: `prometheus-station`
4. Press Enter

**⚠️ IMPORTANT:** On Raspberry Pi OS versions from late 2024+, this option **may not exist**. GPU memory is now **automatically managed** by the system.

**If you see "P2 GPU Memory":**
1. Select `4 Performance Options`
2. Select `P2 GPU Memory`
3. Enter: `16` (minimum for GPU)
4. Press Enter
5. Back to main menu

**What this gives you:** ~240MB RAM freed for Kiwix

**If you DON'T see this option:**
- This is NORMAL on newer OS versions
- GPU memory is optimized automatically
- **Skip to Setting 3** - your system is already optimized!

---

| `curl` | Download files from URLs | Scripting, API calls |
| `wget` | Alternative file downloader | Backup for curl |
| `vim` | Text editor | Edit config files (alternative to nano) |
| `htop` | Process monitor | See what's using CPU/RAM |
| `ufw` | Firewall | Security (block unwanted connections) |

**Installation takes:** ~2 minutes

---

### Step 3.3b: Install Tailscale (HIGHLY RECOMMENDED) ðŸŒŸ

**What is Tailscale?** A VPN that lets you access your Pi from ANYWHERE in the world, securely.

#### ðŸ§  Why This Changes Everything

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
You're in a cafÃ© in Paris.
Your Pi is at home in Lyon.
Type: ssh prometheus@100.x.x.x (Tailscale IP)
â†’ You're connected instantly. Securely. Magically.
```

**Think of it as:** Your Pi gets a permanent phone number that works globally.

---

#### Installation steps

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

#### Disable Swap (Optional but Recommended)

**What is swap?** When RAM fills up, the system uses SD card as "fake RAM" (swap space).

**Problem:** SD cards are SLOW and wear out from constant writing.

**Solution:** Disable swap (we have 8GB RAM, plenty for our needs).

**⚠️ Note:** Commands have changed in newer Raspberry Pi OS versions. Use this updated method:

```bash
# Turn off swap immediately
sudo swapoff -a

# Prevent swap from coming back after reboot
sudo systemctl disable dphys-swapfile.service 2>/dev/null || sudo systemctl mask swap.target

# Check it's off
free -h
```

**Expected output:**
```
               total        used        free      shared  buff/cache   available
Mem:           7.6Gi       313Mi       6.6Gi       9.6Mi       806Mi       7.3Gi
Swap:             0B          0B          0B
```

See that `Swap: 0B`? Perfect. ✅

**What the commands do:**
- `swapoff -a` → Disables all swap immediately
- `systemctl mask swap.target` → Prevents swap from re-enabling on reboot
- The `2>/dev/null ||` part handles both old and new OS versions gracefully

**Verify after reboot:**
```bash
sudo reboot
```

Wait 30 seconds, reconnect, then:
```bash
free -h
```

Swap should still be `0B`. ✅

**If you have 4GB RAM:** Consider keeping swap enabled (skip these commands).

---

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

**If it works:** You can now access your Pi from anywhere! ðŸŒ

---

#### ðŸ”’ Tailscale Security Configuration

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
2. Under "Machine name" â†’ Edit
3. Set to: `prometheus` (short and easy)
4. Save

**Now you can SSH with:**
```bash
ssh prometheus@prometheus
```

**Even cleaner!** (Tailscale handles the .ts.net domain automatically)

---

#### ðŸŽ¯ How to Use Tailscale Going Forward

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

#### ðŸ’¡ Tailscale Bonus Features

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

#### ðŸ†˜ Tailscale Troubleshooting

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

#### âš ï¸ Important Firewall Update (If Using Tailscale)

If you installed Tailscale, allow it through the firewall:

```bash
# Allow all traffic on Tailscale interface
sudo ufw allow in on tailscale0
```

**Why:** Tailscale creates its own network interface. UFW needs to know it's safe.

---

#### ðŸ“Š Check Tailscale Status Anytime

```bash
# See connected devices
tailscale status

# See your IPs
tailscale ip -4

# Test connection to another device
tailscale ping OTHER_DEVICE_NAME
```

---

#### ðŸŽ“ What You Just Learned

By installing Tailscale, you've:
- âœ… Created a global VPN for your Pi
- âœ… Eliminated the need for port forwarding
- âœ… Made your Pi accessible from anywhere
- âœ… Added military-grade encryption to all connections
- âœ… Future-proofed your deployment (works even if you move)

**This is POWERFUL.** You can now manage Prometheus Station from literally anywhere on Earth with internet. ðŸŒ

---

**Skip Tailscale?** You can, but you'll regret it when you want to check on your Pi remotely and can't. **Just install it now.** Takes 2 minutes, saves hours of frustration later.

---

### Step 3.4: Configure firewall (security)

**Why a firewall?** Your Pi is on your network. A firewall blocks unwanted connections.

#### Enable UFW and set rules

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

âœ… Perfect! Firewall is protecting you while allowing necessary services.

---

### Step 3.5: Optimize system performance

#### Disable Swap (Optional but Recommended)

**What is swap?** When RAM fills up, the system uses SD card as "fake RAM" (swap space).

**Problem:** SD cards are SLOW and wear out from constant writing.

**Solution:** Disable swap (we have 8GB RAM, plenty for our needs).

**Note:** Commands have changed in newer Raspberry Pi OS versions. Use this updated method:

```bash
# Turn off swap immediately
sudo swapoff -a

# Prevent swap from coming back after reboot
sudo systemctl disable dphys-swapfile.service 2>/dev/null || sudo systemctl mask swap.target

# Check it's off
free -h
```

**Expected output:**
```
               total        used        free      shared  buff/cache   available
Mem:           7.6Gi       313Mi       6.6Gi       9.6Mi       806Mi       7.3Gi
Swap:             0B          0B          0B
```

See that `Swap: 0B`? Perfect. âœ…

**What the commands do:**
- `swapoff -a` â†’ Disables all swap immediately
- `systemctl mask swap.target` â†’ Prevents swap from re-enabling on reboot
- The `2>/dev/null ||` part handles both old and new OS versions gracefully

**Verify after reboot:**
```bash
sudo reboot
```

Wait 30 seconds, reconnect, then:
```bash
free -h
```

Swap should still be `0B`. âœ…

**If you have 4GB RAM:** Consider keeping swap enabled (skip these commands).

---

#### Disable unnecessary services

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

### Step 3.6: Create a system monitoring script

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

## âœ… Verification Checklist

Before moving to Step 2 (Kiwix), verify everything works:

### System access
- [ ] Can SSH into Pi from laptop: `ssh prometheus@192.168.1.42`
- [ ] (If installed) Can SSH via Tailscale: `ssh prometheus@100.x.x.x`
- [ ] Filesystem expanded (df -h shows full SD card capacity)
- [ ] System updated (`sudo apt update` shows no pending updates)

### Configuration
- [ ] Hostname set correctly (`hostname` returns `prometheus-station`)
- [ ] GPU memory set to 16MB (`vcgencmd get_mem gpu` returns `gpu=16M`)
- [ ] SSH enabled (`sudo systemctl status ssh` shows "active (running)")
- [ ] (If installed) Tailscale running (`tailscale status` shows connected devices)

### Security
- [ ] Firewall active (`sudo ufw status` shows "Status: active")
- [ ] SSH port allowed (port 22 in firewall rules)
- [ ] Kiwix port allowed (port 80 in firewall rules)
- [ ] (If installed) Tailscale allowed (`tailscale0` interface in ufw rules)

### Performance
- [ ] Swap disabled (`free -h` shows Swap: 0B)
- [ ] Bluetooth disabled (`systemctl status bluetooth` shows "disabled")
- [ ] System monitoring script works (`~/system_status.sh` runs without errors)

### System health
- [ ] Temperature under 60Â°C (`vcgencmd measure_temp`)
- [ ] Free RAM > 6GB (`free -h`)
- [ ] CPU load average < 1.0 (`uptime`)

**All checkboxes ticked?** ðŸŽ‰ **You're ready for Step 2!**

---


---

### 📊 Expected results (tested on real hardware)

**System specs you should see:**

```bash
hostname
# Output: Prometheus-Station (or your chosen name)

uname -a
# Output: Linux Prometheus-Station 6.12.47+rpt-rpi-v8 #1 SMP PREEMPT Debian... (or newer kernel)

vcgencmd measure_temp
# Output: temp=40.0-45.0'C (idle, with fan)

free -h
# Mem: 7.8Gi total, ~7.4Gi free (after fresh boot)
# Swap: 0B 0B 0B

df -h /
# /dev/root: 233G total (for 256GB SD), ~2.1G used initially
```

**What's normal:**
- **Temperature:** 40-50°C idle (with fan), up to 60°C under load
- **Boot time:** ~45-60 seconds from power-on to SSH ready
- **RAM usage:** ~300-500MB after boot
- **Kernel version:** 6.12.x or newer (OS is actively updated)
- **First update:** 40-50 packages typically need updating

**What's NOT normal (troubleshoot if you see this):**
- ❌ Temperature >70°C idle → Check fan, improve cooling
- ❌ RAM usage >2GB idle → Something is wrong, investigate
- ❌ "Under-voltage detected" warnings → Bad power supply!
- ❌ Swap not 0B after disabling → Reboot and verify again
- ❌ SD card showing only 2GB → Filesystem not expanded

---

## ðŸ†˜ Troubleshooting

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
   - macOS: Check System Preferences â†’ Security
   
5. **Pi not booted yet**
   - Solution: Wait 2 full minutes after power-on

---

### Problem: SSH connection drops immediately

**Symptom:** Connects, then disconnects within seconds

**Possible causes:**
1. **Power supply insufficient**
   - Solution: Use official 3A power supply
   - Check for "low voltage" icon on Pi (lightning bolt)
   
2. **SD card corruption**
   - Solution: Re-flash SD card, use quality A2 card
   
3. **Overheating**
   - Solution: Add heatsinks, improve ventilation
   - Check temp: `vcgencmd measure_temp` (should be <80Â°C)

---

### Problem: `sudo apt update` fails

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
   # Navigate to: System Options â†’ Wireless LAN
   # Re-enter SSID and password
   ```

---

### Problem: Filesystem not expanded

**Symptom:** `df -h` shows only 2GB available

**Solution:**
```bash
# Expand manually
sudo raspi-config
# Navigate to: Advanced Options â†’ Expand Filesystem
# Reboot
sudo reboot
```

---

### Problem: Temperature too high

**Symptom:** `vcgencmd measure_temp` shows >70Â°C

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

**Critical:** If temp hits 80Â°C+, Pi will throttle (slow down). At 85Â°C, it will shut down to protect itself.

---

### Problem: Can't remember password

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


---

## ⚠️ Common pitfalls (and how to avoid them)

**Based on real experience building this - these mistakes cost me ~30 minutes combined. You can skip them all!**

### 1. Wrong SD card class
- ❌ **Mistake:** Buying cheap A1 or Class 10 card to save 5€
- ✅ **Solution:** Get A2 class specifically
- **Impact:** 3-5x slower Wikipedia searches, frustrating user experience
- **Why it matters:** A2 has better random read/write for databases

### 2. Weak power supply
- ❌ **Mistake:** Using phone charger (2A) or cheap no-name adapter
- ✅ **Solution:** Official Raspberry Pi power supply (3A) or quality equivalent
- **Impact:** Random reboots, "low voltage" warnings, SD card corruption
- **Why it matters:** Pi 4 needs stable 3A, especially under load

### 3. WiFi network name typos
- ❌ **Mistake:** Typing "MyWiFi" when actual network is "mywifi"  
- ✅ **Solution:** Copy-paste SSID exactly (it's case sensitive!)
- **Impact:** Pi won't connect to WiFi, need monitor/keyboard to debug
- **How to avoid:** Triple-check SSID in Raspberry Pi Imager settings

### 4. Enabling firewall before allowing SSH
- ❌ **Mistake:** Running `sudo ufw enable` before `sudo ufw allow 22/tcp`
- ✅ **Solution:** ALWAYS allow SSH port first, THEN enable firewall
- **Impact:** Locked out of your Pi! Need monitor/keyboard to fix
- **Remember:** SSH = port 22. Allow it before enabling UFW!

### 5. Copying markdown formatting to terminal
- ❌ **Mistake:** Pasting ``` or ** or other markdown into PowerShell/Terminal
- ✅ **Solution:** Only copy actual commands, not the formatting around them
- **Impact:** Confusing "command not found" errors
- **Tip:** If guide shows \`\`\`bash, don't copy that line - start after it!

### 6. PowerShell command syntax (Windows users)
- ❌ **Mistake:** Using `&&` to chain commands (Bash syntax)
- ✅ **Solution:** Use `;` in PowerShell instead
- **Example:** `git add . ; git commit -m "msg" ; git push`
- **Why:** PowerShell and Bash have different syntax for chaining

### 7. Not setting up SSH keys
- ❌ **Mistake:** Skipping SSH key setup to "save time"
- ✅ **Solution:** Take 10 minutes to set up keys now
- **Impact:** You'll waste 13+ minutes typing passwords during build
- **Bonus:** More secure AND more convenient!

**💡 Pro tip:** If something doesn't work, check these pitfalls first. They're the most common issues!

---

## ðŸŽ“ What You've Learned

Congratulations! You've just:

âœ… **Installed an operating system** from scratch  
âœ… **Configured headless access** (no monitor needed)  
âœ… **Secured a Linux system** (firewall, SSH hardening)  
âœ… **Optimized performance** (disabled swap, unnecessary services)  
âœ… **Learned basic Linux commands** (sudo, apt, systemctl)  
âœ… **Troubleshot network issues** (finding IP, SSH debugging)  

**These skills transfer to:**
- Any Raspberry Pi project
- Linux server administration
- IoT device management
- Cloud computing (same principles)

**You're now a sysadmin.** ðŸŽ‰ (Well, baby sysadmin. But still!)

---

## ðŸ“š Useful Commands Reference

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

## ðŸš€ Next Steps

**Your Raspberry Pi is now ready for Kiwix!**

Head to: **[Step 2: Kiwix Installation](02-kiwix-installation.md)**

In Step 2, you'll:
- Install Kiwix server software
- Download Wikipedia ZIM files (~171GB)
- Configure Kiwix as a systemd service
- Access Wikipedia through your browser

**Estimated time:** 3-4 hours (mostly downloading)

See you there! ðŸ”¥

---

**Last updated:** December 2025  
**Tested on:** Raspberry Pi 4 (8GB), Raspberry Pi OS Lite (64-bit)  
**Written by:** Guillain d'Erceville

*Questions? Open an issue on GitHub!*

---

## ⏱️ Time analysis (tested real build)

| Phase | Actual Time | Notes |
|-------|-------------|-------|
| SD Card Prep | 28 min | First time, learning Imager interface |
| First Boot & Find IP | 20 min | Exploring router, testing connectivity |
| SSH Key Setup | 10 min | Worth every second - saves time later! |
| System Configuration | 45 min | System updates took ~35min on 50 Mbps connection |
| **TOTAL** | **1h 45min** | Smooth process, zero blockers |

**Time Perspective:**
- **First-time build:** ~2 hours with learning and exploration
- **Repeat builds:** ~1 hour once you know the process
- **Waiting time:** ~45min (downloads, updates - make coffee!)
- **Active hands-on time:** ~60min

**What slows you down:**
- Internet speed (for OS download + system updates)
- First time learning Raspberry Pi Imager
- Finding Pi's IP address if router is unfamiliar

**What speeds you up:**
- SSH keys (instant connections)
- Headless setup (no monitor juggling)
- This guide (skip my mistakes!)

---

## 💡 PowerShell vs Bash quick reference

**For Windows users:** Some command syntax differs from Linux/macOS guides.

**Chaining commands:**
```powershell
# ❌ WRONG (Bash syntax):
sudo apt update && sudo apt upgrade -y

# ✅ RIGHT (PowerShell):
# Just run commands separately, or use:
sudo apt update ; sudo apt upgrade -y
```

**Why:** PowerShell uses `;` not `&&` for command chaining.

**Paths:**
```powershell
# Bash uses:
~/.ssh/config

# PowerShell uses:
$env:USERPROFILE\.ssh\config
```

**When in doubt:** Just run commands one at a time instead of chaining.

---

