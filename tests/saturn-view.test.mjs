import assert from 'node:assert/strict';
import {earthFacingNorth,orbitPoint} from '../lib/saturn-view.mjs';
for(const opening of [-26,0,26]){
 const n=earthFacingNorth(opening);assert.ok(Math.abs(Math.hypot(n.x,n.y,n.z)-1)<1e-12);
 assert.ok(Math.abs(Math.asin(n.z)*180/Math.PI-opening)<1e-12);
}
assert.deepEqual(orbitPoint(0,100),{x:100,y:-0});
assert.ok(Math.abs(orbitPoint(90,100).y+100)<1e-12);
assert.ok(Math.abs(orbitPoint(360,100).x-100)<1e-12);
console.log('PASS: signed Earth-facing tilt and orbital diagram coordinates.');
