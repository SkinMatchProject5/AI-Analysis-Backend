from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum

class ResponseFormat(str, Enum):
    JSON = "json"
    XML = "xml"


class SkinDiagnosisResponse(BaseModel):
    id: str = Field(..., description="진단 결과 ID")
    diagnosis: str = Field(..., description="피부 병변 진단 결과")
    confidence_score: Optional[float] = Field(None, description="진단 신뢰도 (0-1)")
    recommendations: Optional[str] = Field(None, description="추천 사항")
    similar_conditions: Optional[str] = Field(None, description="유사한 피부 질환")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="추가 메타데이터")
    created_at: datetime = Field(default_factory=datetime.now, description="생성 시간")
    
    class Config:
        schema_extra = {
            "example": {
                "id": "skin_diagnosis_123",
                "diagnosis": "기저세포암 의심",
                "confidence_score": 0.85,
                "recommendations": "즉시 피부과 전문의 상담을 받으시기 바랍니다.",
                "similar_conditions": "광선각화증, 멜라닌세포모반",
                "metadata": {"model": "gpt-4o-mini", "processing_time": 2.3},
                "created_at": "2023-12-01T10:00:00"
            }
        }

class SkinLesionRequest(BaseModel):
    lesion_description: Optional[str] = Field(None, description="피부 병변 설명 (이미지가 없을 때 필수)")
    additional_info: Optional[str] = Field(None, description="추가 정보 (환자 정보, 병력 등)")
    response_format: ResponseFormat = Field(ResponseFormat.JSON, description="응답 형식")
    
    class Config:
        schema_extra = {
            "example": {
                "lesion_description": "얼굴에 있는 갈색 반점이 최근 크기가 커지고 있습니다.",
                "additional_info": "50세 남성, 야외 활동 많음",
                "response_format": "json"
            }
        }

class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)