# 04_SONG_SCHEMA_JSON

## 현재 데이터 기준

현재 운영 기준은 CSV master + JSON build output 구조다.

```text
data/songs_master.csv = 사람이 수정하는 운영 원본
data/songs.json       = public web DB / build output
```

이 문서는 이름은 JSON schema지만, 실제로는 CSV master와 JSON build output의 공통 필드 의미를 설명한다.

## 필드 순서

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
singCount
pick
thumbnailUrl
songIntro
```

## CSV master 규칙

- `songs_master.csv`는 UTF-8-SIG로 저장한다.
- 신규 곡의 `id`는 비워도 된다.
- `singCount`가 비어 있으면 0으로 처리할 수 있다.
- `pick`은 boolean-like 값을 허용한다.
- `videoUrl`, `lyricsUrl`, `thumbnailUrl`, `songIntro`, `tags`, `sourceNote`는 비어 있어도 된다.
- `thumbnailUrl`은 `videoUrl`에서 자동 생성할 수 있다.

## JSON build output 규칙

- `songs.json`은 public site가 fetch하는 배포용 DB다.
- JSON은 `ensure_ascii=False`, `indent=2`로 저장한다.
- `singCount`는 숫자여야 한다.
- `pick`은 boolean이어야 한다.
- public site는 이 JSON을 읽어서 검색 결과를 렌더링한다.

## 검증 범위

도구가 검증하는 것:

- id 중복
- 필수 최소 필드 누락
- singCount 숫자 변환
- pick boolean 변환
- YouTube ID 추출 가능 여부
- thumbnailUrl/videoUrl ID 불일치
- 유사 중복 후보

도구가 검증하지 않는 것:

- 실제 존재하는 곡인지
- 영상이 공식 영상인지
- 가사 링크가 정확한지
- 작품 출처가 맞는지
