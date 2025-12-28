# Prometheus Station
### 🔥 A Lighthouse When Everything Burns

---

## The Vision

When civilization's infrastructure collapses—whether by earthquake, war, censorship, or chaos—knowledge becomes the most precious resource.

**Prometheus Station is a beacon in the darkness.**

A solar-powered, self-sufficient knowledge repository that works when the internet doesn't. When cell towers are rubble. When libraries are ash. When asking Google isn't an option.

This is the Library of Alexandria for the apocalypse. A lifeboat filled with humanity's accumulated wisdom, ready to deploy anywhere, serving anyone within reach.

**No internet. No monthly fees. No dependency on infrastructure that can fail.**

Just knowledge, communication, and light in the darkness.

---

## What This Actually Is

Three critical systems in one portable, resilient package:

### 📚 An Offline Knowledge Repository
- Complete Wikipedia (90GB+ in English alone)
- Emergency medical protocols (WHO, MSF, ICRC field guides)
- Survival knowledge (water purification, food safety, emergency procedures)
- Educational content in multiple languages
- Access via WiFi hotspot - connect like any network, no internet needed

### 📡 Long-Range Mesh Communication
- LoRa radio network for text messaging
- Range: 1-15km+ depending on terrain
- Works when cell towers don't
- Messages hop through other stations (mesh networking)
- No carrier. No bills. No permission needed.

### ☀️ Energy Independence
- Solar-powered with battery backup
- Runs indefinitely without grid power
- Portable or fixed installation
- Operates in disaster zones, remote areas, anywhere with sun

**In practice:** You deploy a backpack-sized station. It creates a WiFi bubble containing all human knowledge. People connect with phones, tablets, laptops. No internet required. Knowledge flows. Lives are saved.

---

## Why This Exists

### The Problem

Knowledge is centralized. Wikipedia requires internet. Medical references are online. When infrastructure fails, we go blind.

**We've built a civilization dependent on fragile systems.**

### The Solution

Decentralize critical knowledge. Make it resilient. Make it accessible. Make it work when everything else fails.

**Prometheus gave humanity fire. We're giving humanity knowledge that can't be extinguished.**

### Who This Serves

- 🚑 **Disaster zones** - Earthquake, hurricane, flood response teams
- 🏥 **Remote clinics** - Medical workers in underserved areas
- 🌍 **Humanitarian missions** - MSF, ICRC, Red Cross field operations
- 📚 **Censored regions** - Access to uncensored information
- 🏔️ **Off-grid communities** - Education without infrastructure
- 🔬 **Field research** - Knowledge base in remote locations
- 🛡️ **Resilience planners** - Community preparedness
- 🎓 **Educators** - Teaching in low-connectivity areas

**Real-world examples this system was designed for:**
- 2010 Haiti earthquake - infrastructure destroyed, medical knowledge inaccessible
- 2013 Typhoon Haiyan - hospitals offline, protocols needed
- Syrian conflict zones - censored internet, limited medical access
- Remote Amazon clinics - zero connectivity, life-or-death decisions daily
- Refugee camps - educational resources non-existent

---

## 🎯 What's Inside

### Knowledge Content (Choose Your Strategy)

**Strategy 1: Emergency Response Pack (~5.5 GB)**
- Post-disaster medical protocols (MSF/WHO/ICRC)
- Emergency medicine encyclopedia
- ER procedures and toxicology
- Water purification guides
- Food safety protocols
- Wikipedia medicine subset (EN + FR)
- **Best for:** Field deployment, rapid response, humanitarian missions

**Strategy 2: Full Knowledge Base (~120-150 GB)**
- Complete Wikipedia (English + French)
- All medical content from Strategy 1
- Comprehensive educational resources
- **Best for:** Permanent installations, schools, community centers

**Strategy 3: Minimal Kit (~750 MB)**
- Core disaster medicine protocols
- Emergency procedures only
- Water safety essentials
- **Best for:** Ultra-portable, proof-of-concept, testing

See [Content Strategy Guide](docs/02-kiwix-installation.md) for details.

### Hardware Components

**Computing:**
- Raspberry Pi 4 (8GB RAM) - The brain
- 256GB microSD A2 class - Fast storage for large databases
- E-Ink display - Low-power status monitoring

**Communication:**
- LILYGO T-Beam LORA32 868MHz - Long-range radio gateway
- T-Echo handheld terminals - Mobile mesh nodes
- Omnidirectional antenna - 360° coverage

**Power:**
- 30W foldable solar panel - Energy harvesting
- 24,000mAh battery bank - Multi-day autonomy
- 18650 batteries for portables - Extended operation

**Infrastructure:**
- 7m telescopic mast - Extended range deployment
- Weatherproof cabling - Field durability

**Total cost:** ~400-500€ (components list: [HARDWARE.md](HARDWARE.md))

---

## 🚀 Build Your Own

This repository contains **complete, tested, beginner-friendly documentation** for building Prometheus Station from scratch.

**Documentation philosophy:**
- Written by a beginner, for beginners
- Every step explained, no assumed knowledge
- Real-world tested on actual hardware
- Troubleshooting based on actual problems encountered
- No marketing fluff - just what works

### Setup Guides (Complete & Tested)

**✅ [Step 1: Raspberry Pi Setup](docs/01-raspberry-setup.md)**
- Headless configuration (no monitor needed)
- SSH access with key authentication
- System optimization for 24/7 operation
- **Time:** 1h 45min | **Difficulty:** ⭐⭐☆☆☆ Easy

**✅ [Step 2: Kiwix Installation](docs/02-kiwix-installation.md)**
- Content strategy selection
- ZIM file downloads (Wikipedia, medical content)
- Server configuration and optimization
- **Time:** 2-4 hours (mostly downloads) | **Difficulty:** ⭐⭐☆☆☆ Medium

**⏳ [Step 3: Meshtastic Setup](docs/03-meshtastic-setup.md)**
- LoRa radio configuration
- Mesh network deployment
- Mobile terminal setup
- **Status:** Coming soon

**⏳ [Step 4: System Integration](docs/04-integration.md)**
- WiFi access point creation
- Service orchestration
- User interface
- **Status:** In development

**⏳ [Step 5: Solar Power](docs/05-solar-power.md)**
- Power system wiring
- Energy monitoring
- Autonomy optimization
- **Status:** Planned

### Quick Start

1. **Get hardware** - See [HARDWARE.md](HARDWARE.md) for complete list (~500€)
2. **Follow guides** - Start with [Step 1](docs/01-raspberry-setup.md)
3. **Choose content** - Select strategy based on your mission
4. **Deploy** - Field test, iterate, improve

**Estimated build time:**
- First build: ~8-12 hours (spread over weekend)
- Hardware assembly: ~2 hours
- Software setup: ~4 hours
- Content download: 2-6 hours (depends on strategy)

---

## 🧠 The Philosophy

### Why "Prometheus"?

> **Prometheus stole fire from the gods and gave it to humanity.**
>
> We're stealing knowledge from the cloud and giving it to everyone, everywhere—even when the world burns.

### Core Principles

**Resilience**
- Works when infrastructure fails
- No single point of failure
- Offline-first design
- Solar-powered autonomy

**Accessibility**
- No internet required
- No monthly fees
- No proprietary software
- No permission needed

**Open**
- Fully open-source
- Complete documentation
- Reproducible builds
- Community-driven improvement

**Ethical**
- Knowledge should be free
- Privacy by design (no tracking)
- Humanitarian focus
- Medical information for all

**Practical**
- Real hardware, real testing
- Field-deployable
- Beginner-friendly documentation
- Cost-effective (~500€)

---

## 🌍 Real-World Impact

**Designed for when everything fails:**

- Natural disasters (earthquakes, tsunamis, hurricanes)
- Conflict zones with destroyed infrastructure
- Censored internet regions
- Remote locations with no connectivity
- Grid failures and power outages
- Refugee camps and displacement crises
- Emergency preparedness and resilience

**If you deploy this in the field, we want to hear about it.** Your experience shapes future versions.

---

## 🛠️ Technical Overview

**System Architecture:**
```
┌─────────────────────────────────────────┐
│          PROMETHEUS STATION             │
│                                         │
│  ┌──────────┐        ┌──────────┐     │
│  │  Solar   │───────▶│ Battery  │     │
│  │  Panel   │        │  Bank    │     │
│  └──────────┘        └────┬─────┘     │
│                           │            │
│                           ▼            │
│              ┌─────────────────┐       │
│              │  Raspberry Pi   │       │
│              │  (The Brain)    │       │
│              │                 │       │
│              │ • Kiwix Server  │       │
│              │ • WiFi Hotspot  │       │
│              │ • Mesh Gateway  │       │
│              └────────┬────────┘       │
│                       │                │
│         ┏━━━━━━━━━━━━━┻━━━━━━━━━━━━┓   │
│         ▼                          ▼   │
│  ┌─────────────┐          ┌──────────┐│
│  │   WiFi      │          │   LoRa   ││
│  │   Radio     │          │   Radio  ││
│  │ (300m max)  │          │ (15km+)  ││
│  └─────────────┘          └──────────┘│
│         │                      │      │
└─────────┼──────────────────────┼──────┘
          │                      │
          ▼                      ▼
    [Phones/Laptops]      [Mesh Network]
    Access Wikipedia      Long-range comms
```

**Power Budget:**
- Solar input: 15-25W (daytime average)
- System draw: 4-6W (continuous)
- Battery capacity: 89Wh
- Runtime: 18+ hours without sun
- Autonomy: Indefinite with 4+ hours sunlight/day

**Network Capabilities:**
- WiFi: 50-300m range (local knowledge access)
- LoRa: 1-15km+ range (mesh communication)
- Concurrent users: 10-20 (WiFi), unlimited (LoRa mesh)
- Content size: 5.5GB to 150GB (strategy dependent)

---

## 📋 Project Status

**Completed:**
- ✅ Hardware selection and testing
- ✅ Raspberry Pi setup guide (tested, documented)
- ✅ Kiwix installation guide (tested, documented)
- ✅ Content strategy framework
- ✅ Power consumption analysis
- ✅ Beginner-friendly documentation

**In Progress:**
- ⏳ Meshtastic LoRa integration
- ⏳ WiFi access point configuration
- ⏳ Solar power system assembly
- ⏳ Field testing

**Planned:**
- 📋 Custom landing page UI
- 📋 E-Ink status display integration
- 📋 Multi-language support
- 📋 Remote management tools
- 📋 Deployment case design

**Timeline:** No deadlines. This is built right, not fast.

---

## 🤝 Contributing

**This project needs:**
- Field testing reports (critical!)
- Medical content recommendations
- Hardware alternatives for different budgets
- Translation of documentation
- Power optimization discoveries
- Antenna configuration improvements
- Real-world deployment feedback

**How to contribute:**
1. **Field experience** - Deploy and document your learnings
2. **Technical improvements** - Better configs, optimizations
3. **Documentation** - Fix errors, clarify confusing sections
4. **Content curation** - Recommend additional ZIM files
5. **Translations** - Help reach more people

Open an issue or pull request. All knowledge shared makes this better.

---

## 🏥 Medical Disclaimer

**Critical Notice:**

Medical content provided by Prometheus Station is for **reference and educational purposes only**.

- ✅ Use for field reference when professional care unavailable
- ✅ Training and education for medics and first responders
- ✅ Emergency preparedness planning
- ❌ NOT for self-diagnosis or self-treatment
- ❌ NOT a replacement for qualified medical professionals

**In emergencies:** Seek professional medical help when available. This system is a lifeline when nothing else exists, not a replacement for proper medical care.

Content sources: WHO, MSF, ICRC field guidelines. Verify critical information from multiple sources.

---

## 📜 License

**MIT License** - See [LICENSE](LICENSE)

Copyright © 2025 Guillain d'Erceville

**What this means:**
- ✅ Use freely for any purpose
- ✅ Modify and adapt to your needs
- ✅ Deploy in disaster zones without asking
- ✅ Build commercial products (though why?)
- ✅ Share and distribute
- ❌ Don't blame me if it achieves sentience

**Special Grant to Humanitarian Organizations:**

MSF, ICRC, Red Cross, and all humanitarian organizations: You have explicit permission to use, modify, and deploy this system **without attribution requirements**. Save lives first. Credit never.

---

## 🙏 Standing on Shoulders of Giants

**This exists because of:**

- **[Kiwix](https://www.kiwix.org)** - Making offline knowledge possible
- **[Meshtastic](https://meshtastic.org)** - Resilient mesh communication
- **[Raspberry Pi Foundation](https://www.raspberrypi.org)** - Accessible computing
- **Wikipedia contributors** - Humanity's knowledge, freely shared
- **WHO, MSF, ICRC** - Medical protocols that save lives
- **Open-source community** - Collective brilliance
- **Emergency responders worldwide** - Inspiration and purpose

---

## 📞 Contact & Community

- **GitHub:** [@GuillainM](https://github.com/GuillainM)
- **Issues:** [Report problems or suggest improvements](https://github.com/GuillainM/Prometheus-Station/issues)
- **Discussions:** [Share your deployment stories](https://github.com/GuillainM/Prometheus-Station/discussions)

**If you build this, share your experience.** Every deployment teaches us something.

---

<div align="center">

## 🔥 The Fire We Carry 🔥

In a world where knowledge is centralized, connectivity is fragile, and infrastructure can vanish overnight...

**We choose resilience.**

We build systems that work when nothing else does.
We preserve knowledge that cannot be extinguished.
We light beacons in the darkness.

**Prometheus Station is a lighthouse when everything burns.**

---

### If you believe knowledge should survive anything, star this repo.

**Built with fire and coffee by someone who had no idea what they were doing.**
**Documented for anyone who wants to learn.**

**Deploy. Share. Preserve. Endure.**

</div>

---

*Last updated: December 2025*
*Status: Tested, documented, ready to build*
*Hardware verified: Raspberry Pi 4, tested in real-world conditions*
