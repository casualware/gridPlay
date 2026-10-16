"""Illustrated quick guide, based on GridPlay.ino 0.9.4; not hardware captures."""
from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
import math
OUT=Path(__file__).resolve().parents[2]/'docs/images';OUT.mkdir(parents=True,exist_ok=True)
FONT='/System/Library/Fonts/Supplemental/Arial.ttf'
def font(n):return ImageFont.truetype(FONT,n)
bg='#101A23';fg='#F4FAFC';muted='#B8CAD7';accent='#67E3CE'
def text(x,y,t,n=20,c=fg,center=False):
 d.text((x,y),t,font=font(n),fill=c,anchor='mt' if center else 'lt')
def button(t,x,y,w,h,highlight=False):
 d.rounded_rectangle((x,y,x+w,y+h),12,fill='#243642',outline=accent if highlight else None,width=3)
 d.text((x+w/2,y+h/2),t,font=font(20),fill=fg,anchor='mm')
def base():
 global im,d
 im=Image.new('RGB',(480,480),bg);d=ImageDraw.Draw(im)
 text(16,22,'gridPlay',24)
 button('Home',160,16,78,42);button('Inst',246,16,78,42);button('Settings',332,16,132,42)
 text(22,65,'Wi-Fi connected',16);text(400,65,'82%',16,accent)
 d.rounded_rectangle((374,67,393,78),2,outline=accent,width=2)
 d.rectangle((377,70,389,75),fill=accent)
def save(name):im.save(OUT/(name+'.png'));return im.copy()
shots=[]
base();text(22,104,'Connect your tile',28)
button('Join',22,158,208,72);button('Create',250,158,208,72)
button('Return to inst / QR',22,248,436,64);button('Recent insts',22,330,208,64);button('GPT Live',250,330,208,64,True)
shots.append(('1  Start here','Choose GPT Live for standalone use.',save('home')))
base();text(22,92,'Join setup Wi-Fi',24);text(22,126,'gridPlay-EXAMPLE',20)
button('Wi-Fi setup',128,148,224,224,True);text(22,376,'Tap to start a new 10-minute setup session.',16)
button('Device details',22,402,208,72);button('API key',250,402,208,72,True)
shots.append(('2  Set up Wi-Fi and your key','Settings opens these large setup controls.',save('settings')))
base();text(22,100,'Set API key',28)
d.rectangle((22,142,230,350),fill='white')
for x,y in [(38,158),(162,158),(38,282)]:
 d.rectangle((x,y,x+50,y+50),fill='#17232D');d.rectangle((x+8,y+8,x+42,y+42),fill='white');d.rectangle((x+16,y+16,x+34,y+34),fill='#17232D')
text(126,230,'Setup QR',22,'#17232D',True);text(126,258,'Illustration only',15,'#17232D',True)
text(250,150,'Access code');text(250,186,'[tile code]',20)
for y,t in [(230,'Scan on your phone.'),(251,'Use the same Wi-Fi,'),(272,'then enter the code.'),(293,'Expires in 10 minutes.')]:text(250,y,t,16)
text(22,364,'http://<tile IP>/api-key',16,accent)
button('Open again',22,396,208,72);button('Close',250,396,208,72)
shots.append(('3  Enter your API key','Scan the setup QR, then enter the tile’s code.',save('api-key')))
base();text(22,92,'GPT Live',24);button('Audio test',312,92,156,44)
for i in range(64):
 y=1-2*(i+.5)/64;r=math.sqrt(1-y*y);a=i*2.399963;depth=(math.sin(a)*r+1)/2;size=3+depth*4
 x=236+math.cos(a)*r*62;yy=92+132+y*62*.87
 d.ellipse((x,yy,x+size,yy+size),fill='#34D399')
for t,x,y in [('New inst',12,144),('Reconnect',12,226),('Setup',12,308),('Inst',332,144),('Mute',332,226),('Stop',332,308)]:button(t,x,y,136,72,t in ['New inst','Reconnect','Inst'])
text(240,317,'Listening',20,center=True);text(240,392,'example-indigo-otter',16,center=True)
text(22,424,'New inst starts fresh. Reconnect opens your last inst.',16)
shots.append(('4  Talk with Phantom','Wait for Listening, then speak.',save('gpt-live')))
base();text(240,92,'example-indigo-otter',20,center=True)
d.rectangle((112,124,368,380),fill='white')
# Deliberately no scannable code: no real inst or pairing credential is published.
for x,y in [(136,148),(292,148),(136,304)]:
 d.rectangle((x,y,x+52,y+52),fill='#17232D');d.rectangle((x+8,y+8,x+44,y+44),fill='white');d.rectangle((x+16,y+16,x+36,y+36),fill='#17232D')
d.rectangle((135,222,345,293),fill='white');text(240,235,'Your inst QR',24,'#17232D',True);text(240,265,'Not a scannable code',16,'#17232D',True)
button('Back to GPT Live',22,384,436,48,True);text(22,442,'Scan to open. Your conversation stays on.',16)
shots.append(('5  Open your scene','Scan the real QR on your tile; keep the browser open.',save('inst')))
base();text(22,100,'Firmware updates',28);text(22,142,'Installed: 0.9.4-preview / preview',16)
text(22,183,'Check for signed firmware updates',16);text(22,205,'over Wi-Fi.',16)
button('Check again',22,384,208,72,True);button('Install update',250,384,208,72)
shots.append(('6  Keep your tile updated','Settings → Device details → Updates.',save('updates')))
canvas=Image.new('RGB',(1080,1900),'#F2F5F7');dd=ImageDraw.Draw(canvas)
dd.text((36,24),'gridPlay visual quick guide',font=font(36),fill='#101A23')
dd.text((36,72),'Illustrations of firmware 0.9.4-preview • Example readings, not device screenshots',font=font(18),fill='#435965')
for i,(title,caption,shot) in enumerate(shots):
 x=36+(i%2)*528;y=125+(i//2)*580
 dd.text((x,y),title,font=font(24),fill='#101A23');canvas.paste(shot,(x,y+40))
 dd.text((x,y+532),caption,font=font(16),fill='#435965')
canvas.save(OUT/'quick-guide.png')
