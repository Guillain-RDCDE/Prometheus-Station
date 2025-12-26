# Day 1 - December 26, 2025 (Afternoon)

[← Back to Journal](../JOURNAL.md) | [← Previous: Day 0](day-0.md) | [Next: Day 2 →](day-2.md)

---

## ✅ Step 1: Raspberry Pi Setup - COMPLETED

**Total time:** 1h 45min  
**Difficulty:** ⭐⭐☆☆☆ Easy

---

## Summary

Today was ALL about getting the Raspberry Pi up and running. Everything worked on the first try!

**Major accomplishments:**
- ✅ Flashed Raspberry Pi OS with headless configuration
- ✅ SSH access working (with key authentication!)
- ✅ System updated and optimized
- ✅ Firewall configured
- ✅ Monitoring tools in place

---

## What I Did

### 1. SD Card Preparation (30 minutes)

**Downloaded Raspberry Pi Imager v2.0.0**
- Flashed Raspberry Pi OS Lite (64-bit) to 256GB SD card
- Configured headless setup (WiFi + SSH enabled)
- Hostname: `prometheus-station`
- Username: `guillain`

**Settings:**
- Timezone: Europe/Paris
- Keyboard: French (AZERTY)
- WiFi: Connected on first boot
- SSH: Enabled for remote access

---

### 2. First Boot & SSH Connection (20 minutes)

**Hardware setup:**
- Inserted SD card
- Connected USB-C power (5V 3A)
- Boot time: ~45 seconds

**Found IP address:** `192.168.1.41` via router

**First SSH connection:**
```bash
ssh guillain@prometheus-station
```

**SUCCESS!** 🎉 Headless setup worked perfectly!

---

### 3. SSH Key Authentication (10 minutes)

Generated ED25519 key pair on Windows:
```powershell
ssh-keygen -t ed25519 -C "guillain@prometheus-station"
```

Copied public key to Pi, set up SSH config.

**Result:** Now I can connect with just:
```bash
ssh prometheus
```

**No password, instant connection!** Time saved: ~13 minutes over 100+ connections.

---

### 4. System Configuration (45 minutes)

**System updates:**
```bash
sudo apt update && sudo apt upgrade -y
```
- 47 packages updated
- Download: ~68 MB
- Time: ~35 minutes

**raspi-config settings:**
- ✅ Expanded filesystem (full 256GB available)
- ✅ GPU memory set to 16MB (freed RAM for Kiwix)
- ✅ SSH verified enabled

**Essential packages installed:**
```bash
sudo apt install -y git curl wget vim htop ufw
```

**Firewall configured:**
```bash
sudo ufw allow 22/tcp  # SSH
sudo ufw allow 80/tcp  # Kiwix (future)
sudo ufw enable
```

**Performance optimizations:**
- Disabled swap (SD card protection + 8GB RAM sufficient)
- Disabled Bluetooth service
- Disabled audio service
- Saved: ~50-100 MB RAM, ~2-3s boot time

**Created monitoring script:**
```bash
~/system_status.sh
```
Shows: uptime, temperature, memory, disk, network, connections

---

## Problems Encountered

### 1. SSH Password Annoyance
**Solution:** SSH key authentication  
**Time to fix:** 10 minutes  
**Result:** 2-second instant connections

### 2. PowerShell vs Bash Syntax
**Issue:** `&&` doesn't work in PowerShell  
**Solution:** Use `;` instead  
**Lesson:** Windows ≠ Linux syntax

### 3. Markdown Confusion
**Issue:** Copied ``` formatters into PowerShell  
**Solution:** Only copy actual commands  
**Lesson:** Backticks are for display, not execution!

---

## Final Verification ✅

**System Access:**
- ✅ Can SSH into Pi: `ssh prometheus`
- ✅ Filesystem expanded: 233G total
- ✅ System updated: 0 pending updates

**Configuration:**
- ✅ Hostname: `Prometheus-Station`
- ✅ GPU memory: 16M
- ✅ SSH enabled and running

**Security:**
- ✅ Firewall active
- ✅ SSH port allowed (22)
- ✅ Kiwix port ready (80)

**Performance:**
- ✅ Swap disabled (0B)
- ✅ Bluetooth disabled
- ✅ Temperature: 42.8°C (excellent)
- ✅ Free RAM: 7.4 GB
- ✅ CPU load: 0.08 (idle)

**ALL CHECKS PASSED!** ✅

---

## What I Learned

**Technical skills:**
- Flashing OS with preconfiguration
- Headless Raspberry Pi setup
- SSH key authentication
- Linux firewall (UFW)
- systemd service management
- Performance tuning

**Key concepts:**
- Why SSH keys beat passwords
- Headless setup saves massive time
- File permissions (chmod 700/600)
- Firewall port management
- RAM vs swap trade-offs

**Commands mastered:**
- `ssh` / `ssh-keygen`
- `sudo apt update/upgrade`
- `sudo systemctl`
- `sudo ufw`
- `chmod`
- `free` / `df` / `htop`

---

## Time Analysis

| Phase | Estimated | Actual | Notes |
|-------|-----------|--------|-------|
| SD Card Prep | 15-20 min | 28 min | First time, learning interface |
| First Boot & IP | 2-5 min | 20 min | Exploring, testing |
| SSH Key Setup | Not in guide | 10 min | Worth it! |
| System Config | 30-45 min | 45 min | Right on target |
| **TOTAL** | **~50-70 min** | **1h 45min** | Reasonable |

**Reflection:**
- First-time builds take longer (learning curve)
- Extra time on SSH keys will save time later
- No major blockers, smooth process

---

## Statistics

**Commands run:** ~35  
**Packages installed:** 53  
**Data downloaded:** ~551 MB  
**SSH connections:** ~15  
**Reboots:** 2  
**Errors:** 0  
**Coffee:** 2 ☕☕

---

## Personal Notes

**Mood:** 😃 Very satisfied!

**Highlights:**
- Everything worked first try!
- SSH keys are a game-changer
- Headless setup = no monitor hassle
- Clear documentation helped

**Confidence:**
- Before: 6/10 (nervous)
- After: 8/10 (I can do this!)

**Surprised by:**
- How easy headless setup is
- How fast Pi boots
- Windows SSH works great
- Monitoring script usefulness

---

## Next Steps

**Completed:**
- ✅ Raspberry Pi OS installed
- ✅ SSH working
- ✅ System optimized
- ✅ Firewall configured

**Tomorrow (Day 2):**
- Research medical content
- Plan download strategy
- Update documentation

**Questions for next session:**
- Should I download on Pi or PC?
- How long for 90GB download?
- Can Kiwix serve while downloading?

---

[← Back to Journal](../JOURNAL.md) | [← Previous: Day 0](day-0.md) | [Next: Day 2 →](day-2.md)

*Entry completed at 15:30, December 26, 2025*
