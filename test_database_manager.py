import unittest
from datetime import date, timedelta

from database_manager import DatabaseManager


class TestDatabaseManagerMetricsWithSampleData(unittest.TestCase):
    """
    These tests build a small, known data set in a separate test DB and then
    verify that the metrics helpers return exactly the values we expect.

    Scenario we create (all dates relative to *today*):

    Rooms:
      - Room 101 (id r1)
      - Room 102 (id r2)

    Guests:
      - John Doe (g1)
      - Jane Roe (g2)

    Reservations:
      - A: g1 in room 101, today -> tomorrow,  $200,  status='Confirmed'
      - B: g1 in room 102, today -> +2 days,   $300,  status='Cancelled'
      - C: g2 in room 102, -3d -> -1d,        $400,  status='Complete'

    Expected:
      - total_rooms              = 2
      - available_rooms_today    = 1  (room 102 only; room 101 is booked)
      - active_reservations      = 1  (reservation A)
      - cancelled_reservations   = 1  (reservation B)
      - revenue                  = 600.0  (A + C, cancelled B is ignored)
    """

    @classmethod
    def setUpClass(cls):
        # Use a separate DB file so we don't mess with the main app DB.
        cls.db = DatabaseManager("test_metrics.db")

    def setUp(self):
        """Rebuild our small sample data set before each test."""
        conn = self.db.connect()
        cur = conn.cursor()

        # Clear tables in FK-safe order
        cur.execute("DELETE FROM reservations")
        cur.execute("DELETE FROM guests")
        cur.execute("DELETE FROM rooms")
        conn.commit()

        # --- Rooms ---
        cur.execute(
            """
            INSERT INTO rooms
                (room_number, room_type, smoking, capacity, price, is_available)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            ("101", "Single", 0, 2, 100.0, 1),
        )
        room1_id = cur.lastrowid

        cur.execute(
            """
            INSERT INTO rooms
                (room_number, room_type, smoking, capacity, price, is_available)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            ("102", "Single", 0, 2, 120.0, 1),
        )
        room2_id = cur.lastrowid

        # --- Guests ---
        cur.execute(
            """
            INSERT INTO guests
                (first_name, last_name, email, phone_number,
                 address_line1, address_line2, city, state, postal_code)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            ("John", "Doe", "john@example.com", None,
             "123 Main St", None, "Cityville", "ST", "00000"),
        )
        guest1_id = cur.lastrowid

        cur.execute(
            """
            INSERT INTO guests
                (first_name, last_name, email, phone_number,
                 address_line1, address_line2, city, state, postal_code)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            ("Jane", "Roe", "jane@example.com", None,
             "456 Side St", None, "Townburg", "TS", "11111"),
        )
        guest2_id = cur.lastrowid

        # --- Dates (relative to today) ---
        today = date.today()
        today_s = today.isoformat()
        tomorrow_s = (today + timedelta(days=1)).isoformat()
        plus2_s = (today + timedelta(days=2)).isoformat()
        minus3_s = (today - timedelta(days=3)).isoformat()
        minus1_s = (today - timedelta(days=1)).isoformat()

        # --- Reservations ---

        # A: Confirmed, overlaps today, counts as active & revenue, blocks room 101
        cur.execute(
            """
            INSERT INTO reservations
                (guest_id, room_id, check_in_date, check_out_date,
                 num_guests, total_price, status, is_paid)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (guest1_id, room1_id, today_s, tomorrow_s, 1, 200.0, "Confirmed", 1),
        )

        # B: Cancelled, overlaps today, does NOT block availability,
        #    and does NOT count toward revenue.
        cur.execute(
            """
            INSERT INTO reservations
                (guest_id, room_id, check_in_date, check_out_date,
                 num_guests, total_price, status, is_paid)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (guest1_id, room2_id, today_s, plus2_s, 1, 300.0, "Cancelled", 0),
        )

        # C: Completed stay in the past, DOES count toward revenue,
        #    does NOT overlap today so does not block availability.
        cur.execute(
            """
            INSERT INTO reservations
                (guest_id, room_id, check_in_date, check_out_date,
                 num_guests, total_price, status, is_paid)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (guest2_id, room2_id, minus3_s, minus1_s, 1, 400.0, "Complete", 1),
        )

        conn.commit()
        conn.close()

        # Expected metrics for this fixed dataset
        self.expected_metrics = {
            "total_rooms": 2,
            "available_rooms_today": 1,
            "active_reservations": 1,
            "cancelled_reservations": 1,
            "revenue": 600.0,
        }

    def test_get_manager_metrics_expected_values(self):
        """get_manager_metrics should exactly match our hand-computed metrics."""
        metrics = self.db.get_manager_metrics()

        for key, expected in self.expected_metrics.items():
            self.assertIn(key, metrics, msg=f"Missing key: {key}")
            self.assertEqual(
                expected,
                metrics[key],
                msg=f"Metric {key} expected {expected} but got {metrics[key]}",
            )

    def test_get_all_rooms_status_expected_availability_today(self):
        """
        For our sample data:
          - room 101 should NOT be available today
          - room 102 SHOULD be available today
        """
        today_s = date.today().isoformat()
        statuses = self.db.get_all_rooms_status(today_s)

        # We created exactly 2 rooms
        self.assertEqual(2, len(statuses))

        # Index by room_number to make checks easy
        by_number = {str(r["room_number"]): r for r in statuses}

        self.assertIn("101", by_number)
        self.assertIn("102", by_number)

        self.assertFalse(
            by_number["101"]["is_available"],
            msg="Room 101 should be unavailable (has Confirmed reservation today).",
        )

        self.assertTrue(
            by_number["102"]["is_available"],
            msg="Room 102 should be available (no non-cancelled reservation today).",
        )


if __name__ == "__main__":
    unittest.main()
