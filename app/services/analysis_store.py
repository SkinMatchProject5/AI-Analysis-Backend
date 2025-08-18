from typing import Dict, List, Optional
from app.models.schemas import AnalysisResponse, AnalysisUpdate
from datetime import datetime
import json

class AnalysisStore:
    """간단한 인메모리 저장소 (실제 환경에서는 데이터베이스 사용 권장)"""
    
    def __init__(self):
        self.analyses: Dict[str, Dict] = {}
    
    def create_analysis(self, analysis_data: Dict) -> AnalysisResponse:
        """분석 결과 저장"""
        analysis_id = analysis_data["id"]
        self.analyses[analysis_id] = analysis_data
        return AnalysisResponse(**analysis_data)
    
    def get_analysis(self, analysis_id: str) -> Optional[AnalysisResponse]:
        """특정 분석 결과 조회"""
        if analysis_id in self.analyses:
            return AnalysisResponse(**self.analyses[analysis_id])
        return None
    
    def get_all_analyses(self, page: int = 1, page_size: int = 10) -> Dict:
        """모든 분석 결과 조회 (페이징)"""
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        
        all_analyses = list(self.analyses.values())
        # 최신순으로 정렬
        all_analyses.sort(key=lambda x: x["created_at"], reverse=True)
        
        paginated_analyses = all_analyses[start_idx:end_idx]
        
        return {
            "analyses": [AnalysisResponse(**analysis) for analysis in paginated_analyses],
            "total_count": len(self.analyses),
            "page": page,
            "page_size": page_size
        }
    
    def update_analysis(self, analysis_id: str, update_data: AnalysisUpdate) -> Optional[AnalysisResponse]:
        """분석 결과 수정"""
        if analysis_id not in self.analyses:
            return None
        
        current_analysis = self.analyses[analysis_id]
        
        # 업데이트할 필드만 수정
        update_dict = update_data.dict(exclude_unset=True)
        for key, value in update_dict.items():
            if value is not None:
                current_analysis[key] = value
        
        # 수정 시간 업데이트
        current_analysis["updated_at"] = datetime.now()
        
        return AnalysisResponse(**current_analysis)
    
    def delete_analysis(self, analysis_id: str) -> bool:
        """분석 결과 삭제"""
        if analysis_id in self.analyses:
            del self.analyses[analysis_id]
            return True
        return False
    
    def search_analyses(self, query: str) -> List[AnalysisResponse]:
        """분석 결과 검색"""
        results = []
        query_lower = query.lower()
        
        for analysis in self.analyses.values():
            if (query_lower in analysis["prompt"].lower() or 
                query_lower in analysis["result"].lower()):
                results.append(AnalysisResponse(**analysis))
        
        return results

# 싱글톤 인스턴스
analysis_store = AnalysisStore()