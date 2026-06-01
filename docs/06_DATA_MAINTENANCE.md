# 쿠라's 노래책 — DATA_MAINTENANCE

## 0. 목적

이 문서는 `data/songs.json`을 운영/수정하는 방법을 정리한다.

현재 `data/songs.json`은 Web v1.0의 공식 웹 DB다.

---

## 1. 기본 운영 흐름

```text
곡 정보 수정
↓
data/songs.json 변경
↓
검증
↓
로컬 확인
↓
commit
↓
push
↓
GitHub Pages 배포 확인
```

로컬 확인:

```bash
python -m http.server 8000
```

검증:

```bash
node --check src/app.js
node --check src/portal.js
```

향후:

```bash
python tools/validate_songs.py
```

---

## 2. 부른 횟수 증가

현재 수동 방식:

1. `data/songs.json` 열기
2. 해당 곡 검색
3. `singCount` 값을 +1
4. 저장
5. JSON parse 확인
6. commit/push

향후 도구 방식:

```bash
python tools/update_song.py --title "Lemon" --sing-count +1
```

동명이곡 가능성이 있으면 artist도 함께 지정한다.

```bash
python tools/update_song.py --title "Lemon" --artist "米津玄師" --sing-count +1
```

---

## 3. 영상 링크 교체

수동 방식:

```json
"videoUrl": "https://www.youtube.com/watch?v=<VIDEO_ID>",
"thumbnailUrl": "https://img.youtube.com/vi/<VIDEO_ID>/hqdefault.jpg"
```

playlist, `start_radio`, `si` 같은 파라미터는 제거한다.

향후 도구 방식:

```bash
python tools/update_song.py --title "호랑수월가" --video-url "https://www.youtube.com/watch?v=D92O5JT3E8A"
```

도구는 자동으로 `thumbnailUrl`을 갱신한다.

---

## 4. 가사 링크 추가/교체

수동 방식:

```json
"lyricsUrl": "https://..."
```

가사 전문을 저장하지 않는다.  
링크만 저장한다.

향후 도구 방식:

```bash
python tools/update_song.py --title "Lemon" --lyrics-url "https://..."
```

---

## 5. 검색 alias 추가

예: `별의 아이`는 있지만 `별의아이` 검색이 안 되는 경우.

```json
"tags": "별의아이 명탐정코난"
```

향후 도구 방식:

```bash
python tools/update_song.py --title "星の子" --add-tag "별의아이"
```

원칙:

- 검색 보강 목적만 넣는다.
- 너무 많은 taxonomy를 tags에 몰아넣지 않는다.

---

## 6. 신곡 추가

향후 흐름:

```text
GPT/수동 조사
↓
new_song.json 작성
↓
python tools/append_song.py tools/new_song.json --dry-run
↓
확인
↓
python tools/append_song.py tools/new_song.json
↓
validate
↓
commit/push
```

필수 확인:

- id 자동 생성
- title/artist 중복 경고
- videoUrl 정규화
- thumbnailUrl 생성
- JSON parse 성공

---

## 7. 검증 체크리스트

배포 전 확인:

```text
□ JSON parse 성공
□ id 중복 없음
□ title+artist 중복 없음
□ singCount 숫자
□ pick boolean
□ videoUrl/thumbnailUrl ID 일치
□ lyricsUrl은 비어있어도 허용
□ search.html 로드
□ 검색 정상
□ 랜덤 정상
□ 썸네일 클릭 정상
□ 가사 링크 정상
```

---

## 8. GitHub Pages 배포 확인

```text
commit
↓
push
↓
GitHub Actions / Pages build 확인
↓
배포 URL 접속
```

캐시 이슈가 있으면 URL에 query를 붙여 확인한다.

```text
https://.../kura_songbook/?v=check
```

또는 HTML의 asset query version을 올린다.

```html
src/style.css?v=beta-4
```

---

## 9. TODO / 검증 필요 데이터

### S0027 `星の子 / 별의 아이`

상태:

```text
source verification needed
```

현재 조치:

- `tags`에 `별의아이` alias 추가

남은 확인:

- 정확한 곡 정체
- 아티스트/작품 출처
- 공식/신뢰 가능한 videoUrl
- lyricsUrl

---

## 10. 운영 원칙

1. 불확실한 값은 추정하지 않는다.
2. 링크는 가능한 한 공식/신뢰 가능한 출처를 쓴다.
3. 영상 링크가 바뀌면 thumbnailUrl도 같이 바꾼다.
4. 곡을 추가할 때 모든 필드를 완벽히 채우려고 멈추지 않는다.
5. 최소 필드로 먼저 추가하고, 나중에 보강할 수 있다.
6. 방송 주인의 공간을 존중하고, 요청/제보 기능은 천천히 확장한다.
