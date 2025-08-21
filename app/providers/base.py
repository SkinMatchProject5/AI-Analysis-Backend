from abc import ABC, abstractmethod
from typing import Optional


class TextRefineProvider(ABC):
    @abstractmethod
    async def refine(self, text: str, language: Optional[str] = None) -> str:
        """입력 텍스트를 의사소통에 적합한 형태로 정제하여 반환"""
        raise NotImplementedError


class MedicalInterpretationProvider(ABC):
    @abstractmethod
    async def diagnose_text(self, description: Optional[str], additional_info: Optional[str] = None) -> str:
        """텍스트 기반 진단을 수행하고 XML 문자열을 반환"""
        raise NotImplementedError

    @abstractmethod
    async def diagnose_image(
        self,
        image_base64: str,
        additional_info: Optional[str] = None,
        questionnaire_data: Optional[dict] = None,
    ) -> str:
        """이미지 기반 진단을 수행하고 XML 문자열을 반환"""
        raise NotImplementedError

