from fastapi import APIRouter, HTTPException, status
from schemas.dtos import UserRegisterRequest, UserLoginRequest, TokenResponse, UserResponse
import uuid
from decimal import Decimal
from datetime import datetime

router = APIRouter(prefix="/auth", tags=["1. Auth & Users"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(req: UserRegisterRequest):
    """신규 회원 가입 및 EVM 지갑 자동 매핑"""
    return UserResponse(
        id=uuid.uuid4(),
        email=req.email,
        nickname=req.nickname,
        role="MEMBER",
        wallet_address=req.wallet_address or f"0x{uuid.uuid4().hex[:40]}",
        token_balance=Decimal("100.0"), # 가입 축하 웰컴 리워드 토큰 지급
        created_at=datetime.utcnow()
    )

@router.post("/login", response_model=TokenResponse)
async def login_user(req: UserLoginRequest):
    """JWT 토큰 발급 및 사용자 세션 생성"""
    return TokenResponse(
        access_token=f"jwt_token_sample_{uuid.uuid4().hex}",
        token_type="bearer",
        user_id=uuid.uuid4(),
        email=req.email,
        nickname="테스트사용자",
        role="MEMBER"
    )
