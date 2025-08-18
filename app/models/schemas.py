from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

class ResponseFormat(str, Enum):
    JSON = "json"
    XML = "xml"

class AnalysisRequest(BaseModel):
    prompt: str = Field(..., description="분석할 텍스트 또는 질문")
    context: Optional[str] = Field(None, description="추가 컨텍스트")
    response_format: ResponseFormat = Field(ResponseFormat.JSON, description="응답 형식")
    
    class Config:
        schema_extra = {
            "example": {
                "prompt": "이 제품에 대한 고객 리뷰를 분석해주세요",
                "context": "온라인 쇼핑몰 리뷰 데이터",
                "response_format": "json"
            }
        }

class AnalysisResponse(BaseModel):
    id: str = Field(..., description="분석 결과 ID")
    prompt: str = Field(..., description="원본 프롬프트")
    result: str = Field(..., description="분석 결과")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="추가 메타데이터")
    created_at: datetime = Field(default_factory=datetime.now, description="생성 시간")
    
    class Config:
        schema_extra = {
            "example": {
                "id": "analysis_123",
                "prompt": "이 제품에 대한 고객 리뷰를 분석해주세요",
                "result": "전반적으로 긍정적인 리뷰가 많으며...",
                "metadata": {"model": "gpt-3.5-turbo", "tokens": 150},
                "created_at": "2023-12-01T10:00:00"
            }
        }

class AnalysisUpdate(BaseModel):
    prompt: Optional[str] = Field(None, description="수정할 프롬프트")
    result: Optional[str] = Field(None, description="수정할 결과")
    metadata: Optional[Dict[str, Any]] = Field(None, description="수정할 메타데이터")

class AnalysisListResponse(BaseModel):
    analyses: List[AnalysisResponse]
    total_count: int
    page: int
    page_size: int

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