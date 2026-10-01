"""
[Release 1 - Sprint 1] 기구축 민원 챗봇 연동 브릿지 모듈
"""
from typing import Dict, Any

class CivilComplaintChatbotBridge:
    def __init__(self):
        self.faq_knowledge = {
            "관리비": "관리비 고지서는 매월 25일 앱 및 우편으로 발행되며, KPT 포인트로 일부 감면 가능합니다.",
            "주차": "단지 내 방문 차량은 커뮤니티 앱을 통해 1일 전 사전 등록하시면 1초 입차가 가능합니다.",
            "쓰레기": "재활용 분리수거는 매주 화/금요일 오후 6시부터 10시까지 지정 장소에서 진행됩니다.",
            "리워드": "에너지 절감 및 커뮤니티 활동 참여 시 시간크레딧(KPT)이 적립됩니다."
        }

    def query(self, user_question: str) -> Dict[str, Any]:
        matched_reply = "입주민님, 문의하신 사항에 대해 관리사무소 지식베이스를 기반으로 답변드립니다: "
        found = False
        for key, answer in self.faq_knowledge.items():
            if key in user_question:
                matched_reply += answer
                found = True
                break
        if not found:
            matched_reply += "상세한 민원은 챗봇 상담 접수 후 전담 관리사무소 매니저가 24시간 내 회신드립니다."
        
        return {
            "status": "SUCCESS",
            "question": user_question,
            "answer": matched_reply,
            "source": "K-BTF Civil FAQ KB v1.0"
        }
