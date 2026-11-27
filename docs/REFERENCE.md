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

**Long-range radio (phase 2, working):** a LoRa radio plugged into the station puts the message board on the air: people without a radio write from their phone, handheld radios kilometres away answer ([chapters 15 and 16](15-meshtastic-radios.md)). The keeper's **Radio page** shows every channel, sends direct messages, sets the radio, and switches it in one tap between the two big free networks, **Meshtastic** and **MeshCore**, keeping each network's settings and identity ([chapter 17](17-radio-page.md)). Behind it, the **Mesh section** makes the station a complete mesh-radio post: every node and what to ask it, channels and keys, every one of the radio's settings with a safety net, statistics kept 90 days, a workshop that installs any supported board without internet, and remote administration of other radios ([chapter 18](18-mesh-section.md)).

**What it is not, yet:** it is not solar-powered (see *Status*).

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
| Library readers | **epub.js** 0.3 + jszip (EPUB), **pdf.js** 6.5 legacy (PDF), in `/var/www/prometheus/vendor/` | read in the phone's browser, offline; PDF: bookmarks, links, go to page, search, highlight |
| Downloads | `prometheus-telecharger` (aria2), daily timer | always the newest version, checked, resumed, 5 GB safety margin |
| Password, settings, messages, register, mutual aid, clock | `prometheus-admin` (Python, no extra module) | listens only on the station itself (127.0.0.1:8091) |
| Settings actions needing the administrator | `prometheus-commande`, `prometheus-ssid`, `prometheus-nom`, `prometheus-sobre` | the pages drop a request file; a system service carries it out. No page ever runs a program itself. Each order carries a number and gets an answer the page reads (done, started, waiting, refused); one radio operation at a time, the next one waits instead of being lost |
| What every program says the same way | `prometheus_commun.py` (Python) and `prometheus-commun` (for shell scripts), in `/usr/local/lib/prometheus/` | where files are, the settings and their defaults, writing a file safely, how many people are connected, whether an update is running, the colors. The radio's shared rules (which board is the station's, message sizes, backups, safety net, secrets) are in `radio_*.py` next to it |
| Folders and who may write in them | one table, `/etc/tmpfiles.d/prometheus.conf` (from `installation/prometheus-dossiers.conf`) | applied at every start and at the end of every installation step: a step can be run again alone, in any order |
| Radio | `prometheus-radio` (Python, Meshtastic and MeshCore libraries in `/opt/prometheus-radio`) | links the message board and the Radio page to the T-Beam: by USB on Meshtastic, by Bluetooth on MeshCore; off until turned on in the Settings |
| Radio tool | `prometheus-radio-outil` (run by `prometheus-commande`) | saves and sets the radio, switches networks, fetches and installs the radios' software, puts a backup back, recognises and installs any board ([chapters 17](17-radio-page.md) and [18](18-mesh-section.md)) |
| Station screen | `cage` + Chromium in kiosk mode, `prometheus-kiosque`, `prometheus-ecran-local` (step 11) | a screen and a USB keyboard on the station show its pages full screen, with sleep; off until turned on in the Settings ([chapter 19](19-screen-and-keyboard.md)) |
| Mesh section | pages in `/parametres/mesh/`, orders through `prometheus-admin` to `prometheus-radio`, history in SQLite | every node, channel and setting, statistics, workshop, remote administration ([chapter 18](18-mesh-section.md)) |
| Wi-Fi | NetworkManager + watchdog `prometheus-wifi-auto` | captive portal: every web address leads to the station |
| Remote access | Tailscale | optional |
| E-ink screen | `prometheus-ecran` (Python) | Waveshare 2.13" V4; can be turned off in the Settings when not fitted |
| Power | `prometheus-tension`, `prometheus-extinction` | clean shutdown on weak power; optional shutdown without visitors |
| Battery board | `prometheus-batterie` (Python, step 12) | Geekworm X728 V2.5 and four 18650 cells: charge in the Settings, clean shutdown when the cells run low, power cut afterwards, its button, a log for battery-life tests ([step 9](09-power.md#90-the-battery-case-x728)) |
| Board clock | `prometheus-horloge` (shell, step 12) | the X728's clock (DS1307, `/dev/rtc0`) puts the station on time at boot even without internet; the internet time is copied into it every hour and at shutdown; without internet nor board clock, the time from radios heard, when at least two agree ([step 9](09-power.md#90-the-battery-case-x728)) |
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
| `/srv/prometheus/radio/` | radio messages waiting, sent and received, the radio's state and details, the network in use, the radios' software (`logiciels/`) and each network's settings (`sauvegardes/`, administrator only: it holds the radios' keys) |
| `/srv/prometheus/communaute/` | community settings, register of people, mutual-aid posts, most searched topics (title and count only) |
| `/srv/prometheus/.admin/` | password (scrambled), sessions, chosen colors, low-power mode |
| `/srv/prometheus/sauvegardes/` | the last 7 settings backups (what they contain: `/usr/local/lib/prometheus/sauvegarde.liste`) |
| `/srv/prometheus/commande/` | the orders of the buttons, carried out at once by `prometheus-commande`; `commande-attente/`: a radio order waiting for the one before |
| `/var/www/prometheus/ajouter/resultats/` | the answer to each numbered order, kept one day (behind the password) |
| `/srv/prometheus/.admin/doublons-gardes` | fingerprints of duplicate books the keeper chose to keep (*Keep both*) |
| `/var/lib/prometheus-batterie/journal.csv` | X728 battery board: one reading per minute, each shutdown and start (summed up by `prometheus-batterie --bilan`) |
| `/run/prometheus/` | live values, emptied at every start (automatic shutdown, voltage, batteries; `heure-radio.json`: a time request from the radio) |
| `/run/prometheus-heure` | where the time came from since the start: `carte` (X728 board) or `radio`; internet: `/run/systemd/timesync/synchronized` exists |

### Network

| | |
|---|---|
| Station Wi-Fi | open, `Prometheus-Station` (renamable), 2.4 GHz channel 6, station at `10.42.0.1`, phones isolated from each other |
| Ports open to visitors | 80 only |
| Administration | SSH by key only, from the cable, the home Wi-Fi or Tailscale — never from the station's Wi-Fi |
| Name | `prometheus-station.local` (changeable in the Settings), at home and on the station's Wi-Fi |

### Power (measured)

| | |
|---|---|
| At rest, network cable plugged | about 2.6 W |
| At rest, on battery | about 2.0 W |
| Low-power mode | about 1.9 W |
| Battery board | X728 with four Samsung 35E 18650 (about 50 Wh) — **about 9 h 30, measured** with the radio plugged in (25 November 2026) |
| Power bank | Anker 737, about 86 Wh — **about one day** (estimate; full discharge not tested) |

## Status (November 2026)

**Built and tested**
- installation from an empty card, step by step;
- the nine collections downloaded and searchable (about 200 GB);
- library, message board, welcome board, settings, two languages, eight themes (Neutral by default, High contrast);
- community tools: announcement (pages and e-ink screen), Emergency page (its 28 links all checked), register of people, mutual aid, printable poster (its QR code checked with a reader). Tested on the station's server and on copies of the pages; not yet from several phones at once;
- automatic switching between home Wi-Fi and the station's Wi-Fi;
- e-ink screen;
- clean shutdown on weak power (simulated in real time);
- **the crisis test**: on battery, phone in airplane mode, no internet — Wi-Fi, home page, encyclopedias, books, messages and settings all worked ([step 13](13-crisis-test.md));
- **Meshtastic radio** (phase 2): a T-Beam on the station, two T-Echo handhelds, all on the same Meshtastic version; the message board on the air both ways, the e-ink screen showing radio messages, long ones scrolling ([chapters 15 and 16](15-meshtastic-radios.md)). Tested indoors only.
- **The Radio page** (October 2026): every channel, direct messages delivered and acknowledged, radio settings, the radios' software fetched and installed with their settings kept, and **two full round trips Meshtastic → MeshCore → Meshtastic**, with each network's identity kept and checked ([chapter 17](17-radio-page.md)). On MeshCore, sending and receiving tested with a second radio one metre away; range to the neighbouring MeshCore repeaters not reached yet with the short antenna indoors.
- **The radios' software managed from the station**: the latest versions of both networks fetched every day when there is internet; the T-Beam and the T-Echo installed, updated or switched between Meshtastic (full screen or the simpler InkHUD screen), MeshCore for a phone and MeshCore for the station, each radio's settings and identity kept and checked.
- **The Mesh section** (19 October 2026): every Meshtastic and MeshCore setting read and written with a backup before each change, a safety net that puts the previous settings back by itself when the radio does not come back, nodes and requests by radio (traceroute, metrics), channels, statistics, remote administration of a T-Echo over the air, and a workshop that recognised and updated a T-Echo through its general path, identity unchanged ([chapter 18](18-mesh-section.md)). Not yet tried on other boards (ESP32, RP2040) nor with a MeshCore repeater.
- **A radio beacon** (20 October 2026): a ready-made message sent by radio every 3 hours, at first only while the Emergency page is on ([chapter 16](16-radio-message-board.md#the-beacon)).
- **A screen and a keyboard on the station** (19 October 2026): its pages full screen without a phone, sleep and wake-up, tested with a virtual screen; a real HDMI screen comes next ([chapter 19](19-screen-and-keyboard.md)).
- **A battery board and a metal case** (25 November 2026): Geekworm X728 with four 18650 cells; charge and mains read, clean-shutdown rule checked in a dry run, charge shown in the Settings. First full discharge (25 November): **about 9 h 30** with the radio plugged in, clean shutdown at 5 %, then the power cut by the board. Since 26 November, the board's clock keeps the station on time without internet, and the time left is read from the voltage. Switched back on with the board's button after a real power cut, on time at once; the button while running is not tested yet ([step 9](09-power.md#90-the-battery-case-x728)). The e-ink screen is set aside: it does not fit in the closed case.
- **System updates with their details on screen**, as they run, and a plain-language summary under them (27 November 2026).
- **Automated tests** (27 November 2026), after a review of the whole code: one place for each rule that used to be copied (settings and their defaults, folder rights, the backup list, the radio's rules, the pages' shared code), and tests that keep it so — `bash tests/lancer.sh`, also run by GitHub on every change: the shared module, the radio without a radio, every address of the settings server, the buttons' orders, each page in a real browser. Eleven defects found by the review are fixed, among them the safety net now also on MeshCore (tried for real: a risky setting written, the radio's link cut, the previous settings put back by the station itself after 3 minutes), radio keys no longer readable by other accounts, and a step of the installation that could be run again without breaking the buttons.

**Built, not yet tested in real conditions**
- firewall and phone isolation, seen from a phone on the station's Wi-Fi;
- automatic shutdown without visitors, with its message on the screen;
- several phones at once;
- **radio range**: outdoors, then with the antenna on the mast;
- **the time from the radio** (26 November 2026): two radios agreeing set the station on time, a lone wrong repeater is ignored; tested with simulated radios only.

**Next**
- **more from the radio**: ready-made messages and an SOS from the handhelds without a phone, a roll call that warns when a radio has gone silent, a "radar" showing how far and in which direction each radio is, messages that wait for a radio out of range, Wikipedia answers by radio;
- **the antenna on the mast**, and a range map;
- **solar power**: a 30 W folding panel feeding the battery;
- **linking stations together**: messages, announcements, the register of people and mutual-aid posts travel from one station to another — by Meshtastic radio, or failing that on a USB stick carried by hand — so that someone safe in one village can be found from the next;
- **a rugged case**: the whole station in a waterproof hard case that works closed (left at the foot of a tree for the night), with a keyboard in the lid and 3D-printed inner parts;
- **a ready-made card image**, so that nobody has to type a single command.

## Contributing

Most useful: field reports, content suggestions (other languages, other ZIM files), hardware alternatives, corrections to the guide. Open an issue or a pull request on [the repository](https://github.com/Guillain-RDCDE/Prometheus-Station).

Before proposing a change to the code, run `bash tests/lancer.sh` from the repository (Python 3, and Node for the pages; Chrome for the browser test). A rule that several programs need goes in the shared module, never in a copy: the tests check it.

---

**Prometheus Station is a lighthouse when everything burns.**

*Last updated: November 2026.*
