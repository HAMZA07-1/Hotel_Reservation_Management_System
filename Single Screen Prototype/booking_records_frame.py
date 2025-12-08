import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from database_manager import DatabaseManager
import sqlite3
import calendar
from datetime import date

db = DatabaseManager()

class BookingRecordsFrame(tk.Frame):
    def __init__(self, parent, controller: "HotelApp"):
        super().__init__(parent, bg="#2C3E50")
        self.controller = controller

        # ttk style for table
        style = ttk.Style()
        style.configure("Treeview", font=("TkDefaultFont", 13), rowheight=30)
        style.configure("Treeview.Heading", font=("TkDefaultFont", 12, "bold"))

        # Title
        title_label = tk.Label(
            self,
            text="Booking Records",
            bg="#2C3E50",
            fg="white",
            font=("Arial", 30, "bold")
        )
        title_label.pack(pady=(10, 5))

        # -----------------------
        # Filter variables (instance attributes)
        # -----------------------
        self.guest_var = tk.StringVar()
        self.room_var = tk.StringVar()
        self.status_var = tk.StringVar()

        self.ci_year_var = tk.StringVar()
        self.ci_month_var = tk.StringVar()
        self.ci_day_var = tk.StringVar()

        self.co_year_var = tk.StringVar()
        self.co_month_var = tk.StringVar()
        self.co_day_var = tk.StringVar()

        self.show_active_var = tk.BooleanVar(value=True)

        # --------------------
        # FILTER BAR
        # --------------------
        filter_frame = tk.Frame(self, bg="#2C3E50")
        filter_frame.pack(fill="x", pady=8)

        # Back button (now resets filters before switching)
        back_btn = tk.Button(
            filter_frame,
            text="Back",
            command=lambda: (self.reset_filters(), controller.show_frame("main_menu")),
        )
        back_btn.pack(side="left", padx=12)

        # Guest name search
        tk.Label(filter_frame, text="Guest:", bg="#2C3E50", fg="white").pack(
            side="left", padx=(12, 4)
        )
        guest_entry = tk.Entry(filter_frame, textvariable=self.guest_var, width=20)
        guest_entry.pack(side="left", padx=4)

        # Room number search
        tk.Label(filter_frame, text="Room#:", bg="#2C3E50", fg="white").pack(
            side="left", padx=(12, 4)
        )
        room_entry = tk.Entry(filter_frame, textvariable=self.room_var, width=8)
        room_entry.pack(side="left", padx=4)

        # Status dropdown
        tk.Label(filter_frame, text="Status:", bg="#2C3E50", fg="white").pack(
            side="left", padx=(12, 4)
        )
        status_dropdown = ttk.Combobox(
            filter_frame,
            textvariable=self.status_var,
            values=[
                "",
                "Confirmed",
                "Checked-in",
                "Late",
                "Complete",
                "Late Check-out",
            ],
            width=12,
            state="readonly",
        )
        status_dropdown.current(0)
        status_dropdown.pack(side="left", padx=4)

        # -------------------------
        # CHECK-IN DATE FILTER
        # -------------------------
        tk.Label(filter_frame, text="Check-in After:", bg="#2C3E50", fg="white").pack(
            side="left", padx=(12, 4)
        )

        start_year = 2020
        current_year = date.today().year
        ci_years = list(range(start_year, current_year + 1))

        self.ci_year_cb = ttk.Combobox(
            filter_frame,
            textvariable=self.ci_year_var,
            values=ci_years,
            width=6,
            state="readonly",
        )
        self.ci_year_cb.pack(side="left", padx=2)

        self.ci_month_cb = ttk.Combobox(
            filter_frame,
            textvariable=self.ci_month_var,
            values=list(range(1, 13)),
            width=4,
            state="readonly",
        )
        self.ci_month_cb.pack(side="left", padx=2)

        self.ci_day_cb = ttk.Combobox(
            filter_frame,
            textvariable=self.ci_day_var,
            width=4,
            state="readonly",
        )
        self.ci_day_cb.pack(side="left", padx=2)

        # -------------------------
        # CHECK-OUT DATE FILTER
        # -------------------------
        tk.Label(filter_frame, text="Check-out Before:", bg="#2C3E50", fg="white").pack(
            side="left", padx=(12, 4)
        )

        co_years = list(range(start_year, current_year + 3))

        self.co_year_cb = ttk.Combobox(
            filter_frame,
            textvariable=self.co_year_var,
            values=co_years,
            width=6,
            state="readonly"
        )
        self.co_year_cb.pack(side="left", padx=2)

        self.co_month_cb = ttk.Combobox(
            filter_frame,
            textvariable=self.co_month_var,
            values=list(range(1, 13)),
            width=4,
            state="readonly"
        )
        self.co_month_cb.pack(side="left", padx=2)

        self.co_day_cb = ttk.Combobox(
            filter_frame,
            textvariable=self.co_day_var,
            width=4,
            state="readonly"
        )
        self.co_day_cb.pack(side="left", padx=2)

        # Active Reservations Checkbox
        active_chk = tk.Checkbutton(
            filter_frame,
            text="Show Active Reservations",
            variable=self.show_active_var,
            onvalue=True,
            offvalue=False,
            bg="#2C3E50",
            fg="white",
            selectcolor="#395A7F",
        )
        active_chk.pack(side="left", padx=(12, 4))

        # Clear Filters Button
        clear_btn = tk.Button(
            filter_frame,
            text="Clear Filters",
            command=lambda: (self.reset_filters(), self._load_data()),
        )
        clear_btn.pack(side="left", padx=8)

        # Filter button
        filter_btn = tk.Button(filter_frame, text="Filter", command=lambda: load_data())
        filter_btn.pack(side="left", padx=12)

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

        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=12)
        self.tree.pack(fill="both", expand=True, padx=10, pady=(0, 10))

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
            self.tree.heading(col, text=head)
            self.tree.column(col, width=100)

        # ------------------------
        # PAGINATION
        # ------------------------
        page_frame = tk.Frame(self, bg="#2C3E50")
        page_frame.pack(fill="x", pady=6)

        self.current_page = tk.IntVar(value=1)
        self.rows_per_page = 29
        self.result_rows = []

        prev_btn = tk.Button(page_frame, text="<", command=lambda: change_page(-1))
        prev_btn.pack(side="left", padx=6)
        tk.Label(page_frame, text="Page", bg="#2C3E50", fg="white").pack(side="left")

        self.page_entry = tk.Entry(page_frame, width=4, justify="center")
        self.page_entry.insert(0, "1")
        self.page_entry.pack(side="left", padx=6)

        self.max_page_label = tk.Label(page_frame, text="of 1", bg="#2C3E50", fg="white")
        self.max_page_label.pack(side="left", padx=(6, 20))

        next_btn = tk.Button(page_frame, text=">", command=lambda: change_page(1))
        next_btn.pack(side="left")

        # ------------ pagination helpers ------------
        def change_page(amount):
            new_page = self.current_page.get() + amount
            max_page = max(1, (len(self.result_rows) - 1) // self.rows_per_page + 1)
            if 1 <= new_page <= max_page:
                self.current_page.set(new_page)
                update_page()

        def update_page():
            self.tree.delete(*self.tree.get_children())
            page = self.current_page.get()
            start = (page - 1) * self.rows_per_page
            end = start + self.rows_per_page
            for row in self.result_rows[start:end]:
                self.tree.insert("", tk.END, values=row)
            max_page = max(1, (len(self.result_rows) - 1) // self.rows_per_page + 1)
            self.page_entry.delete(0, tk.END)
            self.page_entry.insert(0, str(page))
            self.max_page_label.config(text=f"of {max_page}")

        def go_to_page(event=None):
            try:
                new_page = int(self.page_entry.get())
            except ValueError:
                self.page_entry.delete(0, tk.END)
                self.page_entry.insert(0, "1")
                return
            max_page = max(1, (len(self.result_rows) - 1) // self.rows_per_page + 1)
            new_page = max(1, min(new_page, max_page))
            self.current_page.set(new_page)
            update_page()

        self.page_entry.bind("<Return>", lambda e: go_to_page())

        # -------------------------------
        # DATA LOADING
        # -------------------------------
        def load_data():
            """Load/filter reservations into result_rows and refresh current page."""
            self.result_rows = []
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

                # Guest filter
                if self.guest_var.get().strip() != "":
                    query += " AND (g.first_name || ' ' || g.last_name) LIKE ?"
                    params.append(f"%{self.guest_var.get().strip()}%")

                # Room filter
                if self.room_var.get().strip() != "":
                    query += " AND rm.room_number LIKE ?"
                    params.append(f"%{self.room_var.get().strip()}%")

                # Status filter
                if self.status_var.get().strip() != "":
                    query += " AND r.status = ?"
                    params.append(self.status_var.get().strip())

                # Check-in After Date filter
                if self.ci_year_var.get() and self.ci_month_var.get() and self.ci_day_var.get():
                    try:
                        y = int(self.ci_year_var.get())
                        m = int(self.ci_month_var.get())
                        d = int(self.ci_day_var.get())
                        filter_date = f"{y:04d}-{m:02d}-{d:02d}"
                        query += " AND r.check_in_date >= ?"
                        params.append(filter_date)
                    except ValueError:
                        pass

                # Check-out Before Date filter
                if self.co_year_var.get() and self.co_month_var.get() and self.co_day_var.get():
                    try:
                        y = int(self.co_year_var.get())
                        m = int(self.co_month_var.get())
                        d = int(self.co_day_var.get())
                        filter_date = f"{y:04d}-{m:02d}:{d:02d}"
                        query += " AND r.check_out_date <= ?"
                        params.append(filter_date)
                    except ValueError:
                        pass

                # Active/Inactive filter
                if self.show_active_var.get():
                    # Show only active reservations
                    query += " AND r.status IN ('Confirmed', 'Checked-in', 'Late', 'Late Check-out')"
                else:
                    # Show only inactive/completed reservations
                    query += " AND r.status IN ('Cancelled', 'Complete')"

                # ORDER-BY PRIORITY
                query += """
                    ORDER BY 
                        CASE 
                            WHEN r.status = 'Late Check-out' THEN 1
                            WHEN r.status = 'Late' THEN 2
                            WHEN r.status = 'Checked-in' THEN 3
                            ELSE 99
                        END,
                        r.check_in_date DESC
                """

                cur.execute(query, params)
                rows = cur.fetchall()

                self.result_rows = [
                    (
                        r[0],
                        r[1],
                        r[2] or "",
                        r[3],
                        r[4] or "",
                        r[5],
                        r[6],
                        f"{r[7]:.2f}" if isinstance(r[7], (float, int)) else r[7],
                        r[8],
                    )
                    for r in rows
                ]

            except sqlite3.Error as e:
                msg = str(e).lower()
                if "no such table" in msg:
                    self.result_rows = []
                else:
                    print("Database error:", e)
            finally:
                if conn:
                    conn.close()

            self.current_page.set(1)
            update_page()

        # Make load_data accessible in refresh()
        self._load_data = load_data

        # ----------------------------------------
        # EDIT RESERVATION DIALOG
        # ----------------------------------------
        def open_edit_dialog(event=None):
            """Open edit dialog for selected reservation (double-click or button)."""
            selection = self.tree.selection()
            if not selection:
                messagebox.showwarning("No Selection", "Please select a reservation to edit.")
                return

            selected_item = selection[0]
            values = self.tree.item(selected_item, "values")

            res_id = values[0]
            guest_name = values[2]
            room_num = values[4]
            check_in = values[5]
            check_out = values[6]
            current_status = values[8]

            edit_win = tk.Toplevel(self)
            edit_win.title(f"Edit Reservation #{res_id}")
            edit_w, edit_h = 450, 350
            edit_win.geometry(f"{edit_w}x{edit_h}")
            edit_win.configure(bg="#2C3E50")
            edit_win.resizable(False, False)

            edit_win.update_idletasks()  # ensure geometry is ready
            screen_w = self.winfo_screenwidth()
            screen_h = self.winfo_screenheight()

            x = (screen_w // 2) - (edit_w // 2)
            y = (screen_h // 2) - (edit_h // 2)

            edit_win.geometry(f"{edit_w}x{edit_h}+{x}+{y}")

            tk.Label(edit_win, text=f"Reservation #{res_id}", font=("Arial", 12, "bold"), bg="#2C3E50", fg="white").pack(pady=10)
            tk.Label(edit_win, text=f"Guest: {guest_name}", bg="#2C3E50", fg="white").pack()
            tk.Label(edit_win, text=f"Room: {room_num}", bg="#2C3E50", fg="white").pack()
            tk.Label(edit_win, text=f"Check-in: {check_in}", bg="#2C3E50", fg="white").pack()
            tk.Label(edit_win, text=f"Check-out: {check_out}", bg="#2C3E50", fg="white").pack(pady=(0, 20))

            tk.Label(edit_win, text="Update Status:", font=("Arial", 10, "bold"), bg="#2C3E50", fg="white").pack(anchor="w", padx=20)
            status_options = ["Confirmed", "Checked-in", "Checked-out", "Cancelled", "Paid", "Unpaid", "Late", "No-show"]
            status_var_edit = tk.StringVar(value=current_status)
            status_combo = ttk.Combobox(
                edit_win,
                textvariable=status_var_edit,
                values=status_options,
                state="readonly",
                width=30
            )
            status_combo.pack(pady=10, padx=20)

            btn_frame = tk.Frame(edit_win, bg="#2C3E50")
            btn_frame.pack(pady=20)

            def save_changes():
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
                    load_data()
                    edit_win.destroy()
                except sqlite3.Error as e:
                    messagebox.showerror("Database Error", f"Failed to update reservation: {e}")

            def delete_reservation_confirm():
                if messagebox.askyesno("Confirm Delete", f"Delete reservation #{res_id}? This cannot be undone."):
                    try:
                        conn = db.connect()
                        cur = conn.cursor()
                        cur.execute("DELETE FROM reservations WHERE reservation_id = ?", (res_id,))
                        conn.commit()
                        conn.close()
                        messagebox.showinfo("Success", f"Reservation #{res_id} deleted.")
                        load_data()
                        edit_win.destroy()
                    except sqlite3.Error as e:
                        messagebox.showerror("Database Error", f"Failed to delete reservation: {e}")

            save_btn = tk.Button(btn_frame, text="Save Status", command=save_changes, bg="#4CAF50", fg="white", width=15)
            save_btn.pack(side="left", padx=5)

            delete_btn = tk.Button(btn_frame, text="Delete", command=delete_reservation_confirm, bg="#f44336", fg="white", width=10)
            delete_btn.pack(side="left", padx=5)

            close_btn = tk.Button(btn_frame, text="Close", command=edit_win.destroy, width=10)
            close_btn.pack(side="left", padx=5)

        self.tree.bind("<Double-1>", open_edit_dialog)

        # -----------------------
        # Day dropdown updaters
        # -----------------------
        def update_day_dropdown_ci(*args):
            """Update day list for Check-in After filter."""
            year = self.ci_year_var.get()
            month = self.ci_month_var.get()

            if not year.isdigit() or not month.isdigit():
                self.ci_day_cb["values"] = []
                self.ci_day_var.set("")
                return

            year = int(year)
            month = int(month)

            _, num_days = calendar.monthrange(year, month)
            day_values = list(range(1, num_days + 1))
            self.ci_day_cb["values"] = day_values

            if self.ci_day_var.get().isdigit() and int(self.ci_day_var.get()) <= num_days:
                return

            self.ci_day_var.set("")

        def update_day_dropdown_co(*args):
            """Update day list for Check-out Before filter."""
            year = self.co_year_var.get()
            month = self.co_month_var.get()

            if not year.isdigit() or not month.isdigit():
                self.co_day_cb["values"] = []
                self.co_day_var.set("")
                return

            year = int(year)
            month = int(month)

            _, num_days = calendar.monthrange(year, month)
            day_values = list(range(1, num_days + 1))
            self.co_day_cb["values"] = day_values

            if self.co_day_var.get().isdigit() and int(self.co_day_var.get()) <= num_days:
                return

            self.co_day_var.set("")

        self.ci_year_var.trace_add("write", update_day_dropdown_ci)
        self.ci_month_var.trace_add("write", update_day_dropdown_ci)
        self.co_year_var.trace_add("write", update_day_dropdown_co)
        self.co_month_var.trace_add("write", update_day_dropdown_co)

        # Initial load
        load_data()

        # Keyboard niceties: Enter on guest/room fields triggers filter
        guest_entry.bind("<Return>", lambda e: load_data())
        room_entry.bind("<Return>", lambda e: load_data())

    # -----------------------
    # Utility methods
    # -----------------------
    def reset_filters(self):
        """Resets all filter inputs back to blank/empty."""
        self.guest_var.set("")
        self.room_var.set("")
        self.status_var.set("")
        self.ci_year_var.set("")
        self.ci_month_var.set("")
        self.ci_day_var.set("")
        self.co_year_var.set("")
        self.co_month_var.set("")
        self.co_day_var.set("")
        self.show_active_var.set(True)

        # Clear day dropdown values to avoid stale data
        try:
            self.ci_day_cb["values"] = []
            self.co_day_cb["values"] = []
        except Exception:
            pass

    def refresh(self):
        """Called when this frame is shown."""
        # If you want filters to automatically clear when the frame is shown:
        # self.reset_filters()
        if hasattr(self, "_load_data"):
            self._load_data()
