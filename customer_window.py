import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from typing import Optional
import subprocess
import sys
from pathlib import Path

from database_manager import DatabaseManager
from hotel_manager import HotelManager

# Create default instances if caller doesn't pass them
_default_db = None
_default_hotel = None


def _ensure_services(db: Optional[DatabaseManager], hotel: Optional[HotelManager]):
    global _default_db, _default_hotel
    if db is None:
        if _default_db is None:
            _default_db = DatabaseManager()
        db = _default_db
    if hotel is None:
        if _default_hotel is None:
            _default_hotel = HotelManager(db)
            db.hotel_manager = _default_hotel
        hotel = _default_hotel
    return db, hotel


def open_customer_window(parent: tk.Widget = None,
                         db: DatabaseManager | None = None,
                         hotel: HotelManager | None = None,
                         guest_id: int | None = None,
                         guest_email: str | None = None):
    """
    Customer-facing window.

    - If `parent` is provided the view will render inside and replace children.
    - Otherwise a Toplevel window is created.
    - Optionally pass `guest_id` or `guest_email` to pre-select a guest.
    """
    db, hotel = _ensure_services(db, hotel)

    # choose container
    is_standalone = parent is None
    if parent is not None:
        for w in parent.winfo_children():
            w.destroy()
        container = parent
        container.config(bg="#395A7F")
    else:
        container = tk.Toplevel()
        container.title("Customer - My Reservations")
        container.geometry("980x640")
        container.config(bg="#395A7F")

    # UI style
    style = ttk.Style()
    style.configure("Treeview", rowheight=26)

    # Title
    tk.Label(container, text="Customer Portal", bg="#395A7F", fg="white", font=("Arial", 18, "bold")).pack(pady=(12, 6))

    # --- Top: identity/search ---
    identity_frame = tk.Frame(container, bg="#395A7F")
    identity_frame.pack(fill="x", padx=12, pady=(0, 8))

    guest_id_var = tk.StringVar(value=str(guest_id) if guest_id else "")
    guest_email_var = tk.StringVar(value=guest_email or "")

    def load_guest_from_inputs():
        nonlocal guest_id
        gid = guest_id_var.get().strip()
        gemail = guest_email_var.get().strip()
        if gid:
            try:
                guest_id = int(gid)
            except ValueError:
                messagebox.showwarning("Invalid ID", "Guest ID must be an integer.")
                return
        elif gemail:
            try:
                row = db.get_guest(email=gemail)
            except Exception as e:
                messagebox.showerror("Database Error", str(e))
                return
            if not row:
                messagebox.showinfo("Not Found", "No guest with that email.")
                guest_id = None
                return
            guest_id = int(row["guest_id"])
        else:
            messagebox.showinfo("Enter Info", "Enter Guest ID or Email to continue.")
            return
        # update guest label and load reservations
        try:
            grow = db.get_guest(guest_id=guest_id)
            if grow:
                guest_display_label.config(text=f"{grow['first_name']} {grow['last_name']} (ID {grow['guest_id']})")
            else:
                guest_display_label.config(text=f"Guest ID {guest_id}")
        except Exception:
            guest_display_label.config(text=f"Guest ID {guest_id}")
        load_reservations()

    if guest_id is None:
        tk.Label(identity_frame, text="Email:", bg="#395A7F", fg="white").pack(side="left", padx=(6,4))
        tk.Entry(identity_frame, textvariable=guest_email_var, width=28).pack(side="left", padx=4)
        tk.Label(identity_frame, text="or ID:", bg="#395A7F", fg="white").pack(side="left", padx=(10,4))
        tk.Entry(identity_frame, textvariable=guest_id_var, width=8).pack(side="left", padx=4)
        tk.Button(identity_frame, text="Load My Reservations", command=load_guest_from_inputs).pack(side="left", padx=10)
    else:
        # show guest info if preloaded
        try:
            grow = db.get_guest(guest_id=guest_id)
            gd = f"{grow['first_name']} {grow['last_name']} (ID {grow['guest_id']})" if grow else f"Guest ID {guest_id}"
        except Exception:
            gd = f"Guest ID {guest_id}"
        tk.Label(identity_frame, text=f"Showing reservations for: {gd}", bg="#395A7F", fg="white", font=("Arial", 10, "bold")).pack(side="left", padx=8)

    # If running standalone, show an "Employee Login" button (launches staff main app)
    def _launch_employee_app():
        # locate Single Screen Prototype main.py relative to repo root (this file's parent)
        main_path = Path(__file__).resolve().parent / "Single Screen Prototype" / "main.py"
        if not main_path.exists():
            messagebox.showerror("Not found", f"Could not find staff app at:\n{main_path}")
            return
        try:
            subprocess.Popen([sys.executable, str(main_path)])
        except Exception as e:
            messagebox.showerror("Launch failed", f"Failed to start staff app:\n{e}")
            return
        # Close this window after launching staff app
        try:
            top = container.winfo_toplevel()
            top.destroy()
        except Exception:
            pass

    guest_display_label = tk.Label(container, text="No guest loaded", bg="#395A7F", fg="white")
    guest_display_label.pack(anchor="w", padx=14)

    if is_standalone:
        # place login button aligned to top-right area
        btn_frame = tk.Frame(container, bg="#395A7F")
        btn_frame.pack(fill="x", padx=12, pady=(4, 6))
        emp_btn = tk.Button(btn_frame, text="Employee Login", command=_launch_employee_app, bg="#34495E", fg="white")
        emp_btn.pack(side="right")

    # --- Middle: reservations table ---
    cols = ("reservation_id", "room_number", "check_in", "check_out", "total_price", "status")
    tree = ttk.Treeview(container, columns=cols, show="headings", height=10)
    tree.pack(fill="both", expand=False, padx=12, pady=(8,6))

    headings = ["Res ID", "Room #", "Check-in", "Check-out", "Total", "Status"]
    widths = [90, 100, 120, 120, 110, 120]
    for col, h, w in zip(cols, headings, widths):
        tree.heading(col, text=h)
        tree.column(col, width=w, anchor="center")

    # Buttons under table
    table_btns = tk.Frame(container, bg="#395A7F")
    table_btns.pack(fill="x", padx=12, pady=(0,8))
    tk.Button(table_btns, text="Refresh", command=lambda: load_reservations()).pack(side="left", padx=6)
    tk.Button(table_btns, text="View Details", command=lambda: open_details_dialog()).pack(side="left", padx=6)
    tk.Button(table_btns, text="Cancel Selected Reservation", command=lambda: cancel_selected()).pack(side="left", padx=6)

    # --- Bottom: new reservation form ---
    form_frame = tk.LabelFrame(container, text="Create New Reservation", bg="#395A7F", fg="white", padx=10, pady=8)
    form_frame.pack(fill="x", padx=12, pady=(6,12))

    checkin_var = tk.StringVar()
    checkout_var = tk.StringVar()
    num_guests_var = tk.StringVar(value="1")
    available_rooms_var = tk.StringVar()
    selected_room_id_var = tk.StringVar()

    # Row 0
    tk.Label(form_frame, text="Check-in (YYYY-MM-DD):", bg="#395A7F", fg="white").grid(row=0, column=0, sticky="e", padx=6, pady=6)
    tk.Entry(form_frame, textvariable=checkin_var, width=14).grid(row=0, column=1, sticky="w", padx=6, pady=6)

    tk.Label(form_frame, text="Check-out (YYYY-MM-DD):", bg="#395A7F", fg="white").grid(row=0, column=2, sticky="e", padx=6, pady=6)
    tk.Entry(form_frame, textvariable=checkout_var, width=14).grid(row=0, column=3, sticky="w", padx=6, pady=6)

    # Row 1
    tk.Label(form_frame, text="Number of guests:", bg="#395A7F", fg="white").grid(row=1, column=0, sticky="e", padx=6, pady=6)
    tk.Entry(form_frame, textvariable=num_guests_var, width=6).grid(row=1, column=1, sticky="w", padx=6, pady=6)

    tk.Label(form_frame, text="Available Rooms:", bg="#395A7F", fg="white").grid(row=1, column=2, sticky="e", padx=6, pady=6)
    rooms_combo = ttk.Combobox(form_frame, textvariable=available_rooms_var, values=[], width=30, state="readonly")
    rooms_combo.grid(row=1, column=3, sticky="w", padx=6, pady=6)

    # Row 2 buttons
    tk.Button(form_frame, text="Search Available Rooms", command=lambda: search_available_rooms()).grid(row=2, column=1, padx=6, pady=8)
    tk.Button(form_frame, text="Book Selected Room", command=lambda: book_selected_room()).grid(row=2, column=3, padx=6, pady=8, sticky="e")

    # internal state
    result_rows = []
    rooms_lookup = {}  # display -> room_id

    def load_reservations():
        nonlocal result_rows
        result_rows = []
        tree.delete(*tree.get_children())
        if guest_id is None:
            return
        conn = None
        try:
            conn = db.connect()
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute("""
                SELECT r.reservation_id, rm.room_number, r.check_in_date, r.check_out_date, r.total_price, r.status
                FROM reservations r
                LEFT JOIN rooms rm ON r.room_id = rm.room_id
                WHERE r.guest_id = ?
                ORDER BY r.check_in_date DESC
            """, (guest_id,))
            rows = cur.fetchall()
            result_rows = [
                (
                    r["reservation_id"],
                    r["room_number"] or "",
                    r["check_in_date"],
                    r["check_out_date"],
                    f"{r['total_price']:.2f}" if isinstance(r["total_price"], (int, float)) else (r["total_price"] or ""),
                    r["status"] or ""
                )
                for r in rows
            ]
            for r in result_rows:
                tree.insert("", tk.END, values=r)
        except sqlite3.Error as e:
            msg = str(e).lower()
            if "no such table" in msg:
                # treat as no reservations
                return
            messagebox.showerror("Database Error", str(e))
        finally:
            if conn:
                conn.close()

    def get_selected_reservation_id():
        sel = tree.focus()
        if not sel:
            return None
        vals = tree.item(sel, "values")
        if not vals:
            return None
        try:
            return int(vals[0])
        except Exception:
            return None

    def open_details_dialog():
        rid = get_selected_reservation_id()
        if rid is None:
            messagebox.showinfo("No selection", "Select a reservation first.")
            return
        conn = None
        try:
            conn = db.connect()
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute("""
                SELECT r.reservation_id, g.first_name || ' ' || g.last_name AS guest_name,
                       rm.room_number, r.check_in_date, r.check_out_date, r.total_price, r.status
                FROM reservations r
                LEFT JOIN guests g ON r.guest_id = g.guest_id
                LEFT JOIN rooms rm ON r.room_id = rm.room_id
                WHERE r.reservation_id = ?
            """, (rid,))
            row = cur.fetchone()
            if not row:
                messagebox.showerror("Not found", "Reservation not found.")
                return
            dlg = tk.Toplevel(container)
            dlg.title(f"Reservation {row['reservation_id']}")
            dlg.transient(container)
            dlg.grab_set()
            dlg.config(bg="#34495E")
            padx = 12; pady = 8
            tk.Label(dlg, text=f"Reservation ID: {row['reservation_id']}", bg="#34495E", fg="white").pack(anchor="w", padx=padx, pady=(pady,0))
            tk.Label(dlg, text=f"Guest: {row['guest_name']}", bg="#34495E", fg="white").pack(anchor="w", padx=padx, pady=(0,pady))
            tk.Label(dlg, text=f"Room #: {row['room_number']}", bg="#34495E", fg="white").pack(anchor="w", padx=padx, pady=(0,pady))
            tk.Label(dlg, text=f"Check-in: {row['check_in_date']}", bg="#34495E", fg="white").pack(anchor="w", padx=padx, pady=(0,pady))
            tk.Label(dlg, text=f"Check-out: {row['check_out_date']}", bg="#34495E", fg="white").pack(anchor="w", padx=padx, pady=(0,pady))
            tk.Label(dlg, text=f"Total: {row['total_price']}", bg="#34495E", fg="white").pack(anchor="w", padx=padx, pady=(0,pady))
            tk.Label(dlg, text=f"Status: {row['status']}", bg="#34495E", fg="white").pack(anchor="w", padx=padx, pady=(0,pady))
            tk.Button(dlg, text="Close", command=dlg.destroy).pack(pady=(8,12))
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", str(e))
        finally:
            if conn:
                conn.close()

    def cancel_selected():
        rid = get_selected_reservation_id()
        if rid is None:
            messagebox.showinfo("No selection", "Select a reservation first.")
            return
        if guest_id is None:
            messagebox.showwarning("Not authorized", "You must identify yourself to cancel your reservation.")
            return
        if not messagebox.askyesno("Confirm Cancel", "Cancel selected reservation?"):
            return
        try:
            # Use HotelManager.cancel_reservation which applies policy and returns receipt dict
            receipt = hotel.cancel_reservation(rid)
        except Exception as e:
            messagebox.showerror("Cancel Failed", str(e))
            return
        # Show summary to customer
        msg = (f"Reservation {receipt['reservation_id']} cancelled.\n"
               f"Cancellation fee: {receipt['cancellation_fee']:.2f}\n"
               f"Refund amount: {receipt['refund_amount']:.2f}\n"
               f"Reason: {receipt.get('reason','')}")
        messagebox.showinfo("Cancelled", msg)
        load_reservations()

    def search_available_rooms():
        nonlocal rooms_lookup
        rooms_lookup = {}
        rooms_combo['values'] = []
        # validate dates
        ci = checkin_var.get().strip()
        co = checkout_var.get().strip()
        try:
            ng = int(num_guests_var.get().strip())
            if ng <= 0:
                raise ValueError()
        except Exception:
            messagebox.showwarning("Invalid guests", "Enter number of guests as a positive integer.")
            return
        if not ci or not co:
            messagebox.showwarning("Enter dates", "Enter check-in and check-out dates in YYYY-MM-DD format.")
            return
        try:
            rooms = hotel.search_rooms(check_in=ci, check_out=co, num_guests=ng, availability="free", sort_by="price", sort_dir="asc")
        except Exception as e:
            messagebox.showerror("Search Error", str(e))
            return
        displays = []
        for r in rooms:
            # HotelManager.search_rooms returns sqlite3.Row (room fields), get room_id and room_number and price
            rid = r["room_id"]
            rnum = r.get("room_number", str(rid))
            price = r.get("price", "")
            display = f"{rnum} — ID:{rid} — ${price:.2f}" if isinstance(price, (int, float)) else f"{rnum} — ID:{rid}"
            rooms_lookup[display] = rid
            displays.append(display)
        if not displays:
            messagebox.showinfo("No rooms", "No available rooms match your criteria.")
            return
        rooms_combo['values'] = displays
        rooms_combo.current(0)

    def book_selected_room():
        if guest_id is None:
            messagebox.showwarning("Identify yourself", "You must identify (Guest ID or Email) before booking.")
            return
        sel = rooms_combo.get()
        if not sel:
            messagebox.showinfo("Choose room", "Select an available room first.")
            return
        try:
            rid = int(rooms_lookup[sel])
        except Exception:
            messagebox.showerror("Invalid room", "Selected room could not be parsed.")
            return
        ci = checkin_var.get().strip()
        co = checkout_var.get().strip()
        try:
            ng = int(num_guests_var.get().strip())
        except Exception:
            messagebox.showwarning("Invalid guests", "Enter number of guests as a positive integer.")
            return
        # Reserve via HotelManager for transactional safety
        try:
            new_res_id = hotel.reserve_room(guest_id=guest_id, room_id=rid, check_in=ci, check_out=co, num_guests=ng)
        except Exception as e:
            messagebox.showerror("Booking Failed", str(e))
            return
        messagebox.showinfo("Booked", f"Reservation created (ID {new_res_id}).")
        # refresh reservations
        load_reservations()

    # initial load if guest_id pre-supplied
    if guest_id is not None:
        try:
            grow = db.get_guest(guest_id=guest_id)
            if grow:
                guest_display_label.config(text=f"{grow['first_name']} {grow['last_name']} (ID {grow['guest_id']})")
        except Exception:
            pass
        load_reservations()

    return container


if __name__ == "__main__":
    # Create a hidden root window, open the customer UI as a standalone Toplevel
    root = tk.Tk()
    root.withdraw()
    open_customer_window(parent=None)
    root.mainloop()