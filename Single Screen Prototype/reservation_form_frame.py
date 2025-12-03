import tkinter as tk
from tkinter import ttk, messagebox
from room_search_popup import RoomSearchPopup
import calendar
from datetime import date, datetime, timedelta

BG_COLOR = "#2C3E50"
PANEL_BG = "#34495E"
FG_COLOR = "white"


class ReservationFormFrame(tk.Frame):
    def __init__(self, parent, controller: "HotelApp"):
        super().__init__(parent, bg=BG_COLOR)
        self.controller = controller

        # ===============================
        # Centered Wrapper
        # ===============================
        wrapper = tk.Frame(self, bg=BG_COLOR)
        wrapper.pack(pady=40)

        # Title
        title = tk.Label(
            wrapper,
            text="Create New Reservation",
            font=("Arial", 30, "bold"),
            fg=FG_COLOR,
            bg=BG_COLOR
        )
        title.pack(pady=(0, 40))

        # ===============================
        # SIDE-BY-SIDE MAIN FRAME
        # ===============================
        main_container = tk.Frame(wrapper, bg=BG_COLOR)
        main_container.pack()

        # Left column frame (Guest Info)
        left_col = tk.Frame(main_container, bg=BG_COLOR)
        left_col.grid(row=0, column=0, padx=40)

        # Right column frame (Reservation Details)
        right_col = tk.Frame(main_container, bg=BG_COLOR)
        right_col.grid(row=0, column=1, padx=40)

        # ============================================================
        # SECTION 1 — Guest Information (LEFT)
        # ============================================================
        guest_frame = tk.LabelFrame(
            left_col,
            text="Guest Information",
            bg=PANEL_BG,
            fg=FG_COLOR,
            padx=20,
            pady=20,
            width=450,
            labelanchor="n"
        )
        guest_frame.pack(fill="both")

        # Variables
        self.first_name_var = tk.StringVar()
        self.last_name_var = tk.StringVar()
        self.email_var = tk.StringVar()
        self.phone_var = tk.StringVar()

        # Address variables
        self.addr1_var = tk.StringVar()
        self.addr2_var = tk.StringVar()
        self.city_var = tk.StringVar()
        self.state_var = tk.StringVar()
        self.postal_var = tk.StringVar()

        # First + Last Name
        tk.Label(guest_frame, text="First Name:", bg=PANEL_BG, fg=FG_COLOR)\
            .grid(row=0, column=0, sticky="e", pady=6, padx=5)
        tk.Entry(guest_frame, textvariable=self.first_name_var, width=22)\
            .grid(row=0, column=1, pady=6)

        tk.Label(guest_frame, text="Last Name:", bg=PANEL_BG, fg=FG_COLOR)\
            .grid(row=1, column=0, sticky="e", pady=6, padx=5)
        tk.Entry(guest_frame, textvariable=self.last_name_var, width=22)\
            .grid(row=1, column=1, pady=6)

        # Email
        tk.Label(guest_frame, text="Email:", bg=PANEL_BG, fg=FG_COLOR)\
            .grid(row=2, column=0, sticky="e", pady=6)
        tk.Entry(guest_frame, textvariable=self.email_var, width=22)\
            .grid(row=2, column=1, pady=6)

        # Phone
        tk.Label(guest_frame, text="Phone Number:", bg=PANEL_BG, fg=FG_COLOR)\
            .grid(row=3, column=0, sticky="e", pady=6)
        tk.Entry(guest_frame, textvariable=self.phone_var, width=22)\
            .grid(row=3, column=1, pady=6)

        # ===== Address Breakdown =====
        tk.Label(guest_frame, text="Address Line 1:", bg=PANEL_BG, fg=FG_COLOR)\
            .grid(row=4, column=0, sticky="e", pady=6)
        tk.Entry(guest_frame, textvariable=self.addr1_var, width=22)\
            .grid(row=4, column=1, pady=6)

        tk.Label(guest_frame, text="Address Line 2:", bg=PANEL_BG, fg=FG_COLOR)\
            .grid(row=5, column=0, sticky="e", pady=6)
        tk.Entry(guest_frame, textvariable=self.addr2_var, width=22)\
            .grid(row=5, column=1, pady=6)

        tk.Label(guest_frame, text="City:", bg=PANEL_BG, fg=FG_COLOR)\
            .grid(row=6, column=0, sticky="e", pady=6)
        tk.Entry(guest_frame, textvariable=self.city_var, width=22)\
            .grid(row=6, column=1, pady=6)

        tk.Label(guest_frame, text="State:", bg=PANEL_BG, fg=FG_COLOR)\
            .grid(row=7, column=0, sticky="e", pady=6)
        tk.Entry(guest_frame, textvariable=self.state_var, width=10)\
            .grid(row=7, column=1, pady=6, sticky="w")

        tk.Label(guest_frame, text="Postal Code:", bg=PANEL_BG, fg=FG_COLOR)\
            .grid(row=8, column=0, sticky="e", pady=6)
        tk.Entry(guest_frame, textvariable=self.postal_var, width=10)\
            .grid(row=8, column=1, pady=6, sticky="w")

        # ============================================================
        # SECTION 2 — Reservation Details (RIGHT)
        # ============================================================
        reserve_frame = tk.LabelFrame(
            right_col,
            text="Reservation Details",
            bg=PANEL_BG,
            fg=FG_COLOR,
            padx=20,
            pady=20,
            width=600,
            labelanchor="n"
        )
        reserve_frame.pack(fill="both")

        # Number + Smoking
        self.num_guests_var = tk.IntVar(value=1)
        self.include_smoking_var = tk.BooleanVar(value=True)

        tk.Label(reserve_frame, text="Number of Guests:", bg=PANEL_BG, fg=FG_COLOR)\
            .grid(row=0, column=0, sticky="e", pady=6)
        tk.Spinbox(reserve_frame, from_=1, to=20, textvariable=self.num_guests_var, width=5)\
            .grid(row=0, column=1, pady=6, sticky="w")

        # ---------------------------
        # Date dropdown variables
        # ---------------------------
        today = date.today()
        current_year = today.year
        years = [current_year, current_year + 1, current_year + 2]

        # Keep ISO string vars for compatibility (you asked for B)
        self.check_in_var = tk.StringVar()
        self.check_out_var = tk.StringVar()

        # Individual components (IntVars are convenient for calendar calculations)
        self.ci_year = tk.IntVar(value=current_year)
        self.ci_month = tk.IntVar(value=today.month)
        self.ci_day = tk.IntVar(value=today.day)

        # default checkout = tomorrow
        default_co = today + timedelta(days=1)
        self.co_year = tk.IntVar(value=default_co.year)
        self.co_month = tk.IntVar(value=default_co.month)
        self.co_day = tk.IntVar(value=default_co.day)

        # Helper: update the ISO string vars to keep them in sync
        def sync_iso_vars(*args):
            try:
                ci = date(self.ci_year.get(), self.ci_month.get(), self.ci_day.get())
                co = date(self.co_year.get(), self.co_month.get(), self.co_day.get())
                self.check_in_var.set(ci.isoformat())
                self.check_out_var.set(co.isoformat())
            except Exception:
                # If values are temporarily inconsistent, don't crash
                pass

        # Helper: update day combobox values based on year/month
        def update_days(year_var: tk.IntVar, month_var: tk.IntVar, day_var: tk.IntVar, day_box: ttk.Combobox):
            y = year_var.get()
            m = month_var.get()
            if not y or not m:
                return
            # monthrange returns (weekday_first, days_in_month)
            days_in_month = calendar.monthrange(y, m)[1]
            day_values = list(range(1, days_in_month + 1))
            # set combobox values
            day_box['values'] = day_values
            # clamp the selected day
            if day_var.get() > days_in_month:
                day_var.set(days_in_month)
            # ensure ISO strings sync
            sync_iso_vars()

        # Build horizontal date selectors
        # Row labels
        tk.Label(reserve_frame, text="Check-In:", bg=PANEL_BG, fg=FG_COLOR)\
            .grid(row=1, column=0, sticky="e", pady=6)
        # Year combobox
        ci_year_cb = ttk.Combobox(reserve_frame, textvariable=self.ci_year, values=years, width=6, state="readonly")
        ci_year_cb.grid(row=1, column=1, sticky="w", padx=(2, 6))
        # Month combobox (1-12)
        ci_month_cb = ttk.Combobox(reserve_frame, textvariable=self.ci_month, values=list(range(1, 13)), width=4, state="readonly")
        ci_month_cb.grid(row=1, column=2, sticky="w", padx=(2, 6))
        # Day combobox (filled below)
        ci_day_cb = ttk.Combobox(reserve_frame, textvariable=self.ci_day, width=4, state="readonly")
        ci_day_cb.grid(row=1, column=3, sticky="w", padx=(2, 6))

        # Check-Out row
        tk.Label(reserve_frame, text="Check-Out:", bg=PANEL_BG, fg=FG_COLOR)\
            .grid(row=2, column=0, sticky="e", pady=6)
        co_year_cb = ttk.Combobox(reserve_frame, textvariable=self.co_year, values=years, width=6, state="readonly")
        co_year_cb.grid(row=2, column=1, sticky="w", padx=(2, 6))
        co_month_cb = ttk.Combobox(reserve_frame, textvariable=self.co_month, values=list(range(1, 13)), width=4, state="readonly")
        co_month_cb.grid(row=2, column=2, sticky="w", padx=(2, 6))
        co_day_cb = ttk.Combobox(reserve_frame, textvariable=self.co_day, width=4, state="readonly")
        co_day_cb.grid(row=2, column=3, sticky="w", padx=(2, 6))

        # Bind traces to update days and keep checkout at least 1 day after checkin
        def on_ci_change(*_):
            update_days(self.ci_year, self.ci_month, self.ci_day, ci_day_cb)
            # ensure checkout >= checkin + 1 day
            try:
                ci_date = date(self.ci_year.get(), self.ci_month.get(), self.ci_day.get())
                co_date = date(self.co_year.get(), self.co_month.get(), self.co_day.get())
                if co_date <= ci_date:
                    new_co = ci_date + timedelta(days=1)
                    # adjust co component vars (this will trigger co traces)
                    self.co_year.set(new_co.year)
                    self.co_month.set(new_co.month)
                    self.co_day.set(new_co.day)
                sync_iso_vars()
            except Exception:
                pass

        def on_co_change(*_):
            update_days(self.co_year, self.co_month, self.co_day, co_day_cb)
            # If co <= ci, keep but validation will catch if user tries to search
            sync_iso_vars()

        # Attach the traces
        self.ci_year.trace_add("write", on_ci_change)
        self.ci_month.trace_add("write", on_ci_change)
        self.ci_day.trace_add("write", sync_iso_vars)

        self.co_year.trace_add("write", on_co_change)
        self.co_month.trace_add("write", on_co_change)
        self.co_day.trace_add("write", sync_iso_vars)

        # Initialize day lists + ISO string vars
        update_days(self.ci_year, self.ci_month, self.ci_day, ci_day_cb)
        update_days(self.co_year, self.co_month, self.co_day, co_day_cb)
        sync_iso_vars()

        # Include smoking checkbox
        tk.Checkbutton(
            reserve_frame,
            text="Include Smoking Rooms?",
            variable=self.include_smoking_var,
            bg=PANEL_BG,
            fg=FG_COLOR,
            selectcolor=PANEL_BG
        ).grid(row=3, column=0, columnspan=4, pady=10, sticky="w")

        # Search button
        tk.Button(
            reserve_frame,
            text="Search for Rooms",
            width=18,
            command=self.open_room_search_popup
        ).grid(row=4, column=0, columnspan=4, pady=10, sticky="e")

        # ============================================================
        # Buttons
        # ============================================================
        button_frame = tk.Frame(wrapper, bg=BG_COLOR)
        button_frame.pack(pady=30)

        tk.Button(
            button_frame,
            text="Submit Reservation",
            width=18,
            command=self.submit_reservation
        ).grid(row=0, column=0, padx=15)

        tk.Button(
            button_frame,
            text="Cancel",
            width=12,
            command=lambda: controller.show_frame("main_menu")
        ).grid(row=0, column=1, padx=15)


    # -------------------------------------------------------------------
    def refresh(self):
        self.first_name_var.set("")
        self.last_name_var.set("")
        self.email_var.set("")
        self.phone_var.set("")
        self.addr1_var.set("")
        self.addr2_var.set("")
        self.city_var.set("")
        self.state_var.set("")
        self.postal_var.set("")
        self.num_guests_var.set(1)

        # reset dates to today / tomorrow
        today = date.today()
        self.ci_year.set(today.year)
        self.ci_month.set(today.month)
        self.ci_day.set(today.day)
        tomorrow = today + timedelta(days=1)
        self.co_year.set(tomorrow.year)
        self.co_month.set(tomorrow.month)
        self.co_day.set(tomorrow.day)
        self.include_smoking_var.set(True)

    # --------------------------------------------------------------------
    def open_room_search_popup(self):
        # Use the internal component IntVars to build date objects
        try:
            check_in_date = date(self.ci_year.get(), self.ci_month.get(), self.ci_day.get())
            check_out_date = date(self.co_year.get(), self.co_month.get(), self.co_day.get())
        except ValueError:
            messagebox.showerror("Invalid Date", "Please select valid dates.")
            return

        today = date.today()

        # Validation: check-in not in the past
        if check_in_date < today:
            messagebox.showerror("Invalid Date", "Check-in date cannot be in the past.")
            return

        # Validation: check-out at least one day after check-in
        if check_out_date <= check_in_date:
            messagebox.showerror("Invalid Date", "Check-out must be at least 1 day after check-in.")
            return

        # Keep the ISO string vars for any other code that expects string format
        self.check_in_var.set(check_in_date.isoformat())
        self.check_out_var.set(check_out_date.isoformat())

        num_guests = self.num_guests_var.get()
        include_smoking = 1 if self.include_smoking_var.get() else 0

        # Pass Python date objects to the popup (DB layer will convert them to strings as needed)
        RoomSearchPopup(self, self.controller, check_in_date, check_out_date, num_guests, include_smoking)


    # -------------------------------------------------------------------
    def submit_reservation(self):
        # Basic validation here (expandable later)
        if not self.first_name_var.get().strip():
            messagebox.showerror("Error", "First name is required.")
            return

        if not self.last_name_var.get().strip():
            messagebox.showerror("Error", "Last name is required.")
            return

        if not self.email_var.get().strip():
            messagebox.showerror("Error", "Email is required.")
            return

        if not self.addr1_var.get().strip():
            messagebox.showerror("Error", "Address Line 1 is required.")
            return

        if not self.city_var.get().strip() or not self.state_var.get().strip():
            messagebox.showerror("Error", "City and State required.")
            return

        if not self.state_var.get().strip():
            messagebox.showerror("Error", "State required.")
            return

        if not self.postal_var.get().strip():
            messagebox.showerror("Error", "Postal Code is required.")
            return

        # Placeholder - actual insert logic to be added later
        messagebox.showinfo("Success", "Reservation saved (database insert coming soon!)")
        self.controller.show_frame("main_menu")
