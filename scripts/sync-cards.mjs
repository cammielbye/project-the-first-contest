// Turns data/card-pool.md into data/cards.json and data/binders.json.
//
// Usage: node scripts/sync-cards.mjs [path/to/card-pool.md]
//
// Only the most recent pass is used. The card pool puts its newest pass at
// the top, so the script reads the first "## " section that defines cards and
// stops at the next "## " heading. Older passes (and anything below a "---"
// line) are ignored entirely, so the table always matches the latest draft.
//
// Tables are recognised by their header row, so titles and prose can change:
//   | No. | Permanence | Rarity | Affinities | Permanence text | Force | Duration | Force text |
//   | No. | Permanence | Force | Rarity | Duration | What the force does |   (force faces only)
//   | Element | Numbers | Cards |                                         (one-affinity commons)
//   | No. | Card | Tags (or Affinities) | Effect |                         (permanence only)
//   | Card | Text |   after a "**Fifth-pillar meta…**" line                 (meta cards)
// plus a "**Pinnacles, numbers…**" paragraph ("Core (96, fire, …)") and
// binder bullets: "- **Binder A, Tides.** Description. Card, Card, Card."

import { existsSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join, relative } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const srcPath = process.argv[2] || join(root, "data", "card-pool.md");
const cardsOut = join(root, "data", "cards.json");
const bindersOut = join(root, "data", "binders.json");

const ELEMENTS = ["fire", "water", "air", "earth"];
const RARITY_BY_WORD = { commons: "C", uncommons: "B", rares: "A", pinnacles: "S" };

const warnings = [];
const warn = (msg) => warnings.push(msg);

const clean = (s) => (s || "").replace(/\\\*/g, "*").replace(/\*\*/g, "").trim();
const text = (s) => {
  const t = clean(s);
  return t === "—" || t === "-" ? "" : t;
};
const slug = (s) => s.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");

function rarityFromNumber(no) {
  if (no >= 1 && no <= 60) return "C";
  if (no >= 61 && no <= 85) return "B";
  if (no >= 86 && no <= 95) return "A";
  if (no >= 96 && no <= 100) return "S";
  return null;
}

// "1 fire, 1 water" | "2 air, 1 earth" | "fire, water" | "water, any"
// | "1 either-or (fire or earth)" -> "fire|earth": one affinity, either element
function parseAffinities(cell, where) {
  const out = [];
  for (const raw of (cell || "").split(",")) {
    const part = raw.trim().toLowerCase();
    if (!part || part === "none" || part === "—") continue; // "none": no affinity of its own (Mirage, Cradle)
    const e = part.match(/^(?:(\d+)\s+)?either-or\s*\(\s*([a-z]+)\s+or\s+([a-z]+)\s*\)$/);
    if (e) {
      if (!ELEMENTS.includes(e[2]) || !ELEMENTS.includes(e[3])) {
        warn(`${where}: can't read the affinity "${raw.trim()}"`);
        continue;
      }
      for (let i = 0; i < Number(e[1] || 1); i++) out.push(`${e[2]}|${e[3]}`);
      continue;
    }
    const m = part.match(/^(?:(\d+)\s+)?([a-z]+)$/);
    if (!m || !(ELEMENTS.includes(m[2]) || m[2] === "any")) {
      warn(`${where}: can't read the affinity "${raw.trim()}"`);
      continue;
    }
    for (let i = 0; i < Number(m[1] || 1); i++) out.push(m[2]);
  }
  return out;
}

// ---- collected definitions, in file order (newest first) ----------------------
const permDefs = []; // { no, name, rarity, affinities, text, note, source }
const forceDefs = []; // { no, permName, name, rarity, duration, text, source }
const metaDefs = []; // { name, text, rarity, source }
const binderLines = []; // { title, rest }

function splitRow(line) {
  let s = line.trim();
  if (s.startsWith("|")) s = s.slice(1);
  if (s.endsWith("|")) s = s.slice(0, -1);
  return s.split("|").map((c) => c.trim());
}
const isSeparator = (line) => /-{3,}/.test(line) && /^\s*\|?[\s|:-]+$/.test(line);

const src = readFileSync(srcPath, "utf8");
const allLines = src.split(/\r?\n/);
const hr = allLines.findIndex((l) => /^\s*-{3,}\s*$/.test(l));
const lines = hr === -1 ? allLines : allLines.slice(0, hr);
if (hr === -1) warn('No "---" line found; read the whole file.');

let section = "top"; // last "## " heading, used to name where a card came from
let context = null; // last bold lead word: commons, uncommons, rares, pinnacles, meta
let leadText = "";

for (let i = 0; i < lines.length; i++) {
  const line = lines[i];

  const h2 = line.match(/^##\s+(.*)$/);
  if (h2) {
    // The newest pass ends where the next section begins.
    if (permDefs.length || metaDefs.length) break;
    section = h2[1].trim();
    context = null;
    continue;
  }

  const binder = line.match(/^\s*[-*]\s+\*\*(Binder[^*]*?)\.?\*\*\s*(.*)$/);
  if (binder) {
    binderLines.push({ title: binder[1].trim(), rest: binder[2].trim(), source: section });
    continue;
  }

  const lead = line.match(/^\*\*([^*]+)\*\*/);
  if (lead) {
    const words = lead[1].toLowerCase();
    leadText = line;
    if (/meta/.test(words)) context = "meta";
    else if (/pinnacles/.test(words)) context = "pinnacles";
    else if (/uncommons/.test(words)) context = "uncommons";
    else if (/commons/.test(words)) context = "commons";
    else if (/rares/.test(words)) context = "rares";
    else context = null;

    if (context === "pinnacles") {
      const re = /([A-Z][A-Za-z' -]+?) \((\d+), (fire|water|air|earth)\b/g;
      let m;
      while ((m = re.exec(line))) {
        permDefs.push({
          no: Number(m[2]),
          name: m[1].trim(),
          rarity: "S",
          affinities: [m[3], m[3], m[3], m[3]],
          text: "",
          source: section,
        });
      }
    }
    continue;
  }

  if (!(line.trim().startsWith("|") && i + 1 < lines.length && isSeparator(lines[i + 1]))) continue;

  const header = splitRow(line).map((h) => h.toLowerCase());
  const rows = [];
  let j = i + 2;
  while (j < lines.length && lines[j].trim().startsWith("|")) rows.push(splitRow(lines[j++]));
  i = j - 1;

  const col = (...names) => {
    for (const n of names) {
      const exact = header.indexOf(n);
      if (exact !== -1) return exact;
    }
    for (const n of names) {
      const loose = header.findIndex((h) => h.includes(n));
      if (loose !== -1) return loose;
    }
    return -1;
  };
  const has = (w) => header.some((h) => h.includes(w));

  if (has("affinit") && has("force")) {
    // Full two-faced card rows.
    const c = {
      no: col("no."),
      perm: col("permanence"),
      rarity: col("rarity"),
      aff: col("affinities"),
      ptext: col("permanence text"),
      force: col("force"),
      duration: col("duration"),
      ftext: col("force text"),
    };
    for (const r of rows) {
      const no = Number(r[c.no]);
      if (!Number.isInteger(no)) {
        warn(`${section}: row without a card number skipped (${r.join(" | ")})`);
        continue;
      }
      permDefs.push({
        no,
        name: clean(r[c.perm]),
        rarity: clean(r[c.rarity]) || rarityFromNumber(no),
        affinities: parseAffinities(r[c.aff], `#${no}`),
        text: text(r[c.ptext]),
        source: section,
      });
      if (clean(r[c.force])) {
        forceDefs.push({
          no,
          permName: clean(r[c.perm]),
          name: clean(r[c.force]),
          rarity: clean(r[c.rarity]),
          duration: text(r[c.duration]),
          text: text(r[c.ftext]),
          source: section,
        });
      }
    }
  } else if (has("permanence") && has("force") && has("duration")) {
    const c = {
      no: col("no."),
      perm: col("permanence"),
      force: col("force"),
      rarity: col("rarity"),
      duration: col("duration"),
      text: header.findIndex((h) => h.includes("does") || h.includes("text") || h.includes("effect")),
    };
    for (const r of rows) {
      forceDefs.push({
        no: Number(r[c.no]),
        permName: clean(r[c.perm]),
        name: clean(r[c.force]),
        rarity: clean(r[c.rarity]),
        duration: text(r[c.duration]),
        text: text(r[c.text]),
        source: section,
      });
    }
  } else if (header[0] === "element" && has("numbers") && has("cards")) {
    for (const r of rows) {
      const el = r[0].trim().toLowerCase();
      const range = r[1].match(/(\d+)\s*[–—-]\s*(\d+)/);
      const names = r[2].split(",").map(clean).filter(Boolean);
      if (!ELEMENTS.includes(el) || !range) {
        warn(`${section}: commons row "${r[0]}" skipped`);
        continue;
      }
      const start = Number(range[1]);
      if (Number(range[2]) - start + 1 !== names.length) {
        warn(`${section}: ${el} lists ${names.length} cards for numbers ${range[1]}–${range[2]}`);
      }
      names.forEach((name, k) =>
        permDefs.push({ no: start + k, name, rarity: "C", affinities: [el], text: "", source: section })
      );
    }
  } else if (has("no") && has("card") && (has("tags") || has("affinit"))) {
    const c = { no: col("no."), name: col("card"), aff: col("affinities", "tags"), text: col("effect", "text") };
    for (const r of rows) {
      const no = Number(r[c.no]);
      if (!Number.isInteger(no)) continue;
      let t = c.text >= 0 ? text(r[c.text]) : "";
      let note = "";
      if (/^\(.*\)$/.test(t)) {
        note = t.slice(1, -1);
        t = "";
      }
      permDefs.push({
        no,
        name: clean(r[c.name]),
        rarity: RARITY_BY_WORD[context] || rarityFromNumber(no),
        affinities: parseAffinities(r[c.aff], `#${no}`),
        text: t,
        note,
        source: section,
      });
    }
  } else if (context === "meta" && header[0] === "card" && has("text")) {
    const rarity = /\bpinnacle\b/i.test(leadText)
      ? "S"
      : /\buncommon\b/i.test(leadText)
      ? "B"
      : /\brare\b/i.test(leadText)
        ? "A"
        : /\bcommon\b/i.test(leadText)
          ? "C"
          : "B";
    const noCol = header.indexOf("no.");
    for (const r of rows) {
      const no = noCol >= 0 ? Number(clean(r[noCol])) || null : null;
      metaDefs.push({ name: clean(r[0]), text: text(r[col("text")]), rarity, no, source: section });
    }
  } else {
    warn(`${section}: table skipped (header: ${header.join(" | ")})`);
  }
}

// ---- assemble ----------------------------------------------------------------------
const cards = new Map(); // id -> card

for (const d of permDefs) {
  const id = String(d.no);
  const existing = cards.get(id);
  if (existing) {
    warn(`#${d.no} is listed twice ("${existing.permanence.name}" and "${d.name}"); keeping the first`);
    continue;
  }
  const perm = { name: d.name, affinities: d.affinities, text: d.text };
  if (d.note) perm.note = d.note;
  cards.set(id, { id, no: d.no, rarity: d.rarity, source: d.source, permanence: perm, force: null });
}

for (const f of forceDefs) {
  const card = cards.get(String(f.no));
  if (!card) {
    warn(`Force ${f.name} names card #${f.no}, which isn't in the pool`);
    continue;
  }
  if (card.force) {
    warn(`${card.permanence.name} (#${f.no}) has two force faces (${card.force.name}, ${f.name}); keeping the first`);
    continue;
  }
  if (f.permName && f.permName !== card.permanence.name) {
    warn(`Force ${f.name} (#${f.no}) is listed with "${f.permName}", but #${f.no} is "${card.permanence.name}"`);
  }
  card.force = { name: f.name, duration: f.duration, text: f.text };
}

for (const m of metaDefs) {
  const id = `meta-${slug(m.name)}`;
  if (cards.has(id)) {
    warn(`Meta card ${m.name} is defined twice; keeping the newer one`);
    continue;
  }
  cards.set(id, { id, no: m.no ?? null, rarity: m.rarity, source: m.source, meta: { name: m.name, text: m.text } });
}

const list = [...cards.values()].sort(
  (a, b) => (a.no ?? 1e6) - (b.no ?? 1e6) || (a.meta?.name || "").localeCompare(b.meta?.name || "")
);

// ---- binders ------------------------------------------------------------------------
const byName = new Map();
for (const c of list) {
  const name = (c.meta ? c.meta.name : c.permanence.name).toLowerCase();
  if (byName.has(name)) warn(`Two cards are called "${name}"; binders will use #${byName.get(name).no ?? byName.get(name).id}`);
  else byName.set(name, c);
}

const binders = [];
for (const b of binderLines) {
  // The card list is the last sentence whose comma-separated items are all card names.
  const sentences = b.rest.split(/\.\s+|\.$/).map((s) => s.trim()).filter(Boolean);
  let listIdx = -1;
  for (let k = sentences.length - 1; k >= 0; k--) {
    const items = sentences[k].split(",").map((s) => s.trim()).filter(Boolean);
    const known = items.filter((n) => byName.has(n.toLowerCase())).length;
    if (items.length >= 3 && known >= items.length * 0.8) {
      listIdx = k;
      break;
    }
  }
  if (listIdx === -1) {
    warn(`${b.title}: couldn't find its card list`);
    continue;
  }
  const names = sentences[listIdx].split(",").map((s) => s.trim()).filter(Boolean);
  const ids = [];
  for (const n of names) {
    const card = byName.get(n.toLowerCase());
    if (!card) warn(`${b.title}: "${n}" isn't a card in the pool`);
    else if (ids.includes(card.id)) warn(`${b.title}: ${n} is listed twice (one of each card per binder)`);
    else ids.push(card.id);
  }
  const missingForce = ids.map((id) => cards.get(id)).filter((c) => !c.meta && !c.force);
  if (missingForce.length) {
    warn(`${b.title}: no force face yet for ${missingForce.map((c) => c.permanence.name).join(", ")}`);
  }
  binders.push({
    id: slug(b.title),
    name: b.title,
    note: sentences.slice(0, listIdx).join(". ") + (listIdx ? "." : ""),
    cards: ids,
    originals: [],
  });
}

// ---- write -----------------------------------------------------------------------------
const numbered = list.filter((c) => !c.meta);
const nos = new Set(list.map((c) => c.no).filter((n) => n != null)); // meta cards carry numbers from the third pass on
const missing = [];
for (let n = 1; n <= 100; n++) if (!nos.has(n)) missing.push(n);

const sources = {};
for (const c of list) sources[c.source] = (sources[c.source] || 0) + 1;

const syncedAt = new Date().toISOString();
const out = {
  source: relative(root, srcPath),
  pass: section,
  syncedAt,
  counts: {
    cards: list.length,
    meta: list.length - numbered.length,
    withForceFace: numbered.filter((c) => c.force).length,
    byRarity: Object.fromEntries(["C", "B", "A", "S"].map((r) => [r, list.filter((c) => c.rarity === r).length])),
    fromSection: sources,
  },
  missingNumbers: missing,
  warnings,
  cards: list,
};
writeFileSync(cardsOut, JSON.stringify(out, null, 2) + "\n");

if (binders.length) {
  writeFileSync(
    bindersOut,
    JSON.stringify(
      {
        about: `Generated from ${relative(root, srcPath)} by scripts/sync-cards.mjs. Edit the binders there, not here.`,
        syncedAt,
        binders,
      },
      null,
      2
    ) + "\n"
  );
} else if (existsSync(bindersOut)) {
  warn("No binders found in the card pool; data/binders.json left as it was.");
}

console.log(`Read ${relative(root, srcPath)}, newest pass only: "${section}"`);
console.log(`  ${list.length} cards (${out.counts.meta} meta), ${out.counts.withForceFace} with a force face`);
for (const b of binders) console.log(`  binder ${b.name}: ${b.cards.length} cards`);
if (missing.length) console.log(`  ${missing.length} card numbers not in this pass`);
for (const w of warnings) console.log(`  warning: ${w}`);
