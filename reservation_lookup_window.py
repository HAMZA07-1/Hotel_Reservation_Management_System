import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date

from database_manager import DatabaseManager
from hotel_manager import HotelManager

# make these once so we don't reconnect over and over
_db = DatabaseManager()
_hotel = HotelManager(_db)


def open_reservation_lookup_window(parent):
    """Tiny guest window to search & cancel a reservation."""

    win = tk.Toplevel(parent)
    win.title("Find My Reservation")
    win.geometry("820x460")
    win.configure(bg="#2C3E50")

    # ---------------- top search bar ----------------
    top = tk.Frame(win, bg="#2C3E50")
    top.pack(fill="x", padx=10, pady=10)

    tk.Label(top, text="Email:", bg="#2C3E50", fg="white").grid(
        row=0, column=0, sticky="e", padx=5, pady=5
    )
    email_var = tk.StringVar()
    email_entry = tk.Entry(top, textvariable=email_var, width=30)
    email_entry.grid(row=0, column=1, sticky="w", padx=5, pady=5)

    tk.Label(top, text="Reservation ID:", bg="#2C3E50", fg="white").grid(
        row=0, column=2, sticky="e", padx=5, pady=5
    )
    res_id_var = tk.StringVar()
    res_id_entry = tk.Entry(top, textvariable=res_id_var, width=10)
    res_id_entry.grid(row=0, column=3, sticky="w", padx=5, pady=5)

    # ---------------- results table ----------------
    cols = (
        "reservation_id",
        "guest_name",
        "email",
        "room_number",
        "check_in",
        "check_out",
        "status",
        "total_price",
    )

    tree = ttk.Treeview(win, columns=cols, show="headings", height=10)
    for c in cols:
        tree.heading(c, text=c.replace("_", " ").title())
        tree.column(c, anchor="center", width=90)

    tree.column("guest_name", width=140)
    tree.column("email", width=170)
    tree.pack(fill="both", expand=True, padx=10, pady=10)

    # ---------------- helpers ----------------
    def clear_rows():
        for item in tree.get_children():
            tree.delete(item)

    def do_search():
        clear_rows()

        email = email_var.get().strip()
        res_raw = res_id_var.get().strip()

        if not email and not res_raw:
            messagebox.showwarning("Missing Info", "Enter email and/or reservation ID.")
            return

        res_id = None
        if res_raw:
            try:
                res_id = int(res_raw)
            except ValueError:
                messagebox.showerror("Bad ID", "Reservation ID must be a number.")
                return

        try:
            rows = _hotel.search_reservation(
                reservation_id=res_id,
                email=email or None,
            )
        except Exception as ex:
            messagebox.showerror("Error", f"Search failed:\n{ex}")
            return

        if not rows:
            messagebox.showinfo("No Results", "No matching reservations were found.")
            return

        for r in rows:
            full_name = f"{r['first_name']} {r['last_name']}"
            price = float(r["total_price"] or 0.0)

            tree.insert(
                "",
                "end",
                values=(
                    r["reservation_id"],
                    full_name,
                    r["email"],
                    r["room_number"],
                    r["check_in_date"],
                    r["check_out_date"],
                    r["status"],
                    f"${price:.2f}",
                ),
            )

    def do_cancel():
        selected = tree.focus()
        if not selected:
            messagebox.showwarning("No Selection", "Click a reservation row first.")
            return

        vals = tree.item(selected, "values")
        if not vals:
            return

        res_id = int(vals[0])
        status = vals[6]
        check_in_str = vals[4]

        # Only allow guests to cancel future Confirmed reservations
        if status != "Confirmed":
            messagebox.showinfo(
                "Not Allowed",
                "Only reservations with status 'Confirmed' can be cancelled here.",
            )
            return

        try:
            ci = datetime.strptime(check_in_str, "%Y-%m-%d").date()
        except ValueError:
            ci = date.today()

        if ci <= date.today():
            messagebox.showinfo(
                "Too Late",
                "Check-in day has started or passed.\nPlease contact the front desk.",
            )
            return

        if not messagebox.askyesno("Confirm", "Cancel this reservation?"):
            return

        try:
            receipt = _hotel.cancel_reservation(res_id)
        except Exception as ex:
            messagebox.showerror("Error", f"Cancellation failed:\n{ex}")
            return

        msg = (
            f"Reservation {receipt['reservation_id']} cancelled.\n\n"
            f"Original Price: ${receipt['original_price']:.2f}\n"
            f"Cancellation Fee: ${receipt['cancellation_fee']:.2f}\n"
            f"Refund: ${receipt['refund_amount']:.2f}\n"
            f"Reason: {receipt['reason']}"
        )
        messagebox.showinfo("Cancelled", msg)
        do_search()  # refresh

    # bottom buttons
    bottom = tk.Frame(win, bg="#2C3E50")
    bottom.pack(fill="x", padx=10, pady=8)

    tk.Button(bottom, text="Search", width=12, command=do_search).pack(
        side="left", padx=5
    )
    tk.Button(
        bottom, text="Cancel Reservation", width=18, command=do_cancel
    ).pack(side="left", padx=5)
    tk.Button(bottom, text="Close", width=10, command=win.destroy).pack(
        side="right", padx=5
    )

    # quick enter bindings
    email_entry.bind("<Return>", lambda e: do_search())
    res_id_entry.bind("<Return>", lambda e: do_search())

    return win
