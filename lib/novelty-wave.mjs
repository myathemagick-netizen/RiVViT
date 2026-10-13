export const DAY_MS = 86400000;
export const PERIOD_DAYS = 29.5 * 365.2425;
export const MIN_DATE = '1830-01-01';
export const MAX_DATE = '2026-12-31';
export const DEFAULT_ANCHOR = '1931-07-01';
export function dateMs(date){
  const value=Date.parse(date+'T00:00:00Z');
  if(!Number.isFinite(value)) throw new Error('Invalid timeline date');
  return value;
}
export function clampTime(value){return Math.max(dateMs(MIN_DATE),Math.min(dateMs(MAX_DATE),value));}
export function waveAt(time,anchor=dateMs(DEFAULT_ANCHOR)){
  const phase=(((time-anchor)/(PERIOD_DAYS*DAY_MS))%1+1)%1;
  return {value:Math.cos(phase*Math.PI*2),phase,
    name:(phase<1e-9 || phase>1-1e-9)?'Novelty crest':Math.abs(phase-.5)<1e-9?'Tradition trough':phase<.25?'Waning':phase<.5?'Collapse':phase<.75?'Renewal':'Ascent'};
}
export function timeAtFraction(fraction){return dateMs(MIN_DATE)+Math.max(0,Math.min(1,fraction))*(dateMs(MAX_DATE)-dateMs(MIN_DATE));}
export function fractionAtTime(time){return (clampTime(time)-dateMs(MIN_DATE))/(dateMs(MAX_DATE)-dateMs(MIN_DATE));}
export function isoDate(time){return new Date(clampTime(time)).toISOString().slice(0,10);}
