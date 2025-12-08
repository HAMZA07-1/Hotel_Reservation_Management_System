"""
Module: hotel_manager.py
Date: 12/07/2025
Programmer: Keano, Daniel

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
from datetime import datetime, time, timedelta
import sqlite3
from typing import Optional, List, Union
from database_manager import DatabaseManager

class HotelManager:
    """Handles hotel operations: room search, reservations, cancellations and pricing."""

    def __init__(self, db: DatabaseManager):
        """Initializes the HotelManager, creating a DatabaseManager instance."""
        self.db = db

    def _parse_dates(self, check_in: str, check_out: str) -> tuple[str, str, int]:
        """Private helper function, validates date text and calculates number of nights."""
        try:
            ci = datetime.strptime(check_in, "%Y-%m-%d").date()
            co = datetime.strptime(check_out, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError("Invalid date format. Use YYYY-MM-DD.")

        if co < ci:
            raise ValueError("check_out must be after check_in.")
        if co == ci:
            raise ValueError("check_out cannot be the same day as check_in.")

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
        num_guests: int = None,
        status: str = "Confirmed",
        is_paid: int = None) -> int: #returns new reservation id

        """Creates a new reservation in the database with transactional safety."""
        # Date parsing and initial validation
        ci_iso, co_iso, _ = self._parse_dates(check_in, check_out)

        if not self.db.guest_exists(guest_id = guest_id):
            raise ValueError("Guest does not exist.")

        if not self.db.room_exists(room_id = room_id):
            raise ValueError("Room does not exist.")

        if num_guests is not None:
            room = self.db.get_room(room_id=room_id)
            if num_guests > room["capacity"]:
                raise ValueError("Number of guests exceeds room capacity.")

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
                INSERT INTO reservations (guest_id, room_id, check_in_date, check_out_date, num_guests, total_price, status, is_paid)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (guest_id, room_id, ci_iso, co_iso, num_guests, total_price, status, is_paid),
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

    def cancel_reservation(self, reservation_id: int) -> dict:
        """
        Cancels a reservation applying strict time-based fee logic centered on 2:00 PM check-in.

        Fee Structure:
         > 24h before check-in: 0% Fee
         0-24h before check-in: 20% Fee
         0-24h after check-in:  50% Fee
         > 24h after check-in:  100% Fee

        Returns a receipt dictionary with fee and refund details.
        """
        conn = self.db.connect()
        cur = conn.cursor()

        try:
            conn.isolation_level = None
            cur.execute("BEGIN IMMEDIATE")

            cur.execute(
                "SELECT status, check_in_date, total_price, room_id FROM reservations WHERE reservation_id = ?",
                (reservation_id,)
            )
            row = cur.fetchone()

            if not row:
                cur.execute("ROLLBACK")
                raise ValueError("Reservation not found.")

            status, check_in_date_str, original_price, room_id = row[0], row[1], float(row[2]), row[3]

            if status in ("Cancelled", "Complete"):
                cur.execute("ROLLBACK")
                raise ValueError("Reservation cannot be cancelled (already cancelled or complete).")

            if status == "Checked-in":
                cur.execute("ROLLBACK")
                raise ValueError("Cannot cancel reservation after check-in, perform early check-out instead.")

            # Calculate Fee Logic
            check_in_date = datetime.strptime(check_in_date_str, "%Y-%m-%d").date()
            check_in_deadline = datetime.combine(check_in_date, time(14,0))
            now = datetime.now()

            # Calculate difference: Positive = Before Check-in, Negative = After Check-in
            delta = check_in_deadline - now

            one_day = timedelta(hours=24)

            final_fee = 0.0
            cancellation_reason = ""

            # Case 1: More than 24 hours before check-in
            if delta > one_day:
                final_fee = 0.0
                cancellation_reason = "Early cancellation (> 24h before check-in)"

            # Case 2: 0-24 hours before check-in
            elif timedelta(0) < delta <= one_day:
                final_fee = original_price * 0.20
                cancellation_reason = "Late cancellation (0-24h before check-in)"

            # Case 3: 0-24 hours after check-in
            elif -one_day < delta <= timedelta(0):
                final_fee = original_price * 0.50
                cancellation_reason = "No-show / Very late cancellation (< 24h after check-in)"

            # Case 4: More than 24 hours after check-in
            else: # delta <= -one_day
                final_fee = original_price
                cancellation_reason = "Expired / Abandoned (> 24h after check-in)"

            refund_amount = original_price - final_fee

            # Update reservation status and price
            cur.execute(
                """
                UPDATE reservations
                SET status = 'Cancelled', total_price = ?
                WHERE reservation_id = ?
                """,
                (final_fee, reservation_id)
            )

            cur.execute("COMMIT")

            return {
                "reservation_id": reservation_id,
                "status": "Cancelled",
                "original_price": original_price,
                "cancellation_fee": final_fee,
                "refund_amount": refund_amount,
                "reason": cancellation_reason,
                "cancelled_at": now.isoformat()
            }

        except Exception:
            try:
                cur.execute("ROLLBACK")
            except Exception:
                pass
            raise

        finally:
            conn.close()



    def update_reservation(
        self,
        reservation_id: int,
        room_id: int = None,
        check_in: str = None,
        check_out: str = None,
        num_guests: int = None,
        status: str = None
    ) -> bool:

        pass

    def search_reservation(
        self,
        *,
        # --- Identity & Guest ---
        reservation_id: Optional[Union[int, List[int]]] = None,
        guest_id: Optional[Union[int, List[int]]] = None,
        email: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        phone: Optional[str] = None,

        # --- Room Filters ---
        room_number: Optional[str] = None,
        room_id: Optional[Union[int, List[int]]] = None,
        room_type: Optional[Union[str, List[str]]] = None,
        smoking: Optional[bool] = None,
        min_capacity: Optional[int] = None,
        max_capacity: Optional[int] = None,

        # --- Price Filters ---
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        min_total: Optional[float] = None,
        max_total: Optional[float] = None,

        # --- Status ---
        status: Optional[Union[str, List[str]]] = None,
        is_paid: Optional[int] = None,

        # --- Dates ---
        check_in: Optional[str] = None,       # Exact match
        check_out: Optional[str] = None,      # Exact match
        stay_start: Optional[str] = None,     # Overlap (start window)
        stay_end: Optional[str] = None,       # Overlap (end window)

        # --- Sorting ---
        sort_by: str = "check_in_date",
        sort_dir: str = "asc"

    ) -> List[sqlite3.Row]:

        # Normalize "List or Single" parameters
        if reservation_id is not None and not isinstance(reservation_id, list):
            reservation_id = [reservation_id]
        if guest_id is not None and not isinstance(guest_id, list):
            guest_id = [guest_id]
        if room_id is not None and not isinstance(room_id, list):
            room_id = [room_id]
        if room_type is not None and not isinstance(room_type, list):
            room_type = [room_type]
        if status is not None and not isinstance(status, list):
            status = [status]

        # Empty list -> None
        if reservation_id is not None and len(reservation_id) == 0:
            reservation_id = None
        if guest_id is not None and len(guest_id) == 0:
            guest_id = None
        if room_id is not None and len(room_id) == 0:
            room_id = None
        if room_type is not None and len(room_type) == 0:
            room_type = None
        if status is not None and len(status) == 0:
            status = None

        # Date validation (reuse _parse_dates for pairs)
        if stay_start and stay_end:
            stay_start, stay_end, _ = self._parse_dates(stay_start, stay_end)
        elif stay_start:
            datetime.strptime(stay_start, "%Y-%m-%d")  # validate only
        elif stay_end:
            datetime.strptime(stay_end, "%Y-%m-%d")  # validate only

        # Base Query
        query = """
            SELECT
                r.*,
                g.first_name, g.last_name, g.email, g.phone_number, 
                rm.room_number, rm.room_type, rm.smoking, rm.capacity, rm.price
            FROM reservations r 
            JOIN guests g ON r.guest_id = g.guest_id
            JOIN rooms rm ON r.room_id = rm.room_id
            WHERE 1=1
        """
        params = []

        if reservation_id:
            placeholders = ", ".join(["?"] * len(reservation_id))
            query += f" AND r.reservation_id IN ({placeholders})"
            params.extend(reservation_id)

        if guest_id:
            placeholders = ", ".join(["?"] * len(guest_id))
            query += f" AND r.guest_id IN ({placeholders})"
            params.extend(guest_id)

        if email:
            query += " AND LOWER(g.email) = ?"
            params.append(email.strip().lower())

        if first_name:
            query += " AND LOWER(g.first_name) LIKE ?"
            params.append(f"%{first_name.strip().lower()}%")

        if last_name:
            query += " AND LOWER(g.last_name) LIKE ?"
            params.append(f"%{last_name.strip().lower()}%")

        if phone:
            query += " AND g.phone_number LIKE ?"
            params.append(f"%{phone.strip()}%")

        if room_number:
            query += " AND rm.room_number LIKE ?"
            params.append(f"%{room_number.strip()}%")

        if room_id:
            placeholders = ", ".join(["?"] * len(room_id))
            query += f" AND r.room_id IN ({placeholders})"
            params.extend(room_id)

        if room_type:
            placeholders = ", ".join(["?"] * len(room_type))
            query += f" AND rm.room_type IN ({placeholders})"
            params.extend(room_type)

        if smoking is not None:
            query += " AND rm.smoking = ?"
            params.append(1 if smoking else 0)

        if min_capacity is not None:
            query += " AND rm.capacity >= ?"
            params.append(min_capacity)
        if max_capacity is not None:
            query += " AND rm.capacity <= ?"
            params.append(max_capacity)

        if min_price is not None:
            query += " AND rm.price >= ?"
            params.append(min_price)
        if max_price is not None:
            query += " AND rm.price <= ?"
            params.append(max_price)

        if min_total is not None:
            query += " AND r.total_price >= ?"
            params.append(min_total)
        if max_total is not None:
            query += " AND r.total_price <= ?"
            params.append(max_total)

        if status:
            placeholders = ", ".join(["?"] * len(status))
            query += f" AND r.status IN ({placeholders})"
            params.extend(status)

        if is_paid is not None:
            query += " AND r.is_paid = ?"
            params.append(1 if is_paid else 0)

        if check_in:
            query += " AND r.check_in_date = ?"
            params.append(check_in)

        if check_out:
            query += " AND r.check_out_date = ?"
            params.append(check_out)

        # Date Filters (Ranges)
        # Scenario A: Bounded Range (Start AND End)
        if stay_start and stay_end:
            # Standard Overlap Logic
            query += " AND (r.check_in_date < ? AND r.check_out_date > ?)"
            params.append(stay_end)
            params.append(stay_start)
        # Scenario B: Open-Ended Start ("From this date onward")
        elif stay_start:
            # Show anything that is still in the hotel after this start date
            query += " AND r.check_out_date > ?"
            params.append(stay_start)
        # Scenario C: Open-Ended End ("Up until this date")
        elif stay_end:
            # Show anything that arrived before this cutoff
            query += " AND r.check_in_date < ?"
            params.append(stay_end)

        valid_sort_cols = {
            "check_in_date": "r.check_in_date",
            "check_out_date": "r.check_out_date",
            "guest_id": "r.guest_id",
            "last_name": "g.last_name",
            "room_number": "rm.room_number",
            "total_price": "r.total_price",
            "status": "r.status"
        }

        # Default to check_in_date if invalid sort column passed
        col_sql = valid_sort_cols.get(sort_by, "r.check_in_date")
        dir_sql = "DESC" if sort_dir.lower() == "desc" else "ASC"

        query += f" ORDER BY {col_sql} {dir_sql}"

        return self.db.execute_query(query, tuple(params))