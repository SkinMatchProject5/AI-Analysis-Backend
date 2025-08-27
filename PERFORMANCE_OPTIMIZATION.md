# AI-Analysis-Backend 성능 최적화 가이드

## 🚨 현재 문제: 응답 시간 2-3분

### 즉시 적용 가능한 해결책들

## 1. 타임아웃 및 모델 파라미터 최적화

### .env 파일 수정:
```env
# 기존
REQUEST_TIMEOUT=30
MAX_TOKENS=1000
TEMPERATURE=0.3

# 최적화
REQUEST_TIMEOUT=15          # 15초로 단축
MAX_TOKENS=500             # 토큰 수 절반으로 줄이기
TEMPERATURE=0.1            # 더 결정적인 응답
LLM_MAX_RETRIES=1          # 재시도 횟수 줄이기
LLM_RETRY_BASE_DELAY=0.2   # 재시도 지연시간 줄이기
```

## 2. RunPod 모델 최적화

### app/providers/runpod_medical.py 수정:
```python
# 현재 (느림)
optimized_llm = ChatOpenAI(
    api_key=self.api_key,
    base_url=self.base_url,
    model=settings.RUNPOD_MODEL_NAME,
    temperature=0.1,
    max_tokens=800,      # 너무 큼
    timeout=45,          # 너무 김
)

# 최적화 버전
optimized_llm = ChatOpenAI(
    api_key=self.api_key,
    base_url=self.base_url,
    model=settings.RUNPOD_MODEL_NAME,
    temperature=0.05,    # 더 결정적
    max_tokens=400,      # 절반으로 줄임
    timeout=20,          # 20초로 단축
)
```

## 3. 프로바이더 스위치 (임시 해결책)

### .env에서 OpenAI로 임시 변경:
```env
# RunPod이 너무 느릴 경우
SKIN_DIAGNOSIS_PROVIDER=openai
SKIN_DIAGNOSIS_IMAGE_PROVIDER=openai
```

## 4. 이미지 전처리 최적화

### app/core/image_utils.py에 추가할 함수:
```python
def optimize_image_for_analysis(image: UploadFile) -> str:
    """이미지를 AI 분석에 최적화"""
    # 이미지 크기를 512x512로 리사이징
    # JPEG 품질을 70%로 압축
    # Base64 크기 최소화
    pass
```

## 5. 캐싱 시스템 도입

### Redis 캐싱으로 중복 요청 방지:
```python
# 동일한 이미지/텍스트에 대한 결과 캐싱
# 30분간 캐시 유지
```

## 6. 비동기 처리 개선

### Background Tasks 사용:
```python
from fastapi import BackgroundTasks

@router.post("/diagnose/skin-lesion-async")
async def diagnose_async(
    request: SkinLesionRequest,
    background_tasks: BackgroundTasks
):
    # 즉시 작업 ID 반환
    # 백그라운드에서 실제 진단 수행
    # 별도 엔드포인트에서 결과 조회
```

## 📊 성능 목표

| 구분 | 현재 | 목표 |
|------|------|------|
| 텍스트 진단 | 2-3분 | 10-15초 |
| 이미지 진단 | 2-3분 | 20-30초 |
| 성공률 | 불명 | 95%+ |

## 🔧 단계별 적용 순서

### Phase 1: 즉시 적용 (5분)
1. `.env` 파일 타임아웃 값들 수정
2. 프로바이더를 OpenAI로 임시 변경
3. 서버 재시작 후 테스트

### Phase 2: 코드 최적화 (30분)
1. RunPod 프로바이더 파라미터 최적화
2. 이미지 전처리 로직 추가
3. 에러 핸들링 개선

### Phase 3: 아키텍처 개선 (1-2시간)
1. 캐싱 시스템 도입
2. 비동기 처리 개선
3. 성능 모니터링 추가

## ⚡ 긴급 해결책 (지금 당장)

1. **프로바이더 변경**:
   ```env
   SKIN_DIAGNOSIS_PROVIDER=openai
   SKIN_DIAGNOSIS_IMAGE_PROVIDER=openai
   ```

2. **타임아웃 단축**:
   ```env
   REQUEST_TIMEOUT=15
   MAX_TOKENS=400
   ```

3. **서버 재시작**:
   ```bash
   # 현재 서버 종료 후 재시작
   python app/main.py
   ```

이 변경사항들로 2-3분 → 10-20초로 단축 가능합니다.
