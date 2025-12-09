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
        middle_col = tk.Frame(main_container, bg=BG_COLOR)
        middle_col.grid(row=0, column=1, padx=40)

        #Right column frame (Payment Details)
        right_col = tk.Frame(main_container, bg=BG_COLOR)
        right_col.grid(row=0, column=2, padx=40)

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

        # Guest ID Variables
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
        tk.Label(guest_frame, text="Phone Number:", bg=PANEL_BG, fg=FG_COLOR) \
            .grid(row=3, column=0, sticky="e", pady=6)

        # create the entry and bind KeyRelease
        self.phone_entry = tk.Entry(guest_frame, textvariable=self.phone_var, width=22)
        self.phone_entry.grid(row=3, column=1, pady=6, sticky="w")

        # call formatter on KeyRelease (works well with cursor adjustments)
        self.phone_entry.bind("<KeyRelease>", lambda e: self.format_phone_number())

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

        tk.Label(
            guest_frame, text="State:", bg=PANEL_BG, fg=FG_COLOR
        ).grid(row=7, column=0, sticky="e", pady=6)

        # List of all 50 U.S. states
        STATE_LIST = [
            "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
            "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
            "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
            "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
            "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"
        ]

        self.state_combo = ttk.Combobox(
            guest_frame,
            textvariable=self.state_var,
            values=STATE_LIST,
            width=5,
            state="readonly"
        )
        self.state_combo.grid(row=7, column=1, pady=6, sticky="w")

        #Pre-select California by default
        self.state_combo.set("CA")

        tk.Label(guest_frame, text="Postal Code:", bg=PANEL_BG, fg=FG_COLOR)\
            .grid(row=8, column=0, sticky="e", pady=6)
        tk.Entry(guest_frame, textvariable=self.postal_var, width=10)\
            .grid(row=8, column=1, pady=6, sticky="w")

        # ============================================================
        # SECTION 2 — Reservation Details (RIGHT)
        # ============================================================
        reserve_frame = tk.LabelFrame(
            middle_col,
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

        tk.Label(reserve_frame, text="Number of Guests (Max 6):", bg=PANEL_BG, fg=FG_COLOR)\
            .grid(row=0, column=0, sticky="e", pady=6)
        tk.Spinbox(reserve_frame, from_=1, to=20, textvariable=self.num_guests_var, width=5)\
            .grid(row=0, column=1, pady=6, sticky="w")

        # ---------------------------
        # Date dropdown variables
        # ---------------------------
        today = date.today()
        current_year = today.year
        years = [current_year, current_year + 1]

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

        # Horizontal date selectors
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

        # Bind traces to update days and keep checkout at least 1 day after checkin and at most 30
        MAX_STAY = 30  # days

        def on_ci_change(*_):
            update_days(self.ci_year, self.ci_month, self.ci_day, ci_day_cb)

            try:
                ci_date = date(self.ci_year.get(), self.ci_month.get(), self.ci_day.get())

                # update checkout selectors
                update_checkout_dropdowns(ci_date)

                # ensure current checkout is valid after updating dropdown options
                min_co = ci_date + timedelta(days=1)
                max_co = ci_date + timedelta(days=30)

                co_date = date(self.co_year.get(), self.co_month.get(), self.co_day.get())

                if co_date < min_co:
                    co_date = min_co
                if co_date > max_co:
                    co_date = max_co

                self.co_year.set(co_date.year)
                self.co_month.set(co_date.month)
                self.co_day.set(co_date.day)

                sync_iso_vars()

            except Exception:
                pass

        def on_co_change(*_):
            try:
                ci_date = date(self.ci_year.get(), self.ci_month.get(), self.ci_day.get())
                min_co = ci_date + timedelta(days=1)
                max_co = ci_date + timedelta(days=30)

                update_checkout_dropdowns(ci_date)

                co_date = date(self.co_year.get(), self.co_month.get(), self.co_day.get())

                if co_date < min_co:
                    co_date = min_co
                if co_date > max_co:
                    co_date = max_co

                self.co_year.set(co_date.year)
                self.co_month.set(co_date.month)
                self.co_day.set(co_date.day)

                sync_iso_vars()

            except Exception:
                pass

        def update_checkout_dropdowns(ci_date):
            """Update checkout year/month/day dropdown values based on 1–30 day max stay."""
            min_co = ci_date + timedelta(days=1)
            max_co = ci_date + timedelta(days=30)

            # --- allowed years ---
            years = list(range(min_co.year, max_co.year + 1))
            co_year_cb['values'] = years

            # Ensure year is within allowed range
            if self.co_year.get() not in years:
                self.co_year.set(min_co.year)

            selected_year = self.co_year.get()

            # --- allowed months ---
            if min_co.year == max_co.year:
                # same year → months are continuous
                months = list(range(min_co.month, max_co.month + 1))
            else:
                if selected_year == min_co.year:
                    months = list(range(min_co.month, 13))
                elif selected_year == max_co.year:
                    months = list(range(1, max_co.month + 1))
                else:
                    months = list(range(1, 13))

            co_month_cb['values'] = months

            # Clamp selected month
            if self.co_month.get() not in months:
                self.co_month.set(months[0])

            selected_month = self.co_month.get()

            # --- allowed days ---
            # compute valid day range within the selected month
            from calendar import monthrange

            month_days = monthrange(selected_year, selected_month)[1]
            days = list(range(1, month_days + 1))

            # Filter days outside allowed range
            valid_days = []
            for d in days:
                candidate = date(selected_year, selected_month, d)
                if min_co <= candidate <= max_co:
                    valid_days.append(d)

            co_day_cb['values'] = valid_days

            # Clamp selected day
            if self.co_day.get() not in valid_days:
                self.co_day.set(valid_days[0])

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

        #Selected room label
        self.selected_room_var = tk.StringVar(value="No room selected")

        tk.Label(
            reserve_frame,
            text="Selected Room:",
            bg=PANEL_BG,
            fg=FG_COLOR,
        ).grid(row=5, column=0, sticky="e", pady=(10,6))

        tk.Label(
            reserve_frame,
            textvariable=self.selected_room_var,
            bg=PANEL_BG,
            fg=FG_COLOR,
        ).grid(row=5, column=1, columnspan=3, sticky="w", pady=(10,6))

        # ============================================================
        # SECTION 3 — Payment Details (RIGHT)
        # ============================================================
        payment_frame = tk.LabelFrame(
            right_col,
            text="Payment Details",
            bg=PANEL_BG,
            fg=FG_COLOR,
            padx=20,
            pady=20,
            width=600,
            labelanchor="n"
        )
        payment_frame.pack(fill="both")

        # ------------------------------------------
        # Payment method radio buttons
        # ------------------------------------------
        self.payment_method = tk.StringVar(value="card")  # default
        self.is_paid_var = tk.IntVar(value=1)

        cash_radio = ttk.Radiobutton(
            payment_frame,
            text="Pay with Cash at Check-In",
            variable=self.payment_method,
            value="cash",
            command=self.toggle_payment_fields
        )
        cash_radio.grid(row=0, column=0, sticky="w", pady=2)

        card_radio = ttk.Radiobutton(
            payment_frame,
            text="Credit Card",
            variable=self.payment_method,
            value="card",
            command=self.toggle_payment_fields
        )
        card_radio.grid(row=1, column=0, sticky="w", pady=2)

        # ------------------------------------------
        # CREDIT CARD FIELDS — inside a sub-frame
        # ------------------------------------------
        self.card_frame = tk.Frame(payment_frame, bg=PANEL_BG)
        self.card_frame.grid(row=2, column=0, columnspan=2, sticky="w", pady=10)

        # Cardholder
        tk.Label(self.card_frame, text="Cardholder Name:", bg=PANEL_BG, fg=FG_COLOR) \
            .grid(row=0, column=0, sticky="w")
        self.cardholder_var = tk.StringVar()
        self.cardholder_entry = tk.Entry(self.card_frame, textvariable=self.cardholder_var)
        self.cardholder_entry.grid(row=0, column=1, pady=2, padx=5)

        # Card Number (formatted)
        tk.Label(self.card_frame, text="Card Number:", bg=PANEL_BG, fg=FG_COLOR) \
            .grid(row=1, column=0, sticky="w")
        self.card_number_var = tk.StringVar()
        self.card_number_entry = tk.Entry(self.card_frame, textvariable=self.card_number_var)
        self.card_number_entry.grid(row=1, column=1, pady=2, padx=5)
        # bind to formatting (KeyRelease so we can reformat after typing)
        self.card_number_entry.bind("<KeyRelease>", lambda e: self.format_card_number())

        # Expiration (MM/YY)
        tk.Label(self.card_frame, text="Expiration (MMYY):", bg=PANEL_BG, fg=FG_COLOR) \
            .grid(row=2, column=0, sticky="w")
        self.card_exp_var = tk.StringVar()
        self.card_exp_entry = tk.Entry(self.card_frame, textvariable=self.card_exp_var, width=8)
        self.card_exp_entry.grid(row=2, column=1, sticky="w", pady=2)
        self.card_exp_entry.bind("<KeyRelease>", lambda e: self.format_expiry())

        # CVV
        tk.Label(self.card_frame, text="CVV:", bg=PANEL_BG, fg=FG_COLOR) \
            .grid(row=3, column=0, sticky="w")
        self.card_cvv_var = tk.StringVar()
        self.card_cvv_entry = tk.Entry(self.card_frame, textvariable=self.card_cvv_var, width=6, show="*")
        self.card_cvv_entry.grid(row=3, column=1, sticky="w", pady=2)
        # optional: restrict CVV characters to digits only on key release
        self.card_cvv_entry.bind("<KeyRelease>", lambda e: self.format_cvv())

        # Hide or show based on initial method selection
        self.toggle_payment_fields()

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
        self.selected_room_var.set("No room selected")

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

    #---------------------------------------------------------------------
    def set_selected_room(self, room_id, room_number):
        self.selected_room_id = room_id
        self.selected_room_var.set(f"Room {room_number}")

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

        #Validation number of guests more than 0
        num_guests = self.num_guests_var.get()

        if num_guests <= 0:
            messagebox.showerror("Invalid Number", "Number of guests must be greater than 0.")
            return

        include_smoking = 1 if self.include_smoking_var.get() else 0

        # Pass Python date objects to the popup (DB layer will convert them to strings as needed)
        RoomSearchPopup(self, self.controller, check_in_date, check_out_date, num_guests, include_smoking)


    # -------------------------------------------------------------------
    def submit_reservation(self):
        # --- Collect Guest Info ---
        first = self.first_name_var.get().strip()
        last = self.last_name_var.get().strip()
        email = self.email_var.get().strip()
        phone = self.phone_var.get().strip()
        addr1 = self.addr1_var.get().strip()
        addr2 = self.addr2_var.get().strip()
        city = self.city_var.get().strip()
        state = self.state_var.get().strip()
        postal = self.postal_var.get().strip()

        # --- Validation ---
        if not all([first, last, email, addr1, city, state, postal]):
            messagebox.showerror("Missing Information", "Please complete all required guest fields.")
            return

        if not hasattr(self, "selected_room_id"):
            messagebox.showerror("No Room Selected", "Please search and choose a room before submitting.")
            return

        room_id = self.selected_room_id

        check_in = self.check_in_var.get().strip()
        check_out = self.check_out_var.get().strip()
        num_guests = self.num_guests_var.get()

        if not check_in or not check_out:
            messagebox.showerror("Missing Dates", "Please select both check-in and check-out dates.")
            return

        # --- Validate date format + length of stay ---
        try:
            from datetime import datetime
            d1 = datetime.strptime(check_in, "%Y-%m-%d")
            d2 = datetime.strptime(check_out, "%Y-%m-%d")

            if d2 <= d1:
                messagebox.showerror("Invalid Dates", "Check-out date must be after check-in date.")
                return

            nights = (d2 - d1).days
        except ValueError:
            messagebox.showerror("Invalid Date Format", "Dates must be in YYYY-MM-DD format.")
            return

        # Validate payment method
        payment_method = self.payment_method.get()

        if payment_method == "card":
            # collect raw data
            cardholder = self.cardholder_var.get().strip()
            cardnum_formatted = self.card_number_var.get().strip()
            cardnum_digits = self.clean_digits(cardnum_formatted)
            exp = self.card_exp_var.get().strip()
            cvv = self.card_cvv_var.get().strip()

            # quick checks
            if not all([cardholder, cardnum_digits, exp, cvv]):
                messagebox.showerror("Missing Payment Info", "Please complete all credit card fields.")
                return

            self.is_paid_var.set(1)

            # expiry validate MM/YY and not expired
            try:
                mm, yy = exp.split("/")
                mm = int(mm);
                yy = int(yy)
                if mm < 1 or mm > 12:
                    raise ValueError
                # Interpret 2-digit year (assume 2000+)
                this_year = date.today().year % 100
                this_full_year = date.today().year
                exp_year_full = 2000 + yy if yy <= 99 else yy
                # create date as last day of that month
                from calendar import monthrange
                last_day = monthrange(exp_year_full, mm)[1]
                expiry_date = date(exp_year_full, mm, last_day)
                if expiry_date < date.today():
                    messagebox.showerror("Card Expired", "The card expiry date is in the past.")
                    return
            except Exception:
                messagebox.showerror("Invalid Expiration", "Expiration must be MM/YY and valid.")
                return

            # Luhn
            if not self.luhn_check(cardnum_digits):
                messagebox.showerror("Invalid Card", "Card number failed Luhn validation.")
                return

            # CVV
            if not self.validate_cvv(cvv, cardnum_digits):
                messagebox.showerror("Invalid CVV", "CVV must be numeric and length appropriate for card type.")
                return

            # all payment validations passed; simulate processing
            amount = 0.0
            try:
                nightly_price = self.controller.db.get_room_price(room_id)
                amount = nightly_price * nights
            except Exception:
                nightly_price = 0.0
                amount = 0.0

            # Show processor modal and simulate result.
            proc_win, finish = self.show_payment_processor(amount, cardnum_digits[-4:],
                callback=lambda ok: self._after_payment(ok, first, last, email, phone, addr1,
                addr2, city, state, postal, room_id, check_in, check_out, num_guests, nights))
            # decide success: we can just approve if validation succeeded; but to simulate occasional failures you could randomize
            # here we'll approve deterministically
            self.after(900, lambda: finish(True))

            return  # insertion continues in _after_payment

        else:
            # Cash: proceed immediately
            # --- Step 1: Insert guest into database ---
            guest_id = self.controller.db.add_guest(
                first, last, email, addr1,
                city, state, postal, phone, addr2,
            )

            self.is_paid_var.set(0)

            # --- Step 2: Insert reservation ---
            reservation_id = self.controller.hotel.reserve_room(
                guest_id=guest_id,
                room_id=room_id,
                check_in=check_in,
                check_out=check_out,
                num_guests=num_guests,
                status="Confirmed",
                is_paid=self.is_paid_var.get(),
            )

            messagebox.showinfo(
                "Reservation Created",
                f"Reservation #{reservation_id} created successfully!"
            )
            self.controller.show_frame("main_menu")

    #-------------------------
    # Phone number Formatting
    #-------------------------
    def format_phone_number(self):
        """Auto-format phone number as (123)-456-7890 and limit to 10 digits.
           Keep the cursor at the end after formatting."""
        raw = "".join(ch for ch in self.phone_var.get() if ch.isdigit())
        raw = raw[:10]  # enforce limit

        # Build formatted string
        formatted = ""
        if len(raw) >= 1:
            formatted = "(" + raw[:3]
        if len(raw) >= 3:
            # if only 1-2 digits inside parentheses, still close when we have 3
            formatted = "(" + raw[:3] + ")"
        if len(raw) >= 4:
            formatted += "-" + raw[3:6]
        if len(raw) >= 7:
            formatted += "-" + raw[6:10]

        # Avoid infinite recursion and only update if different
        if formatted != self.phone_var.get():
            self.phone_var.set(formatted)
            # move cursor to end after current event loop so Tk's own handling won't override it
            self.after_idle(lambda: self.phone_entry.icursor(tk.END))

    # ------------------------
    # Credit Card helpers & validation
    # ------------------------
    def clean_digits(self, s: str) -> str:
        return "".join(ch for ch in s if ch.isdigit())

    def format_card_number(self):
        """Format card number into groups of 4 digits while preserving cursor reasonably."""
        s = self.clean_digits(self.card_number_var.get())
        # limit to 16 digits
        s = s[:16]
        grouped = " ".join(s[i:i+4] for i in range(0, len(s), 4))
        # avoid infinite loop of writes
        if grouped != self.card_number_var.get():
            # set and keep the cursor near the end
            self.card_number_var.set(grouped)

            try:
                self.card_number_entry.icursor(tk.END) #keeps cursor at end of textbox
            except:
                pass

    def format_expiry(self):
        """Auto-insert slash to format MM/YY. Allow partial input while typing."""
        raw = self.clean_digits(self.card_exp_var.get())
        if len(raw) == 0:
            self.card_exp_var.set("")
            return
        # take at most four digits for MMYY
        raw = raw[:4]
        if len(raw) <= 2:
            text = raw
        else:
            text = raw[:2] + "/" + raw[2:]
        if text != self.card_exp_var.get():
            self.card_exp_var.set(text)
            try:
                self.card_exp_entry.icursor(tk.END) #keeps cursor at end of textbox
            except:
                pass

    def format_cvv(self):
        """Ensure CVV contains only digits and is max 4 characters."""
        raw = "".join(filter(str.isdigit, self.card_cvv_var.get()))
        raw = raw[:4]  # max length
        if raw != self.card_cvv_var.get():
            self.card_cvv_var.set(raw)
            self.card_cvv_entry.icursor(tk.END)

    def luhn_check(self, card_number: str) -> bool:
        """Return True if card_number (digits only) passes Luhn checksum."""
        digits = [int(d) for d in card_number if d.isdigit()]
        if len(digits) < 12:
            return False
        checksum = 0
        dbl = False
        for d in reversed(digits):
            if dbl:
                d = d * 2
                if d > 9:
                    d -= 9
            checksum += d
            dbl = not dbl
        return checksum % 10 == 0

    def validate_cvv(self, cvv: str, card_number_digits: str) -> bool:
        """Basic CVV validation: 3 digits for most cards, 4 for Amex (starts with 34 or 37)."""
        if not cvv.isdigit():
            return False
        if len(card_number_digits) >= 2 and card_number_digits[:2] in ("34", "37"):
            return len(cvv) == 4  # Amex
        return len(cvv) == 3

    # -------------------------
    # Payment processor UI
    # -------------------------
    def show_payment_processor(self, amount: float, card_last4: str, callback):
        """Display a modal fake payment processing dialog.
        callback(success: bool, auth_code: Optional[str]) will be called after processing.
        """
        proc = tk.Toplevel(self)
        proc.title("Processing Payment")
        proc.transient(self)
        proc.grab_set()  # modal

        # Set fixed size
        popup_w, popup_h = 320, 140
        proc.geometry(f"{popup_w}x{popup_h}")
        proc.configure(bg=BG_COLOR)
        proc.resizable(False, False)


        # --- Center the window on screen ---
        proc.update_idletasks()  # ensure geometry is calculated
        screen_w = proc.winfo_screenwidth()
        screen_h = proc.winfo_screenheight()

        x = (screen_w // 2) - (popup_w // 2)
        y = (screen_h // 2) - (popup_h // 2)

        proc.geometry(f"{popup_w}x{popup_h}+{x}+{y}")
        # ----------------------------------

        ttk.Label(proc, text="Processing payment...", background=BG_COLOR,
                  foreground=FG_COLOR, font=("Arial", 12, "bold")).pack(pady=(12, 6))

        from tkinter.ttk import Progressbar
        pb = Progressbar(proc, mode="indeterminate", length=260)
        pb.pack(pady=(6, 10))
        pb.start(12)

        status_label = ttk.Label(proc, text="Authorizing...", background=BG_COLOR, foreground=FG_COLOR)
        status_label.pack()

        def finish(success: bool):
            pb.stop()
            status_label.config(text="Approved" if success else "Declined")

            # Show result text
            if success:
                auth = f"AUTH-{int(100000 + (hash(card_last4) % 899999))}"
                ttk.Label(proc, text=f"Auth Code: {auth}",
                          background=BG_COLOR, foreground=FG_COLOR).pack(pady=(6, 0))
            else:
                ttk.Label(proc, text="Payment declined. Try a different card or cash.",
                          background=BG_COLOR, foreground=FG_COLOR).pack(pady=(6, 0))

            # Close after 3 seconds
            proc.after(3000, lambda: (proc.grab_release(), proc.destroy(), callback(success)))

        return proc, finish

    def toggle_payment_fields(self):
        #Show or hide credit card fields depending on the payment method.
        if self.payment_method.get() == "card":
            self.card_frame.grid()
        else:
            self.card_frame.grid_remove()

    def _after_payment(self, success, first, last, email, phone, addr1, addr2, city, state, postal, room_id, check_in,
                       check_out, num_guests, nights):
        """Called after fake processor finishes. If success -> insert guest & reservation."""
        if not success:
            messagebox.showerror("Payment Failed", "Payment was declined. Please try another card or choose cash.")
            return

        # create guest
        guest_id = self.controller.db.add_guest(
            first, last, email, addr1, city,
            state, postal, phone, addr2
        )

        reservation_id = self.controller.hotel.reserve_room(
            guest_id=guest_id,
            room_id=room_id,
            check_in=check_in,
            check_out=check_out,
            num_guests=num_guests,
            status="Confirmed",
            is_paid=self.is_paid_var.get()
        )

        messagebox.showinfo("Reservation Created", f"Reservation #{reservation_id} created successfully!")
        self.controller.show_frame("main_menu")