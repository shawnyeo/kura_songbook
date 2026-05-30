# 쿠라맛챠 노래책 — 시트 구조 및 수식 명세

## 0. 이 문서의 목적

이 문서는 현재 Google Sheets 기반 검색 엔진의 **정확한 탭 구성, 셀 위치, 컬럼 매핑, 수식 구조**를 기록하는 source file이다.

주의:

- 업로드된 `.xlsx`는 셀 위치 확인용으로만 사용한다.
- Google Sheets 전용 함수인 `QUERY`, `ARRAYFORMULA`, `SPLIT`, `TEXTJOIN` 등은 Excel 변환 시 `DUMMYFUNCTION`, `#NAME?`로 깨질 수 있다.
- 따라서 실제 Google Sheets 원본 수식은 이 문서에 적힌 수식을 기준으로 관리한다.

---

## 1. 현재 핵심 시트 목록

| 시트명 | 상태 | 역할 |
|---|---|---|
| `쿠라s 노래책~!` | 핵심 | DB_RAW. 곡 데이터 원본 |
| `검색창` | 핵심 | 현재 작동 중인 검색 엔진 UI/결과 출력 |
| `QUERY_BUILDER` | 핵심 | QUERY 조건 조각 생성 helper |
| `TAXONOMY` | 핵심 | 드롭다운 원본 목록 |
| `메인!` | 보조 | 사용법/버전/안내 |
| `시트6` | 임시 | 이전 작업용 후보/복붙 흔적 |
| `시트2` | 임시 | 이전 작업용 후보/복붙 흔적 |
| `쿠라쿠라!` | 미사용 추정 | 비어 있음 또는 테스트 흔적 |

---

## 2. DB_RAW: `쿠라s 노래책~!`

### 2.1 컬럼 구조

| 열 | 컬럼명 | 용도 | 비고 |
|---|---|---|---|
| A | 제목 | 표시/검색 | 원문 제목 유지 |
| B | 번역명 | 표시/검색 | 자연스러운 한국어 번역 |
| C | 가수 | 표시/검색 | 원어/공식 표기 |
| D | 한국명 | 표시/검색 | 가수명 발음 기반 표기 |
| E | 언어 | 필터 | 한국어/일본어/중국어/영어 등 |
| F | 장르 | 표시 | 예: `발라드 / 팝` |
| G | 장르1 | 필터 | 원자값 |
| H | 장르2 | 필터 | 원자값 |
| I | 설명 | 표시 | 예: `사랑 / 재회 / 그리움` |
| J | 상황 | 필터 | 원자값 |
| K | 대상 | 필터 | 원자값 |
| L | 감정 | 필터 | 원자값 |
| M | 비고 | 표시/contains 검색 | 공개용 짧은 메타 |
| N | 매체 | 내부 메타 | 애니/드라마/오리지널 등 |
| O | 출처유형 | 내부 메타 | OST/OP/ED/인디 등 |
| P | 작품명 | 내부 메타 | 작품명 |
| Q | 기타태그 | 내부 메타 | 바이럴/고음주의 등 |
| R | 링크 | 표시/링크 | 영상 또는 검색 링크 |
| S | 부른 횟수 | 운영 | 숫자만 |

### 2.2 설계 원칙

- F열 `장르`는 보기용이다.
- G/H열 `장르1/장르2`가 실제 검색용이다.
- I열 `설명`은 보기용이다.
- J/K/L열 `상황/대상/감정`이 실제 검색용이다.
- M열 `비고`는 표시용이면서 출처유형/매체/기타태그의 contains 검색에도 사용한다.
- N/O/P/Q는 DB 정규화용 메타이며, 현재 검색엔진은 주로 M열을 검색한다.

---

## 3. 검색 엔진 시트: `검색창`

### 3.1 입력 영역

| 셀 | 내용 | 설명 |
|---|---|---|
| B1 | 자유검색 | 제목/번역명/가수/비고 등 contains 검색 |
| B2 | 언어 | 필터 라벨 |
| C2 | 장르 | 필터 라벨 |
| D2 | 상황 | 필터 라벨 |
| E2 | 대상 | 필터 라벨 |
| F2 | 감정 | 필터 라벨 |
| G2 | 출처유형 | 필터 라벨 |
| H2 | 매체 | 필터 라벨 |
| I2 | 기타태그 | 필터 라벨 |
| B3 | 언어 드롭다운 | TAXONOMY!A:A 기반 |
| C3 | 장르 드롭다운 | TAXONOMY!B:B 기반 |
| D3 | 상황 드롭다운 | TAXONOMY!C:C 기반 |
| E3 | 대상 드롭다운 | TAXONOMY!D:D 기반 |
| F3 | 감정 드롭다운 | TAXONOMY!E:E 기반 |
| G3 | 출처유형 드롭다운 | TAXONOMY!F:F 기반 |
| H3 | 매체 드롭다운 | TAXONOMY!G:G 기반 |
| I3 | 기타태그 드롭다운 | TAXONOMY!H:H 기반 |

### 3.2 결과 영역

| 셀/범위 | 내용 |
|---|---|
| B4:J4 | 결과 헤더 |
| B5:J | QUERY 결과 출력 |

결과 헤더:

| B | C | D | E | F | G | H | I | J |
|---|---|---|---|---|---|---|---|---|
| 제목 | 번역명 | 가수 | 한국명 | 언어 | 장르 | 주제 | 비고 | 링크 |

---

## 4. QUERY_BUILDER 시트

### 4.1 역할

`QUERY_BUILDER`는 검색창의 입력값을 Google Sheets `QUERY` 함수용 WHERE 조건 조각으로 변환한다.

| 셀 | 조건 | 참조 입력 |
|---|---|---|
| A1 | 자유검색 조건 | 검색창!B1 |
| A2 | 언어 조건 | 검색창!B3 |
| A3 | 장르 조건 | 검색창!C3 |
| A4 | 상황 조건 | 검색창!D3 |
| A5 | 대상 조건 | 검색창!E3 |
| A6 | 감정 조건 | 검색창!F3 |
| A7 | 출처유형 조건 | 검색창!G3 |
| A8 | 매체 조건 | 검색창!H3 |
| A9 | 기타태그 조건 | 검색창!I3 |
| B1 | 최종 QUERY 문자열 확인용 | A1:A9 |

---

## 5. QUERY_BUILDER 수식 원본

### 5.1 A1: 자유검색 조건

```gs
=IF(
  검색창!B1="",
  "",
  "(Col1 contains '"&검색창!B1&"' or Col2 contains '"&검색창!B1&"' or Col3 contains '"&검색창!B1&"' or Col4 contains '"&검색창!B1&"' or Col5 contains '"&검색창!B1&"' or Col6 contains '"&검색창!B1&"' or Col9 contains '"&검색창!B1&"' or Col13 contains '"&검색창!B1&"')"
)
```

검색 대상:

| Col | 의미 |
|---|---|
| Col1 | 제목 |
| Col2 | 번역명 |
| Col3 | 가수 |
| Col4 | 한국명 |
| Col5 | 언어 |
| Col6 | 장르 표시 |
| Col9 | 설명/주제 표시 |
| Col13 | 비고 |

---

### 5.2 A2: 언어 다중선택 조건

```gs
=IF(
  검색창!B3="",
  "",
  TEXTJOIN(
    " or ",
    TRUE,
    ARRAYFORMULA(
      "Col5 = '"&TRIM(SPLIT(검색창!B3, ","))&"'"
    )
  )
)
```

예:

```text
검색창!B3 = 일본어, 한국어
→ Col5 = '일본어' or Col5 = '한국어'
```

---

### 5.3 A3: 장르 다중선택 조건

```gs
=IF(
  검색창!C3="",
  "",
  TEXTJOIN(
    " or ",
    TRUE,
    ARRAYFORMULA(
      "(Col7 = '"&TRIM(SPLIT(검색창!C3, ","))&"' or Col8 = '"&TRIM(SPLIT(검색창!C3, ","))&"')"
    )
  )
)
```

예:

```text
검색창!C3 = 팝, 발라드
→ (Col7 = '팝' or Col8 = '팝') or (Col7 = '발라드' or Col8 = '발라드')
```

---

### 5.4 A4: 상황 다중선택 조건

```gs
=IF(
  검색창!D3="",
  "",
  TEXTJOIN(
    " or ",
    TRUE,
    ARRAYFORMULA(
      "Col10 = '"&TRIM(SPLIT(검색창!D3, ","))&"'"
    )
  )
)
```

---

### 5.5 A5: 대상 다중선택 조건

```gs
=IF(
  검색창!E3="",
  "",
  TEXTJOIN(
    " or ",
    TRUE,
    ARRAYFORMULA(
      "Col11 = '"&TRIM(SPLIT(검색창!E3, ","))&"'"
    )
  )
)
```

---

### 5.6 A6: 감정 다중선택 조건

```gs
=IF(
  검색창!F3="",
  "",
  TEXTJOIN(
    " or ",
    TRUE,
    ARRAYFORMULA(
      "Col12 = '"&TRIM(SPLIT(검색창!F3, ","))&"'"
    )
  )
)
```

---

### 5.7 A7: 출처유형 다중선택 조건

```gs
=IF(
  검색창!G3="",
  "",
  TEXTJOIN(
    " or ",
    TRUE,
    ARRAYFORMULA(
      "Col13 contains '"&TRIM(SPLIT(검색창!G3, ","))&"'"
    )
  )
)
```

---

### 5.8 A8: 매체 다중선택 조건

```gs
=IF(
  검색창!H3="",
  "",
  TEXTJOIN(
    " or ",
    TRUE,
    ARRAYFORMULA(
      "Col13 contains '"&TRIM(SPLIT(검색창!H3, ","))&"'"
    )
  )
)
```

---

### 5.9 A9: 기타태그 다중선택 조건

```gs
=IF(
  검색창!I3="",
  "",
  TEXTJOIN(
    " or ",
    TRUE,
    ARRAYFORMULA(
      "Col13 contains '"&TRIM(SPLIT(검색창!I3, ","))&"'"
    )
  )
)
```

---

### 5.10 B1: 최종 쿼리 문자열 디버그

```gs
="select Col1,Col2,Col3,Col4,Col5,Col6,Col9,Col13,Col18 where Col1 is not null"
& IF(A1<>""," and ("&A1&")","")
& IF(A2<>""," and ("&A2&")","")
& IF(A3<>""," and ("&A3&")","")
& IF(A4<>""," and ("&A4&")","")
& IF(A5<>""," and ("&A5&")","")
& IF(A6<>""," and ("&A6&")","")
& IF(A7<>""," and ("&A7&")","")
& IF(A8<>""," and ("&A8&")","")
& IF(A9<>""," and ("&A9&")","")
```

---

## 6. 검색창 B5 최종 QUERY 수식

`검색창!B5`에 들어가는 핵심 수식이다.

```gs
=IF(
  AND(
    검색창!B1="",
    COUNTA(검색창!B3:I3)=0
  ),
  "검색 필터 조건을 넣어주세요.",
  IFERROR(
    QUERY(
      '쿠라s 노래책~!'!A2:R,
      "select Col1,Col2,Col3,Col4,Col5,Col6,Col9,Col13,Col18
       where Col1 is not null"
      & IF(QUERY_BUILDER!A1<>""," and ("&QUERY_BUILDER!A1&")","")
      & IF(QUERY_BUILDER!A2<>""," and ("&QUERY_BUILDER!A2&")","")
      & IF(QUERY_BUILDER!A3<>""," and ("&QUERY_BUILDER!A3&")","")
      & IF(QUERY_BUILDER!A4<>""," and ("&QUERY_BUILDER!A4&")","")
      & IF(QUERY_BUILDER!A5<>""," and ("&QUERY_BUILDER!A5&")","")
      & IF(QUERY_BUILDER!A6<>""," and ("&QUERY_BUILDER!A6&")","")
      & IF(QUERY_BUILDER!A7<>""," and ("&QUERY_BUILDER!A7&")","")
      & IF(QUERY_BUILDER!A8<>""," and ("&QUERY_BUILDER!A8&")","")
      & IF(QUERY_BUILDER!A9<>""," and ("&QUERY_BUILDER!A9&")","")
      ,
      0
    ),
    "조건에 맞는 곡이 없습니다."
  )
)
```

주의:

- Google Sheets에서 시트명이 `쿠라's 노래책~!`처럼 작은따옴표를 포함할 경우 수식에서 escape 문제가 생긴다.
- 현재 xlsx 내 실제 시트명은 `쿠라s 노래책~!`로 확인된다.
- Google Sheets 실제 원본의 시트명이 다르면 반드시 수식의 시트명도 맞춰야 한다.

---

## 7. TAXONOMY 시트 구조

### 7.1 컬럼

| 열 | 목록 |
|---|---|
| A | 언어 |
| B | 장르 |
| C | 상황 |
| D | 대상 |
| E | 감정 |
| F | 출처유형 |
| G | 매체 |
| H | 기타태그 |

### 7.2 드롭다운 범위 권장

| 검색창 셀 | 범위 |
|---|---|
| B3 | `TAXONOMY!A3:A` |
| C3 | `TAXONOMY!B3:B` |
| D3 | `TAXONOMY!C3:C` |
| E3 | `TAXONOMY!D3:D` |
| F3 | `TAXONOMY!E3:E` |
| G3 | `TAXONOMY!F3:F` |
| H3 | `TAXONOMY!G3:G` |
| I3 | `TAXONOMY!H3:H` |

빈 선택지는 드롭다운 맨 위에 빈 행을 두는 방식으로 처리 가능하다.

---

## 8. 현재 확인된 테스트 케이스

### 8.1 자유검색 + 언어

| 입력 | 기대 결과 |
|---|---|
| B1=`요네즈`, B3=`일본어` | `Lemon` |
| B1=`요네즈`, B3=`한국어` | 조건 없음 |

### 8.2 언어 + 장르 다중

| 입력 | 기대 결과 |
|---|---|
| B3=`일본어`, C3=`팝, 발라드` | 일본어 곡 중 장르1/장르2가 팝 또는 발라드인 곡 |

### 8.3 전체 필터 조합

| 필터 | 값 |
|---|---|
| 언어 | 일본어 |
| 장르 | 팝, 발라드 |
| 상황 | 사랑 |
| 대상 | 재회 |
| 감정 | 그리움 |
| 출처유형 | OST |
| 매체 | 애니 |

기대 결과:

```text
なんでもないや
```

---

## 9. 현재 설계의 취약점

| 취약점 | 설명 | 대응 |
|---|---|---|
| xlsx 변환 | Google Sheets 전용 함수가 깨질 수 있음 | 이 문서 수식을 source of truth로 둠 |
| taxonomy 과다 | 드롭다운이 길어짐 | v1.2에서 압축/고급필터 분리 |
| M열 비고 contains 검색 | 출처유형/매체/기타태그가 완전 분리 검색은 아님 | v1.1 이후 N/O/Q 직접 검색 검토 |
| 다중선택 구분자 | Google Sheets 다중칩이 쉼표 문자열로 들어오는 전제 | 구분자가 달라지면 SPLIT 구분자 수정 |
| 사용자 동시 편집 | 전체 editor 공개 시 충돌 가능 | 보호 범위/백업/복구 절차 필요 |

---

## 10. 다음 구조로 리팩토링 예정

현재:

```text
검색창 → QUERY_BUILDER → 검색창 결과
```

v1.0 목표:

```text
검색_UI_PC
↓
검색_ENGINE
↓
QUERY_BUILDER
↓
DB_RAW
↓
CARD_HELPER
↓
검색_UI_PC 결과 카드
```

실제 구현은 기존 `검색창`을 `검색_ENGINE`으로 보존하고, 새 UI 시트를 wrapper로 얹는 방식이 안전하다.

