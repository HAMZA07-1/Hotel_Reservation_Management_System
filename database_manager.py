
import sqlite3
import os

class DatabaseManager:
    """Handles all database operations for rooms, guests, and reservations."""

    def __init__(self, db_name="hotel_data.db"):
        self.db_name = db_name
        self.create_if_missing()

    def create_if_missing(self):
        """Ensure the database exists with basic tables."""
        create_script = "database_scripts/001_create_tables.sql"
        populate_script = "database_scripts/002_populate_rooms.sql"

        # Only create tables if DB doesn’t exist yet
        if not os.path.exists(self.db_name):
            print("[Setup] Creating new hotel database...")
            conn = sqlite3.connect(self.db_name)
            c = conn.cursor()

            try:
                with open(create_script, "r") as file:
                    c.executescript(file.read())
                with open(populate_script, "r") as file:
                    c.executescript(file.read())
                conn.commit()
                print("[Setup] Database created successfully.")
            except Exception as e:
                print("[Error] during DB setup:", e)
            finally:
                conn.close()
        else:
            print("(i) Database already exists. Skipping setup.")

    def connect(self):
        """Return a new database connection."""
        return sqlite3.connect(self.db_name)

    # ---------- BASIC TEST-ABLE METHODS ----------
    def create_tables(self):
        """Create minimal test tables (for unit testing)."""
        conn = self.connect()
        cur = conn.cursor()
        cur.executescript("""
            CREATE TABLE IF NOT EXISTS rooms (
                room_id INTEGER PRIMARY KEY AUTOINCREMENT,
                room_number INTEGER,
                room_type TEXT,
                capacity INTEGER,
                price REAL,
                is_available INTEGER
            );

            CREATE TABLE IF NOT EXISTS guests (
                guest_id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT,
                last_name TEXT,
                email TEXT,
                phone TEXT,
                address TEXT
            );
        """)
        conn.commit()
        conn.close()

    def add_room(self, room_number, room_type, capacity, price, available):
        """Insert a new room record."""
        conn = self.connect()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO rooms (room_number, room_type, capacity, price, is_available)
            VALUES (?, ?, ?, ?, ?)
        """, (room_number, room_type, capacity, price, available))
        conn.commit()
        conn.close()

    def add_guest(self, first_name, last_name, email, phone, address):
        """Insert a new guest record."""
        conn = self.connect()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO guests (first_name, last_name, email, phone, address)
            VALUES (?, ?, ?, ?, ?)
        """, (first_name, last_name, email, phone, address))
        conn.commit()
        conn.close()
