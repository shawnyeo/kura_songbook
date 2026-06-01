# 쿠라's 노래책 — LOCAL_ADMIN_GUI_SPEC_v0_1

## 0. 목적

이 문서는 쿠라's 노래책 Web v1.0 이후의 로컬 관리자 GUI 도구를 구현하기 위한 명세다.

목표는 복잡한 CMS가 아니라, 운영자가 `data/songs_master.csv`를 편하게 수정하고, 변경점을 확인한 뒤 `data/songs.json`으로 반영하는 로컬 전용 관리 도구를 만드는 것이다.

---

## 1. 배경

현재 사이트 구조:

```text
index.html          # 메인 포털
search.html         # 검색 결과 페이지
src/portal.js       # 포털 검색 이동
src/app.js          # 검색/필터/정렬/랜덤/카드 렌더링
src/style.css       # 사이트 스타일
data/songs.json     # 웹사이트가 fetch하는 배포용 DB
```

운영 방향:

```text
data/songs_master.csv = 사람이 수정하는 관리자용 원본
data/songs.json       = 웹사이트가 읽는 배포용 DB
```

Google Sheets/xlsx는 legacy snapshot/import source다.

---

## 2. 왜 GUI인가

운영자는 개발자용 CLI보다 눈으로 보고 수정하는 방식을 선호한다.

원하는 흐름:

```text
로컬 관리자 GUI 실행
↓
곡 검색/선택
↓
폼에서 수정 또는 새 곡 추가
↓
변경점 미리보기
↓
적용
↓
songs_master.csv 저장
↓
songs.json 재생성
↓
로컬 사이트 확인
↓
commit/push
```

PowerShell 명령을 많이 외우지 않아도 되게 한다.

---

## 3. 기술 선택

### 기본 선택: Python 표준 라이브러리 기반 local web admin

파일:

```text
tools/admin_server.py
tools/run_admin_gui.bat
tools/admin_static/admin.css
tools/admin_static/admin.js   # 필요할 때만
data/songs_master.csv
data/backups/
```

이유:

- 외부 패키지 설치 없음
- Windows에서 실행 가능
- 브라우저 UI라 CSV보다 보기 좋게 만들 수 있음
- Python이 로컬 파일 저장 가능
- GitHub Pages 사이트와 분리됨
- production UI를 건드리지 않음

금지:

- Flask/FastAPI 설치
- npm/Vite/React 설치
- production `index.html`, `search.html`, `src/app.js`, `src/style.css` 수정
- data를 자동 push
- 외부 서버화

---

## 4. 실행 방식

운영자는 가능하면 더블클릭으로 실행한다.

```text
tools/run_admin_gui.bat
```

bat 파일 동작:

```bat
@echo off
cd /d %~dp0\..
python tools\admin_server.py
pause
```

서버는 자동으로 브라우저를 연다.

```text
http://localhost:8765
```

---

## 5. 기본 화면

관리자 GUI는 다음 화면/기능을 가진다.

### 5.1 Dashboard

표시:

- 전체 곡 수
- 마지막 JSON 빌드 시간 또는 파일 수정 시간
- 경고 수
- 빠른 버튼:
  - 곡 목록 보기
  - 새 곡 추가
  - 변경 미리보기
  - 적용/빌드
  - 검증만 실행
  - 백업 폴더 안내

### 5.2 Song List

기능:

- 제목 검색
- 가수 검색
- 언어/장르 간단 필터
- id, title, translation, artist, language, singCount 표시
- 클릭하면 Edit 화면으로 이동

### 5.3 Edit Song

기존 곡 수정 폼.

주요 필드:

- id
- title
- translation
- artist
- artistKr
- language
- genre
- genre1
- genre2
- theme
- situation
- target
- emotion
- sourceNote
- media
- sourceType
- workTitle
- tags
- videoUrl
- lyricsUrl
- singCount
- pick
- thumbnailUrl
- songIntro

편의 버튼:

- `부른 횟수 +1`
- `thumbnailUrl 재생성`
- `YouTube URL 정규화`
- `저장 전 미리보기`

### 5.4 Add Song

새 곡 추가 폼.

규칙:

- id는 비워둘 수 있음
- id가 비어 있으면 적용 시 자동 생성
- title, artist, language는 최소 필드
- videoUrl/lyricsUrl/songIntro는 없어도 저장 가능
- pick 기본 false
- singCount 기본 0

### 5.5 Preview Changes

적용 전 변경점 요약.

출력 예:

```text
[추가 예정]
- S0034 새 곡 / 새 가수

[수정 예정]
- S0029 Lemon
  singCount: 1 → 2

[자동 정리]
- videoUrl canonicalized
- thumbnailUrl regenerated

[경고]
- songIntro 비어 있음
- videoUrl 없음
- 유사 제목 후보 있음
```

### 5.6 Apply / Build

적용 시:

1. `data/songs_master.csv` 백업
2. `data/songs.json` 백업
3. CSV 저장
4. CSV를 JSON으로 변환
5. JSON 저장
6. 검증 실행
7. 결과 요약 출력

---

## 6. 데이터 원칙

### 6.1 Master/Build 구조

```text
songs_master.csv = 편집 원본
songs.json       = 빌드 결과
```

Admin GUI는 두 파일을 비교하고 동기화한다.

### 6.2 최초 실행

`data/songs_master.csv`가 없으면:

1. `data/songs.json`에서 CSV를 생성할지 물어본다.
2. 생성 후 관리자 화면으로 이동한다.

### 6.3 CSV 인코딩

CSV는 Excel 호환성을 위해 `utf-8-sig`로 읽고 쓴다.

### 6.4 JSON 저장

JSON은 다음 옵션을 사용한다.

```python
json.dump(data, ensure_ascii=False, indent=2)
```

---

## 7. 필드 순서

CSV/JSON 필드 순서는 고정한다.

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

향후 후보 필드:

```text
performanceClips
verificationStatus
lastSungDate
```

v0.1에서는 도입하지 않는다.

---

## 8. 자동 처리 규칙

### 8.1 id 자동 생성

id 없는 새 곡은 다음 id를 자동 생성한다.

```text
S0034
S0035
...
```

기준:

- 기존 id 중 가장 큰 번호 + 1

### 8.2 singCount

- 빈 값이면 0
- 숫자 문자열이면 int로 변환
- 변환 실패 시 에러

### 8.3 pick

허용 입력:

```text
true, false, TRUE, FALSE, 1, 0, yes, no, y, n, 예, 아니오, 체크, 빈칸
```

저장 시 JSON boolean으로 변환.

빈칸은 false.

### 8.4 YouTube URL 정규화

입력 예:

```text
https://www.youtube.com/watch?v=abc123&list=...
https://youtu.be/abc123?si=...
```

저장:

```text
https://www.youtube.com/watch?v=abc123
```

### 8.5 thumbnailUrl 자동 생성

videoUrl에서 ID 추출 가능하면:

```text
https://img.youtube.com/vi/<VIDEO_ID>/hqdefault.jpg
```

videoUrl이 없으면 thumbnailUrl은 빈 값 허용.

---

## 9. 검증 규칙

### 9.1 에러

에러가 있으면 적용 중단.

- CSV 읽기 실패
- JSON 읽기 실패
- id 중복
- title 빈 값
- artist 빈 값
- language 빈 값
- singCount 숫자 변환 실패
- pick boolean 변환 실패
- 완전 동일 title+artist를 새 행으로 추가하려는 경우

### 9.2 경고

경고는 적용을 막지 않는다.

- videoUrl 없음
- lyricsUrl 없음
- songIntro 없음
- genre1 없음
- tags 없음
- sourceNote 없음
- videoUrl/thumbnailUrl ID 불일치
- 제목 유사 중복 의심
- translation/tags 유사 중복 의심

### 9.3 하지 않는 검증

이 도구는 다음을 검증하지 않는다.

- 실제 존재하는 곡인지
- 영상이 공식 영상인지
- 가사 링크가 정확한지
- 작품 출처가 맞는지
- 스트리머가 실제로 불렀는지

이건 GPT/제미나이/사람이 확인한다.

---

## 10. 중복 의심 로직

중복 검사 대상:

- title
- translation
- artist
- artistKr
- tags

정규화:

- lowercase
- NFKC
- 공백 제거
- 일부 기호 제거
- 괄호/하트/특수기호 완화

검사:

1. 완전 동일 `title + artist` → 에러
2. title 유사도 높음 → 경고
3. translation/tags에 기존 title이 포함 → 경고
4. 새 곡 title이 기존 tags에 포함 → 경고

Python 표준 라이브러리 `difflib.SequenceMatcher` 사용.

자동 병합 금지.  
중복 의심은 사람에게 보여주기만 한다.

---

## 11. 삭제 정책

v0.1에서는 삭제를 자동 반영하지 않는다.

CSV에서 기존 id 행이 사라져도:

```text
[삭제 의심] CSV에서 사라진 기존 곡이 있습니다.
기본 정책상 songs.json에서 삭제하지 않습니다.
```

삭제가 필요하면 나중에 별도 기능으로 만든다.

향후 후보:

- `active` 필드 추가
- 삭제 전용 모드
- archive file 이동

---

## 12. 안전장치

적용 전 반드시 백업한다.

```text
data/backups/songs_master_YYYYMMDD_HHMMSS.csv
data/backups/songs_YYYYMMDD_HHMMSS.json
```

적용 전 preview를 제공한다.

GUI에서 `적용` 버튼을 누르면 확인 메시지를 한 번 더 띄운다.

---

## 13. 구현 범위 v0.1

v0.1에서 반드시 구현:

- local admin server
- browser open
- songs_master.csv 없으면 songs.json에서 생성
- 곡 목록
- 곡 검색
- 곡 수정 폼
- 새 곡 추가 폼
- 부른 횟수 +1
- preview changes
- apply/build
- backup
- validation summary
- Korean UI text

v0.1에서 하지 않음:

- 예쁜 디자인 완성
- user auth
- remote deploy
- git push 자동화
- YouTube iframe preview
- 외부 URL 접속 검증
- batch import advanced UI
- 삭제 기능
- performanceClips UI

---

## 14. UI 톤

관리자 GUI는 production 사이트만큼 예쁠 필요는 없다.

하지만 다음은 지킨다.

- 한국어 중심
- 버튼 명확
- 위험한 작업은 빨간색/경고
- 저장/적용 전 미리보기
- 너무 개발자 콘솔처럼 보이지 않기
- 말차/아이보리 톤을 가볍게 사용해도 됨

---

## 15. 구현 후 검증

Codex는 구현 후 다음을 확인한다.

```text
python tools/admin_server.py 실행 가능
http://localhost:8765 접속 가능
data/songs_master.csv 생성 가능
곡 목록 표시
곡 수정 후 preview 표시
적용 시 songs.json 갱신
백업 생성
node --check src/app.js 통과
node --check src/portal.js 통과
JSON parse 성공
```

production UI 파일은 수정하지 않는다.

---

## 16. 보고 형식

구현 후 보고:

1. 생성/수정한 파일
2. 실행 방법
3. 구현된 기능
4. 구현하지 않은 기능
5. 안전장치
6. 검증 결과
7. 다음 TODO
