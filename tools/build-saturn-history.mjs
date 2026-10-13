import fs from 'node:fs';
import {saturnAt} from '../lib/saturn.mjs';
import {dateMs,MIN_DATE,MAX_DATE,DEFAULT_ANCHOR,waveAt} from '../lib/novelty-wave.mjs';
const samples=[];
for(let year=1830;year<=2026;year++) for(const month of ['01','04','07','10']){
 const date=year+'-'+month+'-01';samples.push({date,opening:saturnAt(dateMs(date)).ringOpening});
}
samples.push({date:MAX_DATE,opening:saturnAt(dateMs(MAX_DATE)).ringOpening});
const events=JSON.parse(fs.readFileSync(new URL('../data/novelty-events.json',import.meta.url),'utf8').replace(/^\uFEFF/,''));
const epochs=events.map(event=>{
 const readings=[];for(let month=1;month<=12;month++) readings.push(saturnAt(dateMs(event.year+'-'+String(month).padStart(2,'0')+'-01')).ringOpening);
 readings.push(saturnAt(dateMs(event.year+'-12-31')).ringOpening);
 const opening=saturnAt(dateMs(event.year+'-07-01')).ringOpening;
 return {year:event.year,opening,min:Math.min(...readings),max:Math.max(...readings)};
});
fs.writeFileSync(new URL('../data/saturn-pole-history.json',import.meta.url),JSON.stringify({source:'Astronomy Engine 2.1.19 / IAU pole',units:'degrees',interval:'quarterly',epochsRange:'monthly samples plus December 31',samples,epochs},null,2)+'\n');
for(let i=0;i<epochs.length;i++) console.log(epochs[i].year,events[i].kind,epochs[i].opening.toFixed(2)+'°',epochs[i].min.toFixed(2)+'…'+epochs[i].max.toFixed(2));
