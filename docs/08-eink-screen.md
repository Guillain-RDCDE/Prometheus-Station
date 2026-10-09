# 8. E-ink screen (optional)

Script: [`installation/06-ecran.sh`](../installation/06-ecran.sh)

The screen is a **Waveshare 2.13" e-Paper HAT, version V4** (250 × 122 pixels, black and white). It sits directly on the Pi's pins. An e-ink screen **keeps its image without power**, like paper: it only uses energy when the picture changes.

> Several versions of this screen exist (V2, V3, V4) and need different drivers. Ours is a V4: we displayed a test image with the V4 driver, and it appeared. If yours stays blank, try V3, then V2 (change `epd2in13_V4` in `prometheus-ecran` and in the script).

Switch the Pi off (`sudo poweroff`), unplug it, put the screen on the pins, power it again, then:

```
Pi$ cd ~/installation
Pi$ sudo bash 06-ecran.sh
```

It downloads only the files it needs from Waveshare's official driver and installs the service `prometheus-ecran`.

## What the screen shows

| Situation | Screen |
|---|---|
| Station's Wi-Fi open | a **QR code** to scan to join the Wi-Fi, and its name |
| Connected to a home Wi-Fi | the network's name, the station's address (and its QR code), the Tailscale address |
| Only the cable | the address |
| Switching off | **"Station éteinte — Rebranchez la batterie pour la rallumer"** (station off, plug the battery back to switch it on) |

The last line exists because the screen keeps its image: without it, a switched-off station would still show a QR code. It is drawn on a real shutdown, not on a restart.

The screen is redrawn only when the situation changes (checked every 20 seconds).

> ⚠️ Never run a test program for the screen while the service is running: both would fight for the pins (`GPIO busy`). Stop it first: `sudo systemctl stop prometheus-ecran`.

Next: [9. Power →](09-power.md)
