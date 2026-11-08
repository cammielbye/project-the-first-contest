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
| `card-pool-2026-11-08-fourth-pass-placeholders.md` | `saved/card-pool-2026-11-08-fourth-pass-placeholders` (HASH) | The fourth pass with twelve unnamed placeholders (Nov 8), before they took names from cut cards. |
