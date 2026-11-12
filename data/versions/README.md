# Saved versions of the card pool

Before each change to the card pool, the version being replaced is saved here as a dated copy of
`data/card-pool.md`, and its commit is pushed to a branch named `saved/card-pool-<date>-<name>`, so
the whole repo at that point (card data, binders, faces, table) can be brought back with
`git checkout <branch>`. (Tags would be the usual way, but the proxy this repo is pushed through
doesn't allow them.)

| File | Branch (commit) | What it is |
| --- | --- | --- |
| `card-pool-2026-11-08-third-pass.md` | `saved/card-pool-2026-11-08-third-pass` (`b5385ad`) | The third pass as of Nov 8, 2026 (100 cards: Gap cut, Origin at #100, Archipelago at 10 water), before the restructure by ring count. The playtest table and simulator still use it. |
| `card-pool-2026-11-08-fourth-pass.md` | `saved/card-pool-2026-11-08-fourth-pass` (`c4200fc`) | The fourth pass as first applied on Nov 8 (87 cards, 13 open slots), before the placeholders for cards unique to one element. |
| `card-pool-2026-11-08-fourth-pass-placeholders.md` | `saved/card-pool-2026-11-08-fourth-pass-placeholders` (`ceb3806`) | The fourth pass with twelve unnamed placeholders (Nov 8), before they took names from cut cards. |
| `card-pool-2026-11-08-fourth-pass-named-placeholders.md` | `saved/card-pool-2026-11-08-fourth-pass-named-placeholders` (`62b2811`) | The fourth pass with named placeholders (Nov 8), before Ice Storm and Permafrost changed from "can't be moved" to "can't be removed". |
| `card-pool-2026-11-08-fourth-pass-removed-wording.md` | `saved/card-pool-2026-11-08-fourth-pass-removed-wording` (`252d2a4`) | The fourth pass after Ice Storm and Permafrost changed to "can't be removed" (Nov 8), before Archipelago went vanilla and Firestorm was reworded. |
| `card-pool-2026-11-08-fourth-pass-vanilla-archipelago.md` | `saved/card-pool-2026-11-08-fourth-pass-vanilla-archipelago` (`2a32d4e`) | The fourth pass with Archipelago vanilla and Firestorm reworded (Nov 8), before the triples took the remove-a-world's-element forces. |
| `card-pool-2026-11-08-fourth-pass-triple-forces.md` | `saved/card-pool-2026-11-08-fourth-pass-triple-forces` (`a416061`) | The fourth pass after the triples took Wildfire, Drought, Flash Flood and Avalanche (Nov 8), before Firestorm and Tsunami moved to the pinnacles. |
| `card-pool-2026-11-08-fourth-pass-pinnacle-forces.md` | `saved/card-pool-2026-11-08-fourth-pass-pinnacle-forces` (`220732e`) | The fourth pass after Firestorm and Tsunami moved to the pinnacles (Nov 8), before provisional binders were added. |
| `card-pool-2026-11-09-fourth-pass-provisional-binders.md` | `saved/card-pool-2026-11-09-fourth-pass-provisional-binders` (`63214c0`) | The fourth pass with provisional binders (Nov 8), before four placeholders became "+1 of this card's affinity if you have a world point" cards. |
| `card-pool-2026-11-09-plus-one-affinity.md` | `saved/card-pool-2026-11-09-plus-one-affinity` (`7fff501`) | The fourth pass after Nov 9's "+1 of this card's affinity if you have a world point" cards, before their text named the element. |
| `card-pool-2026-11-09-plus-one-element.md` | `saved/card-pool-2026-11-09-plus-one-element` (`0e04d96`) | The fourth pass with the +1 cards naming their element (Nov 9), before the open slot (#95) became a no-affinity permanence. |
| `card-pool-2026-11-09-hanging-valley.md` | `saved/card-pool-2026-11-09-hanging-valley` (`12a7c1f`) | The fourth pass with Hanging Valley in #95 (Nov 9), before one either-or common per pair became a meta card. |
| `card-pool-2026-11-10-before-vanilla-two-pips.md` | `saved/card-pool-2026-11-10-before-vanilla-two-pips` (`5d8c2d7`) | The fourth pass with six meta placeholders (Nov 9), before the two-pip permanences went vanilla (except the scoring cycle) and rings became pips. |
| `card-pool-2026-11-10-before-unaffected.md` | `saved/card-pool-2026-11-10-before-unaffected` (`2818e31`) | The fourth pass with the two-pip permanences vanilla (Nov 10), before the ignore cycle became "Unaffected by forces." |
| `card-pool-2026-11-11-binders-of-15.md` | `saved/card-pool-2026-11-11-binders-of-15` (`3d3b4f2`) | The fourth pass with the unaffected-by-forces cycle (Nov 10) and 15-card provisional binders, before binders went to 16 (Nov 11). |
| `card-pool-2026-11-11-binders-9-4-3.md` | `saved/card-pool-2026-11-11-binders-9-4-3` (`fd1f175`) | The fourth pass with 16-card provisional binders of 9 commons, 4 uncommons and 3 rares (Nov 11), before 10 / 4 / 2. |
| `card-pool-2026-11-11-fourth-pass-final.md` | `saved/card-pool-2026-11-11-fourth-pass-final` (`c4cbc04`) | The fourth pass as it ended (Nov 11: 16-card binders of 10 / 4 / 2), before the fifth pass. |
| `card-pool-2026-11-11-fifth-pass-first-draft.md` | `saved/card-pool-2026-11-11-fifth-pass-first-draft` (`b2b5e7d`) | The fifth pass as first drafted (Nov 11), before earth and fire swapped positional directions and Hanging Valley went back to "+1 world point". |
| `card-pool-2026-11-11-fifth-pass-final.md` | `saved/card-pool-2026-11-11-fifth-pass-final` (`754dbdf`) | The fifth pass as it ended (Nov 11): earth beside, fire across, Hanging Valley's +1 world point; before the sixth pass (fewer forces that reach the other player, answers gated by rarity). |
| `card-pool-2026-11-12-sixth-pass-first-draft.md` | `saved/card-pool-2026-11-12-sixth-pass-first-draft` (`d5e6605`) | The sixth pass as first drafted (Nov 11), before the extra-play forces went back to the idea pool and the protections were limited to the other player's cards (Nov 12). |
