"""
[Release 1 - Sprint 2] 폐쇄 쇼핑몰 프론트 상품 및 예약 채널 모듈
"""
import uuid
from typing import List, Dict

class ClosedMallFrontService:
    def __init__(self):
        self.products = [
            {"id": "prod-01", "name": "로컬 친환경 쌀 10kg", "price_krw": 35000, "stock": 100},
            {"id": "prod-02", "name": "무형광 천연 롤화장지 세트", "price_krw": 18900, "stock": 200},
            {"id": "prod-03", "name": "단지 직배송 신선 채소 꾸러미", "price_krw": 15000, "stock": 50}
        ]
        self.reservations = []

    def get_products(self) -> List[Dict]:
        return self.products

    def reserve_product(self, user_id: str, product_id: str, quantity: int) -> Dict:
        reservation = {
            "reservation_id": f"RSV-{uuid.uuid4().hex[:8].upper()}",
            "user_id": user_id,
            "product_id": product_id,
            "quantity": quantity,
            "status": "RESERVED"
        }
        self.reservations.append(reservation)
        return reservation
