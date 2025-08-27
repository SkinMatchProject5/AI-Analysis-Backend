from typing import Optional
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from app.core.config import settings
from .base import MedicalInterpretationProvider
import logging

logger = logging.getLogger(__name__)


class RunPodMedicalInterpreter(MedicalInterpretationProvider):
    """RunPod 파인튜닝 모델을 사용하는 의료 진단 프로바이더
    
    OpenAI 클라이언트를 그대로 사용하되 base_url과 api_key만 변경합니다.
    """
    
    def __init__(self):
        self.api_key = settings.RUNPOD_API_KEY
        self.base_url = settings.RUNPOD_BASE_URL
        self._llm = None
        self._vision_llm = None
        
        if not self.api_key or not self.base_url:
            logger.warning("RunPod API 키 또는 Base URL이 설정되지 않았습니다.")
    
    @property
    def llm(self) -> ChatOpenAI:
        """텍스트 전용 LLM (RunPod 엔드포인트 사용)"""
        if self._llm is None:
            self._llm = ChatOpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
                model=settings.RUNPOD_MODEL_NAME,  # 빈 문자열이 작동함
                temperature=settings.TEMPERATURE,
                max_tokens=settings.MAX_TOKENS,
                timeout=settings.REQUEST_TIMEOUT,
            )
        return self._llm

    @property
    def vision_llm(self) -> ChatOpenAI:
        """Vision API 지원 LLM (RunPod 엔드포인트 사용)"""
        if self._vision_llm is None:
            self._vision_llm = ChatOpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
                model=settings.RUNPOD_MODEL_NAME,  # 빈 문자열이 작동함
                temperature=settings.TEMPERATURE,
                max_tokens=settings.MAX_TOKENS,
                timeout=settings.REQUEST_TIMEOUT,
            )
        return self._vision_llm
    
    def _get_system_prompt(self) -> str:
        """의료 진단을 위한 시스템 프롬프트"""
        return """너는 피부 병변을 진단하는 전문 AI이다. 다음은 네가 진단할 수 있는 피부 병변 목록이며, 각 병변의 임상적 특징은 아래와 같다. 환자에게 나타난 병변의 이미지와 설명을 바탕으로 가장 적합한 질병을 하나 선택하여 진단하라.
아래 진단 기준을 참조하여 이미지에서 어떤 특징이 해당 질병의 특징에 해당되는지 설명하라

0: 광선각화증
1: 기저세포암
2: 멜라닌세포모반
3: 보웬병
4: 비립종
5: 사마귀
6: 악성흑색종
7: 지루각화증
8: 편평세포암
9: 표피낭종
10: 피부섬유종
11: 피지샘증식증
12: 혈관종
13: 화농 육아종
14: 흑색점

<root><label id_code="{코드}" score="{점수}">{진단명}</label><summary>{진단소견}</summary><similar_labels><similar_label id_code="{코드}" score="{점수}">{유사질병명}</similar_label><similar_label id_code="{코드}" score="{점수}">{유사질병명}</similar_label></similar_labels></root>

예시:
<root><label id_code="0" score="67.6">광선각화증</label><summary>이미지에서는 자외선 노출이 많은 부위인 얼굴에 붉은색의 각질성 반점이 관찰됩니다. 이는 만성 자외선 노출로 인한 DNA 손상으로 발생하며, 장기간 방치할 경우 피부암, 특히 편평세포암으로의 진행 가능성이 있습니다. 병변의 진행 속도가 느릴 수 있으나, 조기 발견 시 적절한 치료를 통해 예후를 양호하게 할 수 있습니다.</summary><similar_labels><similar_label id_code="3" score="16.6">보웬병</similar_label><similar_label id_code="1" score="5.7">기저세포암</similar_label></similar_labels></root>

⚠️ 의료 면책 조항: 이 진단은 참고용이며, 최종 진단은 반드시 의료진과 상담하세요."""

    async def diagnose_text(self, description: Optional[str], additional_info: Optional[str] = None) -> str:
        """텍스트 기반 피부 병변 진단"""
        if not description:
            raise ValueError("병변 설명이 필요합니다.")
        
        user_message = f"""
        환자의 피부 병변 정보:
        
        병변 설명: {description}
        추가 정보: {additional_info or "추가 정보 없음"}
        
        위의 정보를 바탕으로 피부 병변을 진단하고, 지정된 XML 형식으로 응답해주세요.
        반드시 다음 형식을 준수해야 합니다:
        
        <root>
        <label id_code="코드" score="점수">진단명</label>
        <summary>진단소견</summary>
        <similar_labels>
        <similar_label id_code="코드" score="점수">유사질병명</similar_label>
        <similar_label id_code="코드" score="점수">유사질병명</similar_label>
        </similar_labels>
        </root>
        """
        
        messages = [
            SystemMessage(content=self._get_system_prompt()),
            HumanMessage(content=user_message)
        ]
        
        logger.info(f"RunPod 텍스트 진단 API 호출 - Base URL: {self.base_url}")
        result = await self.llm.agenerate([messages])
        return result.generations[0][0].text

    async def diagnose_image(
        self,
        image_base64: str,
        additional_info: Optional[str] = None,
        questionnaire_data: Optional[dict] = None,
    ) -> str:
        """이미지 기반 피부 병변 진단 (최적화됨)"""
        if not image_base64:
            raise ValueError("이미지 데이터가 필요합니다.")
        
        user_text = f"""
        환자의 피부 병변 이미지를 분석해주세요.
        
        추가 정보: {additional_info or "추가 정보 없음"}
        
        이미지에서 관찰되는 피부 병변의 특징을 바탕으로 진단하고, 
        반드시 다음 XML 형식으로 응답해주세요:
        
        <root>
        <label id_code="코드" score="점수">진단명</label>
        <summary>진단소견 (이미지에서 관찰된 구체적 특징 포함)</summary>
        <similar_labels>
        <similar_label id_code="코드" score="점수">유사질병명</similar_label>
        <similar_label id_code="코드" score="점수">유사질병명</similar_label>
        </similar_labels>
        </root>
        """
        
        # OpenAI Vision API 메시지 형식 (최적화됨)
        messages = [
            SystemMessage(content=self._get_system_prompt()),
            HumanMessage(content=[
                {
                    "type": "text",
                    "text": user_text
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image_base64}",
                        "detail": "low"  # 낮은 해상도로 빠른 처리
                    }
                }
            ])
        ]
        
        logger.info(f"RunPod Vision API 호출 (최적화 모드) - Base URL: {self.base_url}")
        
        # 최적화된 LLM 설정
        optimized_llm = ChatOpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            model=settings.RUNPOD_MODEL_NAME,
            temperature=0.05,  # 더 결정적인 응답
            max_tokens=400,    # 토큰 수 절반으로 줄임
            timeout=20,        # 20초 타임아웃
        )
        
        result = await optimized_llm.agenerate([messages])
        return result.generations[0][0].text
