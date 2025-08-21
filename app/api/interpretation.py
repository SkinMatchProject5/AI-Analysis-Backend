from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import Response
from typing import Optional
import uuid
from app.models.schemas import SkinDiagnosisResponse, SkinLesionRequest, ResponseFormat
from app.services.analysis_store import analysis_store
from app.services.interpretation_service import interpretation_service
from app.core.image_utils import encode_image_to_base64, validate_image_file, get_image_info
from app.core.xml_utils import analysis_to_xml
from app.core.diagnosis_parser import parse_diagnosis_xml
from starlette.concurrency import run_in_threadpool
import logging
import json

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/interpretation", 
    tags=["진단 해석"],
    responses={404: {"description": "Not found"}}
)


@router.post("/explain", 
    response_model=SkinDiagnosisResponse,
    summary="진단 결과 상세 해석",
    description="""이미 받은 진단 결과에 대해 더 자세한 설명과 해석을 제공합니다.
    
    **주요 기능:**
    - 진단명에 대한 상세 설명
    - 의학 용어 쉽게 풀이
    - 치료 방법 안내
    - 예후 정보 제공
    
    **사용 예시:**
    - 기존 진단: "기저세포암"
    - 해석 결과: 상세 설명, 원인, 치료법, 예방법 포함
    """,
    response_description="상세 해석이 포함된 진단 결과"
)
async def interpret_skin(request: SkinLesionRequest):
    try:
        result = await interpretation_service.diagnose_text(
            description=request.lesion_description,
            additional_info=request.additional_info,
        )

        # parse xml result
        xml = result.get("result_xml", "")
        parsed = parse_diagnosis_xml(xml)

        base = {
            "id": f"skin_diagnosis_{uuid.uuid4().hex[:8]}",
            "diagnosis": parsed["diagnosis"],
            "confidence_score": parsed["confidence_score"],
            "recommendations": parsed["recommendations"],
            "similar_conditions": parsed["similar_conditions"],
            "metadata": result.get("metadata", {}),
            "created_at": result.get("created_at"),
        }

        stored = analysis_store.create_diagnosis(base)

        if request.response_format == ResponseFormat.XML:
            return Response(content=analysis_to_xml(stored.model_dump()), media_type="application/xml")

        return stored
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/explain-image", 
    response_model=SkinDiagnosisResponse,
    summary="이미지 진단 결과 상세 해석",
    description="""이미지 기반 진단 결과에 대한 상세한 해석과 설명을 제공합니다.
    
    **이미지 기반 추가 해석:**
    - 이미지에서 관찰된 특징 설명
    - 비주얼 소견 노트
    - 시각적 진단 포인트 설명
    - 전문의 상담 권고사항
    
    **지원 기능:**
    - 설문조사 데이터 연계 해석
    - 이미지 품질 평가
    - 진단 신뢰도 설명
    """,
    response_description="이미지 분석과 상세 해석이 포함된 결과"
)
async def interpret_skin_image(
    image: UploadFile = File(..., description="피부 병변 이미지 파일 (JPEG, PNG, WebP)"),
    additional_info: Optional[str] = Form(None, description="추가 정보"),
    questionnaire_data: Optional[str] = Form(None, description="설문조사 데이터 (JSON 문자열)"),
    response_format: ResponseFormat = Form(ResponseFormat.JSON, description="응답 형식"),
):
    try:
        validate_image_file(image)
        image_info = await run_in_threadpool(get_image_info, image)
        image_base64 = await run_in_threadpool(encode_image_to_base64, image)

        parsed_questionnaire = None
        if questionnaire_data:
            try:
                parsed_questionnaire = json.loads(questionnaire_data)
            except json.JSONDecodeError:
                logger.warning(f"설문조사 데이터 파싱 실패: {questionnaire_data}")

        result = await interpretation_service.diagnose_image(
            image_base64=image_base64,
            additional_info=additional_info,
            questionnaire_data=parsed_questionnaire,
        )

        # merge metadata
        meta = result.get("metadata", {})
        meta.update({
            "image_info": image_info,
            "image_size_kb": round(len(image_base64) * 0.75 / 1024, 2),
            "questionnaire_included": bool(parsed_questionnaire),
        })

        xml = result.get("result_xml", "")
        parsed = parse_diagnosis_xml(xml)
        base = {
            "id": f"skin_diagnosis_{uuid.uuid4().hex[:8]}",
            "diagnosis": parsed["diagnosis"],
            "confidence_score": parsed["confidence_score"],
            "recommendations": parsed["recommendations"],
            "similar_conditions": parsed["similar_conditions"],
            "metadata": meta,
            "created_at": result.get("created_at"),
        }

        stored = analysis_store.create_diagnosis(base)

        if response_format == ResponseFormat.XML:
            return Response(content=analysis_to_xml(stored.model_dump()), media_type="application/xml")

        return stored
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

