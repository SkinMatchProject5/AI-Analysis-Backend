#!/usr/bin/env python3
"""
전체 시스템 통합 테스트
기존: test_api.py + test_hybrid_setup.py 통합
"""

import asyncio
import sys
import os

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.services.langchain_service import langchain_service
from app.core.config import settings
import requests
import time

async def test_text_diagnosis():
    """텍스트 진단 테스트"""
    print("🧪 텍스트 진단 테스트")
    try:
        result = await langchain_service.diagnose_skin_lesion(
            lesion_description="얼굴에 있는 갈색 반점이 최근 크기가 커지고 있습니다.",
            additional_info="50세 남성, 야외 활동 많음"
        )
        print("✅ 텍스트 진단 성공!")
        print(f"프로바이더: {result['metadata']['provider']}")
        print(f"진단 결과: {result['result'][:200]}...")
        return True
    except Exception as e:
        print(f"❌ 텍스트 진단 실패: {str(e)}")
        return False

def test_api_endpoints():
    """API 엔드포인트 테스트"""
    print("\n🔗 API 엔드포인트 테스트")
    
    # 헬스체크
    try:
        response = requests.get("http://localhost:8001/", timeout=5)
        print(f"✅ 헬스체크: {response.status_code}")
    except Exception as e:
        print(f"❌ 서버 연결 실패: {str(e)}")
        return False
    
    # 텍스트 진단 API
    try:
        data = {
            "lesion_description": "얼굴에 있는 갈색 반점이 커지고 있습니다.",
            "additional_info": "50세 남성",
            "response_format": "json"
        }
        
        response = requests.post(
            "http://localhost:8001/api/v1/diagnose/skin-lesion",
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 텍스트 API 성공!")
            print(f"진단명: {result.get('diagnosis', 'N/A')}")
            print(f"신뢰도: {result.get('confidence', 'N/A')}%")
            return True
        else:
            print(f"❌ API 오류: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ API 테스트 실패: {str(e)}")
        return False

async def main():
    """메인 테스트"""
    print("=" * 70)
    print("🎯 AI-Analysis-Backend 전체 시스템 테스트")
    print("=" * 70)
    print(f"프로바이더: {settings.SKIN_DIAGNOSIS_PROVIDER}")
    print("=" * 70)
    
    # 1. 서비스 레벨 테스트
    service_success = await test_text_diagnosis()
    
    # 2. API 레벨 테스트  
    api_success = test_api_endpoints()
    
    print("\n" + "=" * 70)
    if service_success and api_success:
        print("🎉 전체 시스템 테스트 통과!")
    else:
        print("❌ 일부 테스트 실패")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(main())
