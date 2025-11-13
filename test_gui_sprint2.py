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
