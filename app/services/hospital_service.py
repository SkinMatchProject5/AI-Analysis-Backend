"""
병원 백엔드 호출 서비스
AI 분석 완료 후 병원 백엔드에 질병명과 소견을 전송하여 병원 검색
"""

import asyncio
import aiohttp
import logging
from typing import Dict, List, Optional, Any
from app.core.config import settings

logger = logging.getLogger(__name__)

class HospitalService:
    def __init__(self):
        self.hospital_backend_url = getattr(settings, 'HOSPITAL_BACKEND_URL', 'http://localhost:8002')
    
    def _create_hospital_xml(self, diagnosis: str, description: Optional[str] = None, similar_diseases: Optional[List[str]] = None) -> str:
        """AI 분석 결과를 병원 백엔드용 FT XML 형식으로 변환"""
        xml_parts = ["<root>"]
        
        # 진단명 (Hospital-Location-Backend 기대 형식)
        # <label id_code="코드" score="점수">진단명</label>
        xml_parts.append(f'    <label id_code="0" score="85.0">{diagnosis}</label>')
        
        # 설명/소견 (summary 태그로 변경)
        if description and description.strip():
            xml_parts.append(f"    <summary>{description.strip()}</summary>")
        else:
            xml_parts.append(f"    <summary>{diagnosis}에 대한 진단 소견입니다.</summary>")
        
        # 유사 질병들 (similar_labels 태그 구조로 변경)
        if similar_diseases and len(similar_diseases) > 0:
            xml_parts.append("    <similar_labels>")
            for i, disease in enumerate(similar_diseases[:3]):  # 최대 3개만
                disease_cleaned = disease.strip()
                if disease_cleaned:
                    # 각 유사 질병에 대해 score를 점진적으로 낮춤
                    score = max(10.0, 30.0 - (i * 5))
                    xml_parts.append(f'        <similar_label id_code="{i+1}" score="{score}">{disease_cleaned}</similar_label>')
            xml_parts.append("    </similar_labels>")
        
        xml_parts.append("</root>")
        
        return "\n".join(xml_parts)
    
    async def search_hospitals_async(
        self, 
        diagnosis: str, 
        description: Optional[str] = None, 
        similar_diseases: Optional[List[str]] = None,
        final_k: int = 2
    ) -> Optional[Dict[str, Any]]:
        """
        병원 백엔드에 비동기로 병원 검색 요청
        AI 분석과 병렬로 실행되어 응답 시간 단축
        """
        try:
            xml_data = self._create_hospital_xml(diagnosis, description, similar_diseases)
            
            payload = {
                "xml": xml_data,
                "rerank_mode": "ce",
                "top_k": 24,
                "final_k": final_k
            }
            
            logger.info(f"🏥 병원 백엔드 검색 요청: {diagnosis}")
            logger.debug(f"병원 백엔드 XML: {xml_data}")
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.hospital_backend_url}/search-ft-xml",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        hospitals = result.get("results", [])
                        logger.info(f"✅ 병원 검색 완료: {len(hospitals)}개 병원")
                        
                        return {
                            "hospitals": hospitals,
                            "meta": result.get("meta", {}),
                            "search_strategy": "ai_diagnosis_direct"
                        }
                    else:
                        error_text = await response.text()
                        logger.error(f"❌ 병원 백엔드 오류 ({response.status}): {error_text}")
                        return None
                        
        except asyncio.TimeoutError:
            logger.error("⏰ 병원 백엔드 요청 시간 초과")
            return None
        except Exception as e:
            logger.error(f"❌ 병원 백엔드 호출 실패: {e}")
            return None
    
    def search_hospitals_fire_and_forget(
        self, 
        diagnosis: str, 
        description: Optional[str] = None, 
        similar_diseases: Optional[List[str]] = None
    ):
        """
        병원 검색을 백그라운드에서 실행 (Fire and Forget)
        AI 분석 응답을 지연시키지 않음
        """
        def background_search():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(
                    self.search_hospitals_async(diagnosis, description, similar_diseases)
                )
            except Exception as e:
                logger.error(f"백그라운드 병원 검색 실패: {e}")
            finally:
                loop.close()
        
        # 백그라운드 스레드에서 실행
        import threading
        thread = threading.Thread(target=background_search, daemon=True)
        thread.start()
        logger.info(f"🔄 백그라운드 병원 검색 시작: {diagnosis}")

# 싱글톤 인스턴스
hospital_service = HospitalService()
