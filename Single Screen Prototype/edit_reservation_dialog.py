# edit_reservation_dialog.py
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date, time, datetime, timedelta
import calendar

from room_search_popup import RoomSearchPopup


class EditReservationDialog(tk.Toplevel):
    """
    Full-featured dialog that handles viewing, editing, check-in, check-out,
    payment, room changes, cancellations, and saving reservation updates.
    """

    def __init__(self, parent_frame, controller, reservation_values, refresh_callback):
        super().__init__(parent_frame)

        self.parent_frame = parent_frame
        self.controller = controller
        # HotelManager instance attached to the controller (HotelApp)
        self.hotel = controller.hotel
        self.refresh_callback = refresh_callback

        # Unpack reservation row from Treeview
        self.res_id = int(reservation_values[0])
        self.guest_id = int(reservation_values[1])
        self.guest_name = reservation_values[2]
        self.room_id = int(reservation_values[3])
        self.room_number = reservation_values[4]
        self.check_in_str = reservation_values[5]
        self.check_out_str = reservation_values[6]
        self.total_price = float(reservation_values[7])
        self.status = reservation_values[9]

        # Convert dates
        self.check_in_date = datetime.strptime(self.check_in_str, "%Y-%m-%d").date()
        self.check_out_date = datetime.strptime(self.check_out_str, "%Y-%m-%d").date()

        self.today = date.today()
        self.now_time = datetime.now().time()

        # Room selection from RoomSearchPopup
        self.pending_room = None  # (room_id, room_number) or None

        self.build_window()
        self.load_reservation_data()
        self.center_window()

    # ----------------------------------------------------------
    # --- BASIC WINDOW -----------------------------------------
    # ----------------------------------------------------------
    def build_window(self):
        self.title(f"Edit Reservation #{self.res_id}")
        self.geometry("640x720")
        self.configure(bg="#2C3E50")
        self.resizable(False, False)

        # Header
        tk.Label(
            self,
            text=f"Reservation #{self.res_id}",
            font=("Arial", 18, "bold"),
            bg="#2C3E50",
            fg="white"
        ).pack(pady=10)

        tk.Label(self, text=f"Guest: {self.guest_name}", bg="#2C3E50", fg="white").pack()
        tk.Label(self, text=f"Room: {self.room_number}", bg="#2C3E50", fg="white").pack()

        tk.Label(self, text=f"Check-in: {self.check_in_str}", bg="#2C3E50", fg="white").pack()
        tk.Label(self, text=f"Check-out: {self.check_out_str}", bg="#2C3E50", fg="white").pack()

        tk.Label(
            self,
            text=f"Total: ${self.total_price:,.2f}",
            bg="#2C3E50",
            fg="white"
        ).pack(pady=(0, 15))

        # Button bar
        self.btn_frame = tk.Frame(self, bg="#2C3E50")
        self.btn_frame.pack(pady=10)

    # ----------------------------------------------------------
    # --- INITIAL BUTTON LOGIC --------------------------------
    # ----------------------------------------------------------
    def load_reservation_data(self):
        """
        Configure which buttons are visible/enabled based on
        reservation status, current date/time, and rules.
        """

        # Hotel-defined check-in cutoff (e.g., 14 => 2 PM)
        checkin_cutoff = time(self.hotel.CHECKIN_HOUR, 0)

        # ============ CHECK-IN LOGIC ======================
        # Condition 1: Today == Check-in AND time >= cutoff
        allow_today = (
                self.today == self.check_in_date and
                self.now_time >= checkin_cutoff
        )

        # Condition 2: Today is the day AFTER check-in (yesterday's reservation)
        allow_yesterday = (
                self.today == (self.check_in_date + timedelta(days=1))
        )

        allowed_statuses = (
            "Confirmed",
            "Reserved",
            "Late",
            "Late Reservation"
        )

        in_allowed_status = self.status in allowed_statuses

        can_check_in = (
                (allow_today or allow_yesterday) and in_allowed_status
        )


        # ============ CHECK-OUT LOGIC ======================
        can_check_out = (
                self.status in ("Checked-in", "Late Check-out")
                and self.today == self.check_out_date
        )

        # Active means not permanently closed
        self.is_active_reservation = self.status not in ("Complete", "Cancelled")

        # --- Buttons ---
        if can_check_in:
            tk.Button(
                self.btn_frame,
                text="Check-In",
                bg="#27AE60",
                fg="white",
                width=14,
                command=self.check_in_action
            ).pack(side="left", padx=5)

        if can_check_out:
            tk.Button(
                self.btn_frame,
                text="Check-Out",
                bg="#E67E22",
                fg="white",
                width=14,
                command=self.check_out_action
            ).pack(side="left", padx=5)

        if self.is_active_reservation:
            tk.Button(
                self.btn_frame,
                text="Edit Reservation",
                bg="#8E44AD",
                fg="white",
                width=14,
                command=self.open_edit_panel
            ).pack(side="left", padx=5)

        tk.Button(
            self.btn_frame,
            text="Cancel Reservation",
            bg="#f44336",
            fg="white",
            width=16,
            command=self.cancel_action
        ).pack(side="left", padx=5)

        tk.Button(
            self.btn_frame,
            text="Close",
            width=10,
            command=self.destroy
        ).pack(side="left", padx=5)

    # ----------------------------------------------------------
    # --- CHECK IN --------------------------------------------
    # ----------------------------------------------------------
    def check_in_action(self):
        """
        Use HotelManager.check_in_reservation. If unpaid, show the payment UI.
        """
        try:
            result = self.hotel.check_in_reservation(
                self.res_id,
                confirm_payment=False  # first try without forcing payment change
            )

            messagebox.showinfo(
                "Check-In Complete",
                (
                    f"{result['message']}\n"
                    f"Checked in at: {result['checked_in_at']}\n"
                    f"Payment Settled: {'Yes' if result['payment_settled'] else 'No'}"
                )
            )
            self.refresh()
            self.destroy()

        except Exception as e:
            msg = str(e)

            # If the only problem is unpaid status → open payment UI
            if "Payment of" in msg or "Check-in Denied" in msg:
                self.show_payment_ui()
            else:
                messagebox.showerror("Check-In Failed", msg)

    # ----------------------------------------------------------
    # --- PAYMENT UI -------------------------------------------
    # ----------------------------------------------------------
    def show_payment_ui(self):
        """Show a cash/card payment section; upon success, perform check-in."""

        if hasattr(self, "payment_frame") and self.payment_frame.winfo_exists():
            return

        self.payment_frame = tk.LabelFrame(
            self,
            text="Payment Required",
            bg="#2C3E50",
            fg="white",
            padx=15,
            pady=15,
            labelanchor="n"
        )
        self.payment_frame.pack(fill="both", padx=10, pady=10)

        payment_method = tk.StringVar(value="card")

        # --- Radio buttons ---
        ttk.Radiobutton(
            self.payment_frame, text="Cash", value="cash", variable=payment_method
        ).grid(row=0, column=0, sticky="w")
        ttk.Radiobutton(
            self.payment_frame, text="Credit Card", value="card", variable=payment_method
        ).grid(row=1, column=0, sticky="w")

        # --- CARD SECTION ---
        self.card_section = tk.Frame(self.payment_frame, bg="#2C3E50")
        self.card_section.grid(row=2, column=0, sticky="w", pady=10)

        tk.Label(self.card_section, text="Cardholder Name:", bg="#2C3E50", fg="white") \
            .grid(row=0, column=0, sticky="w")
        self.card_name = tk.StringVar()
        tk.Entry(self.card_section, textvariable=self.card_name).grid(row=0, column=1, padx=5, pady=2)

        tk.Label(self.card_section, text="Card Number:", bg="#2C3E50", fg="white") \
            .grid(row=1, column=0, sticky="w")
        self.card_num = tk.StringVar()
        tk.Entry(self.card_section, textvariable=self.card_num).grid(row=1, column=1, padx=5, pady=2)

        tk.Label(self.card_section, text="Exp (MMYY):", bg="#2C3E50", fg="white") \
            .grid(row=2, column=0, sticky="w")
        self.card_exp = tk.StringVar()
        tk.Entry(self.card_section, textvariable=self.card_exp, width=8) \
            .grid(row=2, column=1, padx=5, pady=2)

        tk.Label(self.card_section, text="CVV:", bg="#2C3E50", fg="white") \
            .grid(row=3, column=0, sticky="w")
        self.card_cvv = tk.StringVar()
        tk.Entry(self.card_section, textvariable=self.card_cvv, width=6, show="*") \
            .grid(row=3, column=1, padx=5, pady=2)

        # --- CASH SECTION ---
        self.cash_section = tk.Frame(self.payment_frame, bg="#2C3E50")
        self.cash_section.grid(row=3, column=0, sticky="w", pady=10)

        tk.Label(self.cash_section, text="Amount Received:", bg="#2C3E50", fg="white") \
            .grid(row=0, column=0, sticky="w")
        self.cash_amount = tk.StringVar()
        tk.Entry(self.cash_section, textvariable=self.cash_amount, width=10) \
            .grid(row=0, column=1, padx=5, pady=2)

        self.change_label = tk.Label(
            self.cash_section,
            text="Change Due: $0.00",
            bg="#2C3E50",
            fg="white"
        )
        self.change_label.grid(row=1, column=0, columnspan=2, sticky="w", pady=(4, 0))

        def update_change(*_):
            try:
                received = float(self.cash_amount.get())
                change = received - self.total_price
                if change < 0:
                    self.change_label.config(text=f"Short by ${abs(change):.2f}")
                else:
                    self.change_label.config(text=f"Change Due: ${change:.2f}")
            except ValueError:
                if self.cash_amount.get().strip() == "":
                    self.change_label.config(text="Change Due: $0.00")
                else:
                    self.change_label.config(text="Invalid amount")

        self.cash_amount.trace_add("write", update_change)

        def toggle_sections(*_):
            if payment_method.get() == "cash":
                self.cash_section.grid()
                self.card_section.grid_remove()
            else:
                self.card_section.grid()
                self.cash_section.grid_remove()

        payment_method.trace_add("write", toggle_sections)
        toggle_sections()

        tk.Button(
            self.payment_frame,
            text="Submit Payment",
            bg="#2980B9",
            fg="white",
            width=18,
            command=lambda: self.process_payment(payment_method.get())
        ).grid(row=4, column=0, pady=10)

    def process_payment(self, method):
        """Validate payment input, mark reservation paid, then call check_in_reservation with confirm_payment."""

        # Basic validation
        if method == "card":
            if not (self.card_name.get().strip()
                    and self.card_num.get().strip()
                    and self.card_exp.get().strip()
                    and self.card_cvv.get().strip()):
                messagebox.showwarning("Missing Fields", "Please complete all credit card fields.")
                return
        else:  # Cash
            try:
                received = float(self.cash_amount.get())
            except ValueError:
                messagebox.showwarning("Invalid Input", "Enter a numeric amount.")
                return

            if received < self.total_price:
                messagebox.showwarning(
                    "Insufficient Amount",
                    "Amount received is less than total price."
                )
                return

        try:
            # Mark as paid in DB
            conn = self.controller.db.connect()
            cur = conn.cursor()
            cur.execute(
                "UPDATE reservations SET is_paid = 1 WHERE reservation_id = ?",
                (self.res_id,)
            )
            conn.commit()
            conn.close()

            # Now perform actual check-in with confirm_payment=True
            result = self.hotel.check_in_reservation(
                self.res_id,
                confirm_payment=True
            )

            messagebox.showinfo("Check-In Complete", result["message"])
            self.refresh()
            self.destroy()

        except Exception as e:
            messagebox.showerror("Payment Error", str(e))

    # ----------------------------------------------------------
    # --- CHECK OUT -------------------------------------------
    # ----------------------------------------------------------
    def check_out_action(self):
        """Use HotelManager.check_out_reservation to handle late fees, etc."""
        try:
            result = self.hotel.check_out_reservation(self.res_id)

            messagebox.showinfo(
                "Checked Out",
                (
                    f"{result['message']}\n\n"
                    f"Original Price: ${result['original_price']:.2f}\n"
                    f"Late Fee: ${result['late_fee']:.2f}\n"
                    f"Final Price: ${result['final_price']:.2f}\n"
                    f"Paid: {'Yes' if result['is_paid'] else 'No'}"
                )
            )
            self.refresh()
            self.destroy()

        except Exception as e:
            messagebox.showerror("Check-Out Failed", str(e))

    # ----------------------------------------------------------
    # --- CANCEL RESERVATION ----------------------------------
    # ----------------------------------------------------------
    def cancel_action(self):
        if not messagebox.askyesno(
            "Confirm Cancel",
            "Are you sure you want to cancel this reservation?\n"
            "Cancellation fees may apply."
        ):
            return

        try:
            result = self.hotel.cancel_reservation(self.res_id)

            messagebox.showinfo(
                "Cancelled",
                (
                    f"Reservation cancelled.\n\n"
                    f"Reason: {result['reason']}\n"
                    f"Original Price: ${result['original_price']:.2f}\n"
                    f"Fee: ${result['cancellation_fee']:.2f}\n"
                    f"Refund: ${result['refund_amount']:.2f}"
                )
            )

            self.refresh()
            self.destroy()

        except Exception as e:
            messagebox.showerror("Cancellation Failed", str(e))

    # ----------------------------------------------------------
    # --- OPEN EDIT PANEL --------------------------------------
    # ----------------------------------------------------------
    def open_edit_panel(self):
        """Create (or lift) the embedded edit form for dates/guests/room."""

        if hasattr(self, "edit_frame") and self.edit_frame.winfo_exists():
            self.edit_frame.lift()
            return

        self.edit_frame = tk.LabelFrame(
            self,
            text="Edit Reservation",
            bg="#2C3E50",
            fg="white",
            padx=15,
            pady=15,
            labelanchor="n"
        )
        self.edit_frame.pack(fill="both", padx=10, pady=10)

        if not self.is_active_reservation:
            tk.Label(
                self.edit_frame,
                text="This reservation is not editable.",
                bg="#2C3E50",
                fg="white"
            ).pack()
            return

        # Guests
        tk.Label(self.edit_frame, text="Guests:", bg="#2C3E50", fg="white") \
            .grid(row=0, column=0, sticky="e")
        self.edit_guests = tk.IntVar(value=1)
        tk.Spinbox(
            self.edit_frame,
            from_=1,
            to=6,
            textvariable=self.edit_guests,
            width=5
        ).grid(row=0, column=1, sticky="w", padx=4, pady=4)

        # Smoking preference for search only
        self.edit_smoking = tk.BooleanVar(value=True)
        tk.Checkbutton(
            self.edit_frame,
            text="Smoking OK",
            variable=self.edit_smoking,
            bg="#2C3E50",
            fg="white",
            selectcolor="#2C3E50"
        ).grid(row=0, column=2, padx=10, sticky="w")

        # Date controls
        self.build_edit_dates()

        # Current room label
        self.room_label = tk.Label(
            self.edit_frame,
            text=f"Current Room #: {self.room_number}",
            bg="#2C3E50",
            fg="white",
            font=("Arial", 11, "bold")
        )
        self.room_label.grid(row=3, column=0, columnspan=4, sticky="w", pady=(10, 4))

        # Room search button
        tk.Button(
            self.edit_frame,
            text="Search for Rooms",
            width=18,
            command=self.search_rooms
        ).grid(row=4, column=0, columnspan=4, pady=8, sticky="e")

        # Save button
        tk.Button(
            self.edit_frame,
            text="Save Changes",
            bg="#16A085",
            fg="white",
            width=14,
            command=self.save_changes
        ).grid(row=5, column=0, columnspan=2, pady=10, sticky="w")

    # ----------------------------------------------------------
    # --- DATE EDITING UI --------------------------------------
    # ----------------------------------------------------------
    def build_edit_dates(self):
        """Build the editable date controls with 1–30 night constraints."""

        self.edit_ci_year = tk.IntVar(value=self.check_in_date.year)
        self.edit_ci_month = tk.IntVar(value=self.check_in_date.month)
        self.edit_ci_day = tk.IntVar(value=self.check_in_date.day)

        self.edit_co_year = tk.IntVar(value=self.check_out_date.year)
        self.edit_co_month = tk.IntVar(value=self.check_out_date.month)
        self.edit_co_day = tk.IntVar(value=self.check_out_date.day)

        # Check-In row
        tk.Label(self.edit_frame, text="Check-In:", bg="#2C3E50", fg="white") \
            .grid(row=1, column=0, sticky="e")

        ci_year_cb = ttk.Combobox(
            self.edit_frame,
            textvariable=self.edit_ci_year,
            values=[self.check_in_date.year, self.check_in_date.year + 1],
            state="readonly",
            width=6
        )
        ci_year_cb.grid(row=1, column=1, padx=2, sticky="w")

        ci_month_cb = ttk.Combobox(
            self.edit_frame,
            textvariable=self.edit_ci_month,
            values=list(range(1, 13)),
            state="readonly",
            width=4
        )
        ci_month_cb.grid(row=1, column=2, padx=2, sticky="w")

        ci_day_cb = ttk.Combobox(
            self.edit_frame,
            textvariable=self.edit_ci_day,
            width=4,
            state="readonly"
        )
        ci_day_cb.grid(row=1, column=3, padx=2, sticky="w")

        # Check-Out row
        tk.Label(self.edit_frame, text="Check-Out:", bg="#2C3E50", fg="white") \
            .grid(row=2, column=0, sticky="e")

        co_year_cb = ttk.Combobox(
            self.edit_frame,
            textvariable=self.edit_co_year,
            values=[self.check_out_date.year, self.check_out_date.year + 1],
            state="readonly",
            width=6
        )
        co_year_cb.grid(row=2, column=1, padx=2, sticky="w")

        co_month_cb = ttk.Combobox(
            self.edit_frame,
            textvariable=self.edit_co_month,
            values=list(range(1, 13)),
            state="readonly",
            width=4
        )
        co_month_cb.grid(row=2, column=2, padx=2, sticky="w")

        co_day_cb = ttk.Combobox(
            self.edit_frame,
            textvariable=self.edit_co_day,
            width=4,
            state="readonly"
        )
        co_day_cb.grid(row=2, column=3, padx=2, sticky="w")

        def update_days(year_var, month_var, day_var, cb):
            y, m = year_var.get(), month_var.get()
            if not y or not m:
                return
            days = calendar.monthrange(y, m)[1]
            valid = list(range(1, days + 1))
            cb["values"] = valid
            if day_var.get() not in valid:
                day_var.set(valid[0])

        update_days(self.edit_ci_year, self.edit_ci_month, self.edit_ci_day, ci_day_cb)
        update_days(self.edit_co_year, self.edit_co_month, self.edit_co_day, co_day_cb)

        def enforce(*_):
            try:
                ci = date(self.edit_ci_year.get(), self.edit_ci_month.get(), self.edit_ci_day.get())
                co = date(self.edit_co_year.get(), self.edit_co_month.get(), self.edit_co_day.get())
            except Exception:
                return

            min_co = ci + timedelta(days=1)
            max_co = ci + timedelta(days=30)

            if co < min_co:
                co = min_co
            if co > max_co:
                co = max_co

            self.edit_co_year.set(co.year)
            self.edit_co_month.set(co.month)
            self.edit_co_day.set(co.day)

            update_days(self.edit_co_year, self.edit_co_month, self.edit_co_day, co_day_cb)

        self.edit_ci_year.trace_add(
            "write",
            lambda *_: (update_days(self.edit_ci_year, self.edit_ci_month, self.edit_ci_day, ci_day_cb), enforce())
        )
        self.edit_ci_month.trace_add(
            "write",
            lambda *_: (update_days(self.edit_ci_year, self.edit_ci_month, self.edit_ci_day, ci_day_cb), enforce())
        )
        self.edit_ci_day.trace_add("write", lambda *_: enforce())

        self.edit_co_year.trace_add(
            "write",
            lambda *_: (update_days(self.edit_co_year, self.edit_co_month, self.edit_co_day, co_day_cb), enforce())
        )
        self.edit_co_month.trace_add(
            "write",
            lambda *_: (update_days(self.edit_co_year, self.edit_co_month, self.edit_co_day, co_day_cb), enforce())
        )
        self.edit_co_day.trace_add("write", lambda *_: enforce())

    # ----------------------------------------------------------
    # --- ROOM SEARCH ------------------------------------------
    # ----------------------------------------------------------
    def search_rooms(self):
        """Open RoomSearchPopup using current edited dates/guests/smoking."""

        try:
            ci = date(self.edit_ci_year.get(), self.edit_ci_month.get(), self.edit_ci_day.get())
            co = date(self.edit_co_year.get(), self.edit_co_month.get(), self.edit_co_day.get())
        except Exception:
            messagebox.showerror("Invalid Dates", "Please enter valid check-in and check-out dates.")
            return

        if co <= ci:
            messagebox.showerror("Invalid Dates", "Check-out must be after check-in.")
            return

        guests = self.edit_guests.get()
        include_smoking = 1 if self.edit_smoking.get() else 0

        RoomSearchPopup(
            parent=self.parent_frame,
            controller=self.controller,
            check_in=ci,
            check_out=co,
            num_guests=guests,
            include_smoking=include_smoking
        )

    # Called from BookingRecordsFrame.set_selected_room()
    def set_new_room(self, room_id, room_number):
        """Update dialog with the room selected from the RoomSearchPopup."""
        self.pending_room = (room_id, room_number)
        if hasattr(self, "room_label") and self.room_label.winfo_exists():
            self.room_label.config(text=f"Current Room #: {room_number}")

    # ----------------------------------------------------------
    # --- SAVE CHANGES -----------------------------------------
    # ----------------------------------------------------------
    def save_changes(self):
        """Validate inputs then delegate the update to HotelManager.update_reservation."""

        # Guests
        guests = self.edit_guests.get()
        if not (1 <= guests <= 6):
            messagebox.showerror("Invalid Guests", "Number of guests must be between 1 and 6.")
            return

        # Dates
        try:
            ci = date(self.edit_ci_year.get(), self.edit_ci_month.get(), self.edit_ci_day.get())
            co = date(self.edit_co_year.get(), self.edit_co_month.get(), self.edit_co_day.get())
        except Exception:
            messagebox.showerror("Invalid Dates", "Please select valid check-in and check-out dates.")
            return

        if ci < self.today:
            messagebox.showerror("Invalid Date", "Check-in date cannot be in the past.")
            return

        if co <= ci:
            messagebox.showerror("Invalid Dates", "Check-out must be after check-in.")
            return

        # Room (optional change)
        new_room_id = None
        if self.pending_room:
            new_room_id = self.pending_room[0]

        try:
            result = self.hotel.update_reservation(
                reservation_id=self.res_id,
                new_room_id=new_room_id,
                new_check_in=ci.isoformat(),
                new_check_out=co.isoformat(),
                new_num_guests=guests,
                is_paid=None
            )

            messagebox.showinfo(
                "Success",
                (
                    "Reservation Updated\n\n"
                    f"Old Total: ${result['old_price']:.2f}\n"
                    f"New Total: ${result['new_price']:.2f}\n"
                    f"Difference: ${result['difference']:.2f}\n"
                    f"Paid: {'Yes' if result['is_paid'] else 'No'}"
                )
            )

            self.refresh()
            self.destroy()

        except Exception as e:
            messagebox.showerror("Update Failed", str(e))

    def center_window(self):
        """Center this dialog on the screen."""
        self.update_idletasks()  # Ensure geometry is calculated

        win_width = self.winfo_width()
        win_height = self.winfo_height()

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        x = (screen_width // 2) - (win_width // 2)
        y = (screen_height // 2) - (win_height // 2)

        self.geometry(f"{win_width}x{win_height}+{x}+{y}")

    # ----------------------------------------------------------
    def refresh(self):
        """Refresh the main table via callback from BookingRecordsFrame."""
        if self.refresh_callback:
            self.refresh_callback()
