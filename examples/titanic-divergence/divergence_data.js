// divergence_data.js
//
// How far a one-ulp difference travels through a chaotic simulation. Runs the Titanic flooding model
// (the JavaScript oracle of the companion sinksim project) twice through the calibrated 1912 scenario:
// as published, and with one parameter (the breach discharge coefficient) moved by exactly one ulp.
// Optionally also compares two golden traces of the same run made on different machines.
//
// Usage: node divergence_data.js <titanic-sim package dir> [golden_a.json golden_b.json] > divergence.csv
// Columns: t_min, dpitch_ulp_deg, dvol_ulp_m3, events_ulp, dpitch_golden_deg, dvol_golden_m3
'use strict';
const fs = require('fs');
const path = require('path');
const pkg = process.argv[2];
if (!pkg) { console.error('usage: node divergence_data.js <titanic-sim package dir> [golden_a.json golden_b.json]'); process.exit(2); }
const C = require(path.resolve(pkg, 'core/core.js'));
const SC = require(path.resolve(pkg, 'core/scenarios.js'));
const ship = C.buildShip();

function runTrace(params) {
  const sim = C.createSim(ship, params, SC.PRESETS.titanic.build());
  const rec = [];
  let next = 0;
  while (!sim.foundered && sim.t < 5 * 3600) {
    if (sim.t >= next - 1e-9) { rec.push({ t: sim.t, pitch: sim.pitch, roll: sim.roll, vol: Array.from(sim.vol) }); next += 60; }
    C.step(sim);
  }
  return { rec, events: sim.events, founderT: sim.founderT };
}
const deg = (r) => r * 180 / Math.PI;
function diff(a, b) {
  const n = Math.min(a.length, b.length), rows = [];
  for (let i = 0; i < n; i++) {
    let sv = 0;
    for (let k = 0; k < 64; k++) sv += Math.abs(a[i].vol[k] - b[i].vol[k]);
    rows.push({ t: a[i].t / 60, dpitch: deg(Math.abs(a[i].pitch - b[i].pitch)), dvol: sv });
  }
  return rows;
}

const base = runTrace({});
const nudged = runTrace({ CdBreach: 0.60 * (1 + Number.EPSILON) });   // 0.6 moved by one ulp
const ulp = diff(base.rec, nudged.rec);
const shifts = base.events.map((e, i) => (nudged.events[i] ? nudged.events[i].t - e.t : NaN));
let golden = null;
if (process.argv[4]) {
  const A = JSON.parse(fs.readFileSync(process.argv[3], 'utf8')).trace;
  const B = JSON.parse(fs.readFileSync(process.argv[4], 'utf8')).trace;
  golden = diff(A, B);
}
console.error(`founder: base ${base.founderT} s, nudged ${nudged.founderT} s; event shifts (s): ` +
  base.events.map((e, i) => `${e.id} ${shifts[i] >= 0 ? '+' : ''}${shifts[i].toFixed(2)}`).join(', '));
const out = ['t_min,dpitch_ulp_deg,dvol_ulp_m3,dpitch_golden_deg,dvol_golden_m3'];
for (let i = 0; i < ulp.length; i++) {
  const g = golden && golden[i] ? golden[i] : { dpitch: '', dvol: '' };
  out.push([ulp[i].t, ulp[i].dpitch, ulp[i].dvol, g.dpitch, g.dvol].join(','));
}
console.log(out.join('\n'));
