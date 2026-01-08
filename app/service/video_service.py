import os
from fastapi import HTTPException, status
from fastapi.responses import FileResponse, StreamingResponse

VIDEO_PATH = "/Users/lyw/Desktop/video.mp4"

def get_video_size():
    if not os.path.exists(VIDEO_PATH):
        raise HTTPException(status_code=404, detail="Video not found")
    return os.path.getsize(VIDEO_PATH)

def get_video_download_response():
    if not os.path.exists(VIDEO_PATH):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        path=VIDEO_PATH,
        filename="downloaded_video.mp4", # 다운로드될 때의 파일명
        media_type="video/mp4"
    )

def get_video_stream_response(range_header: str | None):
    file_size = get_video_size()

    # Range 헤더에 따라 시작과 끝 바이트 계산 (기본값 1MB 청크)
    CHUNK_SIZE = 1024 * 1024  # 1MB
    start = 0
    end = min(CHUNK_SIZE, file_size - 1)

    if range_header:
        # 예: "bytes=0-" 또는 "bytes=1024-2048"
        try:
            range_value = range_header.replace("bytes=", "")
            parts = range_value.split("-")
            start = int(parts[0])
            if len(parts) > 1 and parts[1]:
                 end = int(parts[1])
            else:
                 end = min(start + CHUNK_SIZE, file_size - 1)
        except (ValueError, IndexError):
            raise HTTPException(status_code=400, detail="Invalid Range header")


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
