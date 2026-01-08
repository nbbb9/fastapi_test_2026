import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from dotenv import load_dotenv

load_dotenv()

# 1. 환경 변수에서 스키마 이름 가져오기 (없으면 test 기본값)
TARGET_SCHEMA = os.getenv("DB_SCHEMA", "test")

# 2. 데이터베이스 연결 정보
# SQLALCHEMY_DATABASE_URL = "postgresql://<사용자>:<비밀번호>@<호스트>:<포트>/<DB명>"
SQLALCHEMY_DATABASE_URL = "postgresql://myuser:mypassword@127.0.0.1:5432/mydb"

# 3. 엔진 생성
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={
        "options": f"-c search_path={TARGET_SCHEMA}"
    }
)

# 4. 세션 로컬 생성
# 실제 DB 세션을 생성해주는 공장(Factory) 역할입니다.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 5. Base 클래스 (ORM 모델 상속용, 필요시 사용)
Base = declarative_base()

# ---------------------------------------------------------
# 6. 프로시저 자동 로드 함수
# ---------------------------------------------------------
PROCEDURE_DIR = "app/db/procedures"  # SQL 파일들이 위치한 경로

def load_stored_procedures(db: Session):
    """
    서버 시작 시 지정된 폴더의 모든 프로시저(SQL)를 DB에 적용합니다.
    (파일별 독립 트랜잭션 적용)
    """
    if not os.path.exists(PROCEDURE_DIR):
        print(f"[알림] 프로시저 경로를 찾을 수 없음: {PROCEDURE_DIR}")
        return

    files = sorted([f for f in os.listdir(PROCEDURE_DIR) if f.endswith(".sql")])

    if not files:
        return

    print(f"--- 프로시저 동기화 시작 (총 {len(files)}개) ---")

    for filename in files:
        filepath = os.path.join(PROCEDURE_DIR, filename)
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                sql_content = f.read()

                if sql_content.strip():
                    db.execute(text(sql_content))
                    # 성공하면 즉시 반영 (다른 파일에 영향 안 줌)
                    db.commit()
                    print(f"[성공] {filename} 적용 완료")

        except Exception as e:
            # 실패 시 롤백하여 트랜잭션을 깨끗하게 비움
            db.rollback()
            print(f"[실패] {filename} 적용 중 에러 발생: {e}")
            # 여기서 롤백을 했으므로, 다음 파일은 정상적인 새 트랜잭션에서 실행됨

    print("--- 프로시저 동기화 완료 ---")