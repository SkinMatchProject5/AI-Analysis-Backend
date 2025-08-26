#!/usr/bin/env python3
"""
AI-Analysis-Backend에서 Hospital 호출 디버깅
실제 호출 과정과 응답을 단계별로 확인
"""

import asyncio
import sys
import os

# 프로젝트 경로 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.hospital_service import hospital_service
from app.core.config import settings

async def debug_hospital_service():
    """병원 서비스 호출 디버깅"""
    print("🔍 AI-Analysis-Backend → Hospital-Location-Backend 호출 디버깅")
    print("="*70)
    
    # 설정 확인
    print(f"🔧 현재 설정:")
    print(f"   HOSPITAL_BACKEND_URL: {settings.HOSPITAL_BACKEND_URL}")
    print()
    
    # 1. XML 생성 테스트
    print("📝 1단계: XML 생성 테스트")
    print("-" * 40)
    
    test_diagnosis = "광선각화증"
    test_description = "자외선 노출이 많은 부위인 얼굴에 붉은색의 각질성 반점이 관찰됩니다. 만성 자외선 노출로 인한 DNA 손상으로 발생하며, 피부암으로의 진행 가능성이 있습니다."
    test_similar = ["보웬병", "기저세포암"]
    
    print(f"진단명: {test_diagnosis}")
    print(f"설명: {test_description}")
    print(f"유사질병: {test_similar}")
    print()
    
    # XML 생성
    generated_xml = hospital_service._create_hospital_xml(
        diagnosis=test_diagnosis,
        description=test_description,
        similar_diseases=test_similar
    )
    
    print(f"생성된 XML:")
    print("┌" + "─" * 50 + "┐")
    for line in generated_xml.split('\n'):
        print(f"│ {line:<48} │")
    print("└" + "─" * 50 + "┘")
    print()
    
    # 2. 병원 백엔드 연결 테스트
    print("🌐 2단계: Hospital-Location-Backend 연결 테스트")
    print("-" * 40)
    
    try:
        import requests
        health_response = requests.get(f"{settings.HOSPITAL_BACKEND_URL}/health", timeout=5)
        
        if health_response.status_code == 200:
            health_data = health_response.json()
            print("✅ Hospital-Location-Backend 연결 성공!")
            print(f"   상태: {health_data.get('status', 'unknown')}")
            print(f"   Qdrant: {health_data.get('qdrant_status', 'unknown')}")
            print(f"   리랭커: {health_data.get('reranker_status', 'unknown')}")
        else:
            print(f"❌ Health check 실패: {health_response.status_code}")
            print("   Hospital-Location-Backend가 제대로 실행되지 않았을 수 있습니다.")
            return
            
    except Exception as e:
        print(f"❌ 연결 실패: {e}")
        print("💡 해결방법:")
        print("   cd Hospital-Location-Backend")
        print("   python main.py")
        return
    
    print()
    
    # 3. 실제 병원 검색 호출
    print("🏥 3단계: 실제 병원 검색 호출")
    print("-" * 40)
    
    print("검색 요청 중...")
    result = await hospital_service.search_hospitals_async(
        diagnosis=test_diagnosis,
        description=test_description,
        similar_diseases=test_similar,
        final_k=3
    )
    
    if result:
        hospitals = result.get("hospitals", [])
        meta = result.get("meta", {})
        
        print(f"✅ 검색 성공!")
        print(f"   검색된 병원 수: {len(hospitals)}")
        print(f"   소요 시간: {meta.get('elapsed_ms', 0):.2f}ms")
        print(f"   요청 ID: {meta.get('request_id', 'N/A')}")
        print()
        
        if hospitals:
            print("🏥 검색 결과 분석:")
            print("-" * 40)
            
            for i, hospital in enumerate(hospitals, 1):
                parent = hospital.get("parent", {})
                child = hospital.get("child", {})
                scores = hospital.get("scores", {})
                
                print(f"\n{i}. 🏥 {parent.get('name', '알 수 없는 병원')}")
                print(f"   📍 지역: {parent.get('region', '알 수 없음')}")
                print(f"   📞 연락처: {parent.get('contacts', {}).get('tel', '정보 없음')}")
                print(f"   💊 전문분야: {parent.get('specialties', [])}")
                print(f"   🔬 치료내용: {child.get('title', '정보 없음')}")
                print(f"   📊 검색점수: {scores.get('combined', 0):.3f}")
                
                # 관련성 체크
                specialties = parent.get("specialties", [])
                title = child.get("title", "")
                embedding_text = child.get("embedding_text", "")
                
                # 광선각화증 관련 키워드 체크
                ak_keywords = ["광선각화", "각화", "자외선", "AK", "Actinic"]
                
                specialty_matches = [kw for kw in ak_keywords if any(kw.lower() in spec.lower() for spec in specialties)]
                content_matches = [kw for kw in ak_keywords if kw.lower() in (title + embedding_text).lower()]
                
                if specialty_matches or content_matches:
                    print(f"   ✅ 관련성 있음: {specialty_matches + content_matches}")
                else:
                    print(f"   ⚠️ 관련성 낮음 - 키워드 매칭 없음")
                    print(f"   📝 내용: {embedding_text[:80]}...")
            
            # 전체 관련성 평가
            relevant_count = sum(1 for hospital in hospitals 
                               if _is_relevant_to_ak(hospital))
            
            print(f"\n📊 전체 관련성 평가:")
            print(f"   관련 병원: {relevant_count}/{len(hospitals)} ({relevant_count/len(hospitals)*100:.1f}%)")
            
            if relevant_count == 0:
                print("   ❌ 완전히 관련 없는 결과!")
                print("   💡 문제: 벡터 검색이 제대로 작동하지 않음")
                print("   🔧 확인 사항:")
                print("      - Qdrant에 '광선각화증' 데이터가 있는지")
                print("      - 임베딩 모델이 한국어를 제대로 처리하는지")
                print("      - 리랭킹이 올바르게 작동하는지")
            elif relevant_count < len(hospitals) // 2:
                print("   ⚠️ 관련성이 낮음")
                print("   💡 개선 필요: 검색 알고리즘 또는 리랭킹 조정")
            else:
                print("   ✅ 양호한 검색 결과")
        
        else:
            print("❌ 검색 결과가 없습니다!")
            
    else:
        print("❌ 병원 검색 실패")
        print("   가능한 원인:")
        print("   - Hospital-Location-Backend 내부 오류")
        print("   - Qdrant 연결 문제")
        print("   - 파이프라인 초기화 실패")

def _is_relevant_to_ak(hospital):
    """광선각화증 관련성 체크"""
    parent = hospital.get("parent", {})
    child = hospital.get("child", {})
    
    specialties = parent.get("specialties", [])
    title = child.get("title", "")
    embedding_text = child.get("embedding_text", "")
    
    ak_keywords = ["광선각화", "각화", "자외선", "AK", "Actinic"]
    
    # 전문분야에서 매칭
    specialty_match = any(kw.lower() in " ".join(specialties).lower() for kw in ak_keywords)
    
    # 내용에서 매칭
    content = (title + " " + embedding_text).lower()
    content_match = any(kw.lower() in content for kw in ak_keywords)
    
    return specialty_match or content_match

async def test_other_diseases():
    """다른 질병들로 테스트"""
    print("\n🧪 4단계: 다른 질병 검색 테스트")
    print("-" * 40)
    
    diseases = [
        {
            "name": "악성흑색종",
            "keywords": ["흑색종", "멜라노마", "melanoma", "ABCDE"]
        },
        {
            "name": "사마귀", 
            "keywords": ["사마귀", "wart", "verruca", "HPV"]
        },
        {
            "name": "기저세포암",
            "keywords": ["기저세포", "basal", "BCC"]
        }
    ]
    
    for disease in diseases:
        print(f"\n🔍 {disease['name']} 검색...")
        
        result = await hospital_service.search_hospitals_async(
            diagnosis=disease['name'],
            description=f"{disease['name']}에 대한 진단 소견입니다.",
            similar_diseases=[],
            final_k=2
        )
        
        if result and result.get("hospitals"):
            hospitals = result["hospitals"]
            print(f"   ✅ {len(hospitals)}개 병원 검색됨")
            
            if hospitals:
                first_hospital = hospitals[0]
                parent = first_hospital.get("parent", {})
                child = first_hospital.get("child", {})
                
                print(f"   Top 1: {parent.get('name', '알 수 없음')}")
                print(f"   치료: {child.get('title', '정보 없음')}")
                
                # 키워드 매칭
                content = (child.get('title', '') + child.get('embedding_text', '')).lower()
                matched = [kw for kw in disease['keywords'] if kw.lower() in content]
                
                if matched:
                    print(f"   ✅ 키워드 매칭: {matched}")
                else:
                    print(f"   ⚠️ 키워드 매칭 없음")
        else:
            print(f"   ❌ 검색 결과 없음")

async def main():
    """메인 실행"""
    await debug_hospital_service()
    await test_other_diseases()
    
    print(f"\n🎯 디버깅 완료!")
    print(f"\n💡 결론:")
    print("1. XML 생성이 정상이고 백엔드 연결도 된다면")
    print("2. 벡터DB 검색 자체에 문제가 있을 가능성이 높음")
    print("3. Qdrant 임베딩 또는 리랭킹 알고리즘 점검 필요")

if __name__ == "__main__":
    asyncio.run(main())
