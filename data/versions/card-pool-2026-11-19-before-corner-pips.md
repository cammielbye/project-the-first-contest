# Card pool (draft)

> Terminology (Nov 1, 2026): what the passes below call a "tag" is now an "affinity" (working term). Card texts in the force-face table use the new word; older tables and notes still say "tag."

## Sixth pass: fewer answers, gated by rarity (Nov 11, 2026)

> Cam (Nov 11): playing a permanence and having it answered at once "feels worse for some reason than it does in magic. I think it's because magic decks normally have way fewer pieces of interaction than creatures or threats." He wants to keep double-sided cards ("I want to persist with double sided until I feel there's no way to make it work") and: "let's go with one in ten are hard removal. one in ten can move or swap opponents cards. another one in ten can negate enemy forces." A force that reaches the other player reaches only permanences of its own rarity, shown with rarity symbols in the text like element symbols. "I want to get rid of all the \"x loses its affinities\" because it doesn't feel right. I want to generally avoid forces sticking around on the table where possible." Everything new here is Claude's draft against that brief, not adopted. The fifth pass as it ended is saved in the repo at `data/versions/card-pool-2026-11-11-fifth-pass-final.md` (branch `saved/card-pool-2026-11-11-fifth-pass-final`).

**Changes on Nov 12 (Cam).** "With uncapped turns, playing extra cards in a row doesnt do anything so lets just move that effect back to the idea pool": the 14 forces that only added plays (Overgrowth on Grove, Spark on Flint, Updraft on Dune, Heatwave on Desert, Sandstorm on Savanna, Permafrost on Plateau, Heat Dome on Lava Lake, Meteor on Crater, Ember on Badlands, Eruption on Smoking Hills, Steam Explosion on Lava Coast, Magma on Lava Plain, Supercell on Sand Sea, Wildfire on Cinder Field) and Lava Flow's "When played, play another fire card." are in the idea pool (CARD-28); those force faces are open for now, and Lava Flow has no text. The meta card Verge ("Play two more cards this turn.") has the same effect and is unchanged for now. The protections stop only the other player's cards, "concisely worded as only opponents cards" (Cam): "Your opponent can't move this." (was "Can't be moved."), "Unaffected by your opponent's forces." (was "Unaffected by forces."), Cavern's "Your opponent can't split its world.", and Sinkhole's "Your world ignores your opponent's forces." (was "A world can't lose permanences."). The first draft of the sixth pass is saved in the repo (`data/versions/card-pool-2026-11-12-sixth-pass-first-draft.md`, branch `saved/card-pool-2026-11-12-sixth-pass-first-draft`).

**The format** is unchanged from the fifth pass: best of three, no cap on cards a round, the reveal for who goes second, worlds up to 2×2, one world point at most from a world's affinities with card effects adding to it.

**The 86 force faces by role.**
- **Hard removal (9):** commons Lava Field, Lava Flow, Wilderness: "Remove a common permanence." Uncommons Hot Spring, Obsidian, Volcano: "Remove an uncommon permanence." Rare Caldera Lake: "Remove a rare permanence." Pinnacles Core, Origin: a world, every world.
- **Moving or swapping the other player's cards (9):** commons Ledge, Pass, Summit; uncommons Hidden Valley, Sea Cliff; rare Wind Gap; pinnacles Ocean, Pangaea, Trade Winds.
- **Stopping the other player's forces (9):** commons Bedrock, Cavern, Glacier, Stone Field; uncommons Cloud Forest, Fumarole, Old Growth; rares Ice Sheet, Thicket. "No common forces until your next turn" stops that rarity's forces for the other player's next turn; Thaw removes a common force; Sinkhole shields one of your worlds from the other player's forces.
- **Helping their owner (45):** each element leans on its own verbs. Water brings cards back (from your void to your binder, or straight into play) and returns your own permanences and worlds to your binder, which saves them for a later round; earth returns whole worlds; air moves, swaps and splits your own cards, which matters now that positions give pips and a split can turn one world point into two. Four commons change one of your own permanences' element for the round, one per element. Fire's own verb (extra plays) went to the idea pool on Nov 12.
- **Open (14):** Badlands, Cinder Field, Crater, Desert, Dune, Flint, Grove, Lava Coast, Lava Lake, Lava Plain, Plateau, Sand Sea, Savanna, Smoking Hills: no force for the moment.
- **The rarity gate:** "only its own rarity" (Cam). The pinnacles keep their world-scale forces, which aim at no single permanence (Claude's reading; open).
- **Lasting forces:** 12 of 86 stay on the table (down from about 40): the 7 "No … forces until your next turn", Sinkhole, and the four commons that change an element for the round.
- **No "loses its affinities"** anywhere: the twelve blanking forces are gone, and Ice Sheet's rare cycle now reads "Each permanence in its world gains water" (and earth, fire, air).
- **Unchanged:** the permanence faces apart from Ice Sheet's cycle, the restrictions on the three-pip rares, the meta cards, and the pinnacles' forces.

**Counts.** 29 commons, 28 uncommons, 24 rares, 5 pinnacles and 14 meta cards: 100 cards.

**One pip, common: can't be moved (4).** One per element.

| No. | Permanence | Rarity | Affinities | Permanence text | Force | Duration | Force text |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Glacier | C | 1 water | Your opponent can't move this. | Thaw | Once | Remove a common force. |
| 2 | Bedrock | C | 1 earth | Your opponent can't move this. | Tangle | Until your next turn | No common forces until your next turn. |
| 3 | Lava Field | C | 1 fire | Your opponent can't move this. | Ash | Once | Remove a common permanence. |
| 4 | Spire | C | 1 air | Your opponent can't move this. | Whirlwind | Once | Split one of your worlds. |

**One pip, common: unaffected by forces (4).** Cam (Nov 10): a cycle of single-pip cards unaffected by forces, to make some powerful enough to use late game. Until Nov 10 this cycle ignored the opposite element's forces (water and fire, earth and air); that idea is now in the idea pool.

| No. | Permanence | Rarity | Affinities | Permanence text | Force | Duration | Force text |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | Tide Pool | C | 1 water | Unaffected by your opponent's forces. | Drizzle | Once | Return a card from your void. |
| 6 | Stone Field | C | 1 earth | Unaffected by your opponent's forces. | Dust | Until your next turn | No common forces until your next turn. |
| 7 | Ashfield | C | 1 fire | Unaffected by your opponent's forces. | Brushfire | Lasts the round | One of your permanences becomes fire. |
| 8 | Summit | C | 1 air | Unaffected by your opponent's forces. | Crosswind | Once | Swap two common permanences. |

**One pip, common: when played (4).** One per element.

| No. | Permanence | Rarity | Affinities | Permanence text | Force | Duration | Force text |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 9 | Snowfield | C | 1 water | When played, return one of your permanences. | Freeze | Once | Play a permanence from your void. |
| 10 | Grove | C | 1 earth | When played, remove a common force. | — | — | No force for the moment. |
| 11 | Lava Flow | C | 1 fire | — | Lightning | Once | Remove a common permanence. |
| 12 | Bluff | C | 1 air | When played, move one of your permanences. | Eddy | Once | Swap two of your permanences. |

**One pip, common: either-or, no text (6).** One for each pair of elements (Cam, Nov 9: the other became a meta card).

| No. | Permanence | Rarity | Affinities | Permanence text | Force | Duration | Force text |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 13 | Marsh | C | 1 either-or (water or earth) | — | Mire | Once | Return a card from your void. |
| 14 | Steam Vent | C | 1 either-or (water or fire) | — | Vent | Once | Return one of your permanences. |
| 15 | Sea Stack | C | 1 either-or (water or air) | — | Riptide | Lasts the round | One of your permanences becomes water. |
| 16 | Flint | C | 1 either-or (earth or fire) | — | — | — | No force for the moment. |
| 17 | Pass | C | 1 either-or (earth or air) | — | Whirl | Once | Move a common permanence to another world. |
| 18 | Scrubland | C | 1 either-or (fire or air) | — | Dust Devil | Lasts the round | One of your permanences becomes air. |

**One pip, common: any (1).**

| No. | Permanence | Rarity | Affinities | Permanence text | Force | Duration | Force text |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 19 | Wilderness | C | 1 any | — | Thunderstorm | Once | Remove a common permanence. |

**One pip, common: +1 of its element with a world point (in the unique slots) (4).** Cam (Nov 9): one of each element's placeholders with non-cycle effects; the text names the element ("+1 [water symbol]"). They sit in the slots for cards unique to one element, numbered with them. Claude took the first placeholder of each element; like the other reclaimed slots, each keeps its third-pass force face.

| No. | Permanence | Rarity | Affinities | Permanence text | Force | Duration | Force text |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 83 | Ice Floe | C | 1 water | +1 water if you have a world point. | Current | Once | Play a permanence from your void. |
| 86 | Hill | C | 1 earth | +1 earth if you have a world point. | Rockfall | Lasts the round | One of your permanences becomes earth. |
| 89 | Dune | C | 1 fire | +1 fire if you have a world point. | — | — | No force for the moment. |
| 92 | Ledge | C | 1 air | +1 air if you have a world point. | Gust | Once | A common permanence becomes its own world. |

**Two pips, uncommon: two different elements, no text (6).**

| No. | Permanence | Rarity | Affinities | Permanence text | Force | Duration | Force text |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 20 | Delta | B | 1 water, 1 earth | — | Flood | Once | Return two of your permanences. |
| 21 | Hot Spring | B | 1 water, 1 fire | — | Scald | Once | Remove an uncommon permanence. |
| 22 | Cloud Forest | B | 1 water, 1 air | — | Fog | Until your next turn | No uncommon forces until your next turn. |
| 23 | Volcano | B | 1 earth, 1 fire | — | Lava Bomb | Once | Remove an uncommon permanence. |
| 24 | Sea Cliff | B | 1 earth, 1 air | — | Gale | Once | Move an uncommon permanence to another world. |
| 25 | Desert | B | 1 fire, 1 air | — | — | — | No force for the moment. |

**Two pips, uncommon: two different elements, no text since Nov 10 (6).**

| No. | Permanence | Rarity | Affinities | Permanence text | Force | Duration | Force text |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 26 | Mangrove | B | 1 water, 1 earth | — | Undertow | Once | Return one of your worlds. |
| 27 | Mud Pots | B | 1 water, 1 fire | — | Downpour | Once | Play a permanence from your void. |
| 28 | Waterfall | B | 1 water, 1 air | — | Cloudburst | Once | Return two cards from your void. |
| 29 | Cinder Cone | B | 1 earth, 1 fire | — | Ashfall | Once | Split one of your worlds. |
| 30 | Canyon | B | 1 earth, 1 air | — | Dust Storm | Once | Swap two of your permanences. |
| 31 | Savanna | B | 1 fire, 1 air | — | — | — | No force for the moment. |

**Two pips, uncommon: scoring (the Mountain Range cycle) (4).** Each scores a point per four of its element (Cam, Nov 8).

| No. | Permanence | Rarity | Affinities | Permanence text | Force | Duration | Force text |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 32 | Spring | B | 1 water, 1 fire | Score a point per four water affinities. | Low Tide | Once | Return one of your worlds. |
| 33 | Mountain Range | B | 1 earth, 1 air | Score a point per four earth affinities. | Rockslide | Once | Move one of your permanences. |
| 34 | Fumarole | B | 1 fire, 1 air | Score a point per four fire affinities. | Flare-up | Until your next turn | No uncommon forces until your next turn. |
| 35 | Sky Isle | B | 1 air, 1 any | Score a point per four air affinities. | Waterspout | Once | Split one of your worlds. |

**Two pips, uncommon: one element and one any (4).** Sky Isle (above) is the air card of this cycle.

| No. | Permanence | Rarity | Affinities | Permanence text | Force | Duration | Force text |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 36 | Tidal Flat | B | 1 water, 1 any | — | Hail | Once | Return two of your permanences. |
| 37 | Old Growth | B | 1 earth, 1 any | — | Bramble | Until your next turn | No uncommon forces until your next turn. |
| 38 | Obsidian | B | 1 fire, 1 any | — | Scorch | Once | Remove an uncommon permanence. |
| 39 | Hidden Valley | B | 2 any | — | Landslide | Once | An uncommon permanence becomes its own world. |

**Two pips, uncommon: two of one element (4).**

| No. | Permanence | Rarity | Affinities | Permanence text | Force | Duration | Force text |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 40 | Deep Lake | B | 2 water | — | Ice Storm | Once | Return two cards from your void. |
| 41 | Plateau | B | 2 earth | — | — | — | No force for the moment. |
| 42 | Lava Lake | B | 2 fire | — | — | — | No force for the moment. |
| 43 | Twin Peaks | B | 2 air | — | High Pressure | Once | Swap two of your permanences. |

**No pips, uncommon (1).** No pip of its own, so the pip rule doesn't place it; kept at uncommon.

| No. | Permanence | Rarity | Affinities | Permanence text | Force | Duration | Force text |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 44 | Mirage | B | none | Copies every adjacent permanence's affinities. | Heat Shimmer | Once | Move one of your permanences. |

**No pips, uncommon: +1 world point (in the open slot) (1).** Cam (Nov 9): another permanence with no affinities. The four elements in its text are ringed, as affinities. Claude gave it the one free name and kept it at uncommon like Mirage.

| No. | Permanence | Rarity | Affinities | Permanence text | Force | Duration | Force text |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 95 | Hanging Valley | B | none | +1 world point if this world has water earth fire air. | Squall | Once | Swap two of your permanences. |

**Three pips, rare: three different elements, start a new world (4).**

| No. | Permanence | Rarity | Affinities | Permanence text | Force | Duration | Force text |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 45 | Caldera Lake | A | 1 water, 1 earth, 1 fire | Play only on a new world. | Collapse | Once | Remove a rare permanence. |
| 46 | Rainforest | A | 1 water, 1 earth, 1 air | Play only on a new world. | Monsoon | Once | Play a card from your void. |
| 47 | Geyser Basin | A | 1 water, 1 fire, 1 air | Play only on a new world. | Typhoon | Once | Move two of your permanences. |
| 48 | Red Canyon | A | 1 earth, 1 fire, 1 air | Play only on a new world. | Erosion | Once | Return two of your worlds. |

**Three pips, rare: two of one element and one of another (12).**

| No. | Permanence | Rarity | Affinities | Permanence text | Force | Duration | Force text |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 49 | Archipelago | A | 2 water, 1 earth | — | Surge | Once | Return three cards from your void. |
| 50 | Boiling Lake | A | 2 water, 1 fire | — | Torrent | Once | Play a card from your void. |
| 51 | Misty Fjord | A | 2 water, 1 air | — | Whiteout | Once | Play a card from your void. |
| 52 | Floodplain | A | 1 water, 2 earth | — | Mudflow | Once | Return two of your worlds. |
| 53 | Smoking Hills | A | 2 earth, 1 fire | — | — | — | No force for the moment. |
| 54 | Highlands | A | 2 earth, 1 air | — | Earthquake | Once | Return two of your worlds. |
| 55 | Lava Coast | A | 1 water, 2 fire | — | — | — | No force for the moment. |
| 56 | Lava Plain | A | 1 earth, 2 fire | — | — | — | No force for the moment. |
| 57 | Sand Sea | A | 2 fire, 1 air | — | — | — | No force for the moment. |
| 58 | Cloud Sea | A | 1 water, 2 air | — | Hurricane | Once | Move two of your permanences. |
| 59 | Stone Towers | A | 1 earth, 2 air | — | Gale Force | Once | Move two of your permanences. |
| 60 | High Desert | A | 1 fire, 2 air | — | Tornado | Once | Return two cards you played last round. |

**Three pips, rare: three of one element, first turn only (4).**

| No. | Permanence | Rarity | Affinities | Permanence text | Force | Duration | Force text |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 61 | Lagoon | A | 3 water | Play only on your first turn. | Flash Flood | Once | Return three cards from your void. |
| 62 | Moor | A | 3 earth | Play only on your first turn. | Avalanche | Once | Return two of your worlds. |
| 63 | Cinder Field | A | 3 fire | Play only on your first turn. | — | — | No force for the moment. |
| 64 | Peak | A | 3 air | Play only on your first turn. | Drought | Once | Move two of your permanences. |

**One pip, rare: each permanence in its world gains its element (the opposite-element blanks until Nov 11) (4).**

| No. | Permanence | Rarity | Affinities | Permanence text | Force | Duration | Force text |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 65 | Ice Sheet | A | 1 water | Each permanence in its world gains water. | Blizzard | Until your next turn | No rare forces until your next turn. |
| 66 | Thicket | A | 1 earth | Each permanence in its world gains earth. | Shelter | Until your next turn | No rare forces until your next turn. |
| 67 | Badlands | A | 1 fire | Each permanence in its world gains fire. | — | — | No force for the moment. |
| 68 | Wind Gap | A | 1 air | Each permanence in its world gains air. | Downdraft | Once | A rare permanence becomes its own world. |

**Unique to one element: positional (4).** Cam (Nov 11): positional conditions and buffs (idea 11). In a 2×2 world each card has one card beside it, one above or below it, and one across the diagonal; each element gets its own direction, so no two are the same effect.

| No. | Permanence | Rarity | Affinities | Permanence text | Force | Duration | Force text |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 84 | Shoal | C | 1 water | The permanence below this gains water. | Mist | Once | Move one of your permanences. |
| 87 | Meadow | C | 1 earth | The permanence beside this gains earth. | Mudslide | Once | Move one of your permanences. |
| 90 | Barrens | C | 1 fire | The permanence across from this gains fire. | Smoke | Once | Swap two of your permanences. |
| 93 | Ridge | C | 1 air | The permanence above this gains air. | Breeze | Once | Move one of your permanences. |

**Unique to one element: the element's effect, twisted (4).** Cam (Nov 11): the cards unique to one element lean into the effect and element relationship and double down, with an unusual twist on an existing mechanic left unique to that element; his example was an air return that brings back a card played in a previous round.

| No. | Permanence | Rarity | Affinities | Permanence text | Force | Duration | Force text |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 85 | Fen | B | 1 water, 1 earth | — | Whirlpool | Once | Play a card from a void. |
| 88 | Cavern | C | 1 earth | Your opponent can't split its world. | Sinkhole | Lasts the round | Your world ignores your opponent's forces. |
| 91 | Crater | B | 1 earth, 1 fire | — | — | — | No force for the moment. |
| 94 | Eyrie | C | 1 air | — | Cyclone | Once | Return a card you played last round. |

**Pinnacles (5).**

| No. | Permanence | Rarity | Affinities | Permanence text | Force | Duration | Force text |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 96 | Ocean | S | 4 water | — | Tsunami | Once | Return a player's worlds. |
| 97 | Pangaea | S | 4 earth | — | World Quake | Once | Split every world. |
| 98 | Core | S | 4 fire | — | Firestorm | Once | Remove a world. |
| 99 | Trade Winds | S | 4 air | — | Jet Stream | Once | Every permanence becomes its own world. |
| 100 | Origin | S | 1 water, 1 earth, 1 fire, 1 air | — | Unmaking | Once | Remove every world. |

**Fifth-pillar meta cards, no rarity (14).** One face, usable by either player. Unchanged from the fifth pass.

| Card | No. | Text |
| --- | --- | --- |
| Echo | 69 | Play a card from your void. |
| Hollow | 70 | Return a card from your void. |
| Equinox | 71 | Return 3 cards from your void. |
| Verge | 72 | Play two more cards this turn. |
| Lull | 73 | Your opponent skips their next turn. |
| Ebb | 74 | Remove your opponent's last common. |
| Horizon | 75 | Remove a card from your opponent's binder. |
| Calm | 76 | No forces this round. |
| Aftershock | 77 | Your opponent takes the next two turns. |
| Stillness | 78 | Your opponent passes. |
| Sunlight | 79 | Remove every force. |
| Weathering | 80 | Return the last card your opponent played. |
| Thunder | 81 | Play once more after both players pass. |
| Haze | 82 | Your opponent can't play forces next turn. |

**Provisional test binders (Claude, Nov 8), 5.** Carried over: 16 cards each (10 commons, 4 uncommons, 2 rares), drawn at random until Cam builds real ones.

- **Binder A, Water.** Leans water, loosely (drawn at random). Ashfield, Scrubland, Snowfield, Wilderness, Marsh, Stone Field, Lava Field, Glacier, Sea Cliff, Plateau, Hollow, Deep Lake, Ice Sheet, Stone Towers, Steam Vent, Sea Stack.
- **Binder B, Earth.** Leans earth, loosely (drawn at random). Steam Vent, Marsh, Grove, Scrubland, Stone Field, Pass, Bedrock, Flint, Spring, Canyon, Sea Cliff, Hot Spring, Lava Plain, Geyser Basin, Hill, Wilderness.
- **Binder C, Fire.** Leans fire, loosely (drawn at random). Stone Field, Lava Field, Summit, Lava Flow, Tide Pool, Scrubland, Ashfield, Steam Vent, Hidden Valley, Twin Peaks, Delta, Tidal Flat, Badlands, Caldera Lake, Flint, Wilderness.
- **Binder D, Air.** Leans air, loosely (drawn at random). Stone Field, Sea Stack, Tide Pool, Lava Field, Glacier, Wilderness, Scrubland, Summit, Savanna, Twin Peaks, Equinox, Desert, Sand Sea, Rainforest, Pass, Bluff.
- **Binder E, Even.** No lean (drawn at random). Spire, Summit, Ashfield, Bedrock, Snowfield, Bluff, Scrubland, Wilderness, Savanna, Horizon, Cloud Forest, Old Growth, Boiling Lake, Highlands, Grove, Flint.
## Fifth pass: playable again (Nov 11, 2026), saved separately

The fifth pass as it ended on Nov 11 (every permanence with a force, the unique and meta slots filled, earth beside and fire across, Hanging Valley's +1 world point) is saved in the playtest repo at `data/versions/card-pool-2026-11-11-fifth-pass-final.md` and on the branch `saved/card-pool-2026-11-11-fifth-pass-final`.

## Fourth pass: the pool by pip count (Nov 8, 2026), saved separately

The fourth pass as it ended on Nov 11 (the pool by pip count, eight placeholders for cards unique to one element, six meta placeholders, five provisional binders of 16) is saved in the playtest repo at `data/versions/card-pool-2026-11-11-fourth-pass-final.md` and on the branch `saved/card-pool-2026-11-11-fourth-pass-final`.

## Third pass: the full pool (Nov 2, 2026), saved separately

The third pass, as it stood on Nov 8 before the restructure (100 cards, five test binders, and the notes and changes since Nov 2), is saved in the playtest repo at `data/versions/card-pool-2026-11-08-third-pass.md` and on the branch `saved/card-pool-2026-11-08-third-pass`.

## Second pass: 50 cards plus 5 meta (Nov 1, 2026)

> Claude's draft at Cam's request, nothing Decided: half the pool (30 commons, 13 uncommons, 5 rares, 2 pinnacles) with both faces, plus five weaker fifth-pillar meta cards, and two playtest binders. Text-first: new force faces have placeholder art. Drawn on the [Card Anatomy canvas](https://claude.ai/artifact/5AWUHQhCvrbEw3YSmxbqac) under "Second pass". Rules followed: rules text under 8 words (CARD-23), effects up and restrictions down with rarity (CARD-24), balanced for the likely best case (CARD-25); worlds up to 2×2, scoring one world point per complete set; forces target either player's cards unless they say otherwise; moves and swaps never change a card's owner; "remove" sends a card to its owner's void; a card that "doesn't count" is treated as if it weren't there.

> Revised Nov 1 (Cam): the six dual commons show an either-or mark instead of "Counts as X or Y" text, and Confluence drops its text. On the cards, every affinity sits in a white ring, and an either-or affinity is one capsule holding both symbols, divided by a slash; one ring or one capsule is one affinity, its element chosen at round end for a capsule. Also, a force that lasts the round sits on one card or beside one world and never affects the whole table, so Ash Cloud now hits one card, Blizzard happens once, and Verge plays two cards.

Affinities across the 50: fire 14, water 16, air 15, earth 18, plus 6 either-or capsules and one any. 11 of the 30 commons carry a subtle permanence effect; six carry an either-or capsule, one per pair of elements.

**Fire commons (8)**

| No. | Permanence | Rarity | Affinities | Permanence text | Force | Duration | Force text |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 12 | Cinder Field | C | 1 fire | — | Brushfire | Lasts the round | A one-affinity card doesn't count. |
| 2 | Flint | C | 1 either-or (fire or earth) | — | Spark | Lasts the round | A one-affinity card becomes fire. |
| 3 | Obsidian | C | 1 fire | Forces can't remove this. | Ash Cloud | Lasts the round | A one-affinity air card doesn't count. |
| 6 | Scrubland | C | 1 either-or (fire or air) | — | Controlled Burn | Once | Remove one of your cards. |
| 7 | Ashfield | C | 1 fire | Counts double in affinity ties. | Smoke | Lasts the round | A world doesn't count in ties. |
| 9 | Dune | C | 1 fire | — | Shimmer | Lasts the round | A one-affinity card counts as any element. |
| 10 | Barrens | C | 1 fire | — | Lightning | Once | Remove a lone one-affinity card. |
| 11 | Steam Vent | C | 1 either-or (fire or water) | — | Vent | Once | Return your card to your binder. |

**Water commons (4)**

| No. | Permanence | Rarity | Affinities | Permanence text | Force | Duration | Force text |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 23 | Spring | C | 1 water | Returns to your binder at round end. | Drizzle | Lasts the round | A one-affinity card also counts as water. |
| 24 | Marsh | C | 1 either-or (water or earth) | — | Mire | Lasts the round | A world of two can't grow. |
| 28 | Snowfield | C | 1 water | Play on one-affinity air. It becomes water. | Rain | Lasts the round | A one-affinity card becomes water. |
| 29 | Tide Pool | C | 1 water | Ignores common forces. | Freeze | Lasts the round | A world's one-affinity cards can't be removed. |

**Air commons (9)**

| No. | Permanence | Rarity | Affinities | Permanence text | Force | Duration | Force text |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 41 | Ledge | C | 1 air | — | Gust | Once | A one-affinity card becomes its own world. |
| 33 | Summit | C | 1 air | Counts double in affinity ties. | Breeze | Lasts the round | A one-affinity card becomes air. |
| 38 | Pass | C | 1 either-or (air or earth) | — | Drift | Once | Move your card to another world. |
| 45 | Wind Gap | C | 1 air | — | Crosswind | Once | Swap two one-affinity cards between worlds. |
| 37 | Peak | C | 1 air | — | Downdraft | Lasts the round | A one-affinity air card becomes earth. |
| 32 | Sea Stack | C | 1 either-or (water or air) | — | Sea Breeze | Lasts the round | A one-affinity card also counts as air. |
| 36 | Ridge | C | 1 air | — | Lift | Once | Remove a common sitting on another. |
| 31 | Spire | C | 1 air | Forces can't move this. | Vortex | Once | Move a one-affinity card between worlds. |
| 39 | Bluff | C | 1 air | — | Eddy | Once | Swap two cards in one world. |

**Earth commons (9)**

| No. | Permanence | Rarity | Affinities | Permanence text | Force | Duration | Force text |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 52 | Hill | C | 1 earth | — | Overgrowth | Lasts the round | One of your worlds ignores common forces. |
| 47 | Bedrock | C | 1 earth | Forces can't remove this. | Landslide | Lasts the round | A one-affinity card becomes earth. |
| 48 | Cave | C | 1 earth | Ignores common forces. | Shelter | Lasts the round | A card can't be removed. |
| 49 | Meadow | C | 1 earth | — | Bloom | Lasts the round | A one-affinity card also counts as earth. |
| 50 | Grove | C | 1 earth | Returns to your binder at round end. | Lichen | Lasts the round | A one-affinity card counts double in ties. |
| 59 | Mesa | C | 1 earth | — | Fault Line | Once | Split a world of three or fewer. |
| 57 | Ravine | C | 1 earth | — | Washout | Once | Return a one-affinity card to its binder. |
| 46 | Boulder | C | 1 earth | — | Rockfall | Once | Remove a lone one-affinity card. |
| 54 | Thicket | C | 1 earth | Your touching cards can't be removed. | Tangle | Lasts the round | Cards in a world can't be moved. |

**Uncommons (13)**

| No. | Permanence | Rarity | Affinities | Permanence text | Force | Duration | Force text |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 63 | Hot Spring | B | 1 fire, 1 water | — | Steam Burst | Lasts the round | A touching fire-water pair doesn't count. |
| 62 | Desert | B | 1 fire, 1 air | — | Heatwave | Lasts the round | A card doesn't count. |
| 65 | Volcano | B | 1 fire, 1 earth | — | Eruption | Once | Remove a one-affinity card. |
| 78 | Cloud Forest | B | 1 water, 1 air | — | Fog | Lasts the round | A world can't grow. |
| 69 | Delta | B | 1 water, 1 earth | — | Flood | Once | Return a card to its binder. |
| 71 | Sea Cliff | B | 1 air, 1 earth | — | Gale | Once | Swap two cards between one player's worlds. |
| 66 | Glacier | B | 1 water | Play on earth permanence. It becomes water. | Thaw | Once | Remove a card sitting on another. |
| 79 | Salt Flat | B | 1 fire | Play on one-affinity permanence. It doesn't count. | Drought | Lasts the round | A card becomes fire. |
| 80 | Mirage | B | 1 air | Copies a touching card's affinities. | Haze | Lasts the round | A card counts as any element. |
| 84 | Hidden Valley | B | 1 earth | Your other cards ignore common forces. | Rockslide | Lasts the round | A card becomes earth. |
| 85 | Petrified Forest | B | 1 earth | Stays into the next round. | Uplift | Lasts the round | A world ignores all forces. |
| 82 | Hanging Valley | B | 1 air | Your air counts double in ties. | Updraft | Lasts the round | A card becomes air. |
| 81 | Confluence | B | 1 water, 1 any | — | Current | Once | Move a card between its owner's worlds. |

**Rares (5)**

| No. | Permanence | Rarity | Affinities | Permanence text | Force | Duration | Force text |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 88 | Caldera Lake | A | 1 fire, 1 water, 1 earth | — | Collapse | Once | Remove any card. |
| 91 | Stone Towers | A | 2 air, 1 earth | — | Erosion | Once | Split a world in two. |
| 93 | Archipelago | A | 2 water, 1 earth | Win the round with 10 water affinities. | Rising Sea | Lasts the round | One-affinity cards in a world don't count. |
| 94 | Ice Sheet | A | 1 water | Fire affinities don't count. | Blizzard | Once | Return a world to its owner's binder. |
| 95 | Mountain Range | A | 1 air, 1 earth | Score a point per four earth affinities. | Avalanche | Once | Remove two touching one-affinity cards. |

**Pinnacles (2)**

| No. | Permanence | Rarity | Affinities | Permanence text | Force | Duration | Force text |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 96 | Core | S | 4 fire | — | Solar Flare | Once | Remove all one-affinity cards. |
| 98 | Ocean | S | 4 water | — | Deluge | Lasts the round | A world doesn't count. |

**Fifth-pillar meta cards (5).** One face, usable by either player, uncommon, numbers still to be placed.

| Card | Text |
| --- | --- |
| Echo | Play a one-affinity card from your void. |
| Ebb | Remove your opponent's last card. |
| Horizon | Look through your opponent's binder. |
| Lull | Your opponent skips their next turn. |
| Verge | Play two cards this turn. |

**Two playtest binders (25 each).**

- **Binder A, Tides.** Water and air, control and turtling, built around Ocean. Ocean, Archipelago, Ice Sheet, Stone Towers, Cloud Forest, Glacier, Confluence, Hanging Valley, Mirage, Delta, Sea Cliff, Echo, Lull, Horizon, Cinder Field, Flint, Steam Vent, Ashfield, Dune, Hill, Cave, Thicket, Ledge, Spire, Spring.
- **Binder B, Embers.** Fire and earth, removal and pressure, built around Core. Core, Caldera Lake, Mountain Range, Stone Towers, Hot Spring, Desert, Volcano, Salt Flat, Hidden Valley, Petrified Forest, Ebb, Verge, Horizon, Marsh, Snowfield, Tide Pool, Spring, Summit, Pass, Wind Gap, Peak, Bedrock, Meadow, Grove, Barrens.
- Shared: Horizon, Spring, Stone Towers. In neither binder: Bluff, Boulder, Mesa, Obsidian, Ravine, Ridge, Scrubland, Sea Stack.

## Force faces for the 12 examples (Nov 1, 2026, revised the same day)

> Claude's draft at Cam's request, nothing Decided. Drawn in pairs (permanence beside force) on the "Force faces" board of the [Card Anatomy canvas](https://claude.ai/artifact/5AWUHQhCvrbEw3YSmxbqac). Working rules behind it (Exploring, DUEL-33 and CARD-15): worlds belong to one player; a world is a group of your cards that touch and scores one world point per complete set of the four elements; forces are never part of a world (no tags, no connecting); a force that lasts sits on the card it affects, or beside the world, until the round ends; a force that happens once goes to the void, each player's one place for cards that leave play (DUEL-34).

| No. | Permanence | Force | Rarity | Duration | What the force does |
| --- | --- | --- | --- | --- | --- |
| 12 | Cinder Field | Brushfire | C | Lasts the round | A one-affinity card doesn't count. |
| 23 | Spring | Washout | C | Once | Return a one-affinity card to its binder. |
| 41 | Ledge | Gust | C | Once | A one-affinity card becomes its own world. |
| 52 | Hill | Overgrowth | C | Lasts the round | One of your worlds ignores common forces. |
| 63 | Hot Spring | Steam Burst | B | Lasts the round | A touching fire-water pair doesn't count. |
| 71 | Sea Cliff | Gale | B | Once | Swap two cards between one player's worlds. |
| 78 | Cloud Forest | Fog | B | Lasts the round | A world can't grow. |
| 66 | Glacier | Thaw | B | Once | Remove a card sitting on another. |
| 88 | Caldera Lake | Collapse | A | Once | Remove any card. |
| 91 | Stone Towers | Erosion | A | Once | Split a world in two. |
| 93 | Archipelago | Rising Sea | A | Lasts the round | One-affinity cards in a world don't count. |
| 98 | Ocean | Deluge | S | Lasts the round | A world doesn't count. |

**Choices in this draft:**
- Commons use one simple verb each (play on a card, return, move, shelter) and reach only cards with one tag, so rarer cards are sturdier.
- Uncommons reach any card or shape a whole world; rares remove, split or sweep part of a world; the pinnacle sweeps a whole world. The Black Hole meta card (remove a whole world) sits above that (CARD-12).
- Single-card hits favor big worlds with spare tags; Erosion, Rising Sea and Deluge favor spreading out.
- Force faces look different from permanence: a cooler body, a dashed inner border, an italic name, no tags, and a duration line in place of the tags.

**Revised Nov 1** after Cam locked rules text under 8 words (CARD-23), effects up and restrictions down with rarity (CARD-24), and balancing for the likely best case (CARD-25). Cam's notes: Fog kept; Gale now swaps; Steam Burst reworded and restricted to a touching fire-water pair (placing fire and water diagonally in a 2×2 dodges it); Glacier plays only on earth permanence and turns it to water. Worlds are now capped at 2×2, rectangles only. Conventions in these drafts: forces can target either player's cards unless they say otherwise; "remove" sends a card to its owner's void.

**Open:** whether common forces should stay limited to one-tag cards; every other card's text still needs a pass for the 8-word rule.

## Third pass: permanence faces for the world-points loop (Oct 31, 2026)

> Claude's draft at Cam's request, nothing Decided. Under DUEL-33, a permanence face carries element tags (affinities), and the number of tags scales with rarity (C one, B two, A three, S four of one element). Drawn as cards on the [Card Anatomy canvas](https://claude.ai/artifact/5AWUHQhCvrbEw3YSmxbqac): the "Card examples" board (12 cards across all rarities) and four "commons" boards. Names follow CARD-22 (no "The"). Force and event faces are still open.

**Commons, 60 cards, 15 per element, one tag each.** Numbers run in blocks by element.

| Element | Numbers | Cards |
| --- | --- | --- |
| Fire | 1–15 | Ember Bed, Flint, Obsidian, Crater, Geyser, Scrubland, Ashfield, Lava Field, Dune, Barrens, Steam Vent, Cinder Field, Magma Pool, Pumice, Burnt Hollow |
| Water | 16–30 | Stream, Pond, Brook, Creek, Cove, Lagoon, Bog, Spring, Marsh, Swamp, Waterfall, Mangrove, Snowfield, Tide Pool, Floodplain |
| Air | 31–45 | Spire, Sea Stack, Summit, Cliff, Plateau, Ridge, Peak, Pass, Bluff, Crag, Ledge, Moor, Steppe, Overlook, Wind Gap |
| Earth | 46–60 | Boulder, Bedrock, Cave, Meadow, Grove, Field, Hill, Prairie, Thicket, Woodland, Clay Bank, Ravine, Gulch, Mesa, Plain |

Cam's reaction: most are good, but 15 single-element commons per element is too many to stay interesting; at least half of the 60 need revisiting later.

**Uncommons, 25 cards, numbers 61–85.** Two tags each, or one tag and an effect. Tags in all: fire 10, water 11, air 10, earth 11, plus one wildcard.

| No. | Card | Tags | Effect |
| --- | --- | --- | --- |
| 61 | Boiling Lake | fire, water | |
| 62 | Desert | fire, air | |
| 63 | Hot Spring | water, fire | |
| 64 | Badlands | fire, air | |
| 65 | Volcano | fire, earth | |
| 66 | Glacier | water | Play on earth permanence. It becomes water. |
| 67 | Basalt Columns | fire, earth | |
| 68 | Cloud Sea | water, air | |
| 69 | Delta | water, earth | |
| 70 | Fjord | water, earth | |
| 71 | Sea Cliff | earth, air | |
| 72 | Estuary | water, earth | |
| 73 | Mountain | earth, air | |
| 74 | Lava Lake | fire, fire | |
| 75 | Lake | water, water | |
| 76 | Highlands | air, air | |
| 77 | Forest | earth, earth | |
| 78 | Cloud Forest | air, water | |
| 79 | Salt Flat | fire | Choose one tag on any permanence. That tag doesn't count while Salt Flat stands. |
| 80 | Mirage | fire | Also copies the tags of the permanence played just before it. |
| 81 | Confluence | water, any | Also counts as one tag of any element, chosen at the end of the round. |
| 82 | Hanging Valley | air | Your air tags count double for affinity. |
| 83 | Echo Canyon | air | Also copies the tags of the next permanence played after it. |
| 84 | Hidden Valley | earth | Nothing can be played on your other permanence, and their tags can't be negated. |
| 85 | Petrified Forest | earth | Stays on the table into the next round, like an original. |

**Rares, 10 cards, numbers 86–95.** Three tags, or fewer and an effect. Tags: fire 7, water 7, air 7, earth 7.

| No. | Card | Tags | Effect |
| --- | --- | --- | --- |
| 86 | Geyser Basin | fire, water, air | |
| 87 | Ashen Range | fire, air, earth | |
| 88 | Caldera Lake | fire, earth, water | |
| 89 | Rainforest | water, air, earth | |
| 90 | Savanna | fire, fire, earth | |
| 91 | Stone Towers | air, air, earth | (name still open) |
| 92 | Dune Sea | fire, fire, air | |
| 93 | Archipelago | water, water, earth | Win the round with 10 water affinities. |
| 94 | Ice Sheet | water, water | Fire tags don't count, for either player, while Ice Sheet stands. |
| 95 | Mountain Range | earth, air | Every four earth tags you control also count as one world point. |

**Pinnacles, numbers 96–100.** Four tags of one element, no effect yet: Core (96, fire, the planet's core), Pangaea (97, earth, all land as one), Ocean (98, water, every sea as one), Trade Winds (99, air). Number 100 is reserved for the fifth pinnacle (one face, a move on the game itself, CARD-20).

**Whole pool so far (99 cards):** fire 36, water 37, air 36, earth 37 tags, plus one wildcard.

**Not yet placed:** the eight fifth-pillar cards (CARD-12). With every slot but #100 now holding an elemental card, they would take slots from elsewhere, most naturally from the commons Cam wants to trim.

---

## Second pass (Oct 29, 2026)

> First slice of the card pool: 40 landscape and force pairs, 10 per pillar, as of Oct 29, 2026 (second pass). These are Claude's picks, mostly from the Shortlist, and nothing here is Decided. Related design-doc entries: CARD-12 (pool structure), CARD-15 (paired faces), CARD-20 (scale sets rarity), CARD-21 (fiction where it helps, now parked), DUEL-22 (permanence is static, destruction is a moment) and DUEL-23 (landscapes, tags, strong and weak). The same cards are shown as rough card shapes on the [Card Pool Draft](https://claude.ai/artifact/TnuHoBYnpmHDF9DUriEQQQ) page.

## How the sample is built

- **Pairs.** Each card is a landscape (the Host's face) and the force that same place becomes or unleashes (the Guest's face).
- **Rarity by scale.** Commons are local, uncommons regional, rares continental. Pinnacles are planetary and are left out here.
- **Tags on the Host's face only.** Each tag makes the landscape strong or weak against an element. A card's row follows from its tags.
- **One rule for clashes.** When two tags disagree on the same element, the strength wins.
- **Cam's tests for a tag.** It has to be tied to the identity of the card's word and be in his lexicon for landscapes ("a sheltered canyon" works, "an absorbent marsh" doesn't). It shouldn't imply size, since scale already sets rarity. And tags have to be balanced across the pool: the working target is 15 to 20 tags, each on roughly 8 to 15 of the 92 Host faces, which is about 3 to 7 uses in a 40-card sample.
- **Air is the heights.** Earth is mass (the mountain); air is height (the summit, the spire, the ledge), inspired by the Air Nomads in Avatar: The Last Airbender and the floating islands in Avatar.
- **Marks:** \* is a word not on the Shortlist; † is fiction (CARD-21). The air pillar's forces are wind, so its column in the tables is Wind.

## Tags

| Tag | Effect | The feel | Example | Uses (of 40) |
| --- | --- | --- | --- | --- |
| High | Strong vs water | Above the floods | "a high cliff" | 8 |
| Low | Weak vs water | Water collects there | "a low valley" | 6 |
| Shallow | Weak vs water | Easily overrun | "a shallow pond" | 3 |
| Deep | Strong vs fire, strong vs wind | Below the surface | "a deep cave" | 3 |
| Steep | Weak vs earth | Slopes give way | "a steep hill" | 5 |
| Hollow | Weak vs earth | Caves in | "a hollow crater" | 2 |
| Loose | Weak vs earth, weak vs wind | Rolls, slides or blows away | "loose sand" | 4 |
| Cracked | Weak vs earth | Splits when the ground moves | "cracked bedrock" | 4 |
| Flat | Strong vs earth | Nothing to slide or fall | "a flat meadow" | 4 |
| Solid | Strong vs water, strong vs wind | Floods and wind go around it | "solid bedrock" | 4 |
| Rooted | Strong vs water, strong vs earth | Roots hold the soil | "a deep-rooted forest" | 3 |
| Floating | Strong vs water, strong vs earth | The ground and floods can't reach it | "a floating island" | 1 |
| Drifting | Strong vs earth, weak vs wind | Above the ground, but the wind moves it | "drifting clouds" | 1 |
| Wet | Strong vs fire | Won't burn | "a wet bog" | 7 |
| Dry | Weak vs fire | Tinder | "dry scrubland" | 2 |
| Wooded | Weak vs fire | Fuel | "a wooded valley" | 7 |
| Grassy | Weak vs fire | Burns fast | "a grassy hill" | 3 |
| Barren | Weak vs water | The ground can't drink | "barren ground" | 3 |
| Frozen | Weak vs fire | Heat melts it | "a frozen summit" | 3 |
| Volcanic | Strong vs fire, weak vs earth | Born of fire; a quake wakes it | "volcanic ground" | 3 |
| Sheltered | Strong vs wind | Walls break the wind | "a sheltered grove" | 4 |
| Exposed | Weak vs wind | Nothing breaks the wind | "an exposed cliff" | 6 |
| Weathered | Strong vs wind | It has already outlasted the wind | "a weathered spire" | 4 |

Held back for now: **Returning** (comes back after being cleared) and **Shrouded** (hides what's inside it). They aren't strengths or weaknesses but challenges of a different kind, and Returning still needs a word that passes the lexicon test.

## The sample

### Earth (10)

| Rarity | The Host's face | The Guest's face | Tags | Fire | Water | Earth | Wind |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Common | Boulder | Tremor | Solid, Loose | — | Strong | Weak | Strong |
| Common | Bedrock | Fissure | Solid, Cracked | — | Strong | Weak | Strong |
| Common | Cave | Collapse | Deep, Low, Hollow | Strong | Weak | Weak | Strong |
| Common | Hill | Mudslide | Steep, Grassy | Weak | — | Weak | — |
| Common | Grove | Decay | Wooded, Sheltered | Weak | — | — | Strong |
| Common | Meadow | Sinkhole | Grassy, Flat | Weak | — | Strong | — |
| Uncommon | Mountain | Landslide | High, Steep, Solid | — | Strong | Weak | Strong |
| Uncommon | Valley | Earthquake | Low, Sheltered, Wooded | Weak | Weak | — | Strong |
| Uncommon | Canyon | Erosion | Low, Steep, Sheltered | — | Weak | Weak | Strong |
| Rare | Rainforest | Overgrowth | Wooded, Wet, Rooted | Strong | Strong | Strong | — |

### Water (10)

| Rarity | The Host's face | The Guest's face | Tags | Fire | Water | Earth | Wind |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Common | Stream | Torrent | Wet, Shallow | Strong | Weak | — | — |
| Common | Pond | Cloudburst | Wet, Shallow | Strong | Weak | — | — |
| Common | Snowfield | Avalanche | Frozen, High, Loose | Weak | Strong | Weak | Weak |
| Common | Cove | Whirlpool | Deep | Strong | — | — | Strong |
| Common | Lagoon | Surge | Wet, Shallow | Strong | Weak | — | — |
| Common | Bog | Quicksand | Wet, Flat | Strong | — | Strong | — |
| Uncommon | River | Flood | Wet, Low | Strong | Weak | — | — |
| Uncommon | Marsh | Monsoon | Wet, Low | Strong | Weak | — | — |
| Uncommon | Glacier | Iceberg | Frozen, Solid | Weak | Strong | — | Strong |
| Rare | Reef | Tsunami | Deep, Rooted | Strong | Strong | Strong | Strong |

### Fire (10)

| Rarity | The Host's face | The Guest's face | Tags | Fire | Water | Earth | Wind |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Common | Flint | Spark\* | Cracked | — | — | Weak | — |
| Common | Obsidian | Lava | Volcanic, Barren | Strong | Weak | Weak | — |
| Common | Crater | Meteor | Low, Barren, Hollow | — | Weak | Weak | — |
| Common | Geyser | Steam\* | Volcanic | Strong | — | Weak | — |
| Common | Scrubland | Wildfire | Dry, Exposed | Weak | — | — | Weak |
| Common | Glade | Lightning | Wooded, Sheltered | Weak | — | — | Strong |
| Uncommon | Volcano | Eruption | Volcanic, Steep | Strong | — | Weak | — |
| Uncommon | Badlands | Heatwave | High, Cracked, Exposed | — | Strong | Weak | Weak |
| Uncommon | Savanna | Firestorm | Grassy, Dry, Flat | Weak | — | Strong | — |
| Rare | Desert | Drought | Barren, Flat, Loose | — | Weak | Strong | Weak |

### Air (10)

| Rarity | The Host's face | The Guest's face | Tags | Fire | Water | Earth | Wind |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Common | Ledge\* | Gust | Loose, Exposed | — | — | Weak | Weak |
| Common | Spire\* | Whirlwind | High, Exposed | — | Strong | — | Weak |
| Common | Sea stack\* | Waterspout | Weathered | — | — | — | Strong |
| Common | Stone pillar\* | Sandstorm | Weathered, Cracked | — | — | Weak | Strong |
| Common | Cliff | Storm | High, Steep, Exposed | — | Strong | Weak | Weak |
| Common | Summit\* | Blizzard | High, Frozen, Exposed | Weak | Strong | — | Weak |
| Uncommon | Sky island\* | Thunderstorm | High, Wooded, Rooted | Weak | Strong | Strong | — |
| Uncommon | Stone forest\* | Tornado | Weathered, Wooded | Weak | — | — | Strong |
| Uncommon | Cloud sea\* | Supercell | Drifting, High | — | Strong | Strong | Weak |
| Rare | Floating island†\* | Hurricane | Floating, Weathered, Wooded | Weak | Strong | Strong | Strong |

## Balance check

**Tags:** 23 tags. Most land in the 3 to 7 range. High is just over, at 8. Hollow and Dry are on 2 cards, and the two new air tags, Floating and Drifting, on 1 each.

**Elements:** how many of the 40 landscapes each element beats, and how many hold against it.

| Element | Beats | Resisted by |
| --- | --- | --- |
| Fire | 13 | 13 |
| Water | 11 | 14 |
| Earth | 16 | 9 |
| Wind | 9 | 15 |

**Rarity:** the ladder shows up on its own. Rares hold against almost three elements on average.

| Rarity | Cards | Avg. strengths | Avg. weaknesses |
| --- | --- | --- | --- |
| Common | 24 | 1.0 | 1.3 |
| Uncommon | 12 | 1.3 | 1.2 |
| Rare | 4 | 2.8 | 0.8 |

**Pillars:** how sturdy each pillar's landscapes are.

| Pillar | Cards | Avg. strengths | Avg. weaknesses |
| --- | --- | --- | --- |
| Earth | 10 | 1.5 | 1.3 |
| Water | 10 | 1.6 | 0.9 |
| Fire | 10 | 0.7 | 1.5 |
| Air | 10 | 1.3 | 1.2 |

## What changed in the second pass

- **Air redrafted around the heights,** 10 cards instead of 8, with one fiction card (the Floating island). Cliff moved over from earth.
- **Set aside from air:** Dune, Moor, Field, Island, Prairie, Steppe, Tundra and Plateau. Several could come back under earth in the full pool.
- **Every pillar is now 10 cards.** Stone dropped out of earth.
- **Massive became Solid.** It describes what something is made of, not how big it is.
- **New tags:** Weathered (strong vs wind), Floating (strong vs earth and water), Drifting (strong vs earth, weak vs wind).

## What changed in the first pass

- **Barren is neutral to fire.** Nothing to burn means neutral, not strong, the same logic as Cam's canyon. It keeps its weakness to water (the ground can't drink).
- **Grassy is no longer strong against wind.** It only burns fast.
- **Rooted also holds against earth,** since roots hold slopes together.
- **Merged:** Restless into Volcanic, and Shifting into Loose.
- **Added:** Shallow for small bodies of water, so Low stays with low ground. Cracked replaces Faulted.
- **Dropped:** Remote and Tall.

## Gaps and open questions

- **Cam's first reactions (Oct 29).** Massive was out: it sounds bad, and it doesn't fit small things like a stone. The first air cards didn't feel like air. Both are addressed in the second pass.
- **Cam on the second pass (Oct 29).** Air is going to need a lot of work: a couple seem fine, most aren't good. Earth, water and fire are more than 50% good, so it's the right track. Fiction is parked for now (CARD-21), so the Floating island is on hold.
- **Earth still beats the most cards, and wind the fewest.** Earth beats 16 and is resisted by 9; wind beats 9 and is resisted by 15. The heights help air hold against earth, but much of the pool is still rock that falls when the ground moves.
- **Fire's landscapes are the weakest.** Fire's natural ground is barren or dry. Fiction could give fire sturdier ground, such as a flame that keeps burning in the rain (CARD-21).
- **Fire is two forces in one column.** Flame and drought both belong to fire, and they don't always hit the same things (a marsh holds against flame but dies in a drought).
- **Five cards have no weakness:** Rainforest, Cove, Bog, Reef and Sea stack. Only raw force clears them. That may be fine, but it's worth testing.
- **The Guest's faces have no tags yet.** Only the landscapes have been tagged.
- **The rarity mix runs a little high.** The sample is 24 common, 12 uncommon and 4 rare. The pool's elemental cards are 60, 20 and 8.
- **Most air words aren't on the Shortlist,** since it had almost no air landscapes. Spark and Steam aren't either.
