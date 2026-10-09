# 2. First boot

The Pi has no screen and no keyboard. You will talk to it through a network cable plugged into your computer, and your computer will lend it its internet connection.

## 2.1 Lend your internet to the Pi

1. Plug the network cable between the Pi and your Mac (a USB-to-Ethernet adapter works if your Mac has no network socket).
2. On the Mac: **System Settings > General > Sharing > Internet Sharing**. Click the **(i)**: share your connection from **Wi-Fi**, to computers using **Ethernet** (or the name of your adapter). Turn the switch on.

Your Mac keeps its Wi-Fi. It gives the Pi an address (usually `192.168.2.2`) and passes internet to it.

> On Linux, the equivalent is a "Shared to other computers" Ethernet connection in NetworkManager. Not tested here.

## 2.2 Start the Pi

Put the card in the Pi, then plug in the power. Wait **2 minutes**: on the very first start the Pi sets itself up and restarts.

Check that it answers:

```
Mac$ ping -c2 prometheus-station.local
```

```
64 bytes from 192.168.2.2: icmp_seq=0 ttl=64 time=0.6 ms
```

If you get `cannot resolve`, wait one more minute and try again.

## 2.3 Connect to it

```
Mac$ ssh pi@prometheus-station.local
```

The first time, SSH asks `Are you sure you want to continue connecting (yes/no)?`: type `yes`. You are now **on the Pi**: the prompt changes to something like `pi@prometheus-station:~ $`.

Check that the first-boot setup finished:

```
Pi$ cloud-init status --long
```

```
status: done
```

To leave the Pi and come back to your Mac at any time: type `exit`.

## 2.4 Copy the installation scripts to the Pi

From **your Mac** (type `exit` first if you are on the Pi), in the project folder:

```
Mac$ cd ~/Downloads/Prometheus-Station-main
Mac$ rsync -a --checksum --exclude .DS_Store installation/ pi@prometheus-station.local:installation/
```

Check that the copy is identical on both sides. This matters: during our build the Pi restarted in the middle of a copy and several files arrived **empty**, which broke a later step (see [troubleshooting](14-troubleshooting.md)).

```
Mac$ (cd installation && find . -type f ! -name .DS_Store -exec shasum {} + | LC_ALL=C sort -k2) > /tmp/mac.sha
Mac$ ssh pi@prometheus-station.local 'cd installation && find . -type f -exec sha1sum {} + | LC_ALL=C sort -k2' > /tmp/pi.sha
Mac$ diff /tmp/mac.sha /tmp/pi.sha && echo IDENTICAL_COPY
```

You should see `IDENTICAL_COPY`. If not, run the `rsync` line again.

## 2.5 How to run each step from now on

Every following step is one script. You connect to the Pi, go into the folder, and run it:

```
Mac$ ssh pi@prometheus-station.local
Pi$ cd ~/installation
Pi$ sudo bash 01-systeme.sh
```

Long steps can be run as a **background job of the Pi**, so that they keep going even if your computer goes to sleep or the cable is pulled:

```
Pi$ sudo systemd-run --collect --unit=install-step --working-directory=$HOME/installation bash -c "bash 03-wifi-accueil.sh > $HOME/step.log 2>&1"
Pi$ tail -f ~/step.log
```

(`Ctrl + C` stops watching the log, not the job.)

Each script ends with a line `== Etape N terminee` ("step N finished"). Every script can be run again safely if something went wrong.

Next: [3. Base system →](03-base-system.md)
