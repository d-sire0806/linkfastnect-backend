from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import requests

app = FastAPI()

# CORS（必要に応じて絞る）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 最小のヘルスチェック。DBに触らない ---
@app.get("/")
def index():
    return {"message": "FastAPI top page!"}

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

# Pydantic モデル
class Customer(BaseModel):
    customer_id: str
    customer_name: str
    age: int
    gender: str

# --- ここからDBを使う系。遅延インポートで起動時エラーを回避 ---
@app.post("/customers")
def create_customer(customer: Customer):
    from db_control import crud, mymodels  # ← 遅延インポート
    values = customer.dict()
    _ = crud.myinsert(mymodels.Customers, values)
    result = crud.myselect(mymodels.Customers, values.get("customer_id"))
    if result:
        return json.loads(result)
    return None

@app.get("/customers")
def read_one_customer(customer_id: str = Query(...)):
    from db_control import crud, mymodels
    result = crud.myselect(mymodels.Customers, customer_id)
    if not result:
        raise HTTPException(status_code=404, detail="Customer not found")
    obj = json.loads(result)
    return obj[0] if obj else None

@app.get("/allcustomers")
def read_all_customer():
    from db_control import crud, mymodels
    result = crud.myselectAll(mymodels.Customers)
    return [] if not result else json.loads(result)

@app.put("/customers")
def update_customer(customer: Customer):
    from db_control import crud, mymodels
    values = customer.dict()
    original_id = values.get("customer_id")
    _ = crud.myupdate(mymodels.Customers, values)
    result = crud.myselect(mymodels.Customers, original_id)
    if not result:
        raise HTTPException(status_code=404, detail="Customer not found")
    obj = json.loads(result)
    return obj[0] if obj else None

@app.delete("/customers")
def delete_customer(customer_id: str = Query(...)):
    from db_control import crud, mymodels
    result = crud.mydelete(mymodels.Customers, customer_id)
    if not result:
        raise HTTPException(status_code=404, detail="Customer not found")
    return {"customer_id": customer_id, "status": "deleted"}
