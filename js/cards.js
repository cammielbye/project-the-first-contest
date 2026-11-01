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
  any: { color: "#C2C5B8", d: "M4.5 12 a7.5 7.5 0 1 0 15 0 a7.5 7.5 0 1 0 -15 0 M10.5 12 a1.5 1.5 0 1 0 3 0 a1.5 1.5 0 1 0 -3 0" },
};
const RARITY_WORD = { C: "common", B: "uncommon", A: "rare", S: "pinnacle" };

const esc = (s) =>
  String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);

function symbolSvg(kind, size = 28) {
  const s = SYMBOLS[kind];
  if (!s) return "";
  return `<svg width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke-width="1.9" stroke-linejoin="round" stroke-linecap="round" aria-hidden="true"><g transform="translate(0.8 0.8)" stroke="#0D0F0D"><path d="${s.d}"/></g><g stroke="${s.color}"><path d="${s.d}"/></g></svg>`;
}

const FOOT_RULE = `<svg width="288" height="10" viewBox="0 0 288 10" style="position:absolute;top:386px;left:16px" aria-hidden="true"><path d="M32 5 H256" stroke="#0D0F0D" stroke-width="3" transform="translate(0 1)"/><path d="M32 5 H256" stroke="#7E827A" stroke-width="1.4"/><path d="M24 5 L32 1 L40 5 L32 9 Z M248 5 L256 1 L264 5 L256 9 Z" fill="#7E827A"/></svg>`;

function footer(card) {
  const no = card.no ? `${card.no}/100` : "—/100";
  return `${FOOT_RULE}<div style="position:absolute;left:22px;top:404px;height:32px;display:flex;align-items:center;font-family:'IBM Plex Mono',monospace;font-size:14px;letter-spacing:.04em;color:#B9BCB0">${no}</div><div role="img" aria-label="Rarity ${card.rarity}, ${RARITY_WORD[card.rarity] || ""}" style="position:absolute;right:18px;top:402px;width:36px;height:36px"><div style="position:absolute;top:7px;left:7px;width:20px;height:20px;transform:rotate(45deg);border:1.6px solid #C2C5B8;box-shadow:1px 1px 0 #0D0F0D"></div><div style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center;font-size:19px;font-weight:700;color:#C2C5B8;text-shadow:1px 1px 0 #0D0F0D">${esc(card.rarity)}</div></div>`;
}

const PANEL = "position:absolute;left:16px;width:288px;border-radius:10px;box-shadow:inset 0 4px 12px rgba(0,0,0,.65),inset 0 -1px 0 rgba(255,255,255,.06)";
const TEXTBOX =
  "position:absolute;left:16px;width:288px;box-sizing:border-box;padding:8px 14px;border-radius:8px;background:rgba(13,15,13,.55);border:1px solid rgba(194,197,184,.22);display:flex;align-items:center;justify-content:center;text-align:center;font-size:21px;line-height:1.22;color:#ECE6D6";
const TITLE = "position:absolute;left:16px;width:288px;height:38px;display:flex;align-items:center;justify-content:center;font-size:26px;font-weight:600;color:#ECE6D6;text-shadow:1px 1px 0 #0D0F0D";
const BODY = "position:relative;width:320px;height:448px;border-radius:14px;box-shadow:0 14px 32px rgba(0,0,0,.55),inset 0 1px 0 rgba(255,255,255,.08),inset 0 -4px 10px rgba(0,0,0,.45)";

// A face the canvas hasn't drawn: same layout, a blank art panel.
function fallbackHtml(card, face) {
  if (face === "meta") {
    return `<div style="${BODY};background:#1E1F24"><div style="position:absolute;top:18px;left:16px;width:288px;text-align:center;font-family:'IBM Plex Mono',monospace;font-size:11px;letter-spacing:.14em;color:#B9A6D6">FIFTH PILLAR · META</div><div style="${TITLE};top:40px;font-size:28px">${esc(card.meta.name)}</div><div style="${PANEL};top:92px;height:168px;background:rgba(0,0,0,.28)"></div><div style="${TEXTBOX};top:296px;height:86px">${esc(card.meta.text)}</div>${footer(card)}</div>`;
  }
  if (face === "force") {
    const f = card.force;
    const name = f ? f.name : "Force face not drafted";
    const dur = f && f.duration ? `FORCE · ${f.duration.toUpperCase()}` : "FORCE";
    return `<div style="${BODY};background:#2A2F32"><svg width="320" height="448" style="position:absolute;top:0;left:0" aria-hidden="true"><rect x="5.5" y="5.5" width="309" height="437" rx="10" fill="none" stroke="#7E8A90" stroke-width="1" stroke-dasharray="3 5" opacity=".55"/></svg><div style="${TITLE};top:10px;font-style:italic">${esc(name)}</div><div style="${PANEL};top:52px;height:192px;background:rgba(0,0,0,.22)"></div><div style="position:absolute;top:252px;left:16px;width:288px;height:18px;display:flex;align-items:center;justify-content:center;font-family:'IBM Plex Mono',monospace;font-size:11px;letter-spacing:.1em;color:#A9B3B8">${esc(dur)}</div>${f && f.text ? `<div style="${TEXTBOX};top:276px;height:102px">${esc(f.text)}</div>` : ""}${footer(card)}</div>`;
  }
  const p = card.permanence;
  const text = p.text
    ? `<div style="position:absolute;left:10px;right:10px;bottom:10px;box-sizing:border-box;padding:8px 12px;border-radius:6px;background:rgba(13,15,13,.78);border:1px solid rgba(194,197,184,.28);font-size:16px;font-style:italic;line-height:1.2;color:#ECE6D6">${esc(p.text)}</div>`
    : "";
  const syms = (p.affinities || []).map((a) => symbolSvg(a)).join("");
  return `<div style="${BODY};background:#353A35"><div style="${TITLE};top:10px">${esc(p.name)}</div><div style="${PANEL};top:52px;height:280px;background:rgba(0,0,0,.2);overflow:hidden">${text}</div><div role="img" aria-label="Affinity" style="position:absolute;top:342px;left:16px;width:288px;height:36px;display:flex;align-items:center;justify-content:center;gap:12px">${syms}</div>${footer(card)}</div>`;
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
