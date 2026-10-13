export function nearestPanel(raycaster,panels){
  return panels.map(panel=>({kind:panel.kind,hit:raycaster.intersectObject(panel.mesh,false)[0]}))
    .filter(panel=>panel.hit).sort((a,b)=>a.hit.distance-b.hit.distance)[0] || null;
}
