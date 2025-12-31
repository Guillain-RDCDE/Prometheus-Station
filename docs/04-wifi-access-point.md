# Step 4: Wifi access point configuration

**Goal:** Configure intelligent WiFi that connects to known networks OR creates a hotspot automatically.

**Time Required:** 1-2 hours  
**Difficulty:** ⭐⭐⭐ Medium

**💡 Real experience:** This configuration was tested and debugged in real-world conditions. Every error you might encounter is documented here with solutions.

---

## 📋 Prerequisites

- [ ] ✅ Completed [Step 1 - Raspberry Pi Setup](01-raspberry-setup.md)
- [ ] ✅ Completed [Step 2 - Kiwix Installation](02-kiwix-installation.md)
- [ ] ✅ Completed [Step 3 - Kiwix Configuration](03-kiwix-configuration.md)
- [ ] SSH access to your Pi
- [ ] Pi currently connected to internet (for installing packages)

---

## 🎯 What we're building

**Intelligent WiFi behavior:**

```
┌─────────────────────────────────────────────────────────┐
│              PROMETHEUS STATION LOGIC                    │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  AT HOME (Known WiFi available):                        │
│  ├─ wlan0 connects to your WiFi (client mode)          │
│  ├─ You can SSH normally                                │
│  └─ Pi has internet access                              │
│                                                          │
│  IN THE FIELD (No known WiFi):                          │
│  ├─ wlan0 creates hotspot "Prometheus-Station"         │
│  ├─ Users connect to access Kiwix                       │
│  └─ Works 100% offline                                  │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## 🧠 Understanding the approach

### Why this method works

We're **NOT** fighting against NetworkManager. Instead:

1. ✅ **At home:** NetworkManager manages wlan0 normally (WiFi client)
2. ✅ **In field:** We manually switch to hotspot mode
3. ✅ **Simple scripts** to toggle between modes
4. ✅ **No complex automation** that breaks randomly

### The two modes

**Mode 1: HOME (WiFi Client)**
- NetworkManager controls wlan0
- Connects to known WiFi networks
- Easy SSH access
- Pi has internet

**Mode 2: FIELD (Hotspot)**
- hostapd + dnsmasq control wlan0
- Creates access point
- Users connect for offline content
- No internet dependency

---

## 📦 Part 1: Install required packages (5 minutes)

### Step 1.1: Install hostapd and dnsmasq

```bash
sudo apt update
sudo apt install -y hostapd dnsmasq
```

**What these do:**
- **hostapd** - Creates the WiFi access point
- **dnsmasq** - Provides DHCP (assigns IPs) and DNS

---

### Step 1.2: Stop and disable services

```bash
# Stop services (we'll start them manually when needed)
sudo systemctl stop hostapd
sudo systemctl stop dnsmasq

# Disable auto-start
sudo systemctl disable hostapd
sudo systemctl disable dnsmasq
```

**Why disable?** We don't want them starting automatically and conflicting with NetworkManager at home.

---

## 🔧 Part 2: Configure hostapd (20 minutes)

### Step 2.1: Create hostapd configuration

```bash
sudo nano /etc/hostapd/hostapd.conf
```

**Paste this COMPLETE configuration:**

```
# Prometheus Station - Access Point Configuration

interface=wlan0
driver=nl80211

# Network name (SSID)
ssid=Prometheus-Station

# 2.4GHz mode
hw_mode=g
channel=6

# 802.11n support (basic, no HT40)
ieee80211n=1
wmm_enabled=0

# Security settings
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0

# WPA2 encryption
wpa=2
wpa_key_mgmt=WPA-PSK
wpa_passphrase=12345678
wpa_pairwise=TKIP
rsn_pairwise=CCMP

# Country code (regulatory domain)
country_code=FR

# Maximum connected clients
max_num_sta=30
```

**🔒 IMPORTANT NOTES:**

1. **Password length:** MUST be 8-63 characters for WPA2
   - ✅ `12345678` works
   - ❌ `12345` is TOO SHORT and will fail
   - ❌ `1234578` (typo) will fail

2. **Country code:** Change `FR` to your country:
   - `FR` = France
   - `US` = United States
   - `GB` = United Kingdom
   - `DE` = Germany

3. **Channel:** 
   - Channels 1, 6, 11 don't overlap
   - Usually 6 works well
   - Change if you have interference

4. **NO HT40 configuration:** 
   - Raspberry Pi WiFi doesn't support HT40 in AP mode
   - Stick to basic 802.11n settings shown above

**Save:** Ctrl+X, Y, Enter

---

### Step 2.2: Point to configuration file

```bash
sudo nano /etc/default/hostapd
```

**Find the line:**
```
#DAEMON_CONF=""
```

**Change it to:**
```
DAEMON_CONF="/etc/hostapd/hostapd.conf"
```

**Save:** Ctrl+X, Y, Enter

---

### Step 2.3: Verify configuration

```bash
# Test the configuration syntax
sudo hostapd -dd /etc/hostapd/hostapd.conf 2>&1 | head -20
```

**Look for errors.** Common ones:

**❌ "invalid WPA passphrase length 7"**
→ Password too short, must be 8+ characters

**❌ "Hardware does not support configured channel"**
→ You have HT40 config, remove it (use config above)

**Press Ctrl+C** to stop the test.

**If no errors,** you'll see normal initialization messages. That's good!

---

## 🌐 Part 3: Configure dnsmasq (15 minutes)

### Step 3.1: Backup original config

```bash
sudo mv /etc/dnsmasq.conf /etc/dnsmasq.conf.backup
```

---

### Step 3.2: Create new configuration

```bash
sudo nano /etc/dnsmasq.conf
```

**Paste this COMPLETE configuration:**

```
# Prometheus Station - DHCP/DNS Configuration

# Interface to bind to
interface=wlan0
bind-interfaces

# DHCP range - assigns IPs to connected devices
dhcp-range=192.168.42.10,192.168.42.250,255.255.255.0,24h

# Gateway (the Pi itself)
dhcp-option=3,192.168.42.1

# DNS servers (Pi first, then Google as backup)
dhcp-option=6,192.168.42.1,8.8.8.8

# Domain name
domain=prometheus.local
local=/prometheus.local/
expand-hosts

# DNS entries - point to the Pi
address=/prometheus.local/192.168.42.1
address=/prometheus-station.local/192.168.42.1

# We are the DHCP authority on this network
dhcp-authoritative

# Don't read system resolv.conf
no-resolv

# Upstream DNS servers (for internet queries if available)
server=8.8.8.8
server=8.8.4.4

# Don't forward private IP queries
bogus-priv

# Enable logging (useful for troubleshooting)
log-queries
log-dhcp
```

**What this does:**
- Assigns IPs from `192.168.42.10` to `192.168.42.250`
- Sets Pi as gateway (`192.168.42.1`)
- Provides DNS resolution
- Logs connections (check with `sudo journalctl -u dnsmasq`)

**Save:** Ctrl+X, Y, Enter

---

## 🧪 Part 4: Manual testing (15 minutes)

**Before automating, let's verify everything works manually.**

### Step 4.1: Switch to hotspot mode

```bash
# 1. Tell NetworkManager to stop managing wlan0
sudo nmcli device set wlan0 managed no

# 2. Configure static IP on wlan0
sudo ip addr flush dev wlan0
sudo ip addr add 192.168.42.1/24 dev wlan0
sudo ip link set wlan0 up

# 3. Start DHCP server
sudo systemctl start dnsmasq

# 4. Start access point
sudo systemctl start hostapd

# 5. Verify services are running
sudo systemctl status hostapd
sudo systemctl status dnsmasq
```

**Expected output for hostapd:**
```
● hostapd.service - Access point and authentication server
     Active: active (running)
     ...
     wlan0: AP-ENABLED
```

**Expected output for dnsmasq:**
```
● dnsmasq.service - dnsmasq - A lightweight DHCP and caching DNS server
     Active: active (running)
```

---

### Step 4.2: Verify wifi mode

```bash
iwconfig wlan0
```

**Expected output:**
```
wlan0     IEEE 802.11  ESSID:"Prometheus-Station"
          Mode:Master  Tx-Power=31 dBm
          ...
```

**Key indicators:**
- ✅ `ESSID:"Prometheus-Station"` - Network name correct
- ✅ `Mode:Master` - In access point mode

---

### Step 4.3: Test with phone/laptop

**From your phone or laptop:**

1. **Open WiFi settings**
2. **Scan for networks**
3. **Find:** `Prometheus-Station`
4. **Connect with password:** `12345678`
5. **You should:**
   - See "Connected" status
   - Get IP address like `192.168.42.42`
   - May see "No Internet" warning (normal, we're offline)

---

### Step 4.4: Test content access

**From your connected device, open browser:**

```
http://192.168.42.1
```

**You should see:**
- ✅ Prometheus Station landing page
- ✅ Links to all ZIM files (Kiwix content)
- ✅ Can click and browse Wikipedia articles

**Test navigation:**
- Click on a content card
- Search for an article
- Verify images load
- Check that everything is responsive

---

### Step 4.5: Check connected devices

**On the Pi, view connected clients:**

```bash
# See DHCP leases
cat /var/lib/misc/dnsmasq.leases
```

**Example output:**
```
1735584123 aa:bb:cc:dd:ee:ff 192.168.42.42 iPhone-de-Guillaume 01:aa:bb:cc:dd:ee:ff
```

Shows:
- Timestamp
- MAC address
- Assigned IP
- Device hostname
- Client identifier

---

## 🔄 Part 5: Switching between modes (10 minutes)

### Creating toggle scripts

We'll create two simple scripts to switch modes.

---

### Script 1: Switch to home mode (wifi client)

```bash
nano ~/switch-to-home.sh
```

**Paste:**

```bash
#!/bin/bash
# Prometheus Station - Switch to HOME mode (WiFi client)

echo "========================================"
echo " Switching to HOME mode (WiFi Client)"
echo "========================================"
echo ""

# Stop hotspot services
echo "Stopping hotspot..."
sudo systemctl stop hostapd
sudo systemctl stop dnsmasq

# Let NetworkManager manage wlan0 again
echo "Activating NetworkManager on wlan0..."
sudo nmcli device set wlan0 managed yes

# Wait for connection
echo "Waiting for WiFi connection..."
sleep 10

# Check status
echo ""
echo "Status:"
nmcli device status | grep wlan0

echo ""
echo "✓ Switched to HOME mode"
echo "  wlan0 will connect to known WiFi networks"
echo ""
```

**Save:** Ctrl+X, Y, Enter

**Make executable:**
```bash
chmod +x ~/switch-to-home.sh
```

---

### Script 2: Switch to field mode (hotspot)

```bash
nano ~/switch-to-field.sh
```

**Paste:**

```bash
#!/bin/bash
# Prometheus Station - Switch to FIELD mode (Hotspot)

echo "========================================"
echo " Switching to FIELD mode (Hotspot)"
echo "========================================"
echo ""

# Stop NetworkManager on wlan0
echo "Stopping NetworkManager on wlan0..."
sudo nmcli device set wlan0 managed no

# Configure static IP
echo "Configuring static IP..."
sudo ip addr flush dev wlan0
sudo ip addr add 192.168.42.1/24 dev wlan0
sudo ip link set wlan0 up

# Start DHCP server
echo "Starting DHCP server..."
sudo systemctl start dnsmasq

# Start access point
echo "Starting access point..."
sudo systemctl start hostapd

# Wait for services to start
sleep 3

# Check status
echo ""
echo "Status:"
sudo systemctl is-active hostapd && echo "  hostapd: ✓ Running" || echo "  hostapd: ✗ Failed"
sudo systemctl is-active dnsmasq && echo "  dnsmasq: ✓ Running" || echo "  dnsmasq: ✗ Failed"

echo ""
echo "✓ Switched to FIELD mode"
echo "  Hotspot: Prometheus-Station"
echo "  Password: 12345678"
echo "  Access at: http://192.168.42.1"
echo ""
```

**Save:** Ctrl+X, Y, Enter

**Make executable:**
```bash
chmod +x ~/switch-to-field.sh
```

---

### Using the scripts

**To switch to home mode (WiFi client):**
```bash
~/switch-to-home.sh
```

**To switch to field mode (hotspot):**
```bash
~/switch-to-field.sh
```

---

### Test the scripts now

**1. Currently in hotspot mode, switch back to home:**

```bash
~/switch-to-home.sh
```

**Wait 10-15 seconds, then verify:**
```bash
nmcli device status
iwconfig wlan0
```

**Should show wlan0 connected to your home WiFi.**

---

**2. Switch back to hotspot:**

```bash
~/switch-to-field.sh
```

**Verify with your phone** - you should see "Prometheus-Station" again.

---

## 📝 Part 6: Update connection instructions (10 minutes)

### Update the landing page password

```bash
sudo nano /var/www/html/connect.html
```

**Find ALL occurrences of the old password and update:**

**Change:**
```html
Password: <span class="credential">12345</span>
```

**To:**
```html
Password: <span class="credential">12345678</span>
```

**There are multiple places in the file - update them all!**

**Use Ctrl+W to search** for `12345` and make sure you get every instance.

**Save:** Ctrl+X, Y, Enter

---

### Update main landing page (if needed)

```bash
sudo nano /var/www/html/index.html
```

**If there's a password reference, update it to `12345678`.**

**Save:** Ctrl+X, Y, Enter

---

## ✅ Part 7: Complete testing checklist

### Mode: HOME (wifi client)

**Switch to home mode:**
```bash
~/switch-to-home.sh
```

**Verify:**
- [ ] wlan0 shows as "connected" to your WiFi: `nmcli device status`
- [ ] Can SSH to Pi from your network: `ssh guillain@prometheus-station.local`
- [ ] Pi has internet access: `ping -c 3 google.com`
- [ ] iwconfig shows `Mode:Managed`

---

### Mode: FIELD (hotspot)

**Switch to field mode:**
```bash
~/switch-to-field.sh
```

**Verify:**
- [ ] hostapd running: `sudo systemctl is-active hostapd` returns "active"
- [ ] dnsmasq running: `sudo systemctl is-active dnsmasq` returns "active"
- [ ] iwconfig shows `Mode:Master` and `ESSID:"Prometheus-Station"`
- [ ] Phone/laptop can see "Prometheus-Station" network
- [ ] Can connect with password `12345678`
- [ ] Device receives IP in range 192.168.42.x
- [ ] Can access http://192.168.42.1 from connected device
- [ ] Kiwix content loads and works
- [ ] Can search and browse articles
- [ ] Images load correctly

---

### Switching between modes

- [ ] Can switch from home to field: `~/switch-to-field.sh`
- [ ] Can switch from field to home: `~/switch-to-home.sh`
- [ ] No errors in switching process
- [ ] Each mode works after switching
- [ ] Scripts complete in <15 seconds

---

## 🛠️ Part 8: Troubleshooting

### Problem: hostapd fails to start

**Symptom:**
```
Job for hostapd.service failed because the control process exited with error code
```

**Diagnosis:**
```bash
sudo journalctl -xeu hostapd.service -n 30 --no-pager
```

---

**Common Error 1: "invalid WPA passphrase length"**

```
Line 25: invalid WPA passphrase length 7 (expected 8..63)
```

**Solution:**
```bash
sudo nano /etc/hostapd/hostapd.conf

# Ensure wpa_passphrase is 8-63 characters
wpa_passphrase=12345678  # ✅ Correct (8 chars)
# NOT: wpa_passphrase=12345  # ❌ Too short (5 chars)
# NOT: wpa_passphrase=1234578  # ❌ Typo (7 chars)
```

---

**Common Error 2: "Hardware does not support configured channel"**

```
wlan0: IEEE 802.11 Hardware does not support configured channel
Configured channel (6) or frequency (2437) (secondary_channel=1) not found
```

**Solution:** You have HT40 configuration which Raspberry Pi doesn't support in AP mode.

```bash
sudo nano /etc/hostapd/hostapd.conf

# Remove or comment out these lines:
# ht_capab=[HT40+][SHORT-GI-20][DSSS_CCK-40]

# Use simple config:
ieee80211n=1
wmm_enabled=0
```

**Restart:**
```bash
sudo systemctl restart hostapd
```

---

**Common Error 3: "restart request repeated too quickly"**

```
hostapd.service: Start request repeated too quickly
```

**Solution:**
```bash
# Reset the failure state
sudo systemctl reset-failed hostapd

# Wait 5 seconds
sleep 5

# Try again
sudo systemctl start hostapd
```

---

### Problem: Can't connect to hotspot

**Symptom:** Phone finds network but won't connect, or asks for password repeatedly

**Solutions:**

**1. Verify password in config:**
```bash
cat /etc/hostapd/hostapd.conf | grep wpa_passphrase
```

Should show exactly 8-63 characters, no typos.

---

**2. Check hostapd is running:**
```bash
sudo systemctl status hostapd
```

Must show `Active: active (running)` and `AP-ENABLED`.

---

**3. Verify wlan0 mode:**
```bash
iwconfig wlan0
```

Must show `Mode:Master`.

---

**4. Restart services:**
```bash
sudo systemctl restart hostapd
sudo systemctl restart dnsmasq
```

---

### Problem: Connected but no IP address

**Symptom:** Phone connects to WiFi but shows "Obtaining IP address..." forever

**Solutions:**

**1. Check dnsmasq is running:**
```bash
sudo systemctl status dnsmasq
```

**2. Verify wlan0 has static IP:**
```bash
ip addr show wlan0
```

Should show `inet 192.168.42.1/24`.

**3. Check dnsmasq logs:**
```bash
sudo journalctl -u dnsmasq -n 50
```

Look for DHCP requests and offers.

---

**4. Restart DHCP:**
```bash
sudo systemctl restart dnsmasq
```

---

### Problem: Can access hotspot but not Kiwix

**Symptom:** Connected to WiFi, have IP, but http://192.168.42.1 doesn't load

**Solutions:**

**1. Verify Kiwix is running:**
```bash
sudo systemctl status kiwix-serve
```

**2. Test from Pi itself:**
```bash
curl http://localhost
```

Should return HTML content.

---

**3. Check firewall:**
```bash
sudo ufw status
```

Port 80 should be allowed.

If not:
```bash
sudo ufw allow 80/tcp
sudo ufw reload
```

---

**4. Restart Apache/Kiwix:**
```bash
sudo systemctl restart apache2
sudo systemctl restart kiwix-serve
```

---

### Problem: Hotspot disappears randomly

**Symptom:** Hotspot works initially but stops broadcasting after some time

**Solutions:**

**1. Check for thermal issues:**
```bash
vcgencmd measure_temp
```

If >70°C, add cooling.

---

**2. Disable WiFi power management:**
```bash
sudo iwconfig wlan0 power off

# Make permanent
sudo nano /etc/rc.local
# Add before 'exit 0':
iwconfig wlan0 power off
```

---

**3. Check system logs:**
```bash
sudo journalctl -u hostapd -f
```

Watch for disconnection messages.

---

## 📊 Part 9: Performance metrics

### Expected performance

**With 5 concurrent users:**
- Page load time: 1-3 seconds
- Search results: <2 seconds
- CPU usage: 30-50%
- Temperature: 50-60°C

**With 15 concurrent users:**
- Page load time: 2-5 seconds
- Search results: 2-4 seconds
- CPU usage: 50-80%
- Temperature: 60-70°C

**Maximum recommended:** 20-30 concurrent users

---

### Monitoring performance

**Create monitoring script:**

```bash
nano ~/monitor-hotspot.sh
```

**Paste:**

```bash
#!/bin/bash
# Monitor Prometheus Station hotspot

echo "=== HOTSPOT STATUS ==="
echo ""

# Connected clients
CLIENTS=$(iw dev wlan0 station dump 2>/dev/null | grep Station | wc -l)
echo "Connected clients: $CLIENTS"
echo ""

# Services
echo "Services:"
sudo systemctl is-active hostapd >/dev/null 2>&1 && echo "  hostapd: ✓" || echo "  hostapd: ✗"
sudo systemctl is-active dnsmasq >/dev/null 2>&1 && echo "  dnsmasq: ✓" || echo "  dnsmasq: ✗"
echo ""

# System resources
echo "System:"
echo "  CPU: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)%"
echo "  Temp: $(vcgencmd measure_temp)"
echo "  RAM: $(free -h | awk 'NR==2{printf "%s / %s", $3,$2}')"
echo ""

# DHCP leases
echo "Active leases:"
cat /var/lib/misc/dnsmasq.leases 2>/dev/null | awk '{print "  " $3 " - " $4}' || echo "  None"
echo ""
```

**Save:** Ctrl+X, Y, Enter

**Make executable:**
```bash
chmod +x ~/monitor-hotspot.sh
```

**Use it:**
```bash
~/monitor-hotspot.sh
```

---

## 🌍 Part 10: Field deployment guide

### Pre-deployment checklist

**Before going to the field:**

- [ ] Test hotspot at home (works ✓)
- [ ] Test with 5+ devices simultaneously
- [ ] Verify content accessible (Kiwix loads)
- [ ] Test 24-hour continuous operation
- [ ] Check temperature under load (<65°C)
- [ ] Print connection instructions
- [ ] Note WiFi password on station label
- [ ] Charge all batteries fully
- [ ] Test solar charging (if applicable)

---

### Deployment procedure

**1. On-site setup:**

```bash
# SSH into Pi (via Tailscale or Ethernet initially)
ssh guillain@prometheus-station.local

# Switch to field mode
~/switch-to-field.sh

# Verify hotspot active
~/monitor-hotspot.sh

# Disconnect Ethernet (if used)
# Hotspot should remain active
```

**2. Position for optimal coverage:**
- Elevated location (table, shelf, mast)
- Central to coverage area
- Away from metal objects
- Good ventilation

**3. Test signal strength:**
- Walk to perimeter of coverage area
- Verify WiFi signal visible
- Test connection from furthest point

---

### User instructions template

**Print and display near station:**

```
╔════════════════════════════════════════════╗
║    PROMETHEUS STATION - HOW TO CONNECT     ║
╚════════════════════════════════════════════╝

📶 STEP 1: CONNECT TO WIFI
   Network Name: Prometheus-Station
   Password: 12345678

📱 STEP 2: OPEN WEB BROWSER
   Address: http://192.168.42.1

📚 STEP 3: ACCESS CONTENT
   • Emergency Medical Protocols
   • Wikipedia Encyclopedia  
   • Survival Guides

⚠️ NOTE: "No Internet" warning is NORMAL
         All content works offline

ℹ️ TROUBLESHOOTING:
   Can't connect?
   1. Forget network and reconnect
   2. Turn WiFi off/on
   3. Restart your device
   
   Need help? Ask station operator.

╔════════════════════════════════════════════╗
║         STATION ACTIVE 24/7                ║
╚════════════════════════════════════════════╝
```

---

## 🎓 What you've learned

Congratulations! You now know how to:

✅ **Configure hostapd** for WiFi access point  
✅ **Setup dnsmasq** for DHCP and DNS  
✅ **Debug WPA2 password issues** (length requirements)  
✅ **Troubleshoot channel/hardware conflicts**  
✅ **Create mode-switching scripts** for flexibility  
✅ **Test WiFi hotspot functionality** thoroughly  
✅ **Monitor connected clients and performance**  
✅ **Deploy offline knowledge infrastructure** in field  

**Skills gained:**
- WiFi access point configuration
- DHCP/DNS server management
- NetworkManager interaction
- Bash scripting for system control
- Field deployment procedures
- User support documentation

---

## 🎯 Next steps

**Your WiFi configuration is complete!** Choose your path:

### **Option A: Continue with meshtastic** (recommended)
→ [Step 5 - Meshtastic Setup](05-meshtastic-setup.md)
- Long-range LoRa communication
- Mesh networking (1-15km range)
- Integration with hotspot

### **Option B: Solar power** (if hardware ready)
→ [Step 6 - Solar Power Setup](06-solar-power.md)
- Autonomous operation
- Battery management
- Power optimization

### **Option C: Test current setup**
- Run for 24-48 hours
- Monitor stability
- Test with multiple users
- Document any issues

---

## 📚 Additional resources

### Documentation
- [hostapd Documentation](https://w1.fi/hostapd/)
- [dnsmasq Manual](http://www.thekelleys.org.uk/dnsmasq/doc.html)
- [Raspberry Pi Access Point Guide](https://www.raspberrypi.org/documentation/configuration/wireless/access-point-routed.md)

### Tools
- [WiFi Analyzer (Android)](https://play.google.com/store/apps/details?id=com.farproc.wifi.analyzer) - Check channel interference
- [Network Analyzer (iOS)](https://apps.apple.com/app/network-analyzer/id562315041) - Scan and troubleshoot

### Community
- [Raspberry Pi Forums - Networking](https://forums.raspberrypi.com/viewforum.php?f=36)
- [/r/raspberry_pi](https://reddit.com/r/raspberry_pi)

---

## ⏱️ Time breakdown

**From tested real-world build:**

| Phase | Time | Notes |
|-------|------|-------|
| Install packages | 5 min | Fast on good connection |
| Configure hostapd | 20 min | Including password debugging |
| Configure dnsmasq | 15 min | Straightforward |
| Manual testing | 15 min | First successful connection |
| Create scripts | 10 min | Copy-paste, test |
| Update docs | 10 min | Password corrections |
| Full testing | 15 min | Both modes, multiple devices |
| **TOTAL** | **1h 30min** | With troubleshooting included |

**Time savers:**
- Copy configurations exactly (don't type)
- Verify password length BEFORE starting hostapd
- Use scripts instead of manual commands
- Test incrementally (don't skip verification steps)

---

## 🔐 Security considerations

### Current setup (field deployment)

**Password:** `12345678`
- ✅ Meets WPA2 minimum (8 chars)
- ⚠️ Not very strong
- ✅ Easy to communicate verbally
- ✅ Appropriate for humanitarian/emergency use

### For different contexts

**High-security environment:**
```
wpa_passphrase=Pr0m3th3us!St@ti0n#2025
```

**Public access (no password):**
```bash
# Edit /etc/hostapd/hostapd.conf
# Remove these lines:
# wpa=2
# wpa_key_mgmt=WPA-PSK
# wpa_passphrase=12345678
# wpa_pairwise=TKIP
# rsn_pairwise=CCMP

# Add:
# auth_algs=1  (already there)
```

**Warning:** Open networks have security implications. Only use in controlled environments.

---

## 💾 Backup recommendation

**Now that WiFi works, create a system backup:**

1. **Shutdown Pi:** `sudo shutdown -h now`
2. **Remove SD card**
3. **Image with Win32DiskImager or dd**
4. **Label:** "Prometheus-Station-WiFi-Working-YYYY-MM-DD.img"
5. **Store safely**

**This is your recovery point** if anything breaks later!

---

**Last updated:** December 30, 2025  
**Tested on:** Raspberry Pi 4 8GB, Raspberry Pi OS Lite (64-bit)  
**Hardware:** Built-in WiFi adapter (no external dongle required)  
**Real-world testing:** 15 concurrent users, 8-hour continuous operation, stable performance

---

*Made with 🔥 for Prometheus Station - Tested, debugged, and verified in real deployment conditions*
