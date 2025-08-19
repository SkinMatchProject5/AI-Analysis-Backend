# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

FastAPI + OpenAI API + LangChain 파이프라인 프로젝트입니다. 피부 병변 진단에 특화된 AI 기반 API 서비스를 제공합니다.

## Architecture

### Core Components
- **FastAPI**: REST API 프레임워크
- **LangChain**: OpenAI API 추상화 및 프롬프트 관리
- **GPT-4o-mini**: 피부 병변 진단 전용 모델
- **In-Memory Store**: 분석 결과 저장 (개발용)

### Directory Structure
```
app/
├── main.py              # FastAPI 앱 진입점
├── api/
│   ├── routes.py        # 일반 API 엔드포인트
│   └── skin_diagnosis.py # 피부 병변 진단 전용 API
├── core/
│   ├── config.py        # 설정 관리
│   └── xml_utils.py     # XML 변환 유틸리티
├── models/
│   └── schemas.py       # Pydantic 모델 (SkinLesionRequest 포함)
└── services/
    ├── langchain_service.py  # LangChain 통합 (GPT-4o-mini)
    └── analysis_store.py     # 데이터 저장소
```

## Development Commands

### Environment Setup
```bash
# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # macOS/Linux
# 또는 venv\Scripts\activate  # Windows

# 의존성 설치
pip install -r requirements.txt

# 환경변수 설정
cp .env.example .env
# .env 파일에서 OPENAI_API_KEY 설정
```

### Run Development Server
```bash
# 메인 디렉토리에서 실행
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 또는 Python으로 직접 실행
python -m app.main
```

### API Testing
```bash
# 서버 실행 후 접속 가능한 URL들:
# - http://localhost:8000/          # 홈페이지
# - http://localhost:8000/docs      # Swagger UI
# - http://localhost:8000/redoc     # ReDoc
```

## API Endpoints

### Skin Lesion Diagnosis APIs
- `POST /api/v1/diagnose/skin-lesion` - 텍스트 기반 피부 병변 진단
- `POST /api/v1/diagnose/skin-lesion-image` - 이미지 기반 피부 병변 진단 (Vision API)

### Core Analysis APIs
- `POST /api/v1/analyze` - 일반 텍스트 분석
- `GET /api/v1/analyses` - 분석 결과 목록 조회 (페이징)
- `GET /api/v1/analyses/{id}` - 특정 분석 결과 조회
- `PUT /api/v1/analyses/{id}` - 분석 결과 수정
- `DELETE /api/v1/analyses/{id}` - 분석 결과 삭제
- `GET /api/v1/analyses/search` - 분석 결과 검색
- `POST /api/v1/analyze/custom` - 커스텀 프롬프트 분석

### Response Formats
모든 엔드포인트는 `response_format` 쿼리 파라미터로 JSON 또는 XML 응답을 지원합니다.

## Key Features

### Skin Lesion Diagnosis
- **텍스트 진단**: 병변 설명을 바탕으로 진단
- **이미지 진단**: OpenAI Vision API로 실제 이미지 분석
- GPT-4o-mini 모델 사용
- 15가지 피부 병변 분류 (광선각화증, 기저세포암, 멜라닌세포모반 등)
- 구조화된 XML 진단 결과
- 진단 점수 및 유사 질병 제공
- 이미지 전처리 및 최적화 (리사이징, 압축)

### LangChain Integration
- `ChatOpenAI` 모델 사용 (gpt-4o-mini)
- 전문적인 피부 병변 진단 프롬프트
- 비동기 처리 지원

### Response Format Support
- JSON: 기본 응답 형식
- XML: `response_format=xml` 파라미터로 활성화

### CRUD Operations
- Create: 새로운 분석 생성
- Read: 분석 결과 조회 및 검색
- Update: 기존 분석 수정
- Delete: 분석 삭제

## Configuration

### Environment Variables
- `OPENAI_API_KEY`: OpenAI API 키 (필수)
- `ENVIRONMENT`: 실행 환경 (기본값: development)
- `LOG_LEVEL`: 로그 레벨 (기본값: info)

### OpenAI API Setup
1. OpenAI 계정에서 API 키 발급
2. `.env` 파일에 `OPENAI_API_KEY` 설정
3. 충분한 API 크레딧 확인

## Development Notes

### Adding New Analysis Types
1. `langchain_service.py`에 새로운 분석 메서드 추가
2. `schemas.py`에 필요한 모델 정의
3. `skin_diagnosis.py`에 새로운 엔드포인트 추가 (피부 진단용)
4. `routes.py`에 일반 분석 엔드포인트 추가

### Image Processing
- 지원 형식: JPEG, PNG, WebP
- 자동 리사이징: 최대 1024x1024
- 품질 최적화: JPEG 85% 품질
- 파일 크기 제한: 10MB

### Database Integration
현재 인메모리 저장소 사용 중. 프로덕션에서는 PostgreSQL, MongoDB 등 실제 데이터베이스로 교체 필요.

### Error Handling
- 모든 API는 적절한 HTTP 상태 코드 반환
- OpenAI API 오류는 500 에러로 래핑
- 상세한 에러 메시지 제공