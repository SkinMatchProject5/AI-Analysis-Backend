# app/services/hybrid_diagnosis_service.py
import asyncio
import logging
import time
from typing import Optional, Dict, Any
from app.providers.runpod_medical import RunPodMedicalInterpreter
from app.providers.openai_medical import OpenAIMedicalInterpreter

logger = logging.getLogger(__name__)

class HybridDiagnosisService:
    """RunPod 실패시 OpenAI로 자동 fallback하는 하이브리드 시스템"""
    
    def __init__(self):
        self.runpod_provider = RunPodMedicalInterpreter()
        self.openai_provider = OpenAIMedicalInterpreter()
        
        # RunPod 성능 통계 (간단한 circuit breaker)
        self.runpod_failures = 0
        self.runpod_success = 0
        self.max_failures = 3  # 3회 연속 실패시 OpenAI 우선 사용
    
    def