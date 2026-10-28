// Human-facing coordinate input. Decimal pairs are latitude, longitude;
// GeoJSON output is explicitly longitude, latitude.
export function parseCoordinates(input){
  let value=String(input??'').trim();
  if(!value)throw Error('Paste coordinates first.');
  if(/^https?:\/\//i.test(value)){
    const url=new URL(value);
    value=url.searchParams.get('params')||'';
    value=value.split(/_(?:region|type|scale|dim|source):/i)[0];
  }
  value=value.replace(/_/g,' ').replace(/[º]/g,'°').replace(/[′’]/g,"'").replace(/[″”]/g,'"').replace(/''/g,'"').replace(/^coordinates?\s*:\s*/i,'');
  function result(latitude,longitude){
    if(!Number.isFinite(latitude)||!Number.isFinite(longitude)||Math.abs(latitude)>90||Math.abs(longitude)>180)throw Error('Latitude must be within ±90° and longitude within ±180°.');
    return {latitude,longitude,geometry:{type:'Point',coordinates:[longitude,latitude]}};
  }
  if(value.startsWith('{')){
    let geo;try{geo=JSON.parse(value);}catch{throw Error('The GeoJSON point is not valid JSON.');}
    if(geo.type!=='Point'||!Array.isArray(geo.coordinates)||geo.coordinates.length!==2||geo.coordinates.some(v=>typeof v!=='number'))throw Error('Use a GeoJSON Point with two numeric coordinates.');
    return result(geo.coordinates[1],geo.coordinates[0]);
  }
  const hemispheres=value.match(/^\s*([+\-\d.\s°'"]+)\s*([NS])\s*[,;]?\s*([+\-\d.\s°'"]+)\s*([EW])\s*$/i);
  if(hemispheres){
    const component=(raw,direction)=>{
      const values=raw.match(/[+\-]?\d+(?:\.\d+)?/g)?.map(Number)||[];
      if(!values.length||values.length>3||values.some(v=>v<0)||values.slice(1).some(v=>v>=60)||values.length>1&&!Number.isInteger(values[0])||values.length>2&&!Number.isInteger(values[1]))throw Error('Use degrees, minutes below 60, and seconds below 60; N/S/E/W gives the direction.');
      const degrees=values[0]+(values[1]||0)/60+(values[2]||0)/3600;
      return /[SW]/i.test(direction)?-degrees:degrees;
    };
    return result(component(hemispheres[1],hemispheres[2]),component(hemispheres[3],hemispheres[4]));
  }
  const decimal=value.match(/^\s*([+\-]?\d+(?:\.\d+)?)\s*[,;]\s*([+\-]?\d+(?:\.\d+)?)\s*$/);
  if(decimal)return result(Number(decimal[1]),Number(decimal[2]));
  throw Error('Paste Wikipedia coordinates such as 59°19′46″N 18°4′7″E, or a decimal latitude, longitude pair.');
}
