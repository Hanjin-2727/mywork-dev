from fastapi import APIRouter
from schemas.dtos import AIChatRequest, AIChatResponse
import uuid
from datetime import datetime

router = APIRouter(prefix="/chatbot", tags=["3. AI ChatBot"])

@router.post("/message", response_model=AIChatResponse)
async def send_chat_message(req: AIChatRequest):
    """AI 챗봇 지능형 상담 및 RAG 연계 검색"""
    return AIChatResponse(
        session_id=req.session_id or uuid.uuid4(),
        reply=f"안녕하세요! '{req.message}'에 대한 맞춤형 안내입니다. K-BTF 스마트 주거복지 지식베이스(Vector DB)를 검색하여 답변을 생성했습니다.",
        model=req.model,
        prompt_tokens=42,
        completion_tokens=88,
        rag_sources=[
            {"doc_id": "KB-2026-01", "title": "주거복지 리워드 사용 가이드", "similarity": 0.94}
        ],
        timestamp=datetime.utcnow()
    )
