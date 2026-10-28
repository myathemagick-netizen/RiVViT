import {Body,HelioVector} from '../vendor/astronomy-engine/astronomy.mjs';
const YEAR_MS=365.25*86400000, AU_KM=149597870.7, AU_LY=63241.07708426628;
const J2000=Date.parse('2000-01-01T12:00:00Z');
export const SATURN_FIT_SPEED=24.25;
export const SIRIUS_ORBIT={periodYears:50.1284,periastronYear:1994.5715,eccentricity:.59142,axisArcsec:7.4957};
// Catalogue track of Sirius A: ICRS/J2000, SIMBAD values retrieved 2026-10-13.
// Linear space motion, not a precision system-barycentre or A/B ephemeris.
const ra=(6+45/60+8.91728/3600)*15*Math.PI/180;
const dec=-(16+42/60+58.0171/3600)*Math.PI/180;
const distanceAU=1000/379.21*206264.80624709636;
const n=[Math.cos(dec)*Math.cos(ra),Math.cos(dec)*Math.sin(ra),Math.sin(dec)];
const east=[-Math.sin(ra),Math.cos(ra),0];
const north=[-Math.sin(dec)*Math.cos(ra),-Math.sin(dec)*Math.sin(ra),Math.cos(dec)];
const masRad=Math.PI/(180*3600000);
const velocity=n.map((v,i)=>v*(-5.5)*365.25*86400/AU_KM+distanceAU*masRad*(-546.01*east[i]-1223.07*north[i]));
export function binaryAtYear(year){
  if(!Number.isFinite(year)) throw new Error('Invalid Sirius year');
  const phase=((year-SIRIUS_ORBIT.periastronYear)/SIRIUS_ORBIT.periodYears%1+1)%1;
  const mean=phase*2*Math.PI,e=SIRIUS_ORBIT.eccentricity;
  let eccentric=mean;
  for(let i=0;i<15;i++) eccentric-=(eccentric-e*Math.sin(eccentric)-mean)/(1-e*Math.cos(eccentric));
  return {phase,separationAU:SIRIUS_ORBIT.axisArcsec/(379.21/1000)*(1-e*Math.cos(eccentric))};
}
export function siriusAt(time,speedKmSec=SATURN_FIT_SPEED){
  if(!Number.isFinite(time)||!Number.isFinite(speedKmSec)||speedKmSec<=0) throw new Error('Invalid Sirius inputs');
  const years=(time-J2000)/YEAR_MS;
  const star=n.map((v,i)=>v*distanceAU+velocity[i]*years);
  const earth=HelioVector(Body.Earth,new Date(time));
  const relative=star.map((v,i)=>v-[earth.x,earth.y,earth.z][i]);
  const earthDistanceAU=Math.hypot(...relative),sunDistanceAU=Math.hypot(...star);
  const raDeg=(Math.atan2(relative[1],relative[0])*180/Math.PI+360)%360;
  const decDeg=Math.asin(relative[2]/earthDistanceAU)*180/Math.PI;
  return {distanceLY:earthDistanceAU/AU_LY,sunDistanceLY:sunDistanceAU/AU_LY,
    raDeg,decDeg,...binaryAtYear(2000+years),
    assumedTravelYears:earthDistanceAU*AU_KM/(speedKmSec*365.25*86400),speedKmSec,
    lightTravelYears:earthDistanceAU/AU_LY};
}
