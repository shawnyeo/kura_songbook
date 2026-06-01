# 쿠라's 노래책 — ROADMAP_AFTER_V1

## 0. 목적

이 문서는 Web v1.0 공개 이후의 작업 우선순위를 정리한다.

---

## v1.0 상태

완료:

- GitHub Pages 공개
- `index.html` 메인 포털
- `search.html` 검색 결과 페이지
- `data/songs.json` 기반 검색
- 필터 / 정렬 / 랜덤
- 영상 썸네일 클릭
- 가사 버튼
- 부른 횟수
- Pick 표시
- 말차/아이보리/핑크 해파리 디자인
- 기본 모바일 대응

---

## v1.0.1 — 운영 안정화

목표:

```text
곡 추가와 수정이 귀찮지 않게 만들기
```

작업:

1. 문서 갱신
2. `data/songs.json` schema 확정
3. GPT 곡 출력 포맷 확정
4. `validate_songs.py`
5. `update_song.py`
6. `append_song.py`
7. `new_song.example.json`
8. Lemon singCount +1 테스트
9. 새 곡 1개 추가 테스트
10. 링크 교체 테스트

---

## v1.1 — 검색 결과 품질 개선

목표:

```text
검색 결과 카드의 중복감 감소와 실사용성 향상
```

작업:

1. 태그 핵심 3개 + `+N` collapse/expand
2. 출처/비고/장르 메타 라인 정리
3. 랜덤 카드 정보 위계 개선
4. 포털 랜덤 곡 미리보기
5. Pick collection 기본 구현
6. favicon
7. OG image
8. empty state 개선

---

## v1.2 — 모바일 개선

목표:

```text
모바일에서 검색과 결과 확인이 자연스럽게 되게 만들기
```

작업:

1. search.html 모바일 hero 축소
2. 모바일 결과 카드 재설계
3. 모바일 filter/dropdown 정리
4. 모바일 random/help/pick 순서 정리
5. footer 모바일 정리
6. fixed search 모바일 처리
7. 포털 모바일 CTA 정리

---

## v1.3 — 검색 고도화

작업:

1. 공백 무시 검색
2. alias 필드 강화
3. 일본어/한국어 통용명 매칭
4. 초성 검색 검토
5. ranking 기반 정렬 검토
6. `tags` 운영 규칙 개선

---

## v2.0 — 운영/요청 확장

작업 후보:

1. 피드백/오류 제보 링크
2. Google Form 또는 GitHub Issues 연결
3. 로컬 관리자 페이지
4. YouTube iframe modal
5. 스트리머가 부른 클립 링크 모음
6. performanceClips schema
7. 간단한 changelog 페이지

---

## 보류 / 하지 않음

현재는 하지 않음:

- 서버 DB
- 로그인
- 사용자 입력 저장
- Google Sheets auto sync
- 공식 요청 시스템처럼 보이는 기능
- 가사 전문 호스팅

---

## 디자인 확장 후보

- 핑크 해파리 favicon
- 카드게임/컬렉션 감성 에셋
- 보카로/마후마후풍 추상 장식
- 황금 태양/카드 프레임 계열 추상 장식
- 단, 실제 저작권 캐릭터/로고 직접 사용은 피한다.
