# Tools

Python scripts that draw the design work on the Claude canvases: the card faces on
**Card Anatomy**, and the overworld maps, the shop and the supercontinent on
**World Sketch**. They are not part of the playtest table. Every script here was
checked on Nov 4, 2026 to reproduce the published images and boards exactly.

Setup: Python 3 with `pip install -r tools/requirements.txt` (numpy, Pillow, SciPy).
The map scripts use the DejaVu fonts at `/usr/share/fonts/truetype/dejavu/`.

## cards/: the card faces (Card Anatomy, third pass)

- `pass3.py` is the card data for the current pass: all 101 cards, in the order
  `(no, name, rarity, affinities, permanence text, force name, duration, force text)`.
  It must agree with `data/card-pool.md`; edit both when a card changes.
- `art3.py` (with `lib.py`, `commons.py`, `uncommons.py`, `rares.py`, `forces.py`)
  draws the line-work art. `sizes3.json` holds per-card text sizes, `crop3.json`
  the crops of reused art, `p3H.json` the board heights.
- `pass3_cards.py` writes the four "Third pass" boards:

  ```
  python3 tools/cards/pass3_cards.py publish <folder> tools/cards/p3H.json
  ```

  `<folder>` is the `project/` folder of a local copy of the Card Anatomy canvas
  (read `project/canvas.json` and the boards from the artifact first, write into
  that folder, then publish it). `preview` instead of `publish` embeds local fonts
  for screenshots; it expects the fontsource packages for Cormorant Garamond and
  IBM Plex Mono unpacked in `tools/fonts/` (not in the repo).
- After the boards change, update the table:
  `node scripts/sync-cards.mjs` (card-pool.md to data/cards.json and binders.json),
  then `node scripts/sync-card-art.mjs <folder>` (faces to data/card-faces.json),
  then bump the `?v=` cache version in `index.html`.
- `plates.py <out folder>`: the plates, first draft (Nov 5, LORE-02). Renders a few
  third-pass faces with Playwright (local fonts needed), mirrors them and turns them
  into lit bronze with the drawing raised, or cut in for the cards in `ENGRAVED_TOO`.
  It's a 2D trick: a height map from the drawing, then light, cast shadows and a
  worked surface. `plates_board.py <project folder> plates_blobs.json` writes the
  "Plates, first draft" board; `plates_blobs.json` maps each PNG to its uploaded asset.
- `pass2.py`, `cards.py`, `eitheror.py`, `measure*.py`: earlier passes and
  measuring helpers, kept for reference.

## overworld/: maps (World Sketch)

`gen_overworld.py` is the shared parchment-map renderer. Each script writes its
PNGs next to itself (`ow_*.png`, ignored by git).

| Script | What it drew | Run |
| --- | --- | --- |
| `gen_overworld.py` | Six overworld options (Overworld board) | `python3 gen_overworld.py` |
| `gen_pieces.py` | Overworld pieces: shapes, waters, region splits | `python3 gen_pieces.py` |
| `gen_batch.py`, `gen_batch2.py`, `gen_batch3.py` | Sketches 1–32, 33–64, 65–96 | `python3 gen_batch3.py` |
| `pangaea_drafts_A-C.py` | Supercontinent drafts A, B, C (seeds 7, 11, 23) | `python3 pangaea_drafts_A-C.py 11` |
| `pangaea_drafts_D-F.py` | Drafts D, E, F (47, 61, 104) | |
| `pangaea_drafts_G-I.py` | Drafts G, H, I (313, 315, 318): three round pieces in a chain | |
| `pangaea_draft_J.py` | Draft J (321): uneven sizes, rougher coasts, fewer ridge islands | |
| `pangaea_draft_K.py` | Draft K (321): J plus Cam's edits | `python3 pangaea_draft_K.py 321` |
| `pangaea_draft_L.py` | Draft L (321): K plus Cam's Nov 4 edits and misleading ranges | `python3 pangaea_draft_L.py 321` |
| `pangaea_draft_M.py` | **Draft M (321), the working map**: L with the left continent rounder, and the middle island as the hollow mountain | `python3 pangaea_draft_M.py 321` |

Each supercontinent run writes three images: `ow_pg_now_<seed>.png` (today's
continents, 1704×1068), `ow_pg_old_<seed>.png` (the old map, 852×534) and
`ow_pg_fit_<seed>.png` (how the pieces fit, for us, not the player). Drafts K's,
L's and M's three are saved in `overworld/drafts/`.

How the supercontinent works (LORE-13): three lopsided round lobes are joined
into one landmass and split along weighted borders, so the middle piece shares a
long rift with each outer piece and the outer two touch only briefly. Each piece
drifts and turns, and its coast wears back until 72% of its crust is dry, the
real-world ratio (dry land is ~29% of Earth, continental crust ~40%). The pale
dotted shelf is the lost crust, and the pieces fit at the shelf edge, not the
shore (Bullard, Everett and Smith, 1965). Clues: a range cut by the sea, ridge
islands where the rift opened (one holds the earth seat), a delta, and in Draft K
a straight run of eroding cliffs with sea stacks. Draft K's edits are
hand-placed in the block marked "Cam's edits to Draft J": the right continent
turned 90° clockwise, its lake moved to the bottom of the middle island, and the
left piece taking a slice off the middle piece so its facing coast runs straight.

Draft L (Nov 4) keeps every coast exactly as K drew it: each piece's coast is worn
by noise carried along with the piece, so moving or turning a piece moves its
coast instead of wearing a new one. Its knobs sit at the top of the script:
`TURN_R` (the right continent turned 60° clockwise instead of 90°), `GAP_MR` and
`GAP_LM` (coast-to-coast gaps in today's pixels: the middle island and the right
continent 40 apart over one shared shelf, the left continent 190 off; K had 61
and 122), and the range layout. The ranges are built to mislead: one great range
crosses the old map; its high half still shows on the left continent and the
middle island, cut short by the cliffs, and past a bend it is worn to low hills
today (drawn as humps). Two decoys: a young range on the right continent on the
high half's line across the narrow strait, not on the old map, and an old range
on the left continent that runs into an outer coast. The fit view marks them:
ink for the great range (dashed where worn), rust for the decoys (dashed for the
young one). The earth seat stays off the cliffs, and a delta is drawn only where a
river reaches a coast that faced a rift (none in L).

Draft M (Nov 4) is the working map: it gets adjusted where an idea needs it,
not redrawn as new drafts. It is Draft L with the left continent a bit
rounder: its cliffs curve back toward the ends of the old rift (`CURVE`, 55 px)
instead of running straight, their shape holds a little past the old corners
(`REACH`), and the corners where they meet the rest of the coast are softer
(`SOFT`). Everything else is Draft L.

`HOLLOW` (on) fits the hollow mountain (WORLD-13): the whole middle island is drawn
as a plateau ringed by cliff hachures, with dense forest on top; its lake is hidden
inside as the harbour (the old map still shows it); a sea cave marks the east coast
nearest the harbour. The island is drawn in a second render and pasted in, so
nothing off the island changes. `HOLLOW = False` gives Draft M as first drawn.
`drafts/draftM_today.png` is the hollow version.

`towns_draft_M.py` draws the first twelve towns over Draft M
(`drafts/draftM_today.png`) and writes `ow_towns_M.png`; the copy shown on the
"Towns on Draft M" board is `drafts/towns_M.png`. Ports snap to the nearest coast,
inland towns stay off the coast and off high ground, and number 7 is the port
inside the hollow mountain, on its hidden harbour.

`gen_board.py` and `gen_pieces_board.py` write board HTML into
`../worldsketch-out/project/`, the local copy of the World Sketch canvas.

## places/: the hollow mountain (World Sketch)

- `gen_hollow.py <out folder>`: the middle island as a hollow mountain (WORLD-13), in
  the Hollis Games pixel-art pipeline (360×200, lit, dithered into a small palette,
  scaled ×4): `hollow_outside.png` from the sea, `hollow_inside.png` the port inside.
  The images on the board are saved in `places/out/`.

## shop/: Hollis Games (World Sketch)

- `gen_shop.py <out folder>`: the pixel-art shop scene and cabinet close-up
  (`case2` for the second pass: cards in holders, shadows, prices).
- `gen_night_board.py`: the night scene board with three collectors.
