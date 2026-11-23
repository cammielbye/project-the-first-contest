// Branch B card faces, drawn like the main table's (js/cards.js): a 320x448 face scaled to fit. The front is the
// landscape with its pips (vanilla, Nov 18); the back is the force, with its own pips and its text.
import { CARDS } from "./rules-b.js";

const SYMBOLS = {
  fire: { color: "#D0663F", d: "M12 3.5 L20.5 19 H3.5 Z" },
  water: { color: "#7FA7B5", d: "M3.5 5 H20.5 L12 20.5 Z" },
  air: { color: "#D5D8CC", d: "M12 3.5 L20.5 19 H3.5 Z M3 12.5 H21" },
  earth: { color: "#A88F6B", d: "M3.5 5 H20.5 L12 20.5 Z M3 11.5 H21" },
  any: { color: "#FFFFFF", fill: "#000000", width: 0.6, d: "M4.5 4.5 H19.5 V19.5 H4.5 Z" },
};
const RING = "#E6E1D3";
export const esc = (t) => String(t ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);
function sym(kind, cx, cy, sc) {
  const s = SYMBOLS[kind];
  const t = `translate(${(cx - 12 * sc).toFixed(2)} ${(cy - 12 * sc).toFixed(2)}) scale(${sc})`;
  const own = (s.fill ? ` fill="${s.fill}"` : "") + (s.width ? ` stroke-width="${s.width}"` : "");
  return `<g transform="translate(0.7 0.7)"><g transform="${t}" stroke="#0D0F0D"><path d="${s.d}"/></g></g><g transform="${t}" stroke="${s.color}"><path d="${s.d}"${own}/></g>`;
}
export function pipSvg(kind, size = 32) {
  const ring = `<circle cx="16" cy="16" r="14.6"/>`;
  return `<svg width="${size}" height="${size}" viewBox="0 0 32 32" fill="none" stroke-width="1.9" stroke-linejoin="miter" stroke-linecap="butt" role="img" aria-label="${kind}"><g transform="translate(0.7 0.7)" stroke="#0D0F0D">${ring}</g><g stroke="${RING}" stroke-width="1.4">${ring}</g>${sym(kind, 16, 16.4, 0.8)}</svg>`;
}

const BODY = "position:relative;width:320px;height:448px;border-radius:14px;overflow:hidden;font-family:'Cormorant Garamond',Georgia,serif;box-shadow:inset 0 1px 0 rgba(255,255,255,.08),inset 0 -4px 10px rgba(0,0,0,.45)";
const TITLE = "position:absolute;left:16px;width:288px;height:38px;display:flex;align-items:center;justify-content:center;font-size:28px;font-weight:700;color:#ECE6D6;text-shadow:1px 1px 0 #0D0F0D;white-space:nowrap";
const PANEL = "position:absolute;left:16px;width:288px;border-radius:10px;box-shadow:inset 0 4px 12px rgba(0,0,0,.65),inset 0 -1px 0 rgba(255,255,255,.06)";
const RULE = `<svg width="288" height="10" viewBox="0 0 288 10" style="position:absolute;top:392px;left:16px" aria-hidden="true"><path d="M32 5 H256" stroke="#0D0F0D" stroke-width="3" transform="translate(0 1)"/><path d="M32 5 H256" stroke="#7E827A" stroke-width="1.4"/><path d="M24 5 L32 1 L40 5 L32 9 Z M248 5 L256 1 L264 5 L256 9 Z" fill="#7E827A"/></svg>`;
const MONO = "font-family:'IBM Plex Mono',monospace;font-size:14px;letter-spacing:.04em;color:#B9BCB0";
const foot = (c, label) => `${RULE}<div style="position:absolute;left:22px;top:406px;height:30px;display:flex;align-items:center;${MONO}">${c.no}/24</div>${label ? `<div style="position:absolute;right:22px;top:406px;height:30px;display:flex;align-items:center;${MONO};font-size:12px;letter-spacing:.12em">${label}</div>` : ""}`;
const row = (pips, top, size) => `<div style="position:absolute;top:${top}px;left:16px;width:288px;height:${size + 6}px;display:flex;align-items:center;justify-content:center;gap:10px">${pips.length ? pips.map((p) => pipSvg(p, size)).join("") : `<span style="font-style:italic;font-size:22px;color:#9aa49d">no pips</span>`}</div>`;

export function frontHtml(c) {
  const text = c.ft ? `<div style="position:absolute;left:10px;right:10px;bottom:10px;box-sizing:border-box;padding:6px 10px;border-radius:6px;background:rgba(13,15,13,.82);border:1px solid rgba(194,197,184,.28);font-size:30px;font-style:italic;line-height:1.06;text-align:center;color:#ECE6D6">${esc(c.ft)}</div>` : "";
  return `<div style="${BODY};background:#353A35"><div style="${TITLE};top:10px">${esc(c.n)}</div><div style="${PANEL};top:52px;height:262px;background:rgba(0,0,0,.2)">${text}</div>${row(c.p, 322, 56)}${foot(c, "LANDSCAPE")}</div>`;
}
export function backHtml(c) {
  const len = c.t.length, fs = len > 70 ? 26 : len > 48 ? 29 : 32;
  const text = c.t
    ? `<div style="position:absolute;left:16px;width:288px;top:252px;height:132px;box-sizing:border-box;padding:6px 12px;border-radius:8px;background:rgba(13,15,13,.55);border:1px solid rgba(194,197,184,.22);display:flex;align-items:center;justify-content:center;text-align:center;font-size:${fs}px;line-height:1.05;color:#ECE6D6">${esc(c.t)}</div>`
    : `<div style="position:absolute;left:16px;width:288px;top:252px;height:132px;display:flex;align-items:center;justify-content:center;text-align:center;font-style:italic;font-size:24px;color:#9aa49d">Its pips count as any element.</div>`;
  return `<div style="${BODY};background:#2A2F32"><svg width="320" height="448" style="position:absolute;top:0;left:0" aria-hidden="true"><rect x="5.5" y="5.5" width="309" height="437" rx="10" fill="none" stroke="#7E8A90" stroke-width="1" stroke-dasharray="3 5" opacity=".55"/></svg><div style="${TITLE};top:10px;font-style:italic">${esc(c.b)}</div><div style="${PANEL};top:52px;height:132px;background:rgba(0,0,0,.25)"></div>${row(c.bp, 190, 50)}${text}${foot(c, c.fb ? "FORCE · FLIPS BACK" : "FORCE")}</div>`;
}
// a face as a scaled token: size in px of the card's width
export function token(ci, back, w, extra = "") {
  const c = CARDS[ci], s = w / 320;
  return `<div class="tok${back ? " back" : ""} ${extra}" style="--s:${s.toFixed(4)}"><div class="face">${back ? backHtml(c) : frontHtml(c)}</div></div>`;
}
