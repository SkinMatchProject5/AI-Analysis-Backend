#!/usr/bin/env python3
# 환경변수 로딩 테스트

import os
from dotenv import load_dotenv

print("🔍 환경변수 로딩 테스트...")

# 현재 디렉토리 확인
print(f"📁 현재 디렉토리: {os.getcwd()}")

# .env 파일 존재 확인
env_file_path = ".env"
if os.path.exists(env_file_path):
    print(f"✅ .env 파일 발견: {env_file_path}")
    
    # 파일 내용 확인 (첫 5줄만)
    with open(env_file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()[:5]
        print("📄 .env 파일 내용 (첫 5줄):")
        for i, line in enumerate(lines, 1):
            if 'OPENAI_API_KEY' in line:
                # API 키는 일부만 표시
                parts = line.split('=')
                if len(parts) > 1:
                    key_part = parts[1].strip()
                    if len(key_part) > 10:
                        print(f"   {i}: OPENAI_API_KEY={key_part[:10]}...{key_part[-4:]}")
                    else:
                        print(f"   {i}: {line.strip()}")
                else:
                    print(f"   {i}: {line.strip()}")
            else:
                print(f"   {i}: {line.strip()}")
else:
    print(f"❌ .env 파일 없음: {env_file_path}")

print("\n🔄 dotenv 로딩...")
load_dotenv()

# 환경변수 확인
openai_key = os.getenv("OPENAI_API_KEY")
environment = os.getenv("ENVIRONMENT")
log_level = os.getenv("LOG_LEVEL")

print("\n📊 환경변수 상태:")
print(f"   ENVIRONMENT: {environment}")
print(f"   LOG_LEVEL: {log_level}")

if openai_key:
    if len(openai_key) > 10:
        print(f"   OPENAI_API_KEY: {openai_key[:10]}...{openai_key[-4:]} (길이: {len(openai_key)})")
    else:
        print(f"   OPENAI_API_KEY: {openai_key} (너무 짧음)")
    
    # API 키 형식 검증
    if openai_key.startswith('sk-'):
        print("   ✅ API 키 형식 올바름 (sk-로 시작)")
    else:
        print("   ❌ API 키 형식 잘못됨 (sk-로 시작하지 않음)")
        
    if len(openai_key) >= 50:
        print("   ✅ API 키 길이 적절함")
    else:
        print("   ❌ API 키 길이 부족함")
else:
    print("   ❌ OPENAI_API_KEY 없음")

print("\n🧪 Config 클래스 테스트...")
try:
    from app.core.config import settings
    print(f"   설정 로드 성공!")
    print(f"   ENVIRONMENT: {settings.ENVIRONMENT}")
    print(f"   LOG_LEVEL: {settings.LOG_LEVEL}")
    
    if settings.OPENAI_API_KEY:
        key = settings.OPENAI_API_KEY
        if len(key) > 10:
            print(f"   OPENAI_API_KEY: {key[:10]}...{key[-4:]} (길이: {len(key)})")
        else:
            print(f"   OPENAI_API_KEY: {key} (너무 짧음)")
    else:
        print("   ❌ OPENAI_API_KEY가 설정되지 않음")
        
except Exception as e:
    print(f"   ❌ Config 로드 실패: {e}")

print("\n🤖 OpenAI 클라이언트 테스트...")
try:
    from openai import OpenAI
    
    # 환경변수에서 직접 가져오기
    client = OpenAI(api_key=openai_key)
    print("   ✅ OpenAI 클라이언트 생성 성공")
    
    # 간단한 API 호출 테스트 (실제로는 호출하지 않음)
    print("   💡 실제 API 호출은 비용이 발생하므로 스킵합니다.")
    
except Exception as e:
    print(f"   ❌ OpenAI 클라이언트 생성 실패: {e}")

print("\n✨ 테스트 완료!")
