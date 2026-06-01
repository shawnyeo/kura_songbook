# Kura Songbook / 쿠라's 노래책

쿠라's 노래책은 스트리머 쿠라맛챠 방송용으로 만든 팬메이드 노래 검색 사이트입니다.

Google Sheets MVP로 검증한 검색 구조를 바탕으로, 현재는 GitHub Pages 기반 Web v1.0 Beta 정적 사이트로 운영 중입니다.

## Goal

스트리머와 시청자가 방송 중 곡을 빠르게 검색하고, 영상/가사 링크로 이동하며, 랜덤 추천과 필터를 통해 노래를 고를 수 있는 팬페이지형 노래 검색 사이트를 만든다.

## Current Status

- Web v1.0 Beta 공개 완료
- GitHub Pages 기반 정적 사이트
- Plain HTML/CSS/JavaScript
- `index.html` = 메인 포털
- `search.html` = 검색 결과 페이지
- `data/songs_master.csv` = 사람이 수정하는 관리자용 원본 DB
- `data/songs.json` = 웹사이트가 읽는 public build output
- Google Sheets / xlsx = legacy snapshot / backup / import source
- 말차 / 아이보리 / 연핑크 / 핑크 해파리 디자인

## Main Features

- 자유검색
- 언어 / 장르 / 분위기 필터
- Pick 먼저 보기
- 정렬
- 전체 곡 랜덤 추천
- 현재 검색 결과 내 랜덤 추천
- YouTube 썸네일 기반 영상 링크
- 가사 링크
- 부른 횟수 표시
- songIntro 기반 1줄 곡 소개

## Project Structure

```text
kura_songbook/
├─ index.html              # 메인 포털
├─ search.html             # 검색 결과 페이지
├─ src/
│  ├─ app.js               # 검색/필터/정렬/랜덤/카드 렌더링
│  ├─ portal.js            # 포털 검색 → search.html 이동
│  └─ style.css            # 공통 스타일
├─ data/
│  ├─ songs_master.csv     # 관리자용 편집 원본
│  └─ songs.json           # public web DB / build output
├─ assets/                 # 배경/이미지 에셋
├─ docs/                   # 프로젝트 문서
├─ tools/                  # 로컬 관리자 도구
├─ scripts/                # legacy/import helper scripts
└─ source_archive/         # 과거 자료 / Google Sheets snapshot
```

## Data Source Policy

현재 운영 기준은 다음과 같습니다.

```text
data/songs_master.csv = human-editable admin source of truth
data/songs.json       = public web DB / build output used by the website
Google Sheets / xlsx  = legacy snapshot / backup / import source
```

신곡 추가, 부른 횟수 수정, 영상/가사 링크 교체는 기본적으로 `data/songs_master.csv` 또는 로컬 관리자 GUI를 통해 진행합니다.

`data/songs.json`은 웹사이트가 fetch하는 배포용 DB이며, 일반 운영에서는 `songs_master.csv`에서 빌드된 결과물로 취급합니다.

Google Sheets 기반 문서는 과거 MVP 구조와 taxonomy 원칙을 이해하기 위한 reference로만 사용합니다.

## Local Admin GUI

로컬 관리자 GUI는 `songs_master.csv`를 편하게 수정하고 `songs.json`으로 빌드하기 위한 로컬 전용 도구입니다.

실행:

```powershell
python tools/admin_server.py
```

또는 Windows에서:

```text
tools/run_admin_gui.bat
```

접속:

```text
http://localhost:8765
```

관리자 GUI의 기본 흐름:

```text
곡 목록에서 검색
→ +1 / -1로 부른 횟수 빠른 수정
→ 필요 시 곡 정보 수정
→ 변경 미리보기
→ 적용/빌드
→ data/songs.json 갱신
→ 로컬 사이트 확인
→ 수동 commit/push
```

주의:

- `+1 / -1` 빠른 수정은 `data/songs_master.csv`만 수정합니다.
- `data/songs.json` 반영은 `변경 미리보기 → 적용/빌드` 후 이루어집니다.
- 관리자 GUI는 자동 commit/push를 하지 않습니다.
- 삭제는 기본적으로 자동 반영하지 않습니다.
- 실제 곡 존재 여부, 공식 영상 여부, 가사 링크 정확성은 사람/GPT/웹검색으로 확인합니다.

## Docs

Codex 또는 작업자는 먼저 현재 Web v1.0 기준 문서를 읽어야 합니다.

권장 문서 구조:

1. `docs/00_PROJECT_STATE_v1_0_WEB.md`
2. `docs/01_WEB_ARCHITECTURE_SPEC.md`
3. `docs/02_DESIGN_BRIEF.md`
4. `docs/03_CURRENT_TASK.md`
5. `docs/04_SONG_SCHEMA_JSON.md`
6. `docs/05_GPT_SONG_OUTPUT_FORMAT.md`
7. `docs/06_DATA_MAINTENANCE.md`
8. `docs/07_ROADMAP_AFTER_V1.md`
9. `docs/08_RELEASE_NOTES_v1_0.md`
10. `docs/09_IMPLEMENTATION_HISTORY.md`
11. `docs/10_LOCAL_ADMIN_GUI_SPEC_v0_1.md`

Legacy Google Sheets 문서는 `docs/legacy/` 또는 `source_archive/`에 보관합니다.

문서가 충돌하면 현재 Web v1.0 문서와 `data/songs_master.csv` 운영 기준을 우선합니다.

## Local Preview

로컬에서 공개 사이트를 확인할 때는 `file://` 대신 정적 서버를 사용합니다.

```powershell
python -m http.server 8000
```

그 다음 아래 주소를 엽니다.

```text
http://localhost:8000
```

검색 페이지를 직접 확인하려면:

```text
http://localhost:8000/search.html
```

## Legacy xlsx Import

Google Sheets snapshot을 `data/songs.json`으로 다시 변환해야 할 때만 아래 스크립트를 사용합니다.

```powershell
python scripts/convert_xlsx_to_songs.py
```

미리보기:

```powershell
python scripts/convert_xlsx_to_songs.py --dry-run
```

입력/출력 경로 지정:

```powershell
python scripts/convert_xlsx_to_songs.py --input "source_archive/쿠라's 노래책  v1.0.xlsx" --output data/songs.json
```

주의: 일반 운영에서는 xlsx 변환보다 `data/songs_master.csv`와 로컬 관리자 GUI를 우선합니다.

## GitHub Pages Deployment

GitHub Pages는 repository root를 정적 사이트로 배포하도록 설정합니다.

Recommended settings:

- Source: `Deploy from a branch`
- Branch: currently configured deployment branch
- Folder: `/ (root)`

배포 후에는 GitHub Pages URL에서 다음을 확인합니다.

- `/` 메인 포털 로드
- `/search.html` 검색 페이지 로드
- `data/songs.json` fetch 정상
- CSS/JS/assets 경로 정상

## Design Direction

Primary design direction:

- matcha green
- warm ivory
- sakura pink
- pink jellyfish mascots
- soft Japanese fan site atmosphere
- music search result clarity
- cute but not childish
- fanpage-like but not messy
- not a SaaS dashboard

Design references are stored in:

```text
docs/design_reference/
```

Important:

- 디자인 레퍼런스는 그대로 복제하는 대상이 아니라 mood/reference다.
- Google Sheets screenshots represent the validated MVP mood, information hierarchy, and feature intent.
- The generated desktop mockup is the primary visual mood reference for the web version.
- If visual references conflict with usability, usability wins.

## Fan Nickname

UI와 문서에서 팬닉은 다음 표기를 사용합니다.

```text
냉채단
```

`Kuramates`는 기본 표기로 사용하지 않습니다.

## Current Priorities

v1.0.1 우선순위:

1. README / docs를 CSV-master 운영 기준으로 정리
2. GPT 곡 출력 포맷을 CSV row/table first로 갱신
3. 로컬 관리자 GUI 실사용 테스트
4. `songs_master.csv → songs.json` 적용/빌드 흐름 안정화
5. 부른 횟수 / 영상 링크 / 가사 링크 운영 테스트

v1.1 이후 후보:

- 태그 collapse/expand
- 포털 랜덤 미리보기
- Pick collection
- 모바일 UX 개선
- favicon / OG image
- 스트리머가 부른 클립 링크 모음
