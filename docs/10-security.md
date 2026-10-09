# 10. Security

Script: [`installation/08-securite.sh`](../installation/08-securite.sh)

The station's Wi-Fi is **open**: anyone nearby can join. That is the point — but it means visitors must only be able to *read*, never to reach the station's insides, nor each other.

```
Pi$ cd ~/installation
Pi$ sudo bash 08-securite.sh
```

## What it does

1. **A firewall** (`ufw`) refuses every incoming connection except:

   | Allowed | For |
   |---|---|
   | port 80 | the web pages, for everyone |
   | port 22 (SSH) | the administrator — **but not from the station's own Wi-Fi** |
   | Tailscale | remote access (step 6) |
   | ports 67 and 53 on Wi-Fi | giving addresses to phones, and the captive portal |
   | port 5353 | the name `prometheus-station.local` |

   So you administer the station by **cable, home Wi-Fi or Tailscale** — never from the open Wi-Fi.

2. **Kiwix only answers the station itself**: visitors always go through the web pages.

3. **Phones on the station's Wi-Fi cannot contact each other** (they only see the station).

The firewall does not log every refused connection, to spare the card.

## The safety net — read before running

A firewall mistake can lock you out of the Pi. So the script **switches the firewall off by itself after 5 minutes**, unless you confirm. Once it has run:

1. from your computer, in a **new** Terminal window, check that you can still connect: `ssh pi@prometheus-station.local`;
2. check that the pages open: http://prometheus-station.local/;
3. then confirm, on the Pi:

```
Pi$ sudo systemctl stop prometheus-parefeu-filet.timer
```

If you can't connect any more, just wait 5 minutes: the firewall switches off.

## Check

```
Pi$ sudo ufw status
```
```
Status: active
...
22/tcp     DENY IN     10.42.0.0/24
22/tcp     ALLOW IN    Anywhere
80/tcp     ALLOW IN    Anywhere
...
```

## What is already safe without this step

- SSH only accepts **your key**: there is no password to guess (set at first boot);
- the settings pages need the password; it is stored scrambled (PBKDF2), never in clear.

## Known limit

The pages use plain `http`, not `https`. On the open Wi-Fi, someone with the right tools nearby could capture the settings password when you type it. `https` on a station with no internet would make every phone show a frightening security warning, so it was left out. **Prefer changing settings from home (home Wi-Fi or Tailscale)**, and choose a password you use nowhere else.

Next: [11. Backup →](11-backup.md)
