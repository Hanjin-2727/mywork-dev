# 📘 D2 다이어그램 가이드 & 토큰증권(STO) 4계층 권한형 아키텍처
**파일명**: `skill.y261014.d2lang.guide.md`  
**작성일**: 2026-10-14  
**작성자**: 🎨 Agent 2 (발표자료·디자인·프론트엔드) & 👑 Agent 1 (총괄 기획)  

---

## 1. 개요 및 핵심 요약

본 문서는 선언형 다이어그램 도구인 **D2(Declarative Diagramming Language)**를 활용하여 고품질 아키텍처 다이어그램을 작성할 때 반드시 준수해야 하는 **문법 규칙, 스타일링 가이드, 트러블슈팅 팁**과 함께, 실전 사례인 **「한국예탁결제원 분산원장 표준요건 기반 아발란체 서브넷 4계층 권한형 STO 아키텍처」** 전체 D2 코드를 체계적으로 수록한 스킬 가이드입니다.

---

## 2. D2lang 핵심 문법 및 복사/붙여넣기 트러블슈팅

### ⚠️ D2 Playground `Compile` 오류 발생 원인 및 주의점
* **원인**: D2에서 큰따옴표(`"..."`)로 묶인 단일 라인 문자열은 **중간에 물리적 줄바꿈(Enter/Wrap)이 발생하면 파싱 에러(Syntax Error)**가 발생합니다.
* 터미널이나 메신저, 코드 뷰어에서 텍스트를 드래그하여 복사할 때 **창 너비(Word Wrap)로 인해 한 줄이 여러 줄로 쪼개지면 빨간 물결 밑줄이 생기며 `▷ Compile`이 실패**합니다.
* **해결 원칙**:
  1. 문자열 내 줄바꿈은 반드시 `\n` 이스케이프 문자를 사용하여 한 줄로 작성합니다.
  2. 여러 줄의 설명이 필요한 경우 D2의 **Block String (`|md ... |`)** 문법을 활용합니다.

---

## 3. 실전 아키텍처: 토큰증권(STO) 4계층 권한형 모델

금융위원회 및 한국예탁결제원의 **「토큰증권 분산원장 표준요건 가이드라인」**을 100% 충족하도록 설계된 아발란체 에버그린(Evergreen) 서브넷 아키텍처입니다.

| 계층 | 명칭 | 핵심 권한형(Permissioned) 기능 |
| :--- | :--- | :--- |
| **Layer 4** | **제도 및 총량관리 계층** | • 한국예탁결제원 총량 상시 대사 및 초과발행(Over-issuance) 방지<br>• 이상 거래 감지 시 긴급 거래 동결 (`Emergency Pause`)<br>• 법원 판결/사법 집행에 따른 강제 소각 및 재발행권 보장 |
| **Layer 3** | **스마트 계약 계층** | • **ERC-3643** 토큰 표준 기반 온체인 신원 레지스트리 (`Identity Registry`)<br>• **온체인 실시간 KYC/AML 스크리닝** (FATF 제재 대상 및 불법 지갑 차단)<br>• 투자 한도 통제 (자본시장법상 일반투자자 연간 1천만 원 등 자동 강제) |
| **Layer 2** | **VM / 프로토콜 계층** | • **`TxAllowList`**: KYC 통과된 인가 지갑만 트랜잭션 제출 및 가스비 소모 허용 (외부 미인가 지갑 차단)<br>• **`ContractDeployerAllowList`**: 보안 심의 통과된 인가 금융기관만 스마트 계약 배포 |
| **Layer 1** | **합의 / 네트워크 계층** | • **권한형 검증 노드 (PoA Consensus)**: 불특정 다수의 퍼블릭 노드 진입 원천 차단<br>• 한국예탁결제원 + 인가 증권사(한화투자증권 등) 3개 이상 독립 기관 분산 합의 (51% 독점 방지) |

---

## 4. 완전한 D2 소스 코드 (`avalanche_subnet_architecture.d2`)

```d2
# ==============================================================================
# Avalanche Evergreen Subnet 4-Layer Permissioned Architecture for STO
# 한국예탁결제원 토큰증권 분산원장 표준요건 및 아발란체 서브넷 권한형 아키텍처
# ==============================================================================

direction: down

vars: {
  d2-config: {
    layout-engine: elk
    theme-id: 0
  }
}

# ------------------------------------------------------------------------------
# Layer 4: 거버넌스 및 총량관리 계층
# ------------------------------------------------------------------------------
layer4: "Layer 4. 제도 및 총량관리 계층 (Governance & Legal Oversight)" {
  style: {
    fill: "#F1F5F9"
    stroke: "#475569"
    stroke-width: 2
    border-radius: 12
  }

  ksd_governance: "🏛️ 한국예탁결제원 총량 대사 & 비상 거버넌스\n• 이상 발행 실시간 감지 및 거래 긴급 동결 (Emergency Pause)\n• 사법 집행 / 권리 구제 (법원 판결에 따른 강제 소각 및 재발행권)\n• 외감법·자본시장법 준수 총량 상시 대사" {
    shape: rectangle
    style: {
      fill: "#FFFFFF"
      stroke: "#1E293B"
      stroke-width: 2
      border-radius: 8
      shadow: true
    }
  }
}

# ------------------------------------------------------------------------------
# Layer 3: 스마트 계약 및 컴플라이언스 계층
# ------------------------------------------------------------------------------
layer3: "Layer 3. 스마트 계약 계층 (ERC-3643 토큰 표준 & On-chain Compliance)" {
  style: {
    fill: "#EFF6FF"
    stroke: "#3B82F6"
    stroke-width: 2
    border-radius: 12
  }

  compliance_rules: "규제 준수형 전송 제한 (Transfer Rules Engine)\n• 온체인 신원 레지스트리 (Identity Registry : 실명확인 지갑 화이트리스트)\n• 실시간 AML 스크리닝 (FATF 제재 대상 및 불법 지갑 자동 차단)\n• 투자 한도 통제 (자본시장법상 일반투자자 1천만원 등 한도 자동 강제)\n• 국가별 제재 (Geofencing) 적용" {
    shape: rectangle
    style: {
      fill: "#FFFFFF"
      stroke: "#2563EB"
      stroke-width: 2
      border-radius: 8
      shadow: true
    }
  }
}

# ------------------------------------------------------------------------------
# Layer 2: VM 및 프로토콜 사전컴파일 계층
# ------------------------------------------------------------------------------
layer2: "Layer 2. VM / 프로토콜 계층 (Avalanche Stateful Precompiles)" {
  style: {
    fill: "#FEF2F2"
    stroke: "#EF4444"
    stroke-width: 2
    border-radius: 12
  }

  tx_allow_list: "TxAllowList (트랜잭션 실행 통제)\n• KYC 완료된 인가 지갑만 트랜잭션 제출 허용\n• 미인가 외부 지갑의 가스비 소모 및 접근 원천 차단" {
    shape: rectangle
    style: {
      fill: "#FFFFFF"
      stroke: "#DC2626"
      stroke-width: 1.5
      border-radius: 8
      shadow: true
    }
  }

  contract_deployer: "ContractDeployerAllowList (배포 권한 통제)\n• 보안 심의를 통과한 금융기관/증권사만 스마트 계약 배포\n• 악성 컨트랙트 및 미인가 토큰 생성 차단" {
    shape: rectangle
    style: {
      fill: "#FFFFFF"
      stroke: "#DC2626"
      stroke-width: 1.5
      border-radius: 8
      shadow: true
    }
  }
}

# ------------------------------------------------------------------------------
# Layer 1: 분산 합의 및 네트워크 계층
# ------------------------------------------------------------------------------
layer1: "Layer 1. 합의 / 네트워크 계층 (Validator Permissioning & Infrastructure)" {
  style: {
    fill: "#ECFDF5"
    stroke: "#10B981"
    stroke-width: 2
    border-radius: 12
  }

  permissioned_validators: "허가형 검증 노드 (PoA Consensus)\n• 한국예탁결제원 + 인가 증권사(한화투자증권 등)만 블록 생성 참여\n• 불특정 다수의 퍼블릭 노드 진입 차단 (Permissioned)\n• 3개 이상 독립 기관 분산 합의 (단일 주체 51% 독점 방지 요건 충족)" {
    shape: rectangle
    style: {
      fill: "#FFFFFF"
      stroke: "#059669"
      stroke-width: 2
      border-radius: 8
      shadow: true
    }
  }
}

# ------------------------------------------------------------------------------
# 계층 간 연결 관계 (Inter-layer Flows)
# ------------------------------------------------------------------------------
layer4.ksd_governance -> layer3.compliance_rules: "총량 규제 준수 & 비상 정지 권한" {
  style: {
    stroke: "#475569"
    stroke-width: 2
  }
}

layer3.compliance_rules -> layer2.tx_allow_list: "온체인 KYC 지갑 자격 검증" {
  style: {
    stroke: "#2563EB"
    stroke-width: 2
  }
}

layer3.compliance_rules -> layer2.contract_deployer: "배포 승인 감사" {
  style: {
    stroke: "#2563EB"
    stroke-width: 2
  }
}

layer2.tx_allow_list -> layer1.permissioned_validators: "검증된 트랜잭션 블록 제안" {
  style: {
    stroke: "#DC2626"
    stroke-width: 2
  }
}

layer2.contract_deployer -> layer1.permissioned_validators: "인가된 컨트랙트 배포 합의" {
  style: {
    stroke: "#DC2626"
    stroke-width: 2
  }
}
```

---

## 5. D2 다이어그램 렌더링 및 출력 가이드

1. **온라인 플레이그라운드 렌더링**:
   - [D2 Playground (play.d2lang.com)](https://play.d2lang.com/)에 위 코드를 붙여넣고 `▷ Compile` (단축키 `Ctrl + S`)을 누르면 즉시 실시간 렌더링됩니다.
   - 우측 상단 `Export` 버튼을 통해 **SVG, PNG, PDF** 포맷으로 고해상도 벡터 다운로드가 가능합니다.

2. **로컬 CLI 빌드 명령어 (D2 설치 시)**:
   ```bash
   # SVG 벡터 파일로 컴파일
   d2 avalanche_subnet_architecture.d2 output.svg

   # PNG 이미지 파일로 컴파일
   d2 avalanche_subnet_architecture.d2 output.png

   # 실시간 감시 및 브라우저 프리뷰 서버 실행
   d2 --watch avalanche_subnet_architecture.d2
   ```
