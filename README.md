# Prometheus Station
### 🔥 Bringing Fire to Humanity, One Station at a Time

---

## The Idea

Imagine you're in a disaster zone. Infrastructure has collapsed. A medical emergency happens. Someone needs critical information to save a life.

**What if you could still access emergency medical protocols? What if you could communicate over kilometers without any infrastructure?**

That's Prometheus Station: a solar-powered knowledge hub combining **offline medical encyclopedias** with **long-range radio communication**. No internet required. No monthly fees. No infrastructure dependency.

This project documents building such a station from scratch—written by someone who knew nothing about Raspberry Pi, LoRa networks, or solar power systems before starting. **If I can build this, you can too.**

---

## What This Actually Is

**Prometheus Station** is three things combined:

1. **🏥 An offline medical & knowledge library** - Emergency medical protocols, Wikipedia, and survival guides accessible via WiFi
2. **📡 A long-range messenger** - LoRa mesh network for text communication over several kilometers 
3. **☀️ A self-sufficient system** - Solar-powered, runs indefinitely without external power

**Practical translation:**
- You deploy a backpack-sized device to a disaster zone or remote location
- It creates a local WiFi hotspot serving **medical emergency protocols** and knowledge
- People connect with their phones/laptops like any wifi network—no internet needed
- It enables text messaging between devices over long distances (1-15km+)
- Everything runs on solar power—no external electricity required

**Real-world uses:**
- 🚑 **Emergency/disaster response** - Medical protocols when infrastructure fails
- 🏥 **Remote medical clinics** - Access to medical knowledge offline
- 🌍 **Humanitarian missions** - Field deployment by MSF, ICRC, Red Cross
- 🏔️ **Off-grid communities** - Education and communication
- 🔬 **Field research expeditions** - Knowledge base in remote areas
- 🌐 **Areas with censored internet** - Uncensored information access
- 🛡️ **Just-in-case resilience** - Community preparedness

---

## Why This Repository Exists

Most tech projects are documented by experts, for experts. They skip the "obvious" parts—obvious to them, confusing to beginners.

**This is different.**

I'm documenting this build as a complete beginner. Every problem I hit, every confusion, every wrong turn—it's all in here. The goal: someone else should be able to replicate this without experiencing the same trial and error.

Think of it as "beginner to beginner" documentation. If you've never touched a Raspberry Pi, never heard of LoRa, and think "ZIM files" sound like a snack—you're in the right place.

---

## 🎯 What This Does

### Medical & Emergency Content:
- **🏥 Post-Disaster Medical Protocols** - WHO/MSF field guides (615 MB)
- **🚑 Emergency Medicine Wiki** - ER protocols, trauma care (42 MB)
- **📚 Complete Medical Encyclopedia** - Comprehensive reference (2.1 GB)
- **💧 Water Purification Guides** - Critical for disaster response (20 MB)
- **🍲 Food Safety Protocols** - Field nutrition and safety (93 MB)
- **📖 Wikipedia Medicine** - Filtered medical articles EN + FR (3 GB)

### General Knowledge (Optional):
- **📚 Full Wikipedia** (EN + FR) - Complete offline encyclopedia (115 GB)
- **🔬 Educational Content** - Technical and scientific knowledge

### Communication & Infrastructure:
- **📡 Long-range LoRa mesh** - Text communication via [Meshtastic](https://meshtastic.org)
- **☀️ Solar-powered** - Autonomous operation for days/weeks
- **🌐 No internet required** - Works anywhere, anytime
- **🔧 Open-source** - Build, improve, share freely

**Use cases:**
- Natural disasters (earthquakes, hurricanes, floods)
- Conflict zones with destroyed infrastructure
- Remote medical clinics without connectivity
- Humanitarian missions in underserved areas
- Educational outreach in isolated communities
- Emergency preparedness and resilience
- Learning how decentralized systems work

---

## 🛠️ Hardware Stack

**Core:**
- Raspberry Pi 4 (8GB RAM)
- SanDisk Extreme 256GB microSD (A2)
- LILYGO T-Beam LORA32 868MHz (ESP32 + GPS + LoRa)
- Omnidirectional 868MHz antenna

**Power:**
- Anker Solix PS30 30W foldable solar panel
- Anker PowerCore 737 24000mAh battery
- Samsung 18650 rechargeable batteries (3450mAh)
- Xtar MC2 charger

**Infrastructure:**
- Spiderbeam 7m telescopic fiberglass mast
- 2.13" E-Ink display (low power status display)
- T-Echo Meshtastic mobile terminals (868MHz)

Full parts list with links: [HARDWARE.md](HARDWARE.md)

**Estimated total cost:** ~400-500€ (depends on deals/shipping)

---

## 📦 Content Strategies

Prometheus Station offers **three deployment strategies** based on your mission:

### 🏥 Strategy 1: Emergency Medical Pack (RECOMMENDED)
**Size:** ~5.5 GB | **Download:** 1-3 hours  
**Best for:** Disaster response, humanitarian missions, field deployment

**What you get:**
- Post-disaster medical protocols (MSF/WHO/ICRC standards)
- Emergency medicine procedures
- Complete medical encyclopedia
- Water purification and food safety guides
- Wikipedia medicine subset (EN + FR)

### 📚 Strategy 2: Full Knowledge Base
**Size:** ~120-150 GB | **Download:** 8-24 hours  
**Best for:** Permanent installations, educational centers, remote communities

**What you get:**
- Complete Wikipedia (English + French)
- All medical content from Strategy 1
- Comprehensive educational resources

### 🎒 Strategy 3: Minimal Emergency Kit
**Size:** ~750 MB | **Download:** 15-45 minutes  
**Best for:** Rapid deployment, testing, limited storage

**What you get:**
- Core disaster medicine protocols
- Emergency procedures
- Water safety guide
- Essential medical reference

See [02-kiwix-installation.md](docs/02-kiwix-installation.md) for detailed download instructions.

---

## 🚀 Quick Start

**⚠️ Work in Progress ⚠️**

This project is being built in real-time. Documentation will grow as I figure things out.

Current roadmap:
1. ✅ Hardware acquired
2. ✅ Raspberry Pi OS setup **[COMPLETE]**
3. ⏳ Kiwix installation + Medical content **[IN PROGRESS]**
4. ⏳ Meshtastic configuration
5. ⏳ Integration & testing
6. ⏳ Solar power optimization

Check [JOURNAL.md](JOURNAL.md) for real-time progress updates.

---

## 📖 Documentation

### Setup Guides:
- **[01 - Raspberry Pi Setup](docs/01-raspberry-setup.md)** - Headless Pi configuration ✅
- **[02 - Kiwix Installation](docs/02-kiwix-installation.md)** - Medical content deployment ⏳
- **[03 - Meshtastic Setup](docs/03-meshtastic-setup.md)** - LoRa mesh networking
- **[04 - System Integration](docs/04-integration.md)** - Bringing it all together
- **[05 - Solar Power](docs/05-solar-power.md)** - Autonomous operation

### Reference:
- **[Hardware List](HARDWARE.md)** - Complete bill of materials
- **[Journal](JOURNAL.md)** - My learning journey, mistakes included
- **[Contributing](CONTRIBUTING.md)** - How to help improve this

---

## 🧠 The Philosophy

> Prometheus stole fire from the gods and gave it to humanity.
> 
> We're stealing knowledge from the cloud and giving it to anyone, anywhere, even when the world is on fire.

This project is:
- **Beginner-friendly** - documented by a beginner, for beginners
- **Resilient** - works when nothing else does
- **Mission-focused** - designed for humanitarian and emergency response
- **Open** - free as in freedom, free as in beer
- **Practical** - real hardware, real tests, real problems solved
- **Ethical** - medical knowledge should be accessible to all

---

## 🏥 Medical Content Notice

**Important:**
- Medical content is for **reference and educational purposes only**
- Not a replacement for professional medical care
- In emergencies, seek qualified medical personnel when available
- Content follows WHO, MSF, and ICRC field guidelines
- Always verify critical information from multiple sources

**Recommended for:**
- Field medics and first responders
- Humanitarian workers in remote areas
- Emergency preparedness planning
- Medical education in underserved communities

**NOT recommended for:**
- Self-diagnosis or self-treatment
- Replacing professional medical consultation

---

## 🤝 Contributing

Found a better way to do something? Spotted an error? Have field experience to share?

**Open an issue or pull request!** This is a learning project, and shared knowledge makes it better.

Particularly helpful:
- Field deployment experiences and lessons learned
- Medical content recommendations
- Hardware alternatives/improvements
- Software optimization tips
- Power consumption reduction strategies
- Better antenna configurations for disaster zones
- Documentation improvements
- Translations (especially for disaster-prone regions)
- Testing in real-world scenarios

---

## 📜 License

MIT License - see [LICENSE](LICENSE)

Copyright © 2025 Guillain d'Erceville

**TL;DR:** Do whatever you want with this. Build it, deploy it in disaster zones, improve it, adapt it to your needs. Just don't blame me if your station achieves sentience. 🤖

**Special permission:** Humanitarian organizations (MSF, ICRC, Red Cross, etc.) are explicitly encouraged to use, modify, and deploy this system without attribution requirements. Save lives first, credit later.

---

## 🙏 Acknowledgments

Standing on the shoulders of giants:
- [Kiwix](https://www.kiwix.org) - Offline knowledge heroes
- [Meshtastic](https://meshtastic.org) - Long-range mesh wizards
- [Raspberry Pi Foundation](https://www.raspberrypi.org) - Making computing accessible
- **WHO, MSF, ICRC** - Medical protocols that save lives
- The entire open-source community
- Emergency responders and humanitarian workers worldwide

---

## 📞 Contact

- **GitHub:** [@GuillainM](https://github.com/GuillainM)
- **Issues:** [Report problems or ask questions](https://github.com/GuillainM/Prometheus-Station/issues)

---

## 🌍 Real-World Impact

**This system is designed for situations like:**
- 2010 Haiti earthquake - infrastructure destroyed, no communications
- 2013 Typhoon Haiyan - medical facilities overwhelmed
- Syrian conflict zones - limited access to medical information
- Remote Amazon clinics - no internet connectivity
- Refugee camps - limited educational resources

**If you deploy this system in the field, please share your experience!** Your feedback helps improve future deployments.

---

<div align="center">

### ⚡ If you build this, share your experience! ⚡

**Star this repo if you think medical knowledge should be accessible to everyone, everywhere.**

Made with 🔥 and ☕ somewhere between "I have no idea what I'm doing" and "This might actually save lives."

**Deploy. Share. Save lives.**

</div>
