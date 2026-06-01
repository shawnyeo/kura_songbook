# 쿠라's 노래책 — CURRENT_TASK

## Current Goal

Web v1.0 공개 이후, 공식 DB 운영 체계와 문서를 정리한다.

현재 우선순위는 디자인 대공사가 아니라 다음이다.

```text
문서 갱신
↓
songs.json schema 확정
↓
GPT 곡 출력 포맷 확정
↓
데이터 유지보수 흐름 확정
↓
로컬 관리 도구 생성
```

---

## Current Phase

Phase 1 — Web v1.0 documentation and data maintenance planning.

---

## Source of Truth

현재 source of truth:

1. `docs/00_PROJECT_STATE_v1_0_WEB.md`
2. `docs/04_SONG_SCHEMA_JSON.md`
3. `docs/05_GPT_SONG_OUTPUT_FORMAT.md`
4. `docs/06_DATA_MAINTENANCE.md`
5. `docs/02_DESIGN_BRIEF.md`
6. `docs/07_ROADMAP_AFTER_V1.md`

Legacy reference:

- `docs/legacy/`
- Google Sheets MVP documents
- xlsx snapshot
- old migration plans

Legacy 문서는 현재 운영 기준이 아니다.

---

## Current Rules

- `data/songs.json`을 공식 웹 DB로 본다.
- Google Sheets/xlsx는 legacy import 또는 backup source다.
- 곡 추가는 JSON 객체 기준으로 한다.
- GPT에게 곡 추가를 요청할 때는 `05_GPT_SONG_OUTPUT_FORMAT.md`를 따른다.
- 불확실한 정보는 추정하지 않고 빈 값 또는 TODO로 둔다.
- 웹 UI 수정 전에는 현재 배포 상태와 source of truth를 확인한다.
- 배포 전에는 `validate_songs.py` 또는 JSON parse 검증을 수행한다.

---

## Immediate Tasks

### 1. 문서 갱신

- `00_PROJECT_STATE_v1_0_WEB.md`
- `01_WEB_ARCHITECTURE_SPEC.md`
- `02_DESIGN_BRIEF.md`
- `04_SONG_SCHEMA_JSON.md`
- `05_GPT_SONG_OUTPUT_FORMAT.md`
- `06_DATA_MAINTENANCE.md`
- `07_ROADMAP_AFTER_V1.md`
- `08_RELEASE_NOTES_v1_0.md`

### 2. 운영 도구 설계

- `tools/validate_songs.py`
- `tools/update_song.py`
- `tools/append_song.py`
- `tools/new_song.example.json`

### 3. 실제 운영 테스트

- `Lemon` singCount +1
- 영상 링크 교체
- 가사 링크 추가
- 신곡 1개 append test

---

## Deferred Tasks

- 태그 collapse/expand
- 모바일 전용 개선
- 포털 랜덤 미리보기
- Pick collection
- YouTube iframe modal
- feedback/request form
- local admin page

---

## Codex Rule

Codex 작업자는 다음을 지킨다.

1. 현재 구조를 먼저 요약한다.
2. `data/songs.json` 수정 작업과 UI 수정 작업을 섞지 않는다.
3. 곡 추가/수정 도구를 만들 때는 먼저 dry-run 기능을 둔다.
4. 자동 commit/push 하지 않는다.
5. source verification needed 항목을 추정으로 메우지 않는다.
