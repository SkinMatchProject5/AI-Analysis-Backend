#!/usr/bin/env python3
"""
간단한 XML로 변경 후 테스트
HTML에서 잘 되던 간단한 형식 사용
"""

import asyncio
import sys
import os

# 프로젝트 경로 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.hospital_service import hospital_service

async def test_simplified_xml():
    """간단한 XML로 병원 검색 테스트"""
    print("🔍 간단한 XML 형식 테스트 (HTML과 동일)")
    print("="*60)
    
    # 문제였던 질병들 테스트
    test_cases = [
        {
            "name": "악성흑색종",
            "expected": "흑색종 전문병원이 나와야 함"
        },
        {
            "name": "사마귀", 
            "expected": "사마귀 전문병원이 나와야 함"
        },
        {
            "name": "기저세포암",
            "expected": "기저세포암 전문병원 (이미 잘 됨)"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']} 테스트")
        print("-" * 40)
        
        # XML 생성 확인
        xml = hospital_service._create_hospital_xml(
            diagnosis=test_case['name'],
            description=f"{test_case['name']} 치료가 필요합니다.",
            similar_diseases=[]
        )
        
        print(f"생성된 XML:")
        print(xml)
        print()
        
        # 실제 검색
        print("검색 중...")
        result = await hospital_service.search_hospitals_async(
            diagnosis=test_case['name'],
            description=f"{test_case['name']} 치료가 필요합니다.",
            similar_diseases=[],
            final_k=2
        )
        
        if result:
            hospitals = result.get("hospitals", [])
            print(f"✅ {len(hospitals)}개 병원 검색됨")
            
            for j, hospital in enumerate(hospitals, 1):
                parent = hospital.get("parent", {})
                child = hospital.get("child", {})
                
                print(f"\n  {j}. {parent.get('name', '알 수 없음')}")
                print(f"     지역: {parent.get('region', '알 수 없음')}")
                print(f"     전문분야: {parent.get('specialties', [])}")
                print(f"     치료: {child.get('title', '정보 없음')}")
                
                # 관련성 체크
                content = (
                    " ".join(parent.get('specialties', [])) + " " + 
                    child.get('title', '') + " " + 
                    child.get('embedding_text', '')
                ).lower()
                
                disease_keywords = {
                    "악성흑색종": ["흑색종", "멜라노마", "melanoma", "abcde"],
                    "사마귀": ["사마귀", "wart", "verruca", "hpv"],
                    "기저세포암": ["기저세포", "basal", "bcc"]
                }
                
                keywords = disease_keywords.get(test_case['name'], [test_case['name']])
                matched = [kw for kw in keywords if kw in content]
                
                if matched:
                    print(f"     ✅ 관련성 있음: {matched}")
                else:
                    print(f"     ⚠️ 관련성 낮음")
        else:
            print("❌ 검색 실패")
        
        print()

async def compare_before_after():
    """변경 전후 비교"""
    print("📊 간단한 XML vs 복잡한 XML 비교")
    print("="*60)
    
    # 악성흑색종으로 테스트
    diagnosis = "악성흑색종"
    
    print("변경 전 (복잡한 XML)에서는:")
    print("  결과: 분당서울대학교병원 피부과 - 모반 진단·레이저")
    print("  문제: 모반 != 악성흑색종")
    
    print(f"\n변경 후 (간단한 XML) 결과:")
    result = await hospital_service.search_hospitals_async(
        diagnosis=diagnosis,
        description=f"{diagnosis} 치료가 필요합니다.",
        similar_diseases=[],
        final_k=2
    )
    
    if result:
        hospitals = result.get("hospitals", [])
        if hospitals:
            first = hospitals[0]
            parent = first.get("parent", {})
            child = first.get("child", {})
            
            print(f"  결과: {parent.get('name', '알 수 없음')} - {child.get('title', '정보 없음')}")
            
            content = (child.get('title', '') + child.get('embedding_text', '')).lower()
            if any(kw in content for kw in ['흑색종', '멜라노마', 'melanoma']):
                print("  ✅ 개선됨! 흑색종 관련 병원이 나옴")
            else:
                print("  ⚠️ 여전히 관련성 낮음")

if __name__ == "__main__":
    asyncio.run(test_simplified_xml())
    asyncio.run(compare_before_after())
