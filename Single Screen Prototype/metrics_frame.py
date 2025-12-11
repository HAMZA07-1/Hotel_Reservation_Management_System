import tkinter as tk
from tkinter import messagebox
from database_manager import DatabaseManager

# Shared DB manager for this frame
db = DatabaseManager()


class MetricsFrame(tk.Frame):
    def __init__(self, parent, controller: "HotelApp"):
        super().__init__(parent, bg="#395A7F")
        self.controller = controller

        # --------- Title ----------
        tk.Label(
            self,
            text="Hotel Metrics",
            bg="#395A7F",
            fg="white",
            font=("Arial", 16, "bold"),
        ).pack(pady=12)

        # --------- Main frame ---------
        frame = tk.Frame(self, bg="#395A7F")
        frame.pack(fill="both", expand=True, padx=12, pady=6)

        # values (StringVars)
        self.total_rooms_var = tk.StringVar(value="(init)")
        self.available_rooms_var = tk.StringVar(value="(init)")
        self.active_res_var = tk.StringVar(value="(init)")
        self.cancelled_res_var = tk.StringVar(value="(init)")
        self.revenue_var = tk.StringVar(value="(init)")

        # ----------- ROW 1: Total Rooms -----------
        btn1 = tk.Button(frame, text="Total rooms", width=18,
                         command=self._load_from_db)
        btn1.grid(row=0, column=0, padx=8, pady=8)

        lbl1 = tk.Label(
            frame,
            textvariable=self.total_rooms_var,
            width=14,
            bg="white",
            fg="black",
            relief="sunken",
        )
        lbl1.grid(row=0, column=1, padx=8, pady=8)

        # ----------- ROW 2: Available Rooms -----------
        btn2 = tk.Button(frame, text="Available rooms", width=18,
                         command=self._load_from_db)
        btn2.grid(row=1, column=0, padx=8, pady=8)

        lbl2 = tk.Label(
            frame,
            textvariable=self.available_rooms_var,
            width=14,
            bg="white",
            fg="black",
            relief="sunken",
        )
        lbl2.grid(row=1, column=1, padx=8, pady=8)

        # ----------- ROW 3: Active Reservations -----------
        btn3 = tk.Button(frame, text="Active reservations", width=18,
                         command=self._load_from_db)
        btn3.grid(row=2, column=0, padx=8, pady=8)

        lbl3 = tk.Label(
            frame,
            textvariable=self.active_res_var,
            width=14,
            bg="white",
            fg="black",
            relief="sunken",
        )
        lbl3.grid(row=2, column=1, padx=8, pady=8)

        # ----------- ROW 4: Cancelled Reservations -----------
        btn4 = tk.Button(frame, text="Cancelled reservations", width=18,
                         command=self._load_from_db)
        btn4.grid(row=3, column=0, padx=8, pady=8)

        lbl4 = tk.Label(
            frame,
            textvariable=self.cancelled_res_var,
            width=14,
            bg="white",
            fg="black",
            relief="sunken",
        )
        lbl4.grid(row=3, column=1, padx=8, pady=8)

        # ----------- ROW 5: Revenue (non-cancelled) -----------
        tk.Label(
            frame,
            text="Revenue (non-cancelled)",
            width=18,
            bg="#395A7F",
            fg="white",
            anchor="e",
        ).grid(row=4, column=0, padx=8, pady=8)

        lbl5 = tk.Label(
            frame,
            textvariable=self.revenue_var,
            width=14,
            bg="white",
            fg="black",
            relief="sunken",
        )
        lbl5.grid(row=4, column=1, padx=8, pady=8)

        # Refresh All button
        refresh_btn = tk.Button(self, text="Refresh all",
                                command=self._load_from_db)
        refresh_btn.pack(pady=(2, 10))

        # Back Button
        back_btn = tk.Button(
            self,
            text="Back",
            command=lambda: controller.show_frame("main_menu"),
        )
        back_btn.pack(pady=(0, 6))

        # Load initial data
        self._load_from_db()

    #   Load data from DB and push into the StringVars
    
    def _load_from_db(self):
        print("[METRICS FRAME] starting _load_from_db")
        try:
            metrics = db.get_manager_metrics()
            print("[METRICS FRAME] metrics from DB:", metrics)
        except Exception as e:
            print("[METRICS FRAME] ERROR:", repr(e))
            self.total_rooms_var.set("ERR")
            self.available_rooms_var.set("ERR")
            self.active_res_var.set("ERR")
            self.cancelled_res_var.set("ERR")
            self.revenue_var.set("ERR")
            messagebox.showerror("Database error", str(e))
            return

        # Push data into labels
        self.total_rooms_var.set(str(metrics.get("total_rooms", 0)))
        self.available_rooms_var.set(str(metrics.get("available_rooms_today", 0)))
        self.active_res_var.set(str(metrics.get("active_reservations", 0)))
        self.cancelled_res_var.set(str(metrics.get("cancelled_reservations", 0)))

        revenue = float(metrics.get("revenue", 0.0) or 0.0)
        self.revenue_var.set(f"${revenue:,.2f}")

    def refresh(self):
        """When the frame is shown."""
        self._load_from_db()
