# AI-Analysis-Backend 테스트 파일 정리

## 📁 폴더 구조
- `tests/core/` - 핵심 기능 테스트
- `tests/runpod/` - RunPod 관련 테스트
- `tests/api/` - API 엔드포인트 테스트
- `tests/utils/` - 유틸리티 및 디버깅 도구

## 🚀 주요 테스트 실행 방법

### 전체 시스템 테스트
```bash
python tests/core/test_full_system.py
```

### RunPod 모델 테스트
```bash
python tests/runpod/test_runpod_integration.py
```

### API 테스트
```bash
python tests/api/test_skin_diagnosis_api.py
```

### 개발 도구
```bash
python tests/utils/check_runpod_status.py
python tests/utils/debug_diagnosis.py
```

## 🗑️ 정리된 파일들 (2024-08-23)
기존 루트에 있던 16개의 테스트 파일들을 용도별로 분류하여 정리함.
