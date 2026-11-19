from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sqlite3

app = FastAPI(title="AidPath")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)


def database():
    return sqlite3.connect("aidpath.db")


def setup():
    db = database()

    db.execute("""
        CREATE TABLE IF NOT EXISTS programs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            category TEXT,
            residency TEXT,
            emirate TEXT,
            description TEXT,
            requirements TEXT,
            source TEXT,
            verified_at TEXT
        )
    """)

    # Add verification date column to older databases
    columns = [
        row[1] for row in
        db.execute("PRAGMA table_info(programs)").fetchall()
    ]

    if "verified_at" not in columns:
        db.execute(
            "ALTER TABLE programs ADD COLUMN verified_at TEXT"
        )

    # Remove old demonstration programs
    db.execute("""
        DELETE FROM programs
        WHERE name LIKE 'Demo %'
    """)

    program = (
        "برنامج الدعم الاجتماعي الاتحادي",
        "financial",
        "citizen",
        "all",
        "برنامج اتحادي يقدم مساعدات مالية شهرية للأسر الإماراتية "
        "ذات الدخل المحدود، وفق شروط ومعايير تحددها الوزارة.",
        "يشترط أن يكون المستفيد مواطناً ومقيماً إقامة دائمة في الإمارات. "
        "يجب ألا يقل عمر المستفيد الرئيسي عن 21 سنة. "
        "تطبق شروط الدخل والعمل والتقاعد والأصول المالية، "
        "مع وجود استثناءات لبعض الحالات الاجتماعية والصحية. "
        "هذه معلومات إرشادية وليست قرار أهلية رسمي.",
        "https://www.moce.gov.ae/en/web/guest/w/social-welfare",
        "2026-11-19"
    )

    exists = db.execute(
        "SELECT id FROM programs WHERE name = ?",
        (program[0],)
    ).fetchone()

    if not exists:
        db.execute("""
            INSERT INTO programs
            (name, category, residency, emirate,
             description, requirements, source, verified_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, program)

    db.commit()
    db.close()


setup()


@app.get("/")
def home():
    return {
        "project": "AidPath",
        "status": "Running",
        "version": "3.0"
    }


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/programs")
def get_programs(
    category: str = None,
    residency: str = None,
    emirate: str = None
):
    db = database()
    db.row_factory = sqlite3.Row

    query = "SELECT * FROM programs WHERE 1=1"
    values = []

    if category:
        query += " AND category = ?"
        values.append(category)

    if residency:
        query += " AND residency = ?"
        values.append(residency)

    if emirate:
        query += " AND (emirate = ? OR emirate = 'all')"
        values.append(emirate)

    rows = db.execute(query, values).fetchall()
    db.close()

    return [dict(row) for row in rows]
