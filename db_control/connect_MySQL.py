import os, sys
from pathlib import Path
from dotenv import load_dotenv, find_dotenv
from sqlalchemy import create_engine, text

# --- .env を backend 直下から読む ---
base_path = Path(__file__).resolve().parents[1]   # .../0205_LinkFastNect_Backend-master
env_path = base_path / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path, override=True)
else:
    load_dotenv(find_dotenv(filename=".env", raise_error_if_not_found=True), override=True)

def must_get(k: str) -> str:
    v = os.getenv(k)
    if not v:
        print(f"[ENV ERROR] {k} が未設定です。.env を確認してください。", file=sys.stderr)
        sys.exit(1)
    return v

DB_HOST = must_get("DB_HOST")
DB_USER = must_get("DB_USER")
DB_PASSWORD = must_get("DB_PASSWORD")
DB_NAME = must_get("DB_NAME")
raw_port = os.getenv("DB_PORT", "").strip()

# --- ポートの正規化: 数字でなければ未指定扱い（=URLからポート節を外す or デフォルト3306） ---
DB_PORT = raw_port if raw_port.isdigit() else ""
port_part = f":{DB_PORT}" if DB_PORT else ""   # URLに埋める用

# SSL ルート証明書（backend 直下に置いた前提）
ssl_cert = str(base_path / "DigiCertGlobalRootG2.crt.pem")

# 接続URL（ポート未指定ならホスト名の直後に :◯◯ を付けない）
DATABASE_URL = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}{port_part}/{DB_NAME}?charset=utf8mb4"
)

print(f"[DEBUG] host={DB_HOST}, user={DB_USER}, db={DB_NAME}, port={DB_PORT or 'default(3306)'}")
engine = create_engine(
    DATABASE_URL,
    connect_args={"ssl": {"ssl_ca": ssl_cert}, "connect_timeout": 8},
    echo=True, pool_pre_ping=True, pool_recycle=3600
)

# 単純な疎通テスト
if __name__ == "__main__":
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("MySQL 接続OK")
    except Exception as e:
        print(f"接続エラー: {e}")
        sys.exit(1)
