from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from langchain_core.messages import HumanMessage, SystemMessage
from app.core.config import settings
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

    모델 교체 가이드 (미래 지향, 현재 기능 유지):
    - 교체 포인트 #1 (텍스트 LLM): __init__ 내 `self.llm` 생성부
      -> Runpod/사내 엔드포인트로 전환 시, 이 지점을 커스텀 클라이언트로 대체
    - 교체 포인트 #2 (비전 LLM): `vision_llm` 프로퍼티 내 `_vision_llm` 생성부
      -> 이미지 입력을 지원하는 파인튜닝 모델 엔드포인트로 대체
    - 교체 포인트 #3 (메시지 변환): `diagnose_skin_lesion_with_image`에서 messages 구성부
      -> LangChain 메시지 대신 HTTP 요청 payload로 변환하는 어댑터 레이어 삽입

    권장 구조 (교체 시):
    - 어댑터 레이어 함수(ex. _call_text_model, _call_vision_model)를 만들어
      내부에서 ChatOpenAI 호출 ↔ 외부 엔드포인트 호출을 쉽게 스위칭
    - 환경변수 예시 (주석): MODEL_PROVIDER, CUSTOM_MODEL_ENDPOINT, CUSTOM_MODEL_API_KEY, CUSTOM_MODEL_NAME
      (현재는 사용하지 않으며, 추후 필요 시 Settings에 추가 권장)
    """
    
    def __init__(self):
        # 통일된 LLM 인스턴스는 지연 생성
        self._llm: Optional[ChatOpenAI] = None
        # Vision 지원 LLM (필요시에만 생성)
        self._vision_llm: Optional[ChatOpenAI] = None
        
        # 중앙화된 시스템 프롬프트
        self.system_prompt = self._get_system_prompt()
        
        # 통일된 프롬프트 템플릿들
        self.prompt_templates = self._initialize_prompt_templates()
        
        # 체인은 호출 시점에 생성하여 LLM 지연 초기화를 보장
    
    @property
    def llm(self) -> ChatOpenAI:
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
        """Vision API 지원 LLM (지연 로딩)

        [교체 포인트 #2]
        - 이미지 입력을 지원하는 파인튜닝 모델로 전환할 경우,
          이 지점에서 ChatOpenAI 대신 외부 엔드포인트 클라이언트를 생성/반환하도록 변경하세요.
        - 엔드포인트가 이미지(base64)와 텍스트를 함께 받는다면, 아래 메시지 구성부(#3)와 맞춰 어댑트 필요.
        """
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
        """중앙화된 프롬프트 템플릿 초기화"""
        return {
            "text_diagnosis": ChatPromptTemplate.from_messages([
                ("system", self.system_prompt),
                ("human", """
                환자의 피부 병변 정보:
                
                병변 설명: {lesion_description}
                추가 정보: {additional_info}
                
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
                """)
            ]),
            
            "image_diagnosis": ChatPromptTemplate.from_messages([
                ("system", self.system_prompt),
                ("human", """
                환자의 피부 병변 이미지를 분석해주세요.
                
                추가 정보: {additional_info}
                
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
                """)
            ]),
            
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
            except (OpenAIError, httpx.HTTPError, TimeoutError) as e:  # type: ignore
                if attempt >= retries:
                    raise
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
        
        base_metadata = {
            "model": "gpt-4o-mini",
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
        """텍스트 기반 피부 병변 진단 (LangChain 통합)"""
        try:
            prompt = self.prompt_templates["text_diagnosis"]
            chain = LLMChain(llm=self.llm, prompt=prompt)
            async def run_chain():
                # 설문/추가정보 미주입: additional_info는 강제로 비워서 전달
                return await chain.arun(
                    lesion_description=lesion_description,
                    additional_info="추가 정보 없음"
                )
            result = await self._retry_async(run_chain)
            
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
        """이미지 기반 피부 병변 진단 (LangChain Vision 통합)"""
        try:
            # Vision API용 텍스트 메시지 구성 (설문/추가정보 미주입)
            text_content = f"""
            환자의 피부 병변 이미지를 분석해주세요.

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
            
            # [교체 포인트 #3]
            # 메시지 → 요청 변환 레이어
            # - 현재는 LangChain 메시지 포맷(SystemMessage/HumanMessage + image_url)을 사용합니다.
            # - 외부 엔드포인트로 교체 시, 아래 messages 대신 HTTP 요청 바디를 구성하세요.
            #   예) payload = {"prompt": text_content, "image_base64": image_base64, ...}
            # - 응답 파싱부도 아래 `diagnosis_result`를 생성하는 부분을 해당 포맷에 맞춰 수정합니다.
            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=[
                    {
                        "type": "text",
                        "text": text_content
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_base64}",
                            "detail": "high"
                        }
                    }
                ])
            ]

            # LangChain을 통한 Vision API 호출 (현재 동작 유지)
            async def run_vision():
                return await self.vision_llm.agenerate([messages])
            result = await self._retry_async(run_vision)
            diagnosis_result = result.generations[0][0].text
            
            return await self._create_analysis_result(
                prompt="피부 병변 이미지 분석",
                result=diagnosis_result,
                analysis_type="skin_lesion_image_diagnosis",
                additional_info=None,
                image_analyzed=True,
                questionnaire_included=False
            )
            
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
        """커스텀 프롬프트 분석 (LangChain 통합)"""
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
