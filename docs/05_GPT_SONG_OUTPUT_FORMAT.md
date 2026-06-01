# 05_GPT_SONG_OUTPUT_FORMAT

## 기본 원칙

GPT가 신규 곡 엔트리를 생성할 때는 JSON이 아니라 CSV master에 붙일 수 있는 표를 우선 출력한다.

```text
data/songs_master.csv = 운영 원본
data/songs.json       = build output
```

## 기본 출력 순서

1. 신규 엔트리 표
2. songIntro 후보
3. 검증 필요 메모

## 신규 엔트리 표 컬럼

신규 엔트리 표는 다음 컬럼을 사용한다.

```text
id
title
translation
artist
artistKr
language
genre
genre1
genre2
theme
situation
target
emotion
sourceNote
media
sourceType
workTitle
tags
videoUrl
lyricsUrl
pick
thumbnailUrl
```

주의:

- 신규 엔트리 기본 표에는 `singCount`를 넣지 않는다.
- 신규 곡의 부른 횟수는 운영값이며 기본 0으로 처리한다.
- `songIntro`는 표 바깥에 일반 문자열로 따로 출력한다.
- `id`는 비워도 된다.
- `thumbnailUrl`은 비워도 된다.
- `videoUrl`과 `lyricsUrl`은 없어도 된다.
- 불확실한 정보는 core field에 넣지 말고 검증 필요 메모로 분리한다.

## songIntro 출력

형식:

```text
songIntro 후보:
"..."
```

규칙:

- 40~80자 정도
- 시청자가 곡 느낌을 이해할 수 있게
- 과도한 수식어 금지
- 불확실한 정보를 단정하지 않기

## JSON 출력

JSON은 사용자가 명시적으로 요청할 때만 보조로 출력한다.
