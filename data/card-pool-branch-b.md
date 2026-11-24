# Branch B card pool (first draft, Nov 23, 2026)

> Cam (Nov 23): "let's get the card pool back into a 100 card playable state like it once was. Find the last 100 card pool and update it with any changes we've made to core rules since then." On the fronts: "return the abilities to the idea pool so we don't forget about them, then create the card pool list view like before so I can look through the pool (front and back)." The void and meta cards: "Keep both". Blockers: "A cycle of eight". Everything else is Claude's draft against Branch B's settled rules, not adopted.

Source: the sixth pass (design/card-pool.md; data/cards.json in the playtest repo). Data: data/cards-branch-b.json. Made by tools/cards/branchb_pool.py.

**What changed, and why.**
- **Fronts are vanilla.** The 38 front abilities are in the idea pool (listed below). The only front text left is the blockers'.
- **Blockers, a cycle of eight** (two commons per element): Lava Flow, Ice Floe, Shoal, Hill, Meadow, Dune, Ridge, Eyrie. "Can be played on an opponent's world."
- **Backs have pips.** Most cards lose a pip when flipped, and every one-pip card but Bedrock loses its only pip. Counts: 33 lose every pip, 48 lose some, 3 keep every pip, 2 have none on either side; 3 change element where it's thematic (mud, obsidian, a lava coast making land).
- **Durations.** "Lasts the round" (one round now) is "while flipped": the effect lives on the flipped card, as Cave-in's does, and ends if the card is flipped back or leaves play. 74 once, 7 until your next turn, 5 while flipped.
- **Forces on the table are flipped cards,** so "remove a force" is "flip back" (Thaw, Sunlight).
- **The extra plays are back.** They went to the idea pool on Nov 12 because "with uncapped turns, playing extra cards in a row doesnt do anything" (Cam). A Branch B turn has one landscape, so they matter again: 14 cards.
- **8 cards flip back on their own,** from natural cycles: Tide Pool, Snowfield, Grove, Mud Pots, Savanna, Spring, Tidal Flat, Mirage.
- **Meta cards** are played in place of the turn's landscape, then go to the void (Claude's reading). Six changed words for the new turn: Calm, Aftershock, Stillness, Sunlight, Thunder, Haze.
- **Rarities** are unchanged. The four one-pip rares (Ice Sheet, Thicket, Badlands, Wind Gap) and the two no-pip uncommons (Mirage, Hanging Valley) were rare for their front text, which is now in the idea pool.

## Landscapes (86)

| No. | Card | Rarity | Front pips | Front text | Force | Back pips | Duration | Back text |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Glacier | C | 1 water | — | Thaw | none | Once | Flip back a common permanence. |
| 2 | Bedrock | C | 1 earth | — | Tangle | 1 earth | Until your next turn | No common forces until your next turn. |
| 3 | Lava Field | C | 1 fire | — | Ash | none | Once | Remove a common permanence. |
| 4 | Spire | C | 1 air | — | Whirlwind | none | Once | Split one of your worlds. |
| 5 | Tide Pool | C | 1 water | — | Drizzle | none | Once, flips back | Return a card from your void. Next turn, flip this back. |
| 6 | Stone Field | C | 1 earth | — | Dust | none | Until your next turn | No common forces until your next turn. |
| 7 | Ashfield | C | 1 fire | — | Brushfire | none | While flipped | One of your permanences becomes fire. |
| 8 | Summit | C | 1 air | — | Crosswind | none | Once | Swap two common permanences. |
| 9 | Snowfield | C | 1 water | — | Freeze | none | Once, flips back | Play a permanence from your void. Next turn, flip this back. |
| 10 | Grove | C | 1 earth | — | Overgrowth | none | Once, flips back | Play another earth permanence this turn. Next turn, flip this back. |
| 11 | Lava Flow | C | 1 fire | Can be played on an opponent's world. | Lightning | none | Once | Remove a common permanence. |
| 12 | Bluff | C | 1 air | — | Eddy | none | Once | Swap two of your permanences. |
| 13 | Marsh | C | 1 water or earth | — | Mire | none | Once | Return a card from your void. |
| 14 | Steam Vent | C | 1 water or fire | — | Vent | none | Once | Return one of your permanences. |
| 15 | Sea Stack | C | 1 water or air | — | Riptide | none | While flipped | One of your permanences becomes water. |
| 16 | Flint | C | 1 earth or fire | — | Spark | none | Once | Play another fire permanence this turn. |
| 17 | Pass | C | 1 earth or air | — | Whirl | none | Once | Move a common permanence to another world. |
| 18 | Scrubland | C | 1 fire or air | — | Dust Devil | none | While flipped | One of your permanences becomes air. |
| 19 | Wilderness | C | 1 any | — | Thunderstorm | none | Once | Remove a common permanence. |
| 20 | Delta | B | 1 water, 1 earth | — | Flood | 1 water | Once | Return two of your permanences. |
| 21 | Hot Spring | B | 1 water, 1 fire | — | Scald | 1 water | Once | Remove an uncommon permanence. |
| 22 | Cloud Forest | B | 1 water, 1 air | — | Fog | 1 water | Until your next turn | No uncommon forces until your next turn. |
| 23 | Volcano | B | 1 earth, 1 fire | — | Lava Bomb | 1 fire | Once | Remove an uncommon permanence. |
| 24 | Sea Cliff | B | 1 earth, 1 air | — | Gale | 1 air | Once | Move an uncommon permanence to another world. |
| 25 | Desert | B | 1 fire, 1 air | — | Heatwave | 1 fire | Once | Play another permanence this turn. |
| 26 | Mangrove | B | 1 water, 1 earth | — | Undertow | 1 earth | Once | Return one of your worlds. |
| 27 | Mud Pots | B | 1 water, 1 fire | — | Downpour | 1 earth | Once, flips back | Play a permanence from your void. Next turn, flip this back. |
| 28 | Waterfall | B | 1 water, 1 air | — | Cloudburst | 1 water | Once | Return two cards from your void. |
| 29 | Cinder Cone | B | 1 earth, 1 fire | — | Ashfall | 1 earth | Once | Split one of your worlds. |
| 30 | Canyon | B | 1 earth, 1 air | — | Dust Storm | 1 earth | Once | Swap two of your permanences. |
| 31 | Savanna | B | 1 fire, 1 air | — | Sandstorm | 1 air | Once, flips back | Play another permanence this turn. Next turn, flip this back. |
| 32 | Spring | B | 1 water, 1 fire | — | Low Tide | 1 water | Once, flips back | Return one of your worlds. Next turn, flip this back. |
| 33 | Mountain Range | B | 1 earth, 1 air | — | Rockslide | 1 earth | Once | Move one of your permanences. |
| 34 | Fumarole | B | 1 fire, 1 air | — | Flare-up | 1 air | Until your next turn | No uncommon forces until your next turn. |
| 35 | Sky Isle | B | 1 air, 1 any | — | Waterspout | 1 air | Once | Split one of your worlds. |
| 36 | Tidal Flat | B | 1 water, 1 any | — | Hail | 1 water | Once, flips back | Return two of your permanences. Next turn, flip this back. |
| 37 | Old Growth | B | 1 earth, 1 any | — | Bramble | 1 earth, 1 any | Until your next turn | No uncommon forces until your next turn. |
| 38 | Obsidian | B | 1 fire, 1 any | — | Scorch | 1 earth | Once | Remove an uncommon permanence. |
| 39 | Hidden Valley | B | 2 any | — | Landslide | 1 any | Once | An uncommon permanence becomes its own world. |
| 40 | Deep Lake | B | 2 water | — | Ice Storm | 1 water | Once | Return two cards from your void. |
| 41 | Plateau | B | 2 earth | — | Permafrost | 2 earth | Once | Play another permanence this turn. |
| 42 | Lava Lake | B | 2 fire | — | Heat Dome | 1 fire | Once | Play another fire permanence this turn. |
| 43 | Twin Peaks | B | 2 air | — | High Pressure | 1 air | Once | Swap two of your permanences. |
| 44 | Mirage | B | none | — | Heat Shimmer | none | Once, flips back | Move one of your permanences. Next turn, flip this back. |
| 45 | Caldera Lake | A | 1 water, 1 earth, 1 fire | — | Collapse | 1 water, 1 earth | Once | Remove a rare permanence. |
| 46 | Rainforest | A | 1 water, 1 earth, 1 air | — | Monsoon | 1 water, 1 earth | Once | Play a card from your void. |
| 47 | Geyser Basin | A | 1 water, 1 fire, 1 air | — | Typhoon | 1 water, 1 fire | Once | Move two of your permanences. |
| 48 | Red Canyon | A | 1 earth, 1 fire, 1 air | — | Erosion | 1 earth, 1 fire | Once | Return two of your worlds. |
| 49 | Archipelago | A | 2 water, 1 earth | — | Surge | 2 water | Once | Return three cards from your void. |
| 50 | Boiling Lake | A | 2 water, 1 fire | — | Torrent | 2 water | Once | Play a card from your void. |
| 51 | Misty Fjord | A | 2 water, 1 air | — | Whiteout | 2 water | Once | Play a card from your void. |
| 52 | Floodplain | A | 1 water, 2 earth | — | Mudflow | 1 water, 1 earth | Once | Return two of your worlds. |
| 53 | Smoking Hills | A | 2 earth, 1 fire | — | Eruption | 2 earth | Once | Play two more permanences this turn. |
| 54 | Highlands | A | 2 earth, 1 air | — | Earthquake | 2 earth | Once | Return two of your worlds. |
| 55 | Lava Coast | A | 1 water, 2 fire | — | Steam Explosion | 1 water, 1 earth | Once | Play two more permanences this turn. |
| 56 | Lava Plain | A | 1 earth, 2 fire | — | Magma | 1 earth, 1 fire | Once | Play two more permanences this turn. |
| 57 | Sand Sea | A | 2 fire, 1 air | — | Supercell | 1 fire, 1 air | Once | Play two more permanences this turn. |
| 58 | Cloud Sea | A | 1 water, 2 air | — | Hurricane | 1 water | Once | Move two of your permanences. |
| 59 | Stone Towers | A | 1 earth, 2 air | — | Gale Force | 1 earth, 1 air | Once | Move two of your permanences. |
| 60 | High Desert | A | 1 fire, 2 air | — | Tornado | 1 fire, 1 air | Once | Return the last two permanences you played. |
| 61 | Lagoon | A | 3 water | — | Flash Flood | 2 water | Once | Return three cards from your void. |
| 62 | Moor | A | 3 earth | — | Avalanche | 2 earth | Once | Return two of your worlds. |
| 63 | Cinder Field | A | 3 fire | — | Wildfire | 2 fire | Once | Play two more permanences this turn. |
| 64 | Peak | A | 3 air | — | Drought | 2 air | Once | Move two of your permanences. |
| 65 | Ice Sheet | A | 1 water | — | Blizzard | none | Until your next turn | No rare forces until your next turn. |
| 66 | Thicket | A | 1 earth | — | Shelter | none | Until your next turn | No rare forces until your next turn. |
| 67 | Badlands | A | 1 fire | — | Ember | none | Once | Play two more permanences this turn. |
| 68 | Wind Gap | A | 1 air | — | Downdraft | none | Once | A rare permanence becomes its own world. |
| 83 | Ice Floe | C | 1 water | Can be played on an opponent's world. | Current | none | Once | Play a permanence from your void. |
| 84 | Shoal | C | 1 water | Can be played on an opponent's world. | Mist | none | Once | Move one of your permanences. |
| 85 | Fen | B | 1 water, 1 earth | — | Whirlpool | 1 water | Once | Play a card from a void. |
| 86 | Hill | C | 1 earth | Can be played on an opponent's world. | Rockfall | none | While flipped | One of your permanences becomes earth. |
| 87 | Meadow | C | 1 earth | Can be played on an opponent's world. | Mudslide | none | Once | Move one of your permanences. |
| 88 | Cavern | C | 1 earth | — | Sinkhole | none | While flipped | This world ignores your opponent's forces. |
| 89 | Dune | C | 1 fire | Can be played on an opponent's world. | Updraft | none | Once | Play another fire permanence this turn. |
| 90 | Barrens | C | 1 fire | — | Smoke | none | Once | Swap two of your permanences. |
| 91 | Crater | B | 1 earth, 1 fire | — | Meteor | 1 earth | Once | Play two more fire permanences this turn. |
| 92 | Ledge | C | 1 air | — | Gust | none | Once | A common permanence becomes its own world. |
| 93 | Ridge | C | 1 air | Can be played on an opponent's world. | Breeze | none | Once | Move one of your permanences. |
| 94 | Eyrie | C | 1 air | Can be played on an opponent's world. | Cyclone | none | Once | Return the last permanence you played. |
| 95 | Hanging Valley | B | none | — | Squall | none | Once | Swap two of your permanences. |
| 96 | Ocean | S | 4 water | — | Tsunami | 2 water | Once | Return a player's worlds. |
| 97 | Pangaea | S | 4 earth | — | World Quake | 2 earth | Once | Split every world. |
| 98 | Core | S | 4 fire | — | Firestorm | 2 fire | Once | Remove a world. |
| 99 | Trade Winds | S | 4 air | — | Jet Stream | 2 air | Once | Every permanence becomes its own world. |
| 100 | Origin | S | 1 water, 1 earth, 1 fire, 1 air | — | Unmaking | none | Once | Remove every world. |

## Meta cards (14)

Played in place of the turn's landscape.

| No. | Card | Text |
| --- | --- | --- |
| 69 | Echo | Play a card from your void. |
| 70 | Hollow | Return a card from your void. |
| 71 | Equinox | Return 3 cards from your void. |
| 72 | Verge | Play two more cards this turn. |
| 73 | Lull | Your opponent skips their next turn. |
| 74 | Ebb | Remove your opponent's last common. |
| 75 | Horizon | Remove a card from your opponent's binder. |
| 76 | Calm | No forces until your next turn. | was "No forces this round."
| 77 | Aftershock | Your opponent has the next two turns. | was "Your opponent takes the next two turns."
| 78 | Stillness | Your opponent plays no permanence next turn. | was "Your opponent passes."
| 79 | Sunlight | Flip back every permanence. | was "Remove every force."
| 80 | Weathering | Return the last card your opponent played. |
| 81 | Thunder | Play a permanence after the last turn. | was "Play once more after both players pass."
| 82 | Haze | Your opponent can't use forces next turn. | was "Your opponent can't play forces next turn."

## Front abilities, now in the idea pool (38)

- "Your opponent can't move this." (Glacier, Bedrock, Lava Field, Spire)
- "Unaffected by your opponent's forces." (Tide Pool, Stone Field, Ashfield, Summit)
- "When played, return one of your permanences." (Snowfield)
- "When played, remove a common force." (Grove)
- "When played, move one of your permanences." (Bluff)
- "Score a point per four water affinities." (Spring)
- "Score a point per four earth affinities." (Mountain Range)
- "Score a point per four fire affinities." (Fumarole)
- "Score a point per four air affinities." (Sky Isle)
- "Copies every adjacent permanence's affinities." (Mirage)
- "Play only on a new world." (Caldera Lake, Rainforest, Geyser Basin, Red Canyon)
- "Play only on your first turn." (Lagoon, Moor, Cinder Field, Peak)
- "Each permanence in its world gains water." (Ice Sheet)
- "Each permanence in its world gains earth." (Thicket)
- "Each permanence in its world gains fire." (Badlands)
- "Each permanence in its world gains air." (Wind Gap)
- "+1 water if you have a world point." (Ice Floe)
- "The permanence below this gains water." (Shoal)
- "+1 earth if you have a world point." (Hill)
- "The permanence beside this gains earth." (Meadow)
- "Your opponent can't split its world." (Cavern)
- "+1 fire if you have a world point." (Dune)
- "The permanence across from this gains fire." (Barrens)
- "+1 air if you have a world point." (Ledge)
- "The permanence above this gains air." (Ridge)
- "+1 world point if this world has water earth fire air." (Hanging Valley)
