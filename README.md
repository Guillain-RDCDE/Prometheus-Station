# Prometheus Station
### 🔥 Bringing Fire to Humanity, One Station at a Time

---

## The Idea

Imagine you're in a place with no internet. Maybe you're deep in the mountains, on a remote island, or in an area where infrastructure has failed. A medical emergency happens. A technical problem needs solving. A student wants to learn.

**What if you could still access all of Wikipedia? What if you could communicate over kilometers without cell towers or wifi?**

That's Prometheus Station: a solar-powered knowledge hub combining offline Wikipedia with long-range radio communication. No internet required. No monthly fees. No infrastructure dependency.

This project documents building such a station from scratch—written by someone who knew nothing about Raspberry Pi, LoRa networks, or solar power systems before starting. **If I can build this, you can too.**

---

## What This Actually Is

**Prometheus Station** is three things combined:

1. **📚 An offline library** - Complete Wikipedia (English + French) and medical encyclopedias accessible via WiFi
2. **📡 A long-range messenger** - LoRa mesh network for text communication over several kilometers 
3. **☀️ A self-sufficient system** - Solar-powered, runs indefinitely without external power

**Practical translation:**
- You carry a backpack-sized device to a remote location
- It creates a local WiFi hotspot serving Wikipedia and medical knowledge
- People connect with their phones/laptops like any wifi network—no internet needed
- It also enables text messaging between devices over long distances (1-15km+)
- Everything runs on solar power

**Real-world uses:**
- Emergency/disaster response (power outage, natural disaster)
- Remote medical clinics (access to medical knowledge offline)
- Off-grid communities (education, communication)
- Field research expeditions
- Areas with censored/controlled internet
- Just-in-case resilience for your community

---

## Why This Repository Exists

Most tech projects are documented by experts, for experts. They skip the "obvious" parts—obvious to them, confusing to beginners.

**This is different.**

I'm documenting this build as a complete beginner. Every problem I hit, every confusion, every wrong turn—it's all in here. The goal: someone else should be able to replicate this without experiencing the same trial and error.

Think of it as "beginner to beginner" documentation. If you've never touched a Raspberry Pi, never heard of LoRa, and think "ZIM files" sound like a snack—you're in the right place.

---

## 🎯 What This Does

- **📚 Offline Wikipedia** (EN + FR) + Wikimed via [Kiwix](https://www.kiwix.org)
- **📡 Long-range LoRa mesh** communication via [Meshtastic](https://meshtastic.org)
- **☀️ Solar-powered** autonomous operation
- **🌍 No internet required** - works anywhere
- **🔧 Open-source** - build your own, improve it, share it

**Use cases:**
- Remote areas with no connectivity
- Emergency/disaster response
- Educational outreach
- "Just in case" resilience
- Learning how all this stuff works

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

## 🚀 Quick Start

**⚠️ Work in Progress ⚠️**

This project is being built in real-time. Documentation will grow as I figure things out.

Current roadmap:
1. ✅ Hardware acquired
2. ⏳ Raspberry Pi OS setup
3. ⏳ Kiwix installation + Wikipedia dumps
4. ⏳ Meshtastic configuration
5. ⏳ Integration & testing
6. ⏳ Solar power optimization

Check [JOURNAL.md](JOURNAL.md) for real-time progress updates.

---

## 📖 Documentation

- **[Hardware List](HARDWARE.md)** - Complete bill of materials
- **[Installation Guide](docs/)** - Step-by-step setup (coming soon)
- **[Journal](JOURNAL.md)** - My learning journey, mistakes included
- **[Contributing](CONTRIBUTING.md)** - How to help improve this

---

## 🧠 The Philosophy

> Prometheus stole fire from the gods and gave it to humanity.
> 
> We're stealing knowledge from the cloud and giving it to anyone with a radio.

This project is:
- **Beginner-friendly** - documented by a beginner, for beginners
- **Resilient** - works when nothing else does
- **Open** - free as in freedom, free as in beer
- **Practical** - real hardware, real tests, real problems solved

---

## 🤝 Contributing

Found a better way to do something? Spotted an error? Have suggestions?

**Open an issue or pull request!** This is a learning project, and shared knowledge makes it better.

Particularly helpful:
- Hardware alternatives/improvements
- Software optimization tips
- Power consumption reduction strategies
- Better antenna configurations
- Documentation improvements
- Translations

---

## 📜 License

MIT License - see [LICENSE](LICENSE)

Copyright © 2025 Guillain d'Erceville

**TL;DR:** Do whatever you want with this. Build it, sell it, improve it, break it. Just don't blame me if your station achieves sentience. 🤖

---

## 🙏 Acknowledgments

Standing on the shoulders of giants:
- [Kiwix](https://www.kiwix.org) - Offline knowledge heroes
- [Meshtastic](https://meshtastic.org) - Long-range mesh wizards
- [Raspberry Pi Foundation](https://www.raspberrypi.org) - Making computing accessible
- The entire open-source community

---

## 📞 Contact

- **GitHub:** [@GuillainM](https://github.com/GuillainM)
- **Issues:** [Report problems or ask questions](https://github.com/GuillainM/Prometheus-Station/issues)

---

<div align="center">

### ⚡ If you build this, share your experience! ⚡

**Star this repo if you think bringing knowledge to remote areas is cool.**

Made with 🔥 and ☕ somewhere between "I have no idea what I'm doing" and "Wait, that actually worked!"

</div>
