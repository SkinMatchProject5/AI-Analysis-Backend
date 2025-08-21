from typing import Optional
import httpx
from app.core.config import settings
from .base import MedicalInterpretationProvider


class RunPodMedicalInterpreter(MedicalInterpretationProvider):
    def __init__(self):
        self.endpoint = settings.RUNPOD_ENDPOINT_URL
        self.api_key = settings.RUNPOD_API_KEY
        self.model_id = settings.RUNPOD_MODEL_ID

    def _headers(self):
        if not self.api_key:
            return {}
        return {"Authorization": f"Bearer {self.api_key}"}

    async def diagnose_text(self, description: Optional[str], additional_info: Optional[str] = None) -> str:
        if not self.endpoint:
            raise NotImplementedError("RUNPOD_ENDPOINT_URL 미설정: RunPod 프로바이더는 아직 활성화되지 않았습니다.")
        payload = {
            "model_id": self.model_id or None,
            "task": "diagnose_text",
            "description": description or "",
            "additional_info": additional_info,
        }
        async with httpx.AsyncClient(timeout=settings.REQUEST_TIMEOUT) as client:
            resp = await client.post(self.endpoint, json=payload, headers=self._headers())
            resp.raise_for_status()
            data = resp.json()
            # 예상: data["result_xml"] 또는 data["result"] 형태
            return data.get("result_xml") or data.get("result") or ""

    async def diagnose_image(
        self,
        image_base64: str,
        additional_info: Optional[str] = None,
        questionnaire_data: Optional[dict] = None,
    ) -> str:
        if not self.endpoint:
            raise NotImplementedError("RUNPOD_ENDPOINT_URL 미설정: RunPod 프로바이더는 아직 활성화되지 않았습니다.")
        payload = {
            "model_id": self.model_id or None,
            "task": "diagnose_image",
            "image_base64": image_base64,
            "additional_info": additional_info,
            "questionnaire_data": questionnaire_data,
        }
        async with httpx.AsyncClient(timeout=settings.REQUEST_TIMEOUT) as client:
            resp = await client.post(self.endpoint, json=payload, headers=self._headers())
            resp.raise_for_status()
            data = resp.json()
            return data.get("result_xml") or data.get("result") or ""

