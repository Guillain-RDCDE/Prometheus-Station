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

## For the keeper: Settings (the gear, top right)

Protected by the password you chose in step 5.

**Content**
- **Encyclopedias**: for each collection, the installed version, and whether a newer one exists. **Update all** downloads the new versions (only with internet). Progress and remaining time are shown.
- **Messages**: how many there are, a link to the board, and **Delete all messages** (tap twice to confirm). Signed in, you can also delete messages one by one on the board.
- **Add files**: drag and drop books (EPUB, PDF) or encyclopedias (ZIM). They are sorted by themselves.

**Station**
- **Station Wi-Fi**: rename the open Wi-Fi. The e-ink screen follows.
- **Welcome board**: write the text visitors see when they tap the lighthouse. Five buttons format it: **T** title, **B** bold, *I* italic, U underline, • list. A live preview shows the result. Under the buttons, it is plain text: `# Title`, `## Subtitle`, `**bold**`, `*italic*`, `__underline__`, `- list item`. One language only: yours.
- **Colors**: six color themes (Ocean, Forest, Ember, Sun, Lavender, Night), for every page and every visitor.
- **Language**: same as the flags.

**System**
- **Software**: number of system updates waiting, **Update**, and **Restart** when an update needs it. Your settings are kept.
- **Storage**: how full the card is, and what takes the room, biggest first, each with a **Delete** button (tap twice). A deleted encyclopedia is no longer downloaded.
- **Energy**: low-power mode and automatic shutdown (see [step 9](09-power.md)).
- **Station health**: processor temperature, power supply (*Good*, *Too low right now*, *Has been too low*) and time since switch-on. Above 80 °C the Pi slows itself down: give it shade and air. A power supply that "has been too low" means the battery or its cable is too weak.
- **Backup**: download the latest settings backup, or make one now (see [step 11](11-backup.md)).

**Security**
- **Password**: change it (current one, then new one). This signs out every other device.

Every setting has a small **?** that unfolds a two-line explanation.

Next: [13. The crisis test →](13-crisis-test.md)
