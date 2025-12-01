"""
Module: hotel_manager.py
Date: 11/21/2025
Programmer: Keano

Description:
This module contains the HotelManager class, which implements the core business logic for hotel operations.
It acts as an intermediary between the user interface/API layer and the database layer (DatabaseManager).
Its responsibilities include advanced room searching, price calculation, and handling the reservation process
with transactional integrity.

Important Functions:
- search_rooms(...): Performs a complex search for rooms based on a variety of filter criteria. It dynamically
  builds a SQL query to match all specified conditions.
  Input: A set of optional keyword arguments like check_in, check_out, room_types, capacity, price, etc.
  Output: A list of sqlite3.Row objects representing the matching rooms.
- calculate_total_price(...): Calculates the total cost of a stay based on the room's nightly price and the
  number of nights.
  Input: room_id (int), check_in (str), check_out (str).
  Output: float representing the total price.
- reserve_room(...): Creates a new reservation. It performs a critical check for room availability within a
  database transaction to prevent double-booking (race conditions).
  Input: guest_id (int), room_id (int), check_in (str), check_out (str).
  Output: int, the ID of the newly created reservation.

Algorithms:
- Dynamic SQL Query Construction (in search_rooms): The search function constructs a SQL query string and a
  corresponding parameter list piece-by-piece. Each filter argument adds a new 'AND' clause to the WHERE
  statement. This approach is flexible and avoids writing numerous pre-defined queries. It's chosen for its
  scalability as new search filters can be added easily.
- Transactional Reservation (in reserve_room): To prevent a race condition where two users might book the same
  room for the same dates simultaneously, this function uses a database transaction ('BEGIN IMMEDIATE'). It first
  locks the database for writing, then re-checks for availability, and only then inserts the new reservation. If
  the room was taken in the meantime, the transaction is rolled back. This ensures data consistency.
"""
from datetime import datetime
import sqlite3
from typing import Optional, List
from database_manager import DatabaseManager

class HotelManager:
    """Handles hotel operations: room search, reservations, cancellations and pricing."""

    def __init__(self, db_name: str | None = None):
        """Initializes the HotelManager, creating a DatabaseManager instance."""
        if db_name:
            self.db = DatabaseManager(db_name)
        else:
            self.db = DatabaseManager()

    def _parse_dates(self, check_in: str, check_out: str) -> tuple[str, str, int]:
        """Private helper function, validates date text and calculates number of nights."""
        ci = datetime.strptime(check_in, "%Y-%m-%d").date()
        co = datetime.strptime(check_out, "%Y-%m-%d").date()
        if ci >= co:
            raise ValueError("check_out must be after check_in")
        nights = (co - ci).days
        return ci.isoformat(), co.isoformat(), nights

    def search_rooms(
        self,
        *,
        check_in: Optional[str] = None,
        check_out: Optional[str] = None,
        room_ids: Optional[List[int]] = None,
        room_number_like: Optional[str] = None,
        room_types: Optional[List[str]] = None,
        min_capacity: Optional[int] = None,
        max_capacity: Optional[int] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        smoking: Optional[bool] = None,
        is_available: Optional[int] = None,
        availability: str = "free",
        sort_by: str = "price",
        sort_dir: str = "asc",
    ) -> List[sqlite3.Row]:
        """Builds custom SQL query based on optional filters entered, returns a list of matching rooms.

        Search rooms for manager/employee workflows using attribute filters plus optional
        date-window overlap logic. All filters combine with logical AND.

        See user-provided specification for detailed behavior rules.
        """
        # Normalize empty lists to None
        if room_ids is not None and len(room_ids) == 0:
            room_ids = None
        if room_types is not None and len(room_types) == 0:
            room_types = None

        # Normalize ranges (swap if inverted)
        if min_capacity is not None and max_capacity is not None and min_capacity > max_capacity:
            min_capacity, max_capacity = max_capacity, min_capacity
        if min_price is not None and max_price is not None and min_price > max_price:
            min_price, max_price = max_price, min_price

        # Validate is_available (must be 0/1 or None)
        if is_available not in (None, 0, 1):
            raise ValueError("is_available must be one of: None, 0, 1")

        # Validate availability mode
        availability_mode = availability.lower()
        if availability_mode not in {"free", "occupied", "all"}:
            availability_mode = "free"

        ci_iso = co_iso = None
        use_dates = False
        if check_in and check_out:
            # Parse & validate dates
            ci_iso, co_iso, _ = self._parse_dates(check_in, check_out)
            use_dates = True
        else:
            # Ignore partial date input
            ci_iso = co_iso = None
            use_dates = False

        sql_parts = ["SELECT r.* FROM rooms r WHERE 1=1"]
        params: List[object] = []

        # ID filter
        if room_ids is not None:
            placeholders = ",".join(["?"] * len(room_ids))
            sql_parts.append(f"AND r.room_id IN ({placeholders})")
            params.extend(room_ids)

        # Room number substring (case-insensitive)
        if room_number_like:
            sql_parts.append("AND LOWER(r.room_number) LIKE ?")
            params.append(f"%{room_number_like.lower()}%")

        # Room types list
        if room_types is not None:
            placeholders = ",".join(["?"] * len(room_types))
            sql_parts.append(f"AND r.room_type IN ({placeholders})")
            params.extend(room_types)

        # Capacity bounds
        if min_capacity is not None:
            sql_parts.append("AND r.capacity >= ?")
            params.append(min_capacity)
        if max_capacity is not None:
            sql_parts.append("AND r.capacity <= ?")
            params.append(max_capacity)

        # Price bounds
        if min_price is not None:
            sql_parts.append("AND r.price >= ?")
            params.append(min_price)
        if max_price is not None:
            sql_parts.append("AND r.price <= ?")
            params.append(max_price)

        # Smoking flag
        if smoking is not None:
            sql_parts.append("AND r.smoking = ?")
            params.append(1 if smoking else 0)

        # Inventory availability flag
        if is_available in (0, 1):
            sql_parts.append("AND r.is_available = ?")
            params.append(is_available)

        # Date overlap logic
        if use_dates and availability_mode != "all":
            occ = DatabaseManager.OCCUPIED_STATUSES
            occ_placeholders = ",".join(["?"] * len(occ))
            overlap_predicate = "NOT (res.check_out_date <= ? OR res.check_in_date >= ?)"  # allows back-to-back
            if availability_mode == "free":
                sql_parts.append(
                    f"AND NOT EXISTS (\n"
                    f"    SELECT 1 FROM reservations res\n"
                    f"    WHERE res.room_id = r.room_id\n"
                    f"      AND res.status IN ({occ_placeholders})\n"
                    f"      AND {overlap_predicate}\n"
                    f")"
                )
            elif availability_mode == "occupied":
                sql_parts.append(
                    f"AND EXISTS (\n"
                    f"    SELECT 1 FROM reservations res\n"
                    f"    WHERE res.room_id = r.room_id\n"
                    f"      AND res.status IN ({occ_placeholders})\n"
                    f"      AND {overlap_predicate}\n"
                    f")"
                )
            params.extend(list(occ) + [ci_iso, co_iso])

        # Sorting
        allowed_sort = {
            "price": "r.price",
            "capacity": "r.capacity",
            "room_number": "r.room_number",
            "room_type": "r.room_type",
            "room_id": "r.room_id",
        }
        sort_col = allowed_sort.get(sort_by.lower(), "r.price")
        sort_direction = "DESC" if sort_dir.lower() == "desc" else "ASC"
        order_clause = f"ORDER BY {sort_col} {sort_direction}"
        if sort_col != "r.room_id":
            order_clause += ", r.room_id ASC"  # deterministic tiebreaker
        sql_parts.append(order_clause)

        final_sql = " \n".join(sql_parts)
        return self.db.execute_query(final_sql, tuple(params))


    def calculate_total_price(self, room_id: int, check_in: str, check_out: str) -> float:
        """Calculates the total price for a stay based on the room's price and number of nights."""
        ci_iso, co_iso, nights = self._parse_dates(check_in, check_out)
        room = self.db.get_room(room_id=room_id)
        if room is None:
            raise ValueError("Room does not exist")
        return float(room["price"]) * nights


    def reserve_room(
            self,
            guest_id: int,
            room_id: int,
            check_in: str,
            check_out: str,
            status: str = "Confirmed") -> int: #returns new reservation id
        """Creates a new reservation in the database with transactional safety."""
        # Date parsing and initial validation
        ci_iso, co_iso, _ = self._parse_dates(check_in, check_out)

        if not self.db.guest_exists(guest_id = guest_id):
            raise ValueError("Guest does not exist.")

        if not self.db.room_exists(room_id = room_id):
            raise ValueError("Room does not exist.")

        total_price = self.calculate_total_price(room_id, check_in, check_out)

        conn = self.db.connect()
        cur = conn.cursor()

        try:
            conn.isolation_level = None
            cur.execute("BEGIN IMMEDIATE") #Prevent a race condition

            occ = DatabaseManager.OCCUPIED_STATUSES
            ph = ", ".join(["?"] * len(occ))
            cur.execute(
                f"""
                    SELECT 1
                    FROM reservations
                    WHERE room_id = ?
                        AND status IN ({ph})
                        AND (check_out_date > ? AND check_in_date < ?)
                    LIMIT 1
                    """,
                (room_id, *occ, ci_iso, co_iso),
            )

            if cur.fetchone():
                cur.execute("ROLLBACK")
                raise ValueError("Room is no longer available for the selected dates")

            cur.execute(
                """
                INSERT INTO reservations (guest_id, room_id, check_in_date, check_out_date, total_price, status)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (guest_id, room_id, ci_iso, co_iso, total_price, status),
            )

            reservation_id = cur.lastrowid
            cur.execute("COMMIT")
            return reservation_id

        except Exception:
            # On any error, ensure the transaction is rolled back.(undoes all changes since BEGIN IMMEDIATE)
            try:
                cur.execute("ROLLBACK")
            except Exception:
                # Ignore rollback errors
                pass
            raise

        finally:
            conn.close()



