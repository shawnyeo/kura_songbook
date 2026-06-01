# Kura Songbook / 쿠라's 노래책

쿠라's 노래책은 Google Sheets MVP로 검증한 방송용 노래 검색 UI를 GitHub Pages 기반 Web v1.0 Beta 정적 사이트로 운영하는 프로젝트입니다.

## Goal

스트리머와 시청자가 방송 중 곡을 빠르게 검색하고, 영상/가사 링크로 이동할 수 있는 팬페이지형 노래 검색 사이트를 만든다.

## Current Direction

- GitHub Pages
- Static site
- Plain HTML/CSS/JS first
- `data/songs.json` official web DB 기반 검색
- PC/mobile responsive UI
- 말차 / 아이보리 / 연핑크 / 핑크 해파리 디자인

## Docs

Codex 또는 작업자는 먼저 아래 문서를 읽어야 합니다.

1. `docs/00_PROJECT_STATE_v1_0_WEB.md`
2. `docs/01_WEB_ARCHITECTURE_SPEC.md`
3. `docs/02_DESIGN_BRIEF.md`
4. `docs/03_CURRENT_TASK.md`
5. `docs/04_SONG_SCHEMA_JSON.md`
6. `docs/05_GPT_SONG_OUTPUT_FORMAT.md`
7. `docs/06_DATA_MAINTENANCE.md`

현재 Web v1.0 운영 기준은 `data/songs.json`과 위 문서들입니다.
Google Sheets / xlsx 자료는 legacy snapshot, backup, import source로만 사용합니다.

Legacy Google Sheets MVP 문서는 `docs/legacy/`에 보관되어 있습니다.
문서가 충돌하면 Web v1.0 문서와 `data/songs.json`을 우선합니다.

## Data Source

현재 공식 웹 DB source of truth는 다음 파일입니다.

```text
data/songs.json
```

곡 추가/수정은 기본적으로 `data/songs.json` 기준으로 진행합니다.
schema는 `docs/04_SONG_SCHEMA_JSON.md`를 따릅니다.

## Legacy xlsx Import

Google Sheets snapshot 또는 xlsx 백업을 다시 import해야 할 때만 아래 변환기를 사용합니다.

```powershell
python scripts/convert_xlsx_to_songs.py
```

변환 전 미리보기만 확인하려면:

```powershell
python scripts/convert_xlsx_to_songs.py --dry-run
```

입력/출력 경로를 직접 지정할 수도 있습니다.

```powershell
python scripts/convert_xlsx_to_songs.py --input "source_archive/쿠라's 노래책  v1.0.xlsx" --output data/songs.json
```

일반 운영에서는 xlsx가 source of truth가 아닙니다.

로컬에서 사이트를 확인할 때는 `file://` 대신 정적 서버를 사용합니다.

```powershell
python -m http.server 8000
```

그 다음 `http://localhost:8000`을 엽니다.

## GitHub Pages Deployment

GitHub Pages는 repository root를 정적 사이트로 배포하도록 설정합니다.

Recommended settings:

* Source: `Deploy from a branch`
* Branch: `main`
* Folder: `/ (root)`

## Design References

Visual references are stored in:

```text
docs/design_reference/
```

Important:

* The design references are not literal layouts to copy.
* Google Sheets screenshots represent the validated MVP mood, information hierarchy, and feature intent.
* The generated desktop mockup is the primary visual mood reference for the web version.
* The final website should be web-native, responsive, and easier to use than the sheet.
* If visual references conflict with usability, usability wins.

Primary design direction:

* matcha green
* warm ivory
* sakura pink
* pink jellyfish mascots
* soft Japanese fan site atmosphere
* music search result clarity
* cute but not childish
* fanpage-like but not messy
* not a SaaS dashboard
