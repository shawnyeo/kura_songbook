# 쿠라's 노래책 — DOC_RESTRUCTURE_PLAN

## 0. 목적

이 문서는 Google Sheets MVP 문서 체계에서 GitHub Pages Web v1.0 운영 문서 체계로 전환하기 위한 재배치 계획이다.

현재 프로젝트는 다음 단계에 들어섰다.

```text
Google Sheets MVP 검증
↓
GitHub Pages Web v1.0 Beta 공개
↓
data/songs.json 공식 웹 DB화
↓
운영 도구 / 문서 / 데이터 관리 체계 구축
```

따라서 과거의 “시트 구조 설명” 중심 문서에서, 앞으로는 “웹 운영과 JSON DB 관리” 중심 문서로 전환한다.

---

## 1. 문서 재배치 원칙

### 1.1 현재 운영 문서와 legacy 문서를 분리한다

현재 운영 문서에는 다음 정보만 둔다.

- 현재 배포된 웹 구조
- `data/songs.json` schema
- GPT 곡 추가 출력 포맷
- 로컬 데이터 관리 방법
- v1.0 이후 로드맵
- 현재 디자인/사용성 기준

Google Sheets MVP 구조는 더 이상 source of truth가 아니므로 legacy 문서로 보관한다.

---

### 1.2 `data/songs.json`을 공식 웹 DB로 본다

앞으로의 실운영 기준은 다음과 같다.

```text
data/songs.json = official web DB source of truth
Google Sheets / xlsx = legacy snapshot / backup / import source
```

xlsx 변환기는 유지하되, 일반 운영 흐름의 중심은 아니다.

---

### 1.3 GPT 출력 포맷을 JSON 기준으로 고정한다

앞으로 GPT에게 곡 추가 조사를 시킬 때는 “시트 행”이 아니라 `songs.json`에 들어갈 곡 객체를 생성하게 한다.

단, 모든 필드를 완벽히 채우는 것을 강제하지 않는다.

- 필수 필드: 최소 표시/검색에 필요한 값
- 권장 필드: 있으면 품질이 좋아지는 값
- 선택 필드: 나중에 채울 수 있는 값

---

### 1.4 운영 도구는 문서 이후 만든다

도구 생성 순서:

```text
문서 확정
↓
schema 확정
↓
GPT 출력 포맷 확정
↓
validate_songs.py
↓
update_song.py
↓
append_song.py
```

문서 없이 도구부터 만들면 field name, 빈 값 허용, alias/tag 규칙이 흔들릴 수 있다.

---

## 2. 추천 문서 구조

```text
docs/
  00_PROJECT_STATE_v1_0_WEB.md
  01_WEB_ARCHITECTURE_SPEC.md
  02_DESIGN_BRIEF.md
  03_CURRENT_TASK.md
  04_SONG_SCHEMA_JSON.md
  05_GPT_SONG_OUTPUT_FORMAT.md
  06_DATA_MAINTENANCE.md
  07_ROADMAP_AFTER_V1.md
  08_RELEASE_NOTES_v1_0.md
  09_IMPLEMENTATION_HISTORY.md
  legacy/
    README_LEGACY_DOCS.md
    PROJECT_STATE_SHEETS_MVP.md
    SHEET_ARCHITECTURE_SPEC.md
    UI_IMPLEMENTATION_PLAN_PRE_WEB.md
  templates/
    new_song.example.json
    song_update_examples.md
```

---

## 3. GPT 프로젝트 소스에 남길 문서

GPT에게 항상 읽힐 source of truth는 다음 정도로 줄인다.

1. `00_PROJECT_STATE_v1_0_WEB.md`
2. `04_SONG_SCHEMA_JSON.md`
3. `05_GPT_SONG_OUTPUT_FORMAT.md`
4. `06_DATA_MAINTENANCE.md`
5. `02_DESIGN_BRIEF.md`
6. `07_ROADMAP_AFTER_V1.md`

legacy 문서는 GPT 기본 소스에서 제외한다. 필요할 때만 수동 참조한다.

---

## 4. legacy 처리

Google Sheets 관련 문서는 보존하되 다음 문구를 상단에 붙인다.

> 이 문서는 Google Sheets MVP 시절의 역사적 기록이다. 현재 Web v1.0 운영 기준은 `data/songs.json`과 Web v1.0 문서를 따른다.

권장 위치:

```text
docs/legacy/
```

또는 로컬 보관:

```text
source_archive/docs_legacy/
```

---

## 5. 바로 적용할 우선순위

1. Web v1.0 상태 문서 생성
2. JSON schema 문서 생성
3. GPT 출력 포맷 문서 생성
4. 데이터 유지보수 문서 생성
5. 현재 태스크 문서 교체
6. legacy 문서 위치 정리
7. 이후 운영 도구 생성

---

## 6. 보류할 사항

다음은 문서 Phase 1 이후로 미룬다.

- 로컬 관리자 페이지
- YouTube iframe modal
- clip link collection UI
- 태그 collapse/expand 구현
- 모바일 전용 재설계
- 피드백/요청 폼
