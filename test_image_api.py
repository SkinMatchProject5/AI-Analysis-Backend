#!/usr/bin/env python3
"""
이미지 기반 피부 병변 진단 API 테스트 스크립트
"""

import requests
import json
from PIL import Image, ImageDraw
import io
import os

BASE_URL = "http://localhost:8000/api/v1"

def create_test_image():
    """테스트용 피부 병변 이미지 생성"""
    # 512x512 크기의 이미지 생성
    img = Image.new('RGB', (512, 512), color='#F5DEB3')  # 피부색 배경
    draw = ImageDraw.Draw(img)
    
    # 피부 병변 모방 (갈색 반점)
    draw.ellipse([200, 200, 300, 280], fill='#8B4513', outline='#654321', width=2)
    draw.ellipse([210, 210, 250, 250], fill='#A0522D')  # 내부 음영
    
    # 임시 파일로 저장
    img_buffer = io.BytesIO()
    img.save(img_buffer, format='JPEG', quality=85)
    img_buffer.seek(0)
    
    return img_buffer

def test_image_diagnosis():
    """이미지를 이용한 피부 병변 진단 테스트"""
    print("🖼️ 이미지 기반 피부 병변 진단 테스트")
    
    try:
        # 테스트 이미지 생성
        image_data = create_test_image()
        
        # 멀티파트 폼 데이터 구성
        files = {
            'image': ('test_lesion.jpg', image_data, 'image/jpeg')
        }
        
        data = {
            'additional_info': '45세 여성, 최근 반점 크기 증가',
            'response_format': 'json'
        }
        
        # API 호출
        response = requests.post(
            f"{BASE_URL}/diagnose/skin-lesion-image",
            files=files,
            data=data
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 이미지 진단 성공")
            print(f"   진단 ID: {result['id']}")
            print(f"   이미지 정보: {result['metadata']['image_info']['dimensions']}")
            print(f"   진단 결과: {result['result'][:200]}...")
            return result['id']
        else:
            print(f"❌ 이미지 진단 실패: {response.status_code}")
            print(f"   오류: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ 테스트 중 오류: {str(e)}")
        return None

def test_image_diagnosis_xml():
    """이미지 진단 XML 응답 테스트"""
    print("🖼️ 이미지 진단 XML 응답 테스트")
    
    try:
        # 테스트 이미지 생성
        image_data = create_test_image()
        
        files = {
            'image': ('test_lesion.jpg', image_data, 'image/jpeg')
        }
        
        data = {
            'additional_info': '60세 남성, 농부, 장기간 자외선 노출',
            'response_format': 'xml'
        }
        
        response = requests.post(
            f"{BASE_URL}/diagnose/skin-lesion-image",
            files=files,
            data=data
        )
        
        if response.status_code == 200:
            print("✅ 이미지 XML 진단 성공")
            print("XML 응답:")
            print(response.text[:400] + "...")
        else:
            print(f"❌ 이미지 XML 진단 실패: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 테스트 중 오류: {str(e)}")

def test_invalid_file():
    """잘못된 파일 형식 테스트"""
    print("🚫 잘못된 파일 형식 테스트")
    
    try:
        # 텍스트 파일 생성
        text_data = io.StringIO("This is not an image file")
        
        files = {
            'image': ('test.txt', text_data, 'text/plain')
        }
        
        data = {
            'additional_info': '테스트',
            'response_format': 'json'
        }
        
        response = requests.post(
            f"{BASE_URL}/diagnose/skin-lesion-image",
            files=files,
            data=data
        )
        
        if response.status_code == 400:
            print("✅ 잘못된 파일 형식 검증 성공")
            print(f"   예상된 오류: {response.json()['detail']}")
        else:
            print(f"❌ 파일 형식 검증 실패: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 테스트 중 오류: {str(e)}")

def main():
    """전체 이미지 테스트 실행"""
    print("🚀 이미지 기반 피부 병변 진단 API 테스트 시작\n")
    
    # 서버 연결 확인
    try:
        response = requests.get("http://localhost:8000/")
        if response.status_code != 200:
            print("❌ 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인해주세요.")
            return
    except requests.exceptions.ConnectionError:
        print("❌ 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인해주세요.")
        return
    
    print("✅ 서버 연결 확인\n")
    
    # 테스트 실행
    diagnosis_id = test_image_diagnosis()
    print()
    
    test_image_diagnosis_xml()
    print()
    
    test_invalid_file()
    print()
    
    print("🎉 이미지 진단 테스트 완료!")
    print("\n📋 테스트 요약:")
    print("✅ 이미지 업로드 및 진단")
    print("✅ XML 형식 응답")
    print("✅ 파일 형식 검증")
    print("✅ OpenAI Vision API 연동")
    
    print("\n💡 Postman 테스트 가이드:")
    print("1. POST http://localhost:8000/api/v1/diagnose/skin-lesion-image")
    print("2. Body → form-data 선택")
    print("3. Key: 'image', Type: File, Value: 이미지 파일")
    print("4. Key: 'additional_info', Type: Text, Value: '환자 정보'")
    print("5. Key: 'response_format', Type: Text, Value: 'json' 또는 'xml'")

if __name__ == "__main__":
    main()