"""Procedural, original background music (no samples, no copyright)."""
import numpy as np, soundfile as sf
SR=44100
rng=np.random.default_rng(7)
def midi(m): return 440*2**((m-69)/12)
def env(n,a,d,s=0.0,r=None):
    t=np.arange(n)/SR; e=np.minimum(1,t/max(a,1e-4))*np.exp(-t/d)
    return e*(1-s)+s*np.minimum(1,t/max(a,1e-4))
def piano(f,dur,vel=0.5):
    n=int(dur*SR); t=np.arange(n)/SR; y=np.zeros(n)
    for k,amp in [(1,1),(2,.45),(3,.22),(4,.12),(5,.06)]:
        y+=amp*np.sin(2*np.pi*f*k*t*(1+0.0004*k))*np.exp(-t*(1.2+0.9*k))
    y*=np.minimum(1,t/0.004); return vel*y
def guitar(f,dur,vel=0.4):  # Karplus-Strong pluck
    n=int(dur*SR); N=int(SR/f); buf=rng.uniform(-1,1,N); y=np.zeros(n)
    for i in range(n):
        y[i]=buf[i%N]; buf[i%N]=0.5*(buf[i%N]+buf[(i+1)%N])*0.996
    return vel*y
def pad(freqs,dur,vel=0.08):
    n=int(dur*SR); t=np.arange(n)/SR; y=np.zeros(n)
    for f in freqs:
        for det in (-0.12,0,0.12):
            y+=np.sin(2*np.pi*f*2**(det/12)*t+rng.uniform(0,6))
    a=np.minimum(1,t/0.8)*np.minimum(1,(dur-t)/0.8); return vel*y*a/len(freqs)
def kick(vel=0.6):
    n=int(0.35*SR); t=np.arange(n)/SR; f=50+90*np.exp(-t*25)
    return vel*np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*9)
def hat(vel=0.08):
    n=int(0.06*SR); x=rng.normal(0,1,n); x=np.diff(x,prepend=0)
    return vel*x*np.exp(-np.arange(n)/SR*70)
def snap(vel=0.12):
    n=int(0.18*SR); x=rng.normal(0,1,n); t=np.arange(n)/SR
    return vel*(x*np.exp(-t*30)+0.5*np.sin(2*np.pi*190*t)*np.exp(-t*25))
def add(buf,x,at):
    i=int(at*SR); j=min(len(buf),i+len(x));
    if i<len(buf): buf[i:j]+=x[:j-i]
# chord progressions (warm major / Persian-friendly)
PROG={"A":[(57,[57,61,64,69]),(54,[54,57,61,66]),(50,[50,54,57,62]),(52,[52,56,59,64])],  # A F#m D E
      "D":[(50,[50,54,57,62]),(47,[47,50,54,59]),(43,[43,47,50,55]),(45,[45,49,52,57])],  # D Bm G A
      "G":[(43,[55,59,62,67]),(40,[52,55,59,64]),(36,[48,52,55,60]),(38,[50,54,57,62])]}
def track(dur,bpm,key,style):
    L=int((dur+1)*SR); mix=np.zeros(L); beat=60/bpm; bar=4*beat; prog=PROG[key]
    nb=int(np.ceil(dur/bar))+1
    for b in range(nb):
        root,ch=prog[b%4]; t0=b*bar
        add(mix,pad([midi(m) for m in ch[:3]],bar+0.5,0.05 if style!="soft" else 0.07),t0)
        add(mix,piano(midi(root-12),bar,0.18),t0)
        if style=="soft":   # sparse piano arpeggio
            for k,m in enumerate([ch[0]+12,ch[1]+12,ch[2]+12,ch[-1]+12,ch[2]+12,ch[1]+12]):
                add(mix,piano(midi(m),1.6,0.13),t0+k*bar/6)
        elif style=="cafe":  # guitar pluck pattern + soft brush
            for k in range(8):
                m=ch[[0,2,1,3,0,2,1,2][k]]+12; add(mix,guitar(midi(m),0.9,0.22),t0+k*beat/2)
            for k in range(4): add(mix,hat(0.04),t0+k*beat+beat/2)
            add(mix,kick(0.25),t0); add(mix,kick(0.2),t0+2*beat)
        else:               # beat / upbeat
            for k in range(8):
                m=ch[[0,1,2,3,2,1,2,3][k]]+12; add(mix,piano(midi(m),0.8,0.11),t0+k*beat/2)
            for k in range(4):
                add(mix,kick(0.45 if style=="beat" else 0.4),t0+k*beat if style=="upbeat" else t0+(k%2)*2*beat)
                if k%2: add(mix,snap(0.12),t0+k*beat)
            for k in range(8): add(mix,hat(0.05),t0+k*beat/2)
    mix=mix[:int(dur*SR)]
    # gentle stereo-ish reverb (mono early reflections)
    for dly,g in [(0.031,0.25),(0.047,0.2),(0.083,0.15),(0.121,0.1)]:
        d=int(dly*SR); mix[d:]+=g*mix[:-d]
    mix/=np.max(np.abs(mix))+1e-9; return mix*0.8
def fade(x,fi=1.0,fo=1.5):
    n=len(x); a=int(fi*SR); b=int(fo*SR); x=x.copy()
    x[:a]*=np.linspace(0,1,a); x[n-b:]*=np.linspace(1,0,b); return x
# SFX
def whoosh(d=0.45,vel=0.18):
    n=int(d*SR); x=rng.normal(0,1,n); y=np.zeros(n); a=0.0
    cut=np.linspace(0.02,0.25,n)**1.5
    for i in range(n): a+=cut[i]*(x[i]-a); y[i]=a
    e=np.sin(np.pi*np.arange(n)/n)**2; return vel*y*e/np.max(np.abs(y))
def tick(vel=0.25):
    n=int(0.05*SR); t=np.arange(n)/SR; return vel*np.sin(2*np.pi*2200*t)*np.exp(-t*90)
def sparkle(vel=0.06):
    n=int(1.2*SR); y=np.zeros(n)
    for k,f in enumerate([2637,3136,3520,4186]):
        t=np.arange(n-int(k*0.07*SR))/SR; y[int(k*0.07*SR):]+=np.sin(2*np.pi*f*t)*np.exp(-t*5)
    return vel*y/4
