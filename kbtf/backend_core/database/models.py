"""
SQLAlchemy 2.0 Declarative Async Models
Mapping 1:1 with 4-Tier Enterprise Architecture
"""
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from sqlalchemy import (
    String, Boolean, Integer, Numeric, Text, ForeignKey, DateTime, BigInteger
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    nickname: Mapped[str] = mapped_column(String(100), nullable=False)
    role: Mapped[str] = mapped_column(String(30), default="MEMBER")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    wallet: Mapped[Optional["UserWallet"]] = relationship("UserWallet", back_populates="user", uselist=False)
    posts: Mapped[List["CommunityPost"]] = relationship("CommunityPost", back_populates="author")
    chat_sessions: Mapped[List["AIChatSession"]] = relationship("AIChatSession", back_populates="user")
    orders: Mapped[List["MallOrder"]] = relationship("MallOrder", back_populates="buyer")

class UserWallet(Base):
    __tablename__ = "user_wallets"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    wallet_address: Mapped[str] = mapped_column(String(66), unique=True, nullable=False, index=True)
    token_balance: Mapped[Decimal] = mapped_column(Numeric(36, 18), default=Decimal(0))
    nonce: Mapped[int] = mapped_column(BigInteger, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    user: Mapped["User"] = relationship("User", back_populates="wallet")

class CommunityPost(Base):
    __tablename__ = "community_posts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    author_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(50), default="GENERAL", index=True)
    view_count: Mapped[int] = mapped_column(Integer, default=0)
    like_count: Mapped[int] = mapped_column(Integer, default=0)
    is_pinned: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    author: Mapped["User"] = relationship("User", back_populates="posts")
    comments: Mapped[List["CommunityComment"]] = relationship("CommunityComment", back_populates="post", cascade="all, delete-orphan")

class CommunityComment(Base):
    __tablename__ = "community_comments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    post_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("community_posts.id", ondelete="CASCADE"), nullable=False, index=True)
    author_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    parent_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("community_comments.id", ondelete="CASCADE"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    post: Mapped["CommunityPost"] = relationship("CommunityPost", back_populates="comments")

class AIChatSession(Base):
    __tablename__ = "ai_chat_sessions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(200), default="새로운 대화")
    model_name: Mapped[str] = mapped_column(String(100), default="gemini-3.7-flash")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    user: Mapped["User"] = relationship("User", back_populates="chat_sessions")
    messages: Mapped[List["AIChatMessage"]] = relationship("AIChatMessage", back_populates="session", cascade="all, delete-orphan")

class AIChatMessage(Base):
    __tablename__ = "ai_chat_messages"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("ai_chat_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    sender_type: Mapped[str] = mapped_column(String(20), nullable=False) # USER, ASSISTANT, SYSTEM
    content: Mapped[str] = mapped_column(Text, nullable=False)
    prompt_tokens: Mapped[int] = mapped_column(Integer, default=0)
    completion_tokens: Mapped[int] = mapped_column(Integer, default=0)
    rag_sources: Mapped[dict] = mapped_column(JSONB, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    session: Mapped["AIChatSession"] = relationship("AIChatSession", back_populates="messages")

class MallProduct(Base):
    __tablename__ = "mall_products"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    seller_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    price_krw: Mapped[int] = mapped_column(Integer, nullable=False)
    price_token: Mapped[Decimal] = mapped_column(Numeric(36, 18), default=Decimal(0))
    stock_quantity: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(30), default="ACTIVE")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class MallOrder(Base):
    __tablename__ = "mall_orders"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    buyer_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True)
    total_krw: Mapped[int] = mapped_column(Integer, nullable=False)
    total_token: Mapped[Decimal] = mapped_column(Numeric(36, 18), default=Decimal(0))
    order_status: Mapped[str] = mapped_column(String(30), default="PENDING", index=True)
    escrow_tx_hash: Mapped[Optional[str]] = mapped_column(String(66), nullable=True)
    shipping_address: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    buyer: Mapped["User"] = relationship("User", back_populates="orders")
    items: Mapped[List["MallOrderItem"]] = relationship("MallOrderItem", back_populates="order", cascade="all, delete-orphan")

class MallOrderItem(Base):
    __tablename__ = "mall_order_items"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("mall_orders.id", ondelete="CASCADE"), nullable=False)
    product_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("mall_products.id", ondelete="RESTRICT"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price_krw: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price_token: Mapped[Decimal] = mapped_column(Numeric(36, 18), default=Decimal(0))

    order: Mapped["MallOrder"] = relationship("MallOrder", back_populates="items")
    product: Mapped["MallProduct"] = relationship("MallProduct")

class BlockchainTxLog(Base):
    __tablename__ = "blockchain_tx_logs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tx_hash: Mapped[str] = mapped_column(String(66), unique=True, nullable=False, index=True)
    block_number: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    from_address: Mapped[str] = mapped_column(String(66), nullable=False)
    to_address: Mapped[str] = mapped_column(String(66), nullable=False)
    contract_address: Mapped[Optional[str]] = mapped_column(String(66), nullable=True)
    event_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    payload: Mapped[dict] = mapped_column(JSONB, default=dict)
    status: Mapped[str] = mapped_column(String(20), default="PENDING", index=True)
    gas_used: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    confirmed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
