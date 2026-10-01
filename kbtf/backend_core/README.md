# ⚙️ K-Enterprise 4-Tier Hybrid Backend Core
> **구조**: Community App · AI ChatBot · Closed Mall · Blockchain 온체인 하이브리드 아키텍처

---

## 📁 프로젝트 디렉토리 구조

```text
backend_core/
├── database/
│   ├── schema.sql         # PostgreSQL DDL 스키마 (UUID, 외래키, 인덱스, 트리거)
│   └── models.py          # SQLAlchemy 2.0 비동기(Async) 선언형 ORM 모델
├── schemas/
│   └── dtos.py            # Pydantic v2 요청/응답 검증 및 직렬화 DTO
├── api/
│   ├── auth.py            # 1. 회원가입/로그인 & EVM 지갑 자동 발급/연동
│   ├── community.py       # 2. 커뮤니티 게시글 및 피드 API
│   ├── chatbot.py         # 3. AI 챗봇 및 RAG/Vector DB 지식 연계 엔드포인트
│   ├── mall.py            # 4. 폐쇄형 거래몰 상품 및 온체인 에스크로 결제
│   └── blockchain.py      # 5. Web3 온체인 트랜잭션 릴레이 및 컨트랙트 호출
├── main.py                # FastAPI 메인 애플리케이션 (Swagger OpenAPI 자동 생성)
└── README.md
```

---

## 🗄️ 데이터베이스 5대 핵심 엔티티 (schema.sql)

1. **`users` & `user_wallets`**: 회원 계정 및 0x 블록체인 지갑 주소, ERC-20 토큰 잔액 관리
2. **`community_posts` & `community_comments`**: 입주민 커뮤니티 게시판 및 댓글
3. **`ai_chat_sessions` & `ai_chat_messages`**: 지능형 상담 이력 및 RAG 검색 출처(JSONB)
4. **`mall_products`, `mall_orders`, `mall_order_items`**: 폐쇄몰 상품 및 에스크로 온체인 주문
5. **`blockchain_tx_logs`**: 블록체인 온체인 트랜잭션 해시, 가스비, 블록 번호 감사 로그

---

## 🚀 실행 방법 (FastAPI)

```bash
cd /home/tomkim/backend_core
uvicorn main:app --reload --port 8000
```
- **스웨거 인터랙티브 API 문서**: `http://localhost:8000/docs`
- **ReDoc 기술 명세서**: `http://localhost:8000/redoc`
