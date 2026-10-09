const {chromium}=require('playwright');
const path=require('path');const os=require('os');
const evidence=process.env.BROBS_EVIDENCE_DIR||os.tmpdir();
const cases=process.env.BROBS_DASHBOARD_CASES?JSON.parse(process.env.BROBS_DASHBOARD_CASES):[{url:process.env.BROBS_DASHBOARD_URL||'http://127.0.0.1:8778/',symbol:process.env.BROBS_EXPECTED_SYMBOL||'EUR_USD',currency:process.env.BROBS_EXPECTED_CURRENCY||'USD',profile:'forex'}];
(async()=>{
 const browser=await chromium.launch({executablePath:process.env.BROBS_BROWSER_EXECUTABLE||undefined,args:process.env.BROBS_BROWSER_ARGS?JSON.parse(process.env.BROBS_BROWSER_ARGS):['--no-sandbox','--disable-gpu','--disable-software-rasterizer','--single-process','--no-zygote'],headless:true});
 const results=[];const page=await browser.newPage();
 for(const sample of cases){
  page.removeAllListeners("pageerror");const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto(sample.url);await page.waitForFunction(()=>document.getElementById('equity').textContent!=='—');
  if(!await page.locator('#positions').textContent().then(s=>s.includes(sample.symbol)))throw Error(sample.profile+' position not rendered');
  if(!await page.locator('#currency-label').textContent().then(s=>s.includes(sample.currency)))throw Error('Wrong account currency');
  if(sample.currency==='USDT'&&!await page.locator('#equity').textContent().then(s=>s.includes('USDT')&&!s.includes('$')))throw Error('USDT displayed as USD');
  if(!await page.locator('#expectancy').textContent().then(Boolean))throw Error('Expectancy not rendered');
  if(!await page.locator('#guards').textContent().then(Boolean))throw Error('Entry-guard state not rendered');
  if(process.env.BROBS_EXPECT_FRESH==='1'&&!await page.locator('#connection').textContent().then(s=>s.includes('Connected')))throw Error('Fresh runner state not shown');
  await page.locator('#refresh').click();await page.setViewportSize({width:390,height:844});
  if(!await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth))throw Error('Mobile page overflow');
  await page.screenshot({path:path.join(evidence,'brobs-'+sample.profile+'-mobile.png'),fullPage:true});
  await page.setViewportSize({width:1280,height:900});await page.screenshot({path:path.join(evidence,'brobs-'+sample.profile+'-desktop.png'),fullPage:true});
  if(errors.length)throw Error(errors.join(';'));
  results.push({market:sample.profile,desktop_render:'PASS',mobile_390px:'PASS',live_api_state:'PASS',refresh:'PASS',currency:sample.currency,javascript_errors:errors.length});
 }
 console.log(JSON.stringify(results));await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
