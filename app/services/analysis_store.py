from typing import Dict, List, Optional
from app.models.schemas import SkinDiagnosisResponse
from datetime import datetime

class DiagnosisStore:
    """피부 진단 결과 저장소 (실제 환경에서는 데이터베이스 사용 권장)"""
    
    def __init__(self):
        self.diagnoses: Dict[str, Dict] = {}
    
    def create_diagnosis(self, diagnosis_data: Dict) -> SkinDiagnosisResponse:
        """진단 결과 저장"""
        diagnosis_id = diagnosis_data["id"]
        self.diagnoses[diagnosis_id] = diagnosis_data
        return SkinDiagnosisResponse(**diagnosis_data)
    
    def get_diagnosis(self, diagnosis_id: str) -> Optional[SkinDiagnosisResponse]:
        """특정 진단 결과 조회"""
        if diagnosis_id in self.diagnoses:
            return SkinDiagnosisResponse(**self.diagnoses[diagnosis_id])
        return None
    
    def get_all_diagnoses(self, page: int = 1, page_size: int = 10) -> Dict:
        """모든 진단 결과 조회 (페이징)"""
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        
        all_diagnoses = list(self.diagnoses.values())
        # 최신순으로 정렬
        all_diagnoses.sort(key=lambda x: x["created_at"], reverse=True)
        
        paginated_diagnoses = all_diagnoses[start_idx:end_idx]
        
        return {
            "diagnoses": [SkinDiagnosisResponse(**diagnosis) for diagnosis in paginated_diagnoses],
            "total_count": len(self.diagnoses),
            "page": page,
            "page_size": page_size
        }
    
    def update_diagnosis(self, diagnosis_id: str, update_data: Dict) -> Optional[SkinDiagnosisResponse]:
        """진단 결과 수정"""
        if diagnosis_id not in self.diagnoses:
            return None
        
        current_diagnosis = self.diagnoses[diagnosis_id]
        
        # 업데이트할 필드만 수정
        for key, value in update_data.items():
            if value is not None:
                current_diagnosis[key] = value
        
        # 수정 시간 업데이트
        current_diagnosis["updated_at"] = datetime.now()
        
        return SkinDiagnosisResponse(**current_diagnosis)
    
    def delete_diagnosis(self, diagnosis_id: str) -> bool:
        """진단 결과 삭제"""
        if diagnosis_id in self.diagnoses:
            del self.diagnoses[diagnosis_id]
            return True
        return False
    
    def search_diagnoses(self, query: str) -> List[SkinDiagnosisResponse]:
        """진단 결과 검색"""
        results = []
        query_lower = query.lower()
        
        for diagnosis in self.diagnoses.values():
            if (query_lower in diagnosis["prompt"].lower() or 
                query_lower in diagnosis["result"].lower()):
                results.append(SkinDiagnosisResponse(**diagnosis))
        
        return results

# 싱글톤 인스턴스
analysis_store = DiagnosisStore()
