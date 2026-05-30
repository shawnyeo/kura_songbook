# 쿠라's 노래책 — WEB_MIGRATION_SPEC

## 0. 문서 목적

이 문서는 쿠라's 노래책 Google Sheets MVP를 GitHub Pages 기반 웹사이트로 이전하기 위한 구현 명세서다.

이 문서의 목적:

- Google Sheets의 역할 구조를 웹 구조로 번역한다.
- Codex가 구현해야 할 기능 범위를 명확히 한다.
- outdated source와 최신 구현 상태가 충돌하지 않도록 한다.
- 웹다운 장점을 살리되, 기존 MVP에서 검증된 검색/필터/카드/랜덤 구조를 유지한다.

## 1. 구현 목표

v1 웹 이전 목표:

```text
Google Sheets MVP 최소 복제
  ↓
디자인 향상
  ↓
웹다운 UX 진화
```

필수 목표:

- GitHub Pages에서 작동하는 정적 웹사이트
- 사용자는 접속해서 검색만 한다
- 관리자는 로컬/깃으로 데이터를 관리한다
- 서버, 로그인, DB, 사용자 입력 저장은 v1에서 제외한다
- PC와 모바일 모두 자연스럽게 작동한다
- 기존 검색 논리와 카드 정보 위계를 유지한다

## 2. 비목표

v1에서 하지 않는다:

- Backend server
- Supabase/Firebase/DB 연동
- Login/account
- User submission form
- User editing
- Auto sync with Google Sheets
- Automatic sing count update
- Complex admin CMS
- Full lyrics hosting
- Google Sheets formula 1:1 reproduction

## 3. 기술 선택 원칙

기본 구현:

```text
plain HTML + CSS + JavaScript
```

이유:

- GitHub Pages와 가장 잘 맞는다.
- build 과정이 없다.
- Codex가 만든 결과를 사용자가 직접 확인하기 쉽다.
- 작은 팬페이지 검색 앱에는 충분하다.
- 배포/디버깅 부담이 낮다.

React/Vite 등 프레임워크는 허용 가능하지만 기본 선택이 아니다.

프레임워크 도입 조건:

- 반응형 UI/컴포넌트 관리가 명확히 쉬워진다.
- GitHub Pages 배포 절차가 안정적이다.
- 현재 plain JS보다 오류 가능성이 낮다.
- Codex가 trade-off를 먼저 설명하고 사용자 승인을 받는다.

Codex 규칙:

```text
Do not introduce React/Vite/build tools without explaining why.
Default to plain HTML/CSS/JS.
Ask before broad structural changes.
```

## 4. 권장 파일 구조

```text
kura-songbook/
├─ README.md
├─ index.html
├─ src/
│  ├─ app.js
│  └─ style.css
├─ data/
│  └─ songs.json
├─ assets/
│  └─ images/
├─ docs/
│  ├─ 00_PROJECT_STATE_v1_0.md
│  ├─ 01_WEB_MIGRATION_SPEC.md
│  ├─ 02_DESIGN_BRIEF.md
│  └─ 03_CURRENT_TASK.md
└─ source_archive/
   ├─ legacy_rulebook_v0_94.md
   ├─ legacy_sheet_architecture_spec.md
   ├─ legacy_ui_implementation_plan.md
   └─ sheet_snapshot_v1_0.xlsx
```

GitHub Pages는 루트의 `index.html`을 기본 진입점으로 사용한다.

## 5. Sheets → Web 역할 번역

| Google Sheets MVP | 웹 이식 |
|---|---|
| `쿠라's 노래책~!` / DB_RAW | `data/songs.json` |
| `QUERY_BUILDER` | `matchesSearch()`, `matchesFilters()` |
| `검색_ENGINE` | `filterSongs()` |
| `CARD_HELPER` | `renderSongCard()`, `renderSongRow()` |
| `RANDOM_HELPER` | `getRandomSong()` |
| `MAIN_PORTAL_HELPER` | `renderLandingRandom()` |
| `쿠글` | desktop/search result layout |
| `쿠글 모바일` | responsive/mobile layout |
| `TAXONOMY` | filter options generated from data |
| `TAXONOMY_확장용` | not exposed in v1 UI |

원칙:

- helper 시트를 그대로 복제하지 않는다.
- helper가 하던 역할을 JS 함수로 옮긴다.
- UI는 DB 표가 아니라 검색 결과 페이지처럼 만든다.

## 6. songs.json schema

곡 객체 필드:

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

필수 표시 필드:

- title
- translation
- artist
- artistKr
- language
- genre
- theme
- sourceNote
- videoUrl
- lyricsUrl
- singCount
- pick
- thumbnailUrl

검색/필터용 필드:

- genre1
- genre2
- situation
- target
- emotion
- media
- sourceType
- workTitle
- tags

## 7. xlsx/Google Sheets 변환 원칙

xlsx 또는 Google Sheets export는 데이터 입력 source다.

변환 과정:

```text
xlsx / csv
  ↓
normalize rows
  ↓
map Korean columns to JSON fields
  ↓
clean empty values
  ↓
convert singCount to number
  ↓
convert Pick to boolean
  ↓
generate thumbnailUrl from videoUrl
  ↓
write data/songs.json
```

주의:

- xlsx의 Google Sheets 전용 함수는 깨질 수 있다.
- V열 썸네일은 archive/reference로만 본다.
- 웹에서는 `videoUrl` 기반으로 thumbnailUrl을 재생성한다.
- schema source of truth는 이 문서다.

## 8. 검색 기능

자유검색 논리:

```text
단어 간 = AND
필드 간 = OR
```

검색 대상 필드:

- title
- translation
- artist
- artistKr
- language
- genre
- theme
- sourceNote
- workTitle
- tags

pseudo logic:

```js
function normalizeText(value) {
  return String(value ?? "")
    .toLowerCase()
    .normalize("NFKC")
    .trim();
}

function matchesSearch(song, query) {
  const terms = normalizeText(query).split(/\s+/).filter(Boolean);
  if (terms.length === 0) return true;

  const fields = [
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
  ].map(normalizeText);

  return terms.every(term =>
    fields.some(field => field.includes(term))
  );
}
```

## 9. 필터 기능

v1 필터 축:

- language
- genre
- situation
- target
- emotion
- sourceType
- media
- tags

기본 필터 추천:

- 언어
- 장르
- 감정/분위기
- 출처

고급 필터 추천:

- 상황
- 대상
- 매체
- 기타태그

필터 option 생성 원칙:

- `songs.json`에서 실제 존재하는 값 중심으로 생성한다.
- 결과가 없는 선택지를 기본 UI에 많이 노출하지 않는다.
- 상세 taxonomy는 자유검색과 고급 필터로 보완한다.

## 10. 결과 표시 — PC

PC는 리스트형 검색 결과를 기본으로 한다.

PC 표시 정보:

```text
곡: 제목 + 번역명
가수·언어: 가수 + 한국명 + 언어
장르·주제: 장르 + 핵심 주제
출처: sourceNote
액션: 영상 / 가사 / 횟수 / Pick
```

권장 구조:

```text
┌─────────────────────────────────────────────┐
│ ♪ 제목                         [🍵 Pick]    │
│ └ 번역명                                    │
│ 가수 └ 한국명 · 언어                         │
│ 장르 └ 주제                                  │
│ 출처                                        │
│ [▶ 영상] [📄 가사] [🎙 n회]                  │
└─────────────────────────────────────────────┘
```

PC는 Melon 같은 음악 검색 결과의 정보 위계를 참고하되, 디자인은 쿠라 노래책 테마로 재해석한다.

## 11. 결과 표시 — 모바일

모바일은 정보 축소가 핵심이다.

모바일 표시 정보:

- Pick
- 제목
- 번역명
- 가수 · 언어
- 장르
- 영상 버튼
- 가사 버튼

모바일에서 숨기거나 접는 정보:

- 긴 비고
- 부른 횟수
- 상세 상황/대상/감정
- 긴 작품 설명

권장 구조:

```text
┌──────────────────────┐
│ 🍵 Pick               │
│ 제목                  │
│ 번역명                │
│ 가수 · 언어            │
│ 장르                  │
│ [▶ 영상] [📄 가사]     │
└──────────────────────┘
```

## 12. 랜딩/메인 포털

웹에서는 Google 검색창처럼 단순한 도입부를 참고할 수 있다.

메인 포털 기본 구성:

- 로고/타이틀
- 간단한 설명
- 큰 검색창
- 추천 검색어/필터 칩
- 오늘의 랜덤 추천
- 전체 검색 결과로 전환

가능한 UX:

```text
처음 접속:
  메인 포털 + 큰 검색창

검색 입력:
  검색 결과 화면으로 자연스럽게 전환

모바일:
  같은 구조를 반응형으로 표시
```

시트처럼 PC/모바일 페이지를 완전히 분리할 필요는 없다.  
웹에서는 뷰포트 기반 반응형을 우선한다.

## 13. 랜덤 추천

필수 랜덤 기능:

1. 전체 DB 기반 랜덤
2. 현재 검색 결과 기반 랜덤

원칙:

- 랜덤은 후보 중 무작위다.
- Pick은 별도 표시 신호다.
- Pick 우선 랜덤은 나중에 별도 옵션으로 만든다.
- 웹에서는 버튼 클릭 후 랜덤 결과가 고정되어야 한다.

## 14. 영상/가사 버튼

영상 버튼:

- `videoUrl`이 있으면 활성화
- 새 탭에서 열기
- label: `▶ 영상`

가사 버튼:

- `lyricsUrl`이 있으면 활성화
- 새 탭에서 열기
- label: `📄 가사`
- 링크가 없으면 disabled 상태
- disabled label: `📄 가사 준비 중`

## 15. 썸네일

기본:

```js
function extractYoutubeId(url) {
  const match = String(url ?? "").match(
    /(?:v=|youtu\.be\/|embed\/|shorts\/)([A-Za-z0-9_-]{11})/
  );
  return match ? match[1] : "";
}

function getYoutubeThumbnail(url) {
  const id = extractYoutubeId(url);
  return id ? `https://img.youtube.com/vi/${id}/mqdefault.jpg` : "";
}
```

사용 원칙:

- 썸네일은 보조 시각 앵커다.
- 너무 크게 쓰지 않는다.
- 유튜브 썸네일이 곡 분위기와 안 맞을 수 있으므로 fallback 디자인을 둔다.
- 앨범커버처럼 완벽한 미적 요소로 기대하지 않는다.

## 16. 구현 단계

### Phase 1 — Skeleton

- index.html
- src/style.css
- src/app.js
- data/songs.json sample
- 데이터 load
- 기본 render

### Phase 2 — Search

- 자유검색
- 단어 AND / 필드 OR
- 결과 수 표시
- 결과 없음 메시지

### Phase 3 — Filters

- 필터 option 자동 생성
- 언어/장르/감정/출처 기본 필터
- 고급 필터 접기/펼치기

### Phase 4 — Cards

- PC 리스트형 카드
- 모바일 카드형
- 영상/가사 버튼
- Pick/횟수 표시

### Phase 5 — Random

- 전체 랜덤
- 현재 결과 랜덤
- 랜덤 카드 고정

### Phase 6 — Design polish

- 말차/핑크/아이보리 테마
- 핑크 해파리/벚꽃/잎사귀 asset
- 검색 페이지 감성
- 모바일 UX polish

### Phase 7 — Data pipeline

- xlsx/csv to songs.json 변환 스크립트
- 데이터 검수 루틴
- Git push 관리법

## 17. Codex 작업 규칙

Codex는 다음 규칙을 따른다.

- Before editing, summarize the plan.
- Make small changes.
- Do not rewrite the whole project without approval.
- Do not add backend.
- Do not add React/Vite unless approved.
- Do not infer schema from legacy files.
- Use `docs/` as source of truth.
- Treat `source_archive/` as historical reference.
- Keep mobile usability high.
- Keep the design cute but not childish.
