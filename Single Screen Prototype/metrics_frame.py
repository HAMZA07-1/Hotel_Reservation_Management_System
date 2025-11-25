import tkinter as tk
from tkinter import ttk, messagebox
from database_manager import DatabaseManager
import sqlite3

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
            font=("Arial", 16, "bold")
        ).pack(pady=12)

        # --------- Main frame ----------
        frame = tk.Frame(self, bg="#395A7F")
        frame.pack(fill="both", expand=True, padx=12, pady=6)

        # value labels (updated by queries)
        self.total_rooms_var = tk.StringVar(value="-")
        self.available_rooms_var = tk.StringVar(value="-")
        self.active_res_var = tk.StringVar(value="-")
        self.cancelled_res_var = tk.StringVar(value="-")

        # ---------- DB helpers ----------
        def query_count(sql, params=()):
            conn = None
            try:
                conn = db.connect()
                cur = conn.cursor()
                cur.execute(sql, params)
                row = cur.fetchone()
                return row[0] if row is not None else 0
            except sqlite3.Error as e:
                msg = str(e).lower()
                # If a table doesn't exist yet, treat as zero
                if "no such table" in msg:
                    return 0
                # Other DB errors shown as popup
                messagebox.showerror("Database error", str(e))
                return 0
            finally:
                if conn:
                    conn.close()

        def load_total_rooms():
            n = query_count("SELECT COUNT(*) FROM rooms")
            self.total_rooms_var.set(str(n))

        def load_available_rooms():
            n = query_count("SELECT COUNT(*) FROM rooms WHERE is_available = 1")
            self.available_rooms_var.set(str(n))

        def load_active_reservations():
            # Active statuses: Confirmed + Checked-in
            n = query_count(
                "SELECT COUNT(*) FROM reservations WHERE status IN (?, ?)",
                ("Confirmed", "Checked-in"),
            )
            self.active_res_var.set(str(n))

        def load_cancelled_reservations():
            n = query_count(
                "SELECT COUNT(*) FROM reservations WHERE status = ?",
                ("Cancelled",),
            )
            self.cancelled_res_var.set(str(n))

        def refresh_all():
            load_total_rooms()
            load_available_rooms()
            load_active_reservations()
            load_cancelled_reservations()

        # Store for use in refresh()
        self._refresh_all = refresh_all

        # ---------- Buttons + labels layout ----------
        btn1 = tk.Button(frame, text="Total rooms", width=18, command=load_total_rooms)
        btn1.grid(row=0, column=0, padx=8, pady=8)
        lbl1 = tk.Label(
            frame,
            textvariable=self.total_rooms_var,
            width=10,
            bg="white",
            relief="sunken",
        )
        lbl1.grid(row=0, column=1, padx=8, pady=8)

        btn2 = tk.Button(frame, text="Available rooms", width=18, command=load_available_rooms)
        btn2.grid(row=1, column=0, padx=8, pady=8)
        lbl2 = tk.Label(
            frame,
            textvariable=self.available_rooms_var,
            width=10,
            bg="white",
            relief="sunken",
        )
        lbl2.grid(row=1, column=1, padx=8, pady=8)

        btn3 = tk.Button(frame, text="Active reservations", width=18, command=load_active_reservations)
        btn3.grid(row=2, column=0, padx=8, pady=8)
        lbl3 = tk.Label(
            frame,
            textvariable=self.active_res_var,
            width=10,
            bg="white",
            relief="sunken",
        )
        lbl3.grid(row=2, column=1, padx=8, pady=8)

        btn4 = tk.Button(frame, text="Cancelled reservations", width=18, command=load_cancelled_reservations)
        btn4.grid(row=3, column=0, padx=8, pady=8)
        lbl4 = tk.Label(
            frame,
            textvariable=self.cancelled_res_var,
            width=10,
            bg="white",
            relief="sunken",
        )
        lbl4.grid(row=3, column=1, padx=8, pady=8)

        # Refresh all button
        refresh_btn = tk.Button(self, text="Refresh all", command=refresh_all)
        refresh_btn.pack(pady=(2, 10))

        # Back button (returns to main menu – change target if you like)
        back_btn = tk.Button(
            self,
            text="Back",
            command=lambda: controller.show_frame("main_menu"),
        )
        back_btn.pack(pady=(0, 6))

        # Initial load
        refresh_all()

    def refresh(self):
        """Called whenever this screen is shown."""
        # Re-query everything when user opens the metrics screen
        if hasattr(self, "_refresh_all"):
            self._refresh_all()
