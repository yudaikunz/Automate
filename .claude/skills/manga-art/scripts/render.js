// usage: node render.js in.svg out.png W H [scale]
// SVG を HTML に埋め込んで描画する(SVG 単体で開くと @font-face の合成フォントが効かないため)。
const fs = require('fs');
const { chromium } = require('playwright');
(async () => {
  const [inp, out, W, H, sc] = process.argv.slice(2);
  const svg = fs.readFileSync(inp, 'utf8');
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: +W, height: +H }, deviceScaleFactor: +(sc || 2) });
  await p.setContent(`<!doctype html><html><head><meta charset="utf-8"><style>html,body{margin:0;background:#fff}svg{display:block}</style></head><body>${svg}</body></html>`);
  await p.evaluate(() => document.fonts.ready);
  await p.screenshot({ path: out });
  await b.close();
})();
