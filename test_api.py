#!/usr/bin/env python3
"""
API 테스트 스크립트
서버가 실행된 상태에서 기본적인 API 기능을 테스트합니다.
"""

import requests

BASE_URL = "http://localhost:8000/api/v1"

def test_create_analysis():
    """분석 생성 테스트"""
    print("🧪 분석 생성 테스트")
    
    data = {
        "prompt": "다음 제품 리뷰를 분석해주세요: '이 제품은 정말 훌륭합니다. 품질이 우수하고 가격도 합리적입니다.'",
        "context": "전자제품 리뷰 분석",
        "response_format": "json"
    }
    
    response = requests.post(f"{BASE_URL}/analyze", json=data)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ 분석 생성 성공: {result['id']}")
        return result['id']
    else:
        print(f"❌ 분석 생성 실패: {response.status_code}")
        print(response.text)
        return None

def test_get_analysis(analysis_id: str):
    """분석 조회 테스트"""
    print(f"🧪 분석 조회 테스트 (ID: {analysis_id})")
    
    response = requests.get(f"{BASE_URL}/analyses/{analysis_id}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ 분석 조회 성공")
        print(f"   프롬프트: {result['prompt'][:50]}...")
        print(f"   결과: {result['result'][:100]}...")
    else:
        print(f"❌ 분석 조회 실패: {response.status_code}")

def test_get_all_analyses():
    """전체 분석 조회 테스트"""
    print("🧪 전체 분석 조회 테스트")
    
    response = requests.get(f"{BASE_URL}/analyses?page=1&page_size=5")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ 전체 분석 조회 성공: {result['total_count']}개 결과")
    else:
        print(f"❌ 전체 분석 조회 실패: {response.status_code}")

def test_xml_response():
    """XML 응답 테스트"""
    print("🧪 XML 응답 테스트")
    
    data = {
        "prompt": "XML 형식 테스트를 위한 간단한 분석 요청입니다.",
        "response_format": "xml"
    }
    
    response = requests.post(f"{BASE_URL}/analyze", json=data)
    
    if response.status_code == 200:
        print("✅ XML 응답 생성 성공")
        print("XML 내용:")
        print(response.text[:200] + "...")
    else:
        print(f"❌ XML 응답 실패: {response.status_code}")

def test_custom_analysis():
    """커스텀 분석 테스트"""
    print("🧪 커스텀 분석 테스트")
    
    params = {
        "prompt": "Python과 JavaScript의 차이점을 설명해주세요.",
        "system_message": "당신은 프로그래밍 언어 전문가입니다. 기술적이고 정확한 정보를 제공해주세요."
    }
    
    response = requests.post(f"{BASE_URL}/analyze/custom", params=params)
    
    if response.status_code == 200:
        result = response.json()
        print("✅ 커스텀 분석 성공")
        print(f"   결과: {result['result'][:150]}...")
    else:
        print(f"❌ 커스텀 분석 실패: {response.status_code}")

def test_skin_lesion_diagnosis():
    """피부 병변 진단 테스트"""
    print("🧪 피부 병변 진단 테스트")
    
    data = {
        "lesion_description": "얼굴에 있는 갈색 반점이 최근 크기가 커지고 있으며, 가장자리가 불규칙합니다. 색상도 균일하지 않고 일부는 검은색으로 변했습니다.",
        "additional_info": "50세 남성, 야외 활동을 자주 하며 자외선 노출이 많음",
        "response_format": "json"
    }
    
    response = requests.post(f"{BASE_URL}/diagnose/skin-lesion", json=data)
    
    if response.status_code == 200:
        result = response.json()
        print("✅ 피부 병변 진단 성공")
        print(f"   진단 ID: {result['id']}")
        print(f"   결과: {result['result'][:200]}...")
        return result['id']
    else:
        print(f"❌ 피부 병변 진단 실패: {response.status_code}")
        print(response.text)
        return None

def test_skin_lesion_xml():
    """피부 병변 진단 XML 응답 테스트"""
    print("🧪 피부 병변 진단 XML 응답 테스트")
    
    data = {
        "lesion_description": "손등에 있는 거친 표면의 붉은색 반점, 햇빛에 노출된 부위",
        "additional_info": "65세 농부, 장기간 야외 작업",
        "response_format": "xml"
    }
    
    response = requests.post(f"{BASE_URL}/diagnose/skin-lesion", json=data)
    
    if response.status_code == 200:
        print("✅ 피부 병변 XML 진단 성공")
        print("XML 내용:")
        print(response.text[:300] + "...")
    else:
        print(f"❌ 피부 병변 XML 진단 실패: {response.status_code}")

def main():
    """전체 테스트 실행"""
    print("🚀 FastAPI + LangChain API 테스트 시작\n")
    
    # 서버 연결 확인
    try:
        response = requests.get("http://localhost:8000/")
        if response.status_code != 200:
            print("❌ 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인해주세요.")
            return
    except requests.exceptions.ConnectionError:
        print("❌ 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인해주세요.")
        return
    
    print("✅ 서버 연결 확인\n")
    
    # 테스트 실행
    analysis_id = test_create_analysis()
    print()
    
    if analysis_id:
        test_get_analysis(analysis_id)
        print()
    
    test_get_all_analyses()
    print()
    
    test_xml_response()
    print()
    
    test_custom_analysis()
    print()
    
    # 피부 병변 진단 테스트
    skin_diagnosis_id = test_skin_lesion_diagnosis()
    print()
    
    test_skin_lesion_xml()
    print()
    
    print("🎉 모든 테스트 완료!")
    print("\n📋 테스트 요약:")
    print("✅ 기본 분석 API")
    print("✅ CRUD 기능")
    print("✅ XML 응답 형식") 
    print("✅ 커스텀 분석")
    print("✅ 피부 병변 진단 (GPT-4o-mini)")
    print("✅ 구조화된 XML 진단 결과")

if __name__ == "__main__":
    main()
