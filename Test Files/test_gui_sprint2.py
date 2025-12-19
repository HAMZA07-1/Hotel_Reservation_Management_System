"""
Module: test_gui_sprint2.py
Date: 11/12/2025
Programmer(s): Hamza

Brief Description:
This is a simple integration test script, not a formal unit test. Its purpose is to manually verify the functionality of the `cancel_reservation` and `update_reservation` methods in the `DatabaseManager`. It simulates a sequence of operations that might occur during application use.

Important Functions:
- The script runs procedurally without a main function. It:
  1. Instantiates `DatabaseManager`.
  2. Prints all existing reservations.
  3. Calls `cancel_reservation()` for a specific reservation.
  4. Calls `update_reservation()` for another reservation.
  5. Prints the list of reservations again to show the final state.
  - Input: None (uses hardcoded IDs and data).
  - Output: Prints results to the console.

Important Data Structures:
- N/A

Algorithms:
- N/A. This is a straightforward script for manual, command-line-based testing.
"""

from database_manager import DatabaseManager

db = DatabaseManager("hotel.db")

print("[TEST] All reservations:")
for row in db.view_reservations():
    print(dict(row))

print("\n[TEST] Canceling reservation 1...")
db.cancel_reservation(1, 1)

print("\n[TEST] Updating reservation 2...")
db.update_reservation(2, "2025-11-20", "2025-11-22", 400.0, "Checked-in")

print("\n[TEST] Final Reservations:")
for row in db.view_reservations():
    print(dict(row))
