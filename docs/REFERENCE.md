# Prometheus Station — reference

[← Back to the README](../README.md) · [Build guide](README.md)

## What it is

A Raspberry Pi with a large memory card that creates its own Wi-Fi bubble. Anyone in range joins it with a phone and finds, **without internet**:

- **Encyclopedias**: complete Wikipedia in French and English (with images), MDWiki (medicine), WikEM (emergency medicine), iFixit repair guides, and practical guides on water, food and life after a disaster;
- **A library**: free books from Project Gutenberg, plus any EPUB or PDF you add, read in the browser;
- **A message board** for everyone connected;
- **A welcome board** written by whoever keeps the station: what it is, its rules, its hours;
- **Community tools**, switched on by the keeper when needed: an announcement band on every page, an Emergency page with first-aid shortcuts, a register to find your loved ones, and a mutual-aid board; and a poster to print and stick on the walls.

It runs on a USB power bank, and is built to be safe when the power cuts. When it finds internet again, it updates itself.

**What it is not, yet:** it is not solar-powered and it has no long-range radio. Both are the next phases (see *Status*).

## Why it exists

Modern knowledge lives in the cloud. When the network fails — disaster, war, censorship, or simply a remote place — a doctor can't look up a treatment, a builder can't find a specification, a teacher has nothing to teach from.

Prometheus Station keeps a copy of that knowledge close at hand, readable by anyone with a phone, needing nothing but a little electricity.

**Prometheus gave humanity fire. This station keeps the knowledge to use it.**

### Who it is for

- communities after a disaster, rebuilding water, power, shelter;
- remote clinics and field missions without connectivity;
- places where the internet is censored or cut;
- off-grid settlements, schools without reliable connectivity;
- anyone preparing their community for long outages.

## Principles

- **Works with no network at all.** No internet, no router, nothing. That is goal number one.
- **Nobody needs to know Linux to use it.** Visitors only use their phone's browser; the keeper uses a settings page.
- **As little electricity as possible.** Nothing is added that draws power without a reason.
- **Free and open.** Open-source software only, no subscription, no account needed to use it, no tracking: the web server does not even record visits.
- **Nothing invented.** The documentation is written after the fact, from what actually ran.

## How it works inside

```
            USB power bank (Anker 737)
                      │
              ┌───────▼────────┐        e-ink screen (QR code)
              │ Raspberry Pi 4 │◄────── on the pins (SPI)
              │  256 GB card   │
              └───────┬────────┘
       ┌──────────────┼───────────────┐
  Wi-Fi chip       network socket   internet (when available)
  │                (installation,   │
  │                 rescue access)  └─ updates, Tailscale
  ├─ known home Wi-Fi in range → joins it
  └─ otherwise → opens "Prometheus-Station" (open, 10.42.0.1)
                    │
              phones, tablets, laptops
```

### Software

| Part | What does it | Notes |
|---|---|---|
| Operating system | Raspberry Pi OS Lite 64-bit (Debian 13 "Trixie") | set up at first boot by cloud-init |
| Web pages | **nginx**, port 80 | static pages in `/var/www/prometheus`, in French and English |
| Encyclopedias | **Kiwix** (`kiwix-serve` 3.7), service `prometheus-kiwix` | listens only on the station itself, behind nginx at `/encyclopedies` |
| Downloads | `prometheus-telecharger` (aria2), daily timer | always the newest version, checked, resumed, 5 GB safety margin |
| Password, settings, messages, register, mutual aid, clock | `prometheus-admin` (Python, no extra module) | listens only on the station itself (127.0.0.1:8091) |
| Settings actions needing the administrator | `prometheus-commande`, `prometheus-ssid`, `prometheus-sobre` | the pages drop a request file; a system service carries it out. No page ever runs a program itself |
| Wi-Fi | NetworkManager + watchdog `prometheus-wifi-auto` | captive portal: every web address leads to the station |
| Remote access | Tailscale | optional |
| E-ink screen | `prometheus-ecran` (Python) | Waveshare 2.13" V4 |
| Power | `prometheus-tension`, `prometheus-extinction` | clean shutdown on weak power; optional shutdown without visitors |
| Security | `ufw` firewall | see [step 10](10-security.md) |
| Backup | `prometheus-sauvegarde` (daily), `prometheus-restaurer` | see [step 11](11-backup.md) |

The script and program names are in French; the guide gives each one's role.

### Where things are

| Path | Content |
|---|---|
| `/srv/prometheus/encyclopedies/` | the `.zim` files and Kiwix's catalogue |
| `/srv/prometheus/bibliotheque/` | the books |
| `/srv/prometheus/contenus.txt` | the list of encyclopedias to keep up to date |
| `/srv/prometheus/messages/` | the message board |
| `/srv/prometheus/panneau/` | the welcome board text |
| `/srv/prometheus/communaute/` | community settings, register of people, mutual-aid posts, most searched topics (title and count only) |
| `/srv/prometheus/.admin/` | password (scrambled), sessions, chosen colors, low-power mode |
| `/srv/prometheus/sauvegardes/` | the last 7 settings backups |
| `/run/prometheus/` | live values, emptied at every start (automatic shutdown, voltage) |

### Network

| | |
|---|---|
| Station Wi-Fi | open, `Prometheus-Station` (renamable), 2.4 GHz channel 6, station at `10.42.0.1`, phones isolated from each other |
| Ports open to visitors | 80 only |
| Administration | SSH by key only, from the cable, the home Wi-Fi or Tailscale — never from the station's Wi-Fi |
| Name at home | `prometheus-station.local` |

### Power (measured)

| | |
|---|---|
| At rest, network cable plugged | about 2.6 W |
| At rest, on battery | about 2.0 W |
| Low-power mode | about 1.9 W |
| Battery | Anker 737, about 86 Wh — **about one day** (estimate; full discharge not tested yet) |

## Status (October 2026)

**Built and tested**
- installation from an empty card, step by step;
- the nine collections downloaded and searchable (about 200 GB);
- library, message board, welcome board, settings, two languages, six color themes;
- community tools: announcement (pages and e-ink screen), Emergency page (its 28 links all checked), register of people, mutual aid, printable poster (its QR code checked with a reader). Tested on the station's server and on copies of the pages; not yet from several phones at once;
- automatic switching between home Wi-Fi and the station's Wi-Fi;
- e-ink screen;
- clean shutdown on weak power (simulated in real time);
- **the crisis test**: on battery, phone in airplane mode, no internet — Wi-Fi, home page, encyclopedias, books, messages and settings all worked ([step 13](13-crisis-test.md)).

**Built, not yet tested in real conditions**
- firewall and phone isolation, seen from a phone on the station's Wi-Fi;
- automatic shutdown without visitors, with its message on the screen;
- several phones at once; a full battery discharge.

**Next**
- **Meshtastic** (phase 2, the purpose of the project): LoRa radios that carry text messages over kilometres without any network, and a page on the station to read and answer them from a phone;
- **solar power**: a 30 W folding panel feeding the battery;
- **a battery sensor**, to know the real charge level;
- **linking stations together**: messages, announcements, the register of people and mutual-aid posts travel from one station to another — by Meshtastic radio, or failing that on a USB stick carried by hand — so that someone safe in one village can be found from the next;
- **a ready-made card image**, so that nobody has to type a single command.

## Contributing

Most useful: field reports, content suggestions (other languages, other ZIM files), hardware alternatives, corrections to the guide. Open an issue or a pull request on [the repository](https://github.com/Guillain-RDCDE/Prometheus-Station).

---

**Prometheus Station is a lighthouse when everything burns.**

*Last updated: October 2026.*
