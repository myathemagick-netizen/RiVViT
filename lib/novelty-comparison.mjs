import {dateMs,waveAt} from './novelty-wave.mjs';
export function compareEpoch(event,record,anchor){
 if(!record || event.year!==record.year) return null;
 const wave=waveAt(dateMs(event.year+'-07-01'),anchor);
 return {year:event.year,opening:record.opening,min:record.min,max:record.max,wave:wave.value,
  face:record.min>0?'North all samples':record.max<0?'South all samples':'Changes within year',
  signMatch:event.kind==='crest'?record.opening>0:record.opening<0};
}
