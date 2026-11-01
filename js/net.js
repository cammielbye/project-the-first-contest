// The connection between the two players' browsers.
//
// PeerJS links the two browsers directly (WebRTC). PeerJS's free public
// broker only introduces them; game data then flows browser to browser.
// The host's browser keeps the shared table and sends it to the guest after
// every change; the guest sends its actions to the host.

const ID_PREFIX = "tfc-";

export function peerOptionsFromUrl(params) {
  const opts = { debug: Number(params.get("peerdebug") || 0) };
  if (params.get("peerhost")) {
    opts.host = params.get("peerhost");
    opts.port = Number(params.get("peerport") || 9000);
    opts.path = params.get("peerpath") || "/";
    opts.secure = params.get("peersecure") === "1";
    opts.key = "peerjs";
  }
  return opts;
}

export function createNet({ mode, room, peerOptions, onMessage, onStatus }) {
  const Peer = window.Peer;
  if (!Peer) {
    onStatus({ kind: "error", message: "The connection library didn't load." });
    return { send() {}, isOpen: () => false };
  }

  let peer = null;
  let conn = null;
  let retryTimer = null;
  const isOpen = () => !!(conn && conn.open);

  const send = (msg) => {
    if (isOpen()) conn.send(msg);
  };

  const wire = (c) => {
    c.on("open", () => {
      onStatus({ kind: "linked" });
      onMessage({ type: "_linked" });
    });
    c.on("data", (d) => onMessage(d));
    c.on("close", () => {
      if (conn === c) conn = null;
      onStatus({ kind: "unlinked" });
      if (mode === "guest") scheduleGuestConnect(3000);
    });
    c.on("error", () => {});
  };

  // ---- host ---------------------------------------------------------------
  function startHost() {
    peer = new Peer(ID_PREFIX + room, peerOptions);
    peer.on("open", () => onStatus({ kind: "waiting" }));
    peer.on("connection", (c) => {
      if (isOpen()) {
        c.on("open", () => {
          c.send({ type: "busy" });
          setTimeout(() => c.close(), 500);
        });
        return;
      }
      conn = c;
      wire(c);
    });
    peer.on("disconnected", () => {
      onStatus({ kind: "broker-lost" });
      setTimeout(() => peer && !peer.destroyed && peer.reconnect(), 2000);
    });
    peer.on("error", (err) => {
      if (err.type === "unavailable-id") {
        // The room code is still held by a previous visit; try again shortly.
        onStatus({ kind: "busy-id" });
        peer.destroy();
        clearTimeout(retryTimer);
        retryTimer = setTimeout(startHost, 4000);
      } else if (err.type !== "peer-unavailable") {
        onStatus({ kind: "error", message: err.type || String(err) });
      }
    });
  }

  // ---- guest --------------------------------------------------------------
  function guestConnect() {
    if (!peer || peer.destroyed || peer.disconnected) return;
    if (isOpen()) return;
    onStatus({ kind: "connecting" });
    const c = peer.connect(ID_PREFIX + room, { reliable: true });
    conn = c;
    wire(c);
  }

  function scheduleGuestConnect(ms) {
    clearTimeout(retryTimer);
    retryTimer = setTimeout(guestConnect, ms);
  }

  function startGuest() {
    peer = new Peer(undefined, peerOptions);
    peer.on("open", () => guestConnect());
    peer.on("disconnected", () => {
      setTimeout(() => peer && !peer.destroyed && peer.reconnect(), 2000);
    });
    peer.on("error", (err) => {
      if (err.type === "peer-unavailable") {
        onStatus({ kind: "host-missing" });
        conn = null;
        scheduleGuestConnect(4000);
      } else {
        onStatus({ kind: "error", message: err.type || String(err) });
      }
    });
  }

  if (mode === "host") startHost();
  else startGuest();

  return { send, isOpen };
}
