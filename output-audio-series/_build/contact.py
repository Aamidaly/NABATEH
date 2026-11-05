import sys,subprocess,numpy as np
from PIL import Image,ImageDraw
from render import REELS
import fx
n=int(sys.argv[1]); d=sys.argv[2]; cfg=REELS[n]; sh=cfg["shots"]
tw,th=270,480; cols=5; rows=(len(sh)+cols-1)//cols
im=Image.new("RGB",(cols*tw,rows*(th+70)+90),(30,18,8)); dr=ImageDraw.Draw(im)
dr.text((cols*tw-20,20),f"ریلز {fx.fa_digits(str(n))} — contact sheet",font=fx.font("Bold",34),fill=(255,230,200),anchor="ra",direction="rtl",language="fa")
for k,s in enumerate(sh):
    t=(s["t0"]+s["t1"])/2
    raw=subprocess.run(["ffmpeg","-v","error","-ss",str(t),"-i",f"{d}/reel-{n:02d}-silent.mp4","-frames:v","1","-vf",f"scale={tw}:{th}","-f","rawvideo","-pix_fmt","rgb24","-"],capture_output=True).stdout
    fr=Image.frombytes("RGB",(tw,th),raw); x=(k%cols)*tw; y=90+(k//cols)*(th+70)
    im.paste(fr,(x,y))
    src=s["src"]+(".mov" if s["kind"]=="v" else "")
    dr.text((x+8,y+th+8),f"{s['t0']:.1f}-{s['t1']:.1f}s",font=fx.font("Bold",24),fill=(255,214,140))
    dr.text((x+8,y+th+38),src,font=fx.font("Regular",22),fill=(240,230,220))
im.save(f"{d}/contact-sheet.jpg",quality=88); print("ok",n)
