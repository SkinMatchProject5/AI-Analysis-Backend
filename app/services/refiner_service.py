from datetime import datetime
from typing import Optional
from app.core.config import settings
from app.providers.base import TextRefineProvider
from app.providers.openai_text import OpenAITextRefiner


def _build_refiner_provider() -> TextRefineProvider:
    provider = (settings.SYMPTOM_REFINER_PROVIDER or "openai").lower()
    # 현재는 OpenAI만 지원. 이후 필요 시 분기 추가
    return OpenAITextRefiner()


class RefinerService:
    def __init__(self):
        self.provider = _build_refiner_provider()

    async def refine(self, text: Optional[str], language: Optional[str] = None) -> dict:
        # 텍스트가 비어있거나 None이면 고정된 메시지 반환
        if not text or not text.strip():
            return {
                "refined_text": "해당 결과는 AI 분석 결과이므로 맹신해서는 안되며 정확한 진단은 병원에서 받아보시길 권장드립니다.",
                "style": "default-disclaimer",
                "model": "hardcoded",
                "created_at": datetime.now(),
            }
        
        # 텍스트가 있으면 기존 로직 수행
        refined = await self.provider.refine(text=text, language=language)
        return {
            "refined_text": refined.strip(),
            "style": "doctor-visit",
            "model": settings.SYMPTOM_REFINER_MODEL,
            "created_at": datetime.now(),
        }


refiner_service = RefinerService()

