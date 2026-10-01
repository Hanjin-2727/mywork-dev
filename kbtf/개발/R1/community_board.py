"""
[Release 1 - Sprint 2] 단지 자유게시판 & 나눔 피드 모듈
"""
import uuid
from datetime import datetime
from typing import List, Dict

class CommunityBoardService:
    def __init__(self):
        self.posts = []

    def create_post(self, author_id: str, title: str, content: str, category: str = "GENERAL") -> Dict:
        post = {
            "id": str(uuid.uuid4()),
            "author_id": author_id,
            "title": title,
            "content": content,
            "category": category,
            "like_count": 0,
            "created_at": datetime.utcnow().isoformat()
        }
        self.posts.append(post)
        return post

    def get_feed(self) -> List[Dict]:
        return sorted(self.posts, key=lambda x: x["created_at"], reverse=True)
