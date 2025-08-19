#!/usr/bin/env python3
"""
AI 분석 API 디버깅용 테스트 스크립트
"""

import requests
import base64
import io
from PIL import Image
import json

def create_test_image():
    """테스트용 이미지 생성"""
    # 간단한 테스트 이미지 생성
    img = Image.new('RGB', (100, 100), color='red')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    return img_bytes

def test_skin_diagnosis_api():
    """피부 진단 API 테스트"""
    print("🧪 AI 분석 API 테스트 시작...")
    
    # API 엔드포인트
    url = "http://localhost:8001/api/v1/diagnose/skin-lesion-image"
    
    # 테스트 이미지 생성
    test_image = create_test_image()
    
    # 요청 데이터 준비
    files = {
        'image': ('test_image.jpg', test_image, 'image/jpeg')
    }
    
    data = {
        'additional_info': '테스트용 피부 분석 요청입니다.',
        'response_format': 'json'
    }
    
    try:
        print(f"📡 요청 전송 중: {url}")
        print(f"📝 데이터: {data}")
        
        response = requests.post(url, files=files, data=data, timeout=30)
        
        print(f"📊 응답 상태: {response.status_code}")
        print(f"📄 응답 헤더: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ API 테스트 성공!")
            print(f"🔬 분석 결과:")
            print(f"  - ID: {result.get('id', 'N/A')}")
            print(f"  - 진단: {result.get('predicted_disease', 'N/A')}")
            print(f"  - 신뢰도: {result.get('confidence', 'N/A')}%")
            print(f"  - 요약: {result.get('summary', 'N/A')[:100]}...")
        else:
            print(f"❌ API 테스트 실패: {response.status_code}")
            print(f"📄 응답 내용: {response.text}")
            
            if response.status_code == 422:
                try:
                    error_detail = response.json()
                    print(f"🔍 검증 오류 상세:")
                    print(json.dumps(error_detail, indent=2, ensure_ascii=False))
                except:
                    pass
                    
    except requests.exceptions.RequestException as e:
        print(f"🚨 네트워크 오류: {e}")
    except Exception as e:
        print(f"🚨 예상치 못한 오류: {e}")

def test_health_check():
    """헬스체크 테스트"""
    print("\n🏥 헬스체크 테스트...")
    
    try:
        response = requests.get("http://localhost:8001/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print("✅ 서비스 정상 작동 중")
            print(f"  - OpenAI 설정: {'✅' if health_data.get('openai_configured') else '❌'}")
            print(f"  - 환경: {health_data.get('environment', 'N/A')}")
        else:
            print(f"❌ 헬스체크 실패: {response.status_code}")
    except Exception as e:
        print(f"🚨 헬스체크 오류: {e}")

if __name__ == "__main__":
    test_health_check()
    test_skin_diagnosis_api()
