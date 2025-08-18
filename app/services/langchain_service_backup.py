from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from langchain_core.messages import HumanMessage, SystemMessage, BaseMessage
from app.core.config import settings
from typing import Dict, Any, Optional, List
import uuid
from datetime import datetime
import openai

class LangChainService:
    def __init__(self):
        self.llm = ChatOpenAI(
            openai_api_key=settings.OPENAI_API_KEY,
            model_name="gpt-4o-mini",
            temperature=0.7
        )
        
        # 피부 병변 진단 전용 시스템 프롬프트
        self.system_prompt = """너는 피부 병변을 진단하는 전문 AI이다. 다음은 네가 진단할 수 있는 피부 병변 목록이며, 각 병변의 임상적 특징은 아래와 같다. 환자에게 나타난 병변의 이미지와 설명을 바탕으로 가장 적합한 질병을 하나 선택하여 진단하라.
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
<root><label id_code="0" score="67.6">광선각화증</label><summary>이미지에서는 자외선 노출이 많은 부위인 얼굴에 붉은색의 각질성 반점이 관찰됩니다. 이는 만성 자외선 노출로 인한 DNA 손상으로 발생하며, 장기간 방치할 경우 피부암, 특히 편평세포암으로의 진행 가능성이 있습니다. 병변의 진행 속도가 느릴 수 있으나, 조기 발견 시 적절한 치료를 통해 예후를 양호하게 할 수 있습니다.</summary><similar_labels><similar_label id_code="3" score="16.6">보웬병</similar_label><similar_label id_code="1" score="5.7">기저세포암</similar_label></similar_labels></root>"""
        
        # 피부 병변 진단 프롬프트 템플릿
        self.analysis_template = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("human", """
            환자의 피부 병변 정보:
            
            설명: {prompt}
            추가 정보: {context}
            
            위의 정보를 바탕으로 피부 병변을 진단하고, 지정된 XML 형식으로 응답해주세요.
            """)
        ])
        
        self.analysis_chain = LLMChain(
            llm=self.llm,
            prompt=self.analysis_template
        )
    
    async def analyze_text(self, prompt: str, context: Optional[str] = None) -> Dict[str, Any]:
        """텍스트 분석 수행"""
        try:
            # LangChain을 통한 분석 실행
            result = await self.analysis_chain.arun(
                prompt=prompt,
                context=context or "추가 컨텍스트 없음"
            )
            
            analysis_id = str(uuid.uuid4())
            
            return {
                "id": analysis_id,
                "prompt": prompt,
                "result": result,
                "metadata": {
                    "model": "gpt-4o-mini",
                    "context_provided": bool(context),
                    "analysis_type": "skin_lesion_diagnosis"
                },
                "created_at": datetime.now()
            }
            
        except Exception as e:
            raise Exception(f"분석 중 오류가 발생했습니다: {str(e)}")
    
    async def custom_prompt_analysis(self, prompt: str, system_message: Optional[str] = None) -> Dict[str, Any]:
        """커스텀 프롬프트로 분석"""
        try:
            messages = []
            
            if system_message:
                messages.append(SystemMessage(content=system_message))
            else:
                messages.append(SystemMessage(content=self.system_prompt))
            
            messages.append(HumanMessage(content=prompt))
            
            result = await self.llm.agenerate([messages])
            analysis_result = result.generations[0][0].text
            
            analysis_id = str(uuid.uuid4())
            
            return {
                "id": analysis_id,
                "prompt": prompt,
                "result": analysis_result,
                "metadata": {
                    "model": "gpt-4o-mini",
                    "custom_system_message": bool(system_message),
                    "analysis_type": "custom_skin_diagnosis"
                },
                "created_at": datetime.now()
            }
            
        except Exception as e:
            raise Exception(f"커스텀 분석 중 오류가 발생했습니다: {str(e)}")
    
    async def diagnose_skin_lesion(self, lesion_description: str, additional_info: Optional[str] = None) -> Dict[str, Any]:
        """피부 병변 진단 전용 메서드"""
        try:
            # 피부 병변 진단 전용 프롬프트
            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=f"""
                환자의 피부 병변 정보:
                
                병변 설명: {lesion_description}
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
                """)
            ]
            
            result = await self.llm.agenerate([messages])
            diagnosis_result = result.generations[0][0].text
            
            analysis_id = str(uuid.uuid4())
            
            return {
                "id": analysis_id,
                "prompt": lesion_description,
                "result": diagnosis_result,
                "metadata": {
                    "model": "gpt-4o-mini",
                    "additional_info_provided": bool(additional_info),
                    "analysis_type": "skin_lesion_diagnosis",
                    "diagnosis_format": "xml_structured"
                },
                "created_at": datetime.now()
            }
            
        except Exception as e:
            raise Exception(f"피부 병변 진단 중 오류가 발생했습니다: {str(e)}")
    
    async def diagnose_skin_lesion_with_image(self, image_base64: str, additional_info: Optional[str] = None) -> Dict[str, Any]:
        """이미지를 이용한 피부 병변 진단"""
        try:
            # OpenAI Client 직접 사용 (Vision API)
            client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
            
            # Vision API 메시지 구성
            messages = [
                {
                    "role": "system",
                    "content": self.system_prompt
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"""
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
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}",
                                "detail": "high"
                            }
                        }
                    ]
                }
            ]
            
            # OpenAI Vision API 호출
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=1000,
                temperature=0.3
            )
            
            diagnosis_result = response.choices[0].message.content
            analysis_id = str(uuid.uuid4())
            
            return {
                "id": analysis_id,
                "prompt": "피부 병변 이미지 분석",
                "result": diagnosis_result,
                "metadata": {
                    "model": "gpt-4o-mini",
                    "additional_info_provided": bool(additional_info),
                    "analysis_type": "skin_lesion_image_diagnosis",
                    "diagnosis_format": "xml_structured",
                    "image_analyzed": True
                },
                "created_at": datetime.now()
            }
            
        except Exception as e:
            raise Exception(f"이미지 기반 피부 병변 진단 중 오류가 발생했습니다: {str(e)}")

# 싱글톤 인스턴스
langchain_service = LangChainService()