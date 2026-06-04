# 공지/이벤트 팝업 (Notice Popup) 설계

- 작성일: 2026-06-04
- 브랜치: `feat/notice-popup`
- 상태: 승인됨 (사용자 구두 승인 "진행해")

## 목적

홈(메인) 진입 시 공지·이벤트를 알리는 팝업을 띄운다. 사용자는 X/바깥 클릭/ESC로 닫을 수 있고, "오늘 하루 보지 않기" 체크 시 당일 자정까지 재노출되지 않는다. 팝업 내용은 사장님이 코드를 건드리지 않고 YAML 한 파일만 수정해 바꿀 수 있어야 한다 (기존 `info.yaml`/`menu.yaml` 철학과 동일).

## 확정된 결정 (브레인스토밍 결과)

1. **내용**: 이미지·제목·본문·버튼을 자유 조합 (전부 선택값). 포스터만/글만/혼합 모두 가능.
2. **재노출**: "오늘 하루 보지 않기" 체크박스 (`localStorage`, 날짜 기반).
3. **노출 위치**: 홈(`index.astro`)에서만. 메뉴 페이지엔 노출하지 않음.
4. **방식**: 전용 `notice.yaml` + `NoticePopup.astro` 컴포넌트 (방식 A).

## 데이터 스키마 — `src/data/notice.yaml`

사장님이 수정하는 단일 파일.

```yaml
enabled: true              # false면 팝업이 아예 렌더되지 않음 (껐다 켜기)
version: 1                 # 내용 교체 후 +1 하면 '오늘 하루 보지 않기' 누른 사람에게도 재노출
image: /images/notice.jpg  # 포스터 (없으면 "" → 이미지 영역 생략)
imageAlt: "6월 이벤트 안내"  # 이미지 대체 텍스트 (접근성)
title: "6월 휴무 안내"       # 제목 (없으면 "" → 생략)
body: |                    # 본문, 여러 줄 가능 (없으면 "" → 생략)
  매주 월요일은 정기 휴무입니다.
  6/9(월)은 임시 휴무예요.
button:                    # 버튼 (불필요하면 키 전체 삭제 또는 비움)
  label: "인스타그램에서 소식 보기"
  url: https://www.instagram.com/market.may_/
```

### `src/lib/data.ts` 추가 타입

```ts
export interface NoticeButton { label: string; url: string; }
export interface Notice {
  enabled: boolean;
  version?: number;        // 기본 1
  image?: string;
  imageAlt?: string;
  title?: string;
  body?: string;
  button?: NoticeButton | null;
}
export const notice: Notice = load<Notice>('notice.yaml');
```

## 컴포넌트 — `src/components/NoticePopup.astro`

기존 `MenuLightbox.astro` 패턴을 따른다: 자체 완결형(마크업 + `<script is:inline>` + scoped `<style>`).

### 렌더 가드 (빌드 타임)

- `index.astro`에서 `{notice.enabled && <NoticePopup />}` 로 마운트.
- 추가로 컴포넌트 내부에서 표시할 내용(image/title/body 중 하나라도)이 전혀 없으면 렌더하지 않는다 → 빈 팝업 방지.
- `enabled: false`거나 내용이 비면 HTML/스크립트가 출력되지 않음 (성능·안전).

### 마크업 구조

```
<div class="notice-overlay" aria-hidden="true">      ← 어두운 배경(dim) + 가운데 정렬
  <div class="notice-card" role="dialog" aria-modal="true" aria-labelledby="notice-title">
    <button class="notice-close" aria-label="닫기"> ✕ (SVG) </button>
    [<img> 이미지 — image 있을 때만]
    [<h2 id="notice-title"> 제목 — title 있을 때만]
    [<div class="notice-body"> 본문 — body 있을 때만, 줄바꿈 보존]
    [<a class="notice-btn" target="_blank" rel="noopener"> 버튼 — button 있을 때만]
    <label class="notice-dismiss"><input type="checkbox"> 오늘 하루 보지 않기</label>
  </div>
</div>
```

`id="notice-title"`은 title이 있을 때만 부여하고, 없으면 `aria-label`로 대체.

## 동작 (클라이언트 스크립트)

- **노출 판단** (`DOMContentLoaded` 직후):
  - `localStorage`에서 키 `mm-notice-dismissed` 읽음. 저장 포맷: `"{version}:{YYYY-MM-DD}"`.
  - 저장된 `version`이 현재 `version`과 같고 저장 날짜가 오늘이면 → 표시하지 않음.
  - 그 외(다른 날짜 / 다른 version / 값 없음) → 표시.
  - 날짜는 브라우저 로컬 기준 `new Date()`로 `YYYY-MM-DD` 생성.
- **열기**: `is-open` 클래스 추가, fade+scale 애니메이션(기존 `MenuLightbox`의 cubic-bezier 재사용), 배경 스크롤 잠금(`body { overflow: hidden }`), 포커스를 X 버튼으로 이동.
- **닫기** (X 버튼 · 오버레이 바깥 클릭 · ESC):
  - 체크박스가 체크돼 있으면 → `localStorage`에 `"{version}:{today}"` 저장.
  - 체크 안 돼 있으면 → 저장하지 않음(다음 진입 시 다시 노출).
  - 애니메이션 후 `is-open` 제거, 배경 스크롤 잠금 해제, 포커스 원위치 복원.
- 카드 내부 클릭은 닫힘으로 전파되지 않음(버튼/체크박스 조작 가능).

## 접근성

- `role="dialog"` + `aria-modal="true"` (진짜 모달).
- title 존재 시 `aria-labelledby="notice-title"`, 없으면 카드에 `aria-label="공지"`.
- 열릴 때 포커스 → X 버튼, 닫힐 때 직전 포커스 요소로 복원 (`MenuLightbox`와 동일 수준).
- ESC로 닫기. 키보드만으로 닫기·버튼 이동 가능.
- 닫기 버튼 `focus-visible` 아웃라인 `var(--brand)`.

## 스타일 (디자인 토큰 사용)

- 오버레이: `position: fixed; inset: 0; background: rgba(0,0,0,0.55);` flex 가운데 정렬, `z-index` 헤더보다 위(예: 200; `MenuLightbox`가 100).
- 카드: `background:#fff; border-radius:14px;` 그림자(`MenuLightbox` 그림자 톤), `max-width: 380px; width: calc(100vw - 40px);` 모바일 대응, 본문 길면 카드 내부 스크롤(`max-height: calc(100vh - 80px); overflow:auto`).
- 제목: **본문 폰트(`var(--font-body)`, Pretendard) + 굵게(600)** 사용. 사유: 헤딩 폰트 스택(`Cormorant Garamond → serif`)에는 한글 글꼴이 없어 한글 제목이 생성 serif로 어색하게 폴백됨. 공지 제목은 대부분 한글이므로 가독성·일관성 우선.
- 버튼: `background: var(--brand); color:#fff; border-radius:8px;` 풀폭, hover 시 약간 어둡게.
- 체크박스 라벨: `color: var(--text-mute); font-size:13px;` 상단 `border-top: 1px solid var(--border)` 구분선.
- 등장 애니메이션: opacity 0→1 + `transform: scale(0.92)→scale(1)`, `MenuLightbox`의 `cubic-bezier(0.34,1.56,0.64,1)` 재사용.
- `prefers-reduced-motion` 존중: 모션 줄이기 설정 시 애니메이션 최소화.

## 변경 파일 요약

- **신규**
  - `src/data/notice.yaml`
  - `src/components/NoticePopup.astro`
  - `public/images/notice.jpg` (예시 포스터 — 나중에 교체용 플레이스홀더)
- **수정**
  - `src/lib/data.ts` — `Notice` 타입 + `notice` export 추가
  - `src/pages/index.astro` — import 및 `{notice.enabled && <NoticePopup />}` 마운트

## 엣지 케이스

- 내용 전무(image/title/body 모두 빈값) → 렌더 안 함.
- 이미지 경로가 잘못됨 → 이미지 로드 실패 시 `onerror`로 이미지 영역을 숨김. 제목/본문/버튼은 정상 표시.
- `localStorage` 미사용(시크릿 모드/차단) → 예외 무시, 매번 노출(기능 저하만, 오류 없음).
- JS 비활성 → 팝업은 숨김 시작이므로 노출되지 않음(허용 가능한 동작).
- `version` 누락 시 기본 1로 취급.

## 검증 (Verification)

- `npm install` 후 `npm run dev` → `http://localhost:4321` 에서:
  - 홈 진입 시 팝업 노출 확인.
  - X / 바깥 클릭 / ESC 닫힘 확인.
  - "오늘 하루 보지 않기" 체크 후 닫고 새로고침 → 재노출 안 됨 확인.
  - 체크 없이 닫고 새로고침 → 재노출 됨 확인.
  - `version` +1 후 재노출 확인.
  - 메뉴 페이지(`/menu`) 진입 시 미노출 확인.
  - `enabled: false` 시 미노출 확인.
- `npm run build` 성공(타입/빌드 에러 없음) 확인.
- 모바일 폭(360px)에서 카드가 화면을 넘지 않는지 확인.

## 비범위 (YAGNI — 이번에 안 함)

- 여러 개의 팝업/슬라이드 캐러셀.
- 관리자 UI(파일 직접 편집으로 충분).
- 예약 노출(시작/종료 일시 자동화) — 추후 `startsAt`/`endsAt` 필드로 확장 가능하나 이번 범위 외.
