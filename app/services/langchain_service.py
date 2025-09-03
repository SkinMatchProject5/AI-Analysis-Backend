from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from langchain_core.messages import HumanMessage, SystemMessage
from app.core.config import settings
from app.providers.openai_medical import OpenAIMedicalInterpreter
from app.providers.runpod_medical import RunPodMedicalInterpreter
from typing import Dict, Any, Optional
import uuid
from datetime import datetime
import logging
import asyncio
import httpx
try:
    from openai import OpenAIError  # type: ignore
except Exception:  # pragma: no cover - 안전장치
    class OpenAIError(Exception):
        pass

logger = logging.getLogger(__name__)

class LangChainService:
    """통일된 LangChain 기반 피부 병변 진단 서비스
    
    프로바이더 시스템을 통해 OpenAI 또는 RunPod 파인튜닝 모델을 동적으로 사용합니다.
    """
    
    def __init__(self):
        # 통일된 LLM 인스턴스는 지연 생성
        self._llm: Optional[ChatOpenAI] = None
        # Vision 지원 LLM (필요시에만 생성)
        self._vision_llm: Optional[ChatOpenAI] = None
        
        # 의료 진단 프로바이더는 지연 초기화
        self._skin_diagnosis_provider = None
        self._skin_diagnosis_image_provider = None
        
        # 중앙화된 시스템 프롬프트
        self.system_prompt = self._get_system_prompt()
        
        # 통일된 프롬프트 템플릿들
        self.prompt_templates = self._initialize_prompt_templates()
    
    @property
    def skin_diagnosis_provider(self):
        """피부 진단 프로바이더 (지연 로딩)"""
        if self._skin_diagnosis_provider is None:
            skin_provider = settings.SKIN_DIAGNOSIS_PROVIDER.lower()
            if skin_provider == "runpod":
                logger.info("RunPod 프로바이더를 사용합니다 (텍스트).")
                self._skin_diagnosis_provider = RunPodMedicalInterpreter()
            elif skin_provider == "openai":
                logger.info("OpenAI 프로바이더를 사용합니다 (텍스트).")
                self._skin_diagnosis_provider = OpenAIMedicalInterpreter()
            else:
                logger.warning(f"알 수 없는 프로바이더: {skin_provider}, OpenAI를 기본값으로 사용합니다.")
                self._skin_diagnosis_provider = OpenAIMedicalInterpreter()
        return self._skin_diagnosis_provider
    
    @property
    def skin_diagnosis_image_provider(self):
        """이미지 진단 프로바이더 (지연 로딩)"""
        if self._skin_diagnosis_image_provider is None:
            image_provider = settings.SKIN_DIAGNOSIS_IMAGE_PROVIDER.lower()
            if image_provider == "openai":
                logger.info("OpenAI 프로바이더를 사용합니다 (이미지).")
                self._skin_diagnosis_image_provider = OpenAIMedicalInterpreter()
            elif image_provider == "runpod":
                logger.info("RunPod 프로바이더를 사용합니다 (이미지).")
                self._skin_diagnosis_image_provider = RunPodMedicalInterpreter()
            else:
                logger.warning(f"알 수 없는 이미지 프로바이더: {image_provider}, OpenAI를 기본값으로 사용합니다.")
                self._skin_diagnosis_image_provider = OpenAIMedicalInterpreter()
        return self._skin_diagnosis_image_provider
    
    @property
    def llm(self) -> ChatOpenAI:
        """OpenAI 텍스트 모델 (증상 다듬기 등에 사용)"""
        if self._llm is None:
            self._llm = ChatOpenAI(
                openai_api_key=settings.OPENAI_API_KEY,
                model_name="gpt-4o-mini",
                temperature=settings.TEMPERATURE,
                max_tokens=settings.MAX_TOKENS,
                request_timeout=settings.REQUEST_TIMEOUT,
            )
        return self._llm

    @property
    def vision_llm(self) -> ChatOpenAI:
        """OpenAI Vision API 지원 LLM (백업용, 현재는 사용하지 않음)"""
        if self._vision_llm is None:
            self._vision_llm = ChatOpenAI(
                openai_api_key=settings.OPENAI_API_KEY,
                model_name="gpt-4o-mini",  # Vision 지원
                temperature=settings.TEMPERATURE,
                max_tokens=settings.MAX_TOKENS,
                request_timeout=settings.REQUEST_TIMEOUT,
            )
        return self._vision_llm
    
    def _get_system_prompt(self) -> str:
        """중앙화된 시스템 프롬프트"""
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
    
    def _initialize_prompt_templates(self) -> Dict[str, ChatPromptTemplate]:
        """중앙화된 프롬프트 템플릿 초기화 (OpenAI 텍스트 모델용)"""
        return {
            "custom_analysis": ChatPromptTemplate.from_messages([
                ("system", "{system_message}"),
                ("human", "{prompt}")
            ])
        }
    
    async def _retry_async(self, func, *args, **kwargs):
        retries = max(0, settings.LLM_MAX_RETRIES)
        delay_base = max(0.0, settings.LLM_RETRY_BASE_DELAY)
        attempt = 0
        while True:
            try:
                return await func(*args, **kwargs)
            except (OpenAIError, httpx.HTTPError, TimeoutError, Exception) as e:  # type: ignore
                if attempt >= retries:
                    raise
                # 이미지 진단의 경우 더 긴 백오프 적용
                if hasattr(e, '__class__') and 'timeout' in str(e).lower():
                    backoff = delay_base * (3 ** attempt)  # 지수 증가율 높임
                else:
                    backoff = delay_base * (2 ** attempt)
                logger.warning(f"LLM 호출 실패, 재시도 {attempt+1}/{retries} 후 {backoff:.2f}s: {e}")
                await asyncio.sleep(backoff)
                attempt += 1
    
    async def _create_analysis_result(
        self, 
        prompt: str, 
        result: str, 
        analysis_type: str, 
        additional_info: Optional[str] = None,
        **metadata_kwargs
    ) -> Dict[str, Any]:
        """통일된 분석 결과 생성"""
        analysis_id = str(uuid.uuid4())
        
        # 사용된 프로바이더 정보 추가
        provider_info = "runpod" if settings.SKIN_DIAGNOSIS_PROVIDER.lower() == "runpod" else "openai"
        model_info = "runpod-finetuned-model" if provider_info == "runpod" else "gpt-4o-mini"
        
        base_metadata = {
            "model": model_info,
            "provider": provider_info,
            "analysis_type": analysis_type,
            "additional_info_provided": bool(additional_info),
            "diagnosis_format": "xml_structured"
        }
        base_metadata.update(metadata_kwargs)
        
        return {
            "id": analysis_id,
            "prompt": prompt,
            "result": result,
            "metadata": base_metadata,
            "created_at": datetime.now()
        }
    
    async def _handle_analysis_error(self, error: Exception, context: str) -> Exception:
        """통일된 에러 처리"""
        error_message = f"{context} 중 오류가 발생했습니다: {str(error)}"
        logger.error(error_message, exc_info=True)
        return Exception(error_message)
    
    async def diagnose_skin_lesion(
        self, 
        lesion_description: str, 
        additional_info: Optional[str] = None
    ) -> Dict[str, Any]:
        """텍스트 기반 피부 병변 진단 (프로바이더 시스템 사용)"""
        try:
            logger.info(f"텍스트 기반 진단 시작 - 프로바이더: {settings.SKIN_DIAGNOSIS_PROVIDER}")
            
            async def run_diagnosis():
                return await self.skin_diagnosis_provider.diagnose_text(
                    description=lesion_description,
                    additional_info=additional_info
                )
            
            result = await self._retry_async(run_diagnosis)
            
            return await self._create_analysis_result(
                prompt=lesion_description,
                result=result,
                analysis_type="skin_lesion_text_diagnosis",
                additional_info=additional_info
            )
            
        except Exception as e:
            raise await self._handle_analysis_error(e, "피부 병변 텍스트 진단")
    
    async def diagnose_skin_lesion_with_image(
        self, 
        image_base64: str, 
        additional_info: Optional[str] = None,
        questionnaire_data: Optional[dict] = None
    ) -> Dict[str, Any]:
        """이미지 기반 피부 병변 진단 (별도 프로바이더 시스템 사용)"""
        try:
            image_provider_name = settings.SKIN_DIAGNOSIS_IMAGE_PROVIDER.lower()
            logger.info(f"이미지 기반 진단 시작 - 프로바이더: {image_provider_name}")
            
            async def run_diagnosis():
                return await self.skin_diagnosis_image_provider.diagnose_image(
                    image_base64=image_base64,
                    additional_info=additional_info,
                    questionnaire_data=questionnaire_data
                )
            
            result = await self._retry_async(run_diagnosis)
            
            # 이미지 프로바이더 정보로 메타데이터 생성
            provider_info = image_provider_name
            model_info = "gpt-4o-mini" if provider_info == "openai" else "runpod-finetuned-model"
            
            return {
                "id": str(uuid.uuid4()),
                "prompt": "피부 병변 이미지 분석",
                "result": result,
                "metadata": {
                    "model": model_info,
                    "provider": provider_info,
                    "analysis_type": "skin_lesion_image_diagnosis",
                    "additional_info_provided": bool(additional_info),
                    "diagnosis_format": "xml_structured",
                    "image_analyzed": True,
                    "questionnaire_included": bool(questionnaire_data)
                },
                "created_at": datetime.now()
            }
            
        except Exception as e:
            raise await self._handle_analysis_error(e, "이미지 기반 피부 병변 진단")
    
    async def analyze_text(self, prompt: str, context: Optional[str] = None) -> Dict[str, Any]:
        """일반 텍스트 분석 (하위 호환성)"""
        return await self.diagnose_skin_lesion(prompt, context)
    
    async def custom_prompt_analysis(
        self, 
        prompt: str, 
        system_message: Optional[str] = None
    ) -> Dict[str, Any]:
        """커스텀 프롬프트 분석 (OpenAI 텍스트 모델 사용)"""
        try:
            template = self.prompt_templates["custom_analysis"]
            chain = LLMChain(llm=self.llm, prompt=template)
            async def run_chain():
                return await chain.arun(
                    prompt=prompt,
                    system_message=system_message or self.system_prompt
                )
            result = await self._retry_async(run_chain)
            
            return await self._create_analysis_result(
                prompt=prompt,
                result=result,
                analysis_type="custom_skin_diagnosis",
                custom_system_message=bool(system_message)
            )
            
        except Exception as e:
            raise await self._handle_analysis_error(e, "커스텀 분석")

# 싱글톤 인스턴스
langchain_service = LangChainService()
