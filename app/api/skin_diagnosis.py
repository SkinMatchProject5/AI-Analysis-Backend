from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import Response
from typing import Optional
import uuid
from app.models.schemas import SkinDiagnosisResponse, SkinLesionRequest, ResponseFormat
from app.services.langchain_service import langchain_service
from app.services.analysis_store import analysis_store
from app.core.xml_utils import analysis_to_xml
from app.core.image_utils import encode_image_to_base64, validate_image_file, get_image_info
import logging
from starlette.concurrency import run_in_threadpool
import re
import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)
XML_ROOT_PATTERN = re.compile(r'<root>.*?</root>', re.DOTALL)
router = APIRouter(
    prefix="/diagnose",
    tags=["피부 진단"],
    responses={404: {"description": "Not found"}}
)

def parse_diagnosis_xml(xml_response: str) -> dict:
    """XML 응답을 파싱하여 구조화된 데이터로 변환"""
    try:
        # XML 형식이 포함된 응답에서 실제 XML 부분 추출
        xml_match = XML_ROOT_PATTERN.search(xml_response)
        if not xml_match:
            logger.warning(f"XML 형식을 찾을 수 없음: {xml_response}")
            return {
                "diagnosis": xml_response,
                "confidence_score": None,
                "recommendations": None,
                "similar_conditions": None
            }
        
        xml_content = xml_match.group(0)
        root = ET.fromstring(xml_content)
        
        # 진단 정보 추출
        label_elem = root.find('label')
        diagnosis = label_elem.text if label_elem is not None else "진단 결과 없음"
        confidence_score = None
        
        if label_elem is not None and 'score' in label_elem.attrib:
            try:
                confidence_score = float(label_elem.attrib['score']) / 100.0  # 0-1 범위로 변환
            except ValueError:
                pass
        
        # 진단 소견 추출
        summary_elem = root.find('summary')
        recommendations = summary_elem.text if summary_elem is not None else None
        
        # 유사 질병 추출
        similar_labels = []
        similar_labels_scored = []
        similar_labels_elem = root.find('similar_labels')
        if similar_labels_elem is not None:
            for similar_label in similar_labels_elem.findall('similar_label'):
                if similar_label is not None and similar_label.text:
                    name = similar_label.text
                    similar_labels.append(name)
                    score_val = None
                    try:
                        score_attr = similar_label.attrib.get('score')
                        if score_attr is not None:
                            score_val = float(score_attr)
                    except Exception:
                        score_val = None
                    item = {"name": name}
                    if score_val is not None:
                        item["score"] = score_val
                    similar_labels_scored.append(item)
        
        similar_conditions = ", ".join(similar_labels) if similar_labels else None
        
        return {
            "diagnosis": diagnosis,
            "confidence_score": confidence_score,
            "recommendations": recommendations,
            "similar_conditions": similar_conditions,
            "similar_diseases_scored": similar_labels_scored
        }
        
    except ET.ParseError as e:
        logger.error(f"XML 파싱 오류: {e}, 원본 응답: {xml_response}")
        return {
            "diagnosis": xml_response,
            "confidence_score": None,
            "recommendations": None,
            "similar_conditions": None
        }
    except Exception as e:
        logger.error(f"진단 결과 파싱 중 오류: {e}")
        return {
            "diagnosis": xml_response,
            "confidence_score": None,
            "recommendations": None,
            "similar_conditions": None
        }

@router.post("/skin-lesion", 
    response_model=SkinDiagnosisResponse,
    summary="텍스트 기반 피부 병변 진단",
    description="""환자가 제공한 피부 병변 설명을 바탕으로 AI 진단을 수행합니다.
    
    **진단 가능한 15가지 질병:**
    - 광선각화증, 기저세포암, 멜라닌세포모반, 보웬병, 비립종
    - 사마귀, 악성흑색종, 지루각화증, 편평세포암, 표피낭종
    - 피부섬유종, 피지샘증식증, 혈관종, 화농 육아종, 흑색점
    
    **응답 형식:** JSON 또는 XML 선택 가능
    """,
    response_description="구조화된 진단 결과 (진단명, 신뢰도, 추천사항, 유사질병)"
)
async def diagnose_skin_lesion(request: SkinLesionRequest):
    """텍스트 기반 피부 병변 진단"""
    try:
        # 피부 병변 진단 수행
        diagnosis_result = await langchain_service.diagnose_skin_lesion(
            lesion_description=request.lesion_description,
            additional_info=None  # 설문/추가정보 미주입
        )
        
        # ID 추가
        diagnosis_result["id"] = f"skin_diagnosis_{uuid.uuid4().hex[:8]}"
        
        # XML 응답 파싱
        raw_result = diagnosis_result.get("result", "진단 결과 없음")
        parsed_data = parse_diagnosis_xml(raw_result)
        
        # SkinDiagnosisResponse 형식에 맞게 변환
        formatted_result = {
            "id": diagnosis_result["id"],
            "diagnosis": parsed_data["diagnosis"],
            "confidence_score": parsed_data["confidence_score"],
            "recommendations": parsed_data["recommendations"],
            "similar_conditions": parsed_data["similar_conditions"],
            "metadata": {
                **diagnosis_result.get("metadata", {}),
                "similar_diseases_scored": parsed_data.get("similar_diseases_scored", [])
            },
            "created_at": diagnosis_result.get("created_at")
        }
        
        # 결과 저장
        stored_diagnosis = analysis_store.create_diagnosis(formatted_result)
        
        # 응답 형식에 따라 반환
        if request.response_format == ResponseFormat.XML:
            xml_response = analysis_to_xml(stored_diagnosis.model_dump())
            return Response(
                content=xml_response,
                media_type="application/xml"
            )
        
        return stored_diagnosis
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/skin-lesion-image", 
    response_model=SkinDiagnosisResponse,
    summary="이미지 기반 피부 병변 진단",
    description="""피부 병변 이미지를 업로드하여 OpenAI Vision API로 실시간 진단을 수행합니다.
    
    **지원 이미지 형식:**
    - JPEG, PNG, WebP 파일
    - 최대 파일 크기: 10MB
    - 자동 리사이징: 1024x1024 최대
    
    **추가 기능:**
    - 설문조사 데이터 포함 가능
    - 이미지 메타데이터 자동 추출
    - 신뢰도 점수 제공
    """,
    response_description="이미지 분석 결과와 메타데이터 포함"
)
async def diagnose_skin_lesion_with_image(
    image: UploadFile = File(..., description="피부 병변 이미지 파일 (JPEG, PNG, WebP, 최대 10MB)"),
    additional_info: Optional[str] = Form(None, description="추가 정보 (환자 정보, 병력 등)"),
    questionnaire_data: Optional[str] = Form(None, description="설문조사 데이터 (JSON 문자열)"),
    response_format: ResponseFormat = Form(ResponseFormat.JSON, description="응답 형식 (json 또는 xml)")
):
    """이미지 기반 피부 병변 진단"""
    try:
        # 이미지 파일 유효성 검사
        validate_image_file(image)
        
        # 이미지 정보 추출 (thread offload)
        image_info = await run_in_threadpool(get_image_info, image)
        
        # 이미지를 base64로 인코딩 (thread offload)
        image_base64 = await run_in_threadpool(encode_image_to_base64, image)
        
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
            additional_info=None,
            questionnaire_data=None  # 설문/추가정보 미주입
        )
        
        # 이미지 정보를 메타데이터에 추가
        diagnosis_result["metadata"].update({
            "image_info": image_info,
            "image_size_kb": round(len(image_base64) * 0.75 / 1024, 2),  # base64 크기 추정
            "questionnaire_included": False
        })
        
        # ID 추가
        diagnosis_result["id"] = f"skin_diagnosis_{uuid.uuid4().hex[:8]}"
        
        # XML 응답 파싱
        raw_result = diagnosis_result.get("result", "진단 결과 없음")
        parsed_data = parse_diagnosis_xml(raw_result)
        
        # SkinDiagnosisResponse 형식에 맞게 변환
        formatted_result = {
            "id": diagnosis_result["id"],
            "diagnosis": parsed_data["diagnosis"],
            "confidence_score": parsed_data["confidence_score"],
            "recommendations": parsed_data["recommendations"],
            "similar_conditions": parsed_data["similar_conditions"],
            "metadata": {
                **diagnosis_result.get("metadata", {}),
                "similar_diseases_scored": parsed_data.get("similar_diseases_scored", [])
            },
            "created_at": diagnosis_result.get("created_at")
        }
        
        # 결과 저장
        stored_diagnosis = analysis_store.create_diagnosis(formatted_result)
        
        # 응답 형식에 따라 반환
        if response_format == ResponseFormat.XML:
            xml_response = analysis_to_xml(stored_diagnosis.model_dump())
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
