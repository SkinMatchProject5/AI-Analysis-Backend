#!/usr/bin/env python3
"""
AI-Analysis-Backend → Hospital-Location-Backend 연동 테스트
실제 XML이 제대로 전송되고 파싱되는지 확인
"""

import asyncio
import sys
import os
import json

# 프로젝트 경로 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.hospital_service import hospital_service
from app.core.config import settings

async def test_hospital_xml_generation():
    """병원 XML 생성 테스트"""
    print("🔍 병원 XML 생성 테스트")
    print("="*50)
    
    # 테스트 데이터
    test_cases = [
        {
            "diagnosis": "광선각화증",
            "description": "자외선 노출이 많은 부위인 얼굴에 붉은색의 각질성 반점이 관찰됩니다. 만성 자외선 노출로 인한 DNA 손상으로 발생하며, 피부암으로의 진행 가능성이 있습니다.",
            "similar_diseases": ["보웬병", "기저세포암", "편평세포암"]
        },
        {
            "diagnosis": "악성흑색종", 
            "description": "피부에 검은 점이 생기고 크기가 변하며 비대칭적인 형태를 보입니다.",
            "similar_diseases": ["멜라닌세포모반", "흑색점"]
        },
        {
            "diagnosis": "사마귀",
            "description": "손가락에 거친 표면의 융기된 병변이 관찰됩니다.",
            "similar_diseases": ["지루각화증"]
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 테스트 케이스 {i}: {test_case['diagnosis']}")
        
        # XML 생성
        xml = hospital_service._create_hospital_xml(
            diagnosis=test_case["diagnosis"],
            description=test_case["description"], 
            similar_diseases=test_case["similar_diseases"]
        )
        
        print(f"생성된 XML:")
        print("─" * 40)
        print(xml)
        print("─" * 40)

async def test_hospital_search_request():
    """실제 병원 검색 요청 테스트"""
    print("\n🏥 실제 병원 검색 요청 테스트")
    print("="*50)
    
    print(f"병원 백엔드 URL: {settings.HOSPITAL_BACKEND_URL}")
    
    # 광선각화증으로 테스트
    test_diagnosis = "광선각화증"
    test_description = "얼굴에 붉은색 각질성 반점이 관찰되며, 자외선 노출이 원인으로 추정됩니다."
    test_similar = ["보웬병", "기저세포암"]
    
    print(f"\n🔍 검색 진단명: {test_diagnosis}")
    print(f"설명: {test_description}")
    print(f"유사 질병: {test_similar}")
    
    try:
        result = await hospital_service.search_hospitals_async(
            diagnosis=test_diagnosis,
            description=test_description,
            similar_diseases=test_similar,
            final_k=3
        )
        
        if result:
            hospitals = result.get("hospitals", [])
            meta = result.get("meta", {})
            
            print(f"\n✅ 검색 성공!")
            print(f"검색된 병원 수: {len(hospitals)}")
            print(f"검색 소요 시간: {meta.get('elapsed_ms', 0):.2f}ms")
            
            print(f"\n📋 검색 결과:")
            for j, hospital in enumerate(hospitals, 1):
                parent = hospital.get("parent", {})
                child = hospital.get("child", {})
                scores = hospital.get("scores", {})
                
                print(f"\n  {j}. {parent.get('name', '알 수 없는 병원')}")
                print(f"     지역: {parent.get('region', '알 수 없음')}")
                print(f"     연락처: {parent.get('contacts', {}).get('tel', '정보 없음')}")
                print(f"     치료: {child.get('title', '정보 없음')}")
                print(f"     점수: Dense={scores.get('dense', 0):.3f}, Combined={scores.get('combined', 0):.3f}")
            
            # 진단명과 병원의 연관성 체크
            print(f"\n🔍 연관성 체크:")
            relevant_hospitals = 0
            for hospital in hospitals:
                child_title = hospital.get("child", {}).get("title", "").lower()
                if any(keyword in child_title for keyword in ["광선각화", "각화", "자외선", "피부암"]):
                    relevant_hospitals += 1
            
            print(f"  관련성 있는 병원: {relevant_hospitals}/{len(hospitals)}")
            if relevant_hospitals == 0:
                print("  ⚠️ 관련성이 낮은 결과! 벡터DB 검색에 문제가 있을 수 있습니다.")
            else:
                print(f"  ✅ {relevant_hospitals}개 병원이 관련성 있음")
            
        else:
            print("❌ 검색 실패 - 결과 없음")
            
    except Exception as e:
        print(f"❌ 검색 중 오류: {str(e)}")
        import traceback
        traceback.print_exc()

async def test_different_diseases():
    """다양한 질병으로 검색 테스트"""
    print("\n🧪 다양한 질병 검색 테스트")
    print("="*50)
    
    test_diseases = [
        {"name": "악성흑색종", "keywords": ["흑색종", "멜라노마", "melanoma"]},
        {"name": "기저세포암", "keywords": ["기저세포", "basal", "암"]},
        {"name": "사마귀", "keywords": ["사마귀", "wart", "바이러스"]},
        {"name": "지루각화증", "keywords": ["지루", "각화", "seborrheic"]},
    ]
    
    for disease in test_diseases:
        print(f"\n🔍 {disease['name']} 검색...")
        
        try:
            result = await hospital_service.search_hospitals_async(
                diagnosis=disease['name'],
                description=f"{disease['name']}에 대한 진단 소견입니다.",
                similar_diseases=[],
                final_k=2
            )
            
            if result and result.get("hospitals"):
                hospitals = result["hospitals"]
                print(f"  ✅ {len(hospitals)}개 병원 검색됨")
                
                # 첫 번째 병원 정보
                if hospitals:
                    first_hospital = hospitals[0]
                    parent = first_hospital.get("parent", {})
                    child = first_hospital.get("child", {})
                    
                    print(f"  Top 1: {parent.get('name', '알 수 없음')}")
                    print(f"    치료: {child.get('title', '정보 없음')}")
                    
                    # 키워드 매칭 체크
                    title_lower = child.get('title', '').lower()
                    matched_keywords = [kw for kw in disease['keywords'] if kw.lower() in title_lower]
                    if matched_keywords:
                        print(f"    ✅ 매칭된 키워드: {matched_keywords}")
                    else:
                        print(f"    ⚠️ 키워드 매칭 없음: {disease['keywords']}")
            else:
                print(f"  ❌ 검색 결과 없음")
                
        except Exception as e:
            print(f"  ❌ 오류: {str(e)}")

async def main():
    """메인 테스트 실행"""
    print("🚀 AI-Analysis-Backend ↔ Hospital-Location-Backend 연동 테스트")
    print("="*80)
    
    # 1. XML 생성 테스트
    await test_hospital_xml_generation()
    
    # 2. 실제 병원 검색 테스트  
    await test_hospital_search_request()
    
    # 3. 다양한 질병 검색 테스트
    await test_different_diseases()
    
    print("\n🎯 테스트 완료!")
    print("\n💡 문제 해결 방법:")
    print("1. Hospital-Location-Backend가 실행 중인지 확인")
    print("2. XML 형식이 올바른지 확인")
    print("3. 벡터DB에 해당 질병 데이터가 있는지 확인")
    print("4. 검색 키워드와 벡터DB 내용의 일치성 확인")

if __name__ == "__main__":
    asyncio.run(main())
