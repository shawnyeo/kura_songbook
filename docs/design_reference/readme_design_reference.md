# Design Reference — Kura Songbook

이 폴더는 쿠라's 노래책 GitHub Pages 이전 작업의 시각 레퍼런스를 보관한다.

이 이미지들은 그대로 복제할 레이아웃이 아니라, 다음 요소를 Codex와 작업자가 이해하기 위한 참고자료다.

* 디자인 무드
* 정보 위계
* 검색 UX 방향
* PC/모바일 차이
* 말차/해파리/벚꽃 팬페이지 감성
* Google Sheets MVP에서 검증한 사용성

## Reference Files

### `ref_01_sheet_main_portal.png`

Google Sheets MVP의 메인 포털 화면이다.

참고할 것:

* 말차, 아이보리, 연핑크, 핑크 해파리, 벚꽃, 잎사귀 감성
* PC/모바일 검색 입구
* 사용 방법 안내
* 오늘의 랜덤 추천 카드
* 팬페이지다운 첫인상

주의:

* spreadsheet cell layout을 그대로 복제하지 않는다.
* 배경 일러스트를 그대로 꽉 채우면 웹에서는 가독성이 떨어질 수 있다.
* 웹에서는 장식을 가장자리/hero background로 재해석한다.

### `ref_02_sheet_mobile_search.png`

Google Sheets MVP의 모바일 검색 화면이다.

참고할 것:

* 모바일에서는 정보량을 줄인다.
* 한 곡은 세로 카드처럼 읽힌다.
* 필터는 2열 또는 접이식 구조가 적합하다.
* 영상/가사 버튼은 크고 명확해야 한다.

주의:

* spreadsheet dropdown layout을 그대로 복제하지 않는다.
* 웹에서는 chip, accordion, bottom sheet 같은 mobile-native 구조를 우선 고려한다.

### `ref_03_sheet_pc_results.png`

Google Sheets MVP의 PC 검색 결과 화면이다.

참고할 것:

* 검색창 + 필터 + 결과 리스트 + 우측 랜덤/도움말 구조
* 제목/번역명, 가수/언어, 장르/주제, 출처, 영상/가사/횟수/Pick의 정보 위계
* 방송 중 빠르게 훑을 수 있는 리스트형 결과

주의:

* raw table/grid처럼 보이면 안 된다.
* 웹에서는 row card/list card로 재해석한다.
* 컬럼 구조는 유지하되, 시각적으로는 카드형 결과처럼 만든다.

### `ref_04_generated_desktop_mockup_v1.png`

AI로 생성한 16:9 desktop web mockup이다.

이 파일은 현재 웹 디자인의 primary mood reference로 사용한다.

참고할 것:

* 큰 검색창 중심의 landing/search portal
* Melon-like music results structure
* 우측 sidebar의 random recommendation/search help/card collection
* 말차 초록, warm ivory, sakura pink 색상 조합
* rounded cards, soft shadows, decorative but clean fanpage mood
* pink jellyfish mascot, sakura, leaves, bubbles, matcha tea motifs

주의:

* 텍스트, 곡명, 수치, 영어 문구는 그대로 사용하지 않는다.
* 실제 데이터는 `data/songs.json`을 따른다.
* 장식은 검색성과 가독성을 방해하지 않아야 한다.
* 이 이미지는 PC 방향 레퍼런스이며, 모바일은 별도 responsive layout이 필요하다.

### `ref_05_matcha_jellyfish_background.png`

말차/벚꽃/핑크 해파리 배경 일러스트 레퍼런스다.

참고할 것:

* 사이트 정체성
* hero 또는 page edge decoration
* soft fanpage atmosphere

주의:

* 중요한 텍스트 위에 그대로 깔지 않는다.
* 검은/투명 영역이 생기지 않도록 웹 배경 처리에 주의한다.
* 모바일에서는 장식을 줄인다.

### `ref_06_melon_search_results.png`

Melon 검색 결과 페이지 레퍼런스다.

참고할 것:

* 음악 검색 결과의 빠른 훑기 구조
* 곡명 중심 정보 위계
* 검색 결과 + sidebar 구성

주의:

* Melon branding을 복제하지 않는다.
* exact layout을 복제하지 않는다.
* 구조적 영감만 사용한다.

## Design Interpretation Rules

Codex and contributors must follow these rules:

1. Do not copy spreadsheet cells directly.
2. Do not copy Melon or Google branding directly.
3. Use the references to understand mood, hierarchy, and feature intent.
4. Preserve the current Google Sheets MVP behavior.
5. Make the website web-native, responsive, and easier to use than the sheet.
6. Keep the design cute but not childish.
7. Avoid SaaS dashboard styling.
8. Avoid raw spreadsheet/table styling.
9. Use decorations around content, not over important content.
10. Mobile usability has priority over decoration.
