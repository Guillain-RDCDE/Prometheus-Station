# 1. Prepare the SD card

You will download the Pi's operating system (Raspberry Pi OS), write it on the card, and add two small files that set the Pi up by itself the first time it starts.

## 1.1 Get the project files

Download this repository: on its GitHub page, click **Code > Download ZIP**, then double-click the ZIP to unpack it. You get a folder called `Prometheus-Station-main`. Everything below happens **inside that folder**.

In the Terminal, go into it (drag the folder onto the Terminal window after typing `cd ` with a space, then press Enter):

```
Mac$ cd ~/Downloads/Prometheus-Station-main
```

## 1.2 Create your SSH key (once in your life)

The Pi will have **no password**. You will connect with a *key*: a pair of files on your computer, one secret, one public. The public one goes on the Pi; the secret one never leaves your computer.

Check whether you already have one:

```
Mac$ cat ~/.ssh/id_ed25519.pub
```

If you see a line starting with `ssh-ed25519`, you have one: skip to 1.3. If you see `No such file or directory`, create it:

```
Mac$ ssh-keygen -t ed25519
```

Press Enter three times (default place, no passphrase — or type a passphrase if you want one, and remember it). Then show it:

```
Mac$ cat ~/.ssh/id_ed25519.pub
```

```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAA... you@your-mac
```

Copy that **whole line**.

## 1.3 Fill in the first-boot file

Open `installation/user-data` with TextEdit (right-click > Open With > TextEdit). Change the three lines marked `<-- CHANGE`:

1. `timezone:` your time zone (for example `Europe/London`, `America/New_York`);
2. `layout:` your keyboard (`us`, `gb`, `fr`, `de`...). It only matters if one day you plug a keyboard into the Pi;
3. replace `PASTE-YOUR-PUBLIC-KEY-HERE` with the line you copied in 1.2. Keep the `- ` in front of it.

Save. What this file does on the first start:

- names the Pi `prometheus-station`;
- creates the user **`pi`**, who can only log in with your key (no password at all);
- turns on SSH.

The second file, `installation/network-config`, tells the Pi to use the network cable automatically. You don't need to change it.

## 1.4 Download Raspberry Pi OS Lite

We use **Raspberry Pi OS Lite, 64-bit, "Trixie"** (no desktop: the Pi never has a screen). The project used the version of 6 October 2026:

```
Mac$ mkdir -p ~/PrometheusImages && cd ~/PrometheusImages
Mac$ curl -LO https://downloads.raspberrypi.com/raspios_lite_arm64/images/raspios_lite_arm64-2026-10-06/2026-10-06-raspios-trixie-arm64-lite.img.xz
Mac$ curl -LO https://downloads.raspberrypi.com/raspios_lite_arm64/images/raspios_lite_arm64-2026-10-06/2026-10-06-raspios-trixie-arm64-lite.img.xz.sha256
```

> A newer version may exist: see https://www.raspberrypi.com/software/operating-systems/ (*Raspberry Pi OS Lite*, 64-bit). Change the date in both links.

Check that the file is intact (not damaged during the download):

```
Mac$ shasum -a 256 -c 2026-10-06-raspios-trixie-arm64-lite.img.xz.sha256
```

```
2026-10-06-raspios-trixie-arm64-lite.img.xz: OK
```

Anything other than `OK`: delete the file and download it again.

Unpack it (about 3 GB):

```
Mac$ xz -dkc 2026-10-06-raspios-trixie-arm64-lite.img.xz > raspios.img
```

## 1.5 Write the card

> ⚠️ **This is the only dangerous moment of the whole guide.** The command below erases a whole disk. If you give it the wrong disk number, it erases your computer. Read twice.

Put the microSD card in the reader. Then list the **external** disks only:

```
Mac$ diskutil list external
```

```
/dev/disk4 (external, physical):
   #:                       TYPE NAME                    SIZE       IDENTIFIER
   0:     FDisk_partition_scheme                        *255.9 GB   disk4
...
```

Find the line with **`external, physical`** and the **size of your card** (255.9 GB for a 256 GB card). Its name here is `disk4`. **Yours may be different, and it can change from one day to the next: always read it again.** Below, replace `4` with your number.

Detach the card (without ejecting it):

```
Mac$ diskutil unmountDisk /dev/disk4
```

Write the image. Your Mac's password is asked; nothing appears while you type it, that's normal. Note the `r` in `rdisk4`: it makes the copy much faster.

```
Mac$ sudo dd if=$HOME/PrometheusImages/raspios.img of=/dev/rdisk4 bs=4m status=progress && sync && echo WRITE_OK
```

It takes about 1 min 30. It ends with something like:

```
3078619136 bytes transferred in 89.270230 secs
WRITE_OK
```

## 1.6 Add the two first-boot files

The card now has a small partition called `bootfs`. Mount it, copy the two files, check the copy, and eject:

```
Mac$ diskutil mount disk4s1
Mac$ cd ~/Downloads/Prometheus-Station-main
Mac$ cp installation/user-data installation/network-config /Volumes/bootfs/
Mac$ diff -q installation/user-data /Volumes/bootfs/user-data && diff -q installation/network-config /Volumes/bootfs/network-config && echo COPY_OK
Mac$ rm -f /Volumes/bootfs/._*
Mac$ diskutil eject /dev/disk4
```

You should see `COPY_OK`. The `rm` line deletes hidden files that macOS adds to every card; the Pi doesn't need them.

The card is ready. Next: [2. First boot →](02-first-boot.md)
