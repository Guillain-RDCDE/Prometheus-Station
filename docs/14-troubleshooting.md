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
- Follow them: `journalctl -fu prometheus-telechargement`. When a download ends, the service recomputes what the Settings show (`prometheus-etat`, run by the service itself): the Encyclopedias page no longer stays on *in progress*.
- After a power cut, they resume by themselves 5 minutes after the restart.
- To wait for the end of the downloads in a script, don't use `systemctl is-active`: while downloading, the service is *activating*, not *active*. Use `systemctl show -p ActiveState --value prometheus-telechargement` and wait for `inactive`.

## The e-ink screen stays blank, or `GPIO busy`

- Wrong version of the driver: see step 8.
- `lgpio.error: 'GPIO busy'`: two programs are using the screen at once. Stop the service before any test (`sudo systemctl stop prometheus-ecran`), start it again after.
- The screen is turned off in *Settings › Screen and keyboard › Small e-ink screen*: turn it back on.

## Adding a book fails with "error 500"

Fixed in November 2026: on stations installed before, every file over 1 MB failed (only small EPUBs went through). The password check applied the web server's default 1 MB limit to the upload. Run step 3 again (`sudo bash 03-wifi-accueil.sh`), or add `client_max_body_size 0;` inside `location = /_auth` in `/etc/nginx/sites-available/prometheus`, then `sudo systemctl reload nginx`. The web server's log says it plainly: `client intended to send too large body ... subrequest: "/_auth"`.

## Books sent several at once stay unsorted

Fixed in November 2026: the sorting program runs once per file received; with many files in a row, the system stopped it after 5 runs in 10 seconds (`start-limit-hit`) and the next files stayed in `/srv/prometheus/depot/`. On stations installed before, run step 3 again, or add `StartLimitIntervalSec=0` under `[Unit]` in `/etc/systemd/system/prometheus-ranger.service`, then:

```
Pi$ sudo systemctl daemon-reload
Pi$ sudo systemctl reset-failed prometheus-ranger.service prometheus-ranger.path
Pi$ sudo systemctl start prometheus-ranger.path
```

The waiting files are sorted at once.

## How long did the batteries last?

With the X728 battery board ([step 9](09-power.md#90-the-battery-case-x728)), nobody needs to watch: `sudo prometheus-batterie --bilan` tells when the station went on batteries, whether it shut down cleanly, the last reading and the battery life. The raw record is `/var/lib/prometheus-batterie/journal.csv`.

## The station is not on time

Check where the time came from: `cat /run/prometheus-heure` (`carte` = the X728 board's clock, `radio` = radios heard), and `ls /run/systemd/timesync/synchronized` (exists = internet time). Then `journalctl -u prometheus-horloge -b` (start: *mise a l'heure de la carte*) and `journalctl -u prometheus-horloge-radio`. If the board's clock says *pas encore reglee* (a new board, or its cells were removed), it gets the time back the next time the station has internet. Order of the sources: [step 5](05-portal-and-hotspot.md#the-clock).

## Forgot the settings password

```
Pi$ sudo prometheus-mot-de-passe
```

Then open the Settings: the page lets you choose a new one.

## Locked out after the firewall

Wait 5 minutes: the safety net switches it off (step 10). If you had already confirmed, plug the network cable between the Pi and your computer: SSH is always allowed through the cable.

## The station doesn't go back to the home Wi-Fi

It only checks every **10 minutes**, and only when nobody is connected to its own Wi-Fi. Wait, or restart it.

## A button does nothing, a folder is "permission denied"

Who owns each folder of the station, and who may write in it, is in one table, applied at every start and at the end of every installation step. To apply it now:

```
Pi$ sudo systemd-tmpfiles --create /etc/tmpfiles.d/prometheus.conf
```

Each button of the Settings drops a numbered order; the station's answer is in `/var/www/prometheus/ajouter/resultats/` (`fait` done, `lance` started, `attente` waiting for another radio operation, `refuse` refused, with the reason). The log of the service that carries them out: `journalctl -u prometheus-commande`.

## Checking the code after a change

From the repository, on a Mac, a Linux computer or the station itself:

```
$ bash tests/lancer.sh
```

It runs every test: the shared module, the radio without a radio plugged in, every address of the settings server (logged in or not, compared with `tests/reference/admin.json`), the buttons' orders (Linux), and each page in a real browser when Chrome is there. It ends with `TOUT EST BON` ("all good") or lists what failed. GitHub runs it on every change.

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
| `prometheus-batterie` | the X728 battery board: charge, time left, clean shutdown when the cells run low, its button |
| `prometheus-horloge` | the X728 board's clock: the time at start, internet time copied into it (also `prometheus-horloge-ecrire.timer`, every hour) |
| `prometheus-horloge-radio` | the time from the radios heard, when there is neither internet nor board clock |
| `prometheus-extinction` | automatic shutdown without visitors |
| `prometheus-radio` | the radio, Meshtastic or MeshCore *(phase 2)*: see [chapter 16](16-radio-message-board.md#troubleshooting) |
| `prometheus-radio-outil` | the radio tool behind the Mesh section (network switch, software, backups, workshop): see [chapter 17](17-radio-page.md#troubleshooting) and [chapter 18](18-mesh-section.md#troubleshooting) |
| `prometheus-maj-systeme` | a system update started from *Settings › Software*; its details are also shown on that page |
| `prometheus-nom` | applies a new station address (`<name>.local`) |
| `nginx` | the web pages |

```
Pi$ systemctl status prometheus-kiwix
Pi$ journalctl -u prometheus-kiwix -e
```

Back to the [guide index](README.md).
