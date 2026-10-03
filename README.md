# marketmay-site

market may 카페 공식 웹사이트.

## 개발

```bash
npm install
npm run dev      # http://localhost:4321
npm run build    # 정적 빌드 산출물 → dist/
npm run preview  # production 빌드 미리보기
```

## 콘텐츠 수정

- 가게 정보: `src/data/info.yaml` (이름, 주소, 영업시간, 전화, 인스타, 3층 구조, 카카오맵 키)
- 메뉴: `src/data/menu.yaml`
- 이미지: `public/images/` (같은 파일명으로 덮어쓰면 즉시 반영)

## 배포

`main` 브랜치 push 시 Cloudflare Pages가 자동 빌드/배포.

라이브: https://marketmay.com

## 홈페이지 메뉴 연결 정책

2026-10-03 사용자 결정: 홈페이지에 메뉴 보기를 상시 노출하지 않는 것은 운영상 의도입니다. 디자인 검토에서 이를 결함이나 개선 대상으로 취급하지 않습니다.

같은 요청으로 공지 팝업의 ‘브런치 메뉴 보기’ 연결도 제거했습니다. 후속 디자인 수정에서 홈페이지에 메뉴판 이동 버튼을 다시 추가하지 않습니다.

## 스택

- [Astro](https://astro.build/) — 정적 사이트 생성기
- Vanilla CSS (디자인 토큰: `src/styles/global.css`)
- Daum Roughmap (카카오맵 임베드, key는 `src/data/info.yaml`)
- Cloudflare Pages 호스팅
