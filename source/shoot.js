const {chromium}=require('playwright');const fs=require('fs');
(async()=>{const b=await chromium.launch();const ids=Object.keys(JSON.parse(fs.readFileSync('/home/claude/site/products/products.json')));
const only=process.argv[2];const p=await b.newPage({viewport:{width:1080,height:1920}});const errs=[];p.on('pageerror',e=>errs.push(e.message));
for(const id of ids){if(only&&id!==only)continue;fs.mkdirSync(`/home/claude/site/products/img/${id}`,{recursive:true});
 for(const s of ['0','1','2','3','4','w']){const h=s==='w'?1920:1350;await p.setViewportSize({width:1080,height:h});
  await p.goto(`file:///home/claude/site/products/render/card.html?n=${id}&s=${s}`);await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(120);
  const of=await p.evaluate(()=>{const c=document.querySelector('.c');return c.scrollHeight>c.clientHeight+2});if(of)errs.push(`overflow ${id} ${s}`);
  await p.screenshot({path:`/home/claude/site/products/img/${id}/${s==='w'?'wallpaper':'slide-'+(+s+1)}.jpg`,type:'jpeg',quality:86});}}
console.log('errors',errs);await b.close();})();
