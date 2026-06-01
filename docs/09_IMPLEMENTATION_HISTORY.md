# 쿠라's 노래책 — IMPLEMENTATION_HISTORY

## 0. 목적

이 문서는 Google Sheets MVP에서 Web v1.0까지 어떤 계획이 어떻게 구현되었는지 정리한다.

기존 계획 문서를 하나씩 계속 source of truth로 두기보다, 완료된 흐름을 이 문서에 통합 기록한다.

---

## 1. Google Sheets MVP

초기 목표:

```text
스트리머와 시청자가 방송 중 곡을 빠르게 찾고 고를 수 있는 Google Sheets 기반 노래 검색 UI
```

구현된 주요 구조:

- DB_RAW
- 검색_ENGINE
- QUERY_BUILDER
- CARD_HELPER
- RANDOM_HELPER
- MAIN_PORTAL_HELPER
- TAXONOMY
- PC 검색 UI
- 모바일 검색 UI
- 메인 포털
- 영상/가사 링크
- 부른 횟수
- Pick 표시

핵심 학습:

- DB와 공개 UI는 분리해야 한다.
- 검색 결과는 표가 아니라 카드/검색 페이지처럼 보여야 한다.
- taxonomy는 통제된 확장형이어야 한다.
- 모바일은 PC와 같은 정보량을 보여주면 안 된다.
- 방송용 UI는 예쁨보다 빠른 검색성이 중요하다.

---

## 2. Web Migration

초기 웹 이전 원칙:

- GitHub Pages
- Static site
- Plain HTML/CSS/JS
- `data/songs.json`
- React/Vite/Backend 없음
- Google Sheets 자동 동기화 없음

초기 skeleton:

- `index.html`
- `src/style.css`
- `src/app.js`
- sample `data/songs.json`

이후 구현:

- xlsx → JSON 변환기
- 전체 33곡 변환
- 검색 로직
- 필터
- 랜덤 추천
- songIntro
- 썸네일
- 디자인 에셋
- GitHub Pages 배포

---

## 3. Portal/Search 분리

초기에는 `index.html` 한 페이지에서 포털과 검색 결과를 함께 처리하려 했다.

문제:

- 포털과 검색 결과가 서로 레이아웃을 방해함
- hero가 과도하게 커지거나, 검색 페이지가 포털처럼 보임
- 상태 전환이 꼼수처럼 됨

최종 결정:

```text
index.html = 메인 포털
search.html = 검색 결과 페이지
```

결과:

- 포털은 감성/브랜딩 담당
- 검색 페이지는 실사용 담당
- URL query로 검색어 전달
- `portal.js`와 `app.js` 역할 분리

---

## 4. Design Iteration

주요 방향:

- 말차/아이보리/연핑크
- 핑크 해파리
- 벚꽃/잎사귀
- 일본 팬사이트 분위기
- 검색 결과는 음악 리스트형 카드

중요한 판단:

- 시안 100% 재현보다 방송용 검색성을 우선
- hero 과다 확대는 피함
- 영상은 버튼보다 썸네일 클릭
- YouTube iframe modal은 보류

---

## 5. Data Issues

수정된 데이터 예:

- 영화 속에 나오는 주인공처럼 videoUrl 교체
- グリズリーに襲われたら♡ videoUrl 교체
- 호랑수월가 videoUrl 교체
- Gift videoUrl 교체
- `별의아이` 검색 alias 추가

검증 필요:

- `S0027 星の子 / 별의 아이`

---

## 6. Current Conclusion

Web v1.0은 공개 가능한 수준으로 완료되었다.

다음 성공 기준은 디자인 추가가 아니라 운영 가능성이다.

```text
곡 추가가 쉬운가?
부른 횟수 수정이 쉬운가?
링크 교체가 쉬운가?
GPT가 같은 포맷으로 곡을 뽑아줄 수 있는가?
검증이 자동화되어 있는가?
```

따라서 다음 단계는 문서/도구/운영 체계다.
