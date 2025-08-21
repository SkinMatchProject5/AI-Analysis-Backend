import logging
import re
import xml.etree.ElementTree as ET
from typing import Dict, Optional

logger = logging.getLogger(__name__)
XML_ROOT_PATTERN = re.compile(r'<root>.*?</root>', re.DOTALL)


def parse_diagnosis_xml(xml_response: str) -> Dict[str, Optional[str]]:
    """XML 응답을 파싱하여 구조화된 데이터로 변환.

    기존 skin_diagnosis 라우터 내부 로직을 유틸로 분리한 동일 동작.
    """
    try:
        xml_match = XML_ROOT_PATTERN.search(xml_response)
        if not xml_match:
            logger.warning(f"XML 형식을 찾을 수 없음: {xml_response}")
            return {
                "diagnosis": xml_response,
                "confidence_score": None,
                "recommendations": None,
                "similar_conditions": None,
            }

        xml_content = xml_match.group(0)
        root = ET.fromstring(xml_content)

        label_elem = root.find('label')
        diagnosis = label_elem.text if label_elem is not None else "진단 결과 없음"
        confidence_score = None
        if label_elem is not None and 'score' in label_elem.attrib:
            try:
                confidence_score = float(label_elem.attrib['score']) / 100.0
            except ValueError:
                pass

        summary_elem = root.find('summary')
        recommendations = summary_elem.text if summary_elem is not None else None

        similar_labels = []
        similar_labels_elem = root.find('similar_labels')
        if similar_labels_elem is not None:
            for similar_label in similar_labels_elem.findall('similar_label'):
                if similar_label.text:
                    similar_labels.append(similar_label.text)
        similar_conditions = ", ".join(similar_labels) if similar_labels else None

        return {
            "diagnosis": diagnosis,
            "confidence_score": confidence_score,
            "recommendations": recommendations,
            "similar_conditions": similar_conditions,
        }
    except ET.ParseError as e:
        logger.error(f"XML 파싱 오류: {e}, 원본 응답: {xml_response}")
        return {
            "diagnosis": xml_response,
            "confidence_score": None,
            "recommendations": None,
            "similar_conditions": None,
        }
    except Exception as e:
        logger.error(f"진단 결과 파싱 중 오류: {e}")
        return {
            "diagnosis": xml_response,
            "confidence_score": None,
            "recommendations": None,
            "similar_conditions": None,
        }

