const { chromium } = require('playwright');
(async () => { const b = await chromium.launch();
 const p = await b.newPage({ viewport:{width:800,height:1000}});
 await p.goto('file://'+process.cwd()+'/base.svg'); await p.screenshot({path:'base.png'}); await b.close(); })();
