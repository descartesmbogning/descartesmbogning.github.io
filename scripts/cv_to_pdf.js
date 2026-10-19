const { chromium } = require('playwright');
(async()=>{const b=await chromium.launch({args:['--headless=new'],headless:false});const p=await b.newPage();
await p.goto('file://'+process.argv[2]);await p.pdf({path:process.argv[3],format:'Letter',printBackground:true,preferCSSPageSize:true});await b.close()})();
