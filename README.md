# The First Contest · playtest table

A browser table for playtesting one contest, at one link, with no download and no
accounts. The **Friend / Computer** switch in the top bar picks who you play:

- **Friend:** like Cockatrice, the page knows where every card is but doesn't enforce
  rules. Players apply card effects by moving cards and count world points themselves
  on the manual counters.
- **Computer:** the rules engine applies every card and the computer plays the other
  seat (see *Playing against the computer* below). `index.html?vs=computer` opens
  straight to it.

## Playing

1. Open the page and press **Host a contest**. Copy the invite link and paste it
   in Discord.
2. Your friend opens the link. Your two browsers connect directly to each other.
3. Each of you chooses a ready-made test binder. Your binder is only in your own
   browser; the other player sees only how many cards are left in it.
4. Play by clicking a card in your binder, then a spot on the table, or by
   dragging it there. It goes down on the face it's showing; **↻** flips it.

On the table:

- Each player's area is an open grid (10 spots across, 3 down) that cards snap
  to; only its faint edge and a **dotted 2×2 in the top-left corner** are drawn.
  The 2×2 shows what a complete world looks like; it isn't a slot, and there's
  no limit on how many worlds you make. The spot under the pointer lights up
  while you're placing a card. Your area is at the bottom, the other player's
  at the top, and the log says what each new card sits next to.
- **Hover** any card to see it full size with its other face.
- **Right-click** a card to flip it, send it to its owner's void or return it to
  its owner's binder. Keys while hovering: **F** flip, **V** void, **R** return.
- **Made a mistake?** Drag one of your cards from the table (or a void) back
  onto your binder, or onto the **Binder** button when it's closed.
- Dropping a card on an occupied spot lays it on top (a force on a card, Glacier
  on a permanence). The coloured ring on each card shows whose card it is.

The **scoreboard** between the two boards holds every counter. Each has a small
up and down arrow beside it.

- **Played 3/10** counts the cards each player has played from their binder this
  round, against the round's **Cap** (10 by default; lower it for cards like
  Verge). It turns amber at the cap and red past it, and its tooltip lists
  earlier rounds. Taking back your own card un-counts it; a card returned by a
  card effect still counts.
- **World pts** and **Rounds** are set by hand.
- **Void** shows how many cards are in each player's void; click it to look
  (both players see both voids). Drop a card on it to send that card to its
  owner's void; dropping one straight from your binder plays it there, for a
  force that happens once.
- **Round** and **Cap**, the die (picks who opens at random), and **End turn** /
  **Pass** for whoever is to play sit in the middle. The row of the player to
  play is highlighted.

In the top bar, **Binder** (or **B**) opens and closes your binder, **Log** (or
**L**) shows every action, and **Reset** clears the table, voids and counters
for both players so both choose a binder again.

Without a room, the page runs in **solo mode**: you play both seats and
**Switch seat** changes which binder you see.

## Playing against the computer

Choose **Computer** in the top bar (on a table without a room). It's the same table,
binder and scoreboard, but the page plays by the rules, with the newest card pool (the
third pass) and its five test binders (Tides, Embers, Gales, Roots and the even
Compass; no pinnacles, Origin or the Gap):

1. In the binder panel, choose your binder and the computer's, then **Start the
   contest**. The opener is random.
2. Click a card in your binder to play the side it's showing; the tabs down the right
   edge (or **F**) turn every card over, **↻** flips one. If only its other side can be
   played, you're offered that one. Then click a highlighted spot, card or world, or a
   button in the scoreboard's prompt row. **Esc** or **Cancel** backs out. **Pass for
   the round** when you're done.
3. Your worlds are at the bottom, the computer's at the top, each labelled with its
   world points. A lasting force played on a card is tucked under that card's corner;
   one on a world sits by the world's label, and every lasting force is listed under
   **In play**. When an effect has changed a card's affinities, a small strip on the
   card shows what it has right now. The computer's newest plays glow.
4. Hover any card to see both faces larger. **Log** shows every play; click a **Void**
   to look inside.

The page counts everything: world points per world, the tie-break, the 10-card cap,
round wins, and the Nov 2 test rule (a world worth 3 world points wins the contest at
once). A contest survives a reload, and switching to **Friend** and back keeps both
tables. Everything runs in your browser; nothing is sent anywhere. (The old
`play.html` link now opens this.)

Computer styles for the simulator (Nov 8, `STYLES` in `js/game/ai.js`): plain (the table's
computer), builder (one big world, toward the Perfect World), stacker (the tie-break), breaker
(tears down the other side), turtle (builds its own; crude, since it doesn't value protection
itself) and chaser (its win and scoring cards). `--quick` drops the reply lookahead, about 6x
faster, for wide screens. The win-condition numbers can be changed per contest
(`newContest(..., { knobs })`; the table uses the defaults in `KNOBS`).

The computer doesn't see your binder (since Nov 7): it knows how many cards are in it and
every card you've shown, and guesses the rest. At the start of each round it sets a card
budget for the round and holds some of its strong cards back for later rounds.

The rules live in `js/game/rules.js` and the opponent in `js/game/ai.js`. The same
files run in node:

```sh
node scripts/test-rules3.mjs     # rule checks on hand-built tables
node scripts/sim3.mjs 4          # computer v computer, every pairing of the five binders
node scripts/sim3.mjs 1 --log    # and print one contest per pairing, play by play
node scripts/sim3-pair.mjs 500 --a Tides --b Embers --seed 1107 --json out.json
                                 # one pairing, random opener: wins, how contests end,
                                 # cards left in each binder, plays and the cap by round,
                                 # world sizes, and how often each card gets played, by round
node scripts/sim3-pair.mjs 500 --open             # open worlds: no cap on world size
node scripts/sim3-pair.mjs 41 --seed 1108 --open --show 40   # replay one contest, play by play
node scripts/sim3-pair.mjs 250 --bo1 --nocap --open --aiA bigWorld=2 --aiB bigWorld=2
                                 # one round, no card cap, open worlds, computers aiming
                                 # for the 3-point world (Nov 7)
node scripts/sim3-rate.mjs 4000 --bo1 --nocap --open --quick --json r.json --csv r.csv
                                 # card ratings (Nov 8): random legal binders (14/7/4, leaning
                                 # none, one or two elements), computer styles drawn at random,
                                 # every card rated against an average card of its rarity, plus
                                 # results by lean, element and style; uses every processor
node scripts/sim3-sweep.mjs --knob archipelagoWater=8,10,12 --bo1 --nocap --open --quick
                                 # one win-condition number over a few values on the same
                                 # contests, stopping once each is known to ±3 points
                                 # (knobs: archipelagoWater, mountainPer, cradleEach, perfectWorld)
node scripts/sim3-field.mjs 250 --bo1 --nocap --open --ai bigWorld=2 --json a.json
                                 # a field: each side picks a binder at random every
                                 # contest (Tides, Embers, Gales, Roots; --binders to change);
                                 # --from a.json,b.json summarizes saved runs together
node scripts/sim3-pair.mjs 150 --aiB plan=0       # one side's computer without the round plan
                                 # (hidden=0: sees the other binder, as before Nov 7)
```

### Rule readings

Where a card's text leaves a question open, the engine picks one reading (marked
`READING` in `js/game/rules.js`):

- "With one affinity" means one ring printed on the card; an either-or capsule and a
  wildcard each count as one. Mirage and Cradle have none.
- "A fire permanence" means a permanence showing fire right now, after effects.
- A force has its card's printed elements (both, for an either-or); a wildcard gives
  none. "Ignores … forces" ignores them entirely, helpful or not.
- "Return" isn't "remove", so "can't be removed" doesn't stop a return.
- "Move" goes to another existing world of the card's owner; "becomes its own world"
  starts a new one. A split cuts a world down the middle (left from right, or top from
  bottom). Canyon stops splits (Tremor, Typhoon, Earthquake, Hurricane, Jet Stream),
  not single cards leaving.
- Hurricane ("Rearrange a player's worlds") scatters every world of the chosen player
  into worlds of one.
- Heat Shimmer and Mirage copy printed affinities. Element changes from permanence
  happen first, then lasting forces in the order they were played; losing affinities
  comes last.
- Ice Sheet blanks every fire permanence, both players'.
- Echo's card from the void doesn't count toward the 10; Verge's two plays do.
  "Play another fire card" means a card with fire on it, played on either face.
- Calm stops force faces (from the binder or through Echo) for both players for the
  rest of the round. Whiteout lasts until its player's next turn starts.
- Ebb removes the most recent common the opponent played this round that's still on
  the table, a lasting force included.
- Archipelago (10 water since Nov 7) and Cradle are checked at the start of their owner's
  turns, so not after they pass. A drawn round counts for both players; openers alternate.
- One round and no cap (the simulator's `--bo1` and `--nocap`, Nov 7): the round's winner
  wins the contest, and a player can play down to their last card. Passing stays, as a way
  to stop (a concession, in effect). With no cap the computer never passes just because
  it's ahead.
- Open worlds (the simulator's `--open`, Nov 7; the table keeps 2×2): a world is any
  connected shape of cards, lines included, on an 11×11 grid with no size cap. A split
  cuts the shape's bounding box down the middle. Placing offers one cell per set of
  neighbours the card would touch, the one nearest the world's middle.
- Equinox returns three cards of your choice from your void (all of them if there are
  three or fewer); it goes to the void itself afterwards.
- The eight conversion commons (Updraft, Brushfire, Shower, Current, Rockfall, Dust
  Devil, Riptide, Dry Wind) reach a permanence of any size showing the named element.
  Until the round ends it has a single affinity of the new element, however many it
  printed: a three-affinity card becomes one earth. Flare-up removes a common force
  from the table, ending its effect.
- "Becomes" always overwrites: whatever turns a permanence to an element leaves it a
  single affinity of that element. That covers every force aimed at one permanence
  (Cloudburst and the one-affinity commons too), the permanences that change their
  neighbours (Lava Field, Shoal, Peak, Meadow) and the world-wide forces (Downpour,
  Sandstorm, Waterspout, Dust Storm, and Firestorm and Tsunami, which turn every
  permanence in the world to a single fire or water). Nothing changes every affinity
  on a card unless its text says so.

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
- Affinities read like `1 fire, 1 water`, `2 air, 1 earth`, `water, any`, or
  `1 either-or (fire or earth)`. An either-or affinity is stored as
  `fire|earth` and drawn as one capsule holding both symbols, divided by a
  slash; every other affinity is drawn in a white ring.
- Binders come from bullets like `- **Binder A, Tides.** Description. Ocean,
  Archipelago, …` and are matched to cards by name.

### Card faces

The cards on the table are the faces drawn on the Card Anatomy canvas, copied
as they are, art included:

```sh
node scripts/sync-card-art.mjs <folder with the canvas's canvas.json and boards>
```

It uses only the canvas boards whose title starts with the newest pass's name
("Third pass: …"), matches every 320×448 face to a card by the name at its
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
| `js/computer.js` | Playing the computer on the table: feeds the engine's contest to the table's binder, board and scoreboard. |
| `play.html` | Redirects to `index.html?vs=computer`, for old links. |
| `js/game/rules.js`, `js/game/ai.js` | The third-pass rules engine and the computer opponent (browser and node). |
| `sim/` | The second-pass contest simulator (kept for its Nov 1 results; it doesn't know the third-pass cards). |

To run it locally: `python3 -m http.server 8080`, then open
<http://localhost:8080>. Adding `?peerhost=127.0.0.1&peerport=9000` points the
page at a local PeerJS broker for testing.

### The claude.ai copy

The "First Contest Playtest" page on claude.ai is a copy of this table, and this
repo is its source: never change the claude.ai page by hand. After the table
changes on `main`, republish these files to that page as they are on GitHub:
`index.html`, `css/style.css`, `js/main.js`, `js/state.js`, `js/cards.js`,
`js/net.js`, `js/computer.js`, `js/game/rules.js`, `js/game/ai.js`,
`data/cards.json`, `data/binders.json`, `data/card-faces.json`,
`vendor/peerjs.min.js`. Last republished from `9ecc3d2` (Nov 7).

## Simulating contests

For the current cards, use `node scripts/sim3.mjs` (above). The older `sim/`
simulator was written for the second pass and stops on third-pass cards; it's kept
with its Nov 1 readings. Its usage, for a second-pass card pool:

```sh
node sim/sim.js 200                    # 200 contests, prints the trends
node sim/sim.js 200 --style noforces   # a control run with no force faces
node sim/show.js sim/out/main-200-1.json 0   # read one contest move by move
```

It prints contest and round win rates, how rounds were decided (world points,
the affinity tie-break, a card's own win condition), cards per round, what took
cards off the table, and the least-played cards; the full stats, card by card,
are in `sim/out/`. See `sim/README.md` for the AI styles and the readings it
uses where the rules are still open.
