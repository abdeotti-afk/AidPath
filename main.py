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
            source TEXT
        )
    """)

    programs = [
        (
            "Demo Education Support",
            "education",
            "citizen",
            "all",
            "Sample education support program.",
            "Demo data only.",
            "https://u.ae/"
        ),
        (
            "Demo Housing Support",
            "housing",
            "citizen",
            "abu_dhabi",
            "Sample housing support program.",
            "Demo data only.",
            "https://u.ae/"
        ),
        (
            "Demo Healthcare Support",
            "healthcare",
            "resident",
            "all",
            "Sample healthcare support program.",
            "Demo data only.",
            "https://u.ae/"
        )
    ]

    for program in programs:
        exists = db.execute(
            "SELECT id FROM programs WHERE name = ?",
            (program[0],)
        ).fetchone()

        if not exists:
            db.execute("""
                INSERT INTO programs
                (name, category, residency, emirate,
                 description, requirements, source)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, program)

    db.commit()
    db.close()


setup()


@app.get("/")
def home():
    return {
        "project": "AidPath",
        "status": "Running",
        "version": "2.0"
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