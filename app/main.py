from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from app.api.skin_diagnosis import router as skin_router
from app.core.config import settings

app = FastAPI(
    title="LangChain OpenAI API Pipeline",
    description="FastAPI + OpenAI API + LangChain 파이프라인",
    version="1.0.0"
)

# CORS 설정 - 프론트엔드 연결을 위해 필수
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",    # React 기본 포트
        "http://localhost:3001",    # React 대체 포트
        "http://localhost:5173",    # Vite 기본 포트
        "http://localhost:8080",    # Vue 기본 포트
        "http://localhost:4200",    # Angular 기본 포트
        "http://127.0.0.1:3000",    # 로컬호스트 대체
        "https://your-frontend-domain.com",  # 프로덕션 도메인
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(skin_router, prefix="/api/v1")

@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <html>
        <head>
            <title>LangChain OpenAI API Pipeline</title>
        </head>
        <body>
            <h1>LangChain OpenAI API Pipeline</h1>
            <p>FastAPI + OpenAI API + LangChain 서비스가 실행 중입니다.</p>
            <ul>
                <li><a href="/docs">API 문서 (Swagger)</a></li>
                <li><a href="/redoc">API 문서 (ReDoc)</a></li>
            </ul>
        </body>
    </html>
    """

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)