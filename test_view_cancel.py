"""
Module: test_view_cancel.py
Date: 11/12/2025
Programmer(s): Hamza

Brief Description:
This is a simple, procedural script used for manual integration testing. It focuses on verifying two core functions of the `DatabaseManager`: viewing all reservations and canceling a specific reservation.

Important Functions:
- main() -> None
  - Input: None
  - Output: Prints results to the console.
  - Description: The function first calls `db.view_reservations()` and prints the number of results found. It then attempts to cancel a reservation with a hardcoded ID (`reservation_id=1`) by calling `db.cancel_reservation()` and prints whether the operation was successful.

Important Data Structures:
- N/A

Algorithms:
- N/A. This script is a basic manual test case and does not contain complex algorithms. It's useful for quick, ad-hoc verification during development.
"""

from database_manager import DatabaseManager

def main():
    db = DatabaseManager("hotel.db")

    # ---------------------------
    # Step 1: View all reservations
    # ---------------------------
    print("=== TEST: View Reservations ===")
    rows = db.view_reservations()
    if not rows:
        print("No reservations found in the database yet.")
    else:
        print(f"Found {len(rows)} reservations.")
        print(dict(rows[0]))  # print first row keys and values

    # ---------------------------
    # Step 2: Attempt to cancel a reservation (example id)
    # ---------------------------
    print("\n=== TEST: Cancel Reservation ===")
    success = db.cancel_reservation(reservation_id=1, guest_id=1)
    print("Cancel result:", success)

if __name__ == "__main__":
    main()
