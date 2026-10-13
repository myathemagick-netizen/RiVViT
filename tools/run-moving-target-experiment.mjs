import fs from 'node:fs';
import {solveArrival,radialMotion,encounterReport,baryPosition,DAY_MS,AU_KM} from '../lib/moving-target.mjs';
const input=JSON.parse(fs.readFileSync(new URL('../doc/data/saturn-wave-observations.json',import.meta.url),'utf8'));
const cache=new Map();const position=(body,t)=>{const key=body+':'+t;if(!cache.has(key))cache.set(key,baryPosition(body,t));return cache.get(key);};
const cycles=input.calculated.map(row=>({...row,departure:Date.parse(row.saturnPeak+'T00:00:00Z'),referenceArrival:Date.parse(row.waveCrest+'T00:00:00Z')}));
function prediction(speed){return cycles.map(c=>{const s=solveArrival({departure:c.departure,speedKmSec:speed,position});return s?{solution:s,residualDays:(s.arrival-c.referenceArrival)/DAY_MS}:null;});}
const sweep=[];
for(let speed=20;speed<=35;speed+=.25){const rows=prediction(speed);if(rows.every(Boolean))sweep.push({speedKmSec:speed,rmseDays:Math.sqrt(rows.reduce((a,r)=>a+r.residualDays**2,0)/rows.length)});}
sweep.sort((a,b)=>a.rmseDays-b.rmseDays);const best=sweep[0],fitted=prediction(best.speedKmSec);
const average=cycles.reduce((s,c)=>s+(c.referenceArrival-c.departure)/DAY_MS,0)/cycles.length;
const baselineRMSE=Math.sqrt(cycles.reduce((s,c)=>s+((c.referenceArrival-c.departure)/DAY_MS-average)**2,0)/cycles.length);
const stationaryLengths=cycles.map(c=>radialMotion(c.departure,position).distanceAU*AU_KM);
const durations=cycles.map(c=>(c.referenceArrival-c.departure)/1000);
const inverseSpeed=stationaryLengths.reduce((s,v,i)=>s+v*durations[i],0)/stationaryLengths.reduce((s,v)=>s+v*v,0);
const stationarySpeed=1/inverseSpeed;
const stationaryRMSE=Math.sqrt(stationaryLengths.reduce((s,v,i)=>s+((v*inverseSpeed-durations[i])/86400)**2,0)/cycles.length);
const rows=cycles.map((c,i)=>{
 const fit=fitted[i],motion=radialMotion(c.departure,position),hazards=encounterReport(fit.solution,{position});
 const observedDays=(c.referenceArrival-c.departure)/DAY_MS;
 const departureState=position('Saturn',c.departure),earthAtReference=position('Earth',c.referenceArrival);
 const separation=Math.hypot(earthAtReference.x-departureState.x,earthAtReference.y-departureState.y,earthAtReference.z-departureState.z);
 return {departure:c.saturnPeak,referenceWaveCrest:c.waveCrest,...motion,requiredSpeedToReferenceKmSec:separation*AU_KM/(observedDays*86400),predictedArrival:new Date(fit.solution.arrival).toISOString(),travelDays:fit.solution.travelDays,residualDays:fit.residualDays,pathAU:fit.solution.pathAU,interveningBodies:hazards};
});
const report={hypothesis:'A freely expanding constant-speed spherical wave centered at Saturn departure, with the receiving ray directed to Earth at the earliest sampled arrival. Straight path in SSB/EQJ; no deflection, gravity, attenuation, or blockage effects.',frame:'Solar system barycenter, J2000 equatorial, simultaneous geometric ephemerides without light-time correction.',referenceCrests:input.reference,departureDefinition:'Stored calendar-day north-facing maximum, 00:00 UTC; day-rounded seed, not an observed emission event.',speedSweep:{minKmSec:20,maxKmSec:35,stepKmSec:.25,best,description:'In-sample exploratory fit to fixed-wave crests; not a measured speed and not fitted to independently dated events.'},baseline:{model:'One fitted constant delay',meanDays:average,rmseDays:baselineRMSE,stationaryDistanceModel:{speedKmSec:stationarySpeed,rmseDays:stationaryRMSE,description:'Freeze Earth at its departure position; one analytically fitted speed.'}},solver:{maxDays:1826.2125,bracketStepDays:.25,rootRefinements:55,limitation:'First sampled positive-to-nonpositive crossing; grazing/tangent arrivals can be missed.'},encounterSampling:{stepDays:.25,localMinRefinements:40,bodies:'Sun, Moon, Mercury, Venus, Mars, Jupiter, Uranus, Neptune, Pluto; Earth/Saturn are endpoints.',radiiSource:'https://ssd.jpl.nasa.gov/planets/phys_par.html; Astronomy Engine Sun/Moon constants',limitations:'Spherical radii and finite sampling; not an exhaustive occultation certification. Asteroids, rings, other moons, atmospheres, fields and hypothetical wavefront width are excluded.'},rows};
fs.writeFileSync(new URL('../doc/data/moving-target-experiment.json',import.meta.url),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({best,baselineRMSE,rows:rows.map(r=>({departure:r.departure,arrival:r.predictedArrival,reference:r.referenceWaveCrest,residualDays:r.residualDays,earthRadial:r.earthRadialKmSec,separationRate:r.relativeSeparationRateKmSec,nearestBody:r.interveningBodies.reduce((a,b)=>a.closestSameTimeKm<b.closestSameTimeKm?a:b),overlapCandidates:r.interveningBodies.filter(x=>x.sphereOverlapCandidate).map(x=>x.body)}))},null,2));
