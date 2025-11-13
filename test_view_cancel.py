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
