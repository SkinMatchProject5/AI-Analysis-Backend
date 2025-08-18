from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from langchain_core.messages import HumanMessage, SystemMessage
from app.core.config import settings
from typing import Dict, Any, Optional, List, Union
import uuid
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class LangChainService:
    """통일된 LangChain 기반 피부 병변 진단 서비스"""
    
    def __init__(self):
        # 통일된 LLM 인스턴스
        self.llm = ChatOpenAI(
            openai_api_key=settings.OPENAI_API_KEY,
            model_name="gpt-4o-mini",
            temperature=0.3,  # 의료 진단의 일관성을 위해 낮은 temperature
            max_tokens=1000,
            request_timeout=30  # 타임아웃 설정
        )
        
        # Vision 지원 LLM (필요시에만 생성)
        self._vision_llm = None
        
        # 중앙화된 시스템 프롬프트
        self.system_prompt = self._get_system_prompt()
        
        # 통일된 프롬프트 템플릿들
        self.prompt_templates = self._initialize_prompt_templates()
        
        # 통일된 체인들
        self.chains = self._initialize_chains()
    
    @property
    def vision_llm(self) -> ChatOpenAI:
        """Vision API 지원 LLM (지연 로딩)"""
        if self._vision_llm is None:
            self._vision_llm = ChatOpenAI(
                openai_api_key=settings.OPENAI_API_KEY,
                model_name="gpt-4o-mini",  # Vision 지원
                temperature=0.3,
                max_tokens=1000,
                request_timeout=30
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
    
    def _initialize_chains(self) -> Dict[str, LLMChain]:
        """통일된 체인 초기화"""
        return {
            "text_diagnosis": LLMChain(
                llm=self.llm,
                prompt=self.prompt_templates["text_diagnosis"]
            ),
            "custom_analysis": LLMChain(
                llm=self.llm,
                prompt=self.prompt_templates["custom_analysis"]
            )
        }
    
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
            result = await self.chains["text_diagnosis"].arun(
                lesion_description=lesion_description,
                additional_info=additional_info or "추가 정보 없음"
            )
            
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
        additional_info: Optional[str] = None
    ) -> Dict[str, Any]:
        """이미지 기반 피부 병변 진단 (LangChain Vision 통합)"""
        try:
            # Vision API용 텍스트 메시지 구성
            text_content = f"""
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
            
            # LangChain을 통한 Vision API 호출
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
            
            # LangChain을 통한 Vision API 호출
            result = await self.vision_llm.agenerate([messages])
            diagnosis_result = result.generations[0][0].text
            
            return await self._create_analysis_result(
                prompt="피부 병변 이미지 분석",
                result=diagnosis_result,
                analysis_type="skin_lesion_image_diagnosis",
                additional_info=additional_info,
                image_analyzed=True
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
            result = await self.chains["custom_analysis"].arun(
                prompt=prompt,
                system_message=system_message or self.system_prompt
            )
            
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