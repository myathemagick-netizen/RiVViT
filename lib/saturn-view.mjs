export function earthFacingNorth(opening){const a=opening*Math.PI/180;return {x:0,y:Math.cos(a),z:Math.sin(a)};}
export function orbitPoint(longitude,radius){const a=longitude*Math.PI/180;return {x:radius*Math.cos(a),y:-radius*Math.sin(a)};}
export function createSaturnView(THREE){
  const group=new THREE.Group();group.visible=false;
  const planetFrame=new THREE.Group();group.add(planetFrame);
  const bands=document.createElement('canvas');bands.width=512;bands.height=256;
  const b=bands.getContext('2d');
  for(let y=0;y<256;y++){
    const stripe=Math.sin(y*.28)*9+Math.sin(y*.075)*13;
    b.fillStyle='rgb('+Math.round(191+stripe)+','+Math.round(166+stripe)+','+Math.round(115+stripe)+')';b.fillRect(0,y,512,1);
  }
  const bandTexture=new THREE.CanvasTexture(bands);bandTexture.colorSpace=THREE.SRGBColorSpace;
  const globe=new THREE.Mesh(new THREE.SphereGeometry(.245,48,32),new THREE.MeshPhongMaterial({map:bandTexture,emissive:0x30210e,shininess:8}));
  globe.scale.y=.902;planetFrame.add(globe);
  // Geometry is a ring plane around +Y. The Earth-facing opening rotates it about X.
  const ringColors=[0x85795f,0xd8c599,0xe8d6af,0x9d8f72,0xc0af88];
  [[.30,.335],[.34,.41],[.413,.455],[.468,.49],[.495,.54]].forEach(([a,z],i)=>{
    const ring=new THREE.Mesh(new THREE.RingGeometry(a,z,96),new THREE.MeshBasicMaterial({color:ringColors[i],side:THREE.DoubleSide}));
    ring.rotation.x=-Math.PI/2;planetFrame.add(ring);
  });
  const pole=new THREE.ArrowHelper(new THREE.Vector3(0,1,0),new THREE.Vector3(0,.245,0),.22,0x81d9ed,.045,.025);planetFrame.add(pole);
  function canvasPlane(width,height,w,h,y){
    const canvas=document.createElement('canvas');canvas.width=width;canvas.height=height;
    const texture=new THREE.CanvasTexture(canvas);texture.colorSpace=THREE.SRGBColorSpace;
    const mesh=new THREE.Mesh(new THREE.PlaneGeometry(w,h),new THREE.MeshBasicMaterial({map:texture,transparent:true,depthWrite:false}));mesh.position.y=y;group.add(mesh);
    return {canvas,texture,mesh,ctx:canvas.getContext('2d')};
  }
  const header=canvasPlane(1024,150,1.2,.176,.64);
  const hc=header.ctx;hc.fillStyle='#e9d6ad';hc.font='bold 44px sans-serif';hc.textAlign='center';hc.fillText('SATURN · EARTH-FACING VIEW',512,55);hc.fillStyle='#83d8eb';hc.font='30px sans-serif';hc.fillText('Blue arrow: north pole · illustrative scale',512,110);header.texture.needsUpdate=true;
  const orbit=canvasPlane(900,520,1.3,.751,-.86);
  const stateCard=canvasPlane(1024,180,1.2,.211,-.38);
  const viewPosition=new THREE.Vector3();
  function layout(inVR,camera){
    const zoom=inVR?1:camera.position.z/3.2;
    group.position.set(inVR?-1.05:-1.75*zoom,inVR?1.45:.72*zoom,inVR?-1.6:0);
    group.scale.setScalar(inVR?.75:zoom);
    camera.getWorldPosition(viewPosition);group.lookAt(viewPosition);
  }
  function update(state,date){
    const north=earthFacingNorth(state.ringOpening);
    planetFrame.quaternion.setFromUnitVectors(new THREE.Vector3(0,1,0),new THREE.Vector3(north.x,north.y,north.z));
    const c=stateCard.ctx;c.clearRect(0,0,1024,180);c.fillStyle='rgba(4,10,18,.9)';c.fillRect(0,0,1024,180);c.textAlign='center';
    c.fillStyle='#e6d2a7';c.font='40px sans-serif';c.fillText(date+' · '+state.face,512,52,990);
    c.fillStyle='#bdcad7';c.font='32px sans-serif';c.fillText('Ring opening '+state.ringOpening.toFixed(2)+'° · '+state.distanceAU.toFixed(3)+' AU',512,107);
    c.font='24px sans-serif';c.fillText('Calculated tilt; sky roll and surface features are illustrative',512,153);stateCard.texture.needsUpdate=true;
    const o=orbit.ctx;o.clearRect(0,0,900,520);o.fillStyle='rgba(4,10,18,.95)';o.fillRect(0,0,900,520);
    o.fillStyle='#e6d2a7';o.font='bold 37px sans-serif';o.textAlign='center';o.fillText('SUN-CENTERED ORBITAL POSITION',450,43);
    const cx=450,cy=265;
    for(const radius of [100,175]){o.strokeStyle='#40566b';o.lineWidth=2;o.beginPath();o.arc(cx,cy,radius,0,Math.PI*2);o.stroke();}
    o.fillStyle='#f3d579';o.beginPath();o.arc(cx,cy,15,0,Math.PI*2);o.fill();o.font='24px sans-serif';o.fillText('Sun',cx,cy+42);
    function dot(lon,radius,color,label){const point=orbitPoint(lon,radius),x=cx+point.x,y=cy+point.y;o.fillStyle=color;o.beginPath();o.arc(x,y,9,0,Math.PI*2);o.fill();o.font='34px sans-serif';o.fillText(label,x,y-22);}
    dot(state.earthLongitude,100,'#82d3ed','Earth');dot(state.heliocentricLongitude,175,'#e9c98d','Saturn');
    o.strokeStyle='#657284';o.beginPath();o.moveTo(cx+170,cy);o.lineTo(cx+195,cy);o.stroke();o.fillStyle='#a3b1c0';o.font='22px sans-serif';o.fillText('0°',cx+220,cy+7);
    o.fillStyle='#bdcad7';o.font='32px sans-serif';o.fillText('Saturn '+state.heliocentricLongitude.toFixed(2)+'° · Earth '+state.earthLongitude.toFixed(2)+'°',450,462);
    o.font='26px sans-serif';o.fillText('Ecliptic of date · circular schematic · distances not to scale',450,501);orbit.texture.needsUpdate=true;
  }
  return {group,update,layout};
}
