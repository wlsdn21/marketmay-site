// 메뉴 사진 일괄 처리: D:\그림N.png → public/images/menu/<slug>.jpg
// PNG → JPG (quality 85), 최대 1600px, sRGB 보장
import sharp from 'sharp';
import path from 'node:path';
import fs from 'node:fs';
import process from 'node:process';

const SOURCE_DIR = 'D:\\';
const OUT_DIR = path.join(process.cwd(), 'public', 'images', 'menu');

// 그림번호 → 메뉴 slug (영문 슬러그로 통일, URL 친화적)
const MAPPING = {
  3: 'lemonade',
  4: 'grapefruit-ade',
  5: 'strawberry-yogurt-shake',
  6: 'omija-ade',
  7: 'blueberry-yogurt',
  8: 'blueberry-yoyo',
  9: 'americano-iced',
  10: 'choco-iced',
  11: 'matcha-latte-iced',
  12: 'strawberry-yoyo',         // 메뉴에서는 제거되었지만 보존
  13: 'matcha-latte-hot',
  14: 'hot-chocolate',
  15: 'omija-tea',
  16: 'marocchino',
  17: 'royal-milk-tea',
  18: 'omija-tea-2',             // 15와 중복 대안
  19: 'grapefruit-tea',
  21: 'marocchino-2',            // 16과 중복 대안
  22: 'latte-hot-8',
  30: 'americano-hot',
  32: 'burrata-salad',
  33: 'tomato-stew',
  34: 'ricotta-cold-pasta',
  35: 'jambon-beurre-sandwich',
  36: 'mmbp',
  37: 'pumpkin-soup',
  38: 'margherita-pizza',
};

fs.mkdirSync(OUT_DIR, { recursive: true });

async function processOne(num, slug) {
  const src = path.join(SOURCE_DIR, `그림${num}.png`);
  const dst = path.join(OUT_DIR, `${slug}.jpg`);
  if (!fs.existsSync(src)) {
    console.warn(`SKIP: ${src} (not found)`);
    return;
  }
  await sharp(src)
    .resize({ width: 1600, withoutEnlargement: true })
    .flatten({ background: '#ffffff' })   // PNG 투명도 → 흰색 바탕
    .jpeg({ quality: 85, mozjpeg: true })
    .toFile(dst);
  const sz = fs.statSync(dst).size;
  console.log(`OK:   ${slug.padEnd(28)} ← 그림${num}.png  (${(sz/1024).toFixed(1)}KB)`);
}

(async () => {
  for (const [num, slug] of Object.entries(MAPPING)) {
    try { await processOne(Number(num), slug); }
    catch (e) { console.error(`FAIL: 그림${num} → ${slug}`, e.message); }
  }
  console.log('\nDone.');
})();
