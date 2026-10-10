# 🗄️ [ERD & Schema] K-BTF 2-Tier 분리 데이터 모델 및 DDL 명세서
**문서 식별자**: `ERD-KBTF-2026-V2.2`  
**작성 일자**: 2026-10-10  
**보안 원칙**: CSAP '하' 등급 충족 & Zero-PII 2-Tier 데이터 격리 아키텍처 전면 적용  

---

## 📌 1. 아키텍처 개요 및 2-Tier 데이터 격리 모델

국정원 보안성 검토 및 과기정통부 CSAP '하' 등급 인증 기준을 100% 충족하기 위해, 데이터베이스를 물리적/논리적으로 완전히 분리된 2개의 독립 저장소로 설계합니다.

```mermaid
graph TB
    subgraph Tier1_DB ["🏛️ [Tier 1] 관리사무소 로컬 DB (On-Premise 폐쇄망)"]
        direction TB
        T1_1["local_residents<br/>(개인식별정보 ↔ NFC UID 매핑)"]
        T1_2["local_card_inventory<br/>(실물 카드 재고 및 시리얼 관리)"]
        T1_3["local_manual_audit_logs<br/>(미지참자 구두확인 감사기록)"]
        T1_1 --- T1_2
        T1_1 --- T1_3
    end

    subgraph Tier3_DB ["☁️ [Tier 3] 공공 클라우드 DB (CSAP '하' Zero-PII)"]
        direction TB
        T3_1["custodial_wallets<br/>(NFC UID ↔ 익명 DID/공개키)"]
        T3_2["verifiable_credentials<br/>(익명 자격증명 VC 원장)"]
        T3_3["sensor_policies<br/>(Sensor ID ↔ 정책 매핑)"]
        T3_4["dining_verification_logs<br/>(실시간 검증 트랜잭션 / 7일 보존)"]
        T3_5["daily_kpi_aggregates<br/>(정부 과제 실적 영구 원장)"]
        
        T3_1 --- T3_2
        T3_1 --- T3_4
        T3_3 --- T3_4
        T3_4 --- T3_5
    end

    Tier1_DB -. "개인정보 전달 불가 (에어갭 격리)<br/>오직 난수 [NFC UID]만 전송" .-> Tier3_DB

    style Tier1_DB fill:#fff1f0,stroke:#f5222d,stroke-width:2px
    style Tier3_DB fill:#f6ffed,stroke:#52c41a,stroke-width:2px
```

---

## 📊 2. 전체 엔티티 관계도 (Mermaid ER Diagram)

```mermaid
erDiagram
    %% ==========================================
    %% [Tier 1] On-Premise 관리사무소 로컬 폐쇄망
    %% ==========================================
    LOCAL_RESIDENTS {
        uuid resident_id PK "거주자 내부 고유 식별자"
        string resident_name "성명 (예: 홍길동)"
        string birth_date "생년월일 (YYMMDD)"
        string building_no "동 (예: 101동)"
        string room_no "호수 (예: 1204호)"
        string phone_number "연락처 (선택)"
        string nfc_uid UK "하드웨어 카드 고유번호 (7-Byte)"
        string welfare_tier "수급 자격 등급 (TIER_A/B/C)"
        string status "입주 상태 (ACTIVE/MOVED_OUT)"
        timestamp created_at "등록 일시"
    }

    LOCAL_CARD_INVENTORY {
        uuid card_id PK "카드 관리 식별자"
        string card_serial UK "실물 카드 인쇄 시리얼번호"
        string nfc_uid UK "NFC 칩 고유번호"
        string inventory_status "재고 상태 (AVAILABLE/ISSUED/LOST)"
        timestamp issued_at "교부 일시"
    }

    LOCAL_MANUAL_AUDIT_LOGS {
        uuid log_id PK "감사 로그 식별자"
        uuid resident_id FK "거주자 ID 참조"
        string officer_name "확인 공익요원/복지사 성명"
        string check_reason "미지참 사유 (LOST/HOME/DAMAGED)"
        timestamp checked_at "확인 일시"
    }

    LOCAL_RESIDENTS ||--o| LOCAL_CARD_INVENTORY : "보유 카드"
    LOCAL_RESIDENTS ||--o{ LOCAL_MANUAL_AUDIT_LOGS : "구두 확인 이력"

    %% ==========================================
    %% [Tier 3] 공공 클라우드 CSAP '하' Zero-PII
    %% ==========================================
    CUSTODIAL_WALLETS {
        string nfc_uid PK "카드 하드웨어 고유번호 (단일 키)"
        string custodial_did UK "W3C 표준 DID 식별자"
        string public_key "Ed25519 공개키"
        timestamp registered_at "등록 일시"
        boolean is_active "활성 여부"
    }

    VERIFIABLE_CREDENTIALS {
        uuid vc_id PK "VC 고유 UUID"
        string nfc_uid FK "지갑 참조 키"
        string credential_type "자격증명 종류 (MEAL/BENTO/RESIDENT)"
        string service_domain "서비스 도메인 코드"
        boolean is_eligible "자격 적격 여부 플래그 (True/False)"
        string subsidy_tier "지원 등급 (TIER_A)"
        timestamp issuance_date "발급 일시"
        timestamp expiration_date "만료 일시"
        jsonb proof "암호학적 전자서명 페이로드"
    }

    SENSOR_POLICIES {
        string sensor_id PK "센스 단말 고유 식별자"
        string location_name "설치 위치 (경로식당 1라인/2라인 등)"
        string target_vc_type "요구 자격증명 유형"
        int daily_limit "1일 최대 이용 가능 횟수 (기본 1회)"
        boolean is_active "센서 활성 상태"
    }

    DINING_VERIFICATION_LOGS {
        uuid tx_id PK "검증 트랜잭션 UUID"
        string sensor_id FK "센서 참조 키"
        string nfc_uid FK "지갑 참조 키"
        string result_status "판정 결과 (APPROVED/REJECTED/DUPLICATE)"
        string verification_method "인증 방식 (NFC_TAG/MANUAL_PASS)"
        string failure_reason "실패/거부 사유"
        timestamp verified_at "검증 일시 (7일 후 자동 파기)"
    }

    DAILY_KPI_AGGREGATES {
        date report_date PK "집계 일자"
        int total_meal_count "일일 총 현장 식사 건수"
        int total_bento_count "일일 총 도시락 수령 건수"
        int total_unique_users "순 수혜자 수"
        int duplicate_prevented "중복 수령 차단 건수"
        int manual_pass_count "미지참 구두 구제 건수"
        string onchain_tx_hash "블록체인 배치 앵커링 해시"
        timestamp updated_at "최종 갱신 일시"
    }

    CUSTODIAL_WALLETS ||--o{ VERIFIABLE_CREDENTIALS : "보유 VC 풀"
    CUSTODIAL_WALLETS ||--o{ DINING_VERIFICATION_LOGS : "트랜잭션 발생"
    SENSOR_POLICIES ||--o{ DINING_VERIFICATION_LOGS : "센서 검증 실행"
    DINING_VERIFICATION_LOGS }o--|| DAILY_KPI_AGGREGATES : "일일 집계 요약"
```

---

## 💻 3. 프로덕션 PostgreSQL DDL 스크립트

### 3.1. [Tier 1] 관리사무소 로컬 PC 폐쇄망 DB (`kbtf_local_db`)
*(외부 인터넷이 차단된 관리사무소 로컬 컴퓨터에서 단독 구동)*

```sql
-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. 거주자 인적사항 및 카드 매핑 테이블 (폐쇄망 전용)
CREATE TABLE local_residents (
    resident_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    resident_name VARCHAR(50) NOT NULL,
    birth_date CHAR(6) NOT NULL, -- YYMMDD
    building_no VARCHAR(20) NOT NULL, -- e.g. '101동'
    room_no VARCHAR(20) NOT NULL,     -- e.g. '1204호'
    phone_number VARCHAR(20),
    nfc_uid VARCHAR(32) UNIQUE NOT NULL, -- 7-Byte NFC Hex UID (e.g. '04:A1:B2:C3:D4:E5:F6')
    welfare_tier VARCHAR(20) DEFAULT 'TIER_A' CHECK (welfare_tier IN ('TIER_A', 'TIER_B', 'TIER_C')),
    status VARCHAR(20) DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE', 'MOVED_OUT', 'SUSPENDED')),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_local_residents_search ON local_residents (building_no, room_no, birth_date);
CREATE INDEX idx_local_residents_nfc ON local_residents (nfc_uid);

-- 2. 실물 NFC 목걸이 카드 재고 관리 테이블
CREATE TABLE local_card_inventory (
    card_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    card_serial VARCHAR(50) UNIQUE NOT NULL,
    nfc_uid VARCHAR(32) UNIQUE NOT NULL,
    inventory_status VARCHAR(20) DEFAULT 'AVAILABLE' CHECK (inventory_status IN ('AVAILABLE', 'ISSUED', 'LOST', 'DAMAGED')),
    issued_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 3. 미지참자 현장 에지 사설망 구두 확인 감사 로그 (폐쇄망 보관)
CREATE TABLE local_manual_audit_logs (
    log_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    resident_id UUID NOT NULL REFERENCES local_residents(resident_id) ON DELETE RESTRICT,
    officer_name VARCHAR(50) NOT NULL,
    check_reason VARCHAR(100) DEFAULT 'CARD_LEFT_HOME',
    checked_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
```

---

### 3.2. [Tier 3] 공공 클라우드 CSAP '하' Zero-PII DB (`kbtf_cloud_db`)
*(클라우드 상에 위치하며 개인 식별 정보는 일체 보관하지 않음)*

```sql
-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. 익명 Custodial 지갑 테이블 (Zero-PII)
CREATE TABLE custodial_wallets (
    nfc_uid VARCHAR(32) PRIMARY KEY, -- 하드웨어 난수 식별자
    custodial_did VARCHAR(120) UNIQUE NOT NULL, -- did:kbtf:resident:...
    public_key VARCHAR(128) NOT NULL, -- Ed25519 Public Key (Hex or Base58)
    is_active BOOLEAN DEFAULT TRUE,
    registered_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_custodial_wallets_did ON custodial_wallets (custodial_did);

-- 2. 익명 W3C Verifiable Credentials (자격증명 원장)
CREATE TABLE verifiable_credentials (
    vc_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nfc_uid VARCHAR(32) NOT NULL REFERENCES custodial_wallets(nfc_uid) ON DELETE CASCADE,
    credential_type VARCHAR(50) NOT NULL, -- 'CommunityMealCredential', 'WelfareBentoCredential'
    service_domain VARCHAR(50) NOT NULL,   -- 'WELFARE_MEAL', 'WELFARE_BENTO'
    is_eligible BOOLEAN DEFAULT TRUE NOT NULL,
    subsidy_tier VARCHAR(20) DEFAULT 'TIER_A',
    issuance_date TIMESTAMPTZ NOT NULL,
    expiration_date TIMESTAMPTZ NOT NULL,
    proof JSONB NOT NULL, -- Ed25519Signature2020 전자서명 블록
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_vc_uid_domain ON verifiable_credentials (nfc_uid, service_domain, expiration_date);

-- 3. 센스 단말 및 맥락 인지 정책 테이블
CREATE TABLE sensor_policies (
    sensor_id VARCHAR(50) PRIMARY KEY, -- 'SENSOR_MEAL_01', 'SENSOR_BENTO_02'
    location_name VARCHAR(100) NOT NULL,
    target_vc_type VARCHAR(50) NOT NULL,
    daily_limit INT DEFAULT 1 CHECK (daily_limit >= 1),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 4. 실시간 식사 검증 트랜잭션 로그 (7일 보존 라이프사이클 적용)
CREATE TABLE dining_verification_logs (
    tx_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    sensor_id VARCHAR(50) NOT NULL REFERENCES sensor_policies(sensor_id),
    nfc_uid VARCHAR(32) NOT NULL,
    result_status VARCHAR(30) NOT NULL CHECK (result_status IN ('APPROVED', 'REJECTED', 'DUPLICATE_BLOCKED')),
    verification_method VARCHAR(20) DEFAULT 'NFC_TAG' CHECK (verification_method IN ('NFC_TAG', 'MANUAL_PASS')),
    failure_reason VARCHAR(100),
    verified_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_dining_logs_uid_date ON dining_verification_logs (nfc_uid, verified_at);
CREATE INDEX idx_dining_logs_sensor_date ON dining_verification_logs (sensor_id, verified_at);

-- 5. 정부 과제 정량 실적 영구 보존 집계 원장 (KPI 달성 근거)
CREATE TABLE daily_kpi_aggregates (
    report_date DATE PRIMARY KEY,
    total_meal_count INT DEFAULT 0,
    total_bento_count INT DEFAULT 0,
    total_unique_users INT DEFAULT 0,
    duplicate_prevented INT DEFAULT 0,
    manual_pass_count INT DEFAULT 0,
    onchain_tx_hash VARCHAR(66), -- K-BTF 블록체인 배치 해시 앵커링
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_kpi_report_date ON daily_kpi_aggregates (report_date);
```

---

## 🛡️ 4. 데이터 수명주기(Lifecycle) 및 보안 파기 정책

1. **상세 식사 로그 (`dining_verification_logs`)**:
   - 국정원 보안 권고사항 및 프라이버시 보호를 위해 **7일 경과 시 자동 파기** 스케줄러(pg_cron / Daily Batch) 가동.
   - 파기 전 일별 통계는 `daily_kpi_aggregates`로 사전 집계되어 영구 보존.
2. **단기 식사 VC (`verifiable_credentials`)**:
   - 2주 단위 회차 만료 시 `expiration_date`를 초과한 레코드는 상태값을 `REVOKED` 처리하거나 익월 정산 후 압축 아카이빙.
