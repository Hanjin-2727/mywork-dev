# 🏛️ K-BTF 스마트 주거복지 플랫폼 (KBTF Project)
> **공공클라우드 CSAP '하' 등급 충족 및 Zero-PII 3-Tier 아키텍처 기반의 취약계층 복지 인증 시스템**  
> **기준 일자**: 2026-10-10 | **버전**: v2.2.0

---

## 📌 1. 프로젝트 개요

본 프로젝트는 영구임대단지(산남2-1단지 등) 취약계층 420세대를 대상으로, 모바일 앱 없이도 **실물 NFC 목걸이 카드**를 통해 경로식당에서 **0.05초 원터치 식사패스**를 지원하고, 국정원 보안성 검토 및 CSAP '하' 등급을 100% 충족하는 블록체인/DID 기반 주거복지 플랫폼입니다.

---

## 📁 2. 전체 디렉토리 구조

```text
~/mywork-dev/pj/kbtf/
├── README.md                      # [본 문서] 프로젝트 종합 안내서
├── .agents/
│   └── AGENTS.md                  # 프로젝트 공통 규칙 및 보안 거버넌스
├── 01_prd/
│   └── PRD.md                     # 제품 요구사항 정의서 (FR, NFR, CSAP 하 요건)
├── 02_sequence_diagram/
│   └── SEQUENCE_DIAGRAMS.md       # 5대 핵심 업무 흐름 시퀀스 다이어그램 (Mermaid)
├── 03_erd/
│   └── ERD_AND_SCHEMA.md          # 2-Tier 분리 데이터 모델 (On-Premise vs Cloud) 및 DDL
├── 04_wbs/
│   └── WBS_SCHEDULE.md            # 16주 4단계 애자일 릴리즈 WBS 및 Mermaid Gantt
├── src/                           # 백엔드 코어 소스코드
│   ├── run_demo.py                # 5대 핵심 시나리오 라이브 시뮬레이션 러너
│   ├── core/                      # W3C DID, VC/VP, Zero-PII 보안 모듈
│   │   ├── security.py            # PII 감사기 및 암호화 유틸
│   │   ├── did_kms.py             # Custodial KMS 및 W3C DID 매니저
│   │   └── vc_engine.py           # 익명 VC/VP 발급 및 검증 엔진
│   ├── tier1_local/               # Tier 1 관리사무소 로컬 PC 폐쇄망
│   │   ├── local_db.py            # 온프레미스 거주자 매핑 DB (개인정보 격리)
│   │   ├── resident_service.py    # 대면 등록(시퀀스1), 구두 신원 확인(시퀀스4)
│   │   ├── batch_preprocessor.py  # 2주 엑셀 비식별 전처리기(시퀀스2)
│   │   └── local_api_server.py    # 로컬 사설 Wi-Fi(192.168.0.50:8000) REST 서버
│   ├── tier3_cloud/               # Tier 3 CSAP '하' Zero-PII 클라우드
│   │   ├── cloud_db.py            # 클라우드 익명 저장소 (DID, VC, 정책, KPI)
│   │   ├── custodial_agent.py     # UID별 익명 VC 관리 및 무자각 VP 동적 조합
│   │   ├── verifier_service.py    # VP 서명 검증, 중복 차단(시퀀스5), KPI 로깅
│   │   ├── batch_anchorer.py      # 일일 18시 머클 해시 온체인 배치 앵커러
│   │   └── cloud_api_server.py    # 클라우드 REST API 서버
│   └── edge_terminal/             # 경로식당 센스 단말 모듈 (현장 에지)
│       └── sensor_reader.py       # 0.05초 로컬 선확인 & 비동기 클라우드 전송
└── tests/
    └── test_kbtf_end_to_end.py    # 5대 핵심 시나리오 E2E 통합 테스트 스위트
```

---

## ⚡ 3. 빠른 실행 가이드 (Quick Start)

### 3.1. 라이브 시뮬레이션 실행 (원클릭 데모)
5대 핵심 시나리오가 콘솔에서 실시간으로 시뮬레이션됩니다:
```bash
python3 src/run_demo.py
```

### 3.2. 자동화 테스트 실행 (E2E 검증)
```bash
python3 -m unittest discover -s tests -v
```

---

## 🛡️ 4. 3-Tier 보안 격리 원칙 (CSAP '하' 등급)

1. **[Tier 1] 관리사무소 로컬 PC 폐쇄망 (On-Premise Air-Gap)**
   - 개인정보(성명, 생년월일, 동·호수) ↔ NFC UID 매핑을 온프레미스에 100% 가두고 외부 공용 인터넷(WAN) 직접 연결을 원천 차단합니다.
2. **[Tier 2] 현장 에지 사설망 (Edge Private LAN / 반경 5m)**
   - 공유기 사설 Wi-Fi(192.168.0.x) 내부에서 미지참자 구두 확인(성명 초성 마스킹)을 처리하며, 외부로 개인정보가 유출되지 않습니다.
3. **[Tier 3] 공공클라우드 (CSAP '하' Zero-PII)**
   - 클라우드 DB 및 블록체인에는 개인정보가 **0.00%**이며, 하드웨어 난수 `[NFC UID]`만을 참조하여 무자각 VP 생성, 중복 차단, 정부 과제 실적 원장을 기록합니다.
