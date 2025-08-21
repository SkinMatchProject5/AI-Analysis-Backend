from typing import Optional
from app.services.langchain_service import langchain_service
from .base import MedicalInterpretationProvider


class OpenAIMedicalInterpreter(MedicalInterpretationProvider):
    async def diagnose_text(self, description: Optional[str], additional_info: Optional[str] = None) -> str:
        result = await langchain_service.diagnose_skin_lesion(
            lesion_description=description or "",
            additional_info=additional_info,
        )
        return result.get("result", "")

    async def diagnose_image(
        self,
        image_base64: str,
        additional_info: Optional[str] = None,
        questionnaire_data: Optional[dict] = None,
    ) -> str:
        result = await langchain_service.diagnose_skin_lesion_with_image(
            image_base64=image_base64,
            additional_info=additional_info,
            questionnaire_data=questionnaire_data,
        )
        return result.get("result", "")

