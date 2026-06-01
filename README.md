# Kura Songbook / 쿠라's 노래책

쿠라's 노래책은 스트리머 쿠라맛챠 방송용으로 만든 팬메이드 노래 검색 사이트입니다.

Google Sheets MVP로 검증한 검색 구조를 바탕으로, 현재는 GitHub Pages 기반 Web v1.0 Beta 정적 사이트로 운영 중입니다.

## Current Status

- Web v1.0 Beta 공개 완료
- GitHub Pages 기반 정적 사이트
- `index.html` = 메인 포털
- `search.html` = 검색 결과 페이지
- `data/songs_master.csv` = 사람이 수정하는 관리자용 원본 DB
- `data/songs.json` = 웹사이트가 읽는 public build output
- Google Sheets / xlsx = legacy snapshot / backup / import source
- 로컬 관리자 GUI 도입 완료

## Data Source Policy

현재 운영 기준은 다음과 같습니다.

```text
data/songs_master.csv = human-editable admin source of truth
data/songs.json       = public web DB / build output used by the website
Google Sheets / xlsx  = legacy snapshot / backup / import source
```

신곡 추가, 부른 횟수 수정, 영상/가사 링크 교체는 기본적으로 `data/songs_master.csv` 또는 로컬 관리자 GUI를 통해 진행합니다.

`data/songs.json`은 웹사이트가 fetch하는 배포용 DB이며, 일반 운영에서는 `songs_master.csv`에서 빌드된 결과물로 취급합니다.

## Local Admin GUI

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

기본 흐름:

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

## Docs

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

## Local Preview

```powershell
python -m http.server 8000
```

```text
http://localhost:8000
```

## Fan Nickname

UI와 문서에서 팬닉은 다음 표기를 사용합니다.

```text
냉채단
```

`Kuramates`는 기본 표기로 사용하지 않습니다.
