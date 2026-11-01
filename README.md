# The First Contest · playtest table

A browser table for playtesting one contest between two people, at one link,
with no download and no accounts. Like Cockatrice, the page knows where every
card is but doesn't enforce rules: players apply card effects by moving cards,
and count world points themselves on the manual counters.

## Playing

1. Open the page and press **Host a contest**. Copy the invite link and paste it
   in Discord.
2. Your friend opens the link. Your two browsers connect directly to each other.
3. Each of you chooses a ready-made test binder. Your binder is only in your own
   browser; the other player sees only how many cards are left in it.
4. Play by clicking a card in your binder, then a spot on the table, or by
   dragging it there. It goes down on the face it's showing; **↻** flips it.

On the table:

- **Hover** any card to see it full size with its other face.
- **Right-click** a card to flip it, send it to its owner's void or return it to
  its owner's binder. Keys while hovering: **F** flip, **V** void, **R** return.
- **Made a mistake?** Drag one of your cards from the table (or a void) back
  onto your binder, or onto the **Open binder** button when it's closed.
- Dropping a card on an occupied spot lays it on top (a force on a card, Glacier
  on a permanence). The coloured edge on each card shows whose card it is.
- **Void (n)** opens a void; both players see both voids. Cards can be dragged
  back out.
- **Played R1 3/10** in each player's header counts the cards they've played
  from their binder this round, against the round's **Cap** (10 by default;
  change it beside the round number for cards like Verge). It turns amber at
  the cap and red past it. Taking back your own card (dragging it to your
  binder, or **Take back** on right-click) un-counts it; a card returned by a
  card effect still counts. **−** and **+** correct it by hand.
- World points, rounds won, the round number and whose turn it is are all set
  by hand. **Random opener** picks who opens.
- **Reset game** clears the table, voids and counters for both players, and
  both choose a binder again.
- **B** opens and closes your binder; **L** shows the log of every action.

Without a room, the page runs in **solo mode**: you play both seats and
**Switch seat** changes which binder you see.

## Updating the cards and binders

Cards and test binders both come from `data/card-pool.md`, a copy of
`design/card-pool.md` in the project. After the card pool changes:

```sh
node scripts/sync-cards.mjs   # card-pool.md -> data/cards.json + data/binders.json
```

How it reads the file:

- **Only the most recent pass is used.** The card pool puts its newest pass at
  the top, so the script reads the first `## ` section that defines cards and
  stops at the next `## ` heading. Every older pass is ignored.
- Tables are recognised by their header rows: full two-faced cards (`No. |
  Permanence | Rarity | Affinities | Permanence text | Force | Duration | Force
  text`), force-only tables, the one-affinity commons table (`Element | Numbers
  | Cards`), permanence-only tables (`No. | Card | Tags | Effect`), meta cards
  (`Card | Text` after a "Fifth-pillar meta…" line) and the pinnacles
  paragraph.
- Binders come from bullets like `- **Binder A, Tides.** Description. Ocean,
  Archipelago, …` and are matched to cards by name.

### Card faces

The cards on the table are the faces drawn on the Card Anatomy canvas, copied
as they are, art included:

```sh
node scripts/sync-card-art.mjs <folder with the canvas's canvas.json and boards>
```

It uses only the canvas boards whose title starts with the newest pass's name
("Second pass: …"), matches every 320×448 face to a card by the name at its
top, and writes `data/card-faces.json`. A card the canvas hasn't drawn yet is
shown in the same carved-stone layout with a blank art panel.

Meta cards have one face and no number. To mark a card in a binder as an
original, add its id (the card number, or `meta-<name>`) to that binder's
`originals` in `data/binders.json`; note that the next sync rewrites that file.

## Files

| Path | What it is |
| --- | --- |
| `index.html`, `css/`, `js/` | The page. No build step. |
| `js/state.js` | The shared table and every action on it. |
| `js/net.js` | The browser-to-browser link (PeerJS). |
| `vendor/peerjs.min.js` | PeerJS 1.5.5. |
| `data/` | Card pool, generated card data and binders, card faces from the canvas. |
| `scripts/` | Card sync and state tests (`node scripts/test-state.mjs`). |

To run it locally: `python3 -m http.server 8080`, then open
<http://localhost:8080>. Adding `?peerhost=127.0.0.1&peerport=9000` points the
page at a local PeerJS broker for testing.
