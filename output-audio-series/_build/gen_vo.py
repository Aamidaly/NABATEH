import sys,os,json,numpy as np,soundfile as sf
sys.path.insert(0,os.path.dirname(__file__)+"/..")
from tts import make
from scripts import R
B=os.path.dirname(os.path.abspath(__file__))
VOICE="vits-piper-fa_IR-gyro-medium"; SPEED=0.9
t=make(VOICE); out={}
for n,lines in R.items():
    segs=[];cur=0.0
    for i,(st,txt,_) in enumerate(lines):
        a=t.generate(txt,sid=0,speed={1:0.9,2:1.0,3:0.92,4:0.97}[n]); s=np.array(a.samples,np.float32); sr=a.sample_rate
        # trim silence
        idx=np.where(np.abs(s)>0.01)[0]; s=s[max(0,idx[0]-400):idx[-1]+800]
        start=max(st,cur+0.3) if i else st; d=len(s)/sr; cur=start+d
        sf.write(f"{B}/vo_{n}_{i}.wav",s,sr); segs.append([start,d])
    out[n]={"segs":segs,"sr":sr,"end":cur}
    print(n,[(round(a,2),round(b,2)) for a,b in segs],"end",round(cur,2))
json.dump(out,open(B+"/vo_timing.json","w"))
