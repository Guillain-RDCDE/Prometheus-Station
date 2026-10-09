# 4. Encyclopedias

Script: [`installation/02-encyclopedies.sh`](../installation/02-encyclopedies.sh)

The encyclopedias come from **[Kiwix](https://www.kiwix.org)**, a project that packs whole websites (Wikipedia, medical guides...) into single `.zim` files that can be read without internet.

## 4.1 Choose the content (before running the script)

The script downloads this list, smallest first:

| Name in the list | Content | Size (Oct. 2026) |
|---|---|---|
| `zimgit-water_en` | drinking water | < 0.1 GB |
| `zimgit-food-preparation_en` | food | 0.1 GB |
| `zimgit-post-disaster_en` | after a disaster | 0.6 GB |
| `wikem_en_all_maxi` | WikEM, emergency medicine | 0.4 GB |
| `mdwiki_en_all_maxi` | MDWiki, medicine | 2.3 GB |
| `ifixit_fr_all` | iFixit repair guides (French) | 3.7 GB |
| `wikipedia_fr_all_maxi` | Wikipedia in French, with images | 55 GB |
| `gutenberg_fr_all` | Project Gutenberg, free French books | 11 GB |
| `wikipedia_en_all_maxi` | Wikipedia in English, with images | 127 GB |

Total: about **200 GB**. On a 256 GB card, about 34 GB stay free.

**Smaller card, or other languages?** Open `installation/02-encyclopedies.sh` on your Mac and edit the list between `cat > /srv/prometheus/contenus.txt` and `EOF`: one name per line, **without date**. Every available name is on https://library.kiwix.org (for example `wikipedia_es_all_maxi` for Spanish). With 128 GB, remove `wikipedia_en_all_maxi`. Copy the folder to the Pi again (step 2.4) after editing.

## 4.2 Run it

```
Pi$ cd ~/installation
Pi$ sudo bash 02-encyclopedies.sh
```

The downloads start right away, in the background. Follow them:

```
Pi$ journalctl -fu prometheus-telechargement
```

```
>> wikipedia_fr_all_maxi_2026-05.zim : telechargement...
...
OK wikipedia_fr_all_maxi_2026-05.zim
```

`telechargement` means downloading; `OK` means the file is complete and checked. Press **Ctrl + C** to stop watching (the download goes on).

> A line `[ERROR] Checksum error detected` at the start of each file is **normal**: the tool checks a still-empty file before downloading it. What counts is the `OK` line at the end.

We measured about 7 to 10 MB/s, so **about 7 hours** for everything. You can carry on with the next steps meanwhile.

## What the script sets up

- **A system user `prometheus`** that runs all the station's services. The files live in `/srv/prometheus/`.
- **Kiwix** (the Debian package, version 3.7), as the service `prometheus-kiwix`. It only listens to the station itself; visitors reach it through the web pages of step 5, at `/encyclopedies`. Each collection is also reachable without its date (`wikipedia_fr_all_maxi` instead of `wikipedia_fr_all_maxi_2026-05`), so links survive updates.
- **`prometheus-telecharger`**, the downloader:
  - it always fetches the **newest version** of each content (Kiwix offers links without a date that point to the latest file);
  - it uses several mirrors and **checks every file** against Kiwix's checksum;
  - it **resumes** where it stopped after a power or network cut;
  - it deletes the old version only once the new one is complete;
  - it **refuses to start** a file if less than 5 GB would remain free.
- **A timer** that runs the downloader 5 minutes after each start, then once a day. When a new Wikipedia comes out, the station fetches it by itself whenever it has internet. Without internet, it does nothing.
- **`prometheus-catalogue`**, which rebuilds the list of encyclopedias that Kiwix reads, after each download.

## Check

```
Pi$ ls -lh /srv/prometheus/encyclopedies
```

Finished files end in `.zim`. A file still being downloaded has a companion ending in `.zim.aria2`.

Next: [5. Web portal and Wi-Fi →](05-portal-and-hotspot.md)
