import sqlite3
import json
from typing import Dict, Any, List
from ml.config import DATA_ROOT

DB_PATH = DATA_ROOT / "matone.db"

def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    c = conn.cursor()
    
    # Audit Log
    c.execute('''
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            event_type TEXT,
            source_system TEXT,
            material_code TEXT,
            details TEXT
        )
    ''')
    
    # Review Queue
    c.execute('''
        CREATE TABLE IF NOT EXISTS review_queue (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_material_code TEXT,
            status TEXT DEFAULT 'PENDING',
            recommendation_json TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Decisions
    c.execute('''
        CREATE TABLE IF NOT EXISTS decisions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            review_id INTEGER,
            reviewer_id TEXT,
            decision TEXT,
            comments TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            model_version TEXT,
            rule_version TEXT,
            FOREIGN KEY(review_id) REFERENCES review_queue(id)
        )
    ''')
    
    # Canonical Records
    c.execute('''
        CREATE TABLE IF NOT EXISTS canonical_records (
            cnmc TEXT PRIMARY KEY,
            canonical_description TEXT,
            family TEXT,
            attributes_json TEXT,
            approval_status TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Source Mappings
    c.execute('''
        CREATE TABLE IF NOT EXISTS source_mappings (
            source_material_code TEXT NOT NULL,
            cpse_id TEXT NOT NULL,
            cnmc TEXT,
            status TEXT,
            mapped_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(cnmc) REFERENCES canonical_records(cnmc),
            PRIMARY KEY (cpse_id, source_material_code)
        )
    ''')

    # Migrate databases created before CPSE formed part of a mapping's key.
    # A source code is only unique within its originating organization.
    mapping_columns = c.execute("PRAGMA table_info(source_mappings)").fetchall()
    primary_key_columns = [row["name"] for row in mapping_columns if row["pk"]]
    if primary_key_columns == ["source_material_code"]:
        c.execute("ALTER TABLE source_mappings RENAME TO source_mappings_legacy")
        c.execute('''
            CREATE TABLE source_mappings (
                source_material_code TEXT NOT NULL,
                cpse_id TEXT NOT NULL,
                cnmc TEXT,
                status TEXT,
                mapped_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(cnmc) REFERENCES canonical_records(cnmc),
                PRIMARY KEY (cpse_id, source_material_code)
            )
        ''')
        c.execute('''
            INSERT INTO source_mappings (source_material_code, cpse_id, cnmc, status, mapped_at)
            SELECT source_material_code, cpse_id, cnmc, status, mapped_at
            FROM source_mappings_legacy
        ''')
        c.execute("DROP TABLE source_mappings_legacy")
    
    conn.commit()
    conn.close()

def log_audit_event(event_type: str, source_system: str, material_code: str, details: Dict[str, Any]):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "INSERT INTO audit_log (event_type, source_system, material_code, details) VALUES (?, ?, ?, ?)",
        (event_type, source_system, material_code, json.dumps(details))
    )
    conn.commit()
    conn.close()
    
# Initialize on import
init_db()
