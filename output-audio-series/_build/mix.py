import sys,os,json,numpy as np,soundfile as sf,subprocess
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import music
from render import REELS
B=os.path.dirname(os.path.abspath(__file__))+"/"
SR=44100
def load_vo(path):
    x,sr=sf.read(path,dtype="float32")
    if sr!=SR:
        t=np.arange(int(len(x)*SR/sr))/SR; x=np.interp(t,np.arange(len(x))/sr,x).astype(np.float32)
    return x
def db(x): return 20*np.log10(np.sqrt(np.mean(x**2))+1e-9)
def smooth_env(x,att=0.05,rel=0.35):
    e=np.abs(x); out=np.zeros_like(e); a=np.exp(-1/(att*SR)); r=np.exp(-1/(rel*SR)); v=0
    # block-wise for speed
    blk=256; eb=e[:len(e)//blk*blk].reshape(-1,blk).max(1); ob=np.zeros_like(eb)
    a=np.exp(-blk/(att*SR)); r=np.exp(-blk/(rel*SR))
    for i,s in enumerate(eb): v= a*v+(1-a)*s if s>v else r*v+(1-r)*s; ob[i]=v
    return np.repeat(ob,blk)[:len(e)] if len(ob)*blk>=len(e) else np.pad(np.repeat(ob,blk),(0,len(e)-len(ob)*blk),mode="edge")
def mix(n,outdir):
    cfg=REELS[n]; dur=cfg["dur"]; L=int(dur*SR)
    tm=json.load(open(B+"vo_timing.json"))[str(n)]
    vo=np.zeros(L,np.float32)
    for i,(st,d) in enumerate(tm["segs"]):
        x=load_vo(B+f"vo_{n}_{i}.wav"); j=int(st*SR); k=min(L,j+len(x)); vo[j:k]+=x[:k-j]
    vo*=10**((-16-db(vo[vo!=0]))/20)        # narration ~ -16 dBFS RMS (active)
    bpm,key,style=cfg["music"]
    m=music.track(dur,bpm,key,style)
    if n==2:  # beat hits harder on the first cuts, then softens
        t=np.arange(len(m))/SR; m*=np.where(t<3.4,1.15,0.85)
    m=music.fade(m,0.6,1.6)
    m*=10**((-18.5-db(m))/20)
    # SFX
    sfx=np.zeros(L,np.float32)
    bounds=[s["t0"] for s in cfg["shots"][1:]]
    for b in bounds:
        if n==3 and b<10: continue
        w=music.whoosh(0.4,0.10 if n!=3 else 0.08); music.add(sfx,w,b-0.25)
    if n==3:
        for i in (1,2,3): music.add(sfx,music.tick(0.22),tm["segs"][i][0]-0.1)
        for b in bounds:
            if b<10: music.add(sfx,music.whoosh(0.25,0.05),b-0.15)
    music.add(sfx,music.sparkle(0.05),cfg["cta_t"]+0.1)
    music.add(sfx,music.sparkle(0.035),0.25)
    # ducking: music -10 dB under narration, extra -3 dB in final CTA
    env=smooth_env(vo,0.04,0.30); env=np.clip(env/ (np.percentile(env[env>0],60)+1e-9),0,1)
    gain=10**((-9.5*env)/20)
    t=np.arange(L)/SR; gain*=np.where(t>dur-3.2,10**(-3/20),1.0)
    mus=m[:L]*gain
    full=vo+mus+sfx; mo=mus+sfx*0.8
    for name,x in (("full",full),("music-only",mo)):
        pk=np.max(np.abs(x)); x=x/pk*0.89 if pk>0.89 else x
        sf.write(B+f"mix_{n}_{name}.wav",x.astype(np.float32),SR)
        subprocess.run(["ffmpeg","-v","error","-y","-i",f"{outdir}/reel-{n:02d}-silent.mp4","-i",B+f"mix_{n}_{name}.wav",
            "-map","0:v","-map","1:a","-c:v","copy","-c:a","aac","-b:a","192k","-shortest","-movflags","+faststart",f"{outdir}/reel-{n:02d}-{name}.mp4"],check=True)
    print(n,"vo",round(db(vo[np.abs(vo)>1e-4]),1),"music(under vo)",round(db(mus[np.abs(vo)>0.02]),1),"music(free)",round(db(mus[np.abs(vo)<1e-4]),1))
if __name__=="__main__": mix(int(sys.argv[1]),sys.argv[2])
