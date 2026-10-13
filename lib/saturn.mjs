import {Body,GeoVector,Ecliptic,EclipticLongitude,RotationAxis} from '../vendor/astronomy-engine/astronomy.mjs';
const RAD=180/Math.PI;
const angleDifference=(a,b)=>((a-b+540)%360)-180;
export function saturnAt(time){
  if(!Number.isFinite(time)) throw new Error('Invalid Saturn date');
  const date=new Date(time);
  const apparent=GeoVector(Body.Saturn,date,true);
  const ecliptic=Ecliptic(apparent);
  // Unaberrated Earth-to-Saturn vector and IAU pole both use EQJ.
  const geometric=GeoVector(Body.Saturn,date,false);
  const distance=Math.hypot(geometric.x,geometric.y,geometric.z);
  const lightDays=distance/173.1446326846693;
  const axis=RotationAxis(Body.Saturn,new Date(time-lightDays*86400000)).north;
  const dot=-(axis.x*geometric.x+axis.y*geometric.y+axis.z*geometric.z)/distance;
  const opening=Math.asin(Math.max(-1,Math.min(1,dot)))*RAD;
  const before=Ecliptic(GeoVector(Body.Saturn,new Date(time-43200000),true)).elon;
  const after=Ecliptic(GeoVector(Body.Saturn,new Date(time+43200000),true)).elon;
  return {longitude:ecliptic.elon,latitude:ecliptic.elat,distanceAU:distance,
    heliocentricLongitude:EclipticLongitude(Body.Saturn,date),
    earthLongitude:EclipticLongitude(Body.Earth,date),
    motion:angleDifference(after,before)<0?'Retrograde':'Direct',
    ringOpening:opening,northPoleAngle:90-opening,
    face:Math.abs(opening)<.5?'Near edge-on':opening>0?'North face toward Earth':'South face toward Earth'};
}
