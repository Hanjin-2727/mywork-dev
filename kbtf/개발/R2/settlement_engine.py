"""
[Release 2 - Sprint 4] 시간크레딧 차감(소비) 및 정산 처리 엔진
"""
from typing import Dict, Any

class TimeCreditSettlementEngine:
    def __init__(self):
        self.virtual_ledger = {}

    def credit_reward(self, user_uid: str, hours: float, activity: str) -> Dict[str, Any]:
        """자원봉사/돌봄 활동 시간크레딧 적립"""
        current = self.virtual_ledger.get(user_uid, 0.0)
        self.virtual_ledger[user_uid] = current + hours
        return {
            "status": "EARNED",
            "user_uid": user_uid,
            "earned_hours": hours,
            "new_balance": self.virtual_ledger[user_uid],
            "activity": activity
        }

    def deduct_settlement(self, user_uid: str, hours: float, usage: str) -> Dict[str, Any]:
        """폐쇄몰 물품 구매 또는 식권 교환 시 시간크레딧 차감 정산"""
        current = self.virtual_ledger.get(user_uid, 0.0)
        if current < hours:
            return {"status": "FAILED", "reason": "잔여 시간크레딧 부족"}
        
        self.virtual_ledger[user_uid] = current - hours
        return {
            "status": "SETTLED",
            "user_uid": user_uid,
            "deducted_hours": hours,
            "new_balance": self.virtual_ledger[user_uid],
            "usage": usage
        }
