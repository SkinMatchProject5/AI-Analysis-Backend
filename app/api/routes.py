from fastapi import APIRouter, HTTPException, Query, Path
from fastapi.responses import Response
from typing import Optional, List
from app.models.schemas import (
    AnalysisRequest, AnalysisResponse, AnalysisUpdate, 
    AnalysisListResponse, ErrorResponse, ResponseFormat, SkinLesionRequest
)
from app.services.langchain_service import langchain_service
from app.services.analysis_store import analysis_store
from app.core.xml_utils import analysis_to_xml, analysis_list_to_xml
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/analyze/text", response_model=AnalysisResponse)
async def create_analysis(request: AnalysisRequest):
    """새로운 텍스트 분석 요청"""
    try:
        # LangChain을 통한 분석 수행
        analysis_result = await langchain_service.analyze_text(
            prompt=request.prompt,
            context=request.context
        )
        
        # 결과 저장
        stored_analysis = analysis_store.create_analysis(analysis_result)
        
        # 응답 형식에 따라 반환
        if request.response_format == ResponseFormat.XML:
            xml_response = analysis_to_xml(stored_analysis.dict())
            return Response(
                content=xml_response,
                media_type="application/xml"
            )
        
        return stored_analysis
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analyses", response_model=AnalysisListResponse)
async def get_analyses(
    page: int = Query(1, ge=1, description="페이지 번호"),
    page_size: int = Query(10, ge=1, le=100, description="페이지 크기"),
    response_format: ResponseFormat = Query(ResponseFormat.JSON, description="응답 형식")
):
    """모든 분석 결과 조회"""
    try:
        result = analysis_store.get_all_analyses(page=page, page_size=page_size)
        
        if response_format == ResponseFormat.XML:
            # 응답 데이터를 딕셔너리로 변환
            response_data = {
                "analyses": [analysis.dict() for analysis in result["analyses"]],
                "total_count": result["total_count"],
                "page": result["page"],
                "page_size": result["page_size"]
            }
            xml_response = analysis_list_to_xml(response_data)
            return Response(
                content=xml_response,
                media_type="application/xml"
            )
        
        return AnalysisListResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analyses/{analysis_id}", response_model=AnalysisResponse)
async def get_analysis(
    analysis_id: str = Path(..., description="분석 ID"),
    response_format: ResponseFormat = Query(ResponseFormat.JSON, description="응답 형식")
):
    """특정 분석 결과 조회"""
    analysis = analysis_store.get_analysis(analysis_id)
    
    if not analysis:
        raise HTTPException(status_code=404, detail="분석 결과를 찾을 수 없습니다")
    
    if response_format == ResponseFormat.XML:
        xml_response = analysis_to_xml(analysis.dict())
        return Response(
            content=xml_response,
            media_type="application/xml"
        )
    
    return analysis

@router.put("/analyses/{analysis_id}", response_model=AnalysisResponse)
async def update_analysis(
    analysis_id: str = Path(..., description="분석 ID"),
    update_data: AnalysisUpdate = ...,
    response_format: ResponseFormat = Query(ResponseFormat.JSON, description="응답 형식")
):
    """분석 결과 수정"""
    updated_analysis = analysis_store.update_analysis(analysis_id, update_data)
    
    if not updated_analysis:
        raise HTTPException(status_code=404, detail="분석 결과를 찾을 수 없습니다")
    
    if response_format == ResponseFormat.XML:
        xml_response = analysis_to_xml(updated_analysis.dict())
        return Response(
            content=xml_response,
            media_type="application/xml"
        )
    
    return updated_analysis

@router.delete("/analyses/{analysis_id}")
async def delete_analysis(analysis_id: str = Path(..., description="분석 ID")):
    """분석 결과 삭제"""
    deleted = analysis_store.delete_analysis(analysis_id)
    
    if not deleted:
        raise HTTPException(status_code=404, detail="분석 결과를 찾을 수 없습니다")
    
    return {"message": "분석 결과가 성공적으로 삭제되었습니다"}

@router.get("/analyses/search", response_model=List[AnalysisResponse])
async def search_analyses(
    query: str = Query(..., description="검색 쿼리"),
    response_format: ResponseFormat = Query(ResponseFormat.JSON, description="응답 형식")
):
    """분석 결과 검색"""
    try:
        results = analysis_store.search_analyses(query)
        
        if response_format == ResponseFormat.XML:
            response_data = {
                "analyses": [analysis.dict() for analysis in results],
                "total_count": len(results),
                "query": query
            }
            xml_response = analysis_list_to_xml(response_data)
            return Response(
                content=xml_response,
                media_type="application/xml"
            )
        
        return results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze/custom", response_model=AnalysisResponse)
async def custom_analysis(
    prompt: str,
    system_message: Optional[str] = None,
    response_format: ResponseFormat = Query(ResponseFormat.JSON, description="응답 형식")
):
    """커스텀 시스템 메시지로 분석"""
    try:
        analysis_result = await langchain_service.custom_prompt_analysis(
            prompt=prompt,
            system_message=system_message
        )
        
        stored_analysis = analysis_store.create_analysis(analysis_result)
        
        if response_format == ResponseFormat.XML:
            xml_response = analysis_to_xml(stored_analysis.dict())
            return Response(
                content=xml_response,
                media_type="application/xml"
            )
        
        return stored_analysis
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))