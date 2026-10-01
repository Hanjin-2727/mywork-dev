"""
Pydantic v2 Request & Response DTOs
Validation and Serialization for 4-Tier APIs
"""
import uuid
from decimal import Decimal
from typing import Optional, List, Any
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field

# -----------------------------------------------------------------------------
# 1. Auth & User DTOs
# -----------------------------------------------------------------------------
class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    nickname: str
    wallet_address: Optional[str] = None

class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: uuid.UUID
    email: str
    nickname: str
    role: str

class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    nickname: str
    role: str
    wallet_address: Optional[str] = None
    token_balance: Decimal = Decimal(0)
    created_at: datetime

    class Config:
        from_attributes = True

# -----------------------------------------------------------------------------
# 2. Community DTOs
# -----------------------------------------------------------------------------
class PostCreateRequest(BaseModel):
    title: str = Field(min_length=2, max_length=300)
    content: str
    category: str = "GENERAL"

class PostResponse(BaseModel):
    id: uuid.UUID
    author_id: uuid.UUID
    title: str
    content: str
    category: str
    view_count: int
    like_count: int
    created_at: datetime

    class Config:
        from_attributes = True

# -----------------------------------------------------------------------------
# 3. AI ChatBot DTOs
# -----------------------------------------------------------------------------
class AIChatRequest(BaseModel):
    session_id: Optional[uuid.UUID] = None
    message: str
    model: str = "gemini-3.7-flash"
    use_rag: bool = True

class AIChatResponse(BaseModel):
    session_id: uuid.UUID
    reply: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    rag_sources: List[dict] = []
    timestamp: datetime

# -----------------------------------------------------------------------------
# 4. Closed Mall DTOs
# -----------------------------------------------------------------------------
class ProductCreateRequest(BaseModel):
    name: str
    description: Optional[str] = None
    price_krw: int = Field(ge=0)
    price_token: Decimal = Decimal(0)
    stock_quantity: int = Field(ge=0)

class ProductResponse(BaseModel):
    id: uuid.UUID
    seller_id: uuid.UUID
    name: str
    description: Optional[str]
    price_krw: int
    price_token: Decimal
    stock_quantity: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class OrderItemDTO(BaseModel):
    product_id: uuid.UUID
    quantity: int = Field(gt=0)

class OrderCreateRequest(BaseModel):
    shipping_address: str
    items: List[OrderItemDTO]

class OrderResponse(BaseModel):
    id: uuid.UUID
    buyer_id: uuid.UUID
    total_krw: int
    total_token: Decimal
    order_status: str
    escrow_tx_hash: Optional[str]
    shipping_address: str
    created_at: datetime

    class Config:
        from_attributes = True

# -----------------------------------------------------------------------------
# 5. Blockchain Web3 DTOs
# -----------------------------------------------------------------------------
class TxRelayRequest(BaseModel):
    to_address: str
    contract_address: Optional[str] = None
    event_type: str # 'REWARD_MINT', 'ESCROW_DEPOSIT', 'ESCROW_RELEASE'
    amount: Decimal
    payload: dict = {}

class TxResponse(BaseModel):
    tx_hash: str
    status: str
    event_type: str
    from_address: str
    to_address: str
    gas_used: Optional[int]
    created_at: datetime
