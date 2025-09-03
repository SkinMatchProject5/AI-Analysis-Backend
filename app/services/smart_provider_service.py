# app/services/smart_provider_service.py
from typing import Optional, Dict, Any
from app.core.config import settings
from app.providers.openai_medical import OpenAIMedicalInterpreter
from app.providers.runpod_medical import RunPodMedicalInterpreter
import logging
import asyncio
import time

logger = logging.getLogger(__name__)

class SmartProviderService:
    """성능과 정확도를 균형있게 관리하는 스마트 프로바이더 서비스"""
    
    def __init__(self):
        self.openai_provider = OpenAIMedicalInterpreter()
        self.runpod_provider = RunPodMedicalInterpreter()
        
        # 성능 통계 저장
        self.provider_stats = {
            "openai": {"avg_time": 12.0, "success_rate": 0.95},
            "runpod": {"avg_time": 45.0, "success_rate": 0.98}
        }
    
    async def diagnose_with_smart_routing(
        self,
        image_base64: Optional[str] = None,
        description: Optional[str] = None,
        additional_info: Optional[str] = None,
        questionnaire_data: Optional[dict] = None,
        priority: str = "balanced"  # "speed", "accuracy", "balanced"
    ) -> Dict[str, Any]:
        """
        우선순위에 따른 스마트 라우팅
        - speed: OpenAI 우선 사용
        - accuracy: RunPod 우선 사용  
        - balanced: 상황에 따라 동적 선택
        """
        
        start_time = time.time()
        
        try:
            # 우선순위에 따른 프로바이더 선택
            if priority == "speed":
                primary_provider = "openai"
                fallback_provider = "runpod"
            elif priority == "accuracy":
                primary_provider = "runpod"
                fallback_provider = "openai"
            else:  # balanced
                primary_provider = self._select_balanced_provider()
                fallback_provider = "openai" if primary_provider == "runp