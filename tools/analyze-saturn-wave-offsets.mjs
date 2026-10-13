// Reproduce the documented phase-offset and distance observations.
import fs from 'node:fs';
import {saturnAt} from '../lib/saturn.mjs';
import {dateMs,DEFAULT_ANCHOR,PERIOD_DAYS,DAY_MS,MIN_DATE,MAX_DATE} from '../lib/novelty-wave.mjs';
const yearDays=365.2425,anchor=dateMs(DEFAULT_ANCHOR),period=PERIOD_DAYS*DAY_MS;
function peakNear(time){
 let best=time-6*yearDays*DAY_MS,value=-Infinity;
 for(let t=best;t<=time+6*yearDays*DAY_MS;t+=5*DAY_MS){const x=saturnAt(t).ringOpening;if(x>value){best=t;value=x;}}
 let lo=best-5*DAY_MS,hi=best+5*DAY_MS;
 for(let i=0;i<45;i++){const a=lo+(hi-lo)/3,b=hi-(hi-lo)/3;if(saturnAt(a).ringOpening>saturnAt(b).ringOpening)hi=b;else lo=a;}
 return (lo+hi)/2;
}
function row(time){const peak=peakNear(time);return {saturnPeak:new Date(peak).toISOString().slice(0,10),waveCrest:new Date(time).toISOString().slice(0,10),lagDays:(time-peak)/DAY_MS,distanceAtPeakAU:saturnAt(peak).distanceAU,distanceAtWaveAU:saturnAt(time).distanceAU};}
function stats(rows){const values=rows.map(r=>r.lagDays),mean=values.reduce((s,v)=>s+v,0)/values.length;return {count:rows.length,meanDays:mean,meanMonths:mean/(yearDays/12),meanYears:mean/yearDays,minYears:Math.min(...values)/yearDays,maxYears:Math.max(...values)/yearDays};}
function correlation(x,y){const mean=a=>a.reduce((s,v)=>s+v,0)/a.length,mx=mean(x),my=mean(y);return x.reduce((s,v,i)=>s+(v-mx)*(y[i]-my),0)/Math.sqrt(x.reduce((s,v)=>s+(v-mx)**2,0)*y.reduce((s,v)=>s+(v-my)**2,0));}
const calculated=[];
for(let k=-10;k<=10;k++){const time=anchor+k*period;if(time>=dateMs(MIN_DATE)&&time<=dateMs(MAX_DATE))calculated.push(row(time));}
const events=JSON.parse(fs.readFileSync(new URL('../data/novelty-events.json',import.meta.url),'utf8').replace(/^\uFEFF/,''));
const named=events.filter(e=>e.kind==='crest').map(e=>({markerYear:e.year,name:e.name,...row(dateMs(e.year+'-07-01'))}));
const x=calculated.map(r=>r.distanceAtPeakAU),y=calculated.map(r=>r.lagDays);
const report={reference:DEFAULT_ANCHOR,periodYears:29.5,yearDays,engine:'Astronomy Engine 2.1.19',interval:[MIN_DATE,MAX_DATE],method:'Maximum positive apparent Earth-facing ring opening within ±6 years of each reference; 5-day grid then 45 ternary refinements in ±5-day bracket. Dates shown to calendar-day precision; computations retain sub-day timestamps.',lagConvention:'Positive means the MMS crest follows the Saturn maximum.',distanceConvention:'Light-time-corrected geocentric vector length; distances at observation dates, not a solved chronon departure/arrival path.',calculated,calculatedStats:stats(calculated),namedYearMidpoints:named,namedStats:stats(named),distanceSummary:{peakMinAU:Math.min(...x),peakMaxAU:Math.max(...x),peakMaxOverMinPercent:(Math.max(...x)/Math.min(...x)-1)*100,lagMaxOverMinPercent:(Math.max(...y)/Math.min(...y)-1)*100,peakDistanceLagCorrelation:correlation(x,y),crestDistanceLagCorrelation:correlation(calculated.map(r=>r.distanceAtWaveAU),y)},interpretation:'Descriptive, calibration-dependent observations and a proposed MMS mechanism; no signal transit time, speed, or causation has been measured.'};
fs.writeFileSync(new URL('../doc/data/saturn-wave-observations.json',import.meta.url),JSON.stringify(report,null,2)+'\n');
console.log('Reproduced '+calculated.length+' calculated cycles; mean offset '+report.calculatedStats.meanDays.toFixed(2)+' days; named-year midpoint mean '+report.namedStats.meanYears.toFixed(2)+' years.');
