from fastapi import APIRouter, status
from schemas.dtos import PostCreateRequest, PostResponse
import uuid
from datetime import datetime
from typing import List

router = APIRouter(prefix="/community", tags=["2. Community App"])

@router.post("/posts", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(req: PostCreateRequest):
    """커뮤니티 새 게시글 등록"""
    return PostResponse(
        id=uuid.uuid4(),
        author_id=uuid.uuid4(),
        title=req.title,
        content=req.content,
        category=req.category,
        view_count=0,
        like_count=0,
        created_at=datetime.utcnow()
    )

@router.get("/posts", response_model=List[PostResponse])
async def list_posts():
    """피드 게시글 목록 조회"""
    return [
        PostResponse(
            id=uuid.uuid4(),
            author_id=uuid.uuid4(),
            title="우리 단지 스마트 하우징 소통방 오픈!",
            content="스마트 하우징 리워드 앱을 통해 커뮤니티 활동을 시작하세요.",
            category="NOTICE",
            view_count=120,
            like_count=35,
            created_at=datetime.utcnow()
        )
    ]
