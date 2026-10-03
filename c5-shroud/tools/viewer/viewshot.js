const { chromium } = require(require('child_process').execSync('npm root -g').toString().trim()+'/playwright');
(async()=>{
  const b = await chromium.launch({executablePath:'/opt/pw-browsers/chromium', args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']});
  const p = await b.newPage({viewport:{width:1200,height:760}});
  p.on('pageerror',e=>console.log('ERR '+e.message));
  for (const a of process.argv.slice(2)) {
    const [name, q] = a.split('|');
    await p.goto('http://127.0.0.1:8799/'+(process.env.VIEW||'view.html')+'?'+q,{waitUntil:'load'});
    await p.waitForFunction(()=>window.ready===true,{timeout:120000});
    await (await p.$('#c')).screenshot({path:name});
  }
  await b.close();
})();
