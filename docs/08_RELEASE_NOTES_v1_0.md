# 쿠라's 노래책 — RELEASE_NOTES_v1_0

## Release

Web v1.0 Beta

## 상태

공개 완료.

## 핵심 기능

- 메인 포털
- 검색 결과 페이지
- 자유검색
- 언어/장르/분위기 필터
- Pick 먼저 보기
- 정렬
- 전체 곡 랜덤
- 현재 결과 랜덤
- 영상 썸네일 링크
- 가사 링크
- 부른 횟수 표시
- songIntro 표시
- GitHub Pages 배포

## 기술 구조

- Plain HTML/CSS/JavaScript
- GitHub Pages
- `data/songs.json`
- No backend
- No login
- No DB server

## 디자인

- 말차
- 아이보리
- 연핑크
- 핑크 해파리
- 벚꽃/잎사귀
- 일본 팬사이트형 검색 UI

## v1.0 반응 / 기록

- 핑크 해파리 방향은 긍정적 반응을 얻음.
- 공개 시점에는 실사용 사례는 아직 많지 않음.
- 실사용 증가는 운영자 본인 사용과 스트리머의 노래 추가 여부에 달려 있음.

## 알려진 이슈

- 모바일은 rough beta
- `S0027 星の子 / 별의 아이` source verification needed
- 포털 빠른 검색 예시는 하드코딩
- 포털 랜덤 추천은 실제 곡 미리보기가 아니라 검색 페이지 랜덤 진입 안내
- Pick collection 미구현
- 카드 태그/메타 정보 중복감 있음
- YouTube iframe modal 없음

## 다음 버전

v1.0.1:

- 문서 갱신
- JSON schema 확정
- GPT 곡 출력 포맷
- 데이터 관리 도구
- validate/update/append scripts
