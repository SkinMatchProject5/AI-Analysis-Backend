#!/usr/bin/env python3
"""
간단한 RunPod 분류 확률 테스트
"""

import asyncio
import httpx
import json
from app.core.config import settings

async def test_simple():
    """간단한 분류 확률 테스트"""
    print("🔍 RunPod 분류 확률 간단 테스트")
    
    headers = {
        "Authorization": f"Bearer {settings.RUNPOD_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # 매우 간단한 요청으로 구조 파악
    payload = {
        "model": "",
        "messages": [
            {
                "role": "system",
                "content": "당신은 15개의 피부질환을 분류하는 AI입니다. 각 질환에 대한 확률을 제공해주세요."
            },
            {
                "role": "user", 
                "content": "얼굴의 붉은 반점을 15개 피부질환 중에서 분류하고, 각각의 확률을 알려주세요."
            }
        ],
        "max_tokens": 100,
        "temperature": 0.1,
        "logprobs": True,
        "top_logprobs": 5
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{settings.RUNPOD_BASE_URL}/chat/completions",
                json=payload,
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                print("✅ 요청 성공!")
                
                # 응답 내용 출력
                if "choices" in data:
                    content = data["choices"][0]["message"]["content"]
                    print(f"\n📝 AI 응답:")
                    print(content)
                    
                    # logprobs 확인
                    if "logprobs" in data["choices"][0]:
                        logprobs = data["choices"][0]["logprobs"]
                        print(f"\n🔬 LogProbs 구조:")
                        print(f"Keys: {list(logprobs.keys())}")
                        
                        if "content" in logprobs and logprobs["content"]:
                            print(f"Content tokens: {len(logprobs['content'])}")
                            # 첫 번째 토큰만 상세히 보기
                            first_token = logprobs["content"][0]
                            print(f"첫 번째 토큰: {json.dumps(first_token, indent=2)}")
                
                # 간단한 JSON 저장
                with open("simple_response.json", "w") as f:
                    json.dump(data, f, indent=2)
                print("\n💾 simple_response.json 저장 완료")
                
            else:
                print(f"❌ 실패: {response.status_code}")
                print(f"응답: {response.text}")
                
    except Exception as e:
        print(f"❌ 오류: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_simple())
