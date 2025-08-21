#!/usr/bin/env python3
"""
증상 문장 다듬기 API 테스트 스크립트
빈 텍스트 입력 시 하드코딩된 메시지 반환 테스트
"""

import asyncio
import httpx
import json

# 테스트할 API 엔드포인트
BASE_URL = "http://localhost:8001"
UTTERANCE_ENDPOINT = f"{BASE_URL}/api/v1/utterance/refine"

async def test_utterance_api():
    """증상 문장 다듬기 API 테스트"""
    async with httpx.AsyncClient() as client:
        
        print("=== 증상 문장 다듬기 API 테스트 ===\n")
        
        # 테스트 케이스 1: 정상적인 텍스트 입력
        print("1. 정상 텍스트 입력 테스트")
        test_data_1 = {
            "text": "팔 접히는 부분에 붉고 따갑고 간지러워요. 긁다 보니 피가 났어요.",
            "language": "ko"
        }
        
        try:
            response = await client.post(UTTERANCE_ENDPOINT, json=test_data_1)
            print(f"상태 코드: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"정제된 텍스트: {result['refined_text']}")
                print(f"스타일: {result['style']}")
                print(f"모델: {result['model']}")
            else:
                print(f"오류: {response.text}")
        except Exception as e:
            print(f"요청 실패: {e}")
        
        print("\n" + "="*50 + "\n")
        
        # 테스트 케이스 2: 빈 텍스트 입력
        print("2. 빈 텍스트 입력 테스트")
        test_data_2 = {
            "text": "",
            "language": "ko"
        }
        
        try:
            response = await client.post(UTTERANCE_ENDPOINT, json=test_data_2)
            print(f"상태 코드: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"반환된 텍스트: {result['refined_text']}")
                print(f"스타일: {result['style']}")
                print(f"모델: {result['model']}")
                
                # 하드코딩된 메시지 확인
                expected_message = "해당 결과는 AI 분석 결과이므로 맹신해서는 안되며 정확한 진단은 병원에서 받아보시길 권장드립니다."
                if result['refined_text'] == expected_message:
                    print("✅ 하드코딩된 메시지 정상 반환!")
                else:
                    print("❌ 예상과 다른 메시지 반환")
            else:
                print(f"오류: {response.text}")
        except Exception as e:
            print(f"요청 실패: {e}")
        
        print("\n" + "="*50 + "\n")
        
        # 테스트 케이스 3: text 필드 없음 (None)
        print("3. text 필드 없음 테스트")
        test_data_3 = {
            "language": "ko"
        }
        
        try:
            response = await client.post(UTTERANCE_ENDPOINT, json=test_data_3)
            print(f"상태 코드: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"반환된 텍스트: {result['refined_text']}")
                print(f"스타일: {result['style']}")
                print(f"모델: {result['model']}")
                
                # 하드코딩된 메시지 확인
                expected_message = "해당 결과는 AI 분석 결과이므로 맹신해서는 안되며 정확한 진단은 병원에서 받아보시길 권장드립니다."
                if result['refined_text'] == expected_message:
                    print("✅ 하드코딩된 메시지 정상 반환!")
                else:
                    print("❌ 예상과 다른 메시지 반환")
            else:
                print(f"오류: {response.text}")
        except Exception as e:
            print(f"요청 실패: {e}")
        
        print("\n" + "="*50 + "\n")
        
        # 테스트 케이스 4: 공백만 있는 텍스트
        print("4. 공백만 있는 텍스트 테스트")
        test_data_4 = {
            "text": "   ",
            "language": "ko"
        }
        
        try:
            response = await client.post(UTTERANCE_ENDPOINT, json=test_data_4)
            print(f"상태 코드: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"반환된 텍스트: {result['refined_text']}")
                print(f"스타일: {result['style']}")
                print(f"모델: {result['model']}")
                
                # 하드코딩된 메시지 확인
                expected_message = "해당 결과는 AI 분석 결과이므로 맹신해서는 안되며 정확한 진단은 병원에서 받아보시길 권장드립니다."
                if result['refined_text'] == expected_message:
                    print("✅ 하드코딩된 메시지 정상 반환!")
                else:
                    print("❌ 예상과 다른 메시지 반환")
            else:
                print(f"오류: {response.text}")
        except Exception as e:
            print(f"요청 실패: {e}")

if __name__ == "__main__":
    print("서버가 http://localhost:8001에서 실행 중인지 확인하세요.")
    print("테스트를 시작합니다...\n")
    
    asyncio.run(test_utterance_api())
    
    print("\n테스트 완료!")
    print("\n프론트엔드 연동 가이드:")
    print("- 텍스트가 있을 때: 정상적인 정제된 문장 반환")
    print("- 텍스트가 없을 때: 고정된 면책 메시지 반환")
    print("- style 필드로 구분 가능: 'doctor-visit' vs 'default-disclaimer'")