# 🗄️ Supabase PostgreSQL 실습 DB 접속 및 DBeaver 설정 가이드

본 문서는 부트캠프 실습용 Supabase PostgreSQL 데이터베이스 접속 정보와 **DBeaver CE** 연동 매뉴얼입니다.

---

## 📌 1. 데이터베이스 접속 파라미터

| 항목 | 설정값 | 비고 |
| :--- | :--- | :--- |
| **Host** | `aws-0-ap-southeast-1.pooler.supabase.com` | Session Pooler 주소 |
| **Port** | `5432` | PostgreSQL 기본 포트 |
| **Database** | `postgres` | 기본 데이터베이스명 |
| **User** | `bootcamp_kim.szacvaqcsmnhyrhwpbtb` | 김항진 이사님 전용 계정 |
| **Password** | `2TawPzCJV0synzTBB2Ca` | |
| **SSL Mode** | `require` (필수) | SSL 보안 연결 필요 |

---

## 🖥️ 2. DBeaver CE 연결 세팅 (3단계)

1. **DBeaver 실행**:
   * 터미널에서 `dbeaver` 입력 또는 시작 메뉴에서 실행.
2. **새 연결 생성**:
   * 좌측 상단 **[새 데이터베이스 연결 (콘센트 플러그 모양)]** 클릭 ➡️ **PostgreSQL** 선택 ➡️ **[Next]**
3. **접속 정보 입력**:
   * **Main 탭**:
     * **Host**: `aws-0-ap-southeast-1.pooler.supabase.com`
     * **Database**: `postgres`
     * **Port**: `5432`
     * **Username**: `bootcamp_kim.szacvaqcsmnhyrhwpbtb`
     * **Password**: `2TawPzCJV0synzTBB2Ca`
   * **SSL 탭**:
     * **[Use SSL]** 체크 박스 선택 ✅
     * **SSL mode**: `require` 선택
4. **[Test Connection]** 클릭 ➡️ 연결 성공 확인 후 **[Finish]** 클릭!

---

## 🔍 3. 조회 및 실습 스키마 현황 (검증 완료)

2026-09-07 실제 접속 테스트를 완료하였으며, 현재 다음 스키마들이 정상 조회됩니다:
* `uwf_zeek` (Zeek 네트워크 보안 로그)
* `lanl_cyber1` (LANL 사이버 보안 로그 / dim_computer, fact_auth, fact_dns 등)
* `otrf_sysmon` (Sysmon 엔드포인트 보안 로그)
* `telecom_cdr` (통신사 통화 기록)
* `commodity_trading` (원자재 트레이딩)
* `manufacture` (제조 공정 데이터)
* `ocsf_aws` (AWS 보안 표준 로그)
* `bank_txn` (은행 거래 데이터)

> [!TIP]
> **5번 보안 실습 데이터 적재 시**:  
> `CREATE SCHEMA security;` 스키마 생성 후 테이블을 생성하시면 Timbr 데이터소스(`bootcamp_supabase`)에서 그대로 인식됩니다.
