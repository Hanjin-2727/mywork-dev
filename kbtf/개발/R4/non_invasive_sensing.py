"""
[Release 4 - Sprint 7] 24시간 비침습 무센서 일상 생존 신호 자율 검출 알고리즘
"""
from datetime import datetime, timedelta
from typing import Dict, List

class NonInvasiveLifeSafetySensing:
    def __init__(self, critical_threshold_hours: int = 48):
        self.critical_threshold = timedelta(hours=critical_threshold_hours)
        # resident_did => {"last_meal_tag": ts, "last_app_log": ts}
        self.activity_state = {}

    def record_activity(self, did_uid: str, activity_type: str):
        """배식 태깅 또는 앱 접속 이벤트 수신"""
        now = datetime.utcnow()
        if did_uid not in self.activity_state:
            self.activity_state[did_uid] = {}
        self.activity_state[did_uid][activity_type] = now
        self.activity_state[did_uid]["latest_heartbeat"] = now

    def check_safety_status(self) -> List[Dict]:
        """24시간 생존 신호 자율 모니터링: 48시간 무반응 취약세대 검출"""
        now = datetime.utcnow()
        alerts = []
        for did_uid, logs in self.activity_state.items():
            latest = logs.get("latest_heartbeat")
            if latest and (now - latest) > self.critical_threshold:
                alerts.append({
                    "did_uid": did_uid,
                    "status": "CRITICAL_ALERT",
                    "hours_inactive": round((now - latest).total_seconds() / 3600, 1),
                    "last_detected": latest.isoformat(),
                    "reason": "48시간 이상 배식 및 앱 활동 신호 미검출 (위기 감지)"
                })
        return alerts
