# 11. Backup

Script: [`installation/09-sauvegarde.sh`](../installation/09-sauvegarde.sh)

Memory cards do wear out. The encyclopedias can always be downloaded again, but your **settings** cannot: the password, the messages, your welcome board, your known Wi-Fi networks.

```
Pi$ cd ~/installation
Pi$ sudo bash 09-sauvegarde.sh
```

## What it does

- **Every day**, the station makes a small archive (a few KB) of its settings. The **7 most recent** are kept.
- It contains: the settings password (scrambled), low-power mode, colors, messages, welcome board, the community settings and data (announcement, register of people, mutual aid), content list, and the known Wi-Fi networks **with their passwords**.
- It does **not** contain the encyclopedias (they download again) nor the books (too big: keep your own copy of the books you add).

## Download it

**Settings > System > Backup**: the date of the last backup, a **Download** button and a **Back up now** button. Keep the file somewhere safe — and private, since it holds your Wi-Fi passwords.

## Put it back on a reinstalled station

After reinstalling the station (steps 1 to 11), copy the file to the Pi and restore it:

```
Mac$ scp prometheus-sauvegarde-2026-10-09-1927.tar.gz pi@prometheus-station.local:
Mac$ ssh pi@prometheus-station.local
Pi$ sudo prometheus-restaurer prometheus-sauvegarde-2026-10-09-1927.tar.gz
Pi$ sudo reboot
```

It refuses any file that would write anywhere else than the station's settings folders.

## A full copy of the card

To go further, once everything works, you can copy the whole card to your computer. Switch the station off (`sudo poweroff`), put the card in your Mac, find its number with `diskutil list external` (as in step 1.5), then:

```
Mac$ sudo dd if=/dev/rdisk4 bs=4m status=progress | gzip > ~/prometheus-card.img.gz
```

It takes a long time and as much room as the data on the card (about 200 GB). We have **not** tested this one ourselves; the daily settings backup is usually enough.

Next: [12. Using the station →](12-using-the-station.md)
