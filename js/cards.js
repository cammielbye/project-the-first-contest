// Drawing cards.
//
// Card faces come from the Card Anatomy canvas (data/card-faces.json, made by
// scripts/sync-card-art.mjs): each face is the canvas's own 320×448 drawing,
// scaled to fit where it's shown. A face the canvas hasn't drawn yet gets a
// plain version in the same carved-stone style, built from data/cards.json.

let FACES = {};
export function setFaceArt(faces) {
  FACES = faces || {};
}

// Affinity symbols as drawn on the canvas: thin carved strokes with a dark
// offset shadow; the bars on air and earth run right across the triangle.
const SYMBOLS = {
  fire: { color: "#D0663F", d: "M12 3.5 L20.5 19 H3.5 Z" },
  water: { color: "#7FA7B5", d: "M3.5 5 H20.5 L12 20.5 Z" },
  air: { color: "#D5D8CC", d: "M12 3.5 L20.5 19 H3.5 Z M3 12.5 H21" },
  earth: { color: "#A88F6B", d: "M3.5 5 H20.5 L12 20.5 Z M3 11.5 H21" },
  // "any" has its own color, apart from air's pale grey (Cam, Nov 11)
  any: { color: "#7FBF73", d: "M4.5 12 a7.5 7.5 0 1 0 15 0 a7.5 7.5 0 1 0 -15 0 M10.5 12 a1.5 1.5 0 1 0 3 0 a1.5 1.5 0 1 0 -3 0" },
};
const RARITY_WORD = { C: "common", B: "uncommon", A: "rare", S: "pinnacle" };
// Rarity is a letter with no diamond around it (Cam, Nov 11), in shades of one violet that no element uses: paler and
// greyer at common, deeper and more saturated going up.
export const RARITY_COLOR = { C: "#BDB6CF", B: "#AC93E2", A: "#9A6DF0", S: "#B653FF" };
const RARW = { common: "C", uncommon: "B", rare: "A", pinnacle: "S" };
const rarityGlyph = (r) =>
  `<span role="img" aria-label="${RARITY_WORD[r]}" style="font-style:normal;font-weight:700;color:${RARITY_COLOR[r]};text-shadow:1px 1px 0 #0D0F0D;margin:0 .04em">${r}</span>`;

const esc = (s) =>
  String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);

// Every affinity sits in a white ring. An either-or affinity ("fire|earth") is one
// capsule holding both symbols, divided by a slash. One ring or capsule = one affinity.
const RING = "#E6E1D3";
function sym(kind, cx, cy, sc) {
  const s = SYMBOLS[kind];
  if (!s) return "";
  const t = `translate(${(cx - 12 * sc).toFixed(2)} ${(cy - 12 * sc).toFixed(2)}) scale(${sc})`;
  return `<g transform="translate(0.7 0.7)"><g transform="${t}" stroke="#0D0F0D"><path d="${s.d}"/></g></g><g transform="${t}" stroke="${s.color}"><path d="${s.d}"/></g>`;
}
function symbolSvg(kind, size = 32) {
  const open = (w, vb) => `<svg width="${w}" height="${size}" viewBox="${vb}" fill="none" stroke-width="1.9" stroke-linejoin="round" stroke-linecap="round" aria-hidden="true">`;
  if (kind.includes("|")) {
    const [a, b] = kind.split("|");
    const cap = `<rect x="1.2" y="1.2" width="57.6" height="29.6" rx="14.8"/>`, slash = `<path d="M33.6 6 L26.4 26"/>`;
    return `${open((size * 60) / 32, "0 0 60 32")}<g transform="translate(0.7 0.7)" stroke="#0D0F0D">${cap}${slash}</g><g stroke="${RING}" stroke-width="1.4">${cap}${slash}</g>${sym(a, 15.5, 16.4, 0.72)}${sym(b, 44.5, 16.4, 0.72)}</svg>`;
  }
  if (!SYMBOLS[kind]) return "";
  const ring = `<circle cx="16" cy="16" r="14.6"/>`;
  return `${open(size, "0 0 32 32")}<g transform="translate(0.7 0.7)" stroke="#0D0F0D">${ring}</g><g stroke="${RING}" stroke-width="1.4">${ring}</g>${sym(kind, 16, 16.4, 0.8)}</svg>`;
}

// Rules text draws elements, never names them (Cam, Nov 2): the element a card turns something
// INTO ("becomes fire") is ringed, as an affinity; every other mention is the bare symbol. An affinity a card
// gains ("+1 water", Nov 9) is ringed too, since a ring means an affinity (Claude's reading of the Nov 2 rule), and so
// are the elements a world must have (Hanging Valley, Nov 9: Cam asked for each circled).
// Matches the canvas's own faces (gen/pass3_cards.py).
const bareSym = (el) =>
  `<svg viewBox="0 0 24 24" role="img" aria-label="${el}" style="width:.78em;height:.78em;vertical-align:-.07em;margin:0 .04em" fill="none" stroke-width="2.4" stroke-linejoin="round" stroke-linecap="round"><g transform="translate(1 1)" stroke="#0D0F0D"><path d="${SYMBOLS[el].d}"/></g><g stroke="${SYMBOLS[el].color}"><path d="${SYMBOLS[el].d}"/></g></svg>`;
const ringedSym = (el) => {
  const t = "translate(6.4 6.8) scale(0.8)";
  return `<svg viewBox="0 0 32 32" role="img" aria-label="${el} affinity" style="width:.98em;height:.98em;vertical-align:-.17em;margin:0 .03em" fill="none" stroke-linejoin="round" stroke-linecap="round"><circle cx="16.8" cy="16.8" r="14" stroke="#0D0F0D" stroke-width="2.2"/><circle cx="16" cy="16" r="14" stroke="${RING}" stroke-width="2"/><g transform="translate(0.9 0.9)"><g transform="${t}" stroke="#0D0F0D" stroke-width="2.6"><path d="${SYMBOLS[el].d}"/></g></g><g transform="${t}" stroke="${SYMBOLS[el].color}" stroke-width="2.6"><path d="${SYMBOLS[el].d}"/></g></svg>`;
};
export function rulesHtml(text) {
  return esc(text)
    // a rarity named in a rule is drawn as its symbol, as elements are (Cam, Nov 11): "Remove a [C] permanence."
    .replace(/\b(common|uncommon|rare|pinnacle)(?=\s+(?:permanences?|forces?)\b)/gi, (_, r) => `\u0000Q${RARW[r.toLowerCase()]}\u0000`)
    .replace(/\b(becomes?|become)\s+(fire|water|air|earth)\b/gi, (_, v, e) => `${v} \u0000R${e.toLowerCase()}\u0000`)
    .replace(/\+1\s+(fire|water|air|earth)\b/gi, (_, e) => `+1 \u0000R${e.toLowerCase()}\u0000`)
    .replace(/\bgains\s+(fire|water|air|earth)\b/gi, (_, e) => `gains \u0000R${e.toLowerCase()}\u0000`) // a pip (Nov 11, positional)
    .replace(/\bhas((?:\s+(?:fire|water|air|earth)\b)+)/gi, (_, list) => "has " + `<span style="white-space:nowrap">${list.trim().replace(/(fire|water|air|earth)/gi, (e) => `\u0000R${e.toLowerCase()}\u0000`)}</span>`)
    .replace(/\b(fire|water|air|earth)\b/gi, (_, e) => `\u0000B${e.toLowerCase()}\u0000`)
    .replace(/\u0000([RB])(fire|water|air|earth)\u0000([.,;:]?)/g, (_, k, e, p) => `<span style="white-space:nowrap">${k === "R" ? ringedSym(e) : bareSym(e)}${p}</span>`)
    .replace(/\u0000Q([CBAS])\u0000/g, (_, r) => rarityGlyph(r))
    .replace(/\ban (?=<span role="img" aria-label="uncommon")/g, "a "); // "an uncommon" reads "a [B]" once drawn
}

const FOOT_RULE =`<svg width="288" height="10" viewBox="0 0 288 10" style="position:absolute;top:386px;left:16px" aria-hidden="true"><path d="M32 5 H256" stroke="#0D0F0D" stroke-width="3" transform="translate(0 1)"/><path d="M32 5 H256" stroke="#7E827A" stroke-width="1.4"/><path d="M24 5 L32 1 L40 5 L32 9 Z M248 5 L256 1 L264 5 L256 9 Z" fill="#7E827A"/></svg>`;

function footer(card) {
  const no = card.no ? `${card.no}/100` : "—/100";
  // meta cards have no rarity (Oct 29)
  const rar = card.meta ? "" : `<div role="img" aria-label="Rarity ${card.rarity}, ${RARITY_WORD[card.rarity] || ""}" style="position:absolute;right:18px;top:396px;height:44px;display:flex;align-items:center;font-size:40px;font-weight:700;line-height:1;color:${RARITY_COLOR[card.rarity] || "#C2C5B8"};text-shadow:1.5px 1.5px 0 #0D0F0D">${esc(card.rarity)}</div>`;
  return `${FOOT_RULE}<div style="position:absolute;left:22px;top:404px;height:32px;display:flex;align-items:center;font-family:'IBM Plex Mono',monospace;font-size:14px;letter-spacing:.04em;color:#B9BCB0">${no}</div>${rar}`;
}

const PANEL = "position:absolute;left:16px;width:288px;border-radius:10px;box-shadow:inset 0 4px 12px rgba(0,0,0,.65),inset 0 -1px 0 rgba(255,255,255,.06)";
// Rules text is drawn large (42px on forces and meta cards, 32px on permanence);
// the art panel above it shrinks to make room.
const COLUMN = "position:absolute;left:16px;width:288px;display:flex;flex-direction:column;gap:6px";
const TEXTBOX =
  "flex:none;box-sizing:border-box;padding:6px 10px;border-radius:8px;background:rgba(13,15,13,.55);border:1px solid rgba(194,197,184,.22);text-align:center;font-size:42px;line-height:1.04;color:#ECE6D6";
const FLEXPANEL = "flex:1 1 0;min-height:0;border-radius:10px;box-shadow:inset 0 4px 12px rgba(0,0,0,.65),inset 0 -1px 0 rgba(255,255,255,.06)";
const DURLABEL = "flex:none;height:16px;display:flex;align-items:center;justify-content:center;font-family:'IBM Plex Mono',monospace;font-size:11px;letter-spacing:.1em";
const TITLE = "position:absolute;left:16px;width:288px;height:38px;display:flex;align-items:center;justify-content:center;font-size:26px;font-weight:600;color:#ECE6D6;text-shadow:1px 1px 0 #0D0F0D";
const BODY = "position:relative;width:320px;height:448px;border-radius:14px;box-shadow:0 14px 32px rgba(0,0,0,.55),inset 0 1px 0 rgba(255,255,255,.08),inset 0 -4px 10px rgba(0,0,0,.45)";

// A face the canvas hasn't drawn: same layout, a blank art panel.
function fallbackHtml(card, face) {
  if (face === "meta") {
    return `<div style="${BODY};background:#1E1F24"><div style="position:absolute;top:18px;left:16px;width:288px;text-align:center;font-family:'IBM Plex Mono',monospace;font-size:11px;letter-spacing:.14em;color:#B9A6D6">FIFTH PILLAR · META</div><div style="${TITLE};top:40px;font-size:28px">${esc(card.meta.name)}</div><div style="${COLUMN};top:88px;bottom:66px"><div style="${FLEXPANEL};background:rgba(0,0,0,.28)"></div><div style="${DURLABEL};color:#A9A3B8">ONE FACE · EITHER PLAYER · ONCE</div><div style="${TEXTBOX}">${rulesHtml(card.meta.text)}</div></div>${footer(card)}</div>`;
  }
  if (face === "force") {
    const f = card.force;
    const name = f ? f.name : "Force face not drafted";
    const dur = f && f.duration ? `FORCE · ${f.duration.toUpperCase()}` : "FORCE";
    return `<div style="${BODY};background:#2A2F32"><svg width="320" height="448" style="position:absolute;top:0;left:0" aria-hidden="true"><rect x="5.5" y="5.5" width="309" height="437" rx="10" fill="none" stroke="#7E8A90" stroke-width="1" stroke-dasharray="3 5" opacity=".55"/></svg><div style="${TITLE};top:10px;font-style:italic">${esc(name)}</div><div style="${COLUMN};top:52px;bottom:70px"><div style="${FLEXPANEL};background:rgba(0,0,0,.22)"></div><div style="${DURLABEL};color:#A9B3B8">${esc(dur)}</div>${f && f.text ? `<div style="${TEXTBOX}">${rulesHtml(f.text)}</div>` : ""}</div>${footer(card)}</div>`;
  }
  const p = card.permanence;
  const text = p.text
    ? `<div style="position:absolute;left:10px;right:10px;bottom:10px;box-sizing:border-box;padding:6px 10px;border-radius:6px;background:rgba(13,15,13,.82);border:1px solid rgba(194,197,184,.28);font-size:32px;font-style:italic;line-height:1.08;color:#ECE6D6">${rulesHtml(p.text)}</div>`
    : "";
  // pips 56px tall, about 12.5% of the card's height (Cam, Nov 11: 10-15%)
  const syms = (p.affinities || []).map((a) => symbolSvg(a, 56)).join("");
  return `<div style="${BODY};background:#353A35"><div style="${TITLE};top:10px">${esc(p.name)}</div><div style="${PANEL};top:52px;height:258px;background:rgba(0,0,0,.2);overflow:hidden">${text}</div><div role="img" aria-label="Affinity" style="position:absolute;top:318px;left:16px;width:288px;height:62px;display:flex;align-items:center;justify-content:center;gap:10px">${syms}</div>${footer(card)}</div>`;
}

// SVG ids (filters, patterns) must be unique on the page, and the same card
// can be drawn several times at once (binder, table, preview).
let instanceCounter = 0;
function uniqueIds(html) {
  const n = ++instanceCounter;
  return html.replace(/(\bid="|url\(#|href="#)([A-Za-z_][\w.-]*)/g, (_, pre, id) => `${pre}${id}_${n}`);
}

const template = document.createElement("template");

// One face of a card as a DOM element. face: "permanence" | "force" | "meta".
// size: "token" (table, void), "full" (binder), "preview".
export function renderFace(card, face, opts = {}) {
  const { size = "full", inst = null } = opts;
  if (card.meta) face = "meta";

  const root = document.createElement("div");
  root.className = `card ${size} face-${face} r-${card.rarity}`;
  if (face === "force" && !card.force) root.classList.add("undrafted");
  if (inst) {
    if (inst.iid) root.dataset.iid = inst.iid;
    root.classList.add(`own-${inst.owner}`);
    if (inst.original) root.classList.add("original");
  }

  const art = FACES[card.id]?.[face];
  template.innerHTML = uniqueIds(art || fallbackHtml(card, face));
  const faceEl = document.createElement("div");
  faceEl.className = "face";
  faceEl.append(template.content);
  root.append(faceEl);
  return root;
}

export function otherFace(face) {
  if (face === "meta") return "meta";
  return face === "force" ? "permanence" : "force";
}
