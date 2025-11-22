from datetime import datetime
import sqlite3
from typing import Optional, List
from database_manager import DatabaseManager

class HotelManager:
# Handles hotel operations: room search, reservations, cancellations and pricing.

    def __init__(self, db_name: str | None = None):
        if db_name:
            self.db = DatabaseManager(db_name)
        else:
            self.db = DatabaseManager()

    # Private helper function, validates date text and calculates number of nights
    def _parse_dates(self, check_in: str, check_out: str) -> tuple[str, str, int]:
        ci = datetime.strptime(check_in, "%Y-%m-%d").date()
        co = datetime.strptime(check_out, "%Y-%m-%d").date()
        if ci >= co:
            raise ValueError("check_out must be after check_in")
        nights = (co - ci).days
        return ci.isoformat(), co.isoformat(), nights

    # Builds custom SQL query based on optional filters entered, returns a list of matching rooms
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
        """Search rooms for manager/employee workflows using attribute filters plus optional
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
            status: str = "Confirmed") -> int:
        ci_iso, co_iso, nights = self._parse_dates(check_in, check_out)

        if not self.db.guest_exists(guest_id=guest_id):
            raise ValueError("Guest does not exist")

        room = self.db.get_room(room_id=room_id)
        if room is None:
            raise ValueError("Room does not exist")

        total_price = float(room["price"]) * nights

        conn = self.db.connect()
        cur = conn.cursor()

        try:
            conn.isolation_level = None
            cur.execute("BEGIN IMMEDIATE")  # Prevents a "race condition"

            occ = DatabaseManager.OCCUPIED_STATUSES
            ph = ", ".join(["?"] * len(occ))
            cur.execute(
                f"""
                    SELECT 1
                    FROM reservations
                    WHERE room_id = ?
                      AND status IN ({ph})
                      AND NOT (check_out_date <= ? OR check_in_date >= ?)
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
            try:
                cur.execute("ROLLBACK")
            except Exception:
                pass
            raise

        finally:
            conn.close()