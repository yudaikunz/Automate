import math
W,PW,PH,TOP,GAP=900,820,560,120,26
H=TOP+4*PH+3*GAP+40
FONT="'IPAPGothic','IPAGothic'"
class L:
    def __init__(s): s.t=[]; s.i=[]
    def both(s,t,i): s.t.append(t); s.i.append(i)
    def open(s,attr): s.both(f'<g {attr}>',f'<g {attr}>')
    def close(s): s.both('</g>','</g>')
    def shape(s,el,tone='#fff',sw=3.5,ink='#fff'):
        s.t.append(el.replace('/>',f' fill="{tone}"/>'))
        s.i.append(el.replace('/>',f' fill="{ink}" stroke="#000" stroke-width="{sw}" stroke-linejoin="round"/>') if sw else el.replace('/>',f' fill="{ink}"/>'))
    def tone(s,el,tone): s.t.append(el.replace('/>',f' fill="{tone}"/>'))
    def ink(s,el): s.i.append(el)
    def line(s,d,w=3): s.i.append(f'<path d="{d}" fill="none" stroke="#000" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"/>')
P=lambda d:f'<path d="{d}"/>'
def star(cx,cy,r):
    pts=[]
    for k in range(8):
        a=k*math.pi/4; rr=r if k%2==0 else r*0.28
        pts.append(f'{cx+rr*math.sin(a):.1f} {cy-rr*math.cos(a):.1f}')
    return 'M'+' L'.join(pts)+'Z'
# ---------------- 女の子 ----------------
HAIR='#7a7a7a'
def girl(l,x,y,s,eyes='open',mouth='smile',arm=None,blush=True,fx=None):
    l.open(f'transform="translate({x} {y}) scale({s})"')
    # 後ろ髪
    l.shape(P("M -122 -20 C -135 -150, 135 -150, 122 -20 L 128 95 C 110 118, 85 108, 75 90 L -75 90 C -85 108, -110 118, -128 95 Z"),HAIR)
    # 体(セーラー服)
    l.shape(P("M -150 420 C -150 200, -95 125, 0 120 C 95 125, 150 200, 150 420 Z"))
    l.shape(P("M -22 70 L 22 70 L 24 128 L -24 128 Z"))
    l.shape(P("M -78 128 L 0 205 L 78 128 L 112 150 L 0 250 L -112 150 Z"),'#8c8c8c')
    l.line("M -95 142 L 0 232 L 95 142",2)
    l.shape(P("M 0 205 L -38 185 L -42 228 Z"),'#3c3c3c'); l.shape(P("M 0 205 L 38 185 L 42 228 Z"),'#3c3c3c')
    l.shape(P("M -12 222 L -30 290 L -8 280 L 0 300 L 8 280 L 30 290 L 12 222 Z"),'#3c3c3c')
    l.shape('<circle cx="0" cy="210" r="11"/>','#3c3c3c')
    if arm=='fist':
        l.shape(P("M 95 175 C 130 150, 150 120, 150 75 L 115 70 C 115 110, 100 130, 72 145 Z"))
        l.shape(P("M 108 75 C 100 40, 125 25, 145 30 C 170 35, 172 70, 155 82 C 140 90, 115 90, 108 75 Z"))
        l.line("M 125 48 Q 140 46 152 52 M 122 62 Q 138 60 152 66",2)
    if arm=='teaser':
        l.shape(P("M 95 170 C 140 150, 180 120, 200 105 L 185 80 C 160 95, 120 120, 80 140 Z"))
        l.shape('<ellipse cx="198" cy="92" rx="22" ry="18"/>')
        l.line("M 205 85 C 240 20, 255 -60, 270 -90",4)
        for a in range(-60,61,20):
            r=math.radians(a-80); l.line(f"M 270 -90 l {40*math.cos(r):.1f} {40*math.sin(r)-0:.1f}",2.5)
    # 顔
    l.shape(P("M -90 -30 C -92 40, -40 98, 0 102 C 40 98, 92 40, 90 -30 C 86 -100, -86 -100, -90 -30 Z"))
    # 横髪
    l.shape(P("M -92 -40 C -110 30, -105 80, -88 112 L -80 70 L -70 95 C -78 40, -76 0, -70 -30 Z"),HAIR)
    l.shape(P("M 92 -40 C 110 30, 105 80, 88 112 L 80 70 L 70 95 C 78 40, 76 0, 70 -30 Z"),HAIR)
    # 前髪
    l.shape(P("M -100 -5 C -110 -150, 110 -150, 100 -5 L 88 -22 Q 82 -10 76 4 Q 68 -18 56 -34 Q 50 -14 40 0 Q 30 -20 18 -40 Q 10 -18 0 -2 Q -10 -20 -20 -38 Q -30 -16 -40 0 Q -48 -14 -56 -32 Q -64 -10 -74 4 Q -80 -8 -88 -22 Z"),HAIR)
    l.line("M -40 -60 Q -45 -30 -40 0 M 18 -70 Q 20 -50 18 -40 M 56 -64 Q 58 -48 56 -34",1.8)
    l.tone(P("M -66 -82 Q 0 -104 66 -82 L 58 -72 L 46 -84 L 34 -70 L 20 -86 L 6 -72 L -8 -88 L -22 -72 L -36 -86 L -50 -70 L -60 -80 Z"),'#fff')
    # 目
    for sx in (-1,1):
        ex,ey=sx*40,24
        if eyes in('open','sparkle'):
            l.shape(f'<ellipse cx="{ex}" cy="{ey}" rx="25" ry="31"/>','#fff',1.5)
            l.tone(f'<ellipse cx="{ex}" cy="{ey+3}" rx="21" ry="27"/>','url(#iris)')
            l.ink(f'<ellipse cx="{ex}" cy="{ey+3}" rx="21" ry="27" fill="none" stroke="#000" stroke-width="1.5"/>')
            l.ink(f'<ellipse cx="{ex}" cy="{ey+5}" rx="9" ry="13" fill="#000"/>')
            l.ink(f'<path d="M {ex-sx*24} {ey-12} Q {ex-sx*6} {ey-36} {ex+sx*26} {ey-14} L {ex+sx*30} {ey-6}" fill="none" stroke="#000" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/>')
            l.line(f"M {ex+sx*26} {ey-14} L {ex+sx*36} {ey-14}",3)
            l.line(f"M {ex-10} {ey+34} Q {ex} {ey+36} {ex+10} {ey+34}",1.8)
            if eyes=='sparkle':
                l.ink(f'<path d="{star(ex-6,ey-6,13)}" fill="#fff"/>')
                l.ink(f'<path d="{star(ex+8,ey+15,6)}" fill="#fff"/>')
            else:
                l.ink(f'<circle cx="{ex-7}" cy="{ey-6}" r="7" fill="#fff"/><circle cx="{ex+7}" cy="{ey+14}" r="3.5" fill="#fff"/>')
        elif eyes=='closed':
            l.line(f"M {ex-22} {ey+6} Q {ex} {ey-20} {ex+22} {ey+6}",5)
        elif eyes=='shock':
            l.shape(f'<ellipse cx="{ex}" cy="{ey}" rx="22" ry="27"/>','#fff',3)
            l.ink(f'<circle cx="{ex}" cy="{ey+2}" r="4" fill="#000"/>')
        elif eyes=='flat':
            l.line(f"M {ex-20} {ey+4} L {ex+20} {ey+4}",5)
            l.line(f"M {ex-16} {ey-8} Q {ex} {ey-14} {ex+16} {ey-8}",2)
    # リボン
    l.shape(P("M 78 -78 L 50 -112 L 40 -80 Z"),'#3c3c3c'); l.shape(P("M 78 -78 L 112 -100 L 108 -62 Z"),'#3c3c3c')
    l.shape('<circle cx="78" cy="-80" r="9"/>','#3c3c3c')
    # 頬
    if blush:
        for sx in(-1,1):
            l.line(" ".join(f"M {sx*55+k*9-10} {58} L {sx*55+k*9-4} {46}" for k in range(3)),2)
    # 口
    if mouth=='smile': l.shape(P("M -12 68 Q 0 70 12 68 Q 10 86 0 86 Q -10 86 -12 68 Z"),'#a0a0a0',2.5)
    elif mouth=='small': l.line("M -8 72 Q 0 78 8 72",2.5)
    elif mouth=='shock': l.shape('<ellipse cx="0" cy="74" rx="7" ry="10"/>','#5a5a5a',2.5)
    elif mouth=='wavy': l.line("M -14 74 q 3.5 -5 7 0 q 3.5 5 7 0 q 3.5 -5 7 0 q 3.5 5 7 0",2.5)
    if fx=='gloom':
        for k in range(-5,6): l.line(f"M {k*12} {-100+abs(k)*4} L {k*12} {-40+abs(k)*3}",2)
    if fx in('gloom','sweat'):
        l.shape(P("M 118 -60 C 108 -40, 108 -20, 122 -18 C 136 -20, 134 -40, 118 -60 Z"),'#fff',2.5)
        l.shape(P("M 128 10 C 120 26, 120 40, 131 41 C 142 40, 140 26, 128 10 Z"),'#fff',2.5)
    l.close()
# ---------------- 猫(前作の顔を流用) ----------------
CT='#b4b4b4'
def cat(l,x,y,s,eyes='stare'):
    l.open(f'transform="translate({x} {y}) scale({s}) translate(-400 -505)"')
    l.shape(P("M 560 860 C 680 870, 690 760, 630 720"),'none',0)
    l.ink('<path d="M 560 860 C 680 870, 690 760, 630 720" fill="none" stroke="#000" stroke-width="44" stroke-linecap="round"/>')
    l.ink('<path d="M 560 860 C 680 870, 690 760, 630 720" fill="none" stroke="#fff" stroke-width="34" stroke-linecap="round"/>')
    l.tone('<path d="M 560 860 C 680 870, 690 760, 630 720" stroke="#b4b4b4" stroke-width="34" stroke-linecap="round"/>','none')
    l.shape('<ellipse cx="400" cy="790" rx="175" ry="160"/>',CT,7)
    l.shape('<ellipse cx="400" cy="800" rx="80" ry="125"/>','#fff',0)
    l.shape('<ellipse cx="340" cy="935" rx="48" ry="26"/>','#fff',6); l.shape('<ellipse cx="460" cy="935" rx="48" ry="26"/>','#fff',6)
    l.shape(P("M 262 420 L 248 245 L 352 345 Z"),CT,8); l.shape(P("M 538 420 L 552 245 L 448 345 Z"),CT,8)
    l.tone(P("M 272 395 L 262 285 L 330 350 Z"),'#dcdcdc'); l.tone(P("M 528 395 L 538 285 L 470 350 Z"),'#dcdcdc')
    l.shape(P("M 232 470 C 225 380, 300 330, 400 330 C 500 330, 575 380, 568 470 L 602 515 L 574 532 L 598 568 L 560 584 C 530 650, 470 682, 400 682 C 330 682, 270 650, 240 584 L 202 568 L 226 532 L 198 515 Z"),CT,8)
    l.tone(P("M 330 560 C 330 530, 365 520, 400 535 C 435 520, 470 530, 470 560 C 475 610, 440 640, 400 640 C 360 640, 325 610, 330 560 Z"),'#fff')
    for d in ["M 392 335 L 408 335 L 404 410 L 396 410 Z","M 352 345 L 368 340 L 376 400 L 368 402 Z","M 448 345 L 432 340 L 424 400 L 432 402 Z"]:
        l.tone(P(d),'#6e6e6e')
    for ex in(328,472):
        if eyes=='stare':
            l.tone(f'<ellipse cx="{ex}" cy="505" rx="50" ry="58"/>','url(#iris)')
            l.ink(f'<ellipse cx="{ex}" cy="505" rx="50" ry="58" fill="none" stroke="#000" stroke-width="7"/>')
            l.ink(f'<ellipse cx="{ex+2}" cy="510" rx="20" ry="36" fill="#000"/><circle cx="{ex-16}" cy="484" r="15" fill="#fff"/>')
        else:
            l.line(f"M {ex-45} 515 Q {ex} 470 {ex+45} 515",10)
    l.ink('<path d="M 386 578 L 414 578 L 400 592 Z" fill="#000"/>')
    l.line("M 400 590 L 400 602 M 366 600 Q 384 624 400 602 Q 416 624 434 600",6)
    l.line("M 330 595 Q 260 580 180 592 M 334 610 Q 260 615 190 640 M 470 595 Q 540 580 620 592 M 466 610 Q 540 615 610 640",4)
    l.close()
# ---------------- 箱 ----------------
def box_back(l,x,y,w):
    l.shape(P(f"M {x+20} {y-30} L {x+50} {y-95} L {x+w-50} {y-95} L {x+w-20} {y-30} Z"),'#c8c8c8',3.5)
    l.shape(P(f"M {x} {y} L {x+20} {y-30} L {x+w-20} {y-30} L {x+w} {y} Z"),'#505050',3.5)
def box_front(l,x,y,w,h):
    l.shape(P(f"M {x} {y} L {x+w} {y} L {x+w} {y+h} L {x} {y+h} Z"),'#c8c8c8',4.5)
    l.shape(P(f"M {x} {y} L {x-55} {y-40} L {x-30} {y-75} L {x+20} {y-30} Z"),'#dcdcdc',3.5)
    l.shape(P(f"M {x+w} {y} L {x+w+55} {y-40} L {x+w+30} {y-75} L {x+w-20} {y-30} Z"),'#dcdcdc',3.5)
    l.line(f"M {x+30} {y+50} L {x+70} {y+50} M {x+w-90} {y+90} L {x+w-40} {y+90}",2)
# ---------------- 吹き出し・描き文字 ----------------
def bubble(l,cx,cy,rx,ry,text,tail,fs=34):
    a=math.atan2((tail[1]-cy)/ry,(tail[0]-cx)/rx)
    pt=lambda a,k=1:(cx+rx*k*math.cos(a),cy+ry*k*math.sin(a))
    p1,p2=pt(a-0.22),pt(a+0.22)
    l.ink(f'<path d="M {p1[0]:.1f} {p1[1]:.1f} L {tail[0]} {tail[1]} L {p2[0]:.1f} {p2[1]:.1f} Z" fill="#fff" stroke="#000" stroke-width="3.5" stroke-linejoin="round"/>')
    l.ink(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="#fff" stroke="#000" stroke-width="3.5"/>')
    q1,q2=pt(a-0.17,0.97),pt(a+0.17,0.97)
    l.ink(f'<path d="M {q1[0]:.1f} {q1[1]:.1f} L {tail[0]} {tail[1]} L {q2[0]:.1f} {q2[1]:.1f} Z" fill="#fff"/>')
    l.tone(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}"/>','#fff')
    l.ink(f'<foreignObject x="{cx-rx}" y="{cy-ry}" width="{2*rx}" height="{2*ry}"><div xmlns="http://www.w3.org/1999/xhtml" style="width:{2*rx}px;height:{2*ry}px;display:flex;align-items:center;justify-content:center;"><div style="writing-mode:vertical-rl;font-family:{FONT};font-weight:bold;font-size:{fs}px;line-height:1.3;">{text}</div></div></foreignObject>')
def sfx(l,x,y,text,fs,rot=0,vertical=False,w=400,h=400):
    wm='vertical-rl' if vertical else 'horizontal-tb'
    for st in(f'-webkit-text-stroke:{fs*0.2:.0f}px #fff;paint-order:stroke fill;',f'-webkit-text-stroke:{fs*0.05:.1f}px #000;'):
        l.ink(f'<foreignObject x="{x}" y="{y}" width="{w}" height="{h}" transform="rotate({rot} {x} {y})"><div xmlns="http://www.w3.org/1999/xhtml" style="writing-mode:{wm};font-family:{FONT};font-weight:900;font-size:{fs}px;letter-spacing:-2px;color:#000;{st}">{text}</div></foreignObject>')
# ---------------- ページ組み ----------------
l=L()
l.both(f'<rect width="{W}" height="{H}" fill="#fff"/>',f'<rect width="{W}" height="{H}" fill="#fff"/>')
l.ink(f'<text x="{W/2}" y="70" text-anchor="middle" font-family="IPAPGothic" font-weight="bold" font-size="46" letter-spacing="6">ねこと女の子</text>')
l.ink(f'<text x="{W/2}" y="104" text-anchor="middle" font-family="IPAPGothic" font-size="20" letter-spacing="3">第１話　ねこじゃらし作戦</text>')
defs=[]
for n in range(4):
    px,py=40,TOP+n*(PH+GAP)
    defs.append(f'<clipPath id="c{n}"><rect width="{PW}" height="{PH}"/></clipPath>')
    l.open(f'transform="translate({px} {py})"'); l.open(f'clip-path="url(#c{n})"')
    if n==0:
        l.tone(f'<rect width="{PW}" height="{PH}"/>','#ececec')
        for (sx,sy,r) in [(380,80,26),(430,170,14),(760,90,30),(790,230,16),(350,440,18),(780,440,22),(470,60,10)]:
            l.ink(f'<path d="{star(sx,sy,r)}" fill="#fff" stroke="#000" stroke-width="2"/>')
        girl(l,560,250,1.3,'sparkle','smile','fist')
        bubble(l,160,230,118,175,'今日こそ<br/>ねこちゃんと<br/>仲良くなる！',(395,250),33)
        sfx(l,715,350,'ぐっ',52,12)
    if n==1:
        l.line(f"M 0 470 L {PW} 470",2)
        cat(l,690,330,0.45,'stare')
        girl(l,250,270,1.2,'closed','smile','teaser')
        bubble(l,90,150,62,115,'ほらほら♪',(150,200),32)
        sfx(l,470,80,'ふりふり',40,-10)
        sfx(l,762,40,'じー…',44,0,True,80,300)
    if n==2:
        l.t.append(f'<rect width="430" height="{PH}" fill="url(#dark)"/>')
        box_back(l,545,400,240)
        cat(l,665,305,0.43,'content')
        box_front(l,545,400,240,200)
        girl(l,300,300,1.2,'shock','shock',None,False,'gloom')
        bubble(l,95,185,82,150,'えっ…<br/>箱の方が<br/>いいの…？',(170,330),31)
        sfx(l,500,30,'ガーン',72,-6,False,330,120)
        sfx(l,600,505,'ぬくぬく',28,0,False,150,50)
    if n==3:
        l.line(f"M 0 530 L {PW} 530",2)
        box_back(l,260,470,300)
        girl(l,410,362,1.05,'flat','wavy',None,True)
        cat(l,410,98,0.34,'content')
        box_front(l,260,470,300,200)
        bubble(l,120,280,80,145,'…これで<br/>仲良し？',(300,380),32)
        bubble(l,680,130,52,72,'にゃ',(485,100),34)
        sfx(l,620,330,'ぽふっ',34,8,False,200,60)
    l.close(); l.close()
    l.ink(f'<rect x="{px}" y="{py}" width="{PW}" height="{PH}" fill="none" stroke="#000" stroke-width="6"/>')
gdefs='''<linearGradient id="iris" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2a2a2a"/><stop offset="1" stop-color="#c8c8c8"/></linearGradient>
<linearGradient id="dark" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#555"/><stop offset="1" stop-color="#fff"/></linearGradient>'''
for name,body in(('tone',l.t),('ink',l.i)):
    open(name+'.svg','w').write(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}"><defs>{gdefs}{"".join(defs)}</defs>'+"\n".join(body)+'</svg>')
print(W,H)
