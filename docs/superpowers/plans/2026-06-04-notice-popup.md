# 공지/이벤트 팝업 (Notice Popup) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 홈 진입 시 뜨는 공지/이벤트 팝업을 추가한다 — X/바깥/ESC로 닫고, "오늘 하루 보지 않기" 지원, 내용은 `notice.yaml`로 관리.

**Architecture:** 노출 판단 순수 로직(`notice-visibility.ts`, 브라우저 안전·단위 테스트) + 빌드 타임 데이터 로드(`data.ts`) + 자체 완결형 컴포넌트(`NoticePopup.astro`, 기존 `MenuLightbox` 패턴). 홈에서만 마운트.

**Tech Stack:** Astro 6, Vanilla CSS(디자인 토큰), js-yaml, Vitest(신규, 순수 로직 단위 테스트용).

설계 문서: `docs/superpowers/specs/2026-06-04-notice-popup-design.md`

---

## File Structure

- **신규**
  - `src/lib/notice-visibility.ts` — 순수 함수(`shouldShowNotice`, `dismissValue`, `dateKey`). node import 금지(브라우저 번들에 포함됨).
  - `src/lib/notice-visibility.test.ts` — Vitest 단위 테스트.
  - `src/data/notice.yaml` — 사장님이 수정하는 팝업 내용.
  - `src/components/NoticePopup.astro` — 마크업 + 번들 `<script>`(순수 함수 import) + scoped 스타일.
- **수정**
  - `package.json` — `vitest` devDependency + `test` 스크립트.
  - `src/lib/data.ts` — `NoticeButton`/`Notice` 타입 + `notice` export.
  - `src/pages/index.astro` — import 및 `{notice.enabled && <NoticePopup />}` 마운트.

> **검증 전략 메모:** 이 레포는 테스트가 없는 소형 정적 사이트다. 자동 테스트는 **엣지케이스가 있는 순수 노출 로직에만** 적용하고(Task 1), DOM/애니메이션/스타일은 `npm run dev` 로컬 미리보기로 수동 검증한다(Task 4). 한 컴포넌트를 위해 jsdom/Playwright까지 도입하는 것은 과한 엔지니어링이라 의도적으로 제외.

---

## Task 1: 노출 판단 순수 로직 + 단위 테스트 (TDD)

**Files:**
- Modify: `package.json` (vitest devDep + test 스크립트)
- Test: `src/lib/notice-visibility.test.ts`
- Create: `src/lib/notice-visibility.ts`

- [ ] **Step 1: Vitest 설치 및 test 스크립트 추가**

Run:
```bash
npm install -D vitest
```
그리고 `package.json`의 `scripts`에 `test` 추가 (기존 스크립트는 유지):
```json
  "scripts": {
    "dev": "astro dev",
    "build": "astro build",
    "preview": "astro preview",
    "astro": "astro",
    "test": "vitest run"
  },
```

- [ ] **Step 2: 실패하는 테스트 작성** — `src/lib/notice-visibility.test.ts`

```ts
import { describe, it, expect } from 'vitest';
import { shouldShowNotice, dismissValue, dateKey } from './notice-visibility';

describe('dateKey', () => {
  it('로컬 날짜를 YYYY-MM-DD(0 패딩)로 변환', () => {
    // month는 0-indexed: 5 = 6월
    expect(dateKey(new Date(2026, 5, 4))).toBe('2026-06-04');
    expect(dateKey(new Date(2026, 11, 9))).toBe('2026-12-09');
  });
});

describe('dismissValue', () => {
  it('version과 날짜를 "{version}:{date}"로 결합', () => {
    expect(dismissValue(1, '2026-06-04')).toBe('1:2026-06-04');
    expect(dismissValue(3, '2026-12-09')).toBe('3:2026-12-09');
  });
});

describe('shouldShowNotice', () => {
  it('저장값이 없으면 노출', () => {
    expect(shouldShowNotice(null, 1, '2026-06-04')).toBe(true);
    expect(shouldShowNotice('', 1, '2026-06-04')).toBe(true);
  });
  it('같은 version을 오늘 닫았으면 숨김', () => {
    expect(shouldShowNotice('1:2026-06-04', 1, '2026-06-04')).toBe(false);
  });
  it('날짜가 지나면 다시 노출', () => {
    expect(shouldShowNotice('1:2026-06-03', 1, '2026-06-04')).toBe(true);
  });
  it('version이 바뀌면(새 공지) 다시 노출', () => {
    expect(shouldShowNotice('1:2026-06-04', 2, '2026-06-04')).toBe(true);
  });
  it('저장값 형식이 깨졌으면 노출', () => {
    expect(shouldShowNotice('garbage', 1, '2026-06-04')).toBe(true);
  });
});
```

- [ ] **Step 3: 테스트 실패 확인**

Run: `npm test`
Expected: FAIL — `Cannot find module './notice-visibility'` (또는 export 없음)

- [ ] **Step 4: 최소 구현** — `src/lib/notice-visibility.ts`

```ts
// 브라우저에서도 안전한 순수 로직 (node 모듈 import 금지 — 이 파일은 클라이언트 번들에 포함됨)

/** Date를 로컬 기준 YYYY-MM-DD 문자열로 변환. */
export function dateKey(d: Date): string {
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${y}-${m}-${day}`;
}

/** '오늘 하루 보지 않기' 저장 포맷: "{version}:{YYYY-MM-DD}" */
export function dismissValue(version: number, today: string): string {
  return `${version}:${today}`;
}

/**
 * 지금 팝업을 보여줘야 하는가?
 * 같은 version을 같은 날짜에 '오늘 하루 보지 않기'로 닫은 경우에만 false.
 * 그 외(저장값 없음 / 날짜 지남 / version 변경 / 형식 깨짐)는 모두 true.
 */
export function shouldShowNotice(stored: string | null, version: number, today: string): boolean {
  if (!stored) return true;
  const idx = stored.indexOf(':');
  if (idx === -1) return true;
  const storedVersion = stored.slice(0, idx);
  const storedDate = stored.slice(idx + 1);
  if (storedVersion !== String(version)) return true;
  if (storedDate !== today) return true;
  return false;
}
```

- [ ] **Step 5: 테스트 통과 확인**

Run: `npm test`
Expected: PASS (3 describe, 모든 it 통과)

- [ ] **Step 6: 커밋**

```bash
git add package.json package-lock.json src/lib/notice-visibility.ts src/lib/notice-visibility.test.ts
git commit -m "feat(notice): 팝업 노출 판단 순수 로직 + 단위 테스트 (Vitest)"
```

---

## Task 2: 데이터 — notice.yaml + data.ts 타입/로드

**Files:**
- Create: `src/data/notice.yaml`
- Modify: `src/lib/data.ts`

- [ ] **Step 1: `src/data/notice.yaml` 작성** (사장님이 수정하는 파일, 예시 내용 포함)

```yaml
# 공지/이벤트 팝업 — 이 파일만 수정하면 팝업 내용이 바뀝니다.
# - 팝업을 끄려면: enabled: false
# - 내용을 새로 바꿔서 '오늘 하루 보지 않기' 누른 사람에게도 다시 띄우려면: version 숫자를 +1
enabled: true
version: 1

# 포스터 이미지. public/images/ 안에 넣고 경로를 적으세요. 이미지가 없으면 image: "" (텍스트만 나옴).
image: /images/exterior.jpg
imageAlt: "market may 안내"

# 제목 (없으면 title: "")
title: "market may에 오신 것을 환영합니다"

# 본문 (여러 줄 가능, 없으면 body: "")
body: |
  영업시간 10:00 – 22:00
  매주 월요일은 정기 휴무입니다.

# 버튼이 필요 없으면 아래 button 블록 전체를 삭제하세요.
button:
  label: "인스타그램 구경하기"
  url: https://www.instagram.com/market.may_/
```

- [ ] **Step 2: `src/lib/data.ts`에 타입 + export 추가**

기존 `Menu` 인터페이스 블록 아래(파일 하단의 `export const info ...` 위 또는 근처)에 추가:
```ts
export interface NoticeButton {
  label: string;
  url: string;
}

export interface Notice {
  enabled: boolean;
  version?: number;
  image?: string;
  imageAlt?: string;
  title?: string;
  body?: string;
  button?: NoticeButton | null;
}
```
그리고 파일 맨 아래 export 묶음에 추가:
```ts
export const notice: Notice = load<Notice>('notice.yaml');
```

- [ ] **Step 3: YAML 파싱 검증**

Run:
```bash
node --input-type=module -e "import yaml from 'js-yaml'; import fs from 'node:fs'; console.log(yaml.load(fs.readFileSync('src/data/notice.yaml','utf8')))"
```
Expected: `{ enabled: true, version: 1, image: '/images/exterior.jpg', imageAlt: 'market may 안내', title: '...', body: '...\n...\n', button: { label: '...', url: '...' } }` 형태로 출력 (에러 없음)

- [ ] **Step 4: 커밋**

```bash
git add src/data/notice.yaml src/lib/data.ts
git commit -m "feat(notice): notice.yaml 데이터 + data.ts 타입/로드 추가"
```

---

## Task 3: NoticePopup.astro 컴포넌트

**Files:**
- Create: `src/components/NoticePopup.astro`

- [ ] **Step 1: 컴포넌트 작성** — `src/components/NoticePopup.astro`

```astro
---
// 공지/이벤트 팝업 — 홈 진입 시 노출, '오늘 하루 보지 않기' 지원.
// 기존 MenuLightbox.astro 패턴을 따르되, 노출 판단 로직은 lib/notice-visibility로 분리(테스트됨).
import { notice } from '../lib/data';

const version = notice.version ?? 1;
const hasContent = Boolean(notice.image || notice.title || notice.body);
const show = notice.enabled && hasContent;
const hasButton = Boolean(notice.button && notice.button.url && notice.button.label);
const hasTextBlock = Boolean(notice.title || notice.body || hasButton);
---
{show && (
  <div class="notice-overlay" data-version={version} aria-hidden="true">
    <div
      class="notice-card"
      role="dialog"
      aria-modal="true"
      aria-labelledby={notice.title ? 'notice-title' : undefined}
      aria-label={notice.title ? undefined : '공지'}
    >
      <button class="notice-close" type="button" aria-label="닫기">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
          <line x1="6" y1="6" x2="18" y2="18" />
          <line x1="18" y1="6" x2="6" y2="18" />
        </svg>
      </button>

      {notice.image && (
        <img class="notice-img" src={notice.image} alt={notice.imageAlt ?? ''} />
      )}

      {hasTextBlock && (
        <div class="notice-content">
          {notice.title && <h2 class="notice-title" id="notice-title">{notice.title}</h2>}
          {notice.body && <div class="notice-body">{notice.body}</div>}
          {hasButton && (
            <a class="notice-btn" href={notice.button!.url} target="_blank" rel="noopener noreferrer">
              {notice.button!.label}
            </a>
          )}
        </div>
      )}

      <label class="notice-dismiss">
        <input type="checkbox" class="notice-dismiss-check" />
        오늘 하루 보지 않기
      </label>
    </div>
  </div>
)}

<script>
  import { shouldShowNotice, dismissValue, dateKey } from '../lib/notice-visibility';

  const STORAGE_KEY = 'mm-notice-dismissed';
  const overlay = document.querySelector('.notice-overlay');

  if (overlay) {
    const card = overlay.querySelector('.notice-card');
    const closeBtn = overlay.querySelector('.notice-close');
    const check = overlay.querySelector('.notice-dismiss-check');
    const img = overlay.querySelector('.notice-img');
    const version = Number(overlay.getAttribute('data-version')) || 1;
    const today = dateKey(new Date());
    let lastFocused = null;

    // 이미지 로드 실패 시 이미지 영역 숨김
    if (img) img.addEventListener('error', () => { img.style.display = 'none'; });

    function read() {
      try { return localStorage.getItem(STORAGE_KEY); } catch (e) { return null; }
    }
    function persistDismiss() {
      try { localStorage.setItem(STORAGE_KEY, dismissValue(version, today)); } catch (e) {}
    }

    function open() {
      lastFocused = document.activeElement;
      overlay.setAttribute('aria-hidden', 'false');
      document.body.style.overflow = 'hidden';
      requestAnimationFrame(() => overlay.classList.add('is-open'));
      if (closeBtn && typeof closeBtn.focus === 'function') closeBtn.focus();
    }
    function close() {
      if (check && check.checked) persistDismiss();
      overlay.classList.remove('is-open');
      overlay.setAttribute('aria-hidden', 'true');
      document.body.style.overflow = '';
      if (lastFocused && typeof lastFocused.focus === 'function') lastFocused.focus();
    }

    if (shouldShowNotice(read(), version, today)) {
      open();
    }

    if (closeBtn) closeBtn.addEventListener('click', close);

    // 오버레이(바깥) 클릭 시 닫기 — 카드 내부 클릭은 무시
    overlay.addEventListener('click', (e) => {
      if (card && !card.contains(e.target)) close();
    });

    // ESC
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && overlay.classList.contains('is-open')) close();
    });
  }
</script>

<style>
  .notice-overlay {
    position: fixed;
    inset: 0;
    z-index: 200;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 20px;
    background: rgba(0, 0, 0, 0.55);
    opacity: 0;
    pointer-events: none;
    transition: opacity 0.2s ease;
  }
  .notice-overlay.is-open {
    opacity: 1;
    pointer-events: auto;
  }
  .notice-card {
    position: relative;
    width: calc(100vw - 40px);
    max-width: 380px;
    max-height: calc(100vh - 80px);
    overflow-y: auto;
    background: #fff;
    border-radius: 14px;
    box-shadow: 0 12px 32px rgba(0, 0, 0, 0.18), 0 2px 6px rgba(0, 0, 0, 0.08);
    transform: scale(0.92);
    transition: transform 0.34s cubic-bezier(0.34, 1.56, 0.64, 1);
  }
  .notice-overlay.is-open .notice-card {
    transform: scale(1);
  }
  .notice-img {
    width: 100%;
    border-radius: 14px 14px 0 0;
    object-fit: cover;
  }
  .notice-content {
    padding: 18px 20px 4px;
  }
  .notice-title {
    /* 한글 제목 가독성 위해 본문 폰트 사용 (헤딩 폰트엔 한글 글꼴 없음) */
    font-family: var(--font-body);
    font-weight: 600;
    font-size: 19px;
    color: var(--text);
    margin: 0 0 8px;
  }
  .notice-body {
    white-space: pre-line;
    font-size: 14px;
    line-height: 1.6;
    color: var(--text-mute);
  }
  .notice-btn {
    display: block;
    margin-top: 14px;
    padding: 11px 16px;
    background: var(--brand);
    color: #fff;
    text-align: center;
    border-radius: 8px;
    font-size: 14px;
    font-weight: 600;
    transition: opacity 0.15s;
  }
  .notice-btn:hover { opacity: 0.88; }
  .notice-dismiss {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-top: 14px;
    padding: 12px 20px;
    border-top: 1px solid var(--border);
    font-size: 13px;
    color: var(--text-mute);
    cursor: pointer;
  }
  .notice-dismiss-check { cursor: pointer; }
  .notice-close {
    position: absolute;
    top: 8px;
    right: 8px;
    width: 30px;
    height: 30px;
    border: none;
    background: rgba(0, 0, 0, 0.5);
    color: #fff;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    padding: 0;
    z-index: 1;
    transition: background 0.15s;
  }
  .notice-close:hover { background: rgba(0, 0, 0, 0.7); }
  .notice-close:focus-visible { outline: 2px solid var(--brand); outline-offset: 2px; }
  .notice-close svg { width: 14px; height: 14px; }

  @media (prefers-reduced-motion: reduce) {
    .notice-overlay, .notice-card { transition: none; }
  }
</style>
```

- [ ] **Step 2: 빌드로 컴포넌트 컴파일 확인** (아직 마운트 전이라 페이지 출력엔 없지만, import/타입 오류는 잡힘)

Run: `npm run build`
Expected: 빌드 성공 (에러 없음). NoticePopup은 아직 어디서도 import하지 않으므로 출력엔 미포함 — 다음 태스크에서 마운트.

- [ ] **Step 3: 커밋**

```bash
git add src/components/NoticePopup.astro
git commit -m "feat(notice): NoticePopup 컴포넌트 (마크업+스크립트+스타일)"
```

---

## Task 4: 홈에 마운트 + 빌드/수동 검증

**Files:**
- Modify: `src/pages/index.astro`

- [ ] **Step 1: `src/pages/index.astro` 수정** — import 추가 및 마운트

frontmatter import 블록에 두 줄 추가:
```astro
import NoticePopup from '../components/NoticePopup.astro';
import { notice } from '../lib/data';
```
`<BaseLayout>` 바로 다음 줄(헤더 위)에 마운트:
```astro
<BaseLayout>
  {notice.enabled && <NoticePopup />}
  <Header />
  <Hero />
  <InfoStrip />
  <Floors />
  <Gallery />
  <MapCTA />
  <Footer />
</BaseLayout>
```

- [ ] **Step 2: 단위 테스트 + 빌드 통과 확인**

Run: `npm test`
Expected: PASS (Task 1 테스트 그대로 통과)

Run: `npm run build`
Expected: 빌드 성공. `dist/index.html`에 `notice-overlay` 마크업 포함, `dist/menu/`(메뉴 페이지)엔 미포함.

- [ ] **Step 3: 로컬 수동 검증** (`npm run dev` → http://localhost:4321)

다음 체크리스트를 모두 확인:
- [ ] 홈 진입 시 팝업이 가운데에 부드럽게 뜬다 (배경 어두워짐).
- [ ] X 버튼 클릭 → 닫힌다.
- [ ] 배경(어두운 바깥) 클릭 → 닫힌다. 카드 내부 클릭은 안 닫힌다.
- [ ] ESC 키 → 닫힌다.
- [ ] 체크 없이 닫고 새로고침 → 다시 뜬다.
- [ ] "오늘 하루 보지 않기" 체크 후 닫고 새로고침 → 안 뜬다.
- [ ] (DevTools) Application → Local Storage에 `mm-notice-dismissed = "1:<오늘날짜>"` 저장 확인.
- [ ] `notice.yaml`의 `version`을 2로 바꾸고 새로고침 → (이전에 체크했어도) 다시 뜬다. 확인 후 1로 되돌린다.
- [ ] 메뉴 페이지(http://localhost:4321/menu) 진입 → 팝업 안 뜬다.
- [ ] `notice.yaml`에서 `enabled: false` → 새로고침 시 안 뜬다. 확인 후 true로 되돌린다.
- [ ] 브라우저 폭 360px(모바일)에서 카드가 화면 밖으로 넘치지 않는다.
- [ ] 버튼 클릭 → 인스타그램이 새 탭에서 열린다.

- [ ] **Step 4: 커밋**

```bash
git add src/pages/index.astro
git commit -m "feat(notice): 홈에 NoticePopup 마운트"
```

---

## Self-Review (작성자 점검 결과)

**Spec coverage:** 설계의 모든 요구 — 자유 조합 콘텐츠(Task 2 yaml + Task 3 조건부 렌더), '오늘 하루 보지 않기' 날짜+version(Task 1 로직 + Task 3 wiring), 홈 전용(Task 4 마운트 가드), X/바깥/ESC(Task 3), 접근성(Task 3 role/aria/focus), enabled 토글·빈 콘텐츠 가드(Task 3 `show`/Task 4 index 가드), prefers-reduced-motion(Task 3 CSS), 이미지 onerror(Task 3) — 모두 태스크에 매핑됨.

**Placeholder scan:** "TBD/TODO/적절히 처리" 등 없음. 모든 코드 블록 완전.

**Type consistency:** `Notice`/`NoticeButton` 필드(`enabled, version, image, imageAlt, title, body, button{label,url}`)가 data.ts·notice.yaml·컴포넌트에서 동일. 순수 함수명 `shouldShowNotice/dismissValue/dateKey`가 테스트·컴포넌트에서 일치. localStorage 키 `mm-notice-dismissed` 일관.

**검증 한계:** DOM/시각 동작은 자동 테스트가 아니라 Step 3 수동 체크리스트로 검증함(의도된 범위). 순수 로직만 Vitest로 자동 검증.
