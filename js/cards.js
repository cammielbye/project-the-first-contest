// Drawing cards. Every card is drawn from its data in data/cards.json, so a
// card-pool sync changes what's on screen with no other edits.

const SVG_NS = "http://www.w3.org/2000/svg";

// Classical alchemical symbols: fire and air point up, water and earth point
// down, air and earth carry a bar (as on the Card Anatomy drafts).
const SYMBOL_PATHS = {
  fire: ["M12 3 L21.5 20 H2.5 Z"],
  water: ["M2.5 4 H21.5 L12 21 Z"],
  air: ["M12 3 L21.5 20 H2.5 Z", "M5.6 14.2 H18.4"],
  earth: ["M2.5 4 H21.5 L12 21 Z", "M5.6 9.8 H18.4"],
  any: ["M12 2.5 L14.2 9.8 L21.5 12 L14.2 14.2 L12 21.5 L9.8 14.2 L2.5 12 L9.8 9.8 Z"],
};

export function symbol(kind) {
  const svg = document.createElementNS(SVG_NS, "svg");
  svg.setAttribute("viewBox", "0 0 24 24");
  svg.setAttribute("class", `sym sym-${kind}`);
  const title = document.createElementNS(SVG_NS, "title");
  title.textContent = kind === "any" ? "any element" : kind;
  svg.appendChild(title);
  for (const d of SYMBOL_PATHS[kind] || []) {
    const p = document.createElementNS(SVG_NS, "path");
    p.setAttribute("d", d);
    svg.appendChild(p);
  }
  return svg;
}

const el = (tag, cls, text) => {
  const n = document.createElement(tag);
  if (cls) n.className = cls;
  if (text != null) n.textContent = text;
  return n;
};

// One face of a card, as a DOM element.
//   face: "permanence" | "force" | "meta"
//   size: "token" (on the table) or "full" (binder, preview)
export function renderFace(card, face, opts = {}) {
  const { size = "full", inst = null } = opts;
  if (card.meta) face = "meta";
  const root = el("div", `card ${size} face-${face} r-${card.rarity}`);
  if (face === "force" && !card.force) root.classList.add("undrafted");
  if (inst) {
    root.dataset.iid = inst.iid;
    root.classList.add(`own-${inst.owner}`);
    if (inst.original) root.classList.add("original");
  }

  const inner = el("div", "c-inner");
  root.appendChild(inner);

  let name;
  let body = "";
  if (face === "meta") {
    name = card.meta.name;
    body = card.meta.text;
  } else if (face === "force") {
    name = card.force ? card.force.name : "Force face not drafted";
    body = card.force ? card.force.text : "";
  } else {
    name = card.permanence.name;
    body = card.permanence.text;
  }
  inner.appendChild(el("div", "c-name", name));

  if (size === "full") {
    const kind = face === "meta" ? "Meta" : face === "force" ? "Force" : "Permanence";
    inner.appendChild(el("div", "c-kind", inst && inst.original ? `${kind} · original` : kind));
  }

  if (face === "force") {
    if (card.force && card.force.duration) inner.appendChild(el("div", "c-dur", card.force.duration));
  } else if (face === "permanence") {
    const affs = el("div", "c-tags");
    for (const a of card.permanence.affinities || []) affs.appendChild(symbol(a));
    inner.appendChild(affs);
  } else {
    inner.appendChild(el("div", "c-dur", "Either player"));
  }

  if (size === "full") {
    if (body) inner.appendChild(el("div", "c-text", body));
    if (face === "permanence" && card.permanence.note) inner.appendChild(el("div", "c-note", card.permanence.note));
  }

  const foot = el("div", "c-foot");
  foot.appendChild(el("span", "c-no", card.no ? `${card.no}/100` : "meta"));
  foot.appendChild(el("span", "c-rar", card.rarity));
  inner.appendChild(foot);
  return root;
}

export function otherFace(face) {
  if (face === "meta") return "meta";
  return face === "force" ? "permanence" : "force";
}
