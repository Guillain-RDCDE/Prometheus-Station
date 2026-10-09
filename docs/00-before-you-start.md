# 0. Before you start

This guide builds a Prometheus Station from an empty memory card. It assumes you have **never used Linux**. Every command is given in full; you copy it, paste it, press Enter, and compare what you see with what the guide says you should see.

Allow **one afternoon** for the steps, plus **one night** for the encyclopedias to download.

## What you will have at the end

A small box that:

- creates its own Wi-Fi network, **Prometheus-Station**, with no internet and no password;
- opens a home page by itself on any phone that joins it (like hotel Wi-Fi);
- offers Wikipedia (French and English), medical and survival guides, repair guides, free books, and a message board;
- keeps working on a USB battery, and switches off cleanly before the battery dies;
- can be updated and repaired from your home when it has internet.

## What you need

| Item | Why | Notes |
|---|---|---|
| Raspberry Pi 4 (8 GB) | the computer | 4 GB should work, not tested |
| microSD card, **256 GB**, A2 class | the station's disk | with 128 GB, leave out English Wikipedia (see step 2) |
| USB-C power: a phone charger **or** a USB power bank | power | the project uses an Anker 737 (24,000 mAh) |
| A network cable (Ethernet) | to talk to the Pi during installation | any ordinary cable |
| A microSD card reader | to write the card from your computer | USB or built in |
| A computer | to prepare everything | this guide was written on a **Mac**; Linux works the same way; **Windows is not covered** |
| Internet at home | to download the system and the content | about 200 GB in total |
| *Optional:* Waveshare 2.13" e-Paper HAT **V4** | the little screen with the QR code | see step 6 |
| *Optional:* a free Tailscale account | to repair the station from anywhere | see step 4 |

Nothing else is needed: no keyboard, no mouse and no screen for the Pi.

## Three words you will meet

- **Terminal**: a window where you type commands instead of clicking. On a Mac, open *Applications > Utilities > Terminal*.
- **SSH**: a way to type commands *on the Pi* from your computer's Terminal. Once connected, everything you type runs on the Pi, not on your computer.
- **sudo**: a word you put in front of a command to run it as the administrator. The station is set up so that `sudo` never asks for a password.

## How to read this guide

- A line starting with `Mac$` is typed **on your computer**.
- A line starting with `Pi$` is typed **on the Pi**, through SSH.
- **Do not type** the `Mac$` or `Pi$` part itself, only what follows.
- Grey boxes without a prefix show what the screen should print.

> 💡 To paste in the Mac Terminal: **Cmd + V**. To stop a command that runs forever (like a log that keeps scrolling): **Ctrl + C**.

## The steps

| Step | What it does | Time |
|---|---|---|
| [1. Prepare the SD card](01-prepare-the-sd-card.md) | download the system, write it on the card | 20 min |
| [2. First boot](02-first-boot.md) | start the Pi, connect to it from your computer | 15 min |
| [3. Base system](03-base-system.md) | updates, Wi-Fi country, battery-friendly settings | 10 min |
| [4. Encyclopedias](04-encyclopedias.md) | Kiwix and the automatic downloads | 10 min + one night |
| [5. Web portal and Wi-Fi](05-portal-and-hotspot.md) | the pages, the open Wi-Fi, the password | 15 min |
| [6. Remote access](06-remote-access.md) | Tailscale *(optional)* | 5 min |
| [7. Automatic Wi-Fi](07-automatic-wifi.md) | home Wi-Fi when available, station Wi-Fi otherwise | 10 min |
| [8. E-ink screen](08-eink-screen.md) | QR code to join the Wi-Fi *(optional)* | 10 min |
| [9. Power](09-power.md) | clean shutdown on low battery, low-power mode | 10 min |
| [10. Security](10-security.md) | firewall, phones isolated from each other | 10 min |
| [11. Backup](11-backup.md) | daily copy of the settings | 5 min |
| [12. Using the station](12-using-the-station.md) | a tour of every page and setting | — |
| [13. The crisis test](13-crisis-test.md) | proof that it works with no internet | 20 min |
| [14. Troubleshooting](14-troubleshooting.md) | what went wrong for us, and how we fixed it | — |

The installation scripts are in the [`installation/`](../installation) folder. Their messages are in French (the project started in France); the guide translates what matters.

Next: [1. Prepare the SD card →](01-prepare-the-sd-card.md)
