import assert from 'node:assert/strict';
import {saturnAt} from '../lib/saturn.mjs';
const at=date=>saturnAt(Date.parse(date+'T00:00:00Z'));
// NASA/JPL Horizons Saturn 699, Earth center 500@399, 2017-06-21 00:00 UTC,
// observer quantities 31,20,14, retrieved 2026-10-13.
const ref=at('2017-06-21');
assert.ok(Math.abs(ref.longitude-264.0957827)<.01);
assert.ok(Math.abs(ref.latitude-1.3454300)<.01);
assert.ok(Math.abs(ref.distanceAU-9.04704760753403)<.001);
// Horizons reports planetographic latitude; convert to planetocentric for the ring plane.
const expectedOpening=Math.atan((54364/60268)**2*Math.tan(31.630565*Math.PI/180))*180/Math.PI;
assert.ok(Math.abs(ref.ringOpening-expectedOpening)<.03);
assert.equal(ref.motion,'Retrograde');assert.ok(ref.ringOpening>0);
assert.ok(at('2000-01-01').ringOpening<0);
assert.ok(Math.abs(at('2025-03-23').ringOpening)<.1);
for(const date of ['1830-01-01','1931-07-01','2026-12-31']){
 const x=at(date);assert.ok(x.longitude>=0 && x.longitude<360);assert.ok(x.distanceAU>7 && x.distanceAU<12);assert.ok(Math.abs(x.ringOpening)<30);assert.ok(Number.isFinite(x.heliocentricLongitude));assert.ok(x.earthLongitude>=0 && x.earthLongitude<360);
}
assert.throws(()=>saturnAt(NaN));
console.log('PASS: JPL reference position/distance/pole geometry, north/south sign, edge-on epoch, range endpoints, and invalid dates.');
