"""
Module: reservation_window.py
Date: 11/12/2025
Programmer: hamza

Description:
This module defines the 'Reservations' window of the application, which allows users to view, add, update, and
cancel reservations. It is built using Tkinter and the ttk.Treeview widget for displaying data in a table.

Important Functions:
- open_reservation_window(parent, db): The main function to create and display the reservation window.
  Input: parent (tk.Widget), db (DatabaseManager).
  Output: None.
- refresh_data(): Clears the reservations table and reloads it by calling `db.view_reservations()`. This ensures
  the displayed data is up-to-date.
  Input: None.
  Output: None.
- add_reservation(): Reads data from the form entry fields and calls `db.add_reservation()` to create a new
  record, then refreshes the table.
  Input: None.
  Output: None.
- update_reservation(): Updates the selected reservation in the table with the data from the form fields.
  Input: None.
  Output: None.
- cancel_reservation(): Marks the selected reservation's status as 'Cancelled'.
  Input: None.
  Output: None.
- on_select(event): An event handler that auto-fills the form fields with the data from the reservation
  selected in the table, making it easy to view or update.
  Input: event (tk.Event).
  Output: None.

Important Data Structures:
- table (ttk.Treeview): The central widget used to display the reservation data in a structured, tabular format.
"""
import tkinter as tk
from tkinter import ttk, messagebox

def open_reservation_window(parent, db):
    win = tk.Toplevel(parent)
    win.title("Reservations")
    win.geometry("850x550")
    win.config(bg="#2C3E50")  # matching theme

    tk.Label(
        win, text="Reservations",
        bg="#2C3E50", fg="white",
        font=("Arial", 18, "bold")
    ).pack(pady=10)

    # ---------------------------
    # ----- TABLE -----
    # ---------------------------
    cols = ("ID", "Guest", "Room", "Check-In", "Check-Out", "Total Price", "Status")
    table = ttk.Treeview(win, columns=cols, show="headings")

    for c in cols:
        table.heading(c, text=c)
        table.column(c, width=110, anchor="center")

    table.pack(pady=10, fill="both", expand=True)

    # ---------------------------
    # ----- REFRESH -----
    # ---------------------------
    def refresh_data():
        for i in table.get_children():
            table.delete(i)

        data = db.view_reservations()
        for row in data:
            table.insert(
                "",
                "end",
                values=(
                    row["reservation_id"],
                    row["guest_name"],
                    row["room_number"],
                    row["check_in_date"],
                    row["check_out_date"],
                    row["total_price"],
                    row["status"]
                )
            )

    tk.Button(win, text="Refresh Table", command=refresh_data).pack(pady=5)

    # ---------------------------
    # ----- FORM -----
    # ---------------------------
    form = tk.Frame(win, bg="#34495E", padx=15, pady=15)
    form.pack(pady=10)

    labels = ["Guest ID:", "Room ID:", "Check-In:", "Check-Out:", "Total Price:", "Status:"]
    entries = []

    for i, text in enumerate(labels):
        tk.Label(form, text=text, fg="white", bg="#34495E").grid(row=i, column=0, pady=5, sticky="e")
        entry = tk.Entry(form, width=15)
        entry.grid(row=i, column=1, pady=5, padx=10)
        entries.append(entry)

    guest_entry, room_entry, checkin_entry, checkout_entry, price_entry, status_entry = entries

    # ---------------------------
    # ----- ADD -----
    # ---------------------------
    def add_reservation():
        try:
            g = int(guest_entry.get())
            r = int(room_entry.get())
            total = float(price_entry.get())
            db.add_reservation(g, r, checkin_entry.get(), checkout_entry.get(), total, status_entry.get())
            refresh_data()
            messagebox.showinfo("Added", "Reservation added successfully!")
        except Exception as e:
            messagebox.showerror("Error", e)

    tk.Button(form, text="Add Reservation", width=15, command=add_reservation).grid(row=6, column=0, pady=10)

    # ---------------------------
    # ----- UPDATE -----
    # ---------------------------
    def update_reservation():
        sel = table.focus()
        if not sel:
            messagebox.showwarning("No selection", "Select a reservation first.")
            return
        rid = int(table.item(sel, "values")[0])
        db.update_reservation(
            rid,
            checkin_entry.get(),
            checkout_entry.get(),
            float(price_entry.get()),
            status_entry.get(),
        )
        refresh_data()

    tk.Button(form, text="Update Reservation", width=15, command=update_reservation).grid(row=6, column=1, pady=10)

    # ---------------------------
    # ----- CANCEL -----
    # ---------------------------
    def cancel_reservation():
        sel = table.focus()
        if not sel:
            return
        rid = int(table.item(sel, "values")[0])
        db.cancel_reservation(rid, guest_id=1)
        refresh_data()

    tk.Button(form, text="Cancel Reservation", width=15, command=cancel_reservation).grid(row=7, column=0, columnspan=2, pady=10)

    # ---------------------------
    # ----- AUTO-FILL -----
    # ---------------------------
    def on_select(event):
        sel = table.focus()
        if not sel:
            return
        v = table.item(sel, "values")

        guest_entry.delete(0, tk.END); guest_entry.insert(0, v[1])
        room_entry.delete(0, tk.END); room_entry.insert(0, v[2])
        checkin_entry.delete(0, tk.END); checkin_entry.insert(0, v[3])
        checkout_entry.delete(0, tk.END); checkout_entry.insert(0, v[4])
        price_entry.delete(0, tk.END); price_entry.insert(0, v[5])
        status_entry.delete(0, tk.END); status_entry.insert(0, v[6])

    table.bind("<<TreeviewSelect>>", on_select)

    refresh_data()
