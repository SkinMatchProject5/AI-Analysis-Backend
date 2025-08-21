from datetime import datetime
from typing import Optional, Dict, Any
from app.core.config import settings
from app.providers.base import MedicalInterpretationProvider
from app.providers.openai_medical import OpenAIMedicalInterpreter
from app.providers.runpod_medical import RunPodMedicalInterpreter


def _build_medical_provider() -> MedicalInterpretationProvider:
    provider = (settings.INTERPRETATION_PROVIDER or "openai").lower()
    if provider == "runpod":
        return RunPodMedicalInterpreter()
    return OpenAIMedicalInterpreter()


class InterpretationService:
    def __init__(self):
        self.provider = _build_medical_provider()

    async def diagnose_text(self, description: Optional[str], additional_info: Optional[str] = None) -> Dict[str, Any]:
        xml = await self.provider.diagnose_text(description=description, additional_info=additional_info)
        return {
            "result_xml": xml,
            "metadata": {
                "provider": (settings.INTERPRETATION_PROVIDER or "openai").lower(),
                "model": settings.INTERPRETATION_MODEL,
            },
            "created_at": datetime.now(),
        }

    async def diagnose_image(
        self,
        image_base64: str,
        additional_info: Optional[str] = None,
        questionnaire_data: Optional[dict] = None,
    ) -> Dict[str, Any]:
        xml = await self.provider.diagnose_image(
            image_base64=image_base64,
            additional_info=additional_info,
            questionnaire_data=questionnaire_data,
        )
        return {
            "result_xml": xml,
            "metadata": {
                "provider": (settings.INTERPRETATION_PROVIDER or "openai").lower(),
                "model": settings.INTERPRETATION_MODEL,
                "questionnaire_included": bool(questionnaire_data),
            },
            "created_at": datetime.now(),
        }


interpretation_service = InterpretationService()

