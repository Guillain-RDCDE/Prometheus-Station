# 9. Power

Script: [`installation/07-energie.sh`](../installation/07-energie.sh)

## The problem

The station runs on an ordinary **USB power bank** (the project uses an Anker 737, about 86 Wh). Such a battery **does not tell the Pi how full it is**: it gives 5 volts, then cuts off at once. A computer switched off brutally can damage its memory card. So rather than predicting the end of the battery, the station is made **safe to cut**, and it switches itself off cleanly when it can see trouble coming.

```
Pi$ cd ~/installation
Pi$ sudo bash 07-energie.sh
```

## 9.1 Clean shutdown when the power gets weak

The service `prometheus-tension` asks the Pi every 5 seconds whether its supply voltage is **too low right now**. If it stays too low for **30 seconds in a row**, the station shuts down cleanly (and the e-ink screen says so).

What we tested, in real time:

| Situation | Result |
|---|---|
| voltage low continuously | clean shutdown after 31 s |
| low for 20 s, normal again, then low again | the count starts over, no shutdown |
| an old alert only (in the past) | nothing |

Limit: if a battery cuts off without weakening first, nothing can be done — hence the next point.

## 9.2 Writing less on the card

- the system groups its writes every 30 seconds instead of 5 (`commit=30`), and doesn't note each file read (`noatime`);
- the web server **no longer records visits**: fewer writes, and no trace of who read what;
- downloads write one summary line per minute instead of one per second.

Measured at rest: about 470 KB written per minute, mostly the system log (kept on purpose, to understand an unexpected restart). That rewrites the 256 GB card roughly **once a year**: negligible wear.

## 9.3 Energy settings (Settings > System > Energy)

Both are **off** by default.

**Low-power mode**: lights off, slower processor, USB ports off. We measured it with a cheap USB power meter:

| Setting | Effect |
|---|---|
| network cable unplugged | about −0.4 W (it is never plugged on battery anyway) |
| lights off | slight |
| slower processor | about −0.1 W |
| USB ports off | too small for our meter |
| network socket off | nothing (left on: it is the rescue access) |
| weaker Wi-Fi signal | nothing at rest (left at full power, for range) |

So about **2.1 W → 1.9 W**. The price: searching the encyclopedias is 3 to 5 times slower (usually still under a second). The USB ports don't work in this mode.

**Automatic shutdown**: *Never*, or after 1, 2, 4 or 8 hours **without a visitor** (a phone on the station's Wi-Fi, a page being opened, or a remote connection). Useful at night when someone sleeps next to the station and can plug it back in the morning: once switched off, nobody can reach it until the battery is unplugged and plugged back in. **A restarted station always starts with no shutdown planned.** It never shuts down in the middle of a system update.

> We chose **not** to make a "night mode" that switches the Wi-Fi off: a station nobody can reach is useless, and with the Wi-Fi on, there is nothing left to save at night.

## Switching off by hand

*Settings > Switch off* (tap twice) shuts the station down cleanly, like the command `sudo poweroff`; *Settings > Restart*, next to it, restarts it cleanly. Always prefer it to pulling the battery when you can. To switch it back on: unplug the battery and plug it in again.

## Battery life

At rest, the station uses about **2 W** (2.6 W with the network cable plugged in, which it never is on battery). On the Anker 737, the estimate is **about one day**. A full discharge test has **not** been done yet.

Next: [10. Security →](10-security.md)
