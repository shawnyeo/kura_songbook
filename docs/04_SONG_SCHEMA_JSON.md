# 쿠라's 노래책 — SONG_SCHEMA_JSON

## 0. 목적

이 문서는 `data/songs.json`의 공식 schema를 정의한다.

현재 `data/songs.json`은 GitHub Pages Web v1.0의 공식 웹 DB다.

---

## 1. 곡 객체 기본 구조

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
  "thumbnailUrl": "",
  "songIntro": ""
}
```

---

## 2. 필수 / 권장 / 선택 필드

### 2.1 필수 필드

곡 추가 시 최소한 있어야 하는 필드.

| 필드 | 설명 |
|---|---|
| `id` | 자동 생성 권장. `S0034` 형식 |
| `title` | 원제 또는 대표 제목 |
| `artist` | 원 가수/아티스트 |
| `language` | 한국어, 일본어, 영어 등 |
| `singCount` | 숫자. 기본 0 |
| `pick` | boolean. 기본 false |

### 2.2 권장 필드

있으면 검색/표시 품질이 좋아지는 필드.

| 필드 | 설명 |
|---|---|
| `translation` | 한국어 번역명/통용명 |
| `artistKr` | 가수 한국명 |
| `genre` | 사람이 보는 장르 문자열 |
| `genre1` | 필터용 핵심 장르 |
| `genre2` | 보조 장르 |
| `theme` | 기존 설명/주제표시 |
| `emotion` | 대표 감정 |
| `sourceType` | OST, 보카로, J-POP 등 |
| `workTitle` | 작품명 |
| `songIntro` | GPT가 생성한 1줄 설명 |
| `videoUrl` | 영상 링크 |
| `thumbnailUrl` | YouTube 썸네일 URL |
| `tags` | alias/search helper |

### 2.3 선택 필드

나중에 채워도 되는 필드.

| 필드 | 설명 |
|---|---|
| `lyricsUrl` | 가사 링크 |
| `situation` | 상황 taxonomy |
| `target` | 대상 taxonomy |
| `sourceNote` | 비고/출처 설명 |
| `media` | 드라마, 애니, 영화 등 |

---

## 3. 빈 값 규칙

모르는 값은 추정하지 않는다.

허용:

```json
"translation": "",
"lyricsUrl": "",
"genre2": "",
"sourceNote": ""
```

금지:

```json
"lyricsUrl": "나중에 찾기"
"videoUrl": "아마 공식"
"sourceNote": "확실하지 않음?"
```

불확실한 항목은 별도 TODO에 기록한다.

---

## 4. `songIntro` 규칙

`songIntro`는 검색 결과 카드에서 사람이 읽기 쉽게 보여줄 1줄 설명이다.

목적:

- 곡 제목만 보고 모르는 사람이 분위기를 파악
- 스트리머/시청자가 곡을 고르기 쉽게 함
- taxonomy 단어를 자연어로 풀어줌

길이:

```text
한국어 기준 35~70자 권장
최대 90자 이내
```

좋은 예:

```text
애니 영화의 여운과 재회의 그리움을 잔잔하게 담은 일본어 팝 발라드.
```

나쁜 예:

```text
좋은 노래.
발라드 / 사랑 / 이별 / 그리움.
아마 슬픈 느낌의 노래로 추정됨.
```

원칙:

1. 과장하지 않는다.
2. 불확실한 사실을 단정하지 않는다.
3. 장르/감정/상황을 자연스럽게 녹인다.
4. “명곡”, “레전드” 같은 평가형 표현은 자제한다.
5. 스트리머가 부른 사실은 확인되지 않으면 쓰지 않는다.
6. 저작권 있는 가사 문구를 직접 인용하지 않는다.

---

## 5. YouTube URL 규칙

`videoUrl`은 가능하면 canonical watch URL을 사용한다.

권장:

```text
https://www.youtube.com/watch?v=<VIDEO_ID>
```

피함:

```text
https://www.youtube.com/watch?v=<VIDEO_ID>&list=...
https://youtu.be/<VIDEO_ID>?si=...
```

`thumbnailUrl`은 다음 형식을 권장한다.

```text
https://img.youtube.com/vi/<VIDEO_ID>/hqdefault.jpg
```

기존 `mqdefault.jpg`도 허용하되, 새로 생성할 때는 `hqdefault.jpg`를 기본으로 한다.

---

## 6. `tags` 규칙

`tags`는 검색 보강용 alias 필드다.

사용 예:

- 띄어쓰기 없는 검색어
- 한국어 통용명
- 오타/약칭
- 작품명 별칭

예:

```json
"tags": "별의아이 코난 명탐정코난"
```

`tags`에 taxonomy 전체를 무리하게 넣지 않는다.  
표시용 칩과 검색 alias는 구분한다.

---

## 7. `singCount` 규칙

- 숫자만 사용
- 모르면 0
- 방송에서 부른 것이 확인되면 +1
- 나중에 `singHistory`를 도입할 수 있으나 v1.0에서는 `singCount`만 사용

---

## 8. 향후 확장 후보

### 방송 클립

향후 스트리머가 실제로 부른 클립 링크를 모을 수 있다.

후보 필드:

```json
"performanceClips": [
  {
    "title": "",
    "url": "",
    "date": "",
    "note": ""
  }
]
```

v1.0에서는 사용하지 않는다.

### source verification

불확실한 곡은 다음 식으로 관리할 수 있다.

```json
"verificationStatus": "needs_source_check"
```

단, 현재 v1.0 schema에는 아직 도입하지 않는다.  
대신 TODO 문서에 기록한다.
