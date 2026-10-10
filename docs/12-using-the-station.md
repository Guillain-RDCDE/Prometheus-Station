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

At the top, a **status card**: the station's name, how many people are connected, the temperature, how long it has been on, and whether the power supply is good (the card turns orange if it is too hot or the power is weak). Tap it for details.

*People connected*: on the station's Wi-Fi, the phones joined to it; at home, the devices with a station page open in the last 3 minutes.

Below, the settings are grouped by who they are for. The community features (announcement, emergency page, find your loved ones, mutual aid) are **all off at first**.

**For visitors**
- **Welcome board**: write the text visitors see when they tap the lighthouse. Five buttons format it: **T** title, **B** bold, *I* italic, U underline, • list. A live preview shows the result. Under the buttons, it is plain text: `# Title`, `## Subtitle`, `**bold**`, `*italic*`, `__underline__`, `- list item`. One language only: yours.
- **Announcement**: the message (200 characters at most), its colour (*Information*, *Important*, *Urgent* — urgent pulses), scrolling or still text, scrolling speed, and **Also on the station's screen**: on the e-ink screen, the announcement takes the place of the instructions next to the QR code (3 lines at most).
- **Emergency page**: on/off.
- **Find your loved ones**: on/off, whether to ask *where*, how many entries, a link to the register, **Delete all entries** (tap twice). Signed in, you can also delete entries one by one.
- **Mutual aid**: on/off, which categories are offered, how long posts stay visible (1, 3 or 7 days, or no limit), how many posts, **Delete all posts**.
- **Messages**: how many there are, a link to the board, and **Delete all messages** (tap twice to confirm). Signed in, you can also delete messages one by one on the board.
- **Poster to print**: an A4 poster in French and English — "Free Wi-Fi", a large QR code that joins the station's Wi-Fi, the network's name, the address, and what visitors will find (it follows the features you turned on). Open it on your phone and print it from the browser's menu.

**Content**
- **Encyclopedias**: for each collection, the installed version, and whether a newer one exists. **Update all** downloads the new versions (only with internet). Progress and remaining time are shown.
- **Most searched topics**: the articles most often opened from the encyclopedia search, with how many times (only the title and a count are kept, nothing about who read them). **Pin** up to 8 of them: they appear in small on the home page under *Often searched here*, one tap from the article. A button resets the counts; pinned topics stay.
- **Add files**: drag and drop books (EPUB, PDF) or encyclopedias (ZIM). They are sorted by themselves.
- **Storage**: how full the card is, and what takes the room, biggest first, each with a **Delete** button (tap twice). A deleted encyclopedia is no longer downloaded.

**Station**
- **Station Wi-Fi**: rename the open Wi-Fi. The e-ink screen follows.
- **Energy**: low-power mode and automatic shutdown (see [step 9](09-power.md)).
- **Station health**: processor temperature, power supply (*Good*, *Too low right now*, *Has been too low*), time since switch-on and people connected. Above 80 °C the Pi slows itself down: give it shade and air. A power supply that "has been too low" means the battery or its cable is too weak.
- **Software**: number of system updates waiting, **Update**, and **Restart** when an update needs it. Your settings are kept.
- **Backup**: download the latest settings backup, make one now, or **restore one**: choose the file, tap twice, and the station puts the settings back and restarts (see [step 11](11-backup.md)).

**Appearance**
- **Colors**: six color themes (Ocean, Forest, Ember, Sun, Lavender, Night), for every page and every visitor.
- **Language**: same as the flags.

**Security**
- **Password**: change it (current one, then new one). This signs out every other device.
- **Erase what visitors wrote**: deletes in one go the message board, the register of people and the mutual-aid posts, however many there are. It shows how many of each will go, then asks a second time in a red box (*Yes, erase it all* or *Cancel*). Settings, your announcement, the welcome board and the books are not touched. It cannot be undone.

**Restart** and **Switch off** (two buttons at the bottom of the Settings): tap twice. *Restart* brings the station back by itself after about two minutes. *Switch off* shuts it down cleanly and the e-ink screen says so; to switch it back on, unplug the battery and plug it in again.

Most settings have a small **?** that unfolds a short explanation.

Next: [13. The crisis test →](13-crisis-test.md)
