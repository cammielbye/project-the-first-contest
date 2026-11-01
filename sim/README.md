# Contest simulator

Two AI players play contests between two test binders, using the current loop
(world points, the affinity tie-break, best of three, Gwent-style passing, a cap
of 10 cards a round) and the cards in `data/cards.json` and `data/binders.json`.
It reads the same data as the table, so after a card-pool sync it plays the new
cards.

```sh
node sim/sim.js 200                      # 200 contests, the first two binders
node sim/sim.js 200 --style noforces     # same, with no force faces (a control)
node sim/sim.js 500 --seed 7 --workers 2 # more contests, another seed
node sim/show.js sim/out/main-200-1.json 0 1   # read contests 0 and 1 move by move
node sim/test-rules.js                   # check key rules on hand-built positions
```

`npm run sim -- 200` works too. A contest takes about a second of CPU, and
`--workers` (default: all cores) splits the run. Each binder sits in each seat
half the time. Results go to `sim/out/` (not committed): every contest, and a
`-summary.json` with the stats the run prints.

Styles:

- `main`: the AI tries every legal move, looks at the opponent's best reply to
  the strongest few, and weighs the gain against the cost of spending the card
  (cards the later rounds can't use are nearly free). It passes when it's ahead
  and the opponent can't catch up, and only chases a round it can win without
  falling far behind on cards.
- `thrifty`: values its cards 2.5 times as much, so it passes sooner.
- `greedy`: no lookahead.
- `noforces`: never plays a force face.

The AI is a heuristic player, not a strong one, and both seats use the same
logic. Read results as trends, not balance numbers. It plays straightforward
removal better than combos that need several cards to survive together.

## Files

| File | What it does |
| --- | --- |
| `engine.js` | The table: worlds (a 2×2, connected by sides), scoring, the tie-break, protections. |
| `moves.js` | Every legal move for every card, and what each does. |
| `ai.js` | The AI player. |
| `game.js` | One contest: rounds, turns, passing, the void between rounds. |
| `stats.js` | Turns contests into stats, keyed by binder. |
| `sim.js` | The command above. |
| `show.js` | Prints contests move by move. |
| `test-rules.js` | Rule checks. |

## New cards

Every effect is written by hand in `moves.js` (what a force can target and what
it does) and `engine.js` (how a lasting effect changes scoring). A card whose
force or meta text isn't written yet stops the run with
`force not implemented: <name>` or `meta not implemented: <name>`, so new
cards are never silently ignored. Permanence text is matched by card name in
`engine.js` (for example Mountain Range, Archipelago, Ice Sheet, Thicket).

## Readings of open rules

Where the rules are still open, the simulator picks one reading. Change them in
the code marked `READING`:

- A drawn round counts as a win for both players, as in Gwent.
- The round 1 opener is random; openers alternate after that.
- "Also counts as X" lets a card count as its own element or X.
- "Return to binder" isn't removal, so Bedrock, Shelter, Freeze and Thicket don't stop it.
- Glacier turns the target's earth affinities to water. Mirage copies the
  printed affinities of one card it touches.
- Ice Sheet stops fire affinities for both players while it's in a world.
- Echo plays a card's permanence face from the void as part of the same play.
  Verge allows up to two more plays that turn, each counting toward the cap.
- Petrified Forest stays one extra round. Spring and Grove return to the binder
  at round end; everything else goes to the void.
- Both AIs see each other's binders, so Horizon does nothing.
- For the stake stat, the winner picks the rarest card the loser played.
