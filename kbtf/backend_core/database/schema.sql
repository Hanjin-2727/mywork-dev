-- =============================================================================
-- K-Enterprise 4-Tier Hybrid Architecture PostgreSQL DDL Schema
-- Modules: 1) Auth/User  2) Community  3) AI ChatBot  4) Closed Mall  5) Blockchain
-- =============================================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- -----------------------------------------------------------------------------
-- 1. USERS & AUTH & WALLETS (회원/인증/블록체인 지갑)
-- -----------------------------------------------------------------------------
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    nickname VARCHAR(100) NOT NULL,
    role VARCHAR(30) DEFAULT 'MEMBER' CHECK (role IN ('MEMBER', 'VIP', 'MERCHANT', 'ADMIN')),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE user_wallets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    wallet_address VARCHAR(66) UNIQUE NOT NULL, -- EVM 0x address
    token_balance NUMERIC(36, 18) DEFAULT 0,    -- ERC-20 Reward Token balance
    nonce BIGINT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_user_wallets_user_id ON user_wallets(user_id);
CREATE INDEX idx_user_wallets_address ON user_wallets(wallet_address);

-- -----------------------------------------------------------------------------
-- 2. COMMUNITY APP (커뮤니티 게시글 및 소셜 피드)
-- -----------------------------------------------------------------------------
CREATE TABLE community_posts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    author_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(300) NOT NULL,
    content TEXT NOT NULL,
    category VARCHAR(50) DEFAULT 'GENERAL',
    view_count INT DEFAULT 0,
    like_count INT DEFAULT 0,
    is_pinned BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE community_comments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    post_id UUID NOT NULL REFERENCES community_posts(id) ON DELETE CASCADE,
    author_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    parent_id UUID REFERENCES community_comments(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_community_posts_author ON community_posts(author_id);
CREATE INDEX idx_community_posts_category ON community_posts(category);
CREATE INDEX idx_community_comments_post ON community_comments(post_id);

-- -----------------------------------------------------------------------------
-- 3. AI CHATBOT (지능형 상담 세션 및 RAG 대화 이력)
-- -----------------------------------------------------------------------------
CREATE TABLE ai_chat_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) DEFAULT '새로운 대화',
    model_name VARCHAR(100) DEFAULT 'gemini-3.7-flash',
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE ai_chat_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES ai_chat_sessions(id) ON DELETE CASCADE,
    sender_type VARCHAR(20) NOT NULL CHECK (sender_type IN ('USER', 'ASSISTANT', 'SYSTEM')),
    content TEXT NOT NULL,
    prompt_tokens INT DEFAULT 0,
    completion_tokens INT DEFAULT 0,
    rag_sources JSONB DEFAULT '[]'::jsonb, -- RAG 검색 출처 메타데이터
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_ai_chat_messages_session ON ai_chat_messages(session_id);

-- -----------------------------------------------------------------------------
-- 4. CLOSED MALL (폐쇄형 거래몰: 상품, 주문, 에스크로 결제)
-- -----------------------------------------------------------------------------
CREATE TABLE mall_products (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    seller_id UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price_krw INT NOT NULL CHECK (price_krw >= 0),
    price_token NUMERIC(36, 18) DEFAULT 0,  -- 리워드 토큰 복합 결제 지원
    stock_quantity INT NOT NULL DEFAULT 0,
    status VARCHAR(30) DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE', 'SOLD_OUT', 'SUSPENDED')),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE mall_orders (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    buyer_id UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    total_krw INT NOT NULL,
    total_token NUMERIC(36, 18) DEFAULT 0,
    order_status VARCHAR(30) DEFAULT 'PENDING' CHECK (order_status IN ('PENDING', 'ESCROW_LOCKED', 'PAID', 'SHIPPING', 'COMPLETED', 'CANCELLED')),
    escrow_tx_hash VARCHAR(66),            -- 온체인 에스크로 트랜잭션 해시
    shipping_address TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE mall_order_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    order_id UUID NOT NULL REFERENCES mall_orders(id) ON DELETE CASCADE,
    product_id UUID NOT NULL REFERENCES mall_products(id) ON DELETE RESTRICT,
    quantity INT NOT NULL CHECK (quantity > 0),
    unit_price_krw INT NOT NULL,
    unit_price_token NUMERIC(36, 18) DEFAULT 0
);

CREATE INDEX idx_mall_products_seller ON mall_products(seller_id);
CREATE INDEX idx_mall_orders_buyer ON mall_orders(buyer_id);
CREATE INDEX idx_mall_orders_status ON mall_orders(order_status);

-- -----------------------------------------------------------------------------
-- 5. BLOCKCHAIN TRANSACTION & ANCHORING LOGS (블록체인 온체인 트랜잭션 기록)
-- -----------------------------------------------------------------------------
CREATE TABLE blockchain_tx_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tx_hash VARCHAR(66) UNIQUE NOT NULL,
    block_number BIGINT,
    from_address VARCHAR(66) NOT NULL,
    to_address VARCHAR(66) NOT NULL,
    contract_address VARCHAR(66),
    event_type VARCHAR(50) NOT NULL, -- 'REWARD_MINT', 'ESCROW_DEPOSIT', 'ESCROW_RELEASE', 'DAILY_BATCH_ANCHOR'
    payload JSONB DEFAULT '{}'::jsonb,
    status VARCHAR(20) DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'CONFIRMED', 'FAILED')),
    gas_used BIGINT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    confirmed_at TIMESTAMPTZ
);

CREATE INDEX idx_blockchain_tx_hash ON blockchain_tx_logs(tx_hash);
CREATE INDEX idx_blockchain_tx_status ON blockchain_tx_logs(status);
CREATE INDEX idx_blockchain_tx_event ON blockchain_tx_logs(event_type);
