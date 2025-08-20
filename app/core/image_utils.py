import base64
import io
from PIL import Image
from fastapi import UploadFile, HTTPException

def encode_image_to_base64(image_file: UploadFile) -> str:
    """이미지 파일을 base64로 인코딩"""
    try:
        # 파일 내용 읽기
        image_data = image_file.file.read()
        
        # PIL로 이미지 검증 및 최적화
        image = Image.open(io.BytesIO(image_data))
        
        # 이미지 크기 제한 (OpenAI 권장)
        max_size = (1024, 1024)
        if image.size[0] > max_size[0] or image.size[1] > max_size[1]:
            image.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        # RGB 변환 (RGBA나 다른 모드인 경우)
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # 최적화된 이미지를 바이트로 변환
        buffer = io.BytesIO()
        image.save(buffer, format='JPEG', quality=85, optimize=True)
        buffer.seek(0)
        
        # base64 인코딩
        encoded_string = base64.b64encode(buffer.getvalue()).decode('utf-8')
        return encoded_string
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"이미지 처리 중 오류가 발생했습니다: {str(e)}")

def validate_image_file(file: UploadFile) -> bool:
    """이미지 파일 유효성 검사"""
    # 허용된 MIME 타입
    allowed_types = [
        'image/jpeg', 
        'image/jpg', 
        'image/png', 
        'image/webp'
    ]
    
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400, 
            detail=f"지원하지 않는 파일 형식입니다. 지원 형식: {', '.join(allowed_types)}"
        )
    
    # 파일 크기 제한 (10MB)
    if file.size and file.size > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="파일 크기는 10MB 이하여야 합니다.")
    
    return True

def get_image_info(image_file: UploadFile) -> dict:
    """이미지 정보 추출"""
    try:
        image_data = image_file.file.read()
        image = Image.open(io.BytesIO(image_data))
        
        # 파일 포인터 리셋
        image_file.file.seek(0)
        
        return {
            "filename": image_file.filename,
            "content_type": image_file.content_type,
            "size": image_file.size,
            "dimensions": image.size,
            "mode": image.mode,
            "format": image.format
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"이미지 정보 추출 실패: {str(e)}")
