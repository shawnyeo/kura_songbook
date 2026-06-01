# 10_LOCAL_ADMIN_GUI_SPEC_v0_1

## 목적

로컬 관리자 GUI는 `data/songs_master.csv`를 편하게 수정하고 `data/songs.json`으로 빌드하기 위한 로컬 전용 도구다.

## 현재 구현

- `tools/admin_server.py`
- `tools/run_admin_gui.bat`
- `tools/admin_static/admin.css`
- `data/songs_master.csv`

## 실행

```powershell
python tools/admin_server.py
```

접속:

```text
http://localhost:8765
```

## 구현된 주요 기능

- Dashboard
- 곡 목록
- 곡 검색
- 곡 수정 폼
- 새 곡 추가 폼
- 변경 미리보기
- 검증
- 적용/빌드
- 백업 생성

## 부른 횟수 빠른 수정

현재 추가 구현:

- `/songs` 목록에 `+1 / -1 / 수정` 액션
- `POST /count/increment`: 선택 곡의 singCount를 +1, `songs_master.csv`만 수정
- `GET /count/decrement`: -1 확인 페이지 표시
- `POST /count/decrement`: -1 적용, 0 아래로 내려가지 않음
- 빠른 수정은 `data/songs.json`을 직접 수정하지 않음
- JSON 반영은 여전히 `변경 미리보기 → 적용/빌드` 필요

## 안전 원칙

- 자동 commit/push 없음
- 자동 삭제 없음
- 적용 전 백업
- 외부 URL 공식성 검증 없음
