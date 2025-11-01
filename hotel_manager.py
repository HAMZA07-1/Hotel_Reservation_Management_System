from datetime import datetime
import sqlite3
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
    def search_rooms(self,
                     room_type: str | None = None,
                     min_capacity: int | None = None,
                     max_price: float | None = None,
                     check_in: str | None = None,
                     check_out: str | None = None) -> list[sqlite3.Row]:

        ci_iso = co_iso = None
        if check_in and check_out:
            ci_iso, co_iso, _ = self._parse_dates(check_in, check_out)

        conn = self.db.connect()
        conn.execute("PRAGMA foreign_keys = ON")
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        try:
            sql = ["SELECT r.* FROM rooms r WHERE 1=1"]
            params: list[object] = []

            if room_type:
                sql.append("AND r.room_type = ?")
                params.append(room_type)
            if min_capacity is not None:
                sql.append("AND r.capacity >= ?")
                params.append(int(min_capacity))
            if max_price is not None:
                sql.append("AND r.price <= ?")
                params.append(float(max_price))
            if ci_iso and co_iso:
                sql.append("AND r.is_available = 1")
                occ = DatabaseManager.OCCUPIED_STATUSES
                placeholders = ", ".join(["?"] * len(occ))

                sql.append(
                f"""
                AND NOT EXISTS (
                    SELECT 1
                    FROM reservations res
                    WHERE res.room_id = r.room_id
                        AND res.status IN ({placeholders})
                        AND NOT (res.check_out_date <= ? or res.check_in_date >= ?)
                        )
                """
                )
                params.extend(list(occ) + [ci_iso, co_iso])

            sql.append("ORDER BY r.price ASC, r.room_id ASC")
            cur.execute(" ".join(sql), tuple(params))
            return cur.fetchall()
        finally:
            conn.close()


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
            conn.execute("PRAGMA foreign_keys = ON")
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