import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import os
import sys

# Ensure repository root is on sys.path so imports from repo root work
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

from database_manager import DatabaseManager

BG_APP = "#2C3E50"
PANEL_BG = "#34495E"
ACCENT = "#1ABC9C"

db = DatabaseManager()


class LoginFrame(tk.Frame):
    def __init__(self, parent, controller: "HotelApp"):
        super().__init__(parent, bg=BG_APP)
        self.controller = controller

        # Variables
        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.role_var = tk.StringVar(value="Manager")

        # Make frame stretch
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # --------- OUTER CONTAINER (CENTERED) ---------
        container = tk.Frame(self, bg=BG_APP)
        container.grid(row=0, column=0, sticky="nsew")
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # --------- MODERN LOGIN CARD ---------
        card = tk.Frame(
            container,
            bg=PANEL_BG,
            padx=40,
            pady=40,
            highlightthickness=2,
            highlightbackground="#1f2e3b",
        )
        card.grid(row=0, column=0)

        # Title
        title = tk.Label(
            card,
            text="Hotel Employee Login",
            bg=PANEL_BG,
            fg="white",
            font=("Segoe UI", 26, "bold")
        )
        title.grid(row=0, column=0, columnspan=2, pady=(0, 30))

        # Labels
        lbl_user = tk.Label(
            card, text="Employee ID:", bg=PANEL_BG, fg="white",
            font=("Segoe UI", 12)
        )
        lbl_pass = tk.Label(
            card, text="Password:", bg=PANEL_BG, fg="white",
            font=("Segoe UI", 12)
        )

        lbl_user.grid(row=1, column=0, sticky="e", padx=10, pady=10)
        lbl_pass.grid(row=2, column=0, sticky="e", padx=10, pady=10)

        # Entry styling
        entry_style = {"width": 25, "font": ("Segoe UI", 11), "bd": 2, "relief": "groove"}

        entry_username = tk.Entry(card, textvariable=self.username_var, **entry_style)
        entry_password = tk.Entry(card, show="*", textvariable=self.password_var, **entry_style)

        entry_username.grid(row=1, column=1, pady=10, padx=5)
        entry_password.grid(row=2, column=1, pady=10, padx=5)

        # Modern Login Button
        login_btn = tk.Button(
            card,
            text="Login",
            command=self.check_credentials,
            font=("Segoe UI", 12, "bold"),
            bg=ACCENT,
            fg="white",
            activebackground="#16a085",
            activeforeground="white",
            relief="flat",
            padx=15,
            pady=5,
            width=18,
        )
        login_btn.grid(row=3, column=0, columnspan=2, pady=(30, 10))

        # Rounded button feel
        login_btn.configure(borderwidth=0, highlightthickness=0)

        # Bind enter key
        entry_password.bind("<Return>", self.check_credentials)

        # Focus
        self._username_entry = entry_username

    # ------------------------------------------------
    # LOGIN LOGIC (unchanged)
    # ------------------------------------------------
    def check_credentials(self, event=None):
        employee_id = self.username_var.get().strip()
        password = self.password_var.get().strip()

        if not employee_id or not password:
            messagebox.showerror("Login Failed", "Please enter both username and password.")
            return

        conn = None
        try:
            conn = db.connect()
            cur = conn.cursor()

            cur.execute("""
                SELECT employee_id, employee_password, first_name, last_name, role
                FROM employees WHERE employee_id = ?
            """, (employee_id,))
            row = cur.fetchone()

            if row is None or password != row[1]:
                messagebox.showerror("Login Failed", "Invalid Employee ID or Password.")
                return

            self.controller.current_user_id = row[0]
            self.controller.current_user_role = row[4]
            self.controller.current_user_name = f"{row[2]} {row[3]}".strip()

            self.controller.show_frame("main_menu")
            self.username_var.set("")
            self.password_var.set("")

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", str(e))
        finally:
            if conn:
                conn.close()

    def refresh(self):
        self.password_var.set("")
        self._username_entry.focus_set()
