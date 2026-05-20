// 메뉴 사진 일괄 처리: D:\그림N.png → public/images/menu/<slug>.jpg
// 비백색 픽셀의 무게중심(COM)을 캔버스 정중앙에 맞춰서 피사체를 진짜 가운데 정렬
import sharp from 'sharp';
import path from 'node:path';
import fs from 'node:fs';
import process from 'node:process';

const SOURCE_DIR = 'D:\\';
const OUT_DIR = path.join(process.cwd(), 'public', 'images', 'menu');

const CANVAS_W = 1200;
const CANVAS_H = 900;
const SUBJECT_FIT_W = 0.84; // 캔버스 가로의 최대 점유율
const SUBJECT_FIT_H = 0.92; // 캔버스 세로의 최대 점유율
const WHITE_THRESHOLD = 235; // 픽셀 밝기 >= 이 값이면 백색으로 간주 (피사체 아님)

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
  12: 'strawberry-yoyo',
  13: 'matcha-latte-hot',
  14: 'hot-chocolate',
  15: 'omija-tea',
  16: 'marocchino',
  17: 'royal-milk-tea',
  18: 'omija-tea-2',
  19: 'grapefruit-tea',
  21: 'cafe-mocha',
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

/** 비백색 픽셀의 무게중심 + 바운딩박스 검출 */
async function analyzeSubject(flatBuffer) {
  const { data, info } = await sharp(flatBuffer)
    .grayscale()
    .raw()
    .toBuffer({ resolveWithObject: true });
  const { width, height } = info;

  let sumX = 0, sumY = 0, sumW = 0;
  let minX = width, maxX = 0, minY = height, maxY = 0;
  for (let y = 0; y < height; y++) {
    const row = y * width;
    for (let x = 0; x < width; x++) {
      const v = data[row + x];
      if (v < WHITE_THRESHOLD) {
        // 백색에서 멀수록 가중치↑ (어두운 픽셀이 피사체일 확률 큼)
        const w = WHITE_THRESHOLD - v;
        sumX += x * w;
        sumY += y * w;
        sumW += w;
        if (x < minX) minX = x;
        if (x > maxX) maxX = x;
        if (y < minY) minY = y;
        if (y > maxY) maxY = y;
      }
    }
  }
  if (sumW === 0) return null;
  return {
    cx: sumX / sumW,
    cy: sumY / sumW,
    bbox: { left: minX, top: minY, width: maxX - minX + 1, height: maxY - minY + 1 },
    width, height,
  };
}

async function processOne(num, slug) {
  const src = path.join(SOURCE_DIR, `그림${num}.png`);
  const dst = path.join(OUT_DIR, `${slug}.jpg`);
  if (!fs.existsSync(src)) {
    console.warn(`SKIP: ${src} (not found)`);
    return;
  }

  // 1) 알파 → 흰 배경
  const flatBuffer = await sharp(src).flatten({ background: '#ffffff' }).toBuffer();

  // 2) 무게중심 + 바운딩박스 검출
  const a = await analyzeSubject(flatBuffer);
  if (!a) {
    console.warn(`SKIP: ${slug} (no subject)`);
    return;
  }

  // 3) 피사체 바운딩박스가 캔버스 점유 영역에 맞도록 스케일 결정
  const availW = CANVAS_W * SUBJECT_FIT_W;
  const availH = CANVAS_H * SUBJECT_FIT_H;
  const scale = Math.min(availW / a.bbox.width, availH / a.bbox.height, 1);
  const newW = Math.max(1, Math.round(a.width * scale));
  const newH = Math.max(1, Math.round(a.height * scale));
  const resized = await sharp(flatBuffer).resize(newW, newH).toBuffer();

  // 4) 무게중심(COM)을 캔버스 정중앙에 오도록 합성 위치 계산
  const newCx = a.cx * scale;
  const newCy = a.cy * scale;
  let left = Math.round(CANVAS_W / 2 - newCx);
  let top = Math.round(CANVAS_H / 2 - newCy);

  // 음수 offset도 허용 (이미지 가장자리 자름)
  await sharp({
    create: { width: CANVAS_W, height: CANVAS_H, channels: 3, background: '#ffffff' },
  })
    .composite([{ input: resized, left, top }])
    .jpeg({ quality: 85, mozjpeg: true })
    .toFile(dst);

  const sz = fs.statSync(dst).size;
  console.log(
    `OK: ${slug.padEnd(28)} ${newW}×${newH}  COM(${newCx.toFixed(0)},${newCy.toFixed(0)})  offset(${left},${top})  (${(sz/1024).toFixed(1)}KB)`
  );
}

(async () => {
  for (const [num, slug] of Object.entries(MAPPING)) {
    try { await processOne(Number(num), slug); }
    catch (e) { console.error(`FAIL: 그림${num} → ${slug}`, e.message); }
  }
  console.log('\nDone.');
})();
