from fastapi import FastAPI
from pydantic import BaseModel
import sqlite3
import datetime

app = FastAPI(title="MNCOS Cash Engine v0.1")
DB = "cash_engine.db"

def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS inventory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_name TEXT NOT NULL,
        quantity INTEGER DEFAULT 0,
        reorder_point INTEGER DEFAULT 10,
        updated_at TEXT
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS employees (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        base_salary REAL NOT NULL,
        days_worked INTEGER DEFAULT 30,
        deductions REAL DEFAULT 0,
        bonuses REAL DEFAULT 0
    )""")
    conn.commit()
    conn.close()

init_db()

class Item(BaseModel):
    item_name: str
    quantity: int
    reorder_point: int = 10

class Employee(BaseModel):
    name: str
    base_salary: float
    days_worked: int = 30
    deductions: float = 0
    bonuses: float = 0

@app.get("/health")
def health():
    return {"status": "operational", "version": "0.1.0"}

@app.post("/inventory/add")
def add_item(item: Item):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("INSERT INTO inventory (item_name, quantity, reorder_point, updated_at) VALUES (?, ?, ?, ?)",
              (item.item_name, item.quantity, item.reorder_point, datetime.datetime.now().isoformat()))
    conn.commit()
    conn.close()
    return {"status": "added", "item": item.item_name}

@app.get("/inventory/alerts")
def alerts():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT item_name, quantity, reorder_point FROM inventory WHERE quantity <= reorder_point")
    rows = c.fetchall()
    conn.close()
    return {"total": len(rows), "alerts": [{"item": r[0], "current": r[1]} for r in rows]}

@app.post("/payroll/calculate")
def payroll(emp: Employee):
    daily = emp.base_salary / 30
    gross = daily * emp.days_worked
    net = gross + emp.bonuses - emp.deductions
    return {"employee": emp.name, "net_salary": round(net, 2)}
