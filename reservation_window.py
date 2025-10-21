import tkinter as tk
from tkinter import ttk, messagebox
from database_manager import DatabaseManager

# setup db object for running queries
db = DatabaseManager()

def open_reservation_window(parent):
    """Opens the window that lets you view and add reservations."""

    win = tk.Toplevel(parent)
    win.title("Reservations")
    win.geometry("750x500")
    win.config(bg="#395A7F")

    # ---------- Table to show reservations ----------
    cols = ("ID", "Guest", "Room", "Check-In", "Check-Out", "Total Price", "Status")
    table = ttk.Treeview(win, columns=cols, show="headings")

    for c in cols:
        table.heading(c, text=c)
        table.column(c, width=95, anchor="center")

    table.pack(pady=20, fill="both", expand=True)

    # ---------- Function to refresh table ----------
    def refresh_data():
        for i in table.get_children():
            table.delete(i)
        try:
            data = db.get_all_reservations()
            for row in data:
                table.insert("", "end", values=row)
        except Exception as e:
            print("Error loading reservations:", e)

    refresh_data()

    # ---------- Input form for adding reservations ----------
    form = tk.Frame(win, bg="#395A7F")
    form.pack(pady=10)

    tk.Label(form, text="Guest ID:", bg="#395A7F", fg="white").grid(row=0, column=0, padx=5, pady=5)
    guest_entry = tk.Entry(form, width=10)
    guest_entry.grid(row=0, column=1)

    tk.Label(form, text="Room ID:", bg="#395A7F", fg="white").grid(row=0, column=2, padx=5)
    room_entry = tk.Entry(form, width=10)
    room_entry.grid(row=0, column=3)

    tk.Label(form, text="Check-In:", bg="#395A7F", fg="white").grid(row=1, column=0, padx=5, pady=5)
    checkin_entry = tk.Entry(form, width=12)
    checkin_entry.grid(row=1, column=1)

    tk.Label(form, text="Check-Out:", bg="#395A7F", fg="white").grid(row=1, column=2)
    checkout_entry = tk.Entry(form, width=12)
    checkout_entry.grid(row=1, column=3)

    tk.Label(form, text="Total Price:", bg="#395A7F", fg="white").grid(row=2, column=0, padx=5, pady=5)
    price_entry = tk.Entry(form, width=12)
    price_entry.grid(row=2, column=1)

    tk.Label(form, text="Status:", bg="#395A7F", fg="white").grid(row=2, column=2)
    status_entry = tk.Entry(form, width=12)
    status_entry.grid(row=2, column=3)

    # ---------- Add reservation ----------
    def add_reservation():
        try:
            g_id = int(guest_entry.get())
            r_id = int(room_entry.get())
            total = float(price_entry.get())
            check_in = checkin_entry.get()
            check_out = checkout_entry.get()
            status = status_entry.get()

            db.add_reservation(g_id, r_id, check_in, check_out, total, status)
            db.change_room_status(r_id, 0)

            messagebox.showinfo("Added", "Reservation added successfully!")
            refresh_data()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add reservation:\n{e}")

    # ---------- Buttons ----------
    tk.Button(win, text="Add Reservation", command=add_reservation).pack(pady=8)
    tk.Button(win, text="Refresh Table", command=refresh_data).pack(pady=4)
