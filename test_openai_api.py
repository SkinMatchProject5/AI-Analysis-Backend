#!/usr/bin/env python3
# OpenAI API 실제 테스트

import os
from dotenv import load_dotenv
from openai import OpenAI
import asyncio

load_dotenv()

async def test_openai_api():
    print("🧪 OpenAI API 실제 호출 테스트...")
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ API 키가 없습니다.")
        return
    
    print(f"🔑 API 키: {api_key[:10]}...{api_key[-4:]} (길이: {len(api_key)})")
    
    try:
        # 클라이언트 생성
        client = OpenAI(api_key=api_key)
        print("✅ OpenAI 클라이언트 생성 성공")
        
        # 간단한 텍스트 완성 테스트
        print("📤 간단한 텍스트 완성 요청 중...")
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": "Hello, can you respond with 'API test successful'?"}
            ],
            max_tokens=10
        )
        
        print(f"✅ API 호출 성공!")
        print(f"📨 응답: {response.choices[0].message.content}")
        
        # gpt-4o-mini 모델 테스트 (현재 사용 중인 모델)
        print("\n📤 gpt-4o-mini 모델 테스트...")
        
        response2 = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": "Test gpt-4o-mini model. Respond with 'Model test OK'."}
            ],
            max_tokens=10
        )
        
        print(f"✅ gpt-4o-mini 모델 테스트 성공!")
        print(f"📨 응답: {response2.choices[0].message.content}")
        
    except Exception as e:
        print(f"❌ API 호출 실패: {e}")
        print(f"🔍 오류 타입: {type(e).__name__}")
        
        # 상세한 오류 정보
        if hasattr(e, 'response'):
            print(f"📄 응답 상태: {e.response.status_code if hasattr(e.response, 'status_code') else 'N/A'}")
        
        if "401" in str(e):
            print("💡 401 오류는 API 키 문제를 의미합니다.")
            print("   - API 키가 유효한지 확인해주세요")
            print("   - API 키에 충분한 크레딧이 있는지 확인해주세요")
            print("   - OpenAI 계정이 활성화되어 있는지 확인해주세요")
        elif "429" in str(e):
            print("💡 429 오류는 요청 한도 초과를 의미합니다.")
        elif "403" in str(e):
            print("💡 403 오류는 권한 문제를 의미합니다.")

if __name__ == "__main__":
    asyncio.run(test_openai_api())
