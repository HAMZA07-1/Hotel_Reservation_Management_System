import sqlite3
import random
from datetime import date, timedelta, datetime
import string

DB_PATH = "hotel.db"
# -------------------------------------
# Helper functions
# -------------------------------------
def random_name():
    first = random.choice([
        "Daniel","Sarah","Michael","Emily","Joshua","Laura","David","Olivia","Ethan","Sophia",
        "James","Emma","Ryan","Grace","Matthew","Hannah","Andrew","Chloe","Noah","Ava"
    ])
    last = random.choice([
        "Johnson","Miller","Smith","Anderson","Brown","Davis","Wilson","Moore","Taylor","Clark",
        "Martin","Walker","Hall","Young","King","Allen","Wright","Scott","Green","Baker"
    ])
    return first, last

def random_email(first, last):
    domains = ["gmail.com", "yahoo.com", "outlook.com", "example.com"]
    return f"{first.lower()}.{last.lower()}{random.randint(1,999)}@{random.choice(domains)}"

def random_phone():
    return f"({random.randint(200,999)})-{random.randint(200,999)}-{random.randint(1000,9999)}"

def random_address():
    street_num = random.randint(100,9999)
    street_name = random.choice(["Oak St", "Pine Ave", "Maple Dr", "Cedar Ln", "Lakeview Rd"])
    city = random.choice(["Springfield", "Rivertown", "Hillcrest", "Lakeside", "Fairview"])
    state = random.choice(["CA","NY","TX","FL","WA","OR","NV","IL"])
    postal = f"{random.randint(10000,99999)}"
    return f"{street_num} {street_name}", "", city, state, postal

def random_reservation_dates():
    """
    Returns (check_in, check_out, nights)
    Mix of past, today, and future stays.
    """
    # Random start between 60 days ago and 60 days ahead
    start_offset = random.randint(-60, 60)
    nights = random.randint(1, 7)
    check_in = date.today() + timedelta(days=start_offset)
    check_out = check_in + timedelta(days=nights)
    return check_in, check_out, nights

def random_status(check_in, check_out):
    today = date.today()

    if check_out < today:
        return random.choice(["Complete", "Cancelled"])
    if check_in > today:
        return "Confirmed"
    if check_in <= today <= check_out:
        return random.choice(["Checked-in", "Late", "Late Check-out"])
    return "Confirmed"

def random_payment_status(status):
    if status in ["Cancelled"]:
        return 0
    if status in ["Complete"]:
        return 1
    return random.choice([0,1])

# -------------------------------------------------
# Main population logic
# -------------------------------------------------
def populate_database():

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Fetch room_ids to assign reservations to
    try:
        cur.execute("SELECT room_id FROM rooms")
        rooms = [row[0] for row in cur.fetchall()]
    except sqlite3.OperationalError:
        print("ERROR: 'rooms' table not found.")
        return

    if not rooms:
        print("ERROR: No rooms found in database. Add rooms first.")
        return

    print(f"Found {len(rooms)} rooms.")

    # ---------------------------------------------------
    # Define required status quotas
    # ---------------------------------------------------
    required_statuses = (
        ["Checked-in"] * 20 +
        ["Late"] * 5 +
        ["Late Check-out"] * 5
    )

    # Fill the remaining reservations with randomized statuses
    other_status_pool = ["Confirmed", "Cancelled", "Complete"]
    remaining_count = 50 - len(required_statuses)

    required_statuses += [random.choice(other_status_pool) for _ in range(remaining_count)]
    random.shuffle(required_statuses)

    # ---------------------------------------------------
    # Create 50 Guests + Reservations
    # ---------------------------------------------------
    for status in required_statuses:

        # -------------------------
        # Insert Guest
        # -------------------------
        first, last = random_name()
        email = random_email(first, last)
        phone = random_phone()
        addr1, addr2, city, state, postal = random_address()

        cur.execute("""
            INSERT INTO guests (first_name, last_name, email, phone_number,
                                address_line1, address_line2, city, state, postal_code)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (first, last, email, phone, addr1, addr2, city, state, postal))

        guest_id = cur.lastrowid

        # -------------------------
        # Insert Reservation
        # -------------------------
        room_id = random.choice(rooms)

        # Date logic tied to required status
        today = date.today()

        if status == "Checked-in":
            # Stay happening right now
            check_in = today - timedelta(days=random.randint(0, 2))
            check_out = today + timedelta(days=random.randint(1, 4))

        elif status == "Late":
            # Should have checked in yesterday or earlier
            check_in = today - timedelta(days=random.randint(1, 3))
            check_out = check_in + timedelta(days=random.randint(1, 5))

        elif status == "Late Check-out":
            # Stay ended but checkout overdue
            check_in = today - timedelta(days=random.randint(3, 6))
            check_out = today - timedelta(days=random.randint(0, 1))  # technically should be gone by now

        else:
            # Other statuses: random past or future
            check_in, check_out, _ = random_reservation_dates()

        nights = (check_out - check_in).days
        nightly_rate = random.randint(80, 300)
        total_price = nightly_rate * nights

        # Payment logic
        if status in ["Complete"]:
            is_paid = 1
        elif status in ["Cancelled"]:
            is_paid = 0
        else:
            is_paid = random.choice([0, 1])

        reservation_id = random.randint(100000, 999999)

        cur.execute("""
            INSERT INTO reservations (
                reservation_id, guest_id, room_id,
                check_in_date, check_out_date,
                num_guests, total_price,
                status, is_paid
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            reservation_id, guest_id, room_id,
            check_in.isoformat(), check_out.isoformat(),
            random.randint(1, 4), total_price,
            status, is_paid
        ))

    conn.commit()
    conn.close()

    print("Successfully inserted 50 structured demo reservations!")



if __name__ == "__main__":
    populate_database()
