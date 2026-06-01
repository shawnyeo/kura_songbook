# 06_DATA_MAINTENANCE

## 현재 운영 흐름

```text
data/songs_master.csv 수정
또는 local admin GUI 사용
→ 변경 미리보기
→ 적용/빌드
→ data/songs.json 갱신
→ 로컬 사이트 확인
→ 수동 commit/push
```

## Local Admin GUI

실행:

```powershell
python tools/admin_server.py
```

접속:

```text
http://localhost:8765
```

## 부른 횟수 수정

곡 목록에서 `+1 / -1` 버튼으로 빠르게 수정한다.

주의:

- 이 동작은 `data/songs_master.csv`만 수정한다.
- `data/songs.json`은 바로 수정되지 않는다.
- public site 반영은 `변경 미리보기 → 적용/빌드` 후 이루어진다.

## 신곡 추가

신곡 추가는 두 방식이 가능하다.

1. GPT가 만든 CSV row 표를 `songs_master.csv`에 직접 붙여넣기
2. Admin GUI의 새 곡 추가 폼 사용

현재는 CSV 직접 편집이 더 편할 수 있다.

## 적용/빌드

Admin GUI에서 변경 미리보기를 확인한 뒤 적용/빌드한다.

적용 시:

- CSV 백업
- JSON 백업
- songs_master.csv 저장
- songs.json 빌드
- 검증 결과 표시

## 삭제 정책

삭제는 자동 반영하지 않는다.

CSV에서 기존 id가 사라져도 deletion candidate로만 보여주고 JSON에서는 유지한다.

## 외부 검증

다음은 도구가 아니라 사람/GPT/웹검색이 확인한다.

- 실제 존재하는 곡인지
- 영상이 공식 영상인지
- 가사 링크가 정확한지
- 작품 출처가 맞는지
