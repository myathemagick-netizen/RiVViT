"""Build original schematic route cards from RiVViT's own nodes and coast outlines."""
from pathlib import Path
import json, re, textwrap
import numpy as np
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parents[1]
s=(ROOT/'index.html').read_text(encoding='utf-8')
node_block=s.split('const VORTEX_NODES = [',1)[1].split('const EDGES',1)[0]
nodes={int(i):{'name':name,'lat':float(lat),'lon':float(lon)} for i,name,lat,lon in re.findall(r'id:\s*(\d+),\s*name:"([^"]+)"[^\n]*?lat:\s*([\d.-]+),\s*lon:\s*([\d.-]+)',node_block)}
assert len(nodes)==12
coasts=[]
for raw in re.findall(r'drawLand\((\[[\s\S]*?\]),\s*-?[\d.]+\s*\)',s):
    coasts.append(json.loads(re.sub(r'\s+','',raw)))
assert len(coasts)>5
tex=Image.new('RGB',(1800,900),(9,27,44)); td=ImageDraw.Draw(tex)
for coords in coasts:
    td.polygon([((lon+180)*5,(90-lat)*5) for lat,lon in coords],fill=(52,76,75),outline=(93,116,105))
texture=np.array(tex)
font_path=Path('C:/Windows/Fonts/segoeui.ttf')
bold_path=Path('C:/Windows/Fonts/seguisb.ttf')
def font(size,bold=False):return ImageFont.truetype(str(bold_path if bold else font_path),size)
def vector(lat,lon):
    a,b=np.radians([lat,lon]);return np.array([np.cos(a)*np.sin(b),np.sin(a),np.cos(a)*np.cos(b)])
records=json.loads((ROOT/'data/riftlines.json').read_text(encoding='utf-8-sig'))
for record in records:
    a,b=[nodes[i] for i in record['app_node_ids']]
    va,vb=vector(a['lat'],a['lon']),vector(b['lat'],b['lon'])
    front=va+vb;front/=np.linalg.norm(front)
    right=np.cross([0,1,0],front);right/=np.linalg.norm(right);up=np.cross(front,right)
    cx,cy,radius=450,457,298
    yy,xx=np.mgrid[0:900,0:900];x=(xx-cx)/radius;y=(cy-yy)/radius
    inside=x*x+y*y<=1; z=np.sqrt(np.maximum(0,1-x*x-y*y))
    vv=x[...,None]*right+y[...,None]*up+z[...,None]*front
    lat=np.degrees(np.arcsin(np.clip(vv[...,1],-1,1)));lon=np.degrees(np.arctan2(vv[...,0],vv[...,2]))
    tx=np.clip(((lon+180)*5).astype(int),0,1799);ty=np.clip(((90-lat)*5).astype(int),0,899)
    canvas=np.full((900,900,3),(5,12,23),dtype=np.uint8)
    shade=.6+.4*z
    canvas[inside]=(texture[ty,tx]*shade[...,None])[inside].astype(np.uint8)
    im=Image.fromarray(canvas);d=ImageDraw.Draw(im)
    def project(v):return (cx+radius*np.dot(v,right),cy-radius*np.dot(v,up))
    def line(points,color,width=1):
        segment=[]
        for v in points:
            if np.dot(v,front)>=0:
                segment.append(project(v))
            else:
                if len(segment)>1:d.line(segment,fill=color,width=width)
                segment=[]
        if len(segment)>1:d.line(segment,fill=color,width=width)
    for lat0 in range(-60,90,30):line([vector(lat0,t) for t in np.linspace(-180,180,361)],(38,61,77))
    for lon0 in range(-180,180,30):line([vector(t,lon0) for t in np.linspace(-90,90,181)],(38,61,77))
    d.ellipse((cx-radius,cy-radius,cx+radius,cy+radius),outline=(91,125,136),width=2)
    route=[]
    for t in np.linspace(0,1,141):
        v=va*(1-t)+vb*t;v/=np.linalg.norm(v);route.append(v)
    line(route,(105,84,53),13);line(route,(226,185,112),6)
    for v,label in [(va,record['endpoint_codes'][0]),(vb,record['endpoint_codes'][1])]:
        px,py=project(v);d.ellipse((px-9,py-9,px+9,py+9),fill=(245,213,151),outline=(255,240,207),width=2)
        d.text((px+13,py-23),label,font=font(26,True),fill=(255,234,183),stroke_width=2,stroke_fill=(5,12,23))
    d.text((35,20),'RiVViT  /  RIFTLINE '+str(record['atlas_number']).zfill(2),font=font(22),fill=(167,181,195))
    for j,title in enumerate(textwrap.wrap(record['name'],width=39)):
        d.text((35,53+j*42),title,font=font(34,True),fill=(229,197,140))
    d.text((35,784),record['endpoint_codes'][0]+'  '+a['name'],font=font(21),fill=(226,212,184))
    d.text((35,816),record['endpoint_codes'][1]+'  '+b['name'],font=font(21),fill=(226,212,184))
    d.text((35,862),'Schematic globe · geometric arc · MMS corridor framework',font=font(18),fill=(153,167,181))
    record['img']='images/riftlines/route-'+str(record['atlas_number']).zfill(2)+'.jpg'
    im.save(ROOT/record['img'],quality=90,optimize=True)
(ROOT/'data/riftlines.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Generated 30 original 900 × 900 route cards from existing geometry.')
