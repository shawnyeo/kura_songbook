# 쿠라's 노래책 — GPT_SONG_OUTPUT_FORMAT

## 0. 목적

이 문서는 GPT에게 새 곡 정보를 조사/정리하게 할 때 사용할 출력 포맷을 정의한다.

앞으로 GPT는 Google Sheets 행이 아니라 `data/songs.json`에 들어갈 JSON 객체를 출력한다.

---

## 1. 기본 요청 문장

GPT에게 곡 추가를 요청할 때는 다음처럼 요청한다.

```text
쿠라's 노래책 songs.json 추가용으로 아래 곡을 조사해서 JSON 객체 1개로 만들어줘.
불확실한 값은 추정하지 말고 빈 문자열로 둬.
공식/신뢰 가능한 영상 링크가 불확실하면 videoUrl은 비워둬.
songIntro는 35~70자 정도의 자연스러운 한국어 1문장으로 써줘.
```

---

## 2. 출력 포맷

```json
{
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

`id`는 appender가 자동 생성하는 것을 기본으로 한다.  
수동 작성이 필요한 경우만 `id`를 포함한다.

---

## 3. 필드 작성 규칙

### title

- 원제 우선
- 한국곡이면 한국어 제목
- 일본곡이면 일본어 원제 우선
- 통용 한국어 제목은 `translation` 또는 `tags`에 추가

### translation

- 한국어 번역명/통용명
- 없으면 빈 문자열

### artist / artistKr

- `artist`: 원 표기
- `artistKr`: 한국어 표기
- 모르면 빈 문자열

### language

예:

```text
한국어
일본어
영어
중국어
```

### genre / genre1 / genre2

- `genre`: 사람이 볼 문자열
- `genre1`: 대표 장르
- `genre2`: 보조 장르

예:

```json
"genre": "팝 / 발라드",
"genre1": "팝",
"genre2": "발라드"
```

### theme / situation / target / emotion

Google Sheets taxonomy의 흐름을 유지한다.

예:

```json
"theme": "사랑 / 이별 / 그리움",
"situation": "사랑",
"target": "이별",
"emotion": "그리움"
```

모르면 빈 문자열로 둔다.

### sourceNote / media / sourceType / workTitle

예:

```json
"sourceNote": "애니 영화 OST 너의 이름은",
"media": "애니 영화",
"sourceType": "OST",
"workTitle": "너의 이름은"
```

작품/출처가 불확실하면 단정하지 않는다.

### tags

검색 보강용.

예:

```json
"tags": "별의아이 명탐정코난 코난"
```

사용처:

- 띄어쓰기 없는 검색
- 한국어 통용명
- 약칭
- 별칭
- 오타 대응

### videoUrl

공식 또는 신뢰 가능한 영상 링크만 사용한다.

불확실하면 빈 문자열.

### lyricsUrl

가사 사이트 링크.  
없으면 빈 문자열.

### thumbnailUrl

`videoUrl`이 있으면 다음 형식으로 생성한다.

```text
https://img.youtube.com/vi/<VIDEO_ID>/hqdefault.jpg
```

모르면 빈 문자열.

### songIntro

1문장 한국어 설명.

규칙:

- 35~70자 권장
- 최대 90자
- 장르/감정/출처를 자연스럽게 녹임
- 가사 직접 인용 금지
- 과장된 평가 금지
- 불확실한 사실 단정 금지

좋은 예:

```text
애니 영화의 여운과 재회의 그리움을 잔잔하게 담은 일본어 팝 발라드.
```

---

## 4. 불확실성 표시

GPT가 확실히 모르는 값은 다음처럼 처리한다.

```json
"videoUrl": "",
"sourceNote": "",
"workTitle": "",
"tags": "후보검색어"
```

그리고 JSON 아래에 별도 메모를 붙인다.

```text
검증 필요:
- 공식 영상 링크 확인 필요
- 작품 출처 확인 필요
```

단, appender 입력 파일에는 JSON만 넣는 것을 권장한다.  
검증 메모는 별도 TODO 문서나 작업 노트에 기록한다.

---

## 5. 출력 예시

```json
{
  "title": "Lemon",
  "translation": "레몬",
  "artist": "米津玄師",
  "artistKr": "요네즈 켄시",
  "language": "일본어",
  "genre": "팝 / 발라드",
  "genre1": "팝",
  "genre2": "발라드",
  "theme": "이별 / 상실 / 그리움",
  "situation": "이별",
  "target": "상실",
  "emotion": "그리움",
  "sourceNote": "드라마 OST 언내추럴",
  "media": "드라마",
  "sourceType": "OST",
  "workTitle": "언내추럴",
  "tags": "레몬 요네즈켄시 요네즈",
  "videoUrl": "https://www.youtube.com/watch?v=SX_ViT4Ra7k",
  "lyricsUrl": "",
  "singCount": 0,
  "pick": false,
  "thumbnailUrl": "https://img.youtube.com/vi/SX_ViT4Ra7k/hqdefault.jpg",
  "songIntro": "상실과 그리움의 정서를 담담하게 풀어낸 일본어 팝 발라드."
}
```

---

## 6. 금지 사항

- 불확실한 링크를 공식처럼 쓰지 않는다.
- 가사 전문을 수집/저장하지 않는다.
- 저작권 있는 이미지/로고를 직접 저장하지 않는다.
- taxonomy를 지나치게 많이 넣지 않는다.
- 모든 필드를 억지로 채우지 않는다.
- “쿠라가 불렀다”는 사실을 확인 없이 쓰지 않는다.
