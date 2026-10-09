# Prometheus Station — build guide

A step-by-step guide for people who have **never used Linux**. Every command is given in full, with what you should see.

Start here: **[0. Before you start](00-before-you-start.md)**

| | Step | Script |
|---|---|---|
| 0 | [Before you start](00-before-you-start.md) — what you need, how to read the guide | — |
| 1 | [Prepare the SD card](01-prepare-the-sd-card.md) | — |
| 2 | [First boot](02-first-boot.md) | — |
| 3 | [Base system](03-base-system.md) | `01-systeme.sh` |
| 4 | [Encyclopedias](04-encyclopedias.md) | `02-encyclopedies.sh` |
| 5 | [Web portal and Wi-Fi](05-portal-and-hotspot.md) | `03-wifi-accueil.sh` |
| 6 | [Remote access](06-remote-access.md) *(optional)* | `04-tailscale.sh` |
| 7 | [Automatic Wi-Fi](07-automatic-wifi.md) | `05-wifi-auto.sh` |
| 8 | [E-ink screen](08-eink-screen.md) *(optional)* | `06-ecran.sh` |
| 9 | [Power](09-power.md) | `07-energie.sh` |
| 10 | [Security](10-security.md) | `08-securite.sh` |
| 11 | [Backup](11-backup.md) | `09-sauvegarde.sh` |
| 12 | [Using the station](12-using-the-station.md) | — |
| 13 | [The crisis test](13-crisis-test.md) | — |
| 14 | [Troubleshooting](14-troubleshooting.md) | — |

How it works inside, and what comes next: **[Reference](REFERENCE.md)**. The hardware: **[HARDWARE.md](../HARDWARE.md)**.

## How this guide was written

The station was rebuilt from an empty card in October 2026. Every step was run on the real station, and every check shown is one that passed. What has **not** been tested is said so, where it matters.

Later, a ready-made card image may make all this unnecessary. For now, you build it yourself.

## Contributing

Found a mistake, built one, adapted it to another language? Open an issue or a pull request on [the repository](https://github.com/Guillain-RDCDE/Prometheus-Station).
