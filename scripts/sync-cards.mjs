// Turns data/card-pool.md into data/cards.json for the playtest page.
//
// Usage: node scripts/sync-cards.mjs [path/to/card-pool.md]
//
// Only the part of the file above the first "---" line is read; the older
// passes below it are kept for reference and ignored. The script recognises
// tables by their header row, so section titles and prose can change freely:
//   | Element | Numbers | Cards |                       commons, one tag each
//   | No. | Card | Tags | Effect |                      uncommons and rares
//   | No. | Permanence | Force | Rarity | Duration | … |  force faces
// plus the "**Pinnacles…**" paragraph: "Core (96, fire, …)".
// Anything it can't place is reported as a warning rather than guessed.

import { readFileSync, writeFileSync } from "node:fs";
import { dirname, join, relative } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const srcPath = process.argv[2] || join(root, "data", "card-pool.md");
const outPath = join(root, "data", "cards.json");

const ELEMENTS = ["fire", "water", "air", "earth"];
const RARITY_BY_WORD = { commons: "C", uncommons: "B", rares: "A", pinnacles: "S" };

const warnings = [];
const cards = new Map(); // no -> card

function warn(msg) {
  warnings.push(msg);
}

function cleanText(s) {
  return s.replace(/\\\*/g, "*").replace(/\*\*/g, "").trim();
}

function parseTags(cell, where) {
  const tags = [];
  for (const raw of cell.split(",")) {
    const t = raw.trim().toLowerCase();
    if (!t) continue;
    if (ELEMENTS.includes(t) || t === "any") tags.push(t);
    else warn(`${where}: unknown tag "${raw.trim()}" ignored`);
  }
  return tags;
}

function rarityFromNumber(no) {
  if (no >= 1 && no <= 60) return "C";
  if (no >= 61 && no <= 85) return "B";
  if (no >= 86 && no <= 95) return "A";
  if (no >= 96 && no <= 100) return "S";
  return null;
}

function addCard(card, where) {
  if (cards.has(card.no)) {
    const prev = cards.get(card.no);
    throw new Error(
      `${where}: card #${card.no} (${card.permanence.name}) clashes with #${prev.no} (${prev.permanence.name})`
    );
  }
  cards.set(card.no, card);
}

function splitRow(line) {
  // "| a | b | c |" -> ["a","b","c"]; keeps empty cells
  let s = line.trim();
  if (s.startsWith("|")) s = s.slice(1);
  if (s.endsWith("|")) s = s.slice(0, -1);
  return s.split("|").map((c) => c.trim());
}

const isSeparator = (line) => /^\s*\|?\s*:?-{3,}/.test(line) && /-{3,}/.test(line) && !/[A-Za-z]/.test(line);

const text = readFileSync(srcPath, "utf8");
const allLines = text.split(/\r?\n/);
const hrIndex = allLines.findIndex((l) => /^\s*-{3,}\s*$/.test(l));
const lines = hrIndex === -1 ? allLines : allLines.slice(0, hrIndex);
if (hrIndex === -1) warn('No "---" line found; read the whole file.');

let context = null; // last rarity word seen in a bold lead paragraph
const forces = [];

for (let i = 0; i < lines.length; i++) {
  const line = lines[i];

  const lead = line.match(/^\*\*(Commons|Uncommons|Rares|Pinnacles)\b/i);
  if (lead) {
    context = lead[1].toLowerCase();
    if (context === "pinnacles") {
      const re = /([A-Z][A-Za-z' -]+?) \((\d+), (fire|water|air|earth)\b/g;
      let m;
      let found = 0;
      while ((m = re.exec(line))) {
        const no = Number(m[2]);
        const el = m[3];
        addCard(
          {
            no,
            rarity: "S",
            permanence: { name: m[1].trim(), tags: [el, el, el, el], effect: "" },
            force: null,
          },
          `Pinnacles line`
        );
        found++;
      }
      if (!found) warn("Pinnacles paragraph found but no pinnacles could be read from it.");
    }
    continue;
  }

  // Table start: a row followed by a separator row.
  if (line.trim().startsWith("|") && i + 1 < lines.length && isSeparator(lines[i + 1])) {
    const header = splitRow(line).map((h) => h.toLowerCase());
    const rows = [];
    let j = i + 2;
    while (j < lines.length && lines[j].trim().startsWith("|")) {
      rows.push(splitRow(lines[j]));
      j++;
    }
    i = j - 1;

    const has = (word) => header.some((h) => h.includes(word));

    if (has("permanence") && has("force") && has("duration")) {
      const col = (word) => header.findIndex((h) => h.includes(word));
      const c = {
        no: col("no"),
        perm: col("permanence"),
        force: col("force"),
        rarity: col("rarity"),
        duration: col("duration"),
        effect: header.findIndex((h) => h.includes("does") || h.includes("effect")),
      };
      for (const r of rows) {
        forces.push({
          no: Number(r[c.no]),
          permName: cleanText(r[c.perm] || ""),
          name: cleanText(r[c.force] || ""),
          rarity: (r[c.rarity] || "").trim(),
          duration: cleanText(r[c.duration] || ""),
          effect: cleanText(r[c.effect] || ""),
        });
      }
    } else if (header[0] === "element" && has("numbers") && has("cards")) {
      for (const r of rows) {
        const el = r[0].trim().toLowerCase();
        if (!ELEMENTS.includes(el)) {
          warn(`Commons table: unknown element "${r[0]}" skipped`);
          continue;
        }
        const range = r[1].match(/(\d+)\s*[–—-]\s*(\d+)/);
        const names = r[2].split(",").map((n) => cleanText(n)).filter(Boolean);
        if (!range) {
          warn(`Commons table: can't read the number range "${r[1]}" for ${el}`);
          continue;
        }
        const start = Number(range[1]);
        const end = Number(range[2]);
        if (end - start + 1 !== names.length) {
          warn(`Commons table: ${el} lists ${names.length} cards for numbers ${start}–${end}`);
        }
        names.forEach((name, k) => {
          const no = start + k;
          addCard(
            { no, rarity: "C", permanence: { name, tags: [el], effect: "" }, force: null },
            `Commons (${el})`
          );
        });
      }
    } else if (has("no") && has("card") && has("tags")) {
      const col = (word) => header.findIndex((h) => h.includes(word));
      const c = { no: col("no"), name: col("card"), tags: col("tags"), effect: col("effect") };
      for (const r of rows) {
        const no = Number(r[c.no]);
        if (!Number.isInteger(no)) {
          warn(`Numbered table: row without a number skipped (${r.join(" | ")})`);
          continue;
        }
        const rarity = RARITY_BY_WORD[context] || rarityFromNumber(no);
        const fromNo = rarityFromNumber(no);
        if (fromNo && rarity !== fromNo) {
          warn(`#${no}: listed under ${context} (${rarity}) but its number falls in the ${fromNo} band`);
        }
        let effect = c.effect >= 0 ? cleanText(r[c.effect] || "") : "";
        let note = "";
        if (/^\(.*\)$/.test(effect)) {
          note = effect.slice(1, -1);
          effect = "";
        }
        const perm = { name: cleanText(r[c.name]), tags: parseTags(r[c.tags] || "", `#${no}`), effect };
        if (note) perm.note = note;
        addCard({ no, rarity, permanence: perm, force: null }, `#${no}`);
      }
    } else {
      warn(`Unrecognised table skipped (header: ${header.join(" | ")})`);
    }
  }
}

// Attach force faces.
for (const f of forces) {
  const card = cards.get(f.no);
  if (!card) {
    warn(`Force ${f.name} names card #${f.no}, which isn't in the pool`);
    continue;
  }
  if (f.permName && f.permName !== card.permanence.name) {
    warn(`Force ${f.name} (#${f.no}) is paired with "${f.permName}", but #${f.no} is "${card.permanence.name}"`);
  }
  if (f.rarity && f.rarity !== card.rarity) {
    warn(`Force ${f.name} (#${f.no}) says rarity ${f.rarity}, the card is ${card.rarity}`);
  }
  card.force = { name: f.name, duration: f.duration, effect: f.effect };
}

// Gaps in the numbering.
const nos = [...cards.keys()].sort((a, b) => a - b);
const max = Math.max(100, ...nos);
const missing = [];
for (let n = 1; n <= max; n++) if (!cards.has(n)) missing.push(n);

const list = nos.map((n) => cards.get(n));
const withForce = list.filter((c) => c.force).length;

const out = {
  source: relative(root, srcPath),
  syncedAt: new Date().toISOString(),
  counts: {
    cards: list.length,
    withForceFace: withForce,
    byRarity: Object.fromEntries(["C", "B", "A", "S"].map((r) => [r, list.filter((c) => c.rarity === r).length])),
    tags: Object.fromEntries(
      [...ELEMENTS, "any"].map((e) => [e, list.reduce((s, c) => s + c.permanence.tags.filter((t) => t === e).length, 0)])
    ),
  },
  missingNumbers: missing,
  warnings,
  cards: list,
};

writeFileSync(outPath, JSON.stringify(out, null, 2) + "\n");

console.log(`Read ${relative(root, srcPath)} → ${relative(root, outPath)}`);
console.log(`  ${list.length} cards (${JSON.stringify(out.counts.byRarity)}), ${withForce} with a force face`);
console.log(`  tags: ${JSON.stringify(out.counts.tags)}`);
if (missing.length) console.log(`  numbers not in the pool: ${missing.join(", ")}`);
for (const w of warnings) console.log(`  warning: ${w}`);
