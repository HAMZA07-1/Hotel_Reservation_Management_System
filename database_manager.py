"""
Module: database_manager.py
Date: 12/04/2025
Programmer: Keano, Daniel, Hamza, Allen

Description:
This module provides the DatabaseManager class, which encapsulates all direct interactions with the SQLite database.
It is responsible for initializing the database schema, managing connections, and providing a low-level API for
Create, Read, Update, and Delete (CRUD) operations on the core tables (rooms, guests, reservations). It abstracts
the SQL logic away from the higher-level business logic.

Important Functions:
- create_if_missing(): Checks if the database exists and has the correct schema. If not, it runs SQL scripts to
  create and populate the tables. This ensures a consistent database state on first run.
  Input: None.
  Output: None.
- connect(): Returns a new database connection object with foreign key enforcement enabled.
  Input: None.
  Output: sqlite3.Connection object.
- add_guest(...): Inserts a new guest record into the database.
  Input: first_name, last_name, email, address_line1, city, state, postal_code, phone_number (optional), address_line2 (optional).
  Output: guest_id (int).
- add_room(...): Inserts a new room record into the database.
  Input: room_number, room_type, capacity, price, available.
  Output: None.
- get_guest/get_room(...): Functions to retrieve a single record by its ID or another unique identifier.
  Input: ID or unique field (e.g., email, room_number).
  Output: sqlite3.Row object representing the record, or None if not found.
- guest_exists/room_exists(...): Functions to check if a guest or room exists.
  Input: guest_id or email for guests; room_id or room_number for rooms.
  Output: bool.
- cancel_reservation(reservation_id, guest_id): Updates a reservation's status to 'Cancelled'.
  Input: reservation_id (int), guest_id (int).
  Output: bool indicating success.
- is_room_available(...): Checks if a room is available for a given date range by checking for overlapping
  reservations with 'occupied' statuses.
  Input: room_number (int), check_in_date (str), check_out_date (str).
  Output: bool.

Important Data Structures:
- OCCUPIED_STATUSES: A tuple containing reservation statuses that indicate a room is physically occupied
  ('Confirmed', 'Checked-in'). This is used to determine availability conflicts.

Notes:
- Reservation creation is handled by HotelManager.reserve_room() which provides transactional safety.
"""
import sqlite3
from pathlib import Path


class DatabaseManager:
    """Handles all database operations for rooms, guests, and reservations."""

    OCCUPIED_STATUSES = ("Confirmed", "Checked-in")

    def __init__(self, db_name="hotel.db"):
        self.db_name = db_name
        self.create_if_missing()

    # ---------------------------------------------------
    # Database Setup
    # ---------------------------------------------------

    def create_if_missing(self):
        """Ensure the database exists with required tables and initial data using external SQL scripts.
        Behavior:
          - If file does not exist: initialize.
          - If file exists but required tables absent: initialize.
          - If some (but not all) required tables exist: raise RuntimeError (partial schema).
          - If all required tables exist: skip initialization.
        """
        db_path = Path(self.db_name)
        required_tables = {"rooms", "guests", "reservations"}
        need_init = False

        if not db_path.exists():
            need_init = True
        else:
            try:
                conn = sqlite3.connect(str(db_path))
                cur = conn.cursor()
                cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
                existing = {row[0] for row in cur.fetchall()}
                conn.close()
            except Exception as e:
                # Corrupt file or unreadable -> reinitialize
                print(f"[Warn] Could not inspect existing DB; will reinitialize: {e}")
                need_init = True
            else:
                if required_tables.issubset(existing):
                    print(f"(i) Database '{self.db_name}' schema detected. Skipping setup.")
                    return
                elif existing & required_tables:
                    raise RuntimeError(
                        f"Partial schema detected in '{self.db_name}'. Existing tables: {existing & required_tables}. "
                        "Manual intervention required before initialization."  # Avoid accidental overwrite.
                    )
                else:
                    need_init = True

        if not need_init:
            return

        # Determine script directory relative to this file
        file_dir = Path(__file__).resolve().parent
        scripts_dir = file_dir / "database_scripts"
        create_sql_path = scripts_dir / "001_create_tables.sql"
        populate_sql_path = scripts_dir / "002_populate_rooms.sql"

        try:
            create_sql = create_sql_path.read_text(encoding="utf-8")
            populate_sql = populate_sql_path.read_text(encoding="utf-8")
        except FileNotFoundError as e:
            raise FileNotFoundError(
                f"Required SQL script missing: {e}. Expected at '{scripts_dir}'."
            ) from e

        db_path.parent.mkdir(parents=True, exist_ok=True)
        print("[Setup] Initializing hotel database (schema + seed data)...")
        conn = None
        try:
            conn = sqlite3.connect(str(db_path))
            cur = conn.cursor()
            cur.executescript(create_sql)
            cur.executescript(populate_sql)
            conn.commit()
            print("[Setup] Database initialized successfully.")
        except Exception as e:
            if conn is not None:
                try:
                    conn.close()
                except Exception:
                    pass
            if db_path.exists():
                try:
                    db_path.unlink()
                except Exception:
                    print(f"[Warn] Failed to remove broken DB file '{db_path}'.")
            raise RuntimeError(f"[Error] during DB initialization: {e}") from e
        finally:
            if conn is not None:
                try:
                    conn.close()
                except Exception:
                    pass

    def connect(self):
        """Return a new database connection with foreign key enforcement enabled."""
        conn = sqlite3.connect(self.db_name)
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    # ---------------------------------------------------
    # Guest Methods
    # ---------------------------------------------------
    def add_guest(
        self,
        first_name: str,
        last_name: str,
        email: str,
        address_line1: str,
        city: str,
        state: str,
        postal_code: str,
        phone_number: str = None,
        address_line2: str = None
        ) -> int:
        """Add a new guest to the database. Optional fields default to NULL."""
        conn = self.connect()
        cur = conn.cursor()
        try:
            cur.execute("""
                INSERT INTO guests (first_name, last_name, email, phone_number, address_line1, address_line2, city, state, postal_code)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (first_name, last_name, email, phone_number, address_line1, address_line2, city, state, postal_code))
            conn.commit()
            return cur.lastrowid
        finally:
            conn.close()

    def get_guest(self, guest_id: int = None, email: str = None) -> sqlite3.Row | None:
        """Retrieve a guest by guest_id or email. Returns None if not found."""
        if guest_id is None and email is None:
            raise ValueError("Provide guest_id or email to search for guest.")
        conn = self.connect()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        if guest_id:
            cur.execute("SELECT * FROM guests WHERE guest_id = ?", (guest_id,))
        else:
            cur.execute("SELECT * FROM guests WHERE email = ?", (email,))
        row = cur.fetchone()
        conn.close()
        return row

    def guest_exists(self, guest_id=None, email=None):
        return self.get_guest(guest_id=guest_id, email=email) is not None

    # ---------------------------------------------------
    # Room Methods
    # ---------------------------------------------------
    def add_room(self, room_number, room_type, capacity, price, available):
        conn = self.connect()
        cur = conn.cursor()
        # Explicitly include smoking column (default 0) to be compatible with external schema requiring NOT NULL
        cur.execute("""
            INSERT INTO rooms (room_number, room_type, smoking, capacity, price, is_available)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (room_number, room_type, 0, capacity, price, available))
        conn.commit()
        conn.close()

    def get_room(self, room_id=None, room_number=None):
        if room_id is None and room_number is None:
            raise ValueError("Provide room_id or room_number.")
        conn = self.connect()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        if room_id:
            cur.execute("SELECT * FROM rooms WHERE room_id = ?", (room_id,))
        else:
            cur.execute("SELECT * FROM rooms WHERE room_number = ?", (room_number,))
        row = cur.fetchone()
        conn.close()
        return row

    def room_exists(self, room_id: int = None, room_number: int = None) -> bool:
        """Checks if a room exists using its ID or number."""
        if room_id is None and room_number is None:
            raise ValueError("Provide room_id or room_number.")
        if room_id:
            sql = "SELECT 1 FROM rooms WHERE room_id = ? LIMIT 1"
            params = (room_id,)
        else:
            sql = "SELECT 1 FROM rooms WHERE room_number = ? LIMIT 1"
            params = (room_number,)
        conn = self.connect()
        cur = conn.cursor()
        try:
            cur.execute(sql, params)
            return cur.fetchone() is not None
        finally:
            conn.close()

    def get_room_price(self, room_id):
        """
        Returns the nightly price for a given room.
        """
        conn = self.connect()
        cur = conn.cursor()

        try:
            cur.execute("SELECT price FROM rooms WHERE room_id = ?", (room_id,))
            row = cur.fetchone()

            if row is None:
                raise ValueError(f"Room with ID {room_id} not found.")

            return row[0]

        finally:
            conn.close()

    def get_rooms_filtered(self, room_number="", available=None,
                           smoking=None, capacity=None):
        conn = self.connect()
        cursor = conn.cursor()

        query = """
            SELECT room_id, room_number, room_type,
                   smoking, capacity, price, is_available
            FROM rooms
            WHERE 1=1
        """
        params = []

        if room_number:
            query += " AND room_number LIKE ?"
            params.append(f"%{room_number}%")

        if available is not None:
            query += " AND is_available = ?"
            params.append(1 if available else 0)

        if smoking is not None:
            query += " AND smoking = ?"
            params.append(1 if smoking else 0)

        if capacity is not None:
            query += " AND capacity = ?"
            params.append(int(capacity))

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        return rows

    def update_room(self, room_id, new_price, new_is_available):
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE rooms SET price = ?, is_available = ? WHERE room_id = ?",
            (new_price, new_is_available, room_id),
        )
        conn.commit()
        conn.close()

    # ---------------------------------------------------
    # Reservation Methods
    # ---------------------------------------------------

    def cancel_reservation(self, reservation_id: int, guest_id: int) -> bool:
        conn = self.connect()
        cur = conn.cursor()
        try:
            cur.execute("""
                SELECT status FROM reservations
                WHERE reservation_id = ? AND guest_id = ?
            """, (reservation_id, guest_id))
            row = cur.fetchone()
            if not row or row[0] == "Cancelled":
                return False
            cur.execute("""
                UPDATE reservations
                SET status = 'Cancelled'
                WHERE reservation_id = ? AND guest_id = ?
            """, (reservation_id, guest_id))
            conn.commit()
            return True
        except Exception as e:
            print(f"[Error] Cancel reservation failed: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def update_reservation(self, reservation_id, check_in_date, check_out_date, total_price, status):
        conn = self.connect()
        cur = conn.cursor()
        try:
            cur.execute("""
                UPDATE reservations
                SET check_in_date = ?,
                    check_out_date = ?,
                    total_price = ?,
                    status = ?
                WHERE reservation_id = ?
            """, (check_in_date, check_out_date, total_price, status, reservation_id))
            if cur.rowcount == 0:
                print(f"[Warn] No reservation found with ID {reservation_id}")
                return False
            conn.commit()
            print(f"[Debug] Reservation {reservation_id} updated successfully.")
            return True
        except Exception as e:
            print(f"[Error] Failed to update reservation {reservation_id}: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def execute_query(self, query: str, params: tuple = (), fetch_all: bool = True):
        """Execute a given SQL query and return the results. Commits modifications automatically."""
        conn = self.connect()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        try:
            cur.execute(query, params)
            conn.commit()
            if fetch_all:
                return cur.fetchall()
            return cur.fetchone()
        finally:
            conn.close()

    def is_room_available(self, room_number: int, check_in_date: str | None = None, check_out_date: str | None = None) -> bool:
        conn = self.connect()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        try:
            # Basic availability flag check first
            cur.execute("SELECT room_id, is_available FROM rooms WHERE room_number = ?", (room_number,))
            room = cur.fetchone()
            if room is None:
                return False
            if int(room[1]) == 0:
                return False
            # If no date range provided, rely only on is_available flag
            if not check_in_date or not check_out_date:
                return True
            # Check overlapping reservations with occupied statuses
            occ = self.OCCUPIED_STATUSES
            placeholders = ", ".join(["?"] * len(occ))
            cur.execute(
                f"""
                SELECT 1 FROM reservations
                WHERE room_id = ?
                  AND status IN ({placeholders})
                  AND NOT (check_out_date <= ? OR check_in_date >= ?)
                LIMIT 1
                """,
                (room[0], *occ, check_in_date, check_out_date)
            )
            return cur.fetchone() is None
        finally:
            conn.close()

    # Can be removed if reserve_room has same functionality
    def get_available_rooms(self, check_in_date, check_out_date, num_guests, include_smoking):
        check_in = check_in_date.isoformat()
        check_out = check_out_date.isoformat()
        occ = self.OCCUPIED_STATUSES
        occ_placeholders = ", ".join(["?"] * len(occ))

        query = f"""
            SELECT r.room_id, r.room_number, r.capacity, r.price
            FROM rooms r
            LEFT JOIN reservations res
                ON r.room_id = res.room_id
                AND res.status IN ({occ_placeholders})
                AND NOT (
                    res.check_out_date <= ?
                    OR
                    res.check_in_date >= ?
                )
            WHERE r.capacity >= ?
              AND (? = 1 OR r.smoking = 0)
              AND res.room_id IS NULL
            ORDER BY r.capacity ASC, r.room_number ASC;
        """

        params = (*occ, check_in, check_out, num_guests, include_smoking)

        conn = self.connect()
        cur = conn.cursor()
        cur.execute(query, params)
        rows = cur.fetchall()
        conn.close()

        return rows