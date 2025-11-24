"""
Module: populate_test_data.py
Date: 11/12/2025
Programmer(s): Hamza

Brief Description:
This is a standalone utility script designed to populate the main database (`hotel.db`) with a small, specific set of sample data. It inserts a couple of guests and reservations, which is useful for manual testing, demonstrations, or ensuring the application has initial data to display upon first use.

Important Functions:
- main() -> None
  - Input: None
  - Output: None (modifies the database file and prints progress to the console).
  - Description: Connects to the database, ensures tables are created via the DatabaseManager, and then executes hardcoded SQL INSERT statements to add new guest and reservation records. It commits the transaction and closes the connection.

Important Data Structures:
- The script uses the `DatabaseManager` class to handle database connections and setup.
- The data to be inserted is stored directly within multi-line SQL strings.

Algorithms:
- N/A. This is a simple, procedural script that executes a fixed sequence of database operations.
"""
from database_manager import DatabaseManager
from config import DB_PATH
import sqlite3

print("[Debug] Populating database at:", DB_PATH)
db = DatabaseManager(DB_PATH)

def main():
    """Connects to the database and inserts a small set of test guests and reservations."""
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
