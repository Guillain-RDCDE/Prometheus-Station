# 13. The crisis test

A station is only proven once it has worked **with no internet, no home Wi-Fi, on battery**. This is how we tested ours on 9 October 2026, without carrying it away from home.

## 13.1 Hide your home networks from the station

So that the station believes it is far from home, temporarily rename the networks it knows (it then can't find them):

```
Pi$ nmcli -g NAME con show | grep "^maison-" | while IFS= read -r c; do s=$(nmcli -g 802-11-wireless.ssid con show "$c"); sudo nmcli con mod "$c" 802-11-wireless.ssid "ABSENT-$s"; done
```

(For each network learned in step 7, it puts `ABSENT-` in front of its name.)

## 13.2 The test

1. Unplug the Pi (power **and** network cable). Wait 3 minutes (to test the clock).
2. Plug it into the **power bank only**. After about 2 minutes, the e-ink screen shows the QR code *Wi-Fi ouvert : Prometheus-Station*.
3. Put your phone in **airplane mode**, then switch **Wi-Fi only** back on: no mobile data, no internet.
4. Scan the QR code (or join **Prometheus-Station**). The home page **opens by itself**.
5. Try everything: search the encyclopedias, read a book, write a message, sign in to the Settings.

## What we saw

- The station opened its own Wi-Fi by itself ("no known network").
- **Time**: it started with the time of its last switch-off; the message written at 16:54 carried the right time, **before** the network cable came back: the phone had given it the time.
- All four tries worked.
- **The test found a bug**: 30 seconds after opening its Wi-Fi, the station cut it for 9 seconds to look for home. The 10-minute delay was counted from zero instead of from the opening. Fixed in `05-wifi-auto.sh`.
- After the fix, with nobody connected, the station went back **by itself** to the home Wi-Fi exactly 10 minutes later, as designed.

## 13.3 Put your networks back

```
Pi$ nmcli -g NAME con show | grep "^maison-" | while IFS= read -r c; do s=$(nmcli -g 802-11-wireless.ssid con show "$c"); sudo nmcli con mod "$c" 802-11-wireless.ssid "${s#ABSENT-}"; done
```

(It removes the `ABSENT-` again.)

Within 10 minutes, the station is back on your home Wi-Fi.

## Not tested yet

- several phones at the same time;
- a full battery discharge;
- the firewall and phone isolation (step 10) seen from a phone on the station's Wi-Fi;
- the automatic shutdown with its message on the screen.

Next: [14. Troubleshooting →](14-troubleshooting.md)
