from fastapi import APIRouter, HTTPException
from app.models.schemas import UtteranceRefineRequest, UtteranceRefineResponse
from app.services.refiner_service import refiner_service

router = APIRouter(
    prefix="/utterance",
    tags=["증상 문장 다듬기"],
    responses={404: {"description": "Not found"}}
)


@router.post("/refine", 
    response_model=UtteranceRefineResponse,
    summary="증상 문장 의료진 전달용으로 다듬기",
    description="""환자가 작성한 증상 설명을 의료진에게 전달하기 좋은 형태로 정제합니다.
    
    **주요 기능:**
    - 구어체 → 서면체 변환
    - 의학 용어 정리
    - 문장 구조 개선
    - 다국어 지원 (ko, en 등)
    
    **특별 기능:**
    - 텍스트가 비어있으면 기본 면책 메시지 반환
    - 프론트엔드 연동용 기본값 제공
    
    **예시:**
    - 입력: "팔 접히는 부분에 붉고 따걡고 간지러워요"
    - 출력: "팔 안쪽 주름 부위에 홍반과 열감, 소양증이 있습니다"
    - 빈 입력: "해당 결과는 AI 분석 결과이므로..."
    """,
    response_description="의료진 전달용으로 다듬어진 문장 또는 기본 면책 메시지"
)
async def refine_utterance(body: UtteranceRefineRequest):
    try:
        result = await refiner_service.refine(text=body.text, language=body.language)
        return UtteranceRefineResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

