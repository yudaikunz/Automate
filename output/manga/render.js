const { chromium } = require('playwright');
(async () => { const b = await chromium.launch();
 const p = await b.newPage({ viewport:{width:800,height:1100}, deviceScaleFactor:2});
 await p.goto('file://'+process.cwd()+'/manga.svg');
 for (const [show,hide] of [['tone','ink'],['ink','tone']]) {
   await p.evaluate(([s,h])=>{document.getElementById(s).style.display='';document.getElementById(h).style.display='none';},[show,hide]);
   await p.screenshot({path:show+'.png'});
 }
 await b.close(); })();
