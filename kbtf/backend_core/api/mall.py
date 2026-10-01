from fastapi import APIRouter, status
from schemas.dtos import ProductCreateRequest, ProductResponse, OrderCreateRequest, OrderResponse
import uuid
from decimal import Decimal
from datetime import datetime
from typing import List

router = APIRouter(prefix="/mall", tags=["4. Closed Mall (폐쇄형 거래몰)"])

@router.get("/products", response_model=List[ProductResponse])
async def list_products():
    """폐쇄형 거래몰 회원 전용 상품 목록"""
    return [
        ProductResponse(
            id=uuid.uuid4(),
            seller_id=uuid.uuid4(),
            name="친환경 로컬 유기농 쌀 10kg",
            description="입주민 전용 30% 할인 특가 상품",
            price_krw=35000,
            price_token=Decimal("10.0"), # 토큰 복합 결제
            stock_quantity=50,
            status="ACTIVE",
            created_at=datetime.utcnow()
        )
    ]

@router.post("/orders", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(req: OrderCreateRequest):
    """온체인 에스크로 결제 연계 주문 생성"""
    return OrderResponse(
        id=uuid.uuid4(),
        buyer_id=uuid.uuid4(),
        total_krw=35000,
        total_token=Decimal("10.0"),
        order_status="ESCROW_LOCKED",
        escrow_tx_hash=f"0x{uuid.uuid4().hex}{uuid.uuid4().hex}"[:66],
        shipping_address=req.shipping_address,
        created_at=datetime.utcnow()
    )
