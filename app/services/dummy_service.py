"""
더미 AI 서비스 - OpenAI API 키 문제가 있을 때 사용
"""
from typing import Dict, Any, Optional
import uuid
from datetime import datetime
import random

class DummyLangChainService:
    """OpenAI API 키 문제가 있을 때 사용하는 더미 서비스"""
    
    def __init__(self):
        self.dummy_diseases = [
            {
                "id_code": "2",
                "name": "멜라닌세포모반",
                "confidence": 76.8,
                "summary": "이미지에서 관찰되는 색소성 병변은 경계가 명확하고 대칭적인 형태를 보입니다. 균일한 갈색 색조와 규칙적인 모양으로 보아 양성 멜라닌세포모반으로 판단됩니다. 크기 변화나 색조 변화가 없다면 정기적인 관찰로 충분합니다.",
                "similar_diseases": [
                    {"id_code": "6", "name": "악성흑색종", "confidence": 12.4},
                    {"id_code": "7", "name": "지루각화증", "confidence": 8.1}
                ]
            },
            {
                "id_code": "0",
                "name": "광선각화증",
                "confidence": 83.2,
                "summary": "자외선 노출이 많은 부위에 발생한 각질성 반점으로 보입니다. 거친 표면과 홍반성 기저부가 특징적입니다. 전암성 병변으로 분류되므로 피부과 전문의의 정확한 진단과 적절한 치료가 필요합니다.",
                "similar_diseases": [
                    {"id_code": "3", "name": "보웬병", "confidence": 9.8},
                    {"id_code": "8", "name": "편평세포암", "confidence": 5.4}
                ]
            },
            {
                "id_code": "7",
                "name": "지루각화증",
                "confidence": 71.5,
                "summary": "나이와 함께 흔히 발생하는 양성 각질성 병변입니다. 왁스 같은 표면과 잘 구분되는 경계가 특징적입니다. 미용적 문제 외에는 특별한 치료가 필요하지 않으나, 급격한 변화가 있다면 전문의 상담을 받으시기 바랍니다.",
                "similar_diseases": [
                    {"id_code": "0", "name": "광선각화증", "confidence": 15.2},
                    {"id_code": "2", "name": "멜라닌세포모반", "confidence": 8.7}
                ]
            }
        ]
    
    async def diagnose_skin_lesion_with_image(
        self, 
        image_base64: str, 
        additional_info: Optional[str] = None
    ) -> Dict[str, Any]:
        """더미 이미지 기반 피부 병변 진단"""
        
        # 랜덤하게 질환 선택
        selected_disease = random.choice(self.dummy_diseases)
        
        # 추가 정보가 있으면 신뢰도 약간 조