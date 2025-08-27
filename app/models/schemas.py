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
    
    # 병원 정보 필드 추가
    hospitals: Optional[List[Dict[str, Any]]] = Field(default=None, description="관련 병원 목록")

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
        # 우선순위 1: 메타데이터에 점수 포함 리스트가 있으면 이를 사용
        try:
            md_list = self.metadata.get("similar_diseases_scored")
            if isinstance(md_list, list) and len(md_list) > 0:
                for entry in md_list:
                    if not isinstance(entry, dict):
                        continue
                    name = str(entry.get("name", "")).strip()
                    if not name:
                        continue
                    score_raw = entry.get("score")
                    confidence_val = 0
                    try:
                        if score_raw is not None:
                            # XML score는 보통 0-100 스케일 가정
                            confidence_val = int(round(float(score_raw)))
                    except Exception:
                        confidence_val = 0
                    items.append({
                        "name": name,
                        "confidence": confidence_val,
                        "description": "유사한 피부 질환입니다."
                    })
                return items
        except Exception:
            pass

        # 우선순위 2: 구(old) 문자열 기반 similar_conditions 사용 (점수 없음 → 0)
        if self.similar_conditions:
            for name in [s.strip() for s in self.similar_conditions.split(',') if s.strip()]:
                items.append({
                    "name": name,
                    "confidence": 0,
                    "description": "유사한 피부 질환입니다."
                })
        return items
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "skin_diagnosis_abc12345",
                "diagnosis": "기저세포암",
                "confidence_score": 0.85,
                "recommendations": "즉시 피부과 전문의 상담을 받으시기 바랍니다. 기저세포암은 조기 발견 시 치료 예후가 매우 좋습니다.",
                "similar_conditions": "광선각화증, 멜라닌세포모반",
                "metadata": {
                    "model": "gpt-4o-mini",
                    "analysis_type": "skin_lesion_image_diagnosis",
                    "image_analyzed": True,
                    "processing_time": 2.3
                },
                "created_at": "2025-08-21T10:00:00Z",
                "predicted_disease": "기저세포암",
                "confidence": 85,
                "summary": "즉시 피부과 전문의 상담을 받으시기 바랍니다.",
                "recommendation": "※ 해당 결과는 AI 진단이므로 정확한 진단은 근처 병원에 방문하여 받아보시길 바랍니다.",
                "similar_diseases": [
                    {"name": "광선각화증", "confidence": 0, "description": "유사한 피부 질환입니다."},
                    {"name": "멜라닌세포모반", "confidence": 0, "description": "유사한 피부 질환입니다."}
                ]
            }
        }
    )

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


# ===== 증상 문장 다듬기(utterance refine) =====
class UtteranceRefineRequest(BaseModel):
    text: Optional[str] = Field(None, description="환자 입력 원문 (비어있을 경우 기본 메시지 반환)")
    language: Optional[str] = Field("ko", description="목표 언어 코드(ko|en 등)")

    model_config = ConfigDict(json_schema_extra={
        "examples": [
            {
                "summary": "일반적인 증상 정제 요청",
                "value": {
                    "text": "팔 접히는 부분에 붉고 따갑고 간지러워요. 긁다 보니 피가 났어요.",
                    "language": "ko"
                }
            },
            {
                "summary": "빈 텍스트 (기본 메시지 반환)",
                "value": {
                    "text": "",
                    "language": "ko"
                }
            },
            {
                "summary": "텍스트 없음 (기본 메시지 반환)",
                "value": {
                    "language": "ko"
                }
            }
        ]
    })


class UtteranceRefineResponse(BaseModel):
    refined_text: str = Field(..., description="의사에게 전달하기 좋은 형태로 다듬은 문장")
    style: str = Field("doctor-visit", description="정제 스타일 태그")
    model: Optional[str] = Field(None, description="사용된 모델명")
    created_at: datetime = Field(default_factory=datetime.now)

    model_config = ConfigDict(json_schema_extra={
        "examples": [
            {
                "summary": "일반적인 증상 정제 결과",
                "value": {
                    "refined_text": "팔 안쪽 주름 부위에 붉고 따가운 가려움이 있습니다. 긁은 후 출혈이 있었습니다.",
                    "style": "doctor-visit",
                    "model": "gpt-4o-mini",
                    "created_at": "2025-08-21T10:00:00"
                }
            },
            {
                "summary": "빈 텍스트 입력 시 기본 메시지",
                "value": {
                    "refined_text": "해당 결과는 AI 분석 결과이므로 맹신해서는 안되며 정확한 진단은 병원에서 받아보시길 권장드립니다.",
                    "style": "default-disclaimer",
                    "model": "hardcoded",
                    "created_at": "2025-08-21T10:00:00"
                }
            }
        ]
    })
