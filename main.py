from fastapi import FastAPI
from contextlib import asynccontextmanager
from database import SessionLocal, load_stored_procedures
from router import video_router

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

app.include_router(video_router.router, prefix="/video")