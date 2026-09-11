# 마켓메이 QR 메뉴

- 공개 주소 / QR 내용: `https://marketmay.com/menu`
- 기준: 2026-09-11 사용자가 제공한 새 음료 메뉴판 `IMG_3566.jpeg`.
- 메뉴 페이지와 인쇄용 PDF는 `src/data/drinks.json`을 함께 사용한다.
- 원본에서 한 번만 표시된 가격은 같은 묶음의 가격으로 적용했다: 에이드 6,700원, 과일차 6,500원, 로얄/아이스 밀크티 6,700원.
- 기존 `menu.yaml`의 과거 판매 단가와 비공개 `_menu.astro`는 새 음료 메뉴의 출처가 아니다.
- 기존 초안 PR #5의 브런치 갤러리는 별도 작업으로 유지한다.

## 메뉴 수정

JSON의 이름, 가격, 설명, `signature`, `hotOnly`를 수정한다. 페이지 주소는 유지해야 이미 인쇄한 QR을 계속 사용할 수 있다. 웹페이지 변경 후 종이 메뉴도 아래 명령으로 다시 생성한다.

## 인쇄물 재생성

Python 패키지 `reportlab`, `qrcode`, `Pillow`와 나눔고딕 TTF Regular/Bold가 필요하다. 폰트는 Google Fonts의 `google/fonts` 저장소 `ofl/nanumgothic/`에서 제공된다(SIL Open Font License).

```sh
python scripts/create-print-menu.py --font-dir /path/to/fonts --output /path/to/output
```

폰트 파일명: `NanumGothic-Regular.ttf`, `NanumGothic-Bold.ttf`.

- A4 세로 210 × 297 mm, 2페이지. 1장은 커피와 추가 옵션, 2장은 티·에이드·밀크티·기타 음료. 브런치는 포함하지 않는다.
- 두 페이지 각각에 QR 배치, 전체 크기 약 27.5 mm. 사방 4모듈 여백, Q 오류 정정, 흑백 벡터.
- 흰 QR 여백을 자르거나 QR 위에 로고를 겹치지 않는다. 인쇄 시 해당 종이에 실제 크기(100%)로 출력한다.

## 확인

- 기존 테스트 7개와 Astro 정적 빌드 통과.
- 생성 HTML에서 메뉴 32개, 가격, 세 가지 HOT ONLY 표시, 카테고리 링크, 이미지 경로 및 리필 조건 확인.
- A4 2페이지 PDF를 이미지로 렌더링해 레이아웃 검토하고, 32개 메뉴와 가격의 텍스트 보존 확인.
- 렌더링 이미지의 QR을 OpenCV로 해독해 공개 주소와 일치하는지 확인. 실물 종이 또는 실제 휴대폰 카메라로 시험한 것은 아님.
- 모바일 반응형 CSS 적용. 별도 모바일 브라우저 렌더링 검증은 진행하지 않음.
