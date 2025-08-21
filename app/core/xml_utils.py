import xml.etree.ElementTree as ET
from typing import Dict, Any
from datetime import datetime

def dict_to_xml(data: Dict[str, Any], root_name: str = "response") -> str:
    """딕셔너리를 XML 문자열로 변환"""
    root = ET.Element(root_name)
    _dict_to_xml_element(data, root)
    
    # XML 선언과 함께 문자열로 변환
    xml_str = ET.tostring(root, encoding='unicode', method='xml')
    return f'<?xml version="1.0" encoding="UTF-8"?>\n{xml_str}'

def _dict_to_xml_element(data: Any, parent: ET.Element):
    """재귀적으로 딕셔너리를 XML 엘리먼트로 변환"""
    if isinstance(data, dict):
        for key, value in data.items():
            # 키 이름 정규화 (XML에서 유효하지 않은 문자 처리)
            safe_key = _make_xml_safe_key(key)
            child = ET.SubElement(parent, safe_key)
            _dict_to_xml_element(value, child)
    
    elif isinstance(data, list):
        for i, item in enumerate(data):
            child = ET.SubElement(parent, f"item_{i}")
            _dict_to_xml_element(item, child)
    
    elif isinstance(data, datetime):
        parent.text = data.isoformat()
    
    else:
        parent.text = str(data) if data is not None else ""

def _make_xml_safe_key(key: str) -> str:
    """XML 태그명으로 안전한 키 생성"""
    # 공백을 언더스코어로 변경
    safe_key = key.replace(" ", "_")
    # 숫자로 시작하는 경우 prefix 추가
    if safe_key and safe_key[0].isdigit():
        safe_key = f"field_{safe_key}"
    # 특수문자 제거
    safe_key = "".join(c for c in safe_key if c.isalnum() or c == "_")
    return safe_key or "unknown_field"

def analysis_to_xml(analysis_data: Dict[str, Any]) -> str:
    """분석 결과를 XML로 변환"""
    return dict_to_xml(analysis_data, "analysis")

def analysis_list_to_xml(analyses_data: Dict[str, Any]) -> str:
    """분석 결과 리스트를 XML로 변환"""
    return dict_to_xml(analyses_data, "analyses_response")
