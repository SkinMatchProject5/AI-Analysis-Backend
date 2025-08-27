#!/usr/bin/env python3
"""
간단한 병원 검색 테스트
"""

import asyncio
import sys
import os

# 프로젝트 경로 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.hospital_service import hospital_service

async def simple_test():
    """간단한 병원 검색 테스트"""
    print("🏥 간단한 병원 검색 테스트")
    print("="*50)
    
    # 광선각화증으로 테스트
    print("🔍 검색 중: 광선각화증")
    
    result = await hospital_service.search_hospitals_async(
        diagnosis="광선각화증",
        description="얼굴에 붉은색 각질성 반점",
        similar_diseases=["보웬병"],
        final_k=3
    )
    
    if result:
        hospitals = result.get("hospitals", [])
        print(f"✅ {len(hospitals)}개 병원 검색됨")
        
        for i, hospital in enumerate(hospitals, 1):
            parent = hospital.get("parent", {})
            child = hospital.get("child", {})
            
            print(f"\n{i}. {parent.get('name', '알 수 없음')}")
            print(f"   지역: {parent.get('region', '알 수 없음')}")
            print(f"   치료: {child.get('title', '정보 없음')}")
            
            # 관련성 체크
            content = (child.get('title', '') + child.get('embedding_text', '')).lower()
            if any(kw in content for kw in ['광선각화', '각화', '자외선']):
                print("   ✅ 관련성 있음")
            else:
                print("   ⚠️ 관련성 낮음")
    else:
        print("❌ 검색 실패")

if __name__ == "__main__":
    asyncio.run(simple_test())
