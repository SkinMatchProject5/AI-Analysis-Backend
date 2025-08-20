from pydantic import BaseModel, Field, ConfigDict, computed_field
from typing import Optional, Dict, Any, List
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

    # 프론트엔드 호환을 위한 파생 필드(기능 동일, 표시용)
    @computed_field  # type: ignore[misc]
    @property
    def predicted_disease(self) -> str:
        return self.diagnosis

    @computed_field  # type: ignore[misc]
    @property
    def confidence(self) -> int:
        try:
            return int(round((self.confidence_score or 0.0) * 100))
        except Exception:
            return 0

    @computed_field  # type: ignore[misc]
    @property
    def summary(self) -> str:
        return self.recommendations or ""

    @computed_field  # type: ignore[misc]
    @property
    def recommendation(self) -> str:
        # 프론트 기본 고정 문구와 동일하게 맞춰 중복 소견 표시 방지
        return "※ 해당 결과는 AI 진단이므로 정확한 진단은 근처 병원에 방문하여 받아보시길 바랍니다."

    @computed_field  # type: ignore[misc]
    @property
    def similar_diseases(self) -> List[Dict[str, Any]]:
        items: List[Dict[str, Any]] = []
        if self.similar_conditions:
            for name in [s.strip() for s in self.similar_conditions.split(',') if s.strip()]:
                items.append({
                    "name": name,
                    "confidence": 0,
                    "description": "유사한 피부 질환입니다."
                })
        return items
    
    model_config = ConfigDict(json_schema_extra={
            "example": {
                "id": "skin_diagnosis_123",
                "diagnosis": "기저세포암 의심",
                "confidence_score": 0.85,
                "recommendations": "즉시 피부과 전문의 상담을 받으시기 바랍니다.",
                "similar_conditions": "광선각화증, 멜라닌세포모반",
                "metadata": {"model": "gpt-4o-mini", "processing_time": 2.3},
                "created_at": "2023-12-01T10:00:00"
            }
        })

class SkinLesionRequest(BaseModel):
    lesion_description: Optional[str] = Field(None, description="피부 병변 설명 (이미지가 없을 때 필수)")
    additional_info: Optional[str] = Field(None, description="추가 정보 (환자 정보, 병력 등)")
    response_format: ResponseFormat = Field(ResponseFormat.JSON, description="응답 형식")
    
    model_config = ConfigDict(json_schema_extra={
            "example": {
                "lesion_description": "얼굴에 있는 갈색 반점이 최근 크기가 커지고 있습니다.",
                "additional_info": "50세 남성, 야외 활동 많음",
                "response_format": "json"
            }
        })

class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
