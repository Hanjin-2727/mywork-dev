# 📊 [Sequence Diagram] K-BTF 5대 핵심 업무 흐름 시퀀스 다이어그램 명세서
**문서 식별자**: `SEQ-KBTF-2026-V2.2`  
**작성 일자**: 2026-10-10  
**보안 원칙**: CSAP '하' 등급 충족 & Zero-PII 3-Tier 아키텍처 전면 적용  

---

## 📌 목차
1. [시퀀스 1: 2G폰 어르신 대면 등록 및 익명 Custodial DID/VC 발급](#1-시퀀스-1-2g폰-어르신-대면-등록-및-익명-custodial-didvc-발급)
2. [시퀀스 2: 2주 단위 엑셀 일괄 업로드 및 다계층 VC 배치 발급](#2-시퀀스-2-2주-단위-엑셀-일괄-업로드-및-다계층-vc-배치-발급)
3. [시퀀스 3: 경로식당 0.05초 초고속 선확인 및 비동기 Verifier 검증](#3-시퀀스-3-경로식당-005초-초고속-선확인-및-비동기-verifier-검증)
4. [시퀀스 4: 카드 미지참자 현장 에지 사설망(Edge LAN) 검증 및 구제](#4-시퀀스-4-카드-미지참자-현장-에지-사설망edge-lan-검증-및-구제)
5. [시퀀스 5: 부정/중복 수령 (현장식사 + 도시락) 실시간 차단](#5-시퀀스-5-부정중복-수령-현장식사--도시락-실시간-차단)

---

## 1. 시퀀스 1: 2G폰 어르신 대면 등록 및 익명 Custodial DID/VC 발급

> **핵심 보안 설계**:
> - 성명, 생년월일, 동호수 등 법적 개인정보는 **[Tier 1] 관리사무소 로컬 PC 폐쇄망**에서만 확인 및 저장됩니다.
> - 클라우드로는 **개인정보가 단 1바이트도 전송되지 않으며(Zero-PII)**, 오직 공카드에서 읽은 난수 `[NFC UID] + [자격코드]`만 전송되어 익명 Custodial DID가 생성됩니다.

```mermaid
sequenceDiagram
    autonumber
    actor Senior as 👴 어르신 (2G폰 소지자)
    actor Worker as 👩‍💼 창구 관리자 (복지사)
    participant LocalPC as 💻 관리사무소 로컬 PC (Tier 1 폐쇄망)
    participant Reader as 📟 창구 NFC 등록기
    participant AppServer as 🖥️ 본과제 AppServer (CSAP '하')
    participant Issuer as 🏛️ Issuer 서버
    participant KMS as 🔐 Custodial KMS
    participant Ledger as 📦 DID 레지스트리
    participant PDS as 🗄️ 암호화 PDS 저장소

    Senior->>Worker: 1. 관리소 방문 (신분증 제시: "김철수, 101동 1204호")
    
    rect rgb(255, 241, 240)
    Note over Worker,LocalPC: [Tier 1 로컬 폐쇄망 본인확인] 외부 인터넷 연결 전무
    Worker->>LocalPC: 2. 거주자 명부 조회 (성명/주민번호/동호수)
    LocalPC-->>Worker: 3. 입주민 수급자격 확인 승인 (생계급여 대상)
    end
    
    Worker->>Reader: 4. 기성품 공카드(NFC 목걸이) 태깅
    Reader-->>Worker: 5. NFC 하드웨어 고유 UID (7-Byte) 획득
    
    rect rgb(255, 241, 240)
    Worker->>LocalPC: 6. [로컬 매핑 DB 저장] [NFC UID] ↔ [성명, 동호수, 생년월일]<br/>※ 개인정보는 로컬 PC 폐쇄망에 100% 잔류!
    end
    
    rect rgb(240, 249, 255)
    Note over LocalPC,Issuer: [클라우드 전송: Zero-PII] 개인정보 원천 배제, 오직 UID와 자격코드만 전송
    LocalPC->>AppServer: 7. 익명 계정 및 VC 발급 요청 ({ uid: "04A1B2...", tier: "TIER_A" })
    AppServer->>Issuer: 8. DID 생성 요청 (개인정보 일체 미포함)
    Issuer->>KMS: 9. Ed25519 키쌍 생성 요청
    KMS->>KMS: 난수 기반 개인키 생성 및 보안금고 보관
    KMS-->>Issuer: Public Key 반환
    Issuer->>Ledger: 10. DID Document 온체인 등록 (did:kbtf:resident:난수 + Public Key만 저장)
    Issuer-->>AppServer: 11. 생성된 DID 반환
    end
    
    rect rgb(236, 253, 245)
    Note over AppServer,PDS: [순수 자격화 Dual-VC 발급 및 PDS 저장]
    AppServer->>Issuer: 12. [익명 주민증 VC] & [익명 수급카드 VC] 발급 요청 ({ is_eligible: true })
    Issuer->>Issuer: 발급기관 키로 2종 익명 VC 전자서명 생성
    Issuer->>PDS: 13. 발급된 VC 암호화 저장 (DID 바인딩)
    Issuer->>Ledger: 14. VC 검증용 해시 온체인 앵커링
    Issuer-->>AppServer: 15. 발급 완료 응답
    end
    
    Note over AppServer: 16. 클라우드 저장소 적재: [NFC UID] ↔ [Custodial DID] ↔ [익명 VC 목록] (Zero-PII)
    AppServer-->>LocalPC: 17. 발급 완료 수신
    LocalPC-->>Worker: 18. 등록 완료 화면 표출
    Worker->>Senior: 19. 실물 NFC 목걸이 카드 교부 ("식당에서 찍으시면 됩니다")
```

---

## 2. 시퀀스 2: 2주 단위 엑셀 일괄 업로드 및 다계층 VC 배치 발급

> **핵심 보안 설계**:
> - 엑셀 파일 내의 인적사항(성명, 동호수)은 **로컬 PC에서 사전 분리**됩니다.
> - 클라우드로는 **식사유형별 `NFC UID` 목록만 전송**되어, 14일 유효기간을 갖는 `[2-1] 현장식사 VC`와 `[2-2] 도시락 VC`가 대량 병렬 전자서명 발급됩니다.

```mermaid
sequenceDiagram
    autonumber
    actor WelfareWorker as 👩‍💼 복지관 행정 복지사
    participant EdgeTerminal as 📟 현장 센스 단말 (리더기 캐시)
    participant LocalAdmin as 💻 관리사무소 로컬 PC (Tier 1)
    participant AppServer as 🖥️ 본과제 AppServer (CSAP '하')
    participant Issuer as 🏛️ Issuer 서버
    participant PDS as 🗄️ 암호화 PDS 저장소

    WelfareWorker->>LocalAdmin: 1. 2주 주기 수급자 명단 엑셀 업로드<br/>(로컬 컬럼: 성명, 동호수, 카드UID, 식사유형)
    
    rect rgb(255, 241, 240)
    Note over LocalAdmin: [로컬 개인정보 분리 및 비식별화]<br/>① 성명/동호수는 로컬 폐쇄망 DB에만 갱신<br/>② 클라우드 발송용 비식별 페이로드 생성:<br/>   - 현장식사(2-1): UID 목록 180건<br/>   - 도시락(2-2): UID 목록 40건
    end

    LocalAdmin->>AppServer: 2. [Zero-PII 배치 요청] 비식별 UID 및 식사유형 코드 전송
    
    rect rgb(254, 249, 195)
    Note over AppServer,PDS: [단기 유효기간(2주) 익명 VC 배치 발급]
    AppServer->>Issuer: 3. [Batch 발급 API] 2-1 현장식사 VC (180건) & 2-2 도시락 VC (40건)<br/>(유효기간: 발급일 ~ 14일 후 만료)
    Issuer->>Issuer: 대량 전자서명 병렬 생성
    Issuer->>PDS: 4. 대상자 DID별 신규 단기 VC 암호화 적재 (기존 회차 만료 처리)
    Issuer-->>AppServer: 5. 배치 발급 성공 응답 (총 220건)
    end

    Note over AppServer: 6. AppServer VC 라우팅 캐시 동기화 (UID별 최신 활성 VC 상태값 갱신)
    
    AppServer-)EdgeTerminal: 7. [사설망 푸시] 현장 리더기 로컬 유효 UID 화이트리스트 동기화
    EdgeTerminal-->>AppServer: 8. 동기화 완료 수신 (Ack)
    AppServer-->>LocalAdmin: 9. "총 220명 2주 식사 VC 갱신 완료" 대시보드 리포트
```

---

## 3. 시퀀스 3: 경로식당 0.05초 초고속 선확인 및 비동기 Verifier 검증

> **핵심 보안 및 성능 설계**:
> - **1단계 (현장 0.05초)**: 센서 단말이 캐시된 공개키로 즉시 녹색 LED 및 음성 안내를 출력하여 어르신이 멈춤 없이 식판을 들고 통과합니다.
> - **2단계 (클라우드 비동기)**: 백그라운드로 전송된 `[NFC UID] + [Sensor ID]`에 대해 Custodial Agent가 익명 VP를 동적 조합하고, Verifier 서버가 검증 후 **정부 과제 KPI 실적 원장에 영구 로깅**합니다.

```mermaid
sequenceDiagram
    autonumber
    actor Senior as 👴 어르신 (NFC 목걸이 카드)
    participant Sensor as 📟 경로식당 센스 단말 (Line 1 식사 리더기)
    participant LocalKey as 🔑 단말 로컬 Issuer 공개키
    participant Speaker as 📢 단말 음성/LED 모듈
    participant AppServer as 🖥️ 본과제 AppServer (Custodial Agent)
    participant Verifier as 🔍 Verifier 서버 (정부실적 원장/KPI 로깅)

    Note over Sensor,LocalKey: [사전준비] 단말에 Issuer 공개키 및 화이트리스트 캐싱 완료
    
    Senior->>Sensor: 1. 식사 라인 리더기에 NFC 목걸이 태깅 (삑-)
    
    rect rgb(239, 246, 255)
    Note over Sensor,Speaker: [1단계: 현장 0.05초 초고속 선확인] 대기열 병목 원천 차단
    Sensor->>LocalKey: 센서 로컬 공개키로 화이트리스트 및 무결성 대조
    LocalKey-->>Sensor: 서명 유효성 확인 완료 (소요시간 0.05초)
    Sensor->>Speaker: 2. "띵동! 반갑습니다. 맛있게 드세요." 음성 출력 & 🟢 녹색 LED 점등
    Note over Senior: 어르신 즉시 식판을 들고 배식구 통과 (현장 체류 0초)
    end
    
    rect rgb(236, 253, 245)
    Note over Sensor,Verifier: [2단계: Zero-PII 비동기 검증 및 과제 KPI 실적 로깅]
    Sensor-)AppServer: 3. [비동기 전송] 센서 ID(SENSOR_MEAL_01) + 카드 UID(04A1B2...) 전송<br/>※ 개인정보 일체 미포함!
    
    Note over AppServer: 4. [Custodial Agent 지능형 VP 조합]<br/>① 수신된 UID의 VC 풀 조회<br/>② Sensor ID 정책에 따라 [2-1 현장식사 VC] 선별<br/>③ 인적사항 없는 최소공개 VP 즉시 동적 생성 및 서명
    
    AppServer->>Verifier: 5. [VP 검증 요청] 생성된 익명 VP 제출 (전자서명 포함)
    Verifier->>Verifier: 6. 블록체인 DID 상태 확인 및 익명 자격(is_eligible: true) 유효성 검증
    Verifier->>Verifier: 7. [정부실적 원장] 정상 식사 인증 트랜잭션 자체 영구 로깅 (과제 KPI 실적 인정)
    Verifier-->>AppServer: 8. 최종 검증 성공 응답 (Status: 200 OK, TxId 반환)
    end
```

---

## 4. 시퀀스 4: 카드 미지참자 현장 에지 사설망(Edge LAN) 검증 및 구제

> **핵심 보안 설계**:
> - 카드를 분실하거나 집에 두고 온 어르신의 구두 본인확인은 **현장 에지 사설망(192.168.0.x Wi-Fi)** 내부에서만 처리되며, 외부 공용 인터넷(WAN)으로 나가지 않습니다.
> - 클라우드로는 **정규 태깅과 동일한 `[NFC UID] + [Sensor ID]`만 전송**되므로 클라우드의 Zero-PII 및 CSAP '하' 등급이 완벽히 유지됩니다.

```mermaid
sequenceDiagram
    autonumber
    actor Senior as 👵 어르신 (카드 미지참자)
    actor Officer as 👮 공익요원 (현장 확인자)
    participant AdminPhone as 📱 관리자단말(폰) (로컬 브라우저)
    participant LocalPC as 💻 관리사무소 로컬 PC (192.168.0.50 폐쇄망)
    participant AppServer as 🖥️ 본과제 AppServer (Custodial Agent)
    participant Verifier as 🔍 Verifier 서버 (정부실적 원장/KPI 로깅)

    Note over Senior,Officer: 어르신을 일반 배식 라인 옆 전용 확인석으로 안내 (정체 방지)
    Senior->>Officer: 1. 구두 신원 제시 ("101동 1204호, 850412, 김철수요.")
    Officer->>AdminPhone: 2. 화면에 동·호수 / 생년월일 입력
    
    rect rgb(255, 241, 240)
    Note over AdminPhone,LocalPC: [현장 에지 사설망 로컬 조회 (Edge LAN Air-Gap)] 외부 인터넷(WAN) 미경유
    AdminPhone->>LocalPC: 3. 사설 Wi-Fi 내부 HTTP 조회 (http://192.168.0.50:8000/search)
    Note over LocalPC: 관리사무소 폐쇄망 DB 검색<br/>101동 1204호 거주자 일치 확인 ➡️ 등록된 [NFC UID] 추출
    LocalPC-->>AdminPhone: 4. 로컬 응답: 성명 초성(ㄱㅊㅅ) 확인 & 매핑된 [NFC UID] 반환
    end
    
    Officer->>AdminPhone: 5. 일치 확인 후 화면의 [배식 승인] 터치
    AdminPhone->>AdminPhone: 6. "띵동! 확인되었습니다. 맛있게 드세요." 음성 출력 & 🟢 녹색 승인 화면
    Note over Senior: 어르신 식판 수령하여 식사 진행
    
    rect rgb(236, 253, 245)
    Note over AdminPhone,Verifier: [클라우드 전송: 정규 태깅과 100% 동일 규격 (Zero-PII)]
    AdminPhone-)AppServer: 7. [비동기 전송] 오직 [NFC UID] + [Sensor_ID]만 전송!<br/>※ 구두 개인정보는 클라우드로 1바이트도 유출되지 않음!
    
    Note over AppServer: 8. 정규 시퀀스 3과 100% 동일하게 익명 VP 조합 및 서명
    AppServer->>Verifier: 9. [VP 검증 요청] 익명 VP 제출 (reason: MANUAL_PASS)
    Verifier->>Verifier: 10. [정부실적 원장] MANUAL_PASS 트랜잭션 자체 영구 기록 (과제 KPI 로깅)
    Verifier-->>AppServer: 11. 실적 앵커링 완료 Ack 및 결과 반환
    end
    
    rect rgb(254, 242, 242)
    Note over AdminPhone: [14:00 배식 종료 후 세션 자동 종료]<br/>스마트폰 브라우저 캐시 및 임시 토큰 완전 소멸 (단말 분실 시 유출 위험 0%)
    end
```

---

## 5. 시퀀스 5: 부정/중복 수령 (현장식사 + 도시락) 실시간 차단

> **핵심 보안 설계**:
> - 개인정보 조회 없이 오직 `[NFC UID]`와 `[Sensor ID]`의 당일 이용 기록만을 조회하여 상호 배제 차단을 수행합니다.

```mermaid
sequenceDiagram
    autonumber
    actor Abuser as 👤 중복 수령 시도자 (식사 완료자)
    participant Sensor2 as 📟 도시락 배부처 센스 단말 (Line 2)
    participant Speaker as 📢 단말 음성/경고 모듈
    participant AppServer as 🖥️ 본과제 AppServer (VC 라우터)

    Note over Abuser: 12:10에 이미 Line 1에서 현장식사 완료한 상태
    Abuser->>Sensor2: 1. 12:40 도시락 배부처 리더기에 동일 NFC 카드 태깅
    
    Sensor2-)AppServer: 2. 센서 ID(SENSOR_BENTO_02) + 카드 UID 전송 (Zero-PII)
    
    Note over AppServer: 3. [VC 라우터 중복 검사 로직]<br/>① 카드 UID로 당일 이용 상태 조회<br/>② 결과: 12:10 SENSOR_MEAL_01 식사 완료 기록 발견!<br/>③ 판정: 중복 수령(Bunker) 시도 감지 (차단)
    
    AppServer-->>Sensor2: 4. 승인 거부 응답 (Status: 403, Reason: ALREADY_DINED_TODAY)
    Sensor2->>Speaker: 5. 🟡 황색 LED & "오늘 이미 식사를 완료하셨습니다." 경고 음성 출력
    Note over Abuser: 도시락 지급 차단 및 현장 관리자 안내 유도
```

---

## 📊 시퀀스별 특성 비교 매트릭스

| 구분 | 주요 트리거 | 통신 구간 | 전송 데이터 | 소요 시간 | 보안 특성 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **시퀀스 1** | 창구 대면 등록 | 온프레미스 ➔ 클라우드 | 난수 UID, 자격코드 | 1~2초 | 로컬 폐쇄망 개인정보 격리 |
| **시퀀스 2** | 2주 엑셀 업로드 | 온프레미스 ➔ 클라우드 | 비식별 UID 220건 목록 | 3~5초 (배치) | 로컬 전처리 비식별화 |
| **시퀀스 3** | 경로식당 카드 태깅 | 센서 ➔ 클라우드 (비동기) | `UID` + `Sensor ID` | **0.05초 (선확인)** | 무자각 초고속 통과, KPI 로깅 |
| **시퀀스 4** | 카드 미지참 구두 진술 | 에지 사설망 ➔ 클라우드 | `UID` + `Sensor ID` | 5초 (신원확인) | 192.168.0.x 에어갭 사설망 격리 |
| **시퀀스 5** | 당일 중복 수령 시도 | 센서 ➔ 클라우드 | `UID` + `Sensor ID` | 0.1초 | 실시간 상호 배제 차단 (HTTP 403) |
