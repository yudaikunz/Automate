import math, random
random.seed(3)
W,H=800,1100; cx,cy=400,540
# 集中線
fl=[]
for i in range(170):
    a=random.uniform(0,2*math.pi); R=1000; r=random.uniform(330,450)
    w=random.uniform(0.006,0.022)
    x1,y1=cx+R*math.cos(a-w),cy+R*math.sin(a-w); x2,y2=cx+R*math.cos(a+w),cy+R*math.sin(a+w)
    x3,y3=cx+r*math.cos(a),cy+r*math.sin(a)
    fl.append(f'<path d="M{x1:.1f} {y1:.1f} L{x2:.1f} {y2:.1f} L{x3:.1f} {y3:.1f}Z"/>')
focus="\n".join(fl)
head="M 232 470 C 225 380, 300 330, 400 330 C 500 330, 575 380, 568 470 L 602 515 L 574 532 L 598 568 L 560 584 C 530 650, 470 682, 400 682 C 330 682, 270 650, 240 584 L 202 568 L 226 532 L 198 515 Z"
body="M 272 640 C 220 750, 185 900, 165 1120 L 635 1120 C 615 900, 580 750, 528 640 Z"
chest="M 330 660 L 345 700 L 365 680 L 380 720 L 400 695 L 420 722 L 435 682 L 455 702 L 470 662 C 500 760, 500 900, 470 1120 L 330 1120 C 300 900, 300 760, 330 660 Z"
muzzle="M 330 560 C 330 530, 365 520, 400 535 C 435 520, 470 530, 470 560 C 475 610, 440 640, 400 640 C 360 640, 325 610, 330 560 Z"
earL="M 262 420 L 248 245 L 352 345 Z"; earR="M 538 420 L 552 245 L 448 345 Z"
earLi="M 272 395 L 262 285 L 330 350 Z"; earRi="M 528 395 L 538 285 L 470 350 Z"
def eye(x):
    return f'''<ellipse cx="{x}" cy="505" rx="50" ry="58" fill="url(#iris)"/>'''
svg=f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<defs><linearGradient id="iris" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3c3c3c"/><stop offset="1" stop-color="#c8c8c8"/></linearGradient></defs>
<style>.ink path,.ink ellipse,.ink circle{{}} body{{margin:0}}</style>
<g id="tone">
  <rect width="{W}" height="{H}" fill="#fff"/>
  <path d="{body}" fill="#b4b4b4"/>
  <path d="{chest}" fill="#fff"/>
  <path d="M 300 660 C 340 700, 460 700, 500 660 L 520 700 C 460 740, 340 740, 280 700 Z" fill="#8c8c8c"/>
  <path d="{earL}" fill="#b4b4b4"/><path d="{earR}" fill="#b4b4b4"/>
  <path d="{earLi}" fill="#dcdcdc"/><path d="{earRi}" fill="#dcdcdc"/>
  <path d="{head}" fill="#b4b4b4"/>
  <path d="{muzzle}" fill="#fff"/>
  <g fill="#6e6e6e">
    <path d="M 392 335 L 408 335 L 404 410 L 396 410 Z"/>
    <path d="M 352 345 L 368 340 L 376 400 L 368 402 Z"/><path d="M 448 345 L 432 340 L 424 400 L 432 402 Z"/>
    <path d="M 205 515 L 260 505 L 262 515 L 225 530 Z"/><path d="M 595 515 L 540 505 L 538 515 L 575 530 Z"/>
    <path d="M 215 560 L 262 545 L 264 555 L 232 572 Z"/><path d="M 585 560 L 538 545 L 536 555 L 568 572 Z"/>
    <path d="M 210 760 C 240 770, 260 790, 262 820 L 250 820 C 245 795, 230 780, 205 775 Z"/>
    <path d="M 590 760 C 560 770, 540 790, 538 820 L 550 820 C 555 795, 570 780, 595 775 Z"/>
    <path d="M 195 860 C 230 870, 250 890, 252 930 L 240 930 C 235 900, 220 885, 192 878 Z"/>
    <path d="M 605 860 C 570 870, 550 890, 548 930 L 560 930 C 565 900, 580 885, 608 878 Z"/>
  </g>
  {eye(328)}{eye(472)}
</g>
<g id="ink" class="ink">
  <rect width="{W}" height="{H}" fill="#fff"/>
  <g fill="#000">{focus}</g>
  <g stroke="#000" stroke-linejoin="round" stroke-linecap="round" fill="#fff">
    <path d="{body}" stroke-width="5"/>
    <path d="{earL}" stroke-width="6"/><path d="{earR}" stroke-width="6"/>
    <path d="{head}" stroke-width="6"/>
  </g>
  <g stroke="#000" fill="none" stroke-linecap="round" stroke-width="2.5">
    <!-- 耳の毛 -->
    <path d="M 275 395 L 290 370 M 285 400 L 302 378 M 525 395 L 510 370 M 515 400 L 498 378"/>
    <!-- 胸毛 -->
    <path d="M 345 700 L 352 730 M 380 720 L 384 750 M 420 722 L 416 752 M 455 702 L 448 732 M 360 790 L 368 815 M 440 790 L 432 815 M 400 840 L 400 870"/>
    <!-- 口元 -->
    <path d="M 400 588 L 400 602 M 368 600 Q 384 622 400 602 Q 416 622 432 600" stroke-width="3.5"/>
    <!-- ひげ -->
    <path d="M 330 590 Q 260 575 175 585 M 332 602 Q 260 605 180 625 M 336 614 Q 270 630 200 662"/>
    <path d="M 470 590 Q 540 575 625 585 M 468 602 Q 540 605 620 625 M 464 614 Q 530 630 600 662"/>
    <!-- 頬の斜線(照れ) -->
    <path d="M 268 595 L 280 575 M 282 597 L 294 577 M 296 599 L 308 579 M 532 595 L 520 575 M 518 597 L 506 577 M 504 599 L 492 579" stroke-width="2.2"/>
  </g>
  <!-- 鼻 -->
  <path d="M 388 578 L 412 578 L 400 590 Z" fill="#000"/>
  <!-- 目 -->
  <g>
    <ellipse cx="328" cy="505" rx="50" ry="58" fill="none" stroke="#000" stroke-width="4"/>
    <ellipse cx="472" cy="505" rx="50" ry="58" fill="none" stroke="#000" stroke-width="4"/>
    <path d="M 272 492 Q 290 440 340 444 Q 372 448 384 478 Q 360 455 330 455 Q 295 456 272 492 Z" fill="#000"/>
    <path d="M 528 492 Q 510 440 460 444 Q 428 448 416 478 Q 440 455 470 455 Q 505 456 528 492 Z" fill="#000"/>
    <ellipse cx="330" cy="510" rx="20" ry="36" fill="#000"/><ellipse cx="470" cy="510" rx="20" ry="36" fill="#000"/>
    <circle cx="312" cy="484" r="15" fill="#fff"/><circle cx="452" cy="484" r="15" fill="#fff"/>
    <circle cx="345" cy="535" r="7" fill="#fff"/><circle cx="485" cy="535" r="7" fill="#fff"/>
    <circle cx="300" cy="530" r="3.5" fill="#fff"/><circle cx="440" cy="530" r="3.5" fill="#fff"/>
  </g>
  <!-- 吹き出し -->
  <path d="M 222 296 L 250 338 L 245 288 Z" fill="#fff" stroke="#000" stroke-width="4" stroke-linejoin="round"/>
  <ellipse cx="165" cy="185" rx="95" ry="140" fill="#fff" stroke="#000" stroke-width="4"/>
  <path d="M 228 296 L 248 292" stroke="#fff" stroke-width="8"/>
  <foreignObject x="85" y="70" width="160" height="240">
    <div xmlns="http://www.w3.org/1999/xhtml" style="writing-mode:vertical-rl;font-family:'IPAGothic';font-weight:bold;font-size:44px;line-height:1.25;height:240px;display:flex;justify-content:center;width:160px;">…なに<br/>見てんの？</div>
  </foreignObject>
  <!-- 描き文字 -->
  <foreignObject x="610" y="120" width="180" height="520" transform="rotate(6 700 380)">
    <div xmlns="http://www.w3.org/1999/xhtml" style="writing-mode:vertical-rl;font-family:'IPAGothic';font-weight:900;font-size:120px;letter-spacing:-6px;-webkit-text-stroke:22px #fff;paint-order:stroke fill;color:#000;">じーっ</div>
  </foreignObject>
  <foreignObject x="610" y="120" width="180" height="520" transform="rotate(6 700 380)">
    <div xmlns="http://www.w3.org/1999/xhtml" style="writing-mode:vertical-rl;font-family:'IPAGothic';font-weight:900;font-size:120px;letter-spacing:-6px;-webkit-text-stroke:6px #000;color:#000;">じーっ</div>
  </foreignObject>
</g>
</svg>'''
open('manga.svg','w').write(svg)
