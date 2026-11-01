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
- Dropping a card on an occupied spot lays it on top (a force on a card, Glacier
  on a permanence). The coloured edge on each card shows whose card it is.
- **Void (n)** opens a void; both players see both voids. Cards can be dragged
  back out.
- World points, rounds won, the round number and whose turn it is are all set
  by hand. **Random opener** picks who opens.
- **Reset game** clears the table, voids and counters for both players, and
  both choose a binder again.
- **B** opens and closes your binder; **L** shows the log of every action.

Without a room, the page runs in **solo mode**: you play both seats and
**Switch seat** changes which binder you see.

## Updating the cards

Cards come from `data/card-pool.md`, a copy of `design/card-pool.md` in the
project. After the card pool changes:

```sh
node scripts/sync-cards.mjs   # card-pool.md -> data/cards.json
```

The script reads everything above the first `---` line and recognises tables by
their headers: the commons table (`Element | Numbers | Cards`), numbered tables
(`No. | Card | Tags | Effect`), the force table (`No. | Permanence | Force |
Rarity | Duration | …`) and the pinnacles paragraph. It warns instead of
guessing when something doesn't fit.

## Test binders

`data/binders.json` lists ready-made binders by card number. Add a number to a
binder's `originals` to mark that card as an original.

## Files

| Path | What it is |
| --- | --- |
| `index.html`, `css/`, `js/` | The page. No build step. |
| `js/state.js` | The shared table and every action on it. |
| `js/net.js` | The browser-to-browser link (PeerJS). |
| `vendor/peerjs.min.js` | PeerJS 1.5.5. |
| `data/` | Card pool, generated card data, test binders. |
| `scripts/` | Card sync and state tests (`node scripts/test-state.mjs`). |

To run it locally: `python3 -m http.server 8080`, then open
<http://localhost:8080>. Adding `?peerhost=127.0.0.1&peerport=9000` points the
page at a local PeerJS broker for testing.
