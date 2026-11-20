"""mangakit — SVGで「素人っぽくない」白黒漫画を描くための小さなライブラリ。

二層構成:
  tone 層 … 灰色で塗る(後で網点スクリーントーンに変換される)。白=トーン無し。
  ink  層 … 墨(黒)と、下を隠すための白。線はすべて「入り抜き付きの塗り多角形」で描く。
最後に compose() で tone→網点化 し、ink と min 合成して1枚にする。
"""
import math, os, re, subprocess, random
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
LIGHT = (-0.6, -0.8)          # 光の進む向きの逆(=光源方向)。既定は左上。

# ------------------------------------------------------------ パス処理
def _num(s): return [float(v) for v in re.findall(r'-?\d*\.?\d+(?:e-?\d+)?', s)]

def sample_path(d, n_per_seg=24):
    """絶対座標の M/L/Q/C/Z だけの path を点列にする。"""
    toks = re.findall(r'[MLQCZ][^MLQCZ]*', d.strip())
    pts, cur, start = [], None, None
    for t in toks:
        c, v = t[0], _num(t[1:])
        if c == 'M':
            cur = start = (v[0], v[1]); pts.append(cur)
            v = v[2:]; c = 'L'
        if c == 'L':
            for i in range(0, len(v), 2):
                p = (v[i], v[i+1])
                for k in range(1, n_per_seg+1):
                    a = k / n_per_seg
                    pts.append((cur[0]+(p[0]-cur[0])*a, cur[1]+(p[1]-cur[1])*a))
                cur = p
        elif c == 'Q':
            for i in range(0, len(v), 4):
                c1, p = (v[i], v[i+1]), (v[i+2], v[i+3])
                for k in range(1, n_per_seg+1):
                    a = k / n_per_seg; b = 1 - a
                    pts.append((b*b*cur[0]+2*a*b*c1[0]+a*a*p[0], b*b*cur[1]+2*a*b*c1[1]+a*a*p[1]))
                cur = p
        elif c == 'C':
            for i in range(0, len(v), 6):
                c1, c2, p = (v[i], v[i+1]), (v[i+2], v[i+3]), (v[i+4], v[i+5])
                for k in range(1, n_per_seg+1):
                    a = k / n_per_seg; b = 1 - a
                    pts.append((b**3*cur[0]+3*a*b*b*c1[0]+3*a*a*b*c2[0]+a**3*p[0],
                                b**3*cur[1]+3*a*b*b*c1[1]+3*a*a*b*c2[1]+a**3*p[1]))
                cur = p
        elif c == 'Z' and start and cur != start:
            pts.append(start); cur = start
    return resample(pts)

def resample(pts, step=1.5):
    P = np.array(pts, float)
    seg = np.hypot(*np.diff(P, axis=0).T)
    keep = np.concatenate([[True], seg > 1e-6]); P = P[keep]
    s = np.concatenate([[0], np.cumsum(np.hypot(*np.diff(P, axis=0).T))])
    if s[-1] < step: return P
    t = np.arange(0, s[-1], step); t = np.append(t, s[-1])
    return np.stack([np.interp(t, s, P[:, 0]), np.interp(t, s, P[:, 1])], 1)

def _normals(P, closed=False):
    if closed:
        T = np.roll(P, -1, 0) - np.roll(P, 1, 0)
    else:
        T = np.gradient(P, axis=0)
    T /= (np.linalg.norm(T, axis=1, keepdims=True) + 1e-9)
    return np.stack([-T[:, 1], T[:, 0]], 1)

def _smooth_noise(n, scale=0.06, freq=6, seed=None):
    rng = random.Random(seed)
    ph = [rng.uniform(0, 6.28) for _ in range(3)]
    x = np.linspace(0, 1, n)
    return 1 + scale * sum(np.sin(2*math.pi*(freq*(k+1)/2)*x + ph[k]) / (k+1) for k in range(3)) / 1.8

def _d(P):
    return 'M' + ' L'.join(f'{x:.2f} {y:.2f}' for x, y in P) + 'Z'

# ------------------------------------------------------------ 入り抜き線
def taper(d, w, tin=0.25, tout=0.35, wmin=0.0, wobble=0.05, seed=None):
    """入り(tin)・抜き(tout)付きの線。戻り値は塗り用 path d。
    tin/tout は全長に対する割合。0なら入り/抜き無し(丸止め相当の太さ)。"""
    P = sample_path(d) if isinstance(d, str) else resample(d)
    n = len(P)
    if n < 2: return ''
    s = np.concatenate([[0], np.cumsum(np.hypot(*np.diff(P, axis=0).T))]); t = s / s[-1]
    ease = lambda x: np.sin(np.clip(x, 0, 1) * math.pi / 2)   # 入り抜きの太さカーブ
    fin = ease(t / tin) if tin > 0 else np.ones(n)
    fout = ease((1 - t) / tout) if tout > 0 else np.ones(n)
    W = (wmin + (w - wmin) * fin * fout) * _smooth_noise(n, wobble, seed=seed)
    N = _normals(P)
    L = P + N * W[:, None] / 2; R = P - N * W[:, None] / 2
    return _d(np.concatenate([L, R[::-1]]))

def contour(d, w, light_k=0.7, light=LIGHT, wobble=0.04, seed=None):
    """閉じた輪郭線。光源の反対側(影側)ほど太くなる(=強弱で立体感)。"""
    P = sample_path(d)
    if np.allclose(P[0], P[-1]): P = P[:-1]
    area = 0.5 * np.sum(P[:, 0]*np.roll(P[:, 1], -1) - np.roll(P[:, 0], -1)*P[:, 1])
    N = _normals(P, closed=True) * (1 if area > 0 else -1)   # 外向き法線
    lx, ly = light; ln = math.hypot(lx, ly); lx, ly = lx/ln, ly/ln
    shade = -(N[:, 0]*lx + N[:, 1]*ly)                      # 光源と反対を向くほど +
    W = w * (1 + light_k * shade) * _smooth_noise(len(P), wobble, seed=seed)
    W = np.clip(W, w * 0.35, None)
    o = P + N * W[:, None] * 0.5; i = P - N * W[:, None] * 0.5
    return _d(o) + ' ' + _d(i[::-1])

# ------------------------------------------------------------ 毛束
def clump(root, tip, width, bend=0.0, tipw=0.0, profile='hang'):
    """毛束1本。root→tip を中心線とし、根元 width から先端に向けて細る葉形の path d と中心線を返す。
    bend は中心線の曲がり(幅に対する比、+で進行方向の左)。"""
    (x0, y0), (x1, y1) = root, tip
    dx, dy = x1 - x0, y1 - y0; L = math.hypot(dx, dy)
    nx, ny = -dy / L, dx / L
    c = (x0 + dx*0.5 + nx*bend*L, y0 + dy*0.5 + ny*bend*L)
    center = f'M {x0} {y0} Q {c[0]:.1f} {c[1]:.1f} {x1} {y1}'
    P = sample_path(center); s = np.linspace(0, 1, len(P))
    if profile == 'leaf':   # 根元も細く中ほどが太い(つむじから放射する前髪)
        W = width * np.sin(np.clip(s / 0.4, 0, 1) * math.pi / 2) * (1 - s) ** 0.8 + tipw
    else:                   # 根元が太い(垂れる横髪・後ろ髪)
        W = width * (1 - s) ** 0.75 * (0.85 + 0.6 * s * (1 - s)) + tipw
    N = _normals(P)
    Lp = P + N * W[:, None]/2; Rp = P - N * W[:, None]/2
    return _d(np.concatenate([Lp, Rp[::-1]])), Lp, Rp, P

# ------------------------------------------------------------ ページ
FONT_CSS = """
@font-face{font-family:"MKana";src:local("Noto Serif CJK JP Bold"),local("NotoSerifCJKjp-Bold");unicode-range:U+3000-30FF,U+FF5E;}
@font-face{font-family:"MKanji";src:local("Noto Sans CJK JP Bold"),local("NotoSansCJKjp-Bold");}
@font-face{font-family:"MSfx";src:local("Noto Sans CJK JP Black"),local("NotoSansCJKjp-Black");}
"""
ANTIQUE = "'MKana','MKanji','IPAPGothic',sans-serif"   # 明朝かな+ゴシック漢字 = アンチック体の構成

class Page:
    def __init__(s, w, h):
        s.w, s.h = w, h; s.t, s.i, s.defs = [], [], []
        s._id = 0
    # 基本
    def uid(s, p='id'): s._id += 1; return f'{p}{s._id}'
    def both(s, t, i): s.t.append(t); s.i.append(i)
    def tone(s, d, gray): s.t.append(f'<path d="{d}" fill="{gray}"/>')
    def ink(s, svg): s.i.append(svg)
    def black(s, d): s.i.append(f'<path d="{d}" fill="#000" fill-rule="nonzero"/>')
    def white(s, d): s.i.append(f'<path d="{d}" fill="#fff"/>')
    def fill(s, d, gray='#fff'):
        """塗り(線なし)。tone層に gray、ink層に白(=下の線を隠す)。"""
        s.both(f'<path d="{d}" fill="{gray}"/>', f'<path d="{d}" fill="#fff"/>')
    def shape(s, d, gray='#fff', w=3.0, light_k=0.7, seed=None):
        s.fill(d, gray); s.ink(f'<path d="{contour(d, w, light_k, seed=seed)}" fill="#000" fill-rule="evenodd"/>')
    def line(s, d, w=2.0, tin=0.25, tout=0.35, color='#000', **kw):
        s.ink(f'<path d="{taper(d, w, tin, tout, **kw)}" fill="{color}"/>')
    def open(s, attr): s.both(f'<g {attr}>', f'<g {attr}>')
    def close(s): s.both('</g>', '</g>')
    def clip_open(s, d):
        cid = s.uid('clip'); s.defs.append(f'<clipPath id="{cid}"><path d="{d}"/></clipPath>')
        s.open(f'clip-path="url(#{cid})"')
    def tone_clip_open(s, d):
        cid = s.uid('clip'); s.defs.append(f'<clipPath id="{cid}"><path d="{d}"/></clipPath>')
        s.t.append(f'<g clip-path="url(#{cid})">')
    def tone_close(s): s.t.append('</g>')
    def gradient(s, stops, x1=0, y1=0, x2=0, y2=1):
        gid = s.uid('g')
        st = ''.join(f'<stop offset="{o}" stop-color="{c}"/>' for o, c in stops)
        s.defs.append(f'<linearGradient id="{gid}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}">{st}</linearGradient>')
        return f'url(#{gid})'
    # 文字
    def text(s, x, y, w, h, html, size=30, vertical=True, family=ANTIQUE, extra=''):
        wm = 'vertical-rl' if vertical else 'horizontal-tb'
        s.ink(f'<foreignObject x="{x}" y="{y}" width="{w}" height="{h}"><div xmlns="http://www.w3.org/1999/xhtml" '
              f'style="width:{w}px;height:{h}px;display:flex;align-items:center;justify-content:center;">'
              f'<div style="writing-mode:{wm};font-family:{family};font-size:{size}px;line-height:1.35;'
              f'letter-spacing:0.02em;{extra}">{html}</div></div></foreignObject>')
    def bubble(s, cx, cy, rx, ry, html, tail=None, size=30, w=3.0):
        """楕円吹き出し。しっぽは本体と一体の1本の輪郭で描く(継ぎ目を作らない)。"""
        pts = []
        a0 = math.atan2((tail[1]-cy)/ry, (tail[0]-cx)/rx) if tail else None
        for k in range(181):
            a = 2*math.pi*k/180
            if a0 is not None:
                da = (a - a0 + math.pi) % (2*math.pi) - math.pi
                if abs(da) < 0.16:
                    continue
            pts.append((a, cx + rx*math.cos(a), cy + ry*math.sin(a)))
        if a0 is not None:
            # しっぽの位置で輪郭を開き、先端へ寄り道させる
            idx = min(range(len(pts)), key=lambda j: ((pts[j][0]-a0-0.16+math.pi) % (2*math.pi)-math.pi)**2)
            seq = pts[idx:] + pts[:idx]
            P = [(x, y) for _, x, y in seq] + [tuple(tail)]
        else:
            P = [(x, y) for _, x, y in pts]
        d = 'M' + ' L'.join(f'{x:.1f} {y:.1f}' for x, y in P) + 'Z'
        s.fill(d, '#fff')
        s.ink(f'<path d="{contour(d, w, 0.3)}" fill="#000" fill-rule="evenodd"/>')
        s.text(cx-rx, cy-ry, 2*rx, 2*ry, html, size)
    def sfx(s, x, y, html, size, rot=0, vertical=False, w=500, h=500, outline=0.2):
        """描き文字。白フチ→黒の二度描き。"""
        wm = 'vertical-rl' if vertical else 'horizontal-tb'
        for st in (f'-webkit-text-stroke:{size*outline:.0f}px #fff;paint-order:stroke fill;', f'-webkit-text-stroke:{size*0.04:.1f}px #000;'):
            s.ink(f'<foreignObject x="{x}" y="{y}" width="{w}" height="{h}" transform="rotate({rot} {x} {y})">'
                  f'<div xmlns="http://www.w3.org/1999/xhtml" style="writing-mode:{wm};font-family:\'MSfx\',\'MKanji\';'
                  f'font-size:{size}px;letter-spacing:-0.04em;color:#000;{st}">{html}</div></foreignObject>')
    # 効果
    def focus_lines(s, cx, cy, r_in=(300, 420), n=160, seed=1):
        rng = random.Random(seed)
        for _ in range(n):
            a = rng.uniform(0, 2*math.pi); R = 2000; r = rng.uniform(*r_in); dw = rng.uniform(0.005, 0.02)
            s.black(f'M {cx+R*math.cos(a-dw):.1f} {cy+R*math.sin(a-dw):.1f} L {cx+R*math.cos(a+dw):.1f} {cy+R*math.sin(a+dw):.1f} L {cx+r*math.cos(a):.1f} {cy+r*math.sin(a):.1f} Z')
    def sparkle(s, cx, cy, r, w=1.6):
        pts = []
        for k in range(8):
            a = k*math.pi/4; rr = r if k % 2 == 0 else r*0.22
            pts.append((cx+rr*math.sin(a), cy-rr*math.cos(a)))
        d = 'M' + ' L'.join(f'{x:.1f} {y:.1f}' for x, y in pts) + 'Z'
        s.white(d); s.ink(f'<path d="{contour(d, w, 0)}" fill="#000" fill-rule="evenodd"/>')
    # 出力
    def svg(s, layer):
        body = s.t if layer == 'tone' else s.i
        return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{s.w}" height="{s.h}" viewBox="0 0 {s.w} {s.h}">'
                f'<defs><style>{FONT_CSS}</style>{"".join(s.defs)}</defs><rect width="{s.w}" height="{s.h}" fill="#fff"/>'
                + '\n'.join(body) + '</svg>')
    def save(s, out_png, scale=2, lpi=9, workdir=None):
        workdir = workdir or os.path.dirname(os.path.abspath(out_png))
        base = os.path.splitext(os.path.basename(out_png))[0]
        paths = {}
        for layer in ('tone', 'ink'):
            sp = os.path.join(workdir, f'{base}.{layer}.svg'); open(sp, 'w').write(s.svg(layer))
            pp = os.path.join(workdir, f'{base}.{layer}.png')
            subprocess.run(['node', os.path.join(HERE, 'render.js'), sp, pp, str(s.w), str(s.h), str(scale)], check=True)
            paths[layer] = pp
        compose(paths['tone'], paths['ink'], out_png, period=lpi)
        return out_png

def compose(tone_png, ink_png, out_png, period=9, angle=45):
    """tone 層を網点化し、ink 層と合成。period は網点の周期(px)。2倍出力で 9 前後が細かく上品。粗くしたい時だけ 12〜。"""
    from PIL import Image
    tone = np.asarray(Image.open(tone_png).convert('L')).astype(np.float32) / 255
    ink = np.asarray(Image.open(ink_png).convert('L')).astype(np.float32) / 255
    h, w = tone.shape
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    a = math.radians(angle); u = xx*math.cos(a) + yy*math.sin(a); v = -xx*math.sin(a) + yy*math.cos(a)
    thr = 0.5 + 0.25*(np.cos(2*math.pi*u/period) + np.cos(2*math.pi*v/period))
    dots = np.where((1 - tone) > thr + 1e-4, 0.0, 1.0)
    dots[tone > 0.985] = 1.0; dots[tone < 0.03] = 0.0
    out = np.minimum(dots, ink)
    Image.fromarray((out*255).astype(np.uint8)).save(out_png)
