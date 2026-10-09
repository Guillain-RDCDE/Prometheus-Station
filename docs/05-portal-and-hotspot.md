# 5. Web portal and Wi-Fi

Script: [`installation/03-wifi-accueil.sh`](../installation/03-wifi-accueil.sh) (needs internet: it downloads the web server and the e-book reader)

```
Pi$ cd ~/installation
Pi$ sudo bash 03-wifi-accueil.sh
```

## What it sets up

**The pages** (served by the web server **nginx**, on the usual web port 80):

- **Home**: three big doors, *Encyclopedias*, *Library*, *Messages*; French and English flags; a gear for the settings; the lighthouse logo opens the station's welcome board.
- **Encyclopedias**: one search box that searches *all* the collections while you type, and the list of collections. Articles open full screen, with a round magnifier button to come back to the search.
- **Library**: the EPUB and PDF books, read directly in the phone's browser. The e-book reader (epub.js and jszip) is stored on the station, so it works offline.
- **Messages**: a public message board for everyone connected.
- **Welcome board**: your own text — what the station is, its rules, its hours (you write it in the Settings).
- **Settings** and **Add files**: protected by a password (below).

Every page is in **French and English**; each phone chooses its own language (by default, the phone's language).

**Adding files**: a file dropped on the *Add files* page is sorted by itself — a `.zim` goes to the encyclopedias, an `.epub` or `.pdf` to the library, anything else is refused (program `prometheus-ranger`).

**The station's Wi-Fi**: an **open** network (no password) called **Prometheus-Station**. The station's address on it is `10.42.0.1`.

**The captive portal**: on that Wi-Fi, *any* web address leads to the station. That is what makes the home page open by itself when a phone joins, as in a hotel.

**A small internal server, `prometheus-admin`**, checks the password and handles the settings, the message board and the clock (see below). It only listens to the station itself.

## 5.1 Choose the password

Open the station in your computer's browser (still connected by cable):

**http://prometheus-station.local/parametres/**

The first time, the page asks you to **choose** the password (twice). There is no user name, just one password. You stay signed in for 90 days on that device. After 5 wrong attempts, you have to wait one minute.

> **Forgot it?** On the Pi: `sudo prometheus-mot-de-passe` erases it, and the page lets you choose a new one.

## 5.2 Check

```
Pi$ curl -s -o /dev/null -w "%{http_code}\n" http://localhost/
```
```
200
```

From your phone: the **Prometheus-Station** network now appears. Join it: the home page should open by itself (if not, open any web address, for example `http://example.com`). Step 7 then makes the station switch by itself between your home Wi-Fi and its own.

## The clock

The Pi has **no battery-backed clock**. Without internet it restarts with the time it had when it was switched off. So the home page sends the visiting phone's time to the station, once per visit. The station only takes it if it is **not** already on time through internet **and** is more than 2 minutes off.

Next: [6. Remote access →](06-remote-access.md)
