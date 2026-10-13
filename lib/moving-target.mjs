import {Body,HelioVector} from '../vendor/astronomy-engine/astronomy.mjs';
export const AU_KM=149597870.7, DAY_MS=86400000;
export const sub=(a,b)=>({x:a.x-b.x,y:a.y-b.y,z:a.z-b.z});
export const length=v=>Math.hypot(v.x,v.y,v.z);
export const dot=(a,b)=>a.x*b.x+a.y*b.y+a.z*b.z;
export const lerp=(a,b,f)=>({x:a.x+(b.x-a.x)*f,y:a.y+(b.y-a.y)*f,z:a.z+(b.z-a.z)*f});
// Simultaneous geometric vectors in an approximately inertial SSB/EQJ frame.
export function baryPosition(body,time){const date=new Date(time);return sub(HelioVector(body,date),HelioVector(Body.SSB,date));}
export function solveArrival({departure,speedKmSec,position=baryPosition,maxDays=1826.2125,stepDays=.25}){
 if(!Number.isFinite(departure)||!Number.isFinite(speedKmSec)||speedKmSec<=0||!Number.isFinite(maxDays)||!Number.isFinite(stepDays)||maxDays<=0||stepDays<=0) throw new Error('Invalid moving-target parameters');
 const source=position(Body.Saturn,departure),speedAUms=speedKmSec/AU_KM/1000;
 const residual=t=>length(sub(position(Body.Earth,t),source))-speedAUms*(t-departure);
 let previous=departure,previousValue=residual(previous);
 for(let elapsed=stepDays;elapsed<=maxDays+stepDays;elapsed+=stepDays){
  const now=departure+Math.min(elapsed,maxDays)*DAY_MS,value=residual(now);
  if(value<=0 && previousValue>0){
   let lo=previous,hi=now;for(let i=0;i<55;i++){const mid=(lo+hi)/2;if(residual(mid)>0)lo=mid;else hi=mid;}
   const arrival=(lo+hi)/2,target=position(Body.Earth,arrival);
   return {departure,arrival,travelDays:(arrival-departure)/DAY_MS,source,target,pathAU:length(sub(target,source)),speedKmSec,residualAU:residual(arrival)};
  }
  previous=now;previousValue=value;if(elapsed>=maxDays) break;
 }
 return null;
}
export function radialMotion(departure,position=baryPosition){
 const earth=position(Body.Earth,departure),saturn=position(Body.Saturn,departure);
 const delta=sub(earth,saturn),distance=length(delta),unit={x:delta.x/distance,y:delta.y/distance,z:delta.z/distance};
 const h=.01*DAY_MS;
 const velocity=body=>{const v=sub(position(body,departure+h),position(body,departure-h));return {x:v.x*AU_KM/(2*h/1000),y:v.y*AU_KM/(2*h/1000),z:v.z*AU_KM/(2*h/1000)};};
 return {earthRadialKmSec:dot(velocity(Body.Earth),unit),relativeSeparationRateKmSec:dot(sub(velocity(Body.Earth),velocity(Body.Saturn)),unit),distanceAU:distance};
}
export function segmentDistance(point,a,b){const ab=sub(b,a),denom=dot(ab,ab);if(denom===0)return {distance:length(sub(point,a)),fraction:0,interior:false};const raw=dot(sub(point,a),ab)/denom,fraction=Math.max(0,Math.min(1,raw));return {distance:length(sub(point,lerp(a,b,fraction))),fraction,interior:raw>0&&raw<1};}
export function minimumDuring(fn,start,end,stepDays=.25){
 if(end<=start||stepDays<=0)throw new Error('Invalid encounter interval');
 const samples=[];for(let t=start;t<end;t+=stepDays*DAY_MS)samples.push({time:t,value:fn(t)});samples.push({time:end,value:fn(end)});
 let best=samples.reduce((a,b)=>b.value<a.value?b:a);
 function refine(left,right){
  let lo=left,hi=right;
  for(let j=0;j<40;j++){const a=lo+(hi-lo)/3,b=hi-(hi-lo)/3;if(fn(a)<fn(b))hi=b;else lo=a;}
  const time=(lo+hi)/2,value=fn(time);if(value<best.value)best={time,value};
 }
 // Include the boundary intervals: a closest approach can occur between an endpoint and the first sample.
 if(Number.isFinite(samples[0].value)&&samples[0].value<=samples[1].value)refine(samples[0].time,samples[1].time);
 const last=samples.length-1;
 if(Number.isFinite(samples[last].value)&&samples[last].value<=samples[last-1].value)refine(samples[last-1].time,samples[last].time);
 for(let i=1;i<samples.length-1;i++){
  if(!Number.isFinite(samples[i].value))continue;
  if(samples[i].value>samples[i-1].value || samples[i].value>samples[i+1].value)continue;
  refine(samples[i-1].time,samples[i+1].time);
 }
 return best;
}
// Spherical radii: JPL planetary equatorial radii, library Sun and Moon constants.
export const INTERVENERS=[['Sun',695700],['Moon',1738.1],['Mercury',2440.53],['Venus',6051.8],['Mars',3396.19],['Jupiter',71492],['Uranus',25559],['Neptune',24764],['Pluto',1188.3]];
export function encounterReport(solution,{position=baryPosition,stepDays=.25}={}){
 const {departure,arrival,source,target}=solution;
 const packet=t=>lerp(source,target,(t-departure)/(arrival-departure));
 return INTERVENERS.map(([body,radiusKm])=>{
  const near=minimumDuring(t=>length(sub(position(body,t),packet(t))),departure,arrival,stepDays);
  const alignment=minimumDuring(t=>{const s=segmentDistance(position(body,t),source,target);return s.interior?s.distance:Infinity;},departure,arrival,stepDays);
  return {body,radiusKm,closestSameTimeKm:near.value*AU_KM,closestSameTimeDate:new Date(near.time).toISOString(),sphereOverlapCandidate:near.value*AU_KM<=radiusKm,
   closestSegmentKm:Number.isFinite(alignment.value)?alignment.value*AU_KM:null,closestSegmentDate:Number.isFinite(alignment.value)?new Date(alignment.time).toISOString():null,
   sameTimeKmAtSegmentAlignment:Number.isFinite(alignment.value)?length(sub(position(body,alignment.time),packet(alignment.time)))*AU_KM:null,
   interpretation:'Proximity and sphere-overlap geometry only; no blocking/delay effect assigned.'};
 });
}
