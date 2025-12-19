import tkinter as tk
from tkinter import messagebox
from database_manager import DatabaseManager

db = DatabaseManager()


class MetricsFrame(tk.Frame):
    def __init__(self, parent, controller: "HotelApp"):
        super().__init__(parent, bg="#2C3E50")
        self.controller = controller

        # ---------------- TITLE ----------------
        tk.Label(
            self,
            text="Hotel Metrics Dashboard",
            bg="#2C3E50",
            fg="white",
            font=("Arial", 32, "bold"),
        ).pack(pady=(20, 10))

        # Main wrapper
        self.wrapper = tk.Frame(self, bg="#2C3E50")
        self.wrapper.pack(fill="both", expand=True)

        # Data variables
        self.vars = {
            "occupancy_rate": tk.StringVar(value="--%"),
            "rooms_occupied": tk.StringVar(value="--"),
            "rooms_available": tk.StringVar(value="--"),

            "revenue_total": tk.StringVar(value="$0.00"),
            "adr": tk.StringVar(value="$0.00"),
            "revpar": tk.StringVar(value="$0.00"),

            "checkins_today": tk.StringVar(value="--"),
            "checkouts_today": tk.StringVar(value="--"),
            "upcoming_res": tk.StringVar(value="--"),

            "rooms_oos": tk.StringVar(value="--"),
            "rooms_cleaning": tk.StringVar(value="--"),
            "avg_stay": tk.StringVar(value="--"),

            "payments_today": tk.StringVar(value="$0.00"),
            "outstanding_bal": tk.StringVar(value="$0.00"),

            "popular_room": tk.StringVar(value="--"),
            "avg_group_size": tk.StringVar(value="--"),
            "smoking_ratio": tk.StringVar(value="--%"),
        }

        # --- Grid layout: 4 columns ---
        self.wrapper.grid_columnconfigure((0,1,2,3), weight=1)

        # Add sections
        self._build_section_header("Occupancy Metrics", 0, 0)
        self._metric_card("Occupancy Rate", "occupancy_rate", 1, 0)
        self._metric_card("Occupied Rooms", "rooms_occupied", 2, 0)
        self._metric_card("Available Rooms", "rooms_available", 3, 0)

        self._build_section_header("Revenue Metrics", 0, 1)
        self._metric_card("Total Revenue", "revenue_total", 1, 1)
        self._metric_card("ADR", "adr", 2, 1)
        self._metric_card("RevPAR", "revpar", 3, 1)

        self._build_section_header("Guest & Reservation Flow", 0, 2)
        self._metric_card("Check-ins Today", "checkins_today", 1, 2)
        self._metric_card("Check-outs Today", "checkouts_today", 2, 2)
        self._metric_card("Upcoming (7 days)", "upcoming_res", 3, 2)

        self._build_section_header("Operational Metrics", 0, 3)
        self._metric_card("Out-of-Service Rooms", "rooms_oos", 1, 3)
        self._metric_card("Rooms Cleaning", "rooms_cleaning", 2, 3)
        self._metric_card("Average Stay Length", "avg_stay", 3, 3)

        self._build_section_header("Financial Metrics", 0, 4)
        self._metric_card("Payments Today", "payments_today", 1, 4, wide=True)
        self._metric_card("Outstanding Balance", "outstanding_bal", 2, 4, wide=True)

        self._build_section_header("Guest Demographics", 0, 5)
        self._metric_card("Popular Room Type", "popular_room", 1, 5, wide=True)
        self._metric_card("Average Group Size", "avg_group_size", 2, 5, wide=True)
        self._metric_card("Smoking %", "smoking_ratio", 3, 5, wide=True)

        # Refresh + Back
        tk.Button(
            self,
            text="Refresh Dashboard",
            font=("Arial", 14, "bold"),
            command=self._load_from_db,
        ).pack(pady=10)

        tk.Button(
            self,
            text="Back",
            command=lambda: controller.show_frame("main_menu"),
            width=12
        ).pack(pady=(0, 10))

        # Load initial data
        self._load_from_db()



    # ---------- UI HELPERS ----------
    def _build_section_header(self, text, row, col):
        lbl = tk.Label(
            self.wrapper,
            text=text,
            font=("Arial", 20, "bold"),
            bg="#2C3E50",
            fg="white",
            anchor="w"
        )
        lbl.grid(row=row, column=col, sticky="w", padx=20, pady=(20,5))


    def _metric_card(self, label, var_name, row, col, wide=False):
        width = 32 if wide else 18

        frame = tk.Frame(
            self.wrapper,
            bg="#E8EEF4",
            bd=0,
            highlightthickness=0
        )
        frame.grid(row=row, column=col, padx=20, pady=10, sticky="nsew")

        frame.grid_columnconfigure(0, weight=1)

        tk.Label(
            frame,
            text=label,
            font=("Arial", 14, "bold"),
            bg="#E8EEF4",
        ).grid(pady=(10, 2))

        tk.Label(
            frame,
            textvariable=self.vars[var_name],
            font=("Arial", 24, "bold"),
            bg="#E8EEF4",
            fg="#1B2A41"
        ).grid(pady=(0, 12))


    # --------- DB LOAD ----------
    def _load_from_db(self):
        """
        Reads DB metrics and assigns values to all dashboard cards.
        """
        try:
            metrics = db.get_manager_metrics()
        except Exception as e:
            messagebox.showerror("DB Error", str(e))
            return

        # ----- Occupancy Metrics -----
        total_rooms = metrics.get("total_rooms", 0)
        available = metrics.get("available_rooms_today", 0)
        occupied = metrics.get("rooms_occupied_today", total_rooms - available)

        self.vars["rooms_available"].set(available)
        self.vars["rooms_occupied"].set(occupied)

        occ_rate = metrics.get("occupancy_rate", 0)
        self.vars["occupancy_rate"].set(f"{occ_rate:.1f}%")

        # ----- Revenue Metrics -----
        revenue = float(metrics.get("revenue", 0.0))
        self.vars["revenue_total"].set(f"${revenue:,.2f}")

        adr = float(metrics.get("adr", 0.0))
        self.vars["adr"].set(f"${adr:,.2f}")

        revpar = float(metrics.get("revpar", 0.0))
        self.vars["revpar"].set(f"${revpar:,.2f}")

        # ----- Guest Flow Metrics -----
        self.vars["checkins_today"].set(metrics.get("checkins_today", 0))
        self.vars["checkouts_today"].set(metrics.get("checkouts_today", 0))
        self.vars["upcoming_res"].set(metrics.get("upcoming_res", 0))

        # ----- Operational Metrics -----
        self.vars["rooms_oos"].set(metrics.get("rooms_oos", 0))
        self.vars["avg_stay"].set(f"{metrics.get('avg_stay', 0):.1f} nights")

        # If you add a real cleaning metric later:
        self.vars["rooms_cleaning"].set(metrics.get("rooms_cleaning", "--"))

        # ----- Financial Metrics -----
        payments_today = float(metrics.get("payments_today", 0.0))
        self.vars["payments_today"].set(f"${payments_today:,.2f}")

        outstanding = float(metrics.get("outstanding_bal", 0.0))
        self.vars["outstanding_bal"].set(f"${outstanding:,.2f}")

        # ----- Demographic Metrics -----
        self.vars["popular_room"].set(metrics.get("popular_room", "N/A"))
        self.vars["avg_group_size"].set(f"{metrics.get('avg_group_size', 0):.1f}")

        smoking_ratio = metrics.get("smoking_ratio", 0)
        self.vars["smoking_ratio"].set(f"{smoking_ratio:.1f}%")

    def refresh(self):
        self._load_from_db()
