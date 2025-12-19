import tkinter as tk
from tkinter import ttk, messagebox
import calendar
from datetime import date

from database_manager import DatabaseManager
from edit_reservation_dialog import EditReservationDialog

db = DatabaseManager()


class BookingRecordsFrame(tk.Frame):
    """Displays booking records with filtering, pagination, and edit dialog access."""

    def __init__(self, parent, controller: "HotelApp"):
        super().__init__(parent, bg="#2C3E50")
        self.controller = controller
        self.sort_column = None
        self.sort_reverse = False

        self.hotel = getattr(controller, "hotel", None)
        if self.hotel is None:
            print("[Warning] BookingRecordsFrame: controller has no 'hotel' attribute.")

        # ---------------------------------------------------------
        # TITLE
        # ---------------------------------------------------------
        tk.Label(
            self,
            text="Booking Records",
            font=("Arial", 30, "bold"),
            bg="#2C3E50",
            fg="white"
        ).pack(pady=(10, 5))

        # ---------------------------------------------------------
        # FILTER VARIABLES
        # ---------------------------------------------------------
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

        # ---------------------------------------------------------
        # FILTER FRAME
        # ---------------------------------------------------------
        filter_frame = tk.Frame(self, bg="#2C3E50")
        filter_frame.pack(fill="x", pady=8)

        # BACK BUTTON
        tk.Button(
            filter_frame,
            text="Back",
            command=lambda: (self.reset_filters(), controller.show_frame("main_menu")),
        ).pack(side="left", padx=12)

        # Guest filter
        tk.Label(filter_frame, text="Guest:", bg="#2C3E50", fg="white").pack(side="left", padx=(12, 4))
        guest_entry = tk.Entry(filter_frame, textvariable=self.guest_var, width=20)
        guest_entry.pack(side="left", padx=4)

        # Room filter
        tk.Label(filter_frame, text="Room#:", bg="#2C3E50", fg="white").pack(side="left", padx=(12, 4))
        room_entry = tk.Entry(filter_frame, textvariable=self.room_var, width=8)
        room_entry.pack(side="left", padx=4)

        # Status dropdown
        tk.Label(filter_frame, text="Status:", bg="#2C3E50", fg="white").pack(side="left", padx=(12, 4))
        status_dd = ttk.Combobox(
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
            state="readonly"
        )
        status_dd.current(0)
        status_dd.pack(side="left", padx=4)

        # ---------------------------------------------------------
        # CHECK-IN DATE FILTER
        # ---------------------------------------------------------
        tk.Label(filter_frame, text="Check-in After:", bg="#2C3E50", fg="white").pack(
            side="left", padx=(12, 4)
        )

        start_year = 2020
        current_year = date.today().year
        year_values = list(range(start_year, current_year + 1))

        self.ci_year_cb = ttk.Combobox(
            filter_frame, textvariable=self.ci_year_var, values=year_values, width=6, state="readonly"
        )
        self.ci_year_cb.pack(side="left", padx=2)

        self.ci_month_cb = ttk.Combobox(
            filter_frame, textvariable=self.ci_month_var, values=list(range(1, 13)), width=4, state="readonly"
        )
        self.ci_month_cb.pack(side="left", padx=2)

        self.ci_day_cb = ttk.Combobox(
            filter_frame, textvariable=self.ci_day_var, width=4, state="readonly"
        )
        self.ci_day_cb.pack(side="left", padx=2)

        # ---------------------------------------------------------
        # CHECK-OUT DATE FILTER
        # ---------------------------------------------------------
        tk.Label(filter_frame, text="Check-out Before:", bg="#2C3E50", fg="white").pack(
            side="left", padx=(12, 4)
        )

        co_year_values = list(range(start_year, current_year + 3))

        self.co_year_cb = ttk.Combobox(
            filter_frame, textvariable=self.co_year_var, values=co_year_values, width=6, state="readonly"
        )
        self.co_year_cb.pack(side="left", padx=2)

        self.co_month_cb = ttk.Combobox(
            filter_frame, textvariable=self.co_month_var, values=list(range(1, 13)), width=4, state="readonly"
        )
        self.co_month_cb.pack(side="left", padx=2)

        self.co_day_cb = ttk.Combobox(
            filter_frame, textvariable=self.co_day_var, width=4, state="readonly"
        )
        self.co_day_cb.pack(side="left", padx=2)

        # Active checkbox
        tk.Checkbutton(
            filter_frame,
            text="Show Active Reservations",
            variable=self.show_active_var,
            bg="#2C3E50", fg="white",
            selectcolor="#395A7F"
        ).pack(side="left", padx=(12, 4))

        # Clear Filters
        tk.Button(
            filter_frame, text="Clear Filters",
            command=lambda: (self.reset_filters(), self._load_data())
        ).pack(side="left", padx=8)

        # Apply Filter Button
        tk.Button(
            filter_frame, text="Filter", command=lambda: self._load_data()
        ).pack(side="left", padx=12)

        # ---------------------------------------------------------
        # TREEVIEW TABLE
        # ---------------------------------------------------------
        columns = (
            "reservation_id",
            "guest_id",
            "guest_name",
            "room_id",
            "room_number",
            "check_in",
            "check_out",
            "total_price",
            "is_paid",
            "status",
        )

        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=15)
        self.tree.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        headings = [
            "Res ID", "Guest ID", "Guest", "Room ID", "Room #",
            "Check-in", "Check-out", "Total", "Paid?", "Status"
        ]

        for col, head in zip(columns, headings):
            self.tree.heading(col, text=head, command=lambda c=col: self._sort_by_column(c))
            self.tree.column(col, width=100)

        # Open Edit Dialog on double-click
        self.tree.bind("<Double-1>", self.open_edit_dialog)

        # ---------------------------------------------------------
        # PAGINATION
        # ---------------------------------------------------------
        page_frame = tk.Frame(self, bg="#2C3E50")
        page_frame.pack(fill="x", pady=6)

        self.current_page = tk.IntVar(value=1)
        self.rows_per_page = 29
        self.result_rows = []

        # Prev / Next Buttons
        tk.Button(page_frame, text="<", command=lambda: self._change_page(-1)).pack(side="left", padx=6)
        tk.Label(page_frame, text="Page", bg="#2C3E50", fg="white").pack(side="left")

        self.page_entry = tk.Entry(page_frame, width=4, justify="center")
        self.page_entry.insert(0, "1")
        self.page_entry.pack(side="left", padx=6)
        self.page_entry.bind("<Return>", lambda e: self._go_to_page())

        self.max_page_label = tk.Label(page_frame, text="of 1", bg="#2C3E50", fg="white")
        self.max_page_label.pack(side="left", padx=(6, 20))

        tk.Button(page_frame, text=">", command=lambda: self._change_page(1)).pack(side="left")

        # ---------------------------------------------------------
        # DAY DROP-DOWN UPDATERS
        # ---------------------------------------------------------
        self.ci_year_var.trace_add("write", self._update_ci_days)
        self.ci_month_var.trace_add("write", self._update_ci_days)

        self.co_year_var.trace_add("write", self._update_co_days)
        self.co_month_var.trace_add("write", self._update_co_days)

        # ---------------------------------------------------------
        # INITIAL DATA LOAD
        # ---------------------------------------------------------
        self._load_data()

        # Enter triggers filtering
        guest_entry.bind("<Return>", lambda e: self._load_data())
        room_entry.bind("<Return>", lambda e: self._load_data())

    # ---------------------------------------------------------------------
    # DATA LOADING
    # ---------------------------------------------------------------------
    def _load_data(self):
        """Pulls filters, requests data from DB, and updates table."""

        def build_date(y, m, d):
            if y and m and d:
                return f"{int(y):04d}-{int(m):02d}-{int(d):02d}"
            return None

        ci_date = build_date(self.ci_year_var.get(), self.ci_month_var.get(), self.ci_day_var.get())
        co_date = build_date(self.co_year_var.get(), self.co_month_var.get(), self.co_day_var.get())

        self.result_rows = db.get_filtered_reservations(
            guest_name=self.guest_var.get().strip() or None,
            room_number=self.room_var.get().strip() or None,
            status=self.status_var.get() or None,
            checkin_after=ci_date,
            checkout_before=co_date,
            show_active=self.show_active_var.get(),
        )

        self.current_page.set(1)
        self._update_page()

    def _sort_by_column(self, col_name):
        """Sorts visible reservation records by column header click."""
        try:
            col_index = self.tree["columns"].index(col_name)
        except ValueError:
            return

        # Toggle sorting direction if same column
        if self.sort_column == col_name:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = col_name
            self.sort_reverse = False

        # Attempt numeric sort when appropriate
        def sort_key(row):
            value = row[col_index]
            # Try converting numeric-looking values
            try:
                return float(value)
            except (TypeError, ValueError):
                return value

        # Sort internal rows
        self.result_rows.sort(key=sort_key, reverse=self.sort_reverse)

        # Restart pagination on page 1
        self.current_page.set(1)
        self._update_page()

    def _update_page(self):
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

    def _change_page(self, amount):
        new_page = self.current_page.get() + amount
        max_page = max(1, (len(self.result_rows) - 1) // self.rows_per_page + 1)

        if 1 <= new_page <= max_page:
            self.current_page.set(new_page)
            self._update_page()

    def _go_to_page(self):
        try:
            new_page = int(self.page_entry.get())
        except ValueError:
            self.page_entry.delete(0, tk.END)
            self.page_entry.insert(0, "1")
            return

        max_page = max(1, (len(self.result_rows) - 1) // self.rows_per_page + 1)
        new_page = max(1, min(new_page, max_page))

        self.current_page.set(new_page)
        self._update_page()

    # ---------------------------------------------------------------------
    # EDIT DIALOG OPEN
    # ---------------------------------------------------------------------
    def open_edit_dialog(self, event=None):

        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a reservation to edit.")
            return

        selected_item = selection[0]
        values = self.tree.item(selected_item, "values")

        # Pass row + callback into dialog
        EditReservationDialog(
            parent_frame=self,
            controller=self.controller,
            reservation_values=values,
            refresh_callback=self._load_data
        )

    # ---------------------------------------------------------------------
    # ROOM SELECTION FROM POPUP
    # ---------------------------------------------------------------------
    def set_selected_room(self, room_id, room_number):
        """Called by RoomSearchPopup → forwards to the dialog if open."""

        # Find the active EditReservationDialog
        for win in self.winfo_children():
            if isinstance(win, tk.Toplevel) and hasattr(win, "set_new_room"):
                win.set_new_room(room_id, room_number)
                messagebox.showinfo("Room Selected", f"Room {room_number} applied.")
                return

        messagebox.showwarning("No Edit Window", "Open the reservation editor before selecting a room.")

    # ---------------------------------------------------------------------
    # FILTER UTILITIES
    # ---------------------------------------------------------------------
    def reset_filters(self):
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

        self.ci_day_cb["values"] = []
        self.co_day_cb["values"] = []

    def _update_ci_days(self, *args):
        year = self.ci_year_var.get()
        month = self.ci_month_var.get()

        if not (year.isdigit() and month.isdigit()):
            self.ci_day_cb["values"] = []
            self.ci_day_var.set("")
            return

        year, month = int(year), int(month)
        days = calendar.monthrange(year, month)[1]
        vals = list(range(1, days + 1))
        self.ci_day_cb["values"] = vals

        if not (self.ci_day_var.get().isdigit() and int(self.ci_day_var.get()) <= days):
            self.ci_day_var.set("")

    def _update_co_days(self, *args):
        year = self.co_year_var.get()
        month = self.co_month_var.get()

        if not (year.isdigit() and month.isdigit()):
            self.co_day_cb["values"] = []
            self.co_day_var.set("")
            return

        year, month = int(year), int(month)
        days = calendar.monthrange(year, month)[1]
        vals = list(range(1, days + 1))
        self.co_day_cb["values"] = vals

        if not (self.co_day_var.get().isdigit() and int(self.co_day_var.get()) <= days):
            self.co_day_var.set("")

    # ---------------------------------------------------------------------
    # REFRESH (Called by parent controller)
    # ---------------------------------------------------------------------
    def refresh(self):
        self._load_data()
