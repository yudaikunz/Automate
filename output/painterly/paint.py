# Hertzmann式ペインタリー・レンダリング（筆跡を太→細の順に重ねる）
import sys, numpy as np, cv2, random
from PIL import Image, ImageDraw
random.seed(7); np.random.seed(7)
src = cv2.cvtColor(cv2.imread(sys.argv[1]), cv2.COLOR_BGR2RGB).astype(np.float32)
H, W = src.shape[:2]
S = 2  # スーパーサンプリング倍率
canvas = Image.new('RGB', (W*S, H*S), (205, 190, 160))
height = Image.new('L', (W*S, H*S), 0)   # 絵具の盛り上がり用
draw, hdraw = ImageDraw.Draw(canvas), ImageDraw.Draw(height)
brushes = [(24, 0.9), (12, 0.6), (6, 0.45), (3, 0.3)]
T = 22.0
for R, fc in brushes:
    ref = cv2.GaussianBlur(src, (0, 0), R * 0.5)
    lum = cv2.cvtColor(ref.astype(np.uint8), cv2.COLOR_RGB2GRAY).astype(np.float32)
    gx = cv2.Sobel(lum, cv2.CV_32F, 1, 0, ksize=3); gy = cv2.Sobel(lum, cv2.CV_32F, 0, 1, ksize=3)
    cur = np.asarray(canvas.resize((W, H), Image.BILINEAR)).astype(np.float32)
    diff = np.linalg.norm(cur - ref, axis=2)
    if R == brushes[0][0]: diff[:] = 999
    strokes = []
    step = max(1, R)
    for y0 in range(0, H, step):
        for x0 in range(0, W, step):
            blk = diff[y0:y0+step, x0:x0+step]
            if blk.mean() < T: continue
            iy, ix = np.unravel_index(np.argmax(blk), blk.shape)
            x, y = x0 + ix, y0 + iy
            col = ref[y, x]
            pts = [(x, y)]; lastdx = lastdy = 0
            maxlen = int(np.clip(16 - R*0.3, 4, 14)) if R > 3 else 6
            for i in range(maxlen):
                xi, yi = int(np.clip(x, 0, W-1)), int(np.clip(y, 0, H-1))
                if i > 1 and np.linalg.norm(ref[yi, xi] - cur[yi, xi]) < np.linalg.norm(ref[yi, xi] - col): break
                if i > 1 and np.linalg.norm(ref[yi, xi] - col) > 40: break
                g = np.hypot(gx[yi, xi], gy[yi, xi])
                if g < 1e-3:
                    dx, dy = (lastdx, lastdy) if (lastdx or lastdy) else (1, 0.3)
                else:
                    dx, dy = -gy[yi, xi] / g, gx[yi, xi] / g   # 輪郭に沿う向き
                if lastdx * dx + lastdy * dy < 0: dx, dy = -dx, -dy
                dx = fc * dx + (1 - fc) * lastdx; dy = fc * dy + (1 - fc) * lastdy
                n = np.hypot(dx, dy) or 1; dx, dy = dx / n, dy / n
                x += R * dx; y += R * dy; lastdx, lastdy = dx, dy
                pts.append((x, y))
            strokes.append((pts, col))
    random.shuffle(strokes)
    for pts, col in strokes:
        j = np.random.normal(0, 7, 3) + np.random.normal(0, 5)   # 筆ごとの色ゆらぎ
        c = tuple(int(v) for v in np.clip(col + j, 0, 255))
        p = [(px * S, py * S) for px, py in pts]
        w = int(R * S * random.uniform(0.85, 1.15))
        if len(p) == 1: p = p * 2
        draw.line(p, fill=c, width=w, joint='curve')
        for q in (p[0], p[-1]): draw.ellipse([q[0]-w/2, q[1]-w/2, q[0]+w/2, q[1]+w/2], fill=c)
        # 盛り上がり: 筆の縁が高く、毛筋状の筋
        hv = random.randint(90, 200)
        hdraw.line(p, fill=hv, width=w, joint='curve')
        hdraw.line(p, fill=hv - 25, width=max(1, w // 3), joint='curve')
    print('brush', R, 'strokes', len(strokes), file=sys.stderr)
out = canvas.resize((W, H), Image.LANCZOS)
hmap = np.asarray(height.resize((W, H), Image.LANCZOS)).astype(np.float32)
# 絵具の凹凸に左上からの光を当てる
hb = cv2.GaussianBlur(hmap, (0, 0), 0.8)
sx = cv2.Sobel(hb, cv2.CV_32F, 1, 0, ksize=3); sy = cv2.Sobel(hb, cv2.CV_32F, 0, 1, ksize=3)
shade = 1 + np.clip((-sx - sy) * 0.0006, -0.07, 0.07)
img = np.asarray(out).astype(np.float32) * shade[..., None]
Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).save(sys.argv[2])
