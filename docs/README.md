# 📖 Installation Guide Overview

**Welcome to the build phase!** 

If you're reading this, you've probably already gone through [HARDWARE.md](../HARDWARE.md) and have your components ready. Now comes the fun part: putting it all together.

This document is your **roadmap**. Think of it as the table of contents for building Prometheus Station. By the end of this overview, you'll understand:
- What you're going to build (and in what order)
- How long each step takes
- What skills you'll learn along the way
- Where to get help when stuck

**Important philosophy:** This isn't a race. Take your time. Understand each step before moving to the next. If something breaks, that's learning—not failure.

---

## 🎯 What You're About to Build

Let's be crystal clear about the end goal. When you're done, you'll have:

### A Physical System That:
1. **Sits in a backpack** (or deploys on a mast for permanent installation)
2. **Runs on solar power** (no wall outlet needed)
3. **Creates a WiFi hotspot** that anyone can connect to
4. **Serves Wikipedia offline** (90GB+ of knowledge, no internet required)
5. **Enables long-range messaging** (1-15km using LoRa radio)

### The User Experience:
- Someone walks into range (50-300m for WiFi)
- They see "Prometheus-Station" in their WiFi list
- They connect (no password needed—it's a public resource)
- Their browser opens to a landing page
- They can search Wikipedia, read medical guides, send LoRa messages
- Everything works with **zero** internet connection

**That's what we're building.** Now let's see how.

---

## 🗺️ The Build Path: 6 Steps

Here's the journey from "pile of components" to "working knowledge station":

```
┌─────────────────────────────────────────────────────────────┐
│  STEP 1: Raspberry Pi Setup                                 │
│  ├─ Install operating system                                │
│  ├─ Configure headless access (SSH)                         │
│  └─ System optimization                                     │
│                                                              │
│                          ↓                                   │
│  STEP 2: Kiwix Installation                                 │
│  ├─ Install Kiwix server software                           │
│  ├─ Download Wikipedia ZIM files (~171GB)                   │
│  └─ Set up web service                                      │
│                                                              │
│                          ↓                                   │
│  STEP 3: Meshtastic Setup                                   │
│  ├─ Flash LoRa devices with Meshtastic                      │
│  ├─ Configure mesh network (868MHz)                         │
│  └─ Test communication                                      │
│                                                              │
│                          ↓                                   │
│  STEP 4: System Integration                                 │
│  ├─ Create WiFi access point                                │
│  ├─ Build custom landing page                               │
│  └─ Connect all services together                           │
│                                                              │
│                          ↓                                   │
│  STEP 5: Solar Power Setup                                  │
│  ├─ Wire power system                                       │
│  ├─ Configure battery monitoring                            │
│  └─ Optimize for low power consumption                      │
│                                                              │
│                          ↓                                   │
│  STEP 6: Field Deployment                                   │
│  ├─ Physical installation                                   │
│  ├─ Range testing                                           │
│  └─ User onboarding materials                               │
└─────────────────────────────────────────────────────────────┘
```

**Each step builds on the previous one.** You can't skip ahead (trust me, I tried).

---

## ⏱️ Time & Difficulty Breakdown

Here's what to expect for each phase:

| Step | Guide | Time Estimate | Difficulty | Skills You'll Learn |
|------|-------|---------------|------------|---------------------|
| **1** | [Raspberry Pi Setup](01-raspberry-setup.md) | 1-2 hours | ⭐⭐☆☆☆ Easy | Linux basics, SSH, system administration |
| **2** | [Kiwix Installation](02-kiwix-installation.md) | 3-4 hours* | ⭐⭐⭐☆☆ Medium | Web servers, file management, systemd services |
| **3** | [Meshtastic Setup](03-meshtastic-setup.md) | 1-2 hours | ⭐⭐☆☆☆ Easy | Firmware flashing, radio configuration |
| **4** | [System Integration](04-integration.md) | 2-3 hours | ⭐⭐⭐⭐☆ Hard | Networking, DNS, web development |
| **5** | [Solar Power](05-solar-power.md) | 1 hour | ⭐⭐☆☆☆ Easy | Electrical systems, power monitoring |
| **6** | [Deployment](06-deployment.md) | 1-2 hours | ⭐⭐⭐☆☆ Medium | Field operations, testing, troubleshooting |

**Total first build:** 9-14 hours (spread over several days)

*\*Most of Step 2's time is downloading Wikipedia files (can run overnight)*

### Important Notes:
- **First time:** Plan for the upper end of estimates (things take longer when learning)
- **Second build:** You'll cut time in half (seriously—I did this twice)
- **Don't rush Step 4:** Integration is where most problems happen
- **Take breaks:** Your brain absorbs better when not exhausted

---

## 🧠 Technical Concepts Explained

Before diving in, let's demystify the jargon you'll encounter. **No assumed knowledge here.**

---

### 🖥️ What is "Headless" Setup?

**Simple definition:** Running a computer without a monitor, keyboard, or mouse.

**Why we do this:**
- The Raspberry Pi will be in a backpack or on a pole
- No room (or need) for a screen
- We control it remotely over WiFi/network

**How it works:**
- You access the Pi through **SSH** (explained below)
- Type commands in a terminal on your laptop
- The Pi executes them and sends back results

**Analogy:** It's like texting instructions to someone instead of talking face-to-face.

---

### 🔐 What is SSH?

**SSH = Secure Shell**

**Simple definition:** A way to control one computer from another computer using text commands.

**Example:**
```
Your laptop                      Raspberry Pi
    │                                 │
    │  "sudo apt update"              │
    ├────────────────────────────────>│
    │                                 │ [executes command]
    │  "Done, 47 packages updated"    │
    │<────────────────────────────────┤
```

**Why "secure":** The connection is encrypted. Nobody can spy on your commands.

**In practice:**
- You open a terminal on your laptop
- You type: `ssh pi@192.168.1.100`
- You're now controlling the Raspberry Pi remotely
- Everything you type runs on the Pi, not your laptop

**Common confusion:** 
- SSH is NOT installing software
- SSH is NOT a programming language
- SSH is just a remote control mechanism

---

### 📦 What are ZIM Files?

**ZIM = Wikipedia's offline file format**

**Simple definition:** A single compressed file containing an entire website.

**Example:**
- Wikipedia has ~6 million English articles
- Normally, that's millions of separate web pages
- A ZIM file squashes them all into ONE file
- That file can be searched and browsed offline

**Size context:**
- Wikipedia English: ~90GB (compressed!)
- If uncompressed: ~300-400GB
- The compression is extremely clever (deduplication, indexing)

**Why ZIM specifically:**
- Designed for offline use
- Includes search functionality
- Works on low-power devices (like Raspberry Pi)
- Open format (no DRM, no vendor lock-in)

**Other ZIM files available:**
- Wikipedia in 300+ languages
- Stack Overflow
- Khan Academy
- Project Gutenberg (books)
- Medical encyclopedias

**Download tip:** ZIM files are HUGE. Use a stable internet connection. If download interrupts, you start over (unless using special tools).

---

### 📡 What is LoRa?

**LoRa = Long Range (radio technology)**

**Simple definition:** A way to send small messages over very long distances using low power.

**Comparison table:**

| Technology | Range | Power Use | Speed | Infrastructure |
|------------|-------|-----------|-------|----------------|
| **WiFi** | 50-300m | Medium | Fast (Mbps) | None needed |
| **Bluetooth** | 10-100m | Low | Medium (Mbps) | None needed |
| **Cell/4G** | km | High | Very fast | Needs towers |
| **LoRa** | 1-15km+ | Very low | Slow (Kbps) | None needed |

**The tradeoff:**
- LoRa goes FAR but is SLOW
- Perfect for text messages ("Help needed at coordinates X,Y")
- Terrible for photos, videos, downloads

**Why this matters for Prometheus:**
- Emergency communication when cell towers are down
- Works in remote areas
- Batteries last weeks (not hours)
- Messages "hop" through other LoRa devices (mesh network)

**Real-world example:**
- You're 10km from the station
- Your direct LoRa message can't reach it
- Another LoRa device is 5km away (midpoint)
- Your message hops through that device to reach the station
- This is called "mesh networking"

---

### 🌐 What is a "Systemd Service"?

**Simple definition:** A way to make programs start automatically when the Raspberry Pi boots.

**Without systemd:**
- You turn on the Pi
- You manually SSH in
- You manually type: `kiwix-serve wikipedia.zim`
- If you disconnect, the program stops
- If Pi reboots, you must manually restart everything

**With systemd:**
- You turn on the Pi
- Kiwix starts automatically
- If it crashes, systemd restarts it
- Runs in the background forever
- You never think about it again

**Analogy:** Systemd is like setting your coffee maker to auto-brew at 6am. You don't manually push the button every morning.

**In practice (Step 2):**
- We'll create a file describing how to run Kiwix
- We'll tell systemd "always run this"
- systemd handles the rest

---

### 🔌 What is a WiFi Access Point?

**Simple definition:** Turning your Raspberry Pi into a WiFi router.

**Normal WiFi use:**
```
Your phone ──> Your router ──> Internet
```

**Access Point mode:**
```
Your phone ──> Raspberry Pi ──> Kiwix (offline Wikipedia)
                  │
                  └──> (no internet, that's the point!)
```

**Why we need this:**
- The Pi serves Wikipedia over WiFi
- People connect to "Prometheus-Station" WiFi
- Their phones/laptops can browse Wikipedia
- No internet required anywhere in the chain

**Technical difference:**
- **Client mode:** Pi connects to existing WiFi (like your phone does)
- **Access Point mode:** Pi creates NEW WiFi that others connect to

**Common confusion:**
- Access Point ≠ Internet sharing
- We're NOT providing internet
- We're providing LOCAL services (Wikipedia) over WiFi

---

### ⚡ What is "Power Budget"?

**Simple definition:** Calculating how much electricity you use vs. how much you generate/store.

**The math:**
```
Power IN:   Solar panel generates ~15-25W average (daytime only)
Power OUT:  Raspberry Pi uses ~5W constantly (day + night)
Storage:    Battery holds ~89Wh (watt-hours)
```

**Example calculation:**
- System uses 5W constantly
- Battery has 89Wh
- Runtime = 89Wh ÷ 5W = **17.8 hours** without sun

**The balancing act:**
- Sunny day: Generate 150Wh, use 120Wh → Battery gains 30Wh ✅
- Cloudy day: Generate 50Wh, use 120Wh → Battery loses 70Wh ⚠️
- Night: Generate 0Wh, use 60Wh → Battery loses 60Wh ⚠️

**Goal:** Make sure power IN ≥ power OUT over a week

**Step 5 teaches you:**
- How to measure actual consumption
- How to reduce power usage (disable unused features)
- When to worry about battery level

---

### 🔧 What Does "Flashing Firmware" Mean?

**Simple definition:** Installing the operating system on a device.

**Analogy:** Like installing Windows on a laptop, but for tiny electronics.

**For Meshtastic (Step 3):**
- Your T-Beam arrives with generic firmware
- We "flash" it with Meshtastic-specific firmware
- Now it speaks the Meshtastic protocol
- It can mesh with other Meshtastic devices

**Why "flash":**
- The process writes to "flash memory" (permanent storage)
- Like burning a CD (old term, same idea)

**Can you brick the device?**
- Unlikely with our method (web-based flasher)
- Even if you mess up, devices are usually recoverable
- Worst case: try again

---

## 📋 Prerequisites

Before starting Step 1, make sure you have:

### Hardware (from HARDWARE.md):
- ✅ Raspberry Pi 4 (8GB) with power supply
- ✅ MicroSD card (256GB A2 class)
- ✅ T-Beam LoRa device (868MHz)
- ✅ Solar panel + battery
- ✅ All cables and accessories

### Software Tools (free downloads):
- ✅ **Raspberry Pi Imager** - [Download here](https://www.raspberrypi.com/software/)
  - What: Official tool to install OS on SD card
  - Platforms: Windows, macOS, Linux
  
- ✅ **SSH Client** - Probably already installed
  - Windows 10+: Built into Command Prompt/PowerShell
  - macOS/Linux: Built into Terminal
  - Alternative: [PuTTY](https://www.putty.org/) (Windows)

- ✅ **Web Browser** - Any modern browser
  - For accessing Kiwix and Meshtastic web interface
  - Chrome, Firefox, Safari, Edge all work

### Knowledge Requirements:
- ✅ **Can you copy-paste commands?** → You're ready
- ✅ **Comfortable with basic file management?** → Perfect
- ❌ **Need to be a programmer?** → Absolutely not
- ❌ **Need Linux experience?** → Nope, we'll teach you

### Physical Setup:
- ✅ **Workspace:** Table with power outlet
- ✅ **Internet connection:** For downloading files (use your home WiFi)
- ✅ **SD card reader:** For writing to microSD
  - Most laptops have one built-in
  - USB adapters cost ~5€ if needed

---

## 🚀 Quick Start Options

Depending on your experience level, choose your path:

### 🟢 Path 1: "I've Never Done This Before"
**Recommended approach:**
1. Read this entire overview document first
2. Watch a Raspberry Pi setup video on YouTube (search "Raspberry Pi headless setup")
3. Start with [Step 1](01-raspberry-setup.md)
4. Take 2-3 days, one step per day
5. Ask questions in GitHub Issues when stuck

**Why this works:**
- No pressure to rush
- Time to absorb concepts
- Troubleshooting is easier when not tired

---

### 🟡 Path 2: "I've Used Raspberry Pi Before"
**Faster approach:**
1. Skim this overview
2. Jump straight to [Step 2: Kiwix Installation](02-kiwix-installation.md)
3. Reference Step 1 only if you hit issues
4. Should finish in 1-2 days

**Skip if you know:**
- How to SSH into a Pi
- Basic Linux command line
- How to edit config files with nano/vim

---

### 🔴 Path 3: "I Just Want It Working NOW"
**Speed-run approach:**
1. Download pre-configured image (when available—coming soon!)
2. Flash to SD card
3. Skip to [Step 5: Solar Power](05-solar-power.md)
4. Done in ~2 hours

**Trade-offs:**
- You won't understand HOW it works
- Harder to troubleshoot problems
- Less customizable
- But... it works!

*Note: Pre-built images aren't available yet. This is a future feature.*

---

## 🆘 When Things Go Wrong

**They will.** That's not a bug—it's a feature. Here's how to handle it:

### The Troubleshooting Mindset

1. **Don't panic** - Every error is Google-able
2. **Read the error message** - It usually tells you what's wrong
3. **Check the Troubleshooting section** - Each guide has one
4. **Search GitHub Issues** - Someone probably hit this already
5. **Ask for help** - Open a new issue with details

### What to Include in a Help Request

When asking for help, always provide:

```
**What I'm trying to do:**
[e.g., "Installing Kiwix on Raspberry Pi"]

**What I did:**
[Copy-paste the exact commands you ran]

**What happened:**
[Copy-paste the error message]

**What I expected:**
[e.g., "Kiwix should start automatically"]

**My setup:**
- Raspberry Pi model: [e.g., Pi 4 8GB]
- OS version: [run: cat /etc/os-release]
- Guide step: [e.g., "Step 2, section 2.3"]
```

**The more details, the faster we can help.**

---

## 📊 Documentation Status

Here's what's currently available:

| Guide | Status | Last Updated | Tested |
|-------|--------|--------------|--------|
| **01 - Raspberry Pi Setup** | ✅ Complete | Dec 2024 | ✅ Yes |
| **02 - Kiwix Installation** | ✅ Complete | Dec 2024 | ✅ Yes |
| **03 - Meshtastic Setup** | ✅ Complete | Dec 2024 | ✅ Yes |
| **04 - System Integration** | ✅ Complete | Dec 2024 | ⏳ Partial |
| **05 - Solar Power** | ✅ Complete | Dec 2024 | ⏳ Partial |
| **06 - Deployment** | ✅ Complete | Dec 2024 | ❌ Not yet |

**Legend:**
- ✅ Complete: Fully written and verified
- ⏳ Partial: Written but needs more field testing
- ❌ Not yet: Theory only, no real-world validation

**Feedback welcome!** If something doesn't work as described, please open an issue.

---

## 💡 Learning Philosophy

This project is designed to teach, not just instruct. Here's the approach:

### We Explain WHY, Not Just HOW

**Bad documentation:**
```
Run: sudo apt install kiwix-tools
```

**Our documentation:**
```
Run: sudo apt install kiwix-tools

What this does: Downloads and installs Kiwix server software
Why sudo: Needs admin privileges to install system-wide
What if it fails: Check your internet connection and try again
```

### We Show You What Success Looks Like

Every major step includes:
- ✅ Expected output (so you know it worked)
- ❌ Common errors (so you recognize problems)
- 🔍 How to verify (test that it's actually working)

### We Admit What We Don't Know

If something is theory (not field-tested), we say so. If there are multiple ways to do something, we explain the trade-offs. If we're not sure, we admit it.

**Honesty > false confidence**

---

## 🎯 Success Criteria

How do you know when you're "done"? Here's the checklist:

### After Step 1 (Raspberry Pi):
- [ ] Can SSH into the Pi from your laptop
- [ ] Can run basic Linux commands
- [ ] System is updated and secured

### After Step 2 (Kiwix):
- [ ] Wikipedia search works in browser
- [ ] Kiwix starts automatically on boot
- [ ] Can access from other devices on network

### After Step 3 (Meshtastic):
- [ ] T-Beam shows up in Meshtastic app
- [ ] Can send/receive messages
- [ ] GPS gets a fix (if outdoors)

### After Step 4 (Integration):
- [ ] Raspberry Pi creates WiFi hotspot
- [ ] Phones can connect to it
- [ ] Custom landing page loads
- [ ] All services accessible from one place

### After Step 5 (Solar):
- [ ] System runs on battery power
- [ ] Solar panel charges battery
- [ ] Power monitoring script works
- [ ] Can estimate runtime

### After Step 6 (Deployment):
- [ ] System works in the field
- [ ] Range meets expectations (WiFi + LoRa)
- [ ] Users can connect without help
- [ ] System recovers from power cycles

**When all checkboxes are ticked:** 🎉 **You've built Prometheus Station!**

---

## 🗺️ Where to Go From Here

Ready to start building? Here's your next step:

### For First-Time Builders:
👉 **Go to [01 - Raspberry Pi Setup](01-raspberry-setup.md)**

This guide walks you through:
- Installing the operating system
- Connecting via SSH
- Basic system configuration
- Security hardening

**Estimated time:** 1-2 hours  
**Difficulty:** ⭐⭐☆☆☆ Easy

---

### For Experienced Builders:
👉 **Jump to [02 - Kiwix Installation](02-kiwix-installation.md)**

Assumes you already have:
- Raspberry Pi OS installed
- SSH access configured
- Basic Linux comfort

---

### Just Browsing?
👉 **Check out [JOURNAL.md](../JOURNAL.md)**

See the actual build log from the first Prometheus Station. All the mistakes, discoveries, and "aha!" moments documented in real-time.

---

## 📬 Questions? Stuck? Want to Contribute?

- **Problems during build?** → [Open an Issue](https://github.com/GuillainM/Prometheus-Station/issues)
- **General questions?** → [Start a Discussion](https://github.com/GuillainM/Prometheus-Station/discussions)
- **Found a typo/error?** → Submit a Pull Request
- **Built your own station?** → Share photos in Discussions!

**Remember:** There are no stupid questions. If you're confused, others probably are too. Asking helps everyone.

---

## 🔥 Final Thoughts

Building Prometheus Station isn't just about creating a device. It's about:
- **Learning** how technology actually works (not just using it)
- **Self-reliance** in an increasingly fragile world
- **Sharing knowledge** that empowers communities
- **Understanding** that complex systems are just simple steps combined

**You don't need to be an expert. You just need to start.**

The hardest part? Believing you can do it.  
The truth? **You absolutely can.**

Let's build something amazing. 🚀

---

**Next:** [Step 1 - Raspberry Pi Setup](01-raspberry-setup.md) →

---

*Last updated: December 2024*  
*Written by: Guillain d'Erceville*  
*Status: Living document (feedback welcome!)*
