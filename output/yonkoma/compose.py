import numpy as np
from PIL import Image
tone=np.asarray(Image.open('tone.png').convert('L')).astype(np.float32)/255
ink=np.asarray(Image.open('ink.png').convert('L')).astype(np.float32)/255
h,w=tone.shape
# 45度網点スクリーントーン（周期 12px @2x ≒ 実寸 6px）
yy,xx=np.mgrid[0:h,0:w].astype(np.float32); P=12.0
u=(xx+yy)/np.sqrt(2); v=(xx-yy)/np.sqrt(2)
thr=0.5+0.25*(np.cos(2*np.pi*u/P)+np.cos(2*np.pi*v/P))   # 0..1
dark=1-tone
dots=np.where(dark>thr+0.0001,0.0,1.0)
dots[tone>0.98]=1.0
out=np.minimum(dots,ink)
img=Image.fromarray((out*255).astype(np.uint8))
# 枠線と余白
W,H=img.size; m=0
page=Image.new('L',(W+2*m,H+2*m),255); page.paste(img,(m,m))
from PIL import ImageDraw
d=ImageDraw.Draw(page); 
page.save('yonkoma.png')
