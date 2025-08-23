#!/usr/bin/env python3
"""
RunPod 분류 확률 테스트
실제 15개 클래스에 대한 softmax 확률을 찾는다
"""

import asyncio
import httpx
import json
from app.core.config import settings

async def test_classification_probabilities():
    """RunPod API에서 분류 확률 추출 테스트"""
    print("🔍 RunPod 분류 확률 탐지 테스트")
    print(f"Base URL: {settings.RUNPOD_BASE_URL}")
    print()
    
    headers = {
        "Authorization": f"Bearer {settings.RUNPOD_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # 다양한 옵션으로 API 요청해보기
    test_configs = [
        {
            "name": "기본 + logprobs",
            "payload": {
                "model": "",
                "messages": [{"role": "user", "content": "Test"}],
                "max_tokens": 50,
                "logprobs": True,
                "top_logprobs": 15
            }
        },
        {
            "name": "output_scores 옵션",
            "payload": {
                "model": "",
                "messages": [{"role": "user", "content": "Test"}],
                "max_tokens": 50,
                "output_scores": True,
                "return_full_text": False
            }
        },
        {
            "name": "details 옵션",
            "payload": {
                "model": "",
                "messages": [{"role": "user", "content": "Test"}],
                "max_tokens": 50,
                "details": True,
                "best_of": 1
            }
        },
        {
            "name": "echo + logprobs",
            "payload": {
                "model": "",
                "messages": [{"role": "user", "content": "Test"}],
                "max_tokens": 50,
                "echo": True,
                "logprobs": 15
            }
        }
    ]
    
    for config in test_configs:
        print(f"\n📋 테스트: {config['name']}")
        print(f"요청: {json.dumps(config['payload'], indent=2)}")
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{settings.RUNPOD_BASE_URL}/chat/completions",
                    json=config['payload'],
                    headers=headers
                )
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ 성공!")
                    
                    # 응답 구조 분석
                    print("📥 응답 구조:")
                    analyze_response_structure(data, prefix="  ")
                    
                else:
                    error_data = response.json() if response.text else {}
                    print(f"❌ 실패: {response.status_code}")
                    print(f"에러: {error_data.get('message', response.text)}")
                    
        except Exception as e:
            print(f"❌ 오류: {str(e)}")

def analyze_response_structure(data, prefix=""):
    """응답 구조를 재귀적으로 분석"""
    if isinstance(data, dict):
        for key, value in data.items():
            if key in ["logprobs", "scores", "probabilities", "classification", "output_scores"]:
                print(f"{prefix}🎯 {key}: {type(value)}")
                if isinstance(value, (dict, list)) and value:
                    analyze_response_structure(value, prefix + "  ")
            elif isinstance(value, (dict, list)) and key != "message":
                print(f"{prefix}{key}: {type(value)}")
                if isinstance(value, dict) and len(value) <= 10:  # 작은 dict만 재귀
                    analyze_response_structure(value, prefix + "  ")
                elif isinstance(value, list) and len(value) <= 5:  # 작은 list만 재귀
                    for i, item in enumerate(value):
                        print(f"{prefix}  [{i}]: {type(item)}")
                        if isinstance(item, dict):
                            analyze_response_structure(item, prefix + "    ")
            else:
                if isinstance(value, str) and len(value) > 50:
                    print(f"{prefix}{key}: string (길이: {len(value)})")
                else:
                    print(f"{prefix}{key}: {type(value)} = {value}")
    elif isinstance(data, list):
        for i, item in enumerate(data):
            print(f"{prefix}[{i}]: {type(item)}")
            if isinstance(item, dict):
                analyze_response_structure(item, prefix + "  ")

async def test_medical_classification():
    """의료 진단 요청으로 분류 확률 테스트"""
    print("\n" + "="*70)
    print("🏥 의료 진단 분류 확률 테스트")
    print("="*70)
    
    headers = {
        "Authorization": f"Bearer {settings.RUNPOD_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # 의료 진단 요청
    payload = {
        "model": "",
        "messages": [
            {
                "role": "system", 
                "content": """너는 피부 병변을 진단하는 AI이다. 다음 15개 질병 중 하나를 선택하라:
0: 광선각화증, 1: 기저세포암, 2: 멜라닌세포모반, 3: 보웬병, 4: 비립종,
5: 사마귀, 6: 악성흑색종, 7: 지루각화증, 8: 편평세포암, 9: 표피낭종,
10: 피부섬유종, 11: 피지샘증식증, 12: 혈관종, 13: 화농 육아종, 14: 흑색점

각 질병에 대한 확률을 반환하라."""
            },
            {
                "role": "user",
                "content": "얼굴에 있는 붉은색 각질성 반점을 진단해주세요."
            }
        ],
        "max_tokens": 200,
        "temperature": 0.1,
        "logprobs": True,
        "top_logprobs": 15
    }
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{settings.RUNPOD_BASE_URL}/chat/completions",
                json=payload,
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                print("✅ 의료 진단 요청 성공!")
                
                # logprobs 상세 분석
                if "choices" in data and data["choices"]:
                    choice = data["choices"][0]
                    
                    if "logprobs" in choice and choice["logprobs"]:
                        print("\n🔬 LogProbs 상세 분석:")
                        logprobs = choice["logprobs"]
                        
                        for key, value in logprobs.items():
                            print(f"  {key}: {type(value)}")
                            if key == "content" and isinstance(value, list):
                                print(f"    content 토큰 수: {len(value)}")
                                for i, token_data in enumerate(value[:3]):  # 처음 3개만
                                    print(f"    [{i}]: {token_data}")
                
                # 전체 응답 저장
                with open("runpod_classification_response.json", "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                print("\n💾 전체 응답을 runpod_classification_response.json에 저장")
                
            else:
                print(f"❌ 의료 진단 요청 실패: {response.status_code}")
                print(f"에러: {response.text}")
                
    except Exception as e:
        print(f"❌ 의료 진단 테스트 오류: {str(e)}")

async def main():
    """메인 테스트"""
    print("🎯 RunPod 분류 확률 탐지 테스트")
    print("목표: 15개 피부질환 클래스에 대한 실제 softmax 확률 찾기")
    print("="*70)
    
    # 1. 다양한 API 옵션 테스트
    await test_classification_probabilities()
    
    # 2. 의료 진단 전용 테스트
    await test_medical_classification()
    
    print("\n" + "="*70)
    print("🔍 결론:")
    print("1. runpod_classification_response.json 파일 확인")
    print("2. logprobs 구조에서 분류 확률을 찾을 수 있는지 분석")
    print("3. 만약 없다면 모델 자체에 확률 출력을 요청해야 함")
    print("="*70)

if __name__ == "__main__":
    asyncio.run(main())
