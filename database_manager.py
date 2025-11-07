
import sqlite3
import os

class DatabaseManager:
    """Handles all database operations for rooms, guests, and reservations."""

    # statuses that indicate the room is currently occupied / not available for booking
    # Update this tuple if there are different reservation status values.
    OCCUPIED_STATUSES = ("Confirmed", "Checked-in")

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
                          
            CREATE TABLE IF NOT EXISTS reservations (
                reservation_id INTEGER PRIMARY KEY AUTOINCREMENT,
                guest_id INTEGER NOT NULL,
                room_id INTEGER NOT NULL,
                check_in_date TEXT NOT NULL,
                check_out_date TEXT NOT NULL,
                total_price REAL NOT NULL,
                status TEXT NOT NULL,
                FOREIGN KEY (guest_id) REFERENCES guests(guest_id),
                FOREIGN KEY (room_id) REFERENCES rooms(room_id)
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

    def add_reservation(self, guest_id, room_id, check_in_date, check_out_date, total_price, status):
        """Insert a new reservation record."""
        conn = self.connect()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO reservations (guest_id, room_id, check_in_date, check_out_date, total_price, status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (guest_id, room_id, check_in_date, check_out_date, total_price, status))
        conn.commit()
        last_id = cur.lastrowid
        conn.close()
        return last_id


    def get_guest(self, guest_id = None, email = None):
        """get a guest via email or id"""

        if guest_id is None and email is None:
            raise ValueError("Provide guest_id or email to search for guest")
        
        conn = self.connect()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        if guest_id is not None:
            cur.execute("SELECT * FROM guests WHERE guest_id = ?", (guest_id,))
        else:
            cur.execute("SELECT * FROM guests WHERE email = ?", (email,))
        
        row = cur.fetchone()
        conn.close()
        return row
    
    def guest_exists(self, guest_id = None, email = None):
        """Return True if a guest exists with matching guest id or email"""

        return self.get_guest(guest_id = guest_id, email = email) is not None
    
    def get_room(self, room_id = None, room_number = None):
        """Get a room via room id or room number"""

        """Provide one identifier (room id or room number)"""
        if room_id is None and room_number is None:
            raise ValueError("Provide room_id or room_number to search for room")
        
        conn = self.connect()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        if room_id is not None:
            cur.execute("SELECT * FROM rooms WHERE room_id = ?", (room_id,))
        else:
            cur.execute("SELECT * FROM rooms WHERE room_number = ?", (room_number,))

        row = cur.fetchone()
        conn.close()
        return row
    
    def is_room_available(self, room_id = None, room_number = None, check_in_date = None, check_out_date = None):
        """Check whether a room exists and is available for the date range"""
        # fetch room (allow lookup by id or number)
        room = self.get_room(room_id = room_id, room_number = room_number)

        if room is None:
            raise ValueError("Room not found")

        # if the room-level availability flag is false (0) consider it unavailable
        try:
            if int(room["is_available"]) == 0:
                return False
        except Exception:
            # If the column missing or not int-like, continue to reservation checks
            pass

        conn = self.connect()
        cur = conn.cursor()

        # statuses that indicate the room is occupied/reserved
        occupied_statuses = ("Confirmed", "Checked-in")

        if check_in_date is not None and check_out_date is not None:
            # Overlap logic: a reservation overlaps the requested range if
            # NOT (existing.check_out_date <= requested.check_in_date OR existing.check_in_date >= requested.check_out_date)
            query = (
                "SELECT 1 FROM reservations WHERE room_id = ? AND status IN (?, ?) "
                "AND NOT (check_out_date <= ? OR check_in_date >= ?) LIMIT 1"
            )
            cur.execute(query, (room["room_id"],) + occupied_statuses + (check_in_date, check_out_date))
        else:
            # No dates provided: check for any active/occupied reservations at all
            query = "SELECT 1 FROM reservations WHERE room_id = ? AND status IN (?, ?) LIMIT 1"
            cur.execute(query, (room["room_id"],) + occupied_statuses)

        conflict = cur.fetchone()
        conn.close()

        return conflict is None

    def get_all_reservations(self):
        try:
            conn = self.connect()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT reservation_id, guest_id, room_id, check_in_date, check_out_date, total_price, status
                FROM reservations
                ORDER BY reservation_id DESC
            """)

            rows = cursor.fetchall()
            column_names = [description[0] for description in cursor.description]

            return [dict(zip(column_names, row)) for row in rows]

        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return []
        finally:
            conn.close()

    def explain_query_plan(self, query, params=()):
        #Prints the query plan for debugging
        #Command example: db = DatabaseManager("hotel.db")
        #db.explain_query_plan("SELECT * FROM reservations WHERE room_number = ?", (101,))
        try:
            conn = self.connect()
            cur = conn.cursor()
            cur.execute(f"EXPLAIN QUERY PLAN {query}", params)
            for row in cur.fetchall():
                print(row)
        except sqlite3.Error as e:
            print("Error explaining query plan:", e)
        finally:
            conn.close()
