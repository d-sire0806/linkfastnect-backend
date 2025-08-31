import os
import sys
from pathlib import Path
from dotenv import load_dotenv, find_dotenv
from sqlalchemy import create_engine, Column, Integer, String, text
from sqlalchemy.orm import declarative_base, sessionmaker

# =========================
# 環境変数の読み込み
# =========================
base_path = Path(__file__).resolve().parents[1]  # backendディレクトリへのパス
env_path = base_path / ".env"

if env_path.exists():
    load_dotenv(dotenv_path=env_path, override=True)
else:
    # 念のため探索
    load_dotenv(find_dotenv(filename=".env", raise_error_if_not_found=True), override=True)

def must_get(key: str) -> str:
    v = os.getenv(key)
    if not v:
        print(f"[ENV ERROR] {key} が未設定です。.env を確認してください。", file=sys.stderr)
        sys.exit(1)
    return v

# =========================
# データベース接続情報
# =========================
DB_USER = must_get("DB_USER")
DB_PASSWORD = must_get("DB_PASSWORD")
DB_HOST = must_get("DB_HOST")   # 例: xxxx.mysql.database.azure.com
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = must_get("DB_NAME")

# =========================
# SSL証明書のパス
# =========================
ssl_cert = str(base_path / "DigiCertGlobalRootG2.crt.pem")  # ファイル名を確認

# =========================
# MySQLのURL構築
# =========================
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"

# =========================
# エンジンの作成（SSL設定を追加）
# =========================
engine = create_engine(
    DATABASE_URL,
    connect_args={"ssl": {"ssl_ca": ssl_cert}},
    echo=True,
    pool_pre_ping=True,
    pool_recycle=3600
)

# =========================
# Baseクラスとテーブル定義
# =========================
Base = declarative_base()

class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(String(50), unique=True, nullable=False)
    customer_name = Column(String(100), nullable=False)
    age = Column(Integer)
    gender = Column(String(10))

    def __repr__(self):
        return f"<Customer(customer_id='{self.customer_id}', name='{self.customer_name}')>"

# =========================
# テーブル作成
# =========================
Base.metadata.create_all(engine)

# =========================
# セッション作成 & テストデータ投入
# =========================
Session = sessionmaker(bind=engine)
session = Session()

def add_test_data():
    # 既存データ削除
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM customers"))
        connection.commit()

    test_customers = [
        Customer(customer_id="C1111", customer_name="ああ", age=6, gender="男"),
        Customer(customer_id="C110", customer_name="桃太郎", age=30, gender="女"),
    ]

    for customer in test_customers:
        session.add(customer)

    try:
        session.commit()
        print("テストデータを追加しました")
    except Exception as e:
        session.rollback()
        print(f"エラーが発生しました: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    # 環境変数が正しく読めているか確認用
    print(f"接続先: host={DB_HOST}, user={DB_USER}, db={DB_NAME}, port={DB_PORT}")
    add_test_data()
