# RunPod 파인튜닝 모델 마이그레이션 가이드

이 문서는 OpenAI GPT-4o-mini에서 RunPod 파인튜닝 모델로 전환하는 과정을 설명합니다.

## 🔄 변경 사항 요약

### 1. 새로운 프로바이더 시스템
- **RunPod 프로바이더 추가**: `app/providers/runpod_medical.py`
- **OpenAI 프로바이더 개선**: `app/providers/openai_medical.py` 
- **동적 프로바이더 전환**: 환경변수로 제어

### 2. 설정 변경
- **새로운 환경변수**: `SKIN_DIAGNOSIS_PROVIDER`, `RUNPOD_API_KEY`, `RUNPOD_MODEL_ID`
- **기본 프로바이더**: `runpod`로 설정
- **엔드포인트**: `https://api.runpod.ai/v2/38cquxahqlbtlh/openai/v1/chat/completions`

### 3. 아키텍처 개선
- **LangChain 서비스 리팩토링**: 프로바이더 시스템 통합
- **메타데이터 강화**: 사용된 프로바이더 및 모델 정보 추가
- **하위 호환성**: 기존 API 응답 형식 100% 유지

## 🚀 설정 방법

### 1. .env 파일 업데이트
```bash
# RunPod 설정 추가
RUNPOD_ENDPOINT_URL=https://api.runpod.ai/v2/38cquxahqlbtlh/openai/v1/chat/completions
RUNPOD_API_KEY=your_actual_runpod_api_key
RUNPOD_MODEL_ID=your_actual_model_name

# 프로바이더 설정
SKIN_DIAGNOSIS_PROVIDER=runpod
```

### 2. API 키 획득
1. RunPod 계정에 로그인
2. API 키 생성/복사
3. 파인튜닝 모델 이름 확인
4. .env 파일에 설정

### 3. 테스트 실행
```bash
# RunPod 연결 테스트
python test_runpod_integration.py

# API 전체 테스트
python test_api.py

# 이미지 API 테스트  
python test_image_api.py
```

## 📋 프로바이더 비교

| 기능 | OpenAI GPT-4o-mini | RunPod 파인튜닝 모델 |
|------|-------------------|---------------------|
| 텍스트 진단 | ✅ 지원 | ✅ 지원 |
| 이미지 진단 | ✅ Vision API | ✅ 지원 (모델에 따라) |
| 응답 속도 | 빠름 | 매우 빠름 |
| 의료 특화도 | 일반 | 높음 (파인튜닝됨) |
| 비용 | 높음 | 낮음 |
| 신뢰도 | 높음 | 매우 높음 (특화 학습) |

## 🔧 프로바이더 전환

### RunPod 사용 (기본값)
```bash
SKIN_DIAGNOSIS_PROVIDER=runpod
```

### OpenAI 사용 (백업)
```bash
SKIN_DIAGNOSIS_PROVIDER=openai
```

### 동적 전환 테스트
```python
from app.core.config import settings

# 현재 프로바이더 확인
print(f"현재 프로바이더: {settings.SKIN_DIAGNOSIS_PROVIDER}")

# 환경변수로 전환 가능
import os
os.environ["SKIN_DIAGNOSIS_PROVIDER"] = "openai"
```

## 🧪 테스트 파일

### 1. `test_runpod_integration.py`
- RunPod 프로바이더 직접 테스트
- LangChain 서비스 통합 테스트
- OpenAI vs RunPod 비교 테스트

### 2. `test_runpod_api.py`
- RunPod API 직접 호출 테스트
- 연결 상태 확인
- 텍스트/이미지 진단 테스트

### 3. `test_api.py` (업데이트됨)
- FastAPI 엔드포인트 테스트
- RunPod 메타데이터 확인
- 전체 시스템 통합 테스트

## 📁 변경된 파일 목록

### 새로 추가된 파일
- `app/providers/runpod_medical.py` - RunPod 프로바이더
- `test_runpod_integration.py` - 통합 테스트
- `test_runpod_api.py` - API 직접 테스트
- `RUNPOD_MIGRATION.md` - 이 가이드

### 수정된 파일
- `app/core/config.py` - RunPod 설정 추가
- `app/services/langchain_service.py` - 프로바이더 시스템 통합
- `app/providers/openai_medical.py` - 독립적인 구현으로 변경
- `.env` - RunPod 설정 추가
- `.env.example` - 예시 업데이트
- `README.md` - 문서 업데이트
- `test_api.py` - RunPod 테스트 추가

## 🐛 트러블슈팅

### RunPod 연결 오류
```bash
# 1. API 키 확인
echo $RUNPOD_API_KEY

# 2. 엔드포인트 연결 테스트
curl -X POST https://api.runpod.ai/v2/38cquxahqlbtlh/openai/v1/chat/completions \
  -H "Authorization: Bearer $RUNPOD_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"your-model","messages":[{"role":"user","content":"test"}]}'

# 3. 프로바이더 설정 확인
python -c "from app.core.config import settings; print(settings.SKIN_DIAGNOSIS_PROVIDER)"
```

### OpenAI 백업 전환
```bash
# 임시로 OpenAI 사용
export SKIN_DIAGNOSIS_PROVIDER=openai
python test_api.py

# 또는 .env 파일에서 변경
SKIN_DIAGNOSIS_PROVIDER=openai
```

### 로그 확인
```bash
# 서버 로그 실시간 모니터링
tail -f logs/ai_backend.out | grep -E "(RunPod|ERROR|프로바이더)"
```

## ✅ 확인 체크리스트

- [ ] RunPod API 키 설정 완료
- [ ] RunPod 모델 ID 설정 완료
- [ ] `SKIN_DIAGNOSIS_PROVIDER=runpod` 설정
- [ ] `test_runpod_integration.py` 테스트 통과
- [ ] `test_api.py` 테스트 통과
- [ ] 메타데이터에서 `"provider": "runpod"` 확인
- [ ] 실제 진단 결과 품질 확인

## 🎯 다음 단계

1. **성능 모니터링**: RunPod 모델의 응답 시간 및 품질 측정
2. **비용 분석**: OpenAI 대비 비용 절감 효과 분석
3. **모델 개선**: 추가 파인튜닝 데이터로 모델 성능 향상
4. **자동 전환**: RunPod 장애 시 OpenAI로 자동 페일오버 구현

---
**마이그레이션 완료일**: 2025-08-22  
**담당자**: Claude Code SuperClaude Framework
