#!/usr/bin/env python3
"""
분류 확률 디버깅
"""

import asyncio
import sys
import os
import httpx
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings

async def test_raw_classification_output():
    """AI가 실제로 15개 클래스 확률을 어떻게 출력하는지 확인"""
    print("🔍 실제 분류 확률 출력 디버깅")
    
    headers = {
        "Authorization": f"Bearer {settings.RUNPOD_API_KEY}",
        "Content-Type": "application/json"
    }
    
    classification_prompt = """
    환자의 피부 병변: 얼굴에 있는 붉은색 각질성 반점
    추가 정보: 70세 농부
    
    다음 15개 피부질환 클래스에 대한 분류 확률을 정확히 제공해주세요:
    
    0: 광선각화증, 1: 기저세포암, 2: 멜라닌세포모반, 3: 보웬병, 4: 비립종,
    5: 사마귀, 6: 악성흑색종, 7: 지루각화증, 8: 편평세포암, 9: 표피낭종,
    10: 피부섬유종, 11: 피지샘증식증, 12: 혈관종, 13: 화농 육아종, 14: 흑색점
    
    각 클래스에 대한 확률을 다음 형식으로 제공:
    0.xxxx: 광선각화증
    0.xxxx: 기저세포암
    0.xxxx: 멜라닌세포모반
    ... (모든 15개 클래스의 확률을 반드시 모두 나열)
    """
    
    payload = {
        "model": "",
        "messages": [
            {"role": "user", "content": classification_prompt}
        ],
        "max_tokens": 500,
        "temperature": 0.1,
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
                content = data["choices"][0]["message"]["content"]
                
                print("✅ AI 응답 성공!")
                print(f"\n📝 AI 원본 응답:")
                print("="*70)
                print(content)
                print("="*70)
                
                # 확률 파싱 디버깅
                import re
                pattern = r'(\d+\.\d+):\s*([^\n\r]+)'
                matches = re.findall(pattern, content)
                
                print(f"\n🔍 파싱된 확률 ({len(matches)}개):")
                total_prob = 0
                for prob_str, disease_name in matches:
                    prob = float(prob_str)
                    total_prob += prob
                    print(f"  {prob:.4f} ({prob*100:5.1f}%): {disease_name}")
                
                print(f"\n📊 총 확률 합계: {total_prob:.4f}")
                
                if len(matches) < 15:
                    print(f"⚠️ 15개 클래스 중 {len(matches)}개만 파싱됨")
                    print("💡 AI가 모든 클래스 확률을 제공하지 않았을 수 있음")
                
                if abs(total_prob - 1.0) > 0.1:
                    print(f"⚠️ 확률 합계가 1.0이 아님 (차이: {abs(total_prob - 1.0):.4f})")
                    print("💡 이는 정규화되지 않은 확률이거나 일부 클래스가 누락됨을 의미")
                    
                return content
                
            else:
                print(f"❌ API 오류: {response.status_code}")
                print(f"응답: {response.text}")
                
    except Exception as e:
        print(f"❌ 오류: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_raw_classification_output())
