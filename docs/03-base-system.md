# 3. Base system

Script: [`installation/01-systeme.sh`](../installation/01-systeme.sh)

```
Pi$ cd ~/installation
Pi$ sudo bash 01-systeme.sh
Pi$ sudo reboot
```

The Pi restarts; wait one minute and connect again (`ssh pi@prometheus-station.local`).

## What it does, and why

| Setting | Why |
|---|---|
| Full system update | start from an up-to-date, patched system |
| **Wi-Fi country = France** | without a country, the Wi-Fi chip stays locked (`wlan0: unavailable`). Change `FR` in the script to your country code (`GB`, `US`, `DE`...) before running it |
| SPI and I2C turned on | SPI drives the e-ink screen (step 8); I2C is for a future battery sensor |
| Bluetooth off | not used, saves a little power |
| System log limited to 50 MB, kept across restarts | small enough to spare the card, but still readable after an unexpected restart |
| Automatic security updates | installed by themselves whenever the station has internet |
| `aria2`, `iw`, `rfkill` | download tool, Wi-Fi tools |

## Check

```
Pi$ nmcli radio wifi
```
```
enabled
```

```
Pi$ ls /dev/spidev* /dev/i2c-1
```
```
/dev/i2c-1  /dev/spidev0.0  /dev/spidev0.1
```

Next: [4. Encyclopedias →](04-encyclopedias.md)
