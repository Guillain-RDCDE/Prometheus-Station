# 7. Automatic Wi-Fi

Script: [`installation/05-wifi-auto.sh`](../installation/05-wifi-auto.sh)

The goal:

- **a Wi-Fi network you know is in range** (home, phone hotspot) → the station joins it. It gets internet for its updates, and you can reach it from home;
- **no known network** → the station opens its own Wi-Fi, **Prometheus-Station**.

```
Pi$ cd ~/installation
Pi$ sudo bash 05-wifi-auto.sh
```

## 7.1 Teach it your Wi-Fi networks

Once per network:

```
Pi$ sudo prometheus-wifi-maison
```

It asks for the network's name (exactly as your phone shows it), then its password (nothing appears while you type). Do it for your home Wi-Fi, and perhaps your phone's hotspot. The passwords are kept by the system, readable only by the administrator.

## How it decides

A small watchdog, `prometheus-wifi-auto`, runs all the time:

- at start-up, it leaves **45 seconds** to find a known network; otherwise it opens the station's Wi-Fi;
- it then checks every **30 seconds**. If the connection drops, it looks for a known network, otherwise it opens the station's Wi-Fi;
- while the station's Wi-Fi is open, **nobody is connected** and a known network exists, it pauses the station's Wi-Fi for about 20 seconds **every 10 minutes**, to see whether home is back. Typical case: the router restarts after a power cut.

It never interrupts the station's Wi-Fi while a phone is on it.

## Check

With the cable unplugged and your home Wi-Fi in range:

```
Pi$ nmcli -t -f NAME,DEVICE con show --active
```
```
maison-YourWifiName:wlan0
```

(`maison` means home.) Without any known network nearby, you would see `prometheus-wifi:wlan0`, and **Prometheus-Station** appears on your phone.

Next: [8. E-ink screen →](08-eink-screen.md)
