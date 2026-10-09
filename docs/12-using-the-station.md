# 12. Using the station

Nothing here needs a command: everything happens in a phone or computer browser.

## Joining

- **Phone**: join the **Prometheus-Station** Wi-Fi (or scan the QR code on the e-ink screen). The home page opens by itself. If it doesn't, open any web address.
- **At home**, when the station is on your home Wi-Fi: http://prometheus-station.local/ (or the address shown on the e-ink screen).

## For every visitor

| Page | What you do there |
|---|---|
| **Encyclopedias** | type a subject: results come from every collection at once. Tap one to read it; the round magnifier brings you back to the search |
| **Library** | the list of books; tap one to read it (EPUB pages turn, PDFs open) |
| **Messages** | write a message (500 characters at most), with your name if you want. Newest at the bottom, each with its full date and time. One message every 20 seconds per device |
| **The lighthouse** (logo), or *About and rules* | the welcome board written by the station's keeper |
| **Flags** | French or English, for this phone only |

Three more doors appear only if the keeper turns them on (see *Community* below):

| Page | What you do there |
|---|---|
| **Emergency** (red, at the top) | large buttons — cardiac arrest, bleeding, choking, burn, fracture, stroke, severe allergy, hypothermia, heat stroke, dehydration, snakebite, safe water… — each opens the right article at once: Wikipedia in French, MDWiki in English |
| **Find your loved ones** | say *I am safe* or *I am looking for someone* (name, where, a message), and search the register by name — accents and capitals don't matter. Your phone remembers your entries, so you can delete them |
| **Mutual aid** | post what you need or what you can offer, by category (water, food, health, shelter, power, transport, tools, skills, other), with where to find you; filter by type and category. Posts disappear by themselves after the chosen time |

When the keeper publishes an **announcement**, it scrolls in a coloured band at the top of every page, encyclopedia articles included. Tap it to stop it and read it whole.

## For the keeper: Settings (the gear, top right)

Protected by the password you chose in step 5.

**Content**
- **Encyclopedias**: for each collection, the installed version, and whether a newer one exists. **Update all** downloads the new versions (only with internet). Progress and remaining time are shown.
- **Messages**: how many there are, a link to the board, and **Delete all messages** (tap twice to confirm). Signed in, you can also delete messages one by one on the board.
- **Add files**: drag and drop books (EPUB, PDF) or encyclopedias (ZIM). They are sorted by themselves.

**Community** — all off at first
- **Announcement**: the message (200 characters at most), its colour (*Information*, *Important*, *Urgent* — urgent pulses), scrolling or still text, scrolling speed, and **Also on the station's screen**: on the e-ink screen, the announcement takes the place of the instructions next to the QR code (3 lines at most).
- **Find your loved ones**: on/off, whether to ask *where*, how many entries, a link to the register, **Delete all entries** (tap twice). Signed in, you can also delete entries one by one.
- **Mutual aid**: on/off, which categories are offered, how long posts stay visible (1, 3 or 7 days, or no limit), how many posts, **Delete all posts**.
- **Emergency page**: on/off.

**Station**
- **Poster to print**: an A4 poster in French and English — "Free Wi-Fi", a large QR code that joins the station's Wi-Fi, the network's name, the address, and what visitors will find (it follows the features you turned on). Open it on your phone and print it from the browser's menu.
- **Station Wi-Fi**: rename the open Wi-Fi. The e-ink screen follows.
- **Welcome board**: write the text visitors see when they tap the lighthouse. Five buttons format it: **T** title, **B** bold, *I* italic, U underline, • list. A live preview shows the result. Under the buttons, it is plain text: `# Title`, `## Subtitle`, `**bold**`, `*italic*`, `__underline__`, `- list item`. One language only: yours.
- **Colors**: six color themes (Ocean, Forest, Ember, Sun, Lavender, Night), for every page and every visitor.
- **Language**: same as the flags.

**System**
- **Software**: number of system updates waiting, **Update**, and **Restart** when an update needs it. Your settings are kept.
- **Storage**: how full the card is, and what takes the room, biggest first, each with a **Delete** button (tap twice). A deleted encyclopedia is no longer downloaded.
- **Energy**: low-power mode and automatic shutdown (see [step 9](09-power.md)).
- **Station health**: processor temperature, power supply (*Good*, *Too low right now*, *Has been too low*) and time since switch-on. Above 80 °C the Pi slows itself down: give it shade and air. A power supply that "has been too low" means the battery or its cable is too weak.
- **Backup**: download the latest settings backup, make one now, or **restore one**: choose the file, tap twice, and the station puts the settings back and restarts (see [step 11](11-backup.md)).

**Security**
- **Password**: change it (current one, then new one). This signs out every other device.

**Switch the station off** (red button at the bottom of the Settings): tap twice. The station shuts down cleanly a few seconds later and the e-ink screen says so. To switch it back on, unplug the battery and plug it in again.

Most settings have a small **?** that unfolds a short explanation.

Next: [13. The crisis test →](13-crisis-test.md)
