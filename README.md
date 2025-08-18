# FastAPI + OpenAI Vision API + LangChain Pipeline

FastAPI, OpenAI Vision API, LangChain을 활용한 이미지 기반 피부 병변 진단 API 서비스입니다.

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

### ✨ 핵심 기능
- **이미지 진단**: OpenAI Vision API를 활용한 피부 병변 이미지 분석
- **텍스트 진단**: 병변 설명을 바탕으로 한 진단
- **15가지 질병 분류**: 광선각화증, 기저세포암, 멜라닌세포모반 등
- **구조화된 진단**: XML 형식의 체계적인 진단 결과
- **CRUD API**: 분석 결과의 생성, 조회, 수정, 삭제
- **다중 응답 형식**: JSON 및 XML 형식 지원
- **이미지 최적화**: 자동 리사이징 및 압축

### 🛠 기술 스택
- **FastAPI**: 고성능 웹 프레임워크
- **LangChain**: LLM 오케스트레이션
- **OpenAI GPT-4o-mini**: Vision API 지원 모델
- **Pillow**: 이미지 처리 및 최적화
- **Pydantic**: 데이터 검증
- **Uvicorn**: ASGI 서버

## 🔌 API 엔드포인트

### 이미지 기반 피부 병변 진단
```bash
POST /api/v1/diagnose/skin-lesion-image
Content-Type: multipart/form-data

- image: 이미지 파일 (JPEG, PNG, WebP)
- additional_info: 환자 정보 (선택사항)
- response_format: json 또는 xml
```

### 텍스트 기반 피부 병변 진단
```bash
POST /api/v1/diagnose/skin-lesion
Content-Type: application/json

{
    "lesion_description": "병변 설명",
    "additional_info": "추가 정보 (선택사항)",
    "response_format": "json"  # 또는 "xml"
}
```

### 일반 분석
```bash
POST /api/v1/analyze
Content-Type: application/json

{
    "prompt": "분석할 텍스트",
    "context": "추가 컨텍스트 (선택사항)",
    "response_format": "json"  # 또는 "xml"
}
```

### 분석 조회
```bash
# 전체 목록
GET /api/v1/analyses?page=1&page_size=10&response_format=json

# 특정 분석
GET /api/v1/analyses/{analysis_id}?response_format=json

# 검색
GET /api/v1/analyses/search?query=검색어&response_format=json
```

### 분석 수정
```bash
PUT /api/v1/analyses/{analysis_id}
Content-Type: application/json

{
    "prompt": "수정된 프롬프트",
    "result": "수정된 결과"
}
```

### 분석 삭제
```bash
DELETE /api/v1/analyses/{analysis_id}
```

### 커스텀 분석
```bash
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
langchain/
├── app/
│   ├── main.py                 # FastAPI 앱
│   ├── api/
│   │   └── routes.py          # API 라우터
│   ├── core/
│   │   ├── config.py          # 설정
│   │   └── xml_utils.py       # XML 유틸리티
│   ├── models/
│   │   └── schemas.py         # 데이터 모델
│   └── services/
│       ├── langchain_service.py # LangChain 서비스
│       └── analysis_store.py   # 저장소
├── requirements.txt            # 의존성
├── .env.example               # 환경변수 예시
├── test_api.py               # 테스트 스크립트
└── README.md                 # 프로젝트 문서
```

## 🔧 설정

### 환경변수
- `OPENAI_API_KEY`: OpenAI API 키 (필수)
- `ENVIRONMENT`: 실행 환경 (development/production)
- `LOG_LEVEL`: 로그 레벨 (info/debug/warning/error)

## 📝 개발 가이드

### 새로운 분석 타입 추가
1. `services/langchain_service.py`에 새 메서드 추가
2. `models/schemas.py`에 모델 정의
3. `api/routes.py`에 엔드포인트 추가

### 데이터베이스 통합
현재는 인메모리 저장소를 사용하고 있습니다. 프로덕션 환경에서는 PostgreSQL, MongoDB 등으로 교체하세요.

## 🚨 주의사항

- OpenAI API 키가 필요합니다
- API 사용량에 따른 비용이 발생할 수 있습니다
- 현재 버전은 인메모리 저장소를 사용하므로 서버 재시작 시 데이터가 사라집니다

## 📞 지원

문제가 발생하면 다음을 확인해주세요:
1. OpenAI API 키가 올바르게 설정되었는지
2. 인터넷 연결이 안정적인지
3. API 크레딧이 충분한지

## 📄 라이선스

MIT License
