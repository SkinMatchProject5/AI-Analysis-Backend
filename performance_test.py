#!/usr/bin/env python3
"""
AI-Analysis-Backend 성능 테스트
실제 API 호출 시간을 측정하여 병목지점을 찾습니다.
"""

import asyncio
import time
import httpx
import json
import sys
import os
from typing import Dict, Any

# 프로젝트 경로 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings

class PerformanceTester:
    def __init__(self):
        self.runpod_headers = {
            "Authorization": f"Bearer {settings.RUNPOD_API_KEY}",
            "Content-Type": "application/json"
        }
        
        self.openai_headers = {
            "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }

    async def test_runpod_text_diagnosis(self) -> Dict[str, Any]:
        """RunPod 텍스트 진단 성능 테스트"""
        print("🔍 RunPod 텍스트 진단 테스트 중...")
        
        payload = {
            "model": settings.RUNPOD_MODEL_NAME,
            "messages": [
                {
                    "role": "system",
                    "content": """너는 피부 병변을 진단하는 전문 AI이다. 다음은 네가 진단할 수 있는 피부 병변 목록이며, 각 병변의 임상적 특징은 아래와 같다. 환자에게 나타난 병변의 이미지와 설명을 바탕으로 가장 적합한 질병을 하나 선택하여 진단하라.

0: 광선각화증, 1: 기저세포암, 2: 멜라닌세포모반, 3: 보웬병, 4: 비립종,
5: 사마귀, 6: 악성흑색종, 7: 지루각화증, 8: 편평세포암, 9: 표피낭종,
10: 피부섬유종, 11: 피지샘증식증, 12: 혈관종, 13: 화농 육아종, 14: 흑색점

<root><label id_code="{코드}" score="{점수}">{진단명}</label><summary>{진단소견}</summary><similar_labels><similar_label id_code="{코드}" score="{점수}">{유사질병명}</similar_label></similar_labels></root>"""
                },
                {
                    "role": "user", 
                    "content": "얼굴에 붉은색 각질성 반점이 있습니다. 크기는 약 5mm이고 경계가 불분명합니다. 70세 농부이며 평소 야외활동을 많이 합니다."
                }
            ],
            "max_tokens": 800,
            "temperature": 0.3,
        }
        
        start_time = time.time()
        
        try:
            timeout = httpx.Timeout(120.0)  # 2분 타임아웃
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(
                    f"{settings.RUNPOD_BASE_URL}/chat/completions",
                    json=payload,
                    headers=self.runpod_headers
                )
                
                end_time = time.time()
                elapsed = end_time - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    content = data["choices"][0]["message"]["content"]
                    
                    return {
                        "status": "success",
                        "elapsed_seconds": elapsed,
                        "response_length": len(content),
                        "content": content[:200] + "..." if len(content) > 200 else content
                    }
                else:
                    return {
                        "status": "error",
                        "elapsed_seconds": elapsed,
                        "error_code": response.status_code,
                        "error_message": response.text
                    }
                    
        except Exception as e:
            end_time = time.time()
            elapsed = end_time - start_time
            return {
                "status": "exception",
                "elapsed_seconds": elapsed,
                "error": str(e)
            }

    async def test_openai_text_diagnosis(self) -> Dict[str, Any]:
        """OpenAI 텍스트 진단 성능 테스트 (비교용)"""
        print("🔍 OpenAI 텍스트 진단 테스트 중...")
        
        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {
                    "role": "system",
                    "content": """너는 피부 병변을 진단하는 전문 AI이다. 다음은 네가 진단할 수 있는 피부 병변 목록이며, 각 병변의 임상적 특징은 아래와 같다. 환자에게 나타난 병변의 이미지와 설명을 바탕으로 가장 적합한 질병을 하나 선택하여 진단하라.

0: 광선각화증, 1: 기저세포암, 2: 멜라닌세포모반, 3: 보웬병, 4: 비립종,
5: 사마귀, 6: 악성흑색종, 7: 지루각화증, 8: 편평세포암, 9: 표피낭종,
10: 피부섬유종, 11: 피지샘증식증, 12: 혈관종, 13: 화농 육아종, 14: 흑색점

<root><label id_code="{코드}" score="{점수}">{진단명}</label><summary>{진단소견}</summary><similar_labels><similar_label id_code="{코드}" score="{점수}">{유사질병명}</similar_label></similar_labels></root>"""
                },
                {
                    "role": "user", 
                    "content": "얼굴에 붉은색 각질성 반점이 있습니다. 크기는 약 5mm이고 경계가 불분명합니다. 70세 농부이며 평소 야외활동을 많이 합니다."
                }
            ],
            "max_tokens": 800,
            "temperature": 0.3,
        }
        
        start_time = time.time()
        
        try:
            timeout = httpx.Timeout(60.0)
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    json=payload,
                    headers=self.openai_headers
                )
                
                end_time = time.time()
                elapsed = end_time - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    content = data["choices"][0]["message"]["content"]
                    
                    return {
                        "status": "success",
                        "elapsed_seconds": elapsed,
                        "response_length": len(content),
                        "content": content[:200] + "..." if len(content) > 200 else content
                    }
                else:
                    return {
                        "status": "error",
                        "elapsed_seconds": elapsed,
                        "error_code": response.status_code,
                        "error_message": response.text
                    }
                    
        except Exception as e:
            end_time = time.time()
            elapsed = end_time - start_time
            return {
                "status": "exception",
                "elapsed_seconds": elapsed,
                "error": str(e)
            }

    async def test_multiple_runs(self, provider: str, runs: int = 3):
        """여러 번 테스트하여 평균 성능 측정"""
        print(f"\n🔄 {provider} 성능 테스트 ({runs}회)")
        
        results = []
        total_time = 0
        successful_runs = 0
        
        for i in range(runs):
            print(f"  📊 테스트 {i+1}/{runs} 진행 중...")
            
            if provider.lower() == "runpod":
                result = await self.test_runpod_text_diagnosis()
            elif provider.lower() == "openai":
                result = await self.test_openai_text_diagnosis()
            else:
                print(f"❌ 알 수 없는 프로바이더: {provider}")
                return
            
            results.append(result)
            
            if result["status"] == "success":
                successful_runs += 1
                total_time += result["elapsed_seconds"]
                print(f"    ✅ 성공: {result['elapsed_seconds']:.2f}초")
            else:
                print(f"    ❌ 실패: {result.get('error', result.get('error_message', '알 수 없는 오류'))}")
            
            # 다음 테스트 전 잠시 대기
            if i < runs - 1:
                await asyncio.sleep(2)
        
        # 결과 요약
        print(f"\n📈 {provider} 성능 테스트 결과:")
        print(f"  성공률: {successful_runs}/{runs} ({successful_runs/runs*100:.1f}%)")
        
        if successful_runs > 0:
            avg_time = total_time / successful_runs
            print(f"  평균 응답 시간: {avg_time:.2f}초")
            
            # 개별 결과 출력
            print(f"\n  📋 개별 테스트 결과:")
            for i, result in enumerate(results, 1):
                if result["status"] == "success":
                    print(f"    {i}: {result['elapsed_seconds']:.2f}초")
                else:
                    print(f"    {i}: 실패 ({result.get('error', result.get('error_message', '알 수 없는 오류'))})")
        
        return results

    async def run_comparison_test(self):
        """RunPod vs OpenAI 비교 테스트"""
        print("🚀 AI-Analysis-Backend 성능 비교 테스트 시작")
        print("="*60)
        
        # 설정 정보 출력
        print(f"🔧 현재 설정:")
        print(f"  RunPod Base URL: {settings.RUNPOD_BASE_URL}")
        print(f"  RunPod Model: {settings.RUNPOD_MODEL_NAME}")
        print(f"  OpenAI API 키: {'설정됨' if settings.OPENAI_API_KEY else '설정되지 않음'}")
        print(f"  RunPod API 키: {'설정됨' if settings.RUNPOD_API_KEY else '설정되지 않음'}")
        
        # RunPod 테스트
        runpod_results = await self.test_multiple_runs("runpod", 3)
        
        # OpenAI 테스트 (비교용)
        if settings.OPENAI_API_KEY:
            await asyncio.sleep(3)  # 잠시 대기
            openai_results = await self.test_multiple_runs("openai", 3)
        else:
            print("\n⚠️ OpenAI API 키가 설정되지 않아 OpenAI 테스트를 건너뜁니다.")
            openai_results = []
        
        # 비교 결과 출력
        print("\n🏆 성능 비교 결과")
        print("="*60)
        
        runpod_success = [r for r in runpod_results if r["status"] == "success"]
        openai_success = [r for r in openai_results if r["status"] == "success"]
        
        if runpod_success:
            runpod_avg = sum(r["elapsed_seconds"] for r in runpod_success) / len(runpod_success)
            print(f"RunPod 평균: {runpod_avg:.2f}초 ({len(runpod_success)}/{len(runpod_results)} 성공)")
        
        if openai_success:
            openai_avg = sum(r["elapsed_seconds"] for r in openai_success) / len(openai_success)
            print(f"OpenAI 평균: {openai_avg:.2f}초 ({len(openai_success)}/{len(openai_results)} 성공)")
        
        # 권장사항
        print("\n💡 성능 개선 권장사항:")
        if runpod_success and any(r["elapsed_seconds"] > 60 for r in runpod_success):
            print("  ⚠️ RunPod 응답 시간이 60초를 초과합니다.")
            print("     - 모델 최적화 필요")
            print("     - 서버 위치 확인")
            print("     - 요청 크기 줄이기 (max_tokens, temperature 조정)")
        
        if runpod_success and openai_success:
            runpod_avg = sum(r["elapsed_seconds"] for r in runpod_success) / len(runpod_success)
            openai_avg = sum(r["elapsed_seconds"] for r in openai_success) / len(openai_success)
            
            if runpod_avg > openai_avg * 2:
                print("     - RunPod이 OpenAI보다 2배 이상 느림")
                print("     - OpenAI로 프로바이더 변경 고려")
            elif openai_avg > runpod_avg * 2:
                print("     - OpenAI가 RunPod보다 2배 이상 느림")
                print("     - RunPod 사용 유지 권장")

async def main():
    """메인 테스트 실행"""
    tester = PerformanceTester()
    await tester.run_comparison_test()

if __name__ == "__main__":
    asyncio.run(main())
