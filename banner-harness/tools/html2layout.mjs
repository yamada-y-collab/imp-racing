#!/usr/bin/env node
// HTML をブラウザで実測して layout.json にする。
//
//   node tools/html2layout.mjs <版のディレクトリ>   例: work/sf-finale-suzuka/v1
//
// 版のディレクトリにある <幅>x<高さ>.html をそれぞれそのサイズで開き、次を書き出す。
//   out/<幅>x<高さ>.png     … 仕上がり
//   out/<幅>x<高さ>.bg.png  … 文字とロゴを隠した地（コントラスト検査と PPTX の背景に使う）
//   out/layout.json         … data-role の付いた要素の位置・文字・書体・色
import { createRequire } from 'node:module';
import fs from 'node:fs';
import path from 'node:path';
import { pathToFileURL, fileURLToPath } from 'node:url';

// CJS の解決（NODE_PATH・グローバル導入）でも、プロジェクトに入れた playwright でも読めるように require で読む
const { chromium } = createRequire(import.meta.url)('playwright');

const dir = path.resolve(process.argv[2] || '');
if (!process.argv[2] || !fs.existsSync(dir)) {
  console.error('使い方: node tools/html2layout.mjs <版のディレクトリ>');
  process.exit(2);
}
const files = fs.readdirSync(dir).filter((f) => /^\d+x\d+\.html$/.test(f)).sort(bySize);
if (files.length === 0) {
  console.error(`${dir} に <幅>x<高さ>.html がありません`);
  process.exit(2);
}
const outDir = path.join(dir, 'out');
fs.mkdirSync(outDir, { recursive: true });

function bySize(a, b) {
  const [aw, ah] = a.split('.')[0].split('x').map(Number);
  const [bw, bh] = b.split('.')[0].split('x').map(Number);
  return bw * bh - aw * ah;
}

// Chromium は HTTPS_PROXY を自分では読まないので、あれば渡す（Google Fonts の読み込みのため）
const proxy = process.env.HTTPS_PROXY || process.env.https_proxy;
const browser = await chromium.launch(proxy ? { proxy: { server: proxy } } : {});
const layout = { generated_at: new Date().toISOString(), sizes: {} };

try {
  for (const file of files) {
    const size = file.replace('.html', '');
    const [width, height] = size.split('x').map(Number);
    const page = await browser.newPage({ viewport: { width, height }, deviceScaleFactor: 1 });
    const warnings = [];
    page.on('requestfailed', (r) => warnings.push(`読み込み失敗: ${r.url()} (${r.failure()?.errorText})`));

    await page.goto(pathToFileURL(path.join(dir, file)).href, { waitUntil: 'networkidle' });
    await page.evaluate(async () => {
      await document.fonts.ready;
      await Promise.all([...document.images].map((img) => (img.complete ? null : img.decode().catch(() => null))));
    });

    const measured = await page.evaluate(() => {
      const canvas = document.querySelector('[data-canvas]');
      const c = canvas ? canvas.getBoundingClientRect() : { left: 0, top: 0, width: innerWidth, height: innerHeight };
      const cssUrl = (v) => {
        const m = /url\(["']?(.*?)["']?\)/.exec(v || '');
        return m ? new URL(m[1], document.baseURI).href : null;
      };
      const elements = [...document.querySelectorAll('[data-role]')].map((el, i) => {
        const r = el.getBoundingClientRect();
        const cs = getComputedStyle(el);
        const role = el.dataset.role;
        const item = {
          index: i,
          role,
          id: el.id || el.dataset.name || `${role}-${i}`,
          box: { x: r.left - c.left, y: r.top - c.top, w: r.width, h: r.height },
          opacity: Number(cs.opacity),
          visible: cs.visibility !== 'hidden' && cs.display !== 'none' && r.width > 0 && r.height > 0,
          background_color: cs.backgroundColor,
        };
        if (role === 'text') {
          // 行ごとの位置（PPTX で改行を再現するため）
          const range = document.createRange();
          range.selectNodeContents(el);
          const lineTops = [...new Set([...range.getClientRects()].map((q) => Math.round(q.top)))];
          Object.assign(item, {
            text: el.innerText,
            color: cs.color,
            font_family: cs.fontFamily,
            font_size: parseFloat(cs.fontSize),
            font_weight: cs.fontWeight,
            letter_spacing: cs.letterSpacing,
            line_height: cs.lineHeight,
            text_align: cs.textAlign,
            line_count: lineTops.length,
            // 判定は check.py で行う（行送りを詰めた欧文書体は、収まっていても scrollHeight が少し大きく出る）
            scroll: { w: el.scrollWidth, h: el.scrollHeight, client_w: el.clientWidth, client_h: el.clientHeight },
            nested_roles: el.querySelector('[data-role]') !== null,
          });
        } else if (role === 'image' || role === 'logo') {
          item.src = el.tagName === 'IMG' ? el.currentSrc || el.src : cssUrl(cs.backgroundImage);
          item.object_fit = cs.objectFit;
          item.natural = el.tagName === 'IMG' ? { w: el.naturalWidth, h: el.naturalHeight } : null;
          item.loaded = el.tagName === 'IMG' ? el.complete && el.naturalWidth > 0 : item.src !== null;
        }
        return item;
      });
      return {
        canvas: { w: c.width, h: c.height, found: Boolean(canvas) },
        document_overflow: document.documentElement.scrollWidth > innerWidth || document.documentElement.scrollHeight > innerHeight,
        elements,
      };
    });

    await page.screenshot({ path: path.join(outDir, `${size}.png`) });
    await page.addStyleTag({ content: '[data-role="text"],[data-role="logo"]{visibility:hidden!important}' });
    await page.screenshot({ path: path.join(outDir, `${size}.bg.png`) });
    await page.close();

    for (const el of measured.elements) {
      if (el.src && el.src.startsWith('file:')) el.src_path = fileURLToPath(el.src);
    }
    layout.sizes[size] = { width, height, html: file, warnings, ...measured };
    console.log(`${size}: ${measured.elements.length} 要素${warnings.length ? ` / 警告 ${warnings.length}` : ''}`);
  }
} finally {
  await browser.close();
}

fs.writeFileSync(path.join(outDir, 'layout.json'), JSON.stringify(layout, null, 2) + '\n');
console.log(`書き出し: ${path.relative(process.cwd(), path.join(outDir, 'layout.json'))}`);
