#!/usr/bin/env python3
"""
RunPod 통합 테스트 (최종 버전)
기존: test_runpod_final.py + test_runpod_integration.py + test_skin_diagnosis_runpod.py 통합
"""

import asyncio
import sys
import os

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.providers.runpod_medical import RunPodMedicalInterpreter
from app.services.langchain_service import langchain_service
from app.core.config import settings

async def test_runpod_provider():
    """RunPod 프로바이더 직접 테스트"""
    print("🧪 RunPod 프로바이더 직접 테스트")
    print(f"API Key: {settings.RUNPOD_API_KEY[:20]}...")
    print(f"Base URL: {settings.RUNPOD_BASE_URL}")
    print(f"Model Name: '{settings.RUNPOD_MODEL_NAME}'")
    print()
    
    provider = RunPodMedicalInterpreter()
    
    # 텍스트 진단 테스트 (softmax 확률값 포함)
    print("1️⃣ 텍스트 기반 피부 진단 (실제 softmax 확률값)")
    try:
        result = await provider.diagnose_text(
            description="얼굴에 있는 붉은색 각질성 반점이 거칠고 만지면 까칠합니다.",
            additional_info="70세 농부, 장기간 야외 작업"
        )
        print("✅ 텍스트 진단 성공!")
        print(f"진단 결과: {result}")
        
        # XML에서 실제 확률값 추출 확인
        import re
        score_match = re.search(r'score="([^"]+)"', result)
        if score_match:
            confidence = float(score_match.group(1))
            print(f"🎯 추출된 실제 확률값: {confidence}%")
            
            if confidence > 0 and confidence <= 100:
                print("✅ 올바른 확률값 범위")
            else:
                print("⚠️ 확률값 범위 이상")
        
        return True
    except Exception as e:
        print(f"❌ 텍스트 진단 실패: {str(e)}")
        return False

async def test_langchain_integration():
    """LangChain 서비스 통합 테스트"""
    print("\n🔗 LangChain 서비스 통합 테스트")
    print(f"현재 프로바이더: {settings.SKIN_DIAGNOSIS_PROVIDER}")
    
    try:
        result = await langchain_service.diagnose_skin_lesion(
            lesion_description="손등에 있는 거친 표면의 붉은색 반점입니다.",
            additional_info="65세 농부, 장기간 야외 작업"
        )
        print("✅ LangChain 통합 성공!")
        print(f"ID: {result['id']}")
        print(f"프로바이더: {result['metadata']['provider']}")
        print(f"모델: {result['metadata']['model']}")
        
        # 실제 확률값 확인
        xml_result = result['result']
        import re
        score_match = re.search(r'score="([^"]+)"', xml_result)
        if score_match:
            confidence = float(score_match.group(1))
            print(f"🎯 LangChain을 통한 실제 확률값: {confidence}%")
        
        return True
    except Exception as e:
        print(f"❌ LangChain 통합 실패: {str(e)}")
        return False

async def main():
    """메인 테스트"""
    print("=" * 70)
    print("🎯 RunPod 통합 테스트 (Softmax 확률값 포함)")
    print("=" * 70)
    print(f"설정 정보:")
    print(f"  - SKIN_DIAGNOSIS_PROVIDER: {settings.SKIN_DIAGNOSIS_PROVIDER}")
    print(f"  - RUNPOD_BASE_URL: {settings.RUNPOD_BASE_URL}")
    print(f"  - RUNPOD_MODEL_NAME: '{settings.RUNPOD_MODEL_NAME}' (빈 문자열)")
    print(f"  - RUNPOD_API_KEY: {'설정됨' if settings.RUNPOD_API_KEY else '미설정'}")
    print("=" * 70)
    
    # 1. RunPod 프로바이더 직접 테스트
    provider_success = await test_runpod_provider()
    
    if provider_success:
        # 2. LangChain 서비스 통합 테스트
        service_success = await test_langchain_integration()
        
        print("\n" + "=" * 70)
        if service_success:
            print("🎉 RunPod 통합 완료! (실제 Softmax 확률값 사용)")
            print("\n✅ 다음 단계:")
            print("  1. FastAPI 서버 실행: python -m app.main")
            print("  2. API 테스트: python tests/api/test_skin_diagnosis_api.py")
        else:
            print("❌ LangChain 통합 실패")
    else:
        print("\n" + "=" * 70)
        print("❌ RunPod 프로바이더 테스트 실패")
    
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(main())
