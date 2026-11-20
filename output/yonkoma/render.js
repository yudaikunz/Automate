const { chromium } = require('playwright');
(async () => { const b = await chromium.launch();
 const p = await b.newPage({ viewport:{width:900,height:2478}, deviceScaleFactor:2});
 for (const n of ['tone','ink']) { await p.goto('file://'+process.cwd()+'/'+n+'.svg'); await p.screenshot({path:n+'.png'}); }
 await b.close(); })();
