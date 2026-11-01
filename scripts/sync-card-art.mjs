// Copies the card faces drawn on the Card Anatomy canvas into data/card-faces.json,
// so the table shows exactly the cards from the design work.
//
// Usage: node scripts/sync-card-art.mjs <folder holding the canvas's canvas.json and boards>
//
// Run it after scripts/sync-cards.mjs. It reads the pass name from data/cards.json
// ("Second pass: …" -> "Second pass") and uses only the canvas boards whose title
// starts with that name, so the art always comes from the same, most recent pass.
// Every 320×448 card face on those boards is matched to a card by the name at its
// top: a card's permanence name, its force name, or a meta card's name.

import { readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const canvasDir = process.argv[2];
if (!canvasDir) {
  console.error("Usage: node scripts/sync-card-art.mjs <canvas project folder>");
  process.exit(1);
}

const cardsJson = JSON.parse(readFileSync(join(root, "data", "cards.json"), "utf8"));
const passName = (cardsJson.pass || "").split(":")[0].trim();
if (!passName) {
  console.error("data/cards.json has no pass name; run scripts/sync-cards.mjs first.");
  process.exit(1);
}

const canvas = JSON.parse(readFileSync(join(canvasDir, "canvas.json"), "utf8"));
const boards = (canvas.order || Object.keys(canvas.boards)).filter((file) => {
  const title = canvas.boards[file]?.title || "";
  return title.toLowerCase().startsWith(passName.toLowerCase()) && !/binder/i.test(title);
});

const warnings = [];
const warn = (m) => warnings.push(m);

// name -> { id, face }
const byName = new Map();
for (const c of cardsJson.cards) {
  if (c.meta) byName.set(c.meta.name.toLowerCase(), { id: c.id, face: "meta" });
  else {
    byName.set(c.permanence.name.toLowerCase(), { id: c.id, face: "permanence" });
    if (c.force) byName.set(c.force.name.toLowerCase(), { id: c.id, face: "force" });
  }
}

const decode = (s) =>
  s
    .replace(/&amp;/g, "&")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .trim();

// Only static drawing markup goes into the page: no scripts, handlers or links out.
const sanitize = (html) =>
  html
    .replace(/<script[\s\S]*?<\/script>/gi, "")
    .replace(/\son[a-z]+\s*=\s*"[^"]*"/gi, "")
    .replace(/\son[a-z]+\s*=\s*'[^']*'/gi, "")
    .replace(/javascript:/gi, "")
    .replace(/\s+/g, " ")
    .replace(/> </g, "><");

const CARD_START = /<div style="position: relative; width: 320px; height: 448px/g;

const faces = {}; // id -> { permanence?, force?, meta? }
let found = 0;

for (const file of boards) {
  const src = readFileSync(join(canvasDir, file), "utf8");
  let m;
  CARD_START.lastIndex = 0;
  while ((m = CARD_START.exec(src))) {
    // Walk the div nesting to find where this card's outer div closes.
    const tag = /<div\b|<\/div>/g;
    tag.lastIndex = m.index;
    let depth = 0;
    let end = -1;
    let t;
    while ((t = tag.exec(src))) {
      depth += t[0] === "</div>" ? -1 : 1;
      if (depth === 0) {
        end = t.index + t[0].length;
        break;
      }
    }
    if (end === -1) {
      warn(`${file}: a card face isn't closed; skipped`);
      continue;
    }
    const html = src.slice(m.index, end);
    CARD_START.lastIndex = end;
    found++;

    // The card's name: the first large title div.
    const nameMatch = html.match(/font-size: 2[0-9]px; font-weight: 600[^"]*"[^>]*>([^<]+)</);
    const name = nameMatch ? decode(nameMatch[1]) : null;
    const hit = name && byName.get(name.toLowerCase());
    if (!hit) {
      warn(`${file}: "${name ?? "?"}" doesn't match any card in data/cards.json`);
      continue;
    }
    const slot = (faces[hit.id] ||= {});
    if (slot[hit.face]) {
      warn(`${name}: drawn twice; keeping the first`);
      continue;
    }
    slot[hit.face] = sanitize(html);
  }
}

// What's missing.
for (const c of cardsJson.cards) {
  const f = faces[c.id] || {};
  if (c.meta && !f.meta) warn(`No drawing for ${c.meta.name} (meta)`);
  if (!c.meta && !f.permanence) warn(`No drawing for ${c.permanence.name} (permanence)`);
  if (!c.meta && c.force && !f.force) warn(`No drawing for ${c.force.name} (force of ${c.permanence.name})`);
}

const out = {
  source: canvas.title || "canvas",
  pass: passName,
  boards,
  syncedAt: new Date().toISOString(),
  warnings,
  faces,
};
writeFileSync(join(root, "data", "card-faces.json"), JSON.stringify(out) + "\n");

const n = Object.values(faces).reduce((s, f) => s + Object.keys(f).length, 0);
console.log(`Read ${boards.length} "${passName}" boards: ${boards.join(", ")}`);
console.log(`  ${found} card faces found, ${n} matched to cards`);
for (const w of warnings) console.log(`  warning: ${w}`);
