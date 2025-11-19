from database_manager import DatabaseManager
from config import DB_PATH
import sqlite3

print("[Debug] Populating database at:", DB_PATH)
db = DatabaseManager(DB_PATH)

def main():
    conn = db.connect()
    cur = conn.cursor()

    # Create tables if missing
    db.create_tables()

    print("→ Inserting guests...")
    cur.executescript("""
    INSERT INTO guests (first_name, last_name, email, phone, address)
    VALUES
    ('Alice', 'Johnson', 'alice@example.com', '555-1234', '123 Sunset Blvd'),
    ('Dwayne', 'Johnson', 'dwayne@example.com', '555-9999', '789 Ocean Ave');
    """)

    print("→ Inserting reservations...")
    cur.executescript("""
    INSERT INTO reservations (guest_id, room_id, check_in_date, check_out_date, total_price, status)
    VALUES
    (1, 101, '2025-11-15', '2025-11-17', 240.0, 'Confirmed'),
    (2, 102, '2025-11-18', '2025-11-20', 280.0, 'Confirmed');
    """)

    conn.commit()
    conn.close()
    print("Done populating test data.")

if __name__ == "__main__":
    main()
