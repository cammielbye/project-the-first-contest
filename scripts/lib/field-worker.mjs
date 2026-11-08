// A worker thread for runField: plays its share of a run's contests and sends them back.
import { parentPort, workerData } from "node:worker_threads";
import { playOne, contestSeed } from "./field.mjs";

const { ks, seed, cfg } = workerData;
const out = [];
for (const k of ks) { const r = playOne(contestSeed(seed, k), cfg); if (r) out.push(Object.assign({ k }, r)); }
parentPort.postMessage(out);
