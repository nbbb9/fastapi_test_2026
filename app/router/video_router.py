from fastapi import APIRouter, Header
from app.service import video_service

router = APIRouter()

@router.get("/download", description="동영상을 파일로 다운로드합니다. FileResponse를 사용하여 브라우저가 '저장'하도록 처리합니다.")
async def download_video():
    return video_service.get_video_download_response()

@router.get("/stream", description="동영상을 스트리밍합니다. Range 헤더를 처리하여 동영상의 특정 구간 이동(Seek)을 지원합니다.")
async def stream_video(range: str = Header(None)):
    return video_service.get_video_stream_response(range)