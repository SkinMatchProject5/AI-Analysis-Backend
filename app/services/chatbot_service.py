"""
챗봇 백엔드 호출 서비스
AI 분석 완료 후 챗봇 백엔드에 진단 결과를 전송하여 상담 준비
"""

import asyncio
import aiohttp
import logging
from typing import Dict, List, Optional, Any
from app.core.config import settings

logger = logging.getLogger(__name__)

class ChatbotService:
    def __init__(self):
        self.chatbot_backend_url = getattr(settings, 'CHATBOT_BACKEND_URL', 'http://localhost:8003')
    
    async def notify_diagnosis_complete(
        self, 
        diagnosis_result: Dict[str, Any]
    ) -> Optional[str]:
        """
        챗봇 백엔드에 진단 완료 알림 및 세션 준비
        
        Args:
            diagnosis_result: AI 진단 결과
            
        Returns:
            세션 ID 또는 None (실패시)
        """
        try:
            # 챗봇이 기대하는 형식으로 변환
            analysis_payload = {
                "diagnosis": diagnosis_result.get("diagnosis", ""),
                "recommendations": diagnosis_result.get("recommendations", ""),
                "summary": diagnosis_result.get("recommendations", ""),  # 호환성
                "similar_diseases": self._extract_similar_diseases(diagnosis_result),
                "confidence_score": diagnosis_result.get("confidence_score", 0.0),
                "analysis_id": diagnosis_result.get("id", ""),
                "created_at": str(diagnosis_result.get("created_at", ""))
            }
            
            logger.info(f"🤖 챗봇 백엔드 진단 결과 전송: {diagnosis_result.get('diagnosis', '')}")
            logger.debug(f"챗봇 백엔드 페이로드: {analysis_payload}")
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.chatbot_backend_url}/api/v1/session/init-from-analysis",
                    json=analysis_payload,
                    timeout=aiohttp.ClientTimeout(total=15)
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        session_id = result.get("session_id")
                        logger.info(f"✅ 챗봇 세션 생성 완료: {session_id}")
                        return session_id
                    else:
                        error_text = await response.text()
                        logger.error(f"❌ 챗봇 백엔드 오류 ({response.status}): {error_text}")
                        return None
                        
        except asyncio.TimeoutError:
            logger.error("⏰ 챗봇 백엔드 요청 시간 초과")
            return None
        except Exception as e:
            logger.error(f"❌ 챗봇 백엔드 호출 실패: {e}")
            return None
    
    def _extract_similar_diseases(self, diagnosis_result: Dict[str, Any]) -> List[str]:
        """진단 결과에서 유사 질병 목록 추출"""
        try:
            # metadata에서 similar_diseases_scored 추출
            metadata = diagnosis_result.get("metadata", {})
            similar_diseases_scored = metadata.get("similar_diseases_scored", [])
            
            # score가 있는 경우 이름만 추출
            if isinstance(similar_diseases_scored, list) and len(similar_diseases_scored) > 0:
                diseases = []
                for item in similar_diseases_scored[:3]:  # 상위 3개만
                    if isinstance(item, dict) and "name" in item:
                        diseases.append(item["name"])
                    elif isinstance(item, str):
                        diseases.append(item)
                return diseases
            
            # similar_conditions에서 추출 (fallback)
            similar_conditions = diagnosis_result.get("similar_conditions", "")
            if similar_conditions and isinstance(similar_conditions, str):
                return [cond.strip() for cond in similar_conditions.split(",") if cond.strip()][:3]
            
            return []
            
        except Exception as e:
            logger.warning(f"유사 질병 추출 실패: {e}")
            return []
    
    def notify_diagnosis_fire_and_forget(
        self, 
        diagnosis_result: Dict[str, Any]
    ):
        """
        백그라운드로 챗봇에 진단 결과 전송 (Fire-and-Forget)
        응답 시간에 영향 주지 않음
        """
        def run_task():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self.notify_diagnosis_complete(diagnosis_result))
                loop.close()
            except Exception as e:
                logger.error(f"백그라운드 챗봇 알림 실패: {e}")
        
        # 백그라운드 스레드에서 실행
        import threading
        thread = threading.Thread(target=run_task, daemon=True)
        thread.start()
        logger.info("🚀 챗봇 백엔드 알림 백그라운드 전송 시작")

# 전역 인스턴스
chatbot_service = ChatbotService()


