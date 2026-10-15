"""Cinematic Living World: configurable, deterministic environment compositor.
Requires Python, numpy, OpenCV, Pillow, ffmpeg and ffprobe. No Resolve dependency.
Usage: python render.py input.mp4 scene.json output.mp4 [--seconds 12]
Scene coordinates are source pixels. Design and inspect masks for each new video.
"""
import argparse, json, math, subprocess, re
from pathlib import Path
import cv2
import numpy as np
from PIL import ImageColor

cv2.setNumThreads(1)

DEFAULT_PRISM_COLORS=np.array([[.08,.10,1.],[1.,.12,.72],[1.,.95,.05],[.05,.65,1.]],np.float32)

def resolve_palette(value=None):
    """Return BGR light colors. Reject unclear colors so the agent can clarify."""
    if value is None or (isinstance(value,str) and value.strip().lower()=='default'):
        return DEFAULT_PRISM_COLORS.copy()
    if not isinstance(value,list) or not 1<=len(value)<=3:
        raise ValueError('Choose one to three colors by name or #RGB/#RRGGBB, or use default.')
    colors=[]
    for name in value:
        if not isinstance(name,str):raise ValueError('Each color must be a name or hex string. Ask for clarification.')
        token=name.strip().lower()
        if re.fullmatch(r'#?[0-9a-f]{6}|#[0-9a-f]{3}',token):
            token=token if token.startswith('#') else '#'+token
        else:
            token=''.join(token.split())
            if token not in ImageColor.colormap:
                raise ValueError(f'Unclear color {name!r}. Ask for its exact shade or hex code; do not guess.')
        rgb=ImageColor.getrgb(token)
        colors.append(rgb[::-1])
    if not np.any(colors):
        raise ValueError('An all-black palette produces no light. Ask for a visible highlight color.')
    return np.array(colors,np.float32)/255

class World:
    def __init__(self, cfg):
        self.c=cfg
        self.prism_colors=resolve_palette(cfg.get('prism_colors'))
        self.w,self.h=cfg['size']; self.y0,self.y1=cfg['strip']
        self.Y,self.X=np.mgrid[self.y0:self.y1,0:self.w].astype(np.float32)
        mask=np.zeros(self.X.shape,np.uint8)
        cv2.fillPoly(mask,[np.array(cfg['environment_polygon'],np.int32)-[0,self.y0]],255)
        for x0,y0,x1,y1 in cfg['protected_rectangles']:
            cv2.rectangle(mask,(x0,y0-self.y0),(x1,y1-self.y0),0,-1)
        # Feather inward only, so no effect leaks outside the designated environment.
        self.mask=np.minimum(mask/255.,cv2.GaussianBlur(mask/255.,(0,0),3)).astype(np.float32)
        self.water=np.exp(-((self.Y-cfg['water_y'])/40)**4)*np.exp(-((self.X-cfg['water_x'])/270)**6)*self.mask
        self.flowers=[]
        for x,y,rx,ry,phase in cfg['flowers']:
            s=np.clip(1-((self.X-x)/rx)**2-((self.Y-y)/ry)**2,0,1)**2*self.mask
            self.flowers.append((x,y,s,phase))
        self.prism_regions=[]
        for x0,y0,x1,y1,orientation,phase in cfg.get('prism_regions',[]):
            yy,xx=np.mgrid[y0:y1,x0:x1].astype(np.float32)
            # Each region is an explicit safe frame rectangle; all edges feather inward.
            edge=np.minimum.reduce([xx-x0,x1-1-xx,yy-y0,y1-1-yy])
            feather=np.clip(edge/18,0,1)
            self.prism_regions.append((x0,y0,x1,y1,orientation,phase,xx,yy,feather))

    def prism(self,out,t):
        """Broad spectral light wash, confined to user-defined frame rectangles."""
        colors=self.prism_colors
        for x0,y0,x1,y1,axis,phase,X,Y,feather in self.prism_regions:
            along=Y if axis=='vertical' else X
            across=X if axis=='vertical' else Y
            lo,hi=(y0,y1) if axis=='vertical' else (x0,x1)
            a0,a1=(x0,x1) if axis=='vertical' else (y0,y1)
            center=(lo+hi)/2+(hi-lo)*.62*math.sin(t*2*math.pi/9+phase)
            envelope=np.exp(-((along-center)/(430 if axis=='vertical' else 300))**2)
            width=a1-a0
            drift=(a0+a1)/2+width*.18*math.sin(t*2*math.pi/6+phase)
            # Dispersed rainbow bands bend and travel together, like light through a prism.
            bend=width*.20*np.sin(along*.004+t*.7+phase)
            light=np.zeros((*X.shape,3),np.float32)
            for k,color in enumerate(colors):
                if len(colors)==4:
                    offset=(k-1.5)*width*.24
                    spread=width*.20
                else:
                    offset=0 if len(colors)==1 else (-.36+.72*k/(len(colors)-1))*width
                    spread=width*{1:.60,2:.32,3:.24}[len(colors)]
                stripe=np.exp(-((across-drift-bend-offset)/spread)**2)
                light+=stripe[...,None]*color*.88
            light=np.clip(light*envelope[...,None]*feather[...,None],0,.94)
            p=out[y0:y1,x0:x1].astype(np.float32)
            out[y0:y1,x0:x1]=np.clip(255-(255-p)*(1-light),0,255).astype(np.uint8)

    @staticmethod
    def light(im,x,y,r,intensity,color,star=False):
        h,w=im.shape[:2];x=int(x);y=int(y)
        x0=max(0,x-r);x1=min(w,x+r+1);y0=max(0,y-r);y1=min(h,y+r+1)
        if x1<=x0 or y1<=y0:return
        Y,X=np.mgrid[y0:y1,x0:x1];dx=X-x;dy=Y-y
        a=np.exp(-(dx*dx+dy*dy)/(r*r*.20))*.55
        if star:
            a+=np.exp(-dx*dx/3-dy*dy/(r*r*.55))*.8
            a+=np.exp(-dy*dy/3-dx*dx/(r*r*.55))*.8
        a=np.clip(a*intensity,0,.85)[...,None]
        p=im[y0:y1,x0:x1].astype(np.float32)
        im[y0:y1,x0:x1]=np.clip(255-(255-p)*(1-a*np.array(color)/255),0,255).astype(np.uint8)

    def apply(self,im,t):
        out=im.copy();X,Y=self.X,self.Y
        dx=12*np.sin(Y*.12-t*2.0)*self.water
        dy=2.3*np.sin(X*.04-t*1.3)*self.water
        for x,y,s,phase in self.flowers:
            v=.24*math.sin(t*2*math.pi/8+phase)
            dx+=(X-x)*s*v;dy+=(Y-y)*s*v
        strip=im[self.y0:self.y1]
        moved=cv2.remap(strip,(X+dx).astype(np.float32),(Y-self.y0+dy).astype(np.float32),cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT).astype(np.float32)
        # Traveling warm reflection bands, with actual water displacement above.
        band=(.5+.5*np.sin(Y*.20+X*.015-t*2.2))**9*self.water*.24
        moved=255-(255-moved)*(1-band[...,None]*np.array([.65,.88,1.]))
        # Local jewel contrast; the original presenter bypasses this branch entirely.
        moved=np.clip((moved-110)*1.035+110,0,255)
        m=self.mask[...,None]
        out[self.y0:self.y1]=np.clip(moved*m+strip*(1-m),0,255).astype(np.uint8)
        for x,y,phase in self.c['glints']:
            pulse=max(0,math.sin(t*2*math.pi/4.6+phase))**6
            self.light(out,x,y,34,.95*pulse,[240,248,255],True)
        x,y=self.c['moon_emblem']
        self.light(out,x,y,68,.15+.65*(.5+.5*math.sin(t*2*math.pi/5)),[170,218,255])
        # Light follows existing frame rails; no new moon or floating decorative labels.
        for x,phase in self.c['light_rails']:
            y=300+(self.h-650)*(.5+.5*math.sin(t*2*math.pi/11+phase))
            self.light(out,x,y,22,.85,[185,235,255],True)
        self.prism(out,t)
        return out

def main():
    p=argparse.ArgumentParser();p.add_argument('source');p.add_argument('scene');p.add_argument('output');p.add_argument('--seconds',type=float);p.add_argument('--effect',choices=['prism','world'],default='prism',help='prism: light leak only (default); world: all configured environment effects')
    a=p.parse_args();cfg=json.loads(Path(a.scene).read_text());src=Path(a.source);dest=Path(a.output)
    if src.resolve()==dest.resolve():raise ValueError('Never overwrite source')
    if a.seconds is not None and a.seconds<=0:raise ValueError('seconds must be positive')
    cap=cv2.VideoCapture(str(src)); w=int(cap.get(3));h=int(cap.get(4));fps=cap.get(5);total=int(cap.get(7))
    if [w,h]!=cfg['size'] or fps<=0:raise ValueError('Scene/source geometry mismatch')
    world=World(cfg);dest.parent.mkdir(parents=True,exist_ok=True)
    limit=min(total,round(a.seconds*fps)) if a.seconds else total
    cmd=['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','bgr24','-s',f'{w}x{h}','-r',str(fps),'-i','-','-i',str(src),'-map','0:v','-map','1:a:0?','-c:v','libx264','-preset','veryfast','-crf','18','-threads','4','-pix_fmt','yuv420p','-c:a','copy','-t',str(limit/fps),'-movflags','+faststart',str(dest)]
    process=subprocess.Popen(cmd,stdin=subprocess.PIPE);count=0
    try:
        while count<limit:
            ok,im=cap.read()
            if not ok:raise RuntimeError('Source decoding ended early')
            out=im.copy()
            if a.effect=='prism':world.prism(out,count/fps)
            else:out=world.apply(im,count/fps)
            if count%300==0:
                for x0,y0,x1,y1 in cfg.get('verify_unchanged',[]):
                    if not np.array_equal(im[y0:y1,x0:x1],out[y0:y1,x0:x1]):raise AssertionError('Protected region changed')
            process.stdin.write(out.tobytes());count+=1
            if count%900==0:print(f'Rendered {count/fps:.0f}s',flush=True)
    finally:
        cap.release();process.stdin.close();rc=process.wait()
    if rc:raise RuntimeError('Encoder failed')
    Path(str(dest)+'.json').write_text(json.dumps({'frames':count,'fps':fps,'size':[w,h],'effects':a.effect,'protected_region_checks':'every 300 frames before encoding','human_motion_approval':'pending'},indent=2))
    print('Finished',count,flush=True)

if __name__=='__main__':main()
