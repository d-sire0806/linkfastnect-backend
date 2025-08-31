import os, sys
from pathlib import Path
from dotenv import load_dotenv, find_dotenv
from sqlalchemy import create_engine

# --- .env はローカル用。App Service 本番は環境変数で上書き ---
base_path = Path(__file__).resolve().parents[1]   # backend 直下
env_path = base_path / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path, override=False)  # 本番の AppSettings を優先したいので override=False
else:
    load_dotenv(find_dotenv(filename=".env"), override=False)

def must_get(k: str) -> str:
    v = os.getenv(k)
    if not v:
        print(f"[ENV ERROR] {k} 未設定", file=sys.stderr); sys.exit(1)
    return v

DB_HOST = must_get("DB_HOST")
DB_USER = must_get("DB_USER")
DB_PASSWORD = must_get("DB_PASSWORD")
DB_NAME = must_get("DB_NAME")
DB_PORT = os.getenv("DB_PORT", "3306")

# --- 証明書の場所を複数パスで探す ---
candidate_paths = [
    base_path / "DigiCertGlobalRootG2.crt.pem",                 # backend直下
    Path(__file__).resolve().parent / "DigiCertGlobalRootG2.crt.pem",  # db_control直下
    base_path / "db_control" / "DigiCertGlobalRootG2.crt.pem",  # 念のため
]
ssl_cert = None
for p in candidate_paths:
    if p.exists():
        ssl_cert = str(p); break

if not ssl_cert:
    # 見つからない場合はログに出して接続は試みる（Azure は証明書必須設定だと失敗します）
    print("[WARN] CA証明書ファイルが見つかりませんでした。SSLなしで接続を試みます。", file=sys.stderr)

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"

connect_args = {"connect_timeout": 10}
if ssl_cert:
    connect_args["ssl"] = {"ssl_ca": ssl_cert}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False,
)
