import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
FONT="/tmp/claude-0/-home-user-NABATEH/79480cad-93ff-53f0-81c1-df3fe70eaacc/scratchpad/dl/vazir/fonts/ttf/Vazirmatn-%s.ttf"
def font(w,size): return ImageFont.truetype(FONT%w,size)
def fa_digits(s): return s.translate(str.maketrans("0123456789","۰۱۲۳۴۵۶۷۸۹"))

# ---------- grading & light ----------
def grade(img, warm=1.0):
    x=img
    x=np.clip((x-0.5)*1.05+0.5+0.01,0,1)                     # gentle contrast
    lum=(x[...,0]*.3+x[...,1]*.59+x[...,2]*.11)[...,None]
    x=lum+(x-lum)*(1+0.10*warm)                               # +saturation
    x=x*np.array([1+0.045*warm,1+0.012*warm,1-0.06*warm],np.float32)  # warm balance (amber), keep whites clean
    return np.clip(x,0,1)
def radial(W,H,cx,cy,r,power=2.0):
    yy,xx=np.mgrid[0:H,0:W].astype(np.float32)
    d=np.sqrt((xx-cx)**2+(yy-cy)**2)/r
    return np.clip(1-d,0,1)**power
class Light:
    def __init__(s,W,H,corner="tr"):
        s.W,s.H=W,H
        cx,cy=(W*1.02,-H*0.03) if corner=="tr" else (-W*0.02,-H*0.03)
        s.src=(cx,cy)
        g=radial(W,H,cx,cy,H*0.95,1.8)[...,None]
        s.glow=(g*np.array([1.0,0.70,0.36],np.float32)).astype(np.float32)
        core=radial(W,H,cx,cy,H*0.28,2.2)[...,None]
        s.core=(core*np.array([1.0,0.93,0.78],np.float32)).astype(np.float32)
        v=radial(W,H,W/2,H/2,np.hypot(W,H)*0.62,0.6)
        s.vig=(0.80+0.20*v)[...,None].astype(np.float32)
        # flare ghosts along the axis source->center
        s.flare=np.zeros((H,W,3),np.float32)
        for t,rad,a,col in [(0.55,70,0.10,(1,.8,.5)),(0.85,40,0.12,(1,.6,.4)),(1.25,120,0.06,(.9,.75,.5)),(1.55,28,0.12,(1,.85,.6))]:
            px=cx+(W/2-cx)*t; py=cy+(H/2-cy)*t
            m=radial(W,H,px,py,rad,1.2)[...,None]
            s.flare+=m*a*np.array(col,np.float32)
        # streak
        yy,xx=np.mgrid[0:H,0:W].astype(np.float32)
        streak=np.exp(-((yy-cy- (xx-cx)*0.0)**2)/(2*(H*0.006)**2))*np.clip(1-np.abs(xx-cx)/(W*1.1),0,1)
        s.flare+= (streak*0.10)[...,None]*np.array([1,.8,.55],np.float32)
        # dust particles
        rng=np.random.default_rng(3); s.n=46
        s.p=np.c_[rng.uniform(0,W,s.n),rng.uniform(0,H,s.n),rng.uniform(4,13,s.n),rng.uniform(.25,.8,s.n),rng.uniform(-12,12,s.n),rng.uniform(-30,-8,s.n),rng.uniform(0,6.28,s.n)]
        s.spr={}
    def sprite(s,r):
        r=int(r)
        if r not in s.spr:
            m=radial(2*r+1,2*r+1,r,r,r,2.0)[...,None]; s.spr[r]=m*np.array([1,.9,.7],np.float32)
        return s.spr[r]
    def apply(s,img,t,sun=1.0,drift=0.0):
        x=img
        k=0.5*sun
        x=1-(1-x)*(1-s.glow*k)                     # screen warm glow
        x=1-(1-x)*(1-s.core*0.35*sun)
        fl=s.flare*(0.75+0.25*np.sin(t*0.9))*sun
        if drift: fl=np.roll(fl,int(drift*np.sin(t*0.5)),axis=1)
        x=x+fl
        # dust: brighter near light source
        for (px,py,r,a,vx,vy,ph) in s.p:
            X=int((px+vx*t)%s.W); Y=int((py+vy*t)%s.H)
            near=1-min(1,np.hypot(X-s.src[0],Y-s.src[1])/(s.H*1.1))
            al=a*(0.5+0.5*np.sin(t*1.3+ph))*near*0.55*sun
            if al<0.02: continue
            sp=s.sprite(r); h=sp.shape[0]; r0=int(r)
            y0,y1=max(0,Y-r0),min(s.H,Y+r0+1); x0,x1=max(0,X-r0),min(s.W,X+r0+1)
            x[y0:y1,x0:x1]+=sp[y0-(Y-r0):h-((Y+r0+1)-y1), x0-(X-r0):h-((X+r0+1)-x1)]*al
        x=x*s.vig
        return np.clip(x,0,1)
def leak(W,H,amount,side=0):
    """warm light-leak overlay amount 0..1"""
    if amount<=0: return None
    cx=W*(1.1 if side%2==0 else -0.1); cy=H*(0.35 if side%2==0 else 0.65)
    g=radial(W//4,H//4,cx/4,cy/4,H/4*0.9,1.2)
    g=np.array(Image.fromarray((g*255).astype(np.uint8)).resize((W,H),Image.BILINEAR),np.float32)/255
    return (g[...,None]*np.array([1.0,0.55,0.25],np.float32))*amount*0.85

# ---------- text ----------
def text_rgba(lines, size, weight="Black", fill=(255,255,255), stroke=0, shadow=True, pad=40, lh=1.35, rtl=True, box=None):
    f=font(weight,size); tmp=ImageDraw.Draw(Image.new("L",(10,10)))
    kw=dict(direction="rtl",language="fa") if rtl else {}
    sizes=[tmp.textbbox((0,0),l,font=f,**kw) for l in lines]
    ws=[b[2]-b[0] for b in sizes]; lhpx=int(size*lh)
    W=max(ws)+2*pad; H=lhpx*len(lines)+2*pad
    im=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(im)
    if box:
        d.rounded_rectangle((pad*0.35,pad*0.35,W-pad*0.35,H-pad*0.35),radius=int(size*0.45),fill=box)
    if shadow:
        sh=Image.new("RGBA",(W,H),(0,0,0,0)); sd=ImageDraw.Draw(sh)
        for i,l in enumerate(lines):
            b=sizes[i]; sd.text(((W-ws[i])/2-b[0]+3,pad+i*lhpx-b[1]+(lhpx-(b[3]-b[1]))/2+5),l,font=f,fill=(40,20,0,170),**kw)
        sh=sh.filter(ImageFilter.GaussianBlur(size*0.09)); im=Image.alpha_composite(im,sh); d=ImageDraw.Draw(im)
    for i,l in enumerate(lines):
        b=sizes[i]
        d.text(((W-ws[i])/2-b[0],pad+i*lhpx-b[1]+(lhpx-(b[3]-b[1]))/2),l,font=f,fill=fill,stroke_width=stroke,stroke_fill=(60,30,0),**kw)
    return im
def handle_rgba(size=34):
    f=font("SemiBold",size); t="@nabateh.ir"
    b=ImageDraw.Draw(Image.new("L",(1,1))).textbbox((0,0),t,font=f)
    w,h=b[2]-b[0],b[3]-b[1]; W,H=w+56,h+30
    im=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(im)
    d.rounded_rectangle((0,0,W-1,H-1),radius=H//2,fill=(25,15,5,105))
    d.text((28-b[0],15-b[1]),t,font=f,fill=(255,247,232,255))
    return im
def paste(dst,rgba,x,y,alpha=1.0,scale=1.0):
    """dst float HxWx3, rgba PIL image; x,y = center"""
    if alpha<=0.01: return dst
    if scale!=1.0: rgba=rgba.resize((max(1,int(rgba.width*scale)),max(1,int(rgba.height*scale))),Image.LANCZOS)
    a=np.asarray(rgba,np.float32)/255; H,W=dst.shape[:2]
    x0=int(x-a.shape[1]/2); y0=int(y-a.shape[0]/2)
    sx0,sy0=max(0,-x0),max(0,-y0); x0c,y0c=max(0,x0),max(0,y0)
    x1c=min(W,x0+a.shape[1]); y1c=min(H,y0+a.shape[0])
    if x1c<=x0c or y1c<=y0c: return dst
    s=a[sy0:sy0+(y1c-y0c), sx0:sx0+(x1c-x0c)]
    al=s[...,3:4]*alpha
    dst[y0c:y1c,x0c:x1c]=dst[y0c:y1c,x0c:x1c]*(1-al)+s[...,:3]*al
    return dst
