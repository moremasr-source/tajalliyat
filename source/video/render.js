// usage: node render.js <id> [stills: comma list of seconds]
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const path = require('path');
const [id, stills] = process.argv.slice(2);
const FPS = 30;
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await p.goto('file://' + path.join(__dirname, 'engine.html') + '?v=' + id);
  await p.evaluate(() => window.ready);
  const D = await p.evaluate(() => window.DUR);
  const el = await p.$('canvas');
  if (stills) {
    for (const s of stills.split(',')) { await p.evaluate(t => frame(t), +s);
      await el.screenshot({ path: path.join(__dirname, `out/${id}_${s}.png`) }); }
    return b.close();
  }
  const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-',
    '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', '-pix_fmt', 'yuv420p', path.join(__dirname, `out/${id}_v.mp4`)], { stdio: ['pipe', 'ignore', 'inherit'] });
  for (let i = 0; i < FPS * D; i++) {
    await p.evaluate(t => frame(t), i / FPS);
    const buf = await el.screenshot({ type: 'jpeg', quality: 92 });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
  }
  ff.stdin.end(); await new Promise(r => ff.on('close', r)); await b.close();
})();
