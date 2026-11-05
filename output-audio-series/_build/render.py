import sys,os,json,subprocess,numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import fx
from scripts import R as SCRIPTS
SC="/tmp/claude-0/-home-user-NABATEH/79480cad-93ff-53f0-81c1-df3fe70eaacc/scratchpad/"
IMG="/tmp/claude-0/-home-user-NABATEH/79480cad-93ff-53f0-81c1-df3fe70eaacc/images/"
VID=SC+"raw/videos/"
W,H,FPS=1080,1920,30
def V(name,ss,a,b,speed=1.0,sun=0.8,zoom=(1.0,1.05),focus=(0.5,0.5)):
    return dict(kind="v",src=name,ss=ss,t0=a,t1=b,speed=speed,sun=sun,zoom=zoom,focus=focus)
def P(name,a,b,sun=0.8,zoom=(1.0,1.1),focus=(0.5,0.5),pan=(0,0)):
    return dict(kind="i",src=name,t0=a,t1=b,sun=sun,zoom=zoom,focus=focus,pan=pan)

REELS={
1: dict(dur=18.3, xf=0.35, corner="tr", music=(100,"A","soft"), cta=("برای سفارش","«سفارش» رو دایرکت بفرست"), cta_t=14.9,
   shots=[V("IMG_6070",1.0,0,2.3,sun=1.0,zoom=(1.0,1.08)),
          V("IMG_6221",0.0,2.3,4.6,sun=1.0,zoom=(1.05,1.12),focus=(0.5,0.7)),
          P("4.jpg",4.6,6.3,sun=0.8,zoom=(1.0,1.12),focus=(0.55,0.55)),
          V("IMG_6099",4.0,6.3,8.2,sun=0.8),
          V("IMG_6024",9.0,8.2,9.6,sun=0.9,zoom=(1.0,1.06)),
          P("32.jpg",9.6,11.1,sun=0.9,zoom=(1.15,1.35),focus=(0.5,0.45)),
          V("IMG_6336",0.4,11.1,12.7,sun=0.9),
          V("IMG_6357",0.0,12.7,15.0,sun=1.0),
          P("15.jpg",15.0,18.3,sun=1.0,zoom=(1.0,1.08),focus=(0.55,0.55))]),
2: dict(dur=16.8, xf=0.25, corner="tl", music=(110,"D","beat"), cta=("فرق رو از نزدیک ببین","برای سفارش دایرکت بده"), cta_t=13.1,
   shots=[V("IMG_6024",2.0,0,1.1,sun=0.35,zoom=(1.1,1.2)),
          P("2.jpg",1.1,2.2,sun=0.35,zoom=(1.05,1.15)),
          V("IMG_6029",1.0,2.2,3.4,sun=0.35),
          P("3.jpg",3.4,5.9,sun=0.3,zoom=(1.0,1.08)),
          P("32.jpg",5.9,7.6,sun=0.75,zoom=(1.25,1.45),focus=(0.5,0.48)),
          V("IMG_6087",0.0,7.6,9.5,speed=0.75,sun=0.9,zoom=(1.0,1.06)),
          V("IMG_6070",5.0,9.5,11.2,sun=1.0),
          V("IMG_6331",5.0,11.2,12.9,sun=1.0),
          V("IMG_6349",4.5,12.9,16.8,sun=1.0,zoom=(1.0,1.06))]),
3: dict(dur=14.0, xf=0.12, corner="tr", music=(118,"G","upbeat"), cta=("باکس یلدایی نباته","«یلدا» رو دایرکت کن"), cta_t=10.0,
   shots=[P("9.jpg",0,1.6,sun=1.0,zoom=(1.15,1.0),focus=(0.55,0.65)),
          V("IMG_6205",1.0,1.6,2.5,sun=0.8,zoom=(1.0,1.08)),
          P("33.jpg",2.5,3.3,sun=0.8,zoom=(1.0,1.1)),
          P("10.jpg",3.3,4.2,sun=0.8,zoom=(1.05,1.15),focus=(0.5,0.62)),
          V("IMG_6087",0.2,4.2,5.1,sun=0.9),
          V("IMG_6029",3.0,5.1,6.0,sun=0.9),
          P("32.jpg",6.0,7.0,sun=0.9,zoom=(1.1,1.25)),
          P("18.jpg",7.0,7.8,sun=0.8,zoom=(1.0,1.1),focus=(0.5,0.4)),
          V("IMG_6380",4.5,7.8,8.7,speed=0.8,sun=0.8),
          V("IMG_6355",0.0,8.7,10.0,sun=1.0),
          P("15.jpg",10.0,14.0,sun=1.0,zoom=(1.02,1.1),focus=(0.55,0.55))]),
4: dict(dur=20.0, xf=0.4, corner="tr", music=(100,"D","cafe"), cta=("همون واکنش رو تو هم بگیر","«یلدا» رو بفرست تو دایرکت"), cta_t=15.7,
   shots=[V("IMG_6221",0.0,0,3.0,sun=1.0,zoom=(1.0,1.06),focus=(0.5,0.7)),
          V("IMG_6215",0.4,3.0,5.2,sun=0.9,zoom=(1.0,1.05)),
          P("1.jpg",5.2,7.4,sun=1.0,zoom=(1.08,1.0),focus=(0.45,0.72)),
          P("4.jpg",7.4,9.4,sun=0.8,zoom=(1.05,1.15),focus=(0.55,0.55)),
          P("5.jpg",9.4,12.0,sun=0.8,zoom=(1.0,1.1),focus=(0.55,0.5)),
          P("33.jpg",12.0,13.8,sun=0.9,zoom=(1.0,1.1)),
          V("IMG_6331",1.0,13.8,15.6,sun=0.9),
          V("IMG_6355",0.0,15.6,18.2,sun=1.0),
          P("15.jpg",18.2,20.0,sun=1.0,zoom=(1.05,1.12),focus=(0.55,0.55))]),
}

class VidShot:
    def __init__(s,sh,pre,post):
        s.sh=sh; s.pre=pre
        dur=(sh["t1"]-sh["t0"]+pre+post)*sh["speed"]+0.2
        ss=max(0,sh["ss"]-pre*sh["speed"])
        z0,z1=sh["zoom"]; zmax=max(z0,z1)
        cw,chh=int(W*zmax+2),int(H*zmax+2)
        vf=f"setpts=PTS/{sh['speed']},fps={FPS},scale={cw}:{chh}:force_original_aspect_ratio=increase,crop={cw}:{chh}"
        s.cw,s.ch=cw,chh
        s.p=subprocess.Popen(["ffmpeg","-v","error","-ss",str(ss),"-i",VID+sh["src"]+".mov","-t",str(dur),"-vf",vf,"-f","rawvideo","-pix_fmt","rgb24","-"],stdout=subprocess.PIPE)
        s.last=None; s.idx=-1
    def frame(s,i):
        while s.idx<i:
            b=s.p.stdout.read(s.cw*s.ch*3)
            if len(b)<s.cw*s.ch*3: break
            s.last=np.frombuffer(b,np.uint8).reshape(s.ch,s.cw,3); s.idx+=1
        return s.last
    def close(s): s.p.kill()
class ImgShot:
    def __init__(s,sh):
        im=Image.open(IMG+sh["src"]).convert("RGB")
        sc=max(W/im.width,H/im.height); s.im=im.resize((int(im.width*sc+1),int(im.height*sc+1)),Image.LANCZOS)
    def close(s): pass

def render_shot_frame(sh,obj,lt,span):
    """lt = local time from shot t0 (may be negative / beyond for overlaps); span = full shot length"""
    p=min(1,max(0,(lt+0.3)/(span+0.6)))
    z=sh["zoom"][0]+(sh["zoom"][1]-sh["zoom"][0])*(p*p*(3-2*p))
    fxp,fyp=sh["focus"]
    if sh["kind"]=="v":
        fr=obj.frame(int(round((lt+obj.pre)*FPS)))
        zmax=max(sh["zoom"]); cw,ch=obj.cw,obj.ch
        w,h=W*zmax/z,H*zmax/z
        x0=(cw-w)*fxp; y0=(ch-h)*fyp
        im=Image.fromarray(fr).resize((W,H),Image.BILINEAR,box=(x0,y0,x0+w,y0+h))
    else:
        iw,ih=obj.im.size; w,h=W/z,H/z
        x0=(iw-w)*fxp; y0=(ih-h)*fyp
        im=obj.im.resize((W,H),Image.BILINEAR,box=(x0,y0,x0+w,y0+h))
    return np.asarray(im,np.float32)/255

def build_overlays(n,cfg,timing):
    ov=[]  # (t_in,t_out,rgba,x,y,kind)
    segs=timing[str(n)]["segs"]; lines=SCRIPTS[n]
    for i,(st,_,disp) in enumerate(lines):
        if disp is None: continue
        a=segs[i][0]-0.1; b=(segs[i+1][0]-0.15) if i+1<len(segs) else segs[i][0]+segs[i][1]+0.5
        b=min(b,cfg["cta_t"]-0.05)
        if n==2 and i==1:   # "رنگ قشنگ = رنگ مصنوعی؟" with red strike
            ov.append((a,b,fx.text_rgba(["فکر می‌کنی رنگ قشنگ یعنی…"],62,"ExtraBold"),W/2,1080,"txt"))
            ov.append((a+0.6,b,fx.text_rgba(["رنگ مصنوعی؟"],104,"Black",fill=(235,70,60)),W/2,1220,"strike"))
            continue
        L=disp.split("\n"); size=92 if len(L)==1 and len(L[0])<16 else 70
        if n==3 and i in (1,2,3): size=70
        ov.append((a,b,fx.text_rgba(L,size,"Black" if size>80 else "ExtraBold"),W/2,1180,"txt"))
        if n==3 and i in (1,2,3):
            ov.append((a,b,fx.text_rgba([fx.fa_digits(str(i))],300,"Black",fill=(255,214,140)),W/2,880,"num"))
    # CTA card
    t=cfg["cta_t"]; e=cfg["dur"]
    ov.append((t,e+1,fx.text_rgba(["نباته"],150,"Black",fill=(255,240,214)),W/2,760,"cta"))
    ov.append((t+0.25,e+1,fx.text_rgba([cfg["cta"][0]],60,"Bold"),W/2,960,"cta"))
    ov.append((t+0.45,e+1,fx.text_rgba([cfg["cta"][1]],78,"Black",box=(150,70,20,170),pad=46),W/2,1100,"cta"))
    ov.append((t+0.7,e+1,fx.text_rgba(["ارسال به سراسر ایران  ·  پیش‌فروش باکس یلدایی"],40,"Medium"),W/2,1255,"cta"))
    return ov

def render(n,outdir,preview=None):
    cfg=REELS[n]; timing=json.load(open(SC+"build/vo_timing.json"))
    light=fx.Light(W,H,cfg["corner"]); handle=fx.handle_rgba(36)
    band=fx.radial(W,700,W/2,350,620,1.0); band=np.clip(band*1.6,0,1)
    yy=np.linspace(-1,1,700)[:,None]; band=band*np.clip(1-np.abs(yy)**3,0,1)
    BAND=Image.fromarray(np.dstack([np.full((700,W),25,np.uint8),np.full((700,W),12,np.uint8),np.full((700,W),2,np.uint8),(band*120).astype(np.uint8)]),"RGBA")
    ovs=build_overlays(n,cfg,timing)
    shots=cfg["shots"]; xf=cfg["xf"]; N=int(round(cfg["dur"]*FPS))
    objs={}
    os.makedirs(outdir,exist_ok=True)
    if preview: enc=None
    else: enc=subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-",
        "-c:v","libx264","-preset","medium","-crf","19","-pix_fmt","yuv420p","-profile:v","high","-movflags","+faststart",f"{outdir}/reel-{n:02d}-silent.mp4"],stdin=subprocess.PIPE)
    bounds=[s["t0"] for s in shots[1:]]
    rng_=range(N) if not preview else sorted(int(p*FPS) for p in preview)
    for fi in rng_:
        t=fi/FPS
        # active shots
        act=[]
        for k,sh in enumerate(shots):
            a=sh["t0"]-(xf/2 if k>0 else 0); b=sh["t1"]+(xf/2 if k<len(shots)-1 else 0.5)
            if a<=t<b: act.append(k)
            if k not in objs and t>=a-0.05 and t<b:
                pre=xf/2 if k>0 else 0; post=xf/2+0.5
                objs[k]=VidShot(sh,pre,post) if sh["kind"]=="v" else ImgShot(sh)
        for k in list(objs):
            if k not in act and t>shots[k]["t1"]+xf: objs[k].close(); del objs[k]
        frames=[]
        for k in act:
            sh=shots[k]; frames.append((k,render_shot_frame(sh,objs[k],t-sh["t0"],sh["t1"]-sh["t0"])))
        if len(frames)==1: img=frames[0][1]; sun=shots[frames[0][0]]["sun"]
        else:
            (k1,f1),(k2,f2)=frames[0],frames[1]; b=shots[k2]["t0"]
            w=min(1,max(0,(t-(b-xf/2))/xf)); w=w*w*(3-2*w)
            img=f1*(1-w)+f2*w; sun=shots[k1]["sun"]*(1-w)+shots[k2]["sun"]*w
        img=fx.grade(img,1.0)
        img=light.apply(img,t,sun=sun,drift=40)
        # light leak around cuts
        for j,b in enumerate(bounds):
            d=abs(t-b)
            if d<0.4: 
                L=fx.leak(W,H,(1-d/0.4)**2*(0.55 if n!=3 else 0.4),side=j)
                img=np.clip(img+L,0,1)
        # CTA darken
        if t>=cfg["cta_t"]:
            a=min(1,(t-cfg["cta_t"])/0.4)*0.42
            img=img*(1-a)+a*np.array([0.16,0.08,0.03],np.float32)
        # readability band behind captions
        cap=[ (a,b,y) for (a,b,r,x,y,k) in ovs if k in("txt","strike") and a<=t<b]
        if cap and t<cfg["cta_t"]:
            a,b,y=cap[0]; al=min(1,(t-a)/0.25,(b-t)/0.25)
            fx.paste(img,BAND,W/2,1150,al)
        # overlays
        for (a,b,rgba,x,y,kind) in ovs:
            if not(a<=t<b): continue
            fin=min(1,(t-a)/0.25); fout=min(1,(b-t)/0.25); al=min(fin,fout)
            dy=(1-fin)*30
            if kind=="num":
                sc=1.25-0.25*min(1,(t-a)/0.18); fx.paste(img,rgba,x,y,al,sc)
            elif kind=="strike":
                fx.paste(img,rgba,x,y,al)
                prog=min(1,max(0,(t-a-0.7)/0.35))
                if prog>0:
                    x0=x-rgba.width*0.38; x1=x0+(rgba.width*0.76)*prog
                    img[int(y-6):int(y+8),int(x0):int(x1)]=img[int(y-6):int(y+8),int(x0):int(x1)]*(1-al)+np.array([0.92,0.27,0.24])*al
            else:
                fx.paste(img,rgba,x,y+dy,al)
        fx.paste(img,handle,W/2,200,0.95)
        if preview: Image.fromarray((img*255+0.5).astype(np.uint8)).resize((540,960)).save(f"{outdir}/prev_{n}_{t:05.2f}.jpg",quality=85); continue
        enc.stdin.write((img*255+0.5).astype(np.uint8).tobytes())
        if fi%60==0: print(n,fi,"/",N,flush=True)
    if enc: enc.stdin.close(); enc.wait()
    for o in objs.values(): o.close()
if __name__=="__main__":
    n=int(sys.argv[1]); render(n,sys.argv[2])
