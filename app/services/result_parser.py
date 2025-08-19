# app/services/result_parser.py
import re
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

class DiagnosisResultParser:
    """AI 진단 결과를 파싱하고 구조화하는 클래스"""
    
    @staticmethod
    def parse_xml_diagnosis(xml_result: str) -> Dict[str, Any]:
        """XML 형식의 진단 결과를 JSON으로 변환"""
        try:
            # XML 태그를 찾기 위한 정규식
            root_pattern = r'<root>(.*?)</root>'
            root_match = re.search(root_pattern, xml_result, re.DOTALL)
            
            if not root_match:
                logger.warning("XML root 태그를 찾을 수 없음")
                return DiagnosisResultParser._create_fallback_result(xml_result)
            
            xml_content = f"<root>{root_match.group(1)}</root>"
            
            # XML 파싱
            root = ET.fromstring(xml_content)
            
            # 주 진단 정보 추출
            label_elem = root.find('label')
            if label_elem is None:
                logger.warning("label 태그를 찾을 수 없음")
                return DiagnosisResultParser._create_fallback_result(xml_result)
            
            predicted_disease = label_elem.text or "진단명 불명"
            confidence = float(label_elem.get('score', 0))
            disease_code = label_elem.get('id_code', '')
            
            # 진단 소견 추출
            summary_elem = root.find('summary')
            summary = summary_elem.text if summary_elem is not None else "진단 소견이 제공되지 않았습니다."
            
            # 유사 질환 추출
            similar_diseases = []
            similar_labels_elem = root.find('similar_labels')
            if similar_labels_elem is not None:
                for similar_elem in similar_labels_elem.findall('similar_label'):
                    similar_disease = {
                        "name": similar_elem.text or "질환명 불명",
                        "confidence": float(similar_elem.get('score', 0)),
                        "code": similar_elem.get('id_code', ''),
                        "description": DiagnosisResultParser._get_disease_description(similar_elem.text)
                    }
                    similar_diseases.append(similar_disease)
            
            # 구조화된 결과 반환
            result = {
                "predicted_disease": predicted_disease,
                "confidence": confidence,
                "disease_code": disease_code,
                "summary": summary,
                "recommendation": DiagnosisResultParser._generate_recommendation(predicted_disease, confidence),
                "similar_diseases": similar_diseases,
                "raw_xml": xml_result
            }
            
            logger.info(f"XML 파싱 성공: {predicted_disease} ({confidence}%)")
            return result
            
        except ET.ParseError as e:
            logger.error(f"XML 파싱 오류: {e}")
            return DiagnosisResultParser._create_fallback_result(xml_result)
        except Exception as e:
            logger.error(f"진단 결과 파싱 오류: {e}")
            return DiagnosisResultParser._create_fallback_result(xml_result)
    
    @staticmethod
    def _create_fallback_result(raw_result: str) -> Dict[str, Any]:
        """파싱 실패 시 대체 결과 생성"""
        # 간단한 패턴 매칭으로 정보 추출 시도
        disease_patterns = [
            r'진단[:\s]*([가-힣\s]+)',
            r'질환[:\s]*([가-힣\s]+)',
            r'소견[:\s]*([가-힣\s]+)'
        ]
        
        predicted_disease = "분석 결과 파싱 실패"
        for pattern in disease_patterns:
            match = re.search(pattern, raw_result)
            if match:
                predicted_disease = match.group(1).strip()
                break
        
        # 신뢰도 추출 시도
        confidence_pattern = r'(\d+\.?\d*)\s*%'
        confidence_match = re.search(confidence_pattern, raw_result)
        confidence = float(confidence_match.group(1)) if confidence_match else 50.0
        
        return {
            "predicted_disease": predicted_disease,
            "confidence": confidence,
            "disease_code": "unknown",
            "summary": raw_result,
            "recommendation": "정확한 진단을 위해 전문의와 상담하시기 바랍니다.",
            "similar_diseases": [],
            "raw_xml": raw_result,
            "parsing_failed": True
        }
    
    @staticmethod
    def _get_disease_description(disease_name: Optional[str]) -> str:
        """질환명에 따른 간단한 설명 반환"""
        if not disease_name:
            return "질환 정보를 확인할 수 없습니다."
        
        descriptions = {
            "광선각화증": "만성 자외선 노출로 인한 전암성 병변",
            "기저세포암": "가장 흔한 피부암, 전이는 드물지만 국소 파괴적",
            "멜라닌세포모반": "흔한 양성 점, 대부분 무해하나 변화 관찰 필요",
            "보웬병": "상피내 편평세포암, 조기 치료 시 예후 양호",
            "비립종": "피지샘의 각질 축적으로 형성된 양성 병변",
            "사마귀": "바이러스 감염으로 인한 양성 증식성 병변",
            "악성흑색종": "악성도가 높은 피부암, 조기 발견과 치료가 중요",
            "지루각화증": "나이와 함께 나타나는 양성 각질성 병변",
            "편평세포암": "두 번째로 흔한 피부암, 전이 가능성 있음",
            "표피낭종": "피지나 각질이 축적된 양성 낭성 병변",
            "피부섬유종": "진피의 섬유조직 증식으로 형성된 양성 종양",
            "피지샘증식증": "피지샘의 과도한 증식으로 형성된 양성 병변",
            "혈관종": "혈관의 양성 증식성 병변",
            "화농 육아종": "외상이나 감염 후 발생하는 반응성 병변",
            "흑색점": "멜라닌 색소의 국소적 침착"
        }
        
        return descriptions.get(disease_name, "해당 질환에 대한 상세 정보가 필요합니다.")
    
    @staticmethod
    def _generate_recommendation(disease_name: str, confidence: float) -> str:
        """질환과 신뢰도에 따른 권장사항 생성"""
        base_recommendation = "※ 본 결과는 AI 예측값으로 참고용입니다. 정확한 진단은 반드시 전문의 상담을 받으시기 바랍니다."
        
        if confidence >= 80:
            specific_rec = "높은 신뢰도의 진단 결과입니다. 가능한 빠른 시일 내에 피부과 전문의 상담을 받으시길 권합니다."
        elif confidence >= 60:
            specific_rec = "중간 정도의 신뢰도입니다. 추가적인 검사나 전문의 상담을 통해 정확한 진단을 받아보시기 바랍니다."
        else:
            specific_rec = "신뢰도가 낮은 결과입니다. 다른 각도에서 재촬영하거나 피부과 전문의 직접 진료를 권장합니다."
        
        # 특정 질환에 대한 추가 권장사항
        urgent_diseases = ["악성흑색종", "기저세포암", "편평세포암", "보웬병"]
        if any(urgent in disease_name for urgent in urgent_diseases):
            specific_rec += " 특히 해당 질환은 조기 진단과 치료가 중요하므로 즉시 전문의 상담을 받으시기 바랍니다."
        
        return f"{specific_rec}\n\n{base_recommendation}"
    
    @staticmethod
    def validate_diagnosis_result(result: Dict[str, Any]) -> bool:
        """진단 결과의 유효성 검증"""
        required_fields = ["predicted_disease", "confidence", "summary"]
        
        for field in required_fields:
            if field not in result or not result[field]:
                logger.warning(f"필수 필드 누락: {field}")
                return False
        
        # 신뢰도 범위 검증
        confidence = result.get("confidence", 0)
        if not isinstance(confidence, (int, float)) or confidence < 0 or confidence > 100:
            logger.warning(f"잘못된 신뢰도 값: {confidence}")
            return False
        
        return True
    
    @staticmethod
    def enhance_result_with_metadata(result: Dict[str, Any], processing_time: float) -> Dict[str, Any]:
        """분석 결과에 메타데이터 추가"""
        result["metadata"] = result.get("metadata", {})
        result["metadata"].update({
            "processing_time_seconds": round(processing_time, 2),
            "parser_version": "1.0.0",
            "parsing_successful": not result.get("parsing_failed", False),
            "confidence_level": DiagnosisResultParser._get_confidence_level(result.get("confidence", 0)),
            "urgency_level": DiagnosisResultParser._get_urgency_level(result.get("predicted_disease", "")),
            "similar_diseases_count": len(result.get("similar_diseases", []))
        })
        
        return result
    
    @staticmethod
    def _get_confidence_level(confidence: float) -> str:
        """신뢰도 레벨 반환"""
        if confidence >= 80:
            return "high"
        elif confidence >= 60:
            return "medium"
        else:
            return "low"
    
    @staticmethod
    def _get_urgency_level(disease_name: str) -> str:
        """긴급도 레벨 반환"""
        high_urgency = ["악성흑색종", "기저세포암", "편평세포암"]
        medium_urgency = ["보웬병", "광선각화증"]
        
        if any(urgent in disease_name for urgent in high_urgency):
            return "high"
        elif any(urgent in disease_name for urgent in medium_urgency):
            return "medium"
        else:
            return "low"
