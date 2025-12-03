import tkinter as tk
from tkinter import ttk, messagebox
from room_search_popup import RoomSearchPopup
import calendar
from datetime import date, datetime

BG_COLOR = "#2C3E50"
PANEL_BG = "#34495E"
FG_COLOR = "white"


class ReservationFormFrame(tk.Frame):
    def __init__(self, parent, controller: "HotelApp"):
        super().__init__(parent, bg=BG_COLOR)
        self.controller = controller

        #===============================
        # Centered Wrapper
        #===============================
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

        #===============================
        # SIDE-BY-SIDE MAIN FRAME
        #===============================
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
            width=450,
            labelanchor="n"
        )
        reserve_frame.pack(fill="both")

        self.num_guests_var = tk.IntVar(value=1)
        self.check_in_var = tk.StringVar()
        self.check_out_var = tk.StringVar()
        self.include_smoking_var = tk.BooleanVar(value=True)

        tk.Label(reserve_frame, text="Number of Guests:", bg=PANEL_BG, fg=FG_COLOR)\
            .grid(row=0, column=0, sticky="e", pady=6)
        tk.Spinbox(reserve_frame, from_=1, to=20, textvariable=self.num_guests_var, width=5)\
            .grid(row=0, column=1, pady=6)

        tk.Label(reserve_frame, text="Check-In (YYYY-MM-DD):", bg=PANEL_BG, fg=FG_COLOR)\
            .grid(row=1, column=0, sticky="e", pady=6)
        tk.Entry(reserve_frame, textvariable=self.check_in_var, width=18)\
            .grid(row=1, column=1, pady=6)

        tk.Label(reserve_frame, text="Check-Out (YYYY-MM-DD):", bg=PANEL_BG, fg=FG_COLOR)\
            .grid(row=2, column=0, sticky="e", pady=6)
        tk.Entry(reserve_frame, textvariable=self.check_out_var, width=18)\
            .grid(row=2, column=1, pady=6)

        tk.Checkbutton(
            reserve_frame,
            text="Include Smoking Rooms?",
            variable=self.include_smoking_var,
            bg=PANEL_BG,
            fg=FG_COLOR,
            selectcolor=PANEL_BG
        ).grid(row=3, column=0, columnspan=2, pady=10, sticky="w")

        tk.Button(
            reserve_frame,
            text="Search for Rooms",
            width=18,
            command=self.open_room_search_popup
        ).grid(row=4,column=0, columnspan=2, pady=10, sticky="e")

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


    #-------------------------------------------------------------------
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
        self.check_in_var.set("")
        self.check_out_var.set("")
        self.include_smoking_var.set(True)

    #--------------------------------------------------------------------
    def open_room_search_popup(self):
        check_in = self.check_in_var.get().strip()
        check_out = self.check_out_var.get().strip()
        num_guests = self.num_guests_var.get()
        include_smoking = 1 if self.include_smoking_var.get() else 0

        if not check_in or not check_out:
            messagebox.showerror("Error", "Please enter both check-in and check-out dates.")
            return

        try:
            check_in = datetime.strptime(check_in, "%Y-%m-%d").date()
            check_out = datetime.strptime(check_out, "%Y-%m-%d").date()
        except ValueError:
            messagebox.showerror("Invalid Date", "Dates must be in the format YYYY-MM-DD")
            return

        RoomSearchPopup(self, self.controller, check_in, check_out, num_guests, include_smoking)


    #-------------------------------------------------------------------
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

        # Placeholder
        messagebox.showinfo("Success", "Reservation saved (database insert coming soon!)")
        self.controller.show_frame("main_menu")

