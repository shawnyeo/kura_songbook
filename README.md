# Kura Songbook / 쿠라's 노래책

쿠라's 노래책은 Google Sheets MVP로 검증한 방송용 노래 검색 UI를 GitHub Pages 기반 정적 웹사이트로 이전하는 프로젝트입니다.

## Goal

스트리머와 시청자가 방송 중 곡을 빠르게 검색하고, 영상/가사 링크로 이동할 수 있는 팬페이지형 노래 검색 사이트를 만든다.

## Current Direction

- GitHub Pages
- Static site
- Plain HTML/CSS/JS first
- `data/songs.json` 기반 검색
- PC/mobile responsive UI
- 말차 / 아이보리 / 연핑크 / 핑크 해파리 디자인

## Docs

Codex 또는 작업자는 먼저 아래 문서를 읽어야 합니다.

1. `docs/00_PROJECT_STATE_v1_0.md`
2. `docs/01_WEB_MIGRATION_SPEC.md`
3. `docs/02_DESIGN_BRIEF.md`
4. `docs/03_CURRENT_TASK.md`

`source_archive/`는 과거 자료 보관용입니다.  
문서가 충돌하면 `docs/`를 우선합니다.

## Convert xlsx to JSON

실제 Google Sheets snapshot을 `data/songs.json`으로 변환할 때는 아래 명령을 사용합니다.

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
