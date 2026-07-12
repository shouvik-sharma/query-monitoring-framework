"""Initialize query_history.db with the schema defined in schema/query_history_schema.sql."""

import sqlite3

DB_PATH = "data/query_history.db"
SCHEMA_PATH = "schema/query_history_schema.sql"

def create_database():
    # Connect to database (creates if doesn't exist)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Read schema file
    with open(SCHEMA_PATH, 'r') as f:
        schema = f.read()
    
    # Execute schema
    cursor.executescript(schema)
    
    # Verify tables exist
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("Created tables:", [t[0] for t in tables])
    
    conn.close()

if __name__ == "__main__":
    create_database()