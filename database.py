import sqlite3

DB_PATH = "bot.db"

def get_conn():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_conn()
    c = conn.cursor()

    # Custom commands table
    c.execute("""
        CREATE TABLE IF NOT EXISTS custom_commands (
            guild_id INTEGER,
            trigger TEXT,
            response TEXT,
            PRIMARY KEY (guild_id, trigger)
        )
    """)

    # Warnings table
    c.execute("""
        CREATE TABLE IF NOT EXISTS warnings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            guild_id INTEGER,
            user_id INTEGER,
            reason TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()
    print("✅ Database initialized.")
