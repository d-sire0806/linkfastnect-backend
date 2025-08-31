# db_control/crud.py  --- SQLAlchemy 2.x 対応版（idが無いモデルでも動く）
import json
from typing import List
from sqlalchemy import select, update, delete
from sqlalchemy.orm import sessionmaker

from db_control.connect_MySQL import engine

# ここは your モデル名に合わせて
from db_control.mymodels import Customers

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

def _rows_to_json(rows: List[Customers]) -> str:
    return json.dumps([
        {
            "customer_id": r.customer_id,
            "customer_name": r.customer_name,
            "age": r.age,
            "gender": r.gender,
        } for r in rows
    ], ensure_ascii=False)

def myselect(model, customer_id: str) -> str | None:
    with SessionLocal() as db:
        stmt = select(model).where(model.customer_id == customer_id)
        rows = db.scalars(stmt).all()
        return _rows_to_json(rows) if rows else None

def myselectAll(model) -> str | None:
    with SessionLocal() as db:
        # 並び替えに使えるカラムを自動選択
        if hasattr(model, "id"):
            stmt = select(model).order_by(model.id)
        elif hasattr(model, "customer_id"):
            stmt = select(model).order_by(model.customer_id)
        else:
            stmt = select(model)
        rows = db.scalars(stmt).all()
        return _rows_to_json(rows) if rows else None

def myinsert(model, values: dict) -> bool:
    with SessionLocal() as db:
        obj = model(**values)
        db.add(obj)
        db.commit()
        return True

def myupdate(model, values: dict) -> bool:
    cid = values.get("customer_id")
    if not cid:
        return False
    with SessionLocal() as db:
        stmt = (
            update(model)
            .where(model.customer_id == cid)
            .values(**{k: v for k, v in values.items() if k != "id"})
        )
        db.execute(stmt)
        db.commit()
        return True
