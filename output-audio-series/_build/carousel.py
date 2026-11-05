import sys,os,numpy as np
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import fx
SC="/tmp/claude-0/-home-user-NABATEH/79480cad-93ff-53f0-81c1-df3fe70eaacc/scratchpad/"
IMG="/tmp/claude-0/-home-user-NABATEH/79480cad-93ff-53f0-81c1-df3fe70eaacc/images/"
W,H=1080,1350
CREAM=(255,244,226); AMBER=(150,70,20)
LIGHT={c:fx.Light(W,H,c) for c in ("tr","tl")}
def src(p): return SC+"vframes/"+p if p.endswith(".png") else IMG+p
def cover(path,focus=(0.5,0.5),zoom=1.0,box=(W,H)):
    im=Image.open(src(path)).convert("RGB"); bw,bh=box
    sc=max(bw/im.width,bh/im.height)*zoom; im=im.resize((int(im.width*sc+1),int(im.height*sc+1)),Image.LANCZOS)
    x=(im.width-bw)*focus[0]; y=(im.height-bh)*focus[1]
    return im.crop((int(x),int(y),int(x)+bw,int(y)+bh))
def sunlit(im,corner="tr",sun=0.9,t=1.3):
    a=np.asarray(im,np.float32)/255; a=fx.grade(a,1.0)
    L=LIGHT[corner] if im.size==(W,H) else fx.Light(im.size[0],im.size[1],corner)
    a=L.apply(a,t,sun=sun); return a
def grad(a,top=0.0,bottom=0.75,start=0.42):
    h=a.shape[0]; y=np.linspace(0,1,h)[:,None,None]
    g=np.clip((y-start)/(1-start),0,1)**1.3*bottom + np.clip((0.22-y)/0.22,0,1)*top
    return a*(1-g)+np.array([0.13,0.06,0.02],np.float32)*g
def to_img(a): return Image.fromarray((np.clip(a,0,1)*255+0.5).astype(np.uint8))
def put(im,rgba,cx,cy):
    im.paste(rgba,(int(cx-rgba.width/2),int(cy-rgba.height/2)),rgba)
def chrome(im,i,n):
    d=ImageDraw.Draw(im)
    c=fx.text_rgba([fx.fa_digits(f"{i}/{n}")],34,"Bold",shadow=False,box=(25,12,3,120),pad=26)
    put(im,c,W-40-c.width/2+14,62)
    h=fx.handle_rgba(32); put(im,h,W/2,H-52)
def title_block(im,title,body=None,y=None,tsize=86,label=None):
    tl=title.split("\n"); t=fx.text_rgba(tl,tsize,"Black",fill=(255,255,255))
    parts=[]
    if label: parts.append(fx.text_rgba([label],38,"Bold",fill=(255,226,180),box=(150,70,20,200),pad=30,shadow=False))
    parts.append(t)
    if body: parts.append(fx.text_rgba(body.split("\n"),42,"Medium",fill=(255,244,226),lh=1.55))
    tot=sum(p.height for p in parts)-40*(len(parts)-1)
    y0=(y if y else H-130-tot)
    for p in parts:
        put(im,p,W/2,y0+p.height/2); y0+=p.height-40
    return im
def photo_slide(path,title,body=None,label=None,focus=(0.5,0.5),zoom=1.0,corner="tr",tsize=86,grad_start=0.40):
    a=sunlit(cover(path,focus,zoom),corner); a=grad(a,0.35,0.85,grad_start)
    im=to_img(a); return title_block(im,title,body,tsize=tsize,label=label)
def cta_slide(path,lines,corner="tr",focus=(0.5,0.5)):
    im=cover(path,focus).filter(ImageFilter.GaussianBlur(14))
    a=sunlit(im,corner,1.0); a=a*0.45+np.array([0.20,0.10,0.04],np.float32)*0.55
    im=to_img(a)
    put(im,fx.text_rgba(["نباته"],170,"Black",fill=CREAM),W/2,330)
    put(im,fx.text_rgba(["قند و نبات دست‌ساز"],44,"Medium",fill=(255,226,190)),W/2,460)
    y=620
    for kind,txt in lines:
        if kind=="big": r=fx.text_rgba([txt],70,"Black",box=(165,78,22,235),pad=50)
        elif kind=="mid": r=fx.text_rgba([txt],52,"ExtraBold")
        else: r=fx.text_rgba([txt],40,"Medium",fill=(255,236,210))
        put(im,r,W/2,y+r.height/2); y+=r.height-10
    put(im,fx.handle_rgba(48),W/2,H-170)
    return im
def cubes_panel(w,h):
    """illustration of plain white sugar cubes"""
    im=Image.new("RGB",(w,h),(236,232,226)); d=ImageDraw.Draw(im)
    for k,(cx,cy) in enumerate([(w*0.33,h*0.58),(w*0.55,h*0.52),(w*0.72,h*0.62),(w*0.45,h*0.70)]):
        s=h*0.17
        top=[(cx,cy-s),(cx+s*0.87,cy-s*0.5),(cx,cy),(cx-s*0.87,cy-s*0.5)]
        left=[(cx-s*0.87,cy-s*0.5),(cx,cy),(cx,cy+s),(cx-s*0.87,cy+s*0.5)]
        right=[(cx,cy),(cx+s*0.87,cy-s*0.5),(cx+s*0.87,cy+s*0.5),(cx,cy+s)]
        d.polygon(top,fill=(252,252,250)); d.polygon(left,fill=(222,220,216)); d.polygon(right,fill=(205,203,199))
    return im
def compare_slide(path,left_txt,right_txt,topic,focus=(0.5,0.5)):
    im=Image.new("RGB",(W,H)); ph=H//2
    top=cubes_panel(W,ph); bot=to_img(sunlit(cover(path,focus,1.0,(W,H-ph)),"tr"))
    im.paste(top,(0,0)); im.paste(bot,(0,ph))
    a=np.asarray(im,np.float32)/255
    # darken bottom for text
    y=np.linspace(0,1,H)[:,None,None]; g=np.clip((y-0.6)/0.3,0,1)**1.2*0.85
    a=a*(1-g)+np.array([0.13,0.06,0.02],np.float32)*g; im=to_img(a)
    put(im,fx.text_rgba([topic],60,"Black",fill=(255,255,255),box=(150,70,20,230),pad=40),W/2,ph)
    put(im,fx.text_rgba(["قند معمولی"],40,"Bold",fill=(90,80,70),shadow=False),W/2,110)
    put(im,fx.text_rgba(left_txt.split("\n"),52,"ExtraBold",fill=(70,60,50),shadow=False),W/2,210)
    put(im,fx.text_rgba(["قند نباته"],40,"Bold",fill=(255,226,180)),W/2,H-300)
    put(im,fx.text_rgba(right_txt.split("\n"),56,"Black"),W/2,H-200)
    return im
def dm_bubble(im,words,y):
    d=ImageDraw.Draw(im)
    r=fx.text_rgba([words],64,"Black",fill=(255,255,255),shadow=False,box=(120,70,200,235),pad=44)
    put(im,r,W*0.62,y)
    return im

C={}
C[1]=[lambda: photo_slide("30.jpg","۵ نشانه که قندت\nارزش هدیه دادن داره","قبل از خرید هدیه، این ۵ تا رو چک کن",label="هدیه‌ی خاص",focus=(0.6,0.5)),
      lambda: photo_slide("5.jpg","ظاهر خاص و گلی","یه نگاه کافیه تا معلوم شه\nمعمولی نیست",label="نشانه‌ی ۱"),
      lambda: photo_slide("32.jpg","رنگ گیاهی،\nنه جیغ مصنوعی","رنگ‌های ملایم زعفرونی، گل‌محمدی و دارچینی\nبه‌جای رنگ‌های تند و براق",label="نشانه‌ی ۲",zoom=1.1),
      lambda: photo_slide("14.jpg","مناسب سینی پذیرایی","کنار چای و قهوه، خودش یه دکوره",label="نشانه‌ی ۳",focus=(0.5,0.6)),
      lambda: photo_slide("4.jpg","حس دست‌ساز و باحوصله","تک‌تک قالب‌ها با دست\nو با حوصله آماده می‌شن",label="نشانه‌ی ۴"),
      lambda: photo_slide("15.jpg","باکس آماده‌ی\nتعارف و هدیه","روبان، چیدمان، آماده‌ی دادن",label="نشانه‌ی ۵",focus=(0.6,0.5)),
      lambda: photo_slide("2.jpg","همه‌ش توی\nنباته جمع شده","ظاهر گلی · رنگ ملایم · دست‌ساز · باکس هدیه",label="جمع‌بندی",corner="tl"),
      lambda: cta_slide("IMG_6357.png",[("mid","این پست رو سیو کن"),("big","«سفارش» رو دایرکت بفرست"),("small","جزئیات و قیمت در دایرکت · ارسال به سراسر ایران")])]
C[2]=[lambda: photo_slide("33.jpg","یلدا نزدیکه\nچک‌لیست شیرینی سفره","سیو کن که شب یلدا چیزی جا نمونه",label="شب یلدا",focus=(0.5,0.45)),
      lambda: photo_slide("11.jpg","آجیل و انار\nسر جاشه؟","آجیل، انار، هندونه… تیک!\nحالا نوبت چیدمان چای و شیرینیه",label="قدم ۱"),
      lambda: photo_slide("13.jpg","یه پذیرایی چشم‌گیر\nچی کم داره؟","یه چیزی که کنار چای\nهمه رو بپرسونه «این چیه؟»",label="قدم ۲",focus=(0.5,0.4)),
      lambda: photo_slide("15.jpg","جواب:\nباکس قند و نبات خاص","هم شیرینی چای، هم دکور سفره",label="قدم ۳",focus=(0.6,0.5)),
      lambda: photo_slide("22.jpg","ایده‌ی چیدمان\nروی سفره","یه بشقاب قند فانتزی وسط سفره\nکنار استکان‌های چای و انار",label="ایده",focus=(0.35,0.5),zoom=1.05),
      lambda: photo_slide("19.jpg","گیفت تک‌نفره\nبرای مهمون","یه لالی‌پاپ یا چندتا قند گلی\nکنار بشقاب هر مهمون",label="ایده",focus=(0.5,0.3)),
      lambda: photo_slide("IMG_6349.png","پیش‌فروش\nباکس یلدایی نباته","قبل از شلوغی شب یلدا رزرو کن",label="پیش‌فروش"),
      lambda: cta_slide("IMG_6024.png",[("big","«یلدا» رو دایرکت کن"),("mid","ارسال به سراسر ایران"),("small","جزئیات و قیمت در دایرکت")])]
C[3]=[lambda: photo_slide("3.jpg","قند معمولی\nیا قند نباته؟","یه مقایسه‌ی ساده برای مهمونی بعدی",label="مقایسه",focus=(0.5,0.5)),
      lambda: compare_slide("10.jpg","مکعب ساده","فرم گلی و فانتزی","ظاهر",focus=(0.5,0.62)),
      lambda: compare_slide("15.jpg","مصرف روزمره","سورپرایز مهمون","حس هدیه",focus=(0.6,0.55)),
      lambda: compare_slide("32.jpg","سفید و ساده","طیف رنگی گیاهی\n(زعفران · گل‌محمدی · دارچین)","رنگ"),
      lambda: compare_slide("14.jpg","فقط شیرین کردن","پذیرایی + گیفت + عکس قشنگ","کاربرد",focus=(0.5,0.62)),
      lambda: photo_slide("1.jpg","کدومش برای\nمهمونی بهتره؟","جوابتو کامنت کن",focus=(0.4,0.75),corner="tl"),
      lambda: cta_slide("IMG_6355.png",[("mid","انتخابتو کامنت کن"),("big","برای سفارش دایرکت بده"),("small","جزئیات و قیمت در دایرکت · ارسال به سراسر ایران")])]
def c4_s2():
    im=photo_slide("30.jpg","دایرکت بده","فقط یه کلمه بفرست:\n«سفارش» یا «یلدا»",label="قدم ۱",focus=(0.6,0.5))
    return dm_bubble(im,"سلام، «یلدا»",360)
C[4]=[lambda: photo_slide("28.jpg","سفارش از نباته\nفقط ۴ قدم داره","از دایرکت تا دم در",label="راهنمای سفارش",focus=(0.4,0.5)),
      c4_s2,
      lambda: photo_slide("13.jpg","بگو برای چند نفره","هدیه‌ست یا پذیرایی؟\nمراسم یلدا، بله‌برون، یا سازمانی؟",label="قدم ۲",focus=(0.5,0.4)),
      lambda: photo_slide("15.jpg","پک پیشنهادی\nبرات چیده می‌شه","متناسب با تعداد و مناسبتت",label="قدم ۳",focus=(0.6,0.5)),
      lambda: photo_slide("IMG_6357.png","ارسال به شهرت","ارسال به سراسر ایران\nجزئیات و قیمت در دایرکت",label="قدم ۴"),
      lambda: photo_slide("21.jpg","سؤال پرتکرار؟\nهمین‌جا بپرس","بسته‌بندی، زمان ارسال، سفارش سازمانی…\nزیر همین پست کامنت کن",label="سؤال و جواب",focus=(0.5,0.6)),
      lambda: cta_slide("IMG_6070.png",[("big","«سفارش» یا «یلدا» رو دایرکت کن"),("mid","ارسال به سراسر ایران"),("small","جزئیات و قیمت در دایرکت")])]
if __name__=="__main__":
    out=sys.argv[1]
    for k in ([int(sys.argv[2])] if len(sys.argv)>2 else C):
        d=f"{out}/carousel-{k:02d}"; os.makedirs(d,exist_ok=True); n=len(C[k])
        for i,f in enumerate(C[k],1):
            im=f(); chrome(im,i,n); im.save(f"{d}/slide-{i:02d}.png",optimize=True); print(d,i)
