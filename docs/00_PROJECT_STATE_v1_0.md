# 쿠라's 노래책 — PROJECT_STATE_v1_0

## 0. 문서 목적

이 문서는 쿠라's 노래책 Google Sheets MVP의 **현재 실제 구현 상태**를 기록하는 PM 기준 문서다.

이 문서는 과거 계획서가 아니다.  
이 문서는 GitHub Pages 이전을 위한 구현 명세서도 아니다.  
이 문서는 “현재 무엇이 실제로 존재하고, 무엇을 유지해야 하는가”를 동결하는 최신 상태 보고서다.

이 문서가 필요한 이유:

- 기존 rulebook, architecture spec, UI plan은 대부분 유효하지만 일부는 실제 구현보다 오래되었다.
- Google Sheets MVP는 구현 과정에서 DB 컬럼, helper 구조, UI 구조, 디자인 판단이 업데이트되었다.
- GitHub Pages 이전 시 Codex 또는 다른 작업자가 과거 문서와 실제 구현 상태를 혼동하지 않도록 해야 한다.
- 이후 문서가 서로 충돌할 경우, 현재 상태 판단은 이 문서를 우선한다.

## 1. 프로젝트 정의

쿠라's 노래책은 스트리머 “쿠라맛챠” 방송용 노래 검색/선택 UI다.

핵심 목적:

> 스트리머와 시청자가 방송 중 곡을 빠르게 찾고, 고르고, 영상/가사 링크로 이동할 수 있게 하는 방송용 노래 검색 페이지.

현재 버전은 Google Sheets 기반 MVP다.  
단순한 곡 목록이나 DB 표가 아니라, 다음 기능을 갖춘 검색 UI로 구현되어 있다.

- PC용 검색 페이지
- 모바일용 검색 페이지
- 메인 포털
- 원본 DB
- 검색 엔진
- QUERY_BUILDER
- CARD_HELPER
- RANDOM_HELPER
- MAIN_PORTAL_HELPER
- TAXONOMY
- 영상 링크
- 가사 링크
- 부른 횟수
- Pick 표시
- YouTube 썸네일 실험
- 보호/숨김/백업 기반 운영 구조

## 2. 명칭 기준

프로젝트 표기는 다음을 병행한다.

| 구분 | 표기 |
|---|---|
| 공식 한국어 표시명 | 쿠라's 노래책 |
| 영문/코드명 | Kura Songbook |
| 검색 UI 별칭 | Kuggle |
| GitHub repo 권장명 | kura-songbook |

Google Sheets 실제 탭명은 구현 과정에서 `쿠라's 노래책~!`, `쿠라s 노래책~!`처럼 표기가 혼재될 수 있다.  
문서와 코드에서는 가능한 한 내부 ID, JSON schema, 명시적 field name을 사용하고, 시트명 문자열에 강하게 의존하지 않는다.

## 3. 현재 MVP 레이어 구조

현재 Google Sheets MVP는 다음 레이어로 이해한다.

```text
DB_RAW
  ↓
검색_ENGINE / 검색_ENGINE_MOBILE
  ↓
QUERY_BUILDER / QUERY_BUILDER_MOBILE
  ↓
CARD_HELPER / CARD_HELPER_MOBILE
  ↓
쿠글 / 쿠글 모바일
  ↓
메인 포털
```

핵심 원칙:

- DB는 넓고 정확하게 유지한다.
- 검색 엔진과 helper는 숨기고 안정적으로 둔다.
- 사용자 UI는 짧고 예쁘고 빠르게 만든다.
- PC와 모바일은 정보량이 달라야 한다.
- 공개 화면은 DB 표가 아니라 검색 결과 페이지처럼 보여야 한다.

## 4. 현재 주요 시트 구성

| 시트명 | 역할 | 상태 |
|---|---|---|
| `쿠라's 노래책~!` / `쿠라s 노래책~!` | 원본 DB_RAW | 핵심 |
| `검색_ENGINE` | PC용 검색 엔진 | 구현됨 |
| `검색_ENGINE_MOBILE` | 모바일용 검색 엔진 | 구현됨 |
| `QUERY_BUILDER` | PC 검색 조건 생성 helper | 구현됨 |
| `QUERY_BUILDER_MOBILE` | 모바일 검색 조건 생성 helper | 구현됨 |
| `CARD_HELPER` | PC 결과 표시용 helper | 구현됨 |
| `CARD_HELPER_MOBILE` | 모바일 카드 표시용 helper | 구현됨 |
| `RANDOM_HELPER` | PC 랜덤 추천 helper | 구현됨 |
| `RANDOM_HELPER_MOBILE` | 모바일 랜덤 추천 helper | 구현됨 |
| `MAIN_PORTAL_HELPER` | 메인 랜덤 추천 카드용 helper | 구현됨 |
| `TAXONOMY` | 현재 DB에 실제 존재하는 값 기반 드롭다운 목록 | 구현됨 |
| `TAXONOMY_확장용` | 향후 확장용 taxonomy 보관 | 구현됨 |
| `메인` | 포털/허브 화면 | 구현됨 |
| `쿠글` | PC 공개 검색 UI | 구현됨 |
| `쿠글 모바일` | 모바일 공개 검색 UI | 구현됨 |
| 백업/보호/숨김 시트 | 복구 및 내부 엔진 보호 | 구현됨 |

## 5. 현재 DB 컬럼 A:V

현재 원본 DB는 다음 컬럼 구조를 기준으로 한다.

| 열 | 컬럼명 | 용도 |
|---|---|---|
| A | 제목 | 표시/검색 |
| B | 번역명 | 표시/검색 |
| C | 가수 | 표시/검색 |
| D | 한국명 | 표시/검색 |
| E | 언어 | 필터/표시 |
| F | 장르 | 표시 |
| G | 장르1 | 검색/필터용 원자값 |
| H | 장르2 | 검색/필터용 원자값 |
| I | 설명 / 주제표시 | 표시/검색 |
| J | 상황 | 필터용 원자값 |
| K | 대상 | 필터용 원자값 |
| L | 감정 | 필터용 원자값 |
| M | 비고 | 표시/검색 |
| N | 매체 | 메타/필터 |
| O | 출처유형 | 메타/필터 |
| P | 작품명 | 메타/검색 |
| Q | 기타태그 | 메타/필터 |
| R | 영상 링크 | 버튼/썸네일 생성 |
| S | 가사 링크 | 버튼 |
| T | 부른 횟수 | 운영/표시 |
| U | Pick / 쿠라 픽 | 쿠라 Pick 표시 |
| V | 썸네일 | Google Sheets용 YouTube 썸네일 IMAGE/URL 실험 |

주의:

- V열은 웹 이식의 source of truth가 아니다.
- 웹에서는 `videoUrl`에서 YouTube ID를 추출해 `thumbnailUrl`을 재생성하는 것을 기본으로 한다.
- U열 Pick은 아직 시범 운영 성격이지만, 웹에서는 boolean으로 정규화한다.

## 6. 웹용 JSON schema 권장

GitHub Pages 이전 시 원본 DB는 `data/songs.json`으로 변환한다.

권장 곡 객체:

```json
{
  "id": "S0001",
  "title": "",
  "translation": "",
  "artist": "",
  "artistKr": "",
  "language": "",
  "genre": "",
  "genre1": "",
  "genre2": "",
  "theme": "",
  "situation": "",
  "target": "",
  "emotion": "",
  "sourceNote": "",
  "media": "",
  "sourceType": "",
  "workTitle": "",
  "tags": "",
  "videoUrl": "",
  "lyricsUrl": "",
  "singCount": 0,
  "pick": false,
  "thumbnailUrl": ""
}
```

필드명 기준:

- `sourceNote`는 DB의 `비고`에 해당한다.
- `theme`은 DB의 `설명/주제표시`에 해당한다.
- `thumbnailUrl`은 가능하면 변환 과정 또는 클라이언트 JS에서 `videoUrl` 기반으로 생성한다.

## 7. 현재 검색 구조

현재 자유검색은 다음 논리를 사용한다.

```text
검색어를 공백 기준으로 분리한다.
각 단어는 반드시 매칭되어야 한다.
각 단어는 여러 필드 중 하나에만 포함되어도 된다.

즉:
단어 간 = AND
필드 간 = OR
```

예:

```text
요네즈 발라드
```

의 의미:

```text
“요네즈”가 제목/번역명/가수/한국명/언어/장르/주제/비고 중 어딘가에 포함되고
AND
“발라드”도 제목/번역명/가수/한국명/언어/장르/주제/비고 중 어딘가에 포함되는 곡
```

웹 이식 시 pseudo logic:

```js
const terms = normalize(query).split(/\s+/).filter(Boolean);

const searchableFields = [
  song.title,
  song.translation,
  song.artist,
  song.artistKr,
  song.language,
  song.genre,
  song.theme,
  song.sourceNote,
  song.workTitle,
  song.tags
];

const matchesSearch = terms.every(term =>
  searchableFields.some(field =>
    normalize(field).includes(term)
  )
);
```

## 8. 현재 필터 구조

현재 필터 축은 다음을 사용한다.

| 필터 | 기준 |
|---|---|
| 언어 | `language` |
| 장르 | `genre1`, `genre2` |
| 상황 | `situation` |
| 대상 | `target` |
| 감정 | `emotion` |
| 출처유형 | `sourceType` 또는 `sourceNote` |
| 매체 | `media` 또는 `sourceNote` |
| 기타태그 | `tags` 또는 `sourceNote` |

현재 중요한 판단:

- 미래 확장용 taxonomy를 사용자 드롭다운에 그대로 노출하지 않는다.
- `TAXONOMY`는 현재 DB에 실제 존재하는 값 중심으로 구성한다.
- `TAXONOMY_확장용`은 관리용 후보 pool로 분리한다.
- 사용자가 눌렀는데 결과 0개가 자주 나오는 필터는 UX를 망친다.
- 자유검색이 있으므로 모든 taxonomy를 공개 필터로 노출할 필요는 없다.

## 9. Helper 구조와 철학

Google Sheets MVP에서 helper는 단순 부가 기능이 아니라 구조의 핵심이다.

핵심 역할:

| Sheets helper | 역할 | 웹 이식 개념 |
|---|---|---|
| `QUERY_BUILDER` | 검색 조건 생성 | `matchesSearch`, `matchesFilters` |
| `검색_ENGINE` | DB에서 조건 결과 추출 | `filterSongs` |
| `CARD_HELPER` | 표시용 텍스트 재구성 | `renderSongRow`, `renderSongCard` |
| `RANDOM_HELPER` | 랜덤 추천 | `getRandomSong` |
| `MAIN_PORTAL_HELPER` | 메인 랜덤 카드용 데이터 구성 | `buildLandingRandomCard` |

웹에서는 시트 helper를 1:1로 복제하지 않는다.  
역할만 JS 함수/컴포넌트로 이식한다.

## 10. PC 검색 UI 현재 상태

PC UI 시트명: `쿠글`

PC는 정보량을 어느 정도 허용한다.  
현재 PC 결과 표시는 멜론/벅스식 리스트형 검색 결과에 가깝다.

PC 결과에 표시하는 정보:

- 곡
- 가수·언어
- 장르·주제
- 출처
- 영상
- 가사
- 횟수
- Pick

정보 위계:

```text
♪ 제목
└ 번역명

가수
└ 한국명 · 언어

장르
└ 핵심 주제/분위기
```

디자인 판단:

- DB표처럼 보이면 안 된다.
- 완전한 카드보다 리스트형 카드가 더 실용적이다.
- 세로선은 최소화한다.
- 행별 교차색은 약하게 둔다.
- 제목은 가장 크게/굵게 둔다.
- 가수는 두 번째 위계다.
- 장르/주제/출처는 보조 정보다.
- 영상/가사/횟수/Pick은 액션/상태 칼럼이다.

## 11. 모바일 검색 UI 현재 상태

모바일 UI 시트명: `쿠글 모바일`

모바일은 Google Sheets 모바일 UX 한계가 크다.  
현재 판단은 “꾸미기보다 삭제”다.

모바일에서 유지하는 정보:

- Pick
- 제목
- 번역명
- 가수
- 한국명/언어
- 장르
- 영상 버튼
- 가사 버튼

모바일에서 축소/삭제한 정보:

- 긴 비고
- 출처 상세
- 부른 횟수
- 대상
- 상세 주제

웹 이전 시에는 시트의 PC/모바일 분리를 그대로 복제하기보다, 반응형 UI와 뷰포트 기반 layout을 우선 고려한다.

## 12. 메인 포털 현재 상태

메인 포털 시트명: `메인`

역할:

- 사용자가 처음 들어오는 입구
- PC/모바일 검색 페이지로 이동
- 오늘의 랜덤 추천 제공
- 짧은 사용 안내 제공

현재 메인 포털 요소:

- 배경 일러스트
- PC 검색 버튼
- 모바일 검색 버튼
- 사용법 안내
- 랜덤 추천 카드
- 영상 보기 버튼
- 가사 보기 버튼

메인 랜덤 추천 카드 구조:

```text
┌──────────────────────────────┐
│ 🎲 오늘의 랜덤 추천           │
├──────────────┬───────────────┤
│ 썸네일        │ 제목섬         │
│              │ 가수섬         │
├──────────────┴───────────────┤
│ 설명섬                       │
├──────────────┬───────────────┤
│ ▶ 영상 보기   │ 📄 가사 보기   │
└──────────────┴───────────────┘
```

메인 카드에서 제외한 정보:

- 대상
- 부른 횟수
- 긴 비고

메인 카드에서 유지한 정보:

- 제목
- 번역명
- 가수
- 한국명/언어
- 장르
- 주제
- 영상 링크
- 가사 링크
- 썸네일

## 13. 랜덤 추천 현재 상태

현재 랜덤 기능은 두 축으로 이해한다.

| 랜덤 | 기준 |
|---|---|
| 전체 랜덤 | 전체 DB에서 1곡 추천 |
| 현재 결과 랜덤 | 현재 검색/필터 결과 안에서 1곡 추천 |

현재 원칙:

- 공백 행은 랜덤 대상에서 제외한다.
- “조건에 맞는 곡이 없습니다.”는 랜덤 대상에서 제외한다.
- “검색 필터 조건을 넣어주세요.”는 랜덤 대상에서 제외한다.
- 수식형 랜덤이므로 시트 재계산 시 결과가 바뀐다.
- 웹에서는 버튼 클릭 시 랜덤 결과가 고정되게 만들 수 있다.

Pick과 랜덤은 개념이 다르다.

- 랜덤 = 조건 후보 중 무작위
- Pick = 쿠라가 좋아하거나 고른 곡이라는 별도 신호

Pick 우선 랜덤은 v1 기본 기능이 아니라 별도 옵션으로 분리할 수 있다.

## 14. 영상/가사 링크 현재 상태

영상 링크:

- DB의 R열 `영상 링크`를 사용한다.
- 가능하면 실제 YouTube URL이다.
- 웹에서는 `▶ 영상` 버튼으로 표시한다.

가사 링크:

- DB의 S열 `가사 링크`를 사용한다.
- 웹에서는 `📄 가사` 버튼으로 표시한다.
- 링크가 없을 경우 버튼은 “준비 중” 상태로 비활성화한다.

가사 기능은 장기적으로 중요하다.  
외국어 곡의 원문, 발음, 의미/번역 접근성을 높이는 것이 목적이다.

## 15. 썸네일 현재 상태

현재 V열은 Google Sheets에서 YouTube 썸네일을 바로 표시하기 위한 IMAGE 함수/URL 실험에 가깝다.

웹 이식 원칙:

- V열을 그대로 신뢰하지 않는다.
- 기본은 `videoUrl`에서 YouTube ID를 추출해 `thumbnailUrl`을 재생성한다.
- `thumbnailUrl`이 명시적으로 존재하면 fallback으로 사용할 수 있다.
- 유튜브 썸네일은 앨범 커버가 아니므로 너무 크게 쓰면 어색할 수 있다.
- 썸네일은 보조 시각 앵커로 사용한다.

## 16. 디자인 철학

현재 디자인 키워드:

- 말차
- 아이보리
- 연핑크
- 핑크 해파리
- 벚꽃
- 잎사귀
- 일본 개인 팬사이트
- 애니 굿즈샵
- 카드 컬렉션 감성
- 니코동/보카로 감성 약간
- 유희왕 카드 감성 약간
- 귀엽지만 유아틱하지 않게
- 아기자기하지만 조잡하지 않게
- 팬페이지지만 검색 페이지로서 실용적이게
- Google Sheets에서 검증된 검색 페이지 감성 유지
- SaaS 대시보드처럼 보이지 않게
- Spotify/Discord/Notion처럼 보이지 않게

색상 계열:

| 용도 | 색상 | 예시 |
|---|---|---|
| 메인 말차 | 진한 말차 초록 | `#6F8F5E` |
| 헤더 말차 | 부드러운 말차 초록 | `#8BA872` |
| 배경 | 따뜻한 아이보리 | `#FCFCF8` |
| 보조 배경 | 연한 말차 우유색 | `#F4F8EF` |
| 포인트 | 연핑크 | `#EBCFDA` |
| 진한 텍스트 | 녹갈색 | `#2F5130` |
| 보조 텍스트 | 회색 섞인 녹색 | `#4F5F4F` |

디자인 기준:

- 단순히 “핑크 애니 UI”가 아니다.
- 너무 유아틱하거나 과한 하트/반짝이 UI는 피한다.
- 너무 기업형 SaaS 대시보드처럼 보여도 안 된다.
- 메인 도입부는 Google 검색창처럼 단순하고 직관적인 구조를 참고할 수 있다.
- 검색 결과 화면은 Melon 같은 음악 검색 결과 구조를 참고할 수 있다.
- 단, 최종 결과는 쿠라맛챠/말차/해파리 팬페이지 감성으로 재해석한다.

## 17. 현재 구현 완료로 보는 기능

- 원본 DB 시트 구성
- PC 검색 UI
- 모바일 검색 UI
- 메인 포털
- 자유검색
- 다중 단어 AND 검색
- 필터 검색
- TAXONOMY와 TAXONOMY_확장용 분리
- PC/모바일 검색 엔진 분리
- PC/모바일 카드 helper
- PC/모바일 랜덤 helper
- MAIN_PORTAL_HELPER
- 영상 링크 버튼
- 가사 링크 버튼
- 부른 횟수 표시
- Pick 표시
- 메인 랜덤 추천 카드
- YouTube 썸네일 URL/IMAGE 실험
- 격자선 제거 기반 디자인 개선
- 내부 시트 보호/숨김/백업 운영

## 18. 미완성 또는 향후 과제

데이터:

- 가사 링크 채우기
- 일부 영상 링크 정규화
- Pick 데이터 검수
- 부른 횟수 장기 로그화
- DB 컬럼명 최종 고정
- xlsx/Google Sheets → JSON 변환 루틴 확정

기능:

- 랜덤 추천 결과 고정 버튼
- 필터 초기화 버튼
- 신청용 텍스트 복사 버튼
- 부른 횟수 자동 증가
- LOG 시트 연동
- Apps Script 기반 UI 버튼
- GitHub Pages 이전
- 반응형 웹 UI
- 검색 결과 공유 링크
- 고급 필터 접기/펼치기

UI:

- 모바일 UX 고도화
- 메인 랜덤 카드 정교화
- 앨범아트/썸네일 디자인 일관성
- 가사_INDEX 또는 가사 링크 허브 완성
- 공개 권한/편집 권한 문제 제거

## 19. Google Sheets MVP 한계

Google Sheets MVP의 한계:

- 반응형 UI가 아니다.
- 모바일 UX가 좋지 않다.
- 병합셀/이미지/링크 클릭이 불안정하다.
- 보호된 셀과 편집 가능한 검색창을 동시에 운영하기 어렵다.
- Viewer 권한만으로는 검색창 입력이 어렵다.
- Editor 공개는 수식/서식 파손 위험이 있다.
- 수식형 랜덤은 재계산 시 바뀐다.
- 둥근 카드/그림자/버튼 같은 웹 UI를 정확히 구현하기 어렵다.

이 한계 때문에 다음 단계는 GitHub Pages 이전이다.

## 20. GitHub Pages 이전 시 유지할 핵심

반드시 유지:

- 최신 DB A:V 구조의 의미
- 자유검색: 단어 간 AND, 필드 간 OR
- 필터: 언어/장르/상황/대상/감정/출처유형/매체/기타태그
- PC 결과 정보 위계
- 모바일 정보 축소 원칙
- 영상/가사 버튼
- 가사 링크 없을 때 “준비 중” 비활성 상태
- 전체 랜덤
- 현재 검색 결과 랜덤
- Pick 표시
- 썸네일 보조 앵커
- 메인 포털
- 말차/핑크 해파리/아이보리 디자인 테마

반드시 피할 것:

- Google Sheets 수식 1:1 복제
- helper 시트 구조의 기계적 복제
- 과거 문서의 outdated 컬럼 구조 사용
- DB 표처럼 보이는 웹 UI
- SaaS 대시보드 느낌
- 과도한 React/백엔드/DB 도입
- 사용자 로그인/회원 기능
- 사용자 직접 편집 기능

## 21. GitHub Pages 이전 기본 방향

v1 웹 이전은 다음을 목표로 한다.

```text
최소 복제
  ↓
디자인 향상
  ↓
웹다운 UX 진화
```

초기 구현은 plain HTML/CSS/JS를 기본으로 한다.  
React 등 프레임워크는 모바일/PC UX, 유지보수, 배포 안정성 면에서 명확한 이점이 있을 때만 도입한다.  
Codex는 프레임워크를 임의로 선택하지 말고, 선택 이유와 trade-off를 먼저 설명해야 한다.

권장 웹 구조:

```text
index.html
src/
  app.js
  style.css
data/
  songs.json
assets/
  images/
docs/
  00_PROJECT_STATE_v1_0.md
  01_WEB_MIGRATION_SPEC.md
  02_DESIGN_BRIEF.md
  03_CURRENT_TASK.md
source_archive/
  legacy_rulebook_v0_94.md
  legacy_sheet_architecture_spec.md
  legacy_ui_implementation_plan.md
  sheet_snapshot_v1_0.xlsx
```

## 22. 문서 우선순위

Codex 또는 다른 작업자는 다음 우선순위를 따른다.

1. `docs/00_PROJECT_STATE_v1_0.md`
2. `docs/01_WEB_MIGRATION_SPEC.md`
3. `docs/02_DESIGN_BRIEF.md`
4. `docs/03_CURRENT_TASK.md`
5. `source_archive/` 내부 과거 문서
6. xlsx snapshot

규칙:

- `docs/`와 `source_archive/`가 충돌하면 `docs/`를 우선한다.
- xlsx는 snapshot/archive다.
- xlsx에서 직접 프로젝트 규칙을 추론하지 않는다.
- Google Sheets 전용 수식은 웹에서 역할만 이식한다.
- 최신 JSON schema는 `01_WEB_MIGRATION_SPEC.md`를 따른다.

## 23. 한 줄 결론

쿠라's 노래책 v1.0은 Google Sheets 안에서 검색 UI, 카드 표시, 랜덤 추천, 메인 포털까지 검증한 MVP다.  
다음 단계는 이 검증된 구조를 GitHub Pages 기반 정적 웹앱으로 이전해, 공개 접근성·모바일 UX·권한 문제를 해결하는 것이다.
