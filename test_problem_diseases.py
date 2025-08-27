#!/usr/bin/env python3
"""
문제 질병들 특별 테스트
표피낭종, 사마귀, 악성흑색종 등 잘 안나오던 질병들
"""

import asyncio
import sys
import os

# 프로젝트 경로 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.hospital_service import hospital_service

async def test_problem_diseases():
    """문제 질병들 개별 테스트"""
    print("🧪 문제 질병들 특별 테스트")
    print("="*70)
    
    # 이전에 문제였던 질병들
    problem_diseases = [
        {
            "name": "악성흑색종",
            "expected_keywords": ["흑색종", "멜라노마", "melanoma", "ABCDE"],
            "expected_hospitals": ["세브란스병원 흑색종클리닉", "고려대학교 안암병원 흑색종클리닉"],
            "avoid_keywords": ["모반", "점", "nevus"]
        },
        {
            "name": "사마귀", 
            "expected_keywords": ["사마귀", "wart", "verruca", "HPV"],
            "expected_hospitals": ["사려니의원", "오라클피부과"],
            "avoid_keywords": ["피지샘", "sebaceous", "한관종"]
        },
        {
            "name": "표피낭종",
            "expected_keywords": ["표피낭종", "epidermoid", "낭종", "케라틴"],
            "expected_hospitals": ["오체안성형외과", "아문성형외과"],
            "avoid_keywords": ["피지샘", "한관종", "사마귀"]
        },
        {
            "name": "피지샘증식증",
            "expected_keywords": ["피지샘", "sebaceous", "hyperplasia"],
            "expected_hospitals": ["차앤유클리닉", "미모드림의원"],
            "avoid_keywords": ["사마귀", "낭종", "모반"]
        },
        {
            "name": "혈관종",
            "expected_keywords": ["혈관종", "hemangioma", "vascular"],
            "expected_hospitals": ["세브란스병원 혈관종클리닉", "성빈센트병원 혈관종클리닉"],
            "avoid_keywords": ["화농육아종", "사마귀", "낭종"]
        }
    ]
    
    for i, disease in enumerate(problem_diseases, 1):
        print(f"\n{i}. 🔍 {disease['name']} 테스트")
        print("-" * 50)
        
        # XML 생성 먼저 확인
        xml = hospital_service._create_hospital_xml(
            diagnosis=disease['name'],
            description=f"{disease['name']} 치료가 필요한 환자",
            similar_diseases=[]  # 유사질병 제거됨
        )
        
        print(f"📤 생성된 XML:")
        print(xml)
        print()
        
        # 병원 검색 실행
        print(f"🔍 검색 실행 중...")
        result = await hospital_service.search_hospitals_async(
            diagnosis=disease['name'],
            description=f"{disease['name']} 치료가 필요한 환자",
            similar_diseases=[],  # 유사질병 제거됨
            final_k=3
        )
        
        if result:
            hospitals = result.get("hospitals", [])
            meta = result.get("meta", {})
            
            print(f"✅ {len(hospitals)}개 병원 검색됨 (소요: {meta.get('elapsed_ms', 0):.0f}ms)")
            
            if hospitals:
                print(f"\n📋 검색 결과:")
                
                relevant_count = 0
                wrong_count = 0
                
                for j, hospital in enumerate(hospitals, 1):
                    parent = hospital.get("parent", {})
                    child = hospital.get("child", {})
                    scores = hospital.get("scores", {})
                    
                    hospital_name = parent.get('name', '알 수 없음')
                    specialties = parent.get('specialties', [])
                    treatment = child.get('title', '정보 없음')
                    
                    print(f"\n  {j}. 🏥 {hospital_name}")
                    print(f"     📍 지역: {parent.get('region', '알 수 없음')}")
                    print(f"     💊 전문분야: {specialties}")
                    print(f"     🔬 치료: {treatment}")
                    print(f"     📊 점수: {scores.get('combined', scores.get('rerank', 0)):.3f}")
                    
                    # 관련성 분석
                    all_text = (
                        " ".join(specialties) + " " + 
                        treatment + " " + 
                        child.get('embedding_text', '')
                    ).lower()
                    
                    # 기대 키워드 매칭
                    expected_matches = [kw for kw in disease['expected_keywords'] if kw.lower() in all_text]
                    
                    # 피해야 할 키워드 매칭
                    avoid_matches = [kw for kw in disease['avoid_keywords'] if kw.lower() in all_text]
                    
                    if expected_matches and not avoid_matches:
                        print(f"     ✅ 완전 관련성: {expected_matches}")
                        relevant_count += 1
                    elif expected_matches:
                        print(f"     ⚠️ 부분 관련성: {expected_matches} (하지만 {avoid_matches}도 포함)")
                        relevant_count += 1
                    elif avoid_matches:
                        print(f"     ❌ 잘못된 결과: {avoid_matches} 관련 (원하는 것: {disease['name']})")
                        wrong_count += 1
                    else:
                        print(f"     ⚠️ 관련성 불분명")
                
                # 결과 평가
                print(f"\n📊 결과 평가:")
                print(f"   관련성 있음: {relevant_count}/{len(hospitals)}")
                print(f"   잘못된 결과: {wrong_count}/{len(hospitals)}")
                
                if relevant_count >= len(hospitals) // 2:
                    print(f"   ✅ 양호: {disease['name']} 검색 성공")
                elif wrong_count > relevant_count:
                    print(f"   ❌ 심각한 문제: 잘못된 결과가 더 많음")
                    print(f"      💡 벡터DB나 리랭킹에 문제 있을 수 있음")
                else:
                    print(f"   ⚠️ 개선 필요: 관련성 점수 조정 필요")
                    
                # 기대하던 병원이 나왔는지 체크
                found_expected = False
                for expected_hospital in disease['expected_hospitals']:
                    for hospital in hospitals:
                        if expected_hospital.lower() in hospital.get('parent', {}).get('name', '').lower():
                            found_expected = True
                            print(f"   🎯 기대 병원 발견: {expected_hospital}")
                            break
                
                if not found_expected:
                    print(f"   ⚠️ 기대 병원 못찾음: {disease['expected_hospitals']}")
            
            else:
                print("❌ 검색 결과 없음")
        else:
            print("❌ 검색 실패")
        
        print()

async def test_comparison():
    """비교 테스트: 같은 질병을 다른 방식으로"""
    print("📊 비교 테스트")
    print("="*70)
    
    test_disease = "사마귀"
    
    print(f"🔍 {test_disease} 비교 테스트:")
    
    # 1. 현재 방식 (유사질병 제외)
    print(f"\n1️⃣ 현재 방식 (유사질병 제외):")
    result1 = await hospital_service.search_hospitals_async(
        diagnosis=test_disease,
        description=f"{test_disease} 치료",
        similar_diseases=[],
        final_k=2
    )
    
    if result1 and result1.get("hospitals"):
        for i, hospital in enumerate(result1["hospitals"], 1):
            parent = hospital.get("parent", {})
            child = hospital.get("child", {})
            print(f"   {i}. {parent.get('name', '알 수 없음')} - {child.get('title', '정보 없음')}")
    
    # 2. 유사질병 포함 방식 (비교용)
    print(f"\n2️⃣ 만약 유사질병 포함했다면:")
    result2 = await hospital_service.search_hospitals_async(
        diagnosis=test_disease,
        description=f"{test_disease} 치료",
        similar_diseases=["지루각화증", "비립종"],  # 사마귀와 혼동될 수 있는 질병
        final_k=2
    )
    
    if result2 and result2.get("hospitals"):
        for i, hospital in enumerate(result2["hospitals"], 1):
            parent = hospital.get("parent", {})
            child = hospital.get("child", {})
            print(f"   {i}. {parent.get('name', '알 수 없음')} - {child.get('title', '정보 없음')}")
    
    print(f"\n💡 결론: 유사질병 제외가 더 정확한 결과를 가져오는지 확인")

if __name__ == "__main__":
    asyncio.run(test_problem_diseases())
    asyncio.run(test_comparison())
