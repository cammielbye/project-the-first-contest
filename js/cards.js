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

export function symbol(el) {
  const svg = document.createElementNS(SVG_NS, "svg");
  svg.setAttribute("viewBox", "0 0 24 24");
  svg.setAttribute("class", `sym sym-${el}`);
  svg.setAttribute("aria-label", el);
  const title = document.createElementNS(SVG_NS, "title");
  title.textContent = el === "any" ? "any element" : el;
  svg.appendChild(title);
  for (const d of SYMBOL_PATHS[el] || []) {
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
//   size: "token" (on the table), "full" (binder, preview)
export function renderFace(card, face, opts = {}) {
  const { size = "full", inst = null } = opts;
  const isForce = face === "force";
  const root = el("div", `card ${size} face-${face} r-${card.rarity}`);
  if (isForce && !card.force) root.classList.add("undrafted");
  if (inst) {
    root.dataset.iid = inst.iid;
    root.classList.add(`own-${inst.owner}`);
    if (inst.original) root.classList.add("original");
  }

  const inner = el("div", "c-inner");
  root.appendChild(inner);

  const name = isForce ? (card.force ? card.force.name : "Force face not drafted") : card.permanence.name;
  inner.appendChild(el("div", "c-name", name));

  if (size === "full") {
    const kind = isForce ? "Force" : "Permanence";
    inner.appendChild(el("div", "c-kind", inst && inst.original ? `${kind} · original` : kind));
  }

  if (isForce) {
    if (card.force) inner.appendChild(el("div", "c-dur", card.force.duration));
  } else {
    const tags = el("div", "c-tags");
    for (const t of card.permanence.tags) tags.appendChild(symbol(t));
    inner.appendChild(tags);
  }

  if (size === "full") {
    const text = isForce ? (card.force ? card.force.effect : "") : card.permanence.effect;
    if (text) inner.appendChild(el("div", "c-text", text));
    if (!isForce && card.permanence.note) inner.appendChild(el("div", "c-note", card.permanence.note));
  }

  const foot = el("div", "c-foot");
  foot.appendChild(el("span", "c-no", `${card.no}/100`));
  foot.appendChild(el("span", "c-rar", card.rarity));
  inner.appendChild(foot);
  return root;
}

export function otherFace(face) {
  return face === "force" ? "permanence" : "force";
}
