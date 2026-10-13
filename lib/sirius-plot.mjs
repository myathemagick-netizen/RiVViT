import {binaryAtYear} from './sirius.mjs';
const start=Date.parse('1830-01-01T00:00:00Z'),end=Date.parse('2026-12-31T00:00:00Z');
export function drawSiriusPlot(ctx,width,height,time,top=0){
  const left=64,right=width-32,y0=top+28,y1=top+height-25;
  ctx.fillStyle='#08121d';ctx.fillRect(0,top,width,height);
  ctx.font='17px sans-serif';ctx.fillStyle='#a5bbff';ctx.fillText('SIRIUS A/B · orbital separation · 0–35 AU · same dates',left,top+19);
  ctx.strokeStyle='#29374b';ctx.beginPath();ctx.moveTo(left,y1);ctx.lineTo(right,y1);ctx.stroke();
  ctx.strokeStyle='#a5bbff';ctx.lineWidth=2;ctx.beginPath();
  for(let i=0;i<=500;i++){
    const t=start+(end-start)*i/500;
    const year=2000+(t-Date.parse('2000-01-01T12:00:00Z'))/(365.25*86400000);
    const y=y1-binaryAtYear(year).separationAU/35*(y1-y0),x=left+(right-left)*i/500;
    if(i===0)ctx.moveTo(x,y);else ctx.lineTo(x,y);
  }
  ctx.stroke();const x=left+(right-left)*(time-start)/(end-start);
  ctx.strokeStyle='#ead4a6';ctx.beginPath();ctx.moveTo(x,y0);ctx.lineTo(x,y1);ctx.stroke();
}
