# 14. Troubleshooting

Everything below actually happened while building the station.

## "REMOTE HOST IDENTIFICATION HAS CHANGED" when connecting

After a reinstall, the Pi has a new identity and your computer refuses to trust it. Forget the old one:

```
Mac$ ssh-keygen -R prometheus-station.local
Mac$ ssh-keygen -R 192.168.2.2
```

## The Wi-Fi chip says `unavailable`

The Wi-Fi country is not set. Step 3 sets it; check with `nmcli radio wifi`. To set it by hand (replace `FR` with your country):

```
Pi$ sudo raspi-config nonint do_wifi_country FR
```

## A program refuses to start with `Exec format error`

During our build, the Pi restarted by itself **in the middle of copying** the installation folder: several files arrived **empty**, and a program installed from them could not start. Since then, every copy is checked (step 2.4), and long steps are run as a background job of the Pi (step 2.5). The likely cause was a too-weak USB power supply during heavy downloads.

The system log now survives a restart, so after any unexpected restart you can read what happened before it:

```
Pi$ journalctl -b -1 -e
```

## The downloads seem stuck, or "Checksum error detected"

- `[ERROR] Checksum error detected` at the start of a file is normal (see step 4).
- Follow them: `journalctl -fu prometheus-telechargement`.
- After a power cut, they resume by themselves 5 minutes after the restart.
- To wait for the end of the downloads in a script, don't use `systemctl is-active`: while downloading, the service is *activating*, not *active*. Use `systemctl show -p ActiveState --value prometheus-telechargement` and wait for `inactive`.

## The e-ink screen stays blank, or `GPIO busy`

- Wrong version of the driver: see step 8.
- `lgpio.error: 'GPIO busy'`: two programs are using the screen at once. Stop the service before any test (`sudo systemctl stop prometheus-ecran`), start it again after.

## Forgot the settings password

```
Pi$ sudo prometheus-mot-de-passe
```

Then open the Settings: the page lets you choose a new one.

## Locked out after the firewall

Wait 5 minutes: the safety net switches it off (step 10). If you had already confirmed, plug the network cable between the Pi and your computer: SSH is always allowed through the cable.

## The station doesn't go back to the home Wi-Fi

It only checks every **10 minutes**, and only when nobody is connected to its own Wi-Fi. Wait, or restart it.

## Something else

Each service has its own log. The main ones:

| Service | What it is |
|---|---|
| `prometheus-kiwix` | the encyclopedias |
| `prometheus-telechargement` | the downloads |
| `prometheus-admin` | password, settings, messages |
| `prometheus-wifi-auto` | home Wi-Fi / station Wi-Fi |
| `prometheus-ecran` | the e-ink screen |
| `prometheus-tension` | clean shutdown on weak power |
| `prometheus-extinction` | automatic shutdown without visitors |
| `nginx` | the web pages |

```
Pi$ systemctl status prometheus-kiwix
Pi$ journalctl -u prometheus-kiwix -e
```

Back to the [guide index](README.md).
