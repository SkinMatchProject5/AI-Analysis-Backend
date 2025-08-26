#!/usr/bin/env python3
"""
AI-Analysis-Backend 빠른 성능 테스트
"""

import asyncio
import time
import sys
import os

# 프로젝트 경로 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.langchain_service import langchain_service
from app.core.config import settings

async def test_text_diagnosis():
    """텍스트 진단 성능 테스트"""
    print("🔍 텍스트 진단 테스트 시작...")
    print(f"프로바이더: {settings.SKIN_DIAGNOSIS_PROVIDER}")
    print(f"타임아웃: {settings.REQUEST_TIMEOUT}초")
    print(f"최대 토큰: {settings.MAX_TOKENS}")
    
    test_description = "얼굴에 붉은색 각질성 반점이 있습니다. 크기는 약 5mm이고 경계가 불분명합니다."
    
    start_time = time.time()
    
    try:
        result = await langchain_service.diagnose_skin_lesion(
            lesion_description=test_description,
            additional_info="70세 농부, 평소 야외활동 많음"
        )
        
        end_time = time.time()
        elapsed = end_time - start_time
        
        print(f"✅ 성공!")
        print(f"⏱️ 소요 시간: {elapsed:.2f}초")
        print(f"📝 결과 길이: {len(result.get('result', ''))} 글자")
        print(f"🎯 결과 미리보기: {result.get('result', '')[:100]}...")
        
        if elapsed > 30:
            print("⚠️ 30초 초과! 여전히 느림")
        elif elapsed > 15:
            print("⚠️ 15초 초과. 더 최적화 필요")
        else:
            print("✅ 성능 개선됨!")
        
        return True
        
    except Exception as e:
        end_time = time.time()
        elapsed = end_time - start_time
        
        print(f"❌ 실패!")
        print(f"⏱️ 실패까지 시간: {elapsed:.2f}초")
        print(f"💥 에러: {str(e)}")
        return False

async def main():
    print("🚀 AI-Analysis-Backend 빠른 성능 테스트")
    print("="*50)
    
    # 현재 설정 출력
    print(f"현재 설정:")
    print(f"  SKIN_DIAGNOSIS_PROVIDER: {settings.SKIN_DIAGNOSIS_PROVIDER}")
    print(f"  REQUEST_TIMEOUT: {settings.REQUEST_TIMEOUT}")
    print(f"  MAX_TOKENS: {settings.MAX_TOKENS}")
    print(f"  TEMPERATURE: {settings.TEMPERATURE}")
    print()
    
    success = await test_text_diagnosis()
    
    if success:
        print("\n🎉 테스트 완료! 성능이 개선되었는지 확인하세요.")
    else:
        print("\n💡 추가 최적화 방안:")
        print("1. .env에서 REQUEST_TIMEOUT을 더 줄이기")
        print("2. MAX_TOKENS를 300으로 줄이기") 
        print("3. 프로바이더를 openai로 변경")

if __name__ == "__main__":
    asyncio.run(main())
