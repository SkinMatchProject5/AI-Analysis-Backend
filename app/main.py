from fastapi import FastAPI
from fastapi.responses import HTMLResponse, ORJSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from app.api.skin_diagnosis import router as skin_router
from app.core.config import settings
from app.api.utterance import router as utterance_router
from app.api.interpretation import router as interpretation_router
import logging

app = FastAPI(
    title="AI-Analysis-Backend",
    description="피부 진단, 증상 정제, 진단 해석을 위한 멀티 파이프라인 AI 백엔드",
    version="2.0.0",
    default_response_class=ORJSONResponse,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS 설정 - 프론트엔드 연결을 위해 필수
default_origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:5173",
    "http://localhost:8080",
    "http://localhost:4200",
    "http://127.0.0.1:3000",
    "https://your-frontend-domain.com",
]
extra_origins = [o.strip() for o in settings.ALLOWED_ORIGINS.split(",") if o.strip()]
allow_origins = list(dict.fromkeys(default_origins + extra_origins))

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# GZip 압축으로 응답 크기 최적화
app.add_middleware(GZipMiddleware, minimum_size=500)

# 기본 로깅 레벨 설정
logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))

app.include_router(skin_router, prefix="/api/v1")
app.include_router(utterance_router, prefix="/api/v1")
app.include_router(interpretation_router, prefix="/api/v1")

@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <html>
        <head>
            <title>AI-Analysis-Backend | 의료 AI 진단 서비스</title>
        </head>
        <body>
            <h1>AI-Analysis-Backend</h1>
            <p>피부 진단, 증상 정제, 진단 해석을 위한 멀티 파이프라인 AI 백엔드 서비스가 실행 중입니다.</p>
            <h2>지원 기능</h2>
            <ul>
                <li>피부 병변 진단 (15가지 질병)</li>
                <li>증상 문장 다듬기 (의료진 전달용)</li>
                <li>진단 결과 상세 해석</li>
            </ul>
            <ul>
                <li><a href="/docs">API 문서 (Swagger)</a></li>
                <li><a href="/redoc">API 문서 (ReDoc)</a></li>
            </ul>
        </body>
    </html>
    """

@app.get("/healthz")
async def healthz():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
