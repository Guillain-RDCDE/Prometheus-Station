# 6. Remote access (optional)

Script: [`installation/04-tailscale.sh`](../installation/04-tailscale.sh)

**[Tailscale](https://tailscale.com)** links your devices together through internet as if they were on the same network, with nothing to configure on your router. When the station has internet (at home, or at a friend's), you can repair it from anywhere.

It needs a free Tailscale account.

```
Pi$ cd ~/installation
Pi$ sudo bash 04-tailscale.sh
```

The script prints a link starting with `https://login.tailscale.com/a/...`. Open it in a browser and sign in to your Tailscale account. The script then prints the station's Tailscale address (`100.x.y.z`).

> If you reinstall the station, first delete the old `prometheus-station` machine in https://login.tailscale.com/admin/machines; otherwise the new one is called `prometheus-station-1`.

From any device signed in to the same Tailscale account:

```
Mac$ ssh pi@100.x.y.z
```

Without internet, Tailscale simply waits; the station works the same.

Next: [7. Automatic Wi-Fi →](07-automatic-wifi.md)
