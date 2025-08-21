# AI-Analysis-Backend

**FastAPI + OpenAI + LangChain 통합 의료 진단 플랫폼**

피부 병변 진단, 증상 정제, 진단 해석을 위한 멀티 파이프라인 AI 백엔드 서비스입니다.

## 🚀 Quick Start

### 1. 환경 설정

```bash
# 가상환경 생성
python -m venv venv

# 가상환경 활성화
source venv/bin/activate  # macOS/Linux
# 또는 venv\Scripts\activate  # Windows

# 의존성 설치
pip install -r requirements.txt
```

### 2. 환경변수 설정

```bash
# .env 파일 생성
cp .env.example .env

# .env 파일 편집하여 OpenAI API 키 설정
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. 서버 실행

```bash
# 개발 서버 실행
uvicorn app.main:app --reload

# 또는
python -m app.main
```

### 4. API 확인

- 홈페이지: http://localhost:8001/
- API 문서: http://localhost:8001/docs
- ReDoc: http://localhost:8001/redoc

## 📋 주요 기능

### 🏥 3개 독립 파이프라인

#### 1. 피부 병변 진단 (Skin Diagnosis)
- **이미지 진단**: OpenAI Vision API 기반 실시간 이미지 분석
- **텍스트 진단**: 병변 설명을 통한 진단
- **15가지 질병 분류**: 
  ```
  광선각화증, 기저세포암, 멜라닌세포모반, 보웬병, 비립종, 
  사마귀, 악성흑색종, 지루각화증, 편평세포암, 표피낭종, 
  피부섬유종, 피지샘증식증, 혈관종, 화농 육아종, 흑색점
  ```
- **구조화된 진단**: XML 파싱으로 신뢰도 점수 및 유사 질병 제공

#### 2. 증상 문장 다듬기 (Utterance Refine)
- **의료진 전달용 문장 변환**: 환자 원문 → 의사 소통용 문장
- **다국어 지원**: 한국어, 영어 등
- **스타일 태그**: doctor-visit 형태로 정제

#### 3. 진단 해석 (Interpretation)
- **상세 설명**: 진단 결과에 대한 추가 해석
- **환자 이해도 향상**: 복잡한 의료 용어 쉽게 설명

### ✨ 기술적 특징
- **멀티 프로바이더**: OpenAI/RunPod 동적 전환 지원
- **별도 파이프라인**: 각 기능별 독립적인 처리 흐름
- **이미지 최적화**: 자동 리사이징, 압축, base64 인코딩
- **CRUD API**: 분석 결과의 완전한 생명주기 관리
- **다중 응답 형식**: JSON/XML 형식 지원
- **프론트엔드 호환**: 기존 API 응답 형태 100% 유지

### 🛠 기술 스택
- **FastAPI 0.104+**: 고성능 async 웹 프레임워크 (포트 8001)
- **LangChain 0.0.340+**: LLM 오케스트레이션 및 프롬프트 관리
- **OpenAI GPT-4o-mini**: Vision API 지원 멀티모달 모델
- **Pydantic 2.5+**: 데이터 검증 및 직렬화
- **Pillow 10.1+**: 이미지 처리, 리사이징, 압축
- **ORJSON**: 고성능 JSON 직렬화
- **Uvicorn**: ASGI 서버
- **CORS**: 프론트엔드 완전 호환

## 🔌 API 엔드포인트

### 🏥 피부 병변 진단 API

#### 이미지 기반 진단
```bash
POST /api/v1/diagnose/skin-lesion-image
Content-Type: multipart/form-data

파라미터:
- image: 이미지 파일 (JPEG, PNG, WebP, 최대 10MB)
- additional_info: 환자 정보 (선택사항)
- questionnaire_data: 설문조사 JSON 데이터 (선택사항)
- response_format: json | xml (기본값: json)
```

#### 텍스트 기반 진단
```bash
POST /api/v1/diagnose/skin-lesion
Content-Type: application/json

{
    "lesion_description": "팔에 있는 갈색 반점이 커지고 있습니다",
    "additional_info": "50세 남성, 야외활동 많음",
    "response_format": "json"
}
```

**진단 응답 예시:**
```json
{
    "id": "skin_diagnosis_abc123",
    "diagnosis": "기저세포암",
    "confidence_score": 0.85,
    "recommendations": "즉시 피부과 전문의 상담을 받으시기 바랍니다.",
    "similar_conditions": "광선각화증, 멜라닌세포모반",
    "metadata": {
        "model": "gpt-4o-mini",
        "analysis_type": "skin_lesion_image_diagnosis",
        "image_analyzed": true
    },
    "created_at": "2025-08-21T10:00:00"
}
```

### 📝 증상 문장 다듬기 API

```bash
POST /api/v1/utterance/refine
Content-Type: application/json

{
    "text": "팔 접히는 부분에 붉고 따갑고 간지러워요. 긁다 보니 피가 났어요.",
    "language": "ko"
}
```

**응답 예시:**
```json
{
    "refined_text": "팔 안쪽 주름 부위에 붉고 따가운 가려움이 있습니다. 긁은 후 출혈이 있었습니다.",
    "style": "doctor-visit",
    "model": "gpt-4o-mini",
    "created_at": "2025-08-21T10:00:00"
}
```

### 🔍 진단 해석 API

```bash
POST /api/v1/interpretation/explain
Content-Type: application/json

{
    "diagnosis_result": "기저세포암 의심",
    "additional_context": "환자 연령: 65세"
}
```

### 📊 분석 결과 관리 API

```bash
# 전체 목록 조회 (페이징)
GET /api/v1/analyses?page=1&page_size=10&response_format=json

# 특정 분석 조회
GET /api/v1/analyses/{analysis_id}?response_format=json

# 검색
GET /api/v1/analyses/search?query=기저세포암&response_format=json

# 분석 수정
PUT /api/v1/analyses/{analysis_id}
{
    "prompt": "수정된 프롬프트",
    "result": "수정된 결과"
}

# 분석 삭제
DELETE /api/v1/analyses/{analysis_id}

# 커스텀 분석
POST /api/v1/analyze/custom?prompt=질문&system_message=시스템메시지
```

## 🧪 테스트

```bash
# 일반 API 테스트
python test_api.py

# 이미지 진단 API 테스트
python test_image_api.py
```

### Postman 테스트 가이드
1. **POST** `http://localhost:8001/api/v1/diagnose/skin-lesion-image`
2. **Body** → **form-data** 선택
3. **Key 설정**:
   - `image` (Type: File) → 이미지 파일 선택
   - `additional_info` (Type: Text) → "50세 남성, 야외활동 많음"
   - `response_format` (Type: Text) → "json" 또는 "xml"
4. **Send** 클릭

## 📁 프로젝트 구조

```
AI-Analysis-Backend-main/
├── app/
│   ├── main.py                    # FastAPI 앱 (포트 8001)
│   ├── api/                       # API 라우터
│   │   ├── skin_diagnosis.py      # 피부 진단 API (메인)
│   │   ├── utterance.py           # 증상 문장 다듬기 API
│   │   └── interpretation.py      # 진단 해석 API
│   ├── core/                      # 핵심 설정 및 유틸리티
│   │   ├── config.py              # 환경 변수 및 설정
│   │   ├── image_utils.py         # 이미지 처리 (리사이징, 압축)
│   │   ├── xml_utils.py           # XML 변환 유틸리티
│   │   └── diagnosis_parser.py    # 진단 결과 파싱
│   ├── models/
│   │   └── schemas.py             # Pydantic 데이터 모델
│   ├── services/                  # 비즈니스 로직
│   │   ├── langchain_service.py   # 핵심 LangChain 서비스
│   │   ├── refiner_service.py     # 텍스트 정제 서비스
│   │   ├── interpretation_service.py # 진단 해석 서비스
│   │   ├── analysis_store.py      # 인메모리 저장소
│   │   └── result_parser.py       # 결과 파싱 로직
│   └── providers/                 # AI 프로바이더 추상화
│       ├── base.py                # 기본 프로바이더 인터페이스
│       ├── openai_medical.py      # OpenAI 의료 진단
│       ├── openai_text.py         # OpenAI 텍스트 처리
│       └── runpod_medical.py      # RunPod 대안 (미래 대비)
├── logs/                          # 로그 파일
├── venv/                          # Python 가상환경
├── requirements.txt               # Python 의존성
├── test_api.py                    # 일반 API 테스트
├── test_image_api.py              # 이미지 API 테스트
├── CLAUDE.md                      # Claude Code 작업 가이드
└── README.md                      # 프로젝트 문서
```

## 🔧 설정

### 필수 환경변수
```bash
# OpenAI 설정 (필수)
OPENAI_API_KEY=your_openai_api_key_here

# 서버 설정
ENVIRONMENT=development
LOG_LEVEL=info
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173

# LLM 호출 파라미터
REQUEST_TIMEOUT=30
MAX_TOKENS=1000
TEMPERATURE=0.3
LLM_MAX_RETRIES=2
LLM_RETRY_BASE_DELAY=0.5

# 프로바이더 설정
SYMPTOM_REFINER_PROVIDER=openai
SYMPTOM_REFINER_MODEL=gpt-4o-mini
INTERPRETATION_PROVIDER=openai
INTERPRETATION_MODEL=gpt-4o-mini

# RunPod 설정 (선택사항, 미래 대비)
RUNPOD_ENDPOINT_URL=
RUNPOD_API_KEY=
RUNPOD_MODEL_ID=
```

### 이미지 처리 설정
- **지원 형식**: JPEG, PNG, WebP
- **최대 파일 크기**: 10MB
- **자동 리사이징**: 1024x1024 최대
- **JPEG 품질**: 85% (최적화)

## 📝 개발 가이드

### 새로운 파이프라인 추가
1. **프로바이더 생성**: `app/providers/`에 새 프로바이더 클래스
2. **서비스 레이어**: `app/services/`에 비즈니스 로직 서비스
3. **스키마 정의**: `app/models/schemas.py`에 Pydantic 모델
4. **API 엔드포인트**: `app/api/`에 새 라우터 파일
5. **메인 앱 등록**: `app/main.py`에 라우터 추가

### 프로바이더 시스템 활용
```python
# 새 프로바이더 생성 예시
from app.providers.base import BaseProvider

class CustomProvider(BaseProvider):
    async def analyze(self, prompt: str) -> str:
        # 커스텀 분석 로직
        pass
```

### 멀티 프로바이더 전환
- 환경 변수로 프로바이더 선택
- OpenAI ↔ RunPod 동적 전환 지원
- 프로바이더별 설정 분리

### 데이터베이스 통합 계획
현재: 인메모리 저장소 (`analysis_store.py`)
향후: PostgreSQL, MongoDB 등 영구 저장소로 교체 예정

## 🚨 주의사항

### 보안 및 개인정보
- ⚠️ **의료 정보 취급**: 환자 개인정보 보호 필수
- ⚠️ **API 키 보안**: OpenAI API 키 노출 금지
- ⚠️ **HTTPS 사용**: 프로덕션에서 반드시 HTTPS 적용

### 비용 및 성능
- 💰 **API 비용**: OpenAI Vision API 사용량에 따른 과금
- 🔄 **재시도 로직**: 네트워크 오류 시 자동 재시도 (최대 2회)
- 💾 **인메모리 저장**: 서버 재시작 시 분석 데이터 소실

### 의료 면책
- 🩺 **진단 참고용**: AI 진단은 참고용이며 최종 진단은 의료진과 상담
- 📋 **면책 문구**: 모든 진단 결과에 면책 조항 포함

## 🔗 연동 시스템

### 프론트엔드 연동
- **SkinMatch Frontend**: React 기반 UI
- **CORS 완전 지원**: 개발/프로덕션 환경 모두 대응
- **기존 API 호환**: 100% 하위 호환성 보장

### 향후 확장 계획
- **Hospital Recommendation**: 진단 결과 기반 병원 추천
- **RAG Integration**: 의료 지식 베이스 연동
- **Vector Database**: Qdrant를 통한 의미 검색

## 📞 지원 및 트러블슈팅

### 일반적인 문제 해결
1. **OpenAI API 키 확인**
   ```bash
   echo $OPENAI_API_KEY  # 키가 설정되었는지 확인
   ```

2. **네트워크 연결 확인**
   ```bash
   curl -I https://api.openai.com  # OpenAI API 접근 가능한지 확인
   ```

3. **로그 확인**
   ```bash
   tail -f logs/server.log  # 실시간 로그 확인
   ```

4. **API 크레딧 확인**: OpenAI 대시보드에서 사용량 모니터링

### 성능 최적화
- **이미지 압축**: 업로드 전 이미지 크기 최적화
- **배치 처리**: 여러 진단 요청 시 배치로 처리
- **캐싱**: 동일한 이미지/텍스트 재진단 방지

## 📄 라이선스

MIT License

---
**Last Updated**: 2025-08-21 by Claude Code SuperClaude Framework
