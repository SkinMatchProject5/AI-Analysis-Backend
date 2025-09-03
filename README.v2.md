# AI-Analysis-Backend

피부 병변 이미지 기반 진단, 증상 문장 분해, 결과 해석을 제공하는 FastAPI 백엔드입니다. OpenAI/Runpod 등 LLM·Vision 서비스를 활용하며, 병원 검색/챗봇 백엔드와 비동기 연동합니다.

## 요구사항
- Python 3.12+
- pip / virtualenv (또는 Docker)

## 빠른 시작
- 로컬 실행
```bash
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```
- Docker
```bash
docker build -t skinmatch/ai-analysis-backend:latest .
docker run -p 8001:8001 skinmatch/ai-analysis-backend:latest
# 또는
docker compose up -d
```

## 환경 변수(예시)
- LOG_LEVEL=info
- ALLOWED_ORIGINS (선택)
- OpenAI/Runpod 관련 키는 서비스 구성에 따름 (예: `OPENAI_API_KEY`, `RUNPOD_API_KEY` 등)

## API 개요
- Base URL: `http://localhost:8001`
- 문서: `/docs`, `/redoc`

- v1 진단 (`/api/v1/diagnose`)
  - POST `/skin-lesion-image`: 이미지 업로드 기반 진단
    - Form: `image`(file), `additional_info`(str?), `questionnaire_data`(JSON str?), `response_format`(json|xml)
    - Response: `SkinDiagnosisResponse`

- v1 기타
  - `/api/v1/utterance/*`: 증상 문장 처리
  - `/api/v1/interpretation/*`: 진단 결과 해석/정리

연동
- 병원 검색: 결과를 Hospital-Location-Backend로 전달하여 병원 후보를 조회
- 챗봇: 결과를 Chatbot-Backend로 전달해 상담 세션에 반영

## 디렉터리 구조
- `app/main.py`: FastAPI 진입점, CORS/GZip/라우터 설정
- `app/api/skin_diagnosis.py`: 이미지 진단 API
- `app/api/utterance.py`, `app/api/interpretation.py`: 텍스트 처리/해석
- `app/services/*`: LLM 연동, 결과 저장, 병원/챗봇 연계
- `app/core/*`: 이미지/결과 파서 유틸, 설정

