from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "info")
    # LLM 호출 파라미터(기본값은 현재 코드 동작 유지)
    REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", "30"))
    MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", "1000"))
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.3"))
    LLM_MAX_RETRIES: int = int(os.getenv("LLM_MAX_RETRIES", "2"))
    LLM_RETRY_BASE_DELAY: float = float(os.getenv("LLM_RETRY_BASE_DELAY", "0.5"))
    # CORS 추가 허용(콤마구분)
    ALLOWED_ORIGINS: str = os.getenv("ALLOWED_ORIGINS", "")

    # 파이프라인/프로바이더 설정
    SKIN_DIAGNOSIS_PROVIDER: str = os.getenv("SKIN_DIAGNOSIS_PROVIDER", "runpod")  # openai|runpod
    SKIN_DIAGNOSIS_IMAGE_PROVIDER: str = os.getenv("SKIN_DIAGNOSIS_IMAGE_PROVIDER", "runpod")  # 이미지 전용 프로바이더
    SYMPTOM_REFINER_PROVIDER: str = os.getenv("SYMPTOM_REFINER_PROVIDER", "openai")
    SYMPTOM_REFINER_MODEL: str = os.getenv("SYMPTOM_REFINER_MODEL", "gpt-4o-mini")

    INTERPRETATION_PROVIDER: str = os.getenv("INTERPRETATION_PROVIDER", "openai")  # openai|runpod
    INTERPRETATION_MODEL: str = os.getenv("INTERPRETATION_MODEL", "gpt-4o-mini")

    # RunPod 전용 설정 (간단한 방식)
    RUNPOD_API_KEY: str = os.getenv("RUNPOD_API_KEY", "")
    RUNPOD_BASE_URL: str = os.getenv("RUNPOD_BASE_URL", "")
    RUNPOD_MODEL_NAME: str = os.getenv("RUNPOD_MODEL_NAME", "")
    
    # 병원 백엔드 설정
    HOSPITAL_BACKEND_URL: str = os.getenv("HOSPITAL_BACKEND_URL", "http://localhost:8002")
    
    class Config:
        env_file = ".env"

settings = Settings()
