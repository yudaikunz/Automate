"""mangakit で描くデフォルメ女の子(バストアップ)。表情を切り替えて使い回せる。
python3 girl.py out.png  でデモ(表情4種)を出力。"""
import sys, os, math, numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from mangakit import Page, taper, contour, clump, LIGHT, _d

HAIR, HAIR_SH = '#c4c4c4', '#8e8e8e'      # 髪: ベース / 影(2段目)
SKIN_SH, SKIN_SH2 = '#e2e2e2', '#c8c8c8'   # 肌の影: 1段目 / 2段目

def _hair_clump(p, root, tip, width, bend, profile='leaf', edge=1.7):
    d, Lp, Rp, C = clump(root, tip, width, bend, profile=profile)
    p.fill(d, HAIR)
    # 影側(光源と反対側)の半分に影トーン
    mid = len(C)//2; nx, ny = Lp[mid] - C[mid]
    lit_left = (nx*LIGHT[0] + ny*LIGHT[1]) > 0
    side = Rp if lit_left else Lp
    k = int(len(C)*0.35)
    p.tone(_d(np.concatenate([side[k:], C[k:][::-1]])), HAIR_SH)
    # 輪郭: 根元側は消え入り、毛先はスッと抜く
    for E in (Lp, Rp):
        k0 = int(len(E)*0.15)
        p.line(E[k0:], edge, tin=0.35, tout=0.45)
    return d

def girl(p, x, y, s=1.0, rot=0, eyes='open', mouth='smile', blush=True, fx=None):
    p.open(f'transform="translate({x} {y}) rotate({rot}) scale({s})"')
    # ---- 後ろ髪(全体が影の中なので濃いトーン)
    back = "M -108 -10 C -124 -150, 124 -150, 108 -10 C 112 40, 118 80, 104 112 L -104 112 C -118 80, -112 40, -108 -10 Z"
    p.shape(back, HAIR_SH, 3.2)
    for r, t, w, b in [((-96, 0), (-122, 126), 40, 0.08), ((-80, 20), (-92, 132), 34, 0.04), ((96, 0), (124, 122), 40, -0.08), ((80, 20), (96, 132), 34, -0.04)]:
        d, Lp, Rp, C = clump(r, t, w, b, profile='hang'); p.fill(d, HAIR_SH)
        for E in (Lp, Rp): p.line(E[int(len(E)*.3):], 2.2, 0.3, 0.5)
    # ---- 首・体
    p.shape("M -21 60 L -23 132 L 23 132 L 21 60 Z", '#fff', 2.4)
    p.tone("M -23 74 Q 0 112 23 74 L 23 104 Q 0 120 -23 104 Z", SKIN_SH2)
    body = "M -150 420 L -142 230 C -136 172, -90 146, -22 130 L 22 130 C 90 146, 136 172, 142 230 L 150 420 Z"
    p.shape(body, '#fff', 3.2)
    p.tone_clip_open(body); p.tone("M 150 160 C 130 220, 120 320, 126 420 L 170 420 L 170 160 Z", SKIN_SH); p.tone_close()
    for sx in (-1, 1):
        p.line(f"M {sx*112} 170 C {sx*104} 230, {sx*106} 300, {sx*112} 420", 1.8, .3, .2)      # 腕の付け根
    p.line("M 44 300 Q 60 330 58 380", 1.4, .4, .5); p.line("M -40 310 Q -52 340 -50 372", 1.4, .4, .5)  # シワ
    p.shape("M -62 130 L 0 218 L 62 130 L 100 152 L 0 266 L -100 152 Z", '#a8a8a8', 3.0)
    p.tone(taper("M -86 156 L 0 250 L 86 156", 3.2, 0, 0, wobble=0), '#fff')
    p.tone("M 30 160 L 62 130 L 100 152 L 60 200 Z", '#7a7a7a')     # 襟の影側
    for sx in (-1, 1):
        p.shape(f"M 0 214 Q {sx*30} 192 {sx*44} 200 Q {sx*40} 222 {sx*44} 240 Q {sx*24} 236 0 222 Z", '#808080', 2.4)
        p.line(f"M {sx*8} 216 Q {sx*24} 210 {sx*34} 214", 1.4, .3, .5)
    p.shape("M -9 207 Q 0 202 9 207 L 9 226 Q 0 230 -9 226 Z", '#6a6a6a', 2.2)
    p.shape("M -9 226 L -26 300 L -6 290 L 0 306 L 6 290 L 26 300 L 9 226 Z", '#808080', 2.4)
    # ---- 顔
    face = "M -88 -25 C -90 32, -55 82, -8 100 Q 0 103 8 100 C 55 82, 90 32, 88 -25 C 85 -95, -85 -95, -88 -25 Z"
    p.shape(face, '#fff', 3.0, light_k=0.9)
    p.tone_clip_open(face)
    p.tone("M 88 -40 C 92 30, 56 82, 6 100 C 46 72, 72 34, 74 -40 Z", SKIN_SH)          # 影側の頬
    p.tone_close()
    if blush:
        for sx in (-1, 1):
            p.tone(f"M {sx*52-22} 70 Q {sx*52} 58 {sx*52+22} 70 Q {sx*52} 80 {sx*52-22} 70 Z", '#e8e8e8')
            for k in range(3):
                bx = sx*52 - 9 + k*9
                p.line(f"M {bx-3} 76 L {bx+4} 64", 1.4, .3, .5)
    # ---- 目
    for sx in (-1, 1):
        ex, ey = sx*42, 36
        if eyes in ('open', 'sparkle'):
            ed = (f"M {ex-sx*25} {ey-4} Q {ex-sx*8} {ey-31} {ex+sx*27} {ey-13} Q {ex+sx*26} {ey+20} {ex+sx*3} {ey+30} "
                  f"Q {ex-sx*22} {ey+26} {ex-sx*25} {ey-4} Z")
            p.fill(ed, '#fff')
            p.clip_open(ed)
            iris = f"M {ex+sx} {ey-22} C {ex+sx+27} {ey-22}, {ex+sx+27} {ey+32}, {ex+sx} {ey+32} C {ex+sx-27} {ey+32}, {ex+sx-27} {ey-22}, {ex+sx} {ey-22} Z"
            p.tone(iris, p.gradient([(0, '#222'), (0.55, '#6a6a6a'), (1, '#c4c4c4')]))
            p.ink(f'<path d="{contour(iris, 1.8, 0)}" fill="#000" fill-rule="evenodd"/>')
            p.black(f"M {ex+sx} {ey-6} C {ex+sx+11} {ey-6}, {ex+sx+11} {ey+20}, {ex+sx} {ey+20} C {ex+sx-11} {ey+20}, {ex+sx-11} {ey-6}, {ex+sx} {ey-6} Z")
            p.tone(taper(f"M {ex-12} {ey+22} Q {ex+sx} {ey+30} {ex+13} {ey+21}", 3, .4, .4), '#fff')
            if eyes == 'sparkle':
                p.sparkle(ex-7, ey-3, 12, 1.2); p.sparkle(ex+9, ey+16, 5, 1)
            else:   # ハイライトは光源(左上)側に、両目とも同じ向きで
                p.white(f"M {ex-14} {ey-4} C {ex-14} {ey-16}, {ex-2} {ey-16}, {ex-2} {ey-4} C {ex-2} {ey+6}, {ex-14} {ey+6}, {ex-14} {ey-4} Z")
                p.white(f"M {ex+6} {ey+15} C {ex+6} {ey+10}, {ex+12} {ey+10}, {ex+12} {ey+15} C {ex+12} {ey+20}, {ex+6} {ey+20}, {ex+6} {ey+15} Z")
            p.close()
            p.line(f"M {ex-sx*25} {ey-3} Q {ex-sx*8} {ey-32} {ex+sx*28} {ey-13}", 7.5, .12, .08)        # 上まつげ(主線)
            p.line(f"M {ex+sx*22} {ey-14} Q {ex+sx*31} {ey-14} {ex+sx*38} {ey-22}", 4.5, 0, .85)     # 目尻のハネ
            p.line(f"M {ex+sx*28} {ey-12} Q {ex+sx*29} {ey+2} {ex+sx*24} {ey+12}", 3.2, .05, .9)    # 目尻
            p.line(f"M {ex-sx*16} {ey-32} Q {ex+sx*3} {ey-42} {ex+sx*22} {ey-28}", 1.5, .4, .4)     # 二重
            p.line(f"M {ex-sx*4} {ey+31} Q {ex+sx*8} {ey+32} {ex+sx*18} {ey+25}", 1.7, .5, .5)      # 下まつげ
        elif eyes == 'closed':
            p.line(f"M {ex-sx*24} {ey+6} Q {ex+sx*2} {ey-16} {ex+sx*26} {ey+4}", 5, .2, .2)
            p.line(f"M {ex+sx*22} {ey+1} L {ex+sx*32} {ey-4}", 3, 0, .8)
        elif eyes == 'shock':
            e = f"M {ex} {ey-26} C {ex+30} {ey-26}, {ex+30} {ey+28}, {ex} {ey+28} C {ex-30} {ey+28}, {ex-30} {ey-26}, {ex} {ey-26} Z"
            p.shape(e, '#fff', 2.6, 0.3); p.black(f"M {ex-4} {ey+1} a 4 4 0 1 0 8 0 a 4 4 0 1 0 -8 0 Z")
        elif eyes == 'flat':
            p.line(f"M {ex-sx*22} {ey+4} Q {ex} {ey+2} {ex+sx*22} {ey+4}", 5, .15, .15)
            p.line(f"M {ex-sx*16} {ey-10} Q {ex} {ey-15} {ex+sx*18} {ey-9}", 1.5, .4, .4)
    # ---- 鼻・口
    p.line("M 7 64 Q 10 70 5 73", 2.0, .2, .6)
    if mouth == 'smile':
        md = "M -12 82 Q 0 84 12 82 Q 9 96 0 96 Q -9 96 -12 82 Z"
        p.fill(md, '#b0b0b0')
        p.line("M -13 81 Q 0 85 13 81", 2.2, .2, .2); p.line("M -11 83 Q -9 96 0 96 Q 9 96 11 83", 1.5, .3, .3)
    elif mouth == 'small': p.line("M -8 86 Q 0 91 8 86", 2.2, .3, .3)
    elif mouth == 'shock':
        p.shape("M 0 80 C 9 80, 9 96, 0 96 C -9 96, -9 80, 0 80 Z", '#7a7a7a', 2.0, 0.3)
    elif mouth == 'wavy': p.line("M -14 88 Q -10.5 83 -7 88 Q -3.5 93 0 88 Q 3.5 83 7 88 Q 10.5 93 14 88", 2.0, .15, .15)
    # ---- 前髪: 頭頂の面 → つむじ(分け目)から放射する毛束
    cap = "M -104 -18 C -114 -152, 114 -152, 104 -18 Q 0 -66 -104 -18 Z"
    p.shape(cap, HAIR, 3.2)
    part = (-24, -118)
    bangs = [  # (tip, width, bend)   外側から内側へ(内側が手前に重なる)
        ((-100, 14), 46, 0.10), ((100, 16), 46, -0.10), ((-74, -8), 40, 0.06), ((82, -10), 42, -0.08),
        ((58, 0), 40, -0.06), ((-48, 0), 40, 0.05), ((32, -10), 40, -0.04), ((-20, 6), 42, 0.02), ((6, -4), 36, -0.06)]
    hair_union = [cap]
    for tip, w, b in bangs:
        ang = math.atan2(tip[1]-part[1], tip[0]-part[0])
        root = (part[0] + 14*math.cos(ang), part[1] + 14*math.sin(ang))
        hair_union.append(_hair_clump(p, root, tip, w, b))
    # 横髪(顔の前に垂れる)
    for sx in (-1, 1):
        hair_union.append(_hair_clump(p, (sx*92, -50), (sx*86, 128), 34, -sx*0.06, 'hang'))
        hair_union.append(_hair_clump(p, (sx*80, -30), (sx*70, 96), 22, -sx*0.10, 'hang'))
    # 天使の輪(ハイライト): 毛の流れに沿った短い白の入り抜きを、弧に沿ってギザギザに並べる
    p.tone_clip_open(' '.join(hair_union))
    for k in range(-9, 10):
        a = math.radians(-90 + k*8.5)
        cx, cy = 0 + 92*math.cos(a), -40 + 50*math.sin(a) - 8
        ang = math.atan2(cy-part[1], cx-part[0])
        L = 16 + 10*((k*7) % 3)
        x0, y0 = cx - L/2*math.cos(ang), cy - L/2*math.sin(ang)
        x1, y1 = cx + L/2*math.cos(ang), cy + L/2*math.sin(ang)
        p.tone(taper(f"M {x0:.1f} {y0:.1f} L {x1:.1f} {y1:.1f}", 7 if k % 2 else 5, .5, .5, wobble=0), '#fff')
    p.tone_close()
    # 眉(前髪の上に細く透かして描く)
    if eyes != 'shock':
        for sx in (-1, 1):
            p.line(f"M {sx*24} -6 Q {sx*42} -14 {sx*62} -6", 1.8, .25, .6)
    # リボン
    for d in ("M 72 -92 Q 46 -128 38 -104 Q 40 -88 72 -92 Z", "M 72 -92 Q 106 -116 110 -88 Q 100 -72 72 -92 Z"):
        p.shape(d, '#808080', 2.4)
    p.line("M 70 -94 Q 54 -106 46 -104", 1.3, .3, .5); p.line("M 76 -92 Q 92 -98 102 -92", 1.3, .3, .5)
    p.shape("M 64 -96 Q 72 -102 80 -96 Q 80 -86 72 -86 Q 64 -86 64 -96 Z", '#6a6a6a', 2.0)
    if fx in ('gloom', 'sweat'):
        if fx == 'gloom':
            for k in range(-6, 7):
                p.line(f"M {k*11} -84 L {k*11} {-36 + abs(k)*-3}", 1.6, .1, .6)
        for (sx, sy, r) in ((122, -50, 14), (130, 14, 10)):
            dd = f"M {sx} {sy-r*1.8} C {sx-r} {sy-r*0.4}, {sx-r} {sy+r}, {sx} {sy+r} C {sx+r} {sy+r}, {sx+r} {sy-r*0.4}, {sx} {sy-r*1.8} Z"
            p.shape(dd, '#fff', 2.0, 0.3)
    p.close()

if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else 'girl_demo.png'
    p = Page(1200, 520)
    for i, (e, m, fx) in enumerate([('sparkle', 'smile', None), ('closed', 'smile', None), ('shock', 'shock', 'gloom'), ('flat', 'wavy', None)]):
        girl(p, 150 + i*300, 200, 0.95, rot=[-4, 3, 0, -2][i], eyes=e, mouth=m, fx=fx)
    p.save(out)
    print(out)
