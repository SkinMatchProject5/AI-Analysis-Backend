from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import Response
from typing import Optional
from app.models.schemas import AnalysisResponse, SkinLesionRequest, ResponseFormat
from app.services.langchain_service import langchain_service
from app.services.analysis_store import analysis_store
from app.core.xml_utils import analysis_to_xml
from app.core.image_utils import encode_image_to_base64, validate_image_file, get_image_info
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/diagnose/skin-lesion", response_model=AnalysisResponse)
async def diagnose_skin_lesion(request: SkinLesionRequest):
    """피부 병변 진단 전용 엔드포인트"""
    try:
        # 피부 병변 진단 수행
        diagnosis_result = await langchain_service.diagnose_skin_lesion(
            lesion_description=request.lesion_description,
            additional_info=request.additional_info
        )
        
        # 결과 저장
        stored_diagnosis = analysis_store.create_analysis(diagnosis_result)
        
        # 응답 형식에 따라 반환
        if request.response_format == ResponseFormat.XML:
            xml_response = analysis_to_xml(stored_diagnosis.dict())
            return Response(
                content=xml_response,
                media_type="application/xml"
            )
        
        return stored_diagnosis
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/diagnose/skin-lesion-image", response_model=AnalysisResponse)
async def diagnose_skin_lesion_with_image(
    image: UploadFile = File(..., description="피부 병변 이미지 파일 (JPEG, PNG, WebP)"),
    additional_info: Optional[str] = Form(None, description="추가 정보 (환자 정보, 병력 등)"),
    questionnaire_data: Optional[str] = Form(None, description="설문조사 데이터 (JSON 문자열)"),
    response_format: ResponseFormat = Form(ResponseFormat.JSON, description="응답 형식")
):
    """이미지를 이용한 피부 병변 진단"""
    try:
        # 이미지 파일 유효성 검사
        validate_image_file(image)
        
        # 이미지 정보 추출
        image_info = get_image_info(image)
        
        # 이미지를 base64로 인코딩
        image_base64 = encode_image_to_base64(image)
        
        # 설문조사 데이터 파싱
        parsed_questionnaire = None
        if questionnaire_data:
            try:
                import json
                parsed_questionnaire = json.loads(questionnaire_data)
            except json.JSONDecodeError:
                logger.warning(f"설문조사 데이터 파싱 실패: {questionnaire_data}")
        
        # OpenAI Vision API를 통한 진단
        diagnosis_result = await langchain_service.diagnose_skin_lesion_with_image(
            image_base64=image_base64,
            additional_info=additional_info,
            questionnaire_data=parsed_questionnaire
        )
        
        # 이미지 정보를 메타데이터에 추가
        diagnosis_result["metadata"].update({
            "image_info": image_info,
            "image_size_kb": round(len(image_base64) * 0.75 / 1024, 2),  # base64 크기 추정
            "questionnaire_included": bool(parsed_questionnaire)
        })
        
        # 결과 저장
        stored_diagnosis = analysis_store.create_analysis(diagnosis_result)
        
        # 응답 형식에 따라 반환
        if response_format == ResponseFormat.XML:
            xml_response = analysis_to_xml(stored_diagnosis.dict())
            return Response(
                content=xml_response,
                media_type="application/xml"
            )
        
        return stored_diagnosis
        
    except HTTPException:
        # HTTPException은 그대로 re-raise
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))