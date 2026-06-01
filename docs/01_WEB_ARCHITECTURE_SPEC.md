# 쿠라's 노래책 — WEB_ARCHITECTURE_SPEC

## 0. 문서 목적

이 문서는 GitHub Pages Web v1.0 기준의 실제 웹 아키텍처를 설명한다.

과거 `WEB_MIGRATION_SPEC`는 Google Sheets MVP를 웹으로 이전하기 위한 계획서였다.  
이 문서는 이전 완료 후의 현재 구조를 기준으로 한다.

---

## 1. 전체 구조

```text
index.html
  ↓ 검색/전체 곡 보기
search.html
  ↓
src/app.js
  ↓
data/songs.json
```

파일 역할:

| 파일 | 역할 |
|---|---|
| `index.html` | 메인 포털 |
| `search.html` | 검색 결과 페이지 |
| `src/portal.js` | 포털 검색 입력을 query string으로 변환 |
| `src/app.js` | 곡 데이터 로드, 검색, 필터, 정렬, 랜덤, 카드 렌더링 |
| `src/style.css` | 포털/검색 페이지 공통 스타일 |
| `data/songs.json` | 공식 웹 DB |
| `assets/` | 배경/에셋 |

---

## 2. 페이지 흐름

### 2.1 포털 검색

사용자가 `index.html`에서 검색어를 입력하면:

```text
검색어 입력
↓
src/portal.js
↓
search.html?q=<encoded query>
```

빈 검색어 또는 전체 곡 보기:

```text
search.html
```

### 2.2 검색 페이지 로딩

`search.html`은 `src/app.js`를 로드한다.

`app.js`는 다음을 수행한다.

1. `data/songs.json` fetch
2. URLSearchParams에서 `q` 읽기
3. 검색 input에 query 반영
4. 결과 필터링
5. 카드 렌더링
6. 필터/정렬/랜덤 이벤트 연결

---

## 3. 데이터 흐름

```text
data/songs.json
  ↓ fetch
state.songs
  ↓ matchesSearch / matchesFilters / compareSongs
visibleSongs
  ↓ renderSongCard
#song-list
```

랜덤:

```text
state.songs 또는 visibleSongs
  ↓ getRandomSong
renderRandomSong
  ↓
#random-result
```

---

## 4. 검색 구조

검색 로직:

```text
검색어를 공백 기준으로 분리
단어 간 AND
필드 간 OR
```

검색 대상 필드:

- title
- translation
- artist
- artistKr
- language
- genre
- theme
- songIntro
- sourceNote
- workTitle
- tags

향후 개선 후보:

- 공백 무시 검색
- 가나/가타카나 보정
- alias 필드 추가
- 점수 기반 ranking
- 초성 검색

---

## 5. 필터 구조

현재 공개 필터:

| 필터 | 기준 필드 |
|---|---|
| 언어 | `language` |
| 장르 | `genre1`, `genre2` |
| 분위기 | `emotion` |
| Pick 먼저 | `pick` sort modifier |

원칙:

- 실제 데이터에 존재하는 값만 옵션으로 노출한다.
- 상세 taxonomy를 전부 사용자에게 노출하지 않는다.
- 자유검색이 있으므로 필터는 최소한으로 유지한다.

---

## 6. 카드 렌더링 구조

`renderSongCard(song)`은 다음 정보를 출력한다.

- 썸네일
- 제목
- 번역명
- Pick badge
- 가수/한국명/언어
- songIntro
- compact meta line
- chip 최대 3개
- 가사 버튼
- 부른 횟수

영상 링크는 별도 큰 버튼이 아니라 썸네일 클릭으로 처리한다.

---

## 7. 랜덤 추천 구조

랜덤 추천은 두 종류다.

| 버튼 | 대상 |
|---|---|
| 전체 곡 랜덤 | `state.songs` |
| 현재 결과 랜덤 | `getVisibleSongs()` |

랜덤 카드도 썸네일, 제목, 가수, songIntro, 가사 링크를 표시한다.

---

## 8. GitHub Pages 제약

현재 사이트는 정적 사이트다.

하지 않는 것:

- backend
- login
- DB server
- Supabase/Firebase
- Google Sheets auto sync
- 사용자 입력 저장

로컬 확인:

```bash
python -m http.server 8000
```

GitHub Pages 확인:

```text
https://<owner>.github.io/<repo>/
```

---

## 9. 배포 흐름

```text
파일 수정
↓
로컬 확인
↓
node --check src/app.js
node --check src/portal.js
↓
commit
↓
push
↓
GitHub Actions / Pages build 확인
↓
배포 URL 확인
```

---

## 10. 향후 아키텍처 확장

### v1.0.1

- 로컬 JSON 관리 도구
- validate/update/append script

### v1.1

- 태그 collapse/expand
- 포털 랜덤 미리보기
- favicon / OG image

### v1.2

- 모바일 전용 재정리
- Pick collection
- 검색 고도화

### v2.0

- 피드백/제보 폼
- 로컬 관리자 페이지
- YouTube iframe modal
- 방송 클립 링크 모음
