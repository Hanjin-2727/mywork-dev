# 🌐 [Ontology Workspace] 피지컬 AI & 로보틱스 온톨로지 지식 저장소

본 디렉터리는 **피지컬 AI(Physical AI)**, **지능형 로보틱스**, 그리고 **온톨로지 지식 그래프(Knowledge Graph)**의 융합 연구 및 실무 구현을 위한 메인 작업공간입니다.

---

## 📂 디렉터리 구조 및 핵심 문서 안내

```
~/mywork/product/Ontology/
├── README.md                                       # [본 문서] 프로젝트 안내 및 맵
├── ontology_and_physical_ai_relation.md            # [기초 백서] 온톨로지와 피지컬 AI의 상호작용 원리
├── ontology_deep_dive_implementation_plan.md      # [마스터 플랜] OWL/Protégé/추론엔진 구현 계획서
│
└── references/                                     # 📚 [글로벌 표준 및 오픈소스 레퍼런스 라이브러리]
    ├── 00_Standards_Comparison_Overview.md         # 3대 표준(IEEE 1872, KnowRob, DSG) 종합 비교표
    ├── 01_IEEE_1872_CORA_Standard.md               # IEEE 1872 CORA 국제 표준 규격 및 TTL 스니펫
    ├── 02_KnowRob_Knowledge_Engine.md              # 독일 브레멘대 KnowRob 아키텍처 및 ROS/Prolog 연동
    └── 03_Dynamic_Scene_Graphs_DSG.md              # MIT SPARK Hydra 5계층 3D 동적 씬 그래프 가이드
```

---

## 🏛️ 3대 글로벌 표준 및 오픈소스 레퍼런스 바로가기

| 프레임워크 | 핵심 성격 | 문서 바로가기 |
| :--- | :--- | :--- |
| **IEEE 1872 (CORA)** | 로봇 및 자동화 개념 정의 세계 표준 (SUMO 기반, OWL/TTL) | 📄 [01_IEEE_1872_CORA_Standard.md](./references/01_IEEE_1872_CORA_Standard.md) |
| **KnowRob** | ROS 기반 로봇 일상 작업 지식 추론 오픈소스 엔진 (Prolog+OWL) | 📄 [02_KnowRob_Knowledge_Engine.md](./references/02_KnowRob_Knowledge_Engine.md) |
| **Dynamic Scene Graphs (DSG)** | MIT Hydra 주도 3D 공간 기하학 + 5계층 시맨틱 씬 그래프 | 📄 [03_Dynamic_Scene_Graphs_DSG.md](./references/03_Dynamic_Scene_Graphs_DSG.md) |
| **종합 비교 개요** | 3대 프레임워크의 유기적 결합 및 계층별 역할 매트릭스 | 📄 [00_Standards_Comparison_Overview.md](./references/00_Standards_Comparison_Overview.md) |

---

## 🚀 연구 및 개발 진행 로드맵
1. **[이론/표준 확립]**: IEEE 1872, KnowRob, DSG 분석을 통한 코어 온톨로지 스키마 도출 (완료)
2. **[온톨로지 모델링]**: `robot_core_ontology.ttl` 및 Protégé 검증 파일 작성 (다음 단계)
3. **[지식 엔진 개발]**: Python RDFLib/SPARQL 기반 고속 인지 및 안전 가드레일 모듈 구축
4. **[피지컬 연동]**: 로봇 모빌리티(`robot.Duck.BiWheel` 등) 및 시뮬레이터 연계
