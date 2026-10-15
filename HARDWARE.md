# 🛠️ Hardware

What the station is made of, why, and what it costs. Prices are those paid in December 2025, rounded.

The list has two parts: what **runs the station today** (including the Meshtastic radios since October 2026), and what was **bought for the next phases** and is not in service yet.

## In service today

| Item | Role | Price |
|---|---|---|
| **Raspberry Pi 4, 8 GB** | the computer | ~75 € |
| **microSD SanDisk Extreme 256 GB, A2** | the station's disk: system + about 200 GB of encyclopedias | ~35 € |
| **Anker PowerCore 737** (24,000 mAh, about 86 Wh) | the battery | ~73 € |
| **Waveshare 2.13" e-Paper HAT V4** (250 × 122, ref. 12915) | the small screen with the QR code *(optional)* | ~17 € |
| USB-C cable, network (Ethernet) cable | power, installation | a few euros |

About **200 €** for a working station.

### Raspberry Pi 4 (8 GB)

A credit-card-sized computer, with no screen or keyboard. It runs everything: the Wi-Fi, the web pages, the encyclopedias.

- **You buy separately**: the memory card, a power supply or battery, and a case if you want one. The board comes alone.
- **4 GB** should work (searches a little slower); not tested here. A Pi 5 would work too but uses more power, which matters on battery.
- It has **no battery-backed clock**: without internet, the station takes the time from the first phone that visits.

### microSD card, 256 GB, A2 class

Everything lives on it. With the content list of the guide, about 34 GB stay free.

- **Why A2**: the encyclopedias are read in small random pieces; A2 cards are much faster at that. A slow card makes every search painful.
- **Smaller card?** With 128 GB, leave out English Wikipedia (127 GB); see [step 4](docs/04-encyclopedias.md).
- Buy from a reputable seller: fake capacities are common.

### Anker PowerCore 737

A large USB power bank.

- At rest the station uses about **2 W** (measured): roughly **one day** of battery (estimate; a full discharge has not been tested yet).
- Such a battery doesn't tell the Pi its charge level and cuts off at once when empty. The station is built to survive that ([step 9](docs/09-power.md)).
- The Pi is **sensitive to weak power**: a poor cable or a tired battery causes restarts. *Settings > Station health* shows whether the power has been too low.

### Waveshare 2.13" e-Paper (V4)

A paper-like screen: it **keeps its image without power** and only uses energy when it changes. It shows the QR code to join the Wi-Fi, the station's addresses at home, and "Station éteinte" (switched off) when it shuts down ([step 8](docs/08-eink-screen.md)). Check the **version** (V2, V3, V4): each needs its own driver.

## Meshtastic radio (phase 2, in service)

| Item | Role | Price |
|---|---|---|
| LILYGO T-Beam LoRa32 **868 MHz** (ESP32 + GPS, here v1.2) | the station's radio, plugged into the Pi by USB | ~47 € |
| LILYGO T-Echo Meshtastic terminals × 2 | handheld radios with e-ink screen, GPS and battery | ~97 € |
| Samsung 18650 batteries (3,450 mAh) × 4 | the T-Beam's battery (and spares) | ~14 € |
| Xtar MC2 charger | charging the 18650s safely | ~20 € |

Setting them up: [chapter 15](docs/15-meshtastic-radios.md). Use **data** USB cables (micro-USB for the T-Beam, USB-A to USB-C for the T-Echo): many cables only charge.

## Bought for the next phases (not in service yet)

| Item | Planned role | Price |
|---|---|---|
| 868 MHz omnidirectional antenna | radio range, on the mast | ~30 € |
| Anker SOLIX PS30 solar panel (30 W, foldable) | charging the battery | ~73 € |
| Spiderbeam 7 m telescopic fiberglass mast | height for the antennas | ~55 € |
| USB cables (right-angle, 2 m 100 W PD...) | connections | ~34 € |

### Why LoRa and Meshtastic

LoRa radios carry short text messages over **kilometres** (1 to 15 km depending on terrain and height) using very little power, with no network at all. **Meshtastic** is free software that turns them into a mesh: messages hop from radio to radio. The station shows the radio messages on its message board, so people without a radio can read and answer them from their phone ([chapter 16](docs/16-radio-message-board.md)).

The same T-Beam also runs **MeshCore**, the other big free LoRa mesh network: the station switches it from one network to the other in one tap, with nothing to buy ([chapter 17](docs/17-radio-page.md)). On MeshCore the T-Beam talks to the Pi over Bluetooth, which the Pi 4 has built in.

### Why a mast

Height is range: at ground level, buildings and trees block the signal; at a few metres, radios see much further.

## ⚠️ Warnings

1. **Radio frequencies are regulated.** 868 MHz is the legal band in Europe; the US and Canada use 915 MHz. Check your country's rules before buying. **Never power a LoRa radio without its antenna**: it can destroy it.
2. **Power quality.** The Pi needs a stable 5 V, 3 A. Undervoltage causes random restarts.
3. **18650 batteries** can be dangerous: never short-circuit, puncture or overcharge them; use protected cells from known brands and a proper charger.

## Where to buy (Europe)

- **Raspberry Pi, screen**: [Kubii](https://www.kubii.com) (France), [BerryBase](https://www.berrybase.de) (Germany), [The Pi Hut](https://thepihut.com) (UK)
- **LoRa / Meshtastic**: [AliExpress](https://aliexpress.com) (LILYGO's official store), [Rokland](https://store.rokland.com)
- **Battery, solar panel**: Anker's official stores
- **Antennas, mast**: [Passion Radio](https://www.passion-radio.com) (France), [Spiderbeam](https://www.spiderbeam.com) (Germany)

---

[Build guide](docs/README.md) · [Reference](docs/REFERENCE.md)

*Last updated: October 2026.*
