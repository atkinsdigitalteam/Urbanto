// Render every page in manifest.json to PNG with headless Chromium (Playwright).
// Run: node render.js [name-filter]
const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');
(async () => {
  const manifest = JSON.parse(fs.readFileSync(path.join(__dirname, 'manifest.json'), 'utf8'));
  const filter = process.argv[2] || '';
  const browser = await chromium.launch();
  const mock = path.join(__dirname, '..', 'mockups');
  // pairs embed other PNGs, so render them last
  const order = manifest.filter(m => m.html.includes(filter)).sort((a, b) => (a.html.startsWith('pair') ? 1 : 0) - (b.html.startsWith('pair') ? 1 : 0));
  for (const m of order) {
    const page = await browser.newPage({ viewport: { width: m.width, height: m.height }, deviceScaleFactor: m.scale || 1 });
    await page.goto('file://' + path.join(mock, m.html));
    await page.evaluate(() => document.fonts.ready);
    await page.waitForTimeout(150);
    await page.screenshot({ path: path.join(mock, m.png), fullPage: false });
    await page.close();
    console.log('rendered', m.png);
  }
  await browser.close();
})();
