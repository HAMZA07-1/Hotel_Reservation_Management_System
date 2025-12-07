import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from database_manager import DatabaseManager
import sqlite3

db = DatabaseManager()

class BookingRecordsFrame(tk.Frame):
    def __init__(self, parent, controller: "HotelApp"):
        super().__init__(parent, bg="#395A7F")
        self.controller = controller

        # ttk style for table
        style = ttk.Style()
        style.configure("Treeview", font=("TkDefaultFont", 13), rowheight=30)
        style.configure("Treeview.Heading", font=("TkDefaultFont", 12, "bold"))

        # --------------------
        # FILTER BAR
        # --------------------
        filter_frame = tk.Frame(self, bg="#395A7F")
        filter_frame.pack(fill="x", pady=8)

        # Guest name search
        tk.Label(filter_frame, text="Guest:", bg="#395A7F", fg="white").pack(
            side="left", padx=(12, 4)
        )
        guest_var = tk.StringVar()
        guest_entry = tk.Entry(filter_frame, textvariable=guest_var, width=20)
        guest_entry.pack(side="left", padx=4)

        # Room number search
        tk.Label(filter_frame, text="Room#:", bg="#395A7F", fg="white").pack(
            side="left", padx=(12, 4)
        )
        room_var = tk.StringVar()
        room_entry = tk.Entry(filter_frame, textvariable=room_var, width=8)
        room_entry.pack(side="left", padx=4)

        # Status dropdown
        tk.Label(filter_frame, text="Status:", bg="#395A7F", fg="white").pack(
            side="left", padx=(12, 4)
        )
        status_var = tk.StringVar()
        status_dropdown = ttk.Combobox(
            filter_frame,
            textvariable=status_var,
            values=[
                "",
                "Confirmed",
                "Cancelled",
                "Checked-in",
                "Checked-out",
                "No-show",
            ],
            width=12,
            state="readonly",
        )
        status_dropdown.current(0)
        status_dropdown.pack(side="left", padx=4)

        # Filter button
        filter_btn = tk.Button(filter_frame, text="Filter", command=lambda: load_data())
        filter_btn.pack(side="right", padx=12)

        # Back button
        back_btn = tk.Button(
            filter_frame,
            text="Back",
            command=lambda: controller.show_frame("main_menu"),
        )
        back_btn.pack(side="right", padx=12)

        # ------------------------
        # TABLE SET UP
        # ------------------------
        columns = (
            "reservation_id",
            "guest_id",
            "guest_name",
            "room_id",
            "room_number",
            "check_in",
            "check_out",
            "total_price",
            "status",
        )

        tree = ttk.Treeview(self, columns=columns, show="headings", height=12)
        tree.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        headings = [
            "Res ID",
            "Guest ID",
            "Guest",
            "Room ID",
            "Room #",
            "Check-in",
            "Check-out",
            "Total",
            "Status",
        ]
        for col, head in zip(columns, headings):
            tree.heading(col, text=head)
            tree.column(col, width=100)

        # ------------------------
        # PAGINATION
        # ------------------------
        page_frame = tk.Frame(self, bg="#395A7F")
        page_frame.pack(fill="x", pady=6)

        current_page = tk.IntVar(value=1)
        rows_per_page = 12
        result_rows = []

        prev_btn = tk.Button(page_frame, text="<", command=lambda: change_page(-1))
        prev_btn.pack(side="left", padx=6)
        tk.Label(page_frame, text="Page", bg="#395A7F", fg="white").pack(side="left")

        page_entry = tk.Entry(page_frame, width=4, justify="center")
        page_entry.insert(0, "1")
        page_entry.pack(side="left", padx=6)

        max_page_label = tk.Label(page_frame, text="of 1", bg="#395A7F", fg="white")
        max_page_label.pack(side="left", padx=(6, 20))

        next_btn = tk.Button(page_frame, text=">", command=lambda: change_page(1))
        next_btn.pack(side="left")

        # ------------ pagination helpers ------------

        def change_page(amount):
            new_page = current_page.get() + amount
            max_page = max(1, (len(result_rows) - 1) // rows_per_page + 1)
            if 1 <= new_page <= max_page:
                current_page.set(new_page)
                update_page()

        def update_page():
            tree.delete(*tree.get_children())
            page = current_page.get()
            start = (page - 1) * rows_per_page
            end = start + rows_per_page
            for row in result_rows[start:end]:
                tree.insert("", tk.END, values=row)
            max_page = max(1, (len(result_rows) - 1) // rows_per_page + 1)
            page_entry.delete(0, tk.END)
            page_entry.insert(0, str(page))
            max_page_label.config(text=f"of {max_page}")

        def go_to_page(event=None):
            try:
                new_page = int(page_entry.get())
            except ValueError:
                page_entry.delete(0, tk.END)
                page_entry.insert(0, "1")
                return
            max_page = max(1, (len(result_rows) - 1) // rows_per_page + 1)
            new_page = max(1, min(new_page, max_page))
            current_page.set(new_page)
            update_page()

        page_entry.bind("<Return>", lambda e: go_to_page())

        # -------------------------------
        # DATA LOADING
        # -------------------------------
        def load_data():
            nonlocal result_rows
            result_rows = []
            conn = None
            try:
                conn = db.connect()
                conn.row_factory = sqlite3.Row
                cur = conn.cursor()

                query = (
                    "SELECT r.reservation_id, r.guest_id, "
                    "g.first_name || ' ' || g.last_name AS guest_name, "
                    "r.room_id, rm.room_number, r.check_in_date, "
                    "r.check_out_date, r.total_price, r.status "
                    "FROM reservations r "
                    "LEFT JOIN guests g ON r.guest_id = g.guest_id "
                    "LEFT JOIN rooms rm ON r.room_id = rm.room_id "
                    "WHERE 1=1"
                )
                params = []

                if guest_var.get().strip() != "":
                    query += " AND (g.first_name || ' ' || g.last_name) LIKE ?"
                    params.append(f"%{guest_var.get().strip()}%")

                if room_var.get().strip() != "":
                    query += " AND rm.room_number LIKE ?"
                    params.append(f"%{room_var.get().strip()}%")

                if status_var.get().strip() != "":
                    query += " AND r.status = ?"
                    params.append(status_var.get().strip())

                query += " ORDER BY r.check_in_date DESC"

                cur.execute(query, params)
                rows = cur.fetchall()

                result_rows = [
                    (
                        r[0],
                        r[1],
                        r[2] or "",
                        r[3],
                        r[4] or "",
                        r[5],
                        r[6],
                        f"{r[7]:.2f}"
                        if isinstance(r[7], (float, int))
                        else r[7],
                        r[8],
                    )
                    for r in rows
                ]

            except sqlite3.Error as e:
                msg = str(e).lower()
                if "no such table" in msg:
                    result_rows = []
                else:
                    print("Database error:", e)
            finally:
                if conn:
                    conn.close()

            current_page.set(1)
            update_page()

        # Make load_data accessible in refresh()
        self._load_data = load_data

        # ----------------------------------------
        # EDIT RESERVATION DIALOG
        # ----------------------------------------
        def open_edit_dialog(event=None):
            """Open edit dialog for selected reservation (double-click or button)."""
            selection = tree.selection()
            if not selection:
                messagebox.showwarning("No Selection", "Please select a reservation to edit.")
                return

            selected_item = selection[0]
            values = tree.item(selected_item, 'values')
            
            # values = (reservation_id, guest_id, guest_name, room_id, room_number, check_in, check_out, total_price, status)
            res_id = values[0]
            guest_name = values[2]
            room_num = values[4]
            check_in = values[5]
            check_out = values[6]
            current_status = values[8]

            # Create edit window
            edit_win = tk.Toplevel(self)
            edit_win.title(f"Edit Reservation #{res_id}")
            edit_win.geometry("400x350")
            edit_win.resizable(False, False)

            # Info labels
            tk.Label(edit_win, text=f"Reservation #{res_id}", font=("Arial", 12, "bold")).pack(pady=10)
            tk.Label(edit_win, text=f"Guest: {guest_name}").pack()
            tk.Label(edit_win, text=f"Room: {room_num}").pack()
            tk.Label(edit_win, text=f"Check-in: {check_in}").pack()
            tk.Label(edit_win, text=f"Check-out: {check_out}").pack(pady=(0, 20))

            # Status dropdown
            tk.Label(edit_win, text="Update Status:", font=("Arial", 10, "bold")).pack(anchor="w", padx=20)
            status_options = ["Confirmed", "Checked-in", "Checked-out", "Cancelled", "Paid", "Unpaid", "Late", "No-show"]
            status_var_edit = tk.StringVar(value=current_status)
            status_combo = ttk.Combobox(edit_win, textvariable=status_var_edit, values=status_options, state="readonly", width=30)
            status_combo.pack(pady=10, padx=20)

            # Buttons frame
            btn_frame = tk.Frame(edit_win)
            btn_frame.pack(pady=20)

            def save_changes():
                """Save the status update to the database."""
                new_status = status_var_edit.get()
                if new_status == current_status:
                    messagebox.showinfo("No Change", "Status unchanged.")
                    edit_win.destroy()
                    return

                try:
                    conn = db.connect()
                    cur = conn.cursor()
                    cur.execute(
                        "UPDATE reservations SET status = ? WHERE reservation_id = ?",
                        (new_status, res_id)
                    )
                    conn.commit()
                    conn.close()
                    messagebox.showinfo("Success", f"Reservation #{res_id} status updated to '{new_status}'.")
                    load_data()  # Refresh table
                    edit_win.destroy()
                except sqlite3.Error as e:
                    messagebox.showerror("Database Error", f"Failed to update reservation: {e}")

            def delete_reservation_confirm():
                """Delete the reservation after confirmation."""
                if messagebox.askyesno("Confirm Delete", f"Delete reservation #{res_id}? This cannot be undone."):
                    try:
                        conn = db.connect()
                        cur = conn.cursor()
                        cur.execute("DELETE FROM reservations WHERE reservation_id = ?", (res_id,))
                        conn.commit()
                        conn.close()
                        messagebox.showinfo("Success", f"Reservation #{res_id} deleted.")
                        load_data()  # Refresh table
                        edit_win.destroy()
                    except sqlite3.Error as e:
                        messagebox.showerror("Database Error", f"Failed to delete reservation: {e}")

            save_btn = tk.Button(btn_frame, text="Save Status", command=save_changes, bg="#4CAF50", fg="white", width=15)
            save_btn.pack(side="left", padx=5)

            delete_btn = tk.Button(btn_frame, text="Delete", command=delete_reservation_confirm, bg="#f44336", fg="white", width=10)
            delete_btn.pack(side="left", padx=5)

            close_btn = tk.Button(btn_frame, text="Close", command=edit_win.destroy, width=10)
            close_btn.pack(side="left", padx=5)

        # Bind double-click to open edit dialog
        tree.bind("<Double-1>", open_edit_dialog)

        # Initial load
        load_data()

        # Keyboard niceties: Enter on guest/room fields triggers filter
        guest_entry.bind("<Return>", lambda e: load_data())
        room_entry.bind("<Return>", lambda e: load_data())

    def refresh(self):
        """Called when this frame is shown."""
        if hasattr(self, "_load_data"):
            self._load_data()