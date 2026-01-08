import os

from fastapi import FastAPI, Header, HTTPException, status
from fastapi.responses import FileResponse, StreamingResponse
from contextlib import asynccontextmanager
from database import SessionLocal, load_stored_procedures

# 수명 주기(Lifespan) 관리
@asynccontextmanager
async def lifespan(app: FastAPI):
    # [시작 시 실행]
    db = SessionLocal()
    try:
        load_stored_procedures(db) # 여기서 프로시저 갱신
    finally:
        db.close()

    yield # 서버 실행 중...

    # [종료 시 실행] (필요 시 작성)

app = FastAPI(lifespan=lifespan)


VIDEO_PATH = "/Users/lyw/Desktop/video.mp4"

@app.get("/")
async def root():
    return {"message": "Hello World"}

def get_video_size():
    if not os.path.exists(VIDEO_PATH):
        raise HTTPException(status_code=404, detail="Video not found")
    return os.path.getsize(VIDEO_PATH)

# --- 1. 동영상 다운로드 API ---
@app.get("/download")
async def download_video():
    """
    동영상을 파일로 다운로드합니다.
    FileResponse를 사용하여 브라우저가 '저장'하도록 처리합니다.
    """
    if not os.path.exists(VIDEO_PATH):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        path=VIDEO_PATH,
        filename="downloaded_video.mp4", # 다운로드될 때의 파일명
        media_type="video/mp4"
    )


# --- 2. 동영상 스트리밍 API (Range Request 지원) ---
@app.get("/stream")
async def stream_video(range: str = Header(None)):
    """
    동영상을 스트리밍합니다.
    Range 헤더를 처리하여 동영상의 특정 구간 이동(Seek)을 지원합니다.
    """
    file_size = get_video_size()

    # Range 헤더에 따라 시작과 끝 바이트 계산 (기본값 1MB 청크)
    CHUNK_SIZE = 1024 * 1024  # 1MB
    start = 0
    end = min(CHUNK_SIZE, file_size - 1)

    if range:
        # 예: "bytes=0-" 또는 "bytes=1024-2048"
        try:
            start_str = range.replace("bytes=", "").split("-")[0]
            start = int(start_str)
            # 끝지점이 명시되지 않았다면 시작점 + 청크사이즈로 설정
            end = min(start + CHUNK_SIZE, file_size - 1)
        except ValueError:
            pass  # 파싱 실패 시 기본값 사용

    # 실제 읽어야 할 길이
    content_length = end - start + 1

    # 파일을 열고 해당 구간을 읽어서 반환하는 제너레이터
    def iterfile():
        with open(VIDEO_PATH, "rb") as video:
            video.seek(start)
            data = video.read(content_length)
            yield data

    # 206 Partial Content 응답 헤더 설정
    headers = {
        "Content-Range": f"bytes {start}-{end}/{file_size}",
        "Accept-Ranges": "bytes",
        "Content-Length": str(content_length),
        "Content-Type": "video/mp4",
    }

    return StreamingResponse(
        iterfile(),
        status_code=status.HTTP_206_PARTIAL_CONTENT,
        headers=headers
    )