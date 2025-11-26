import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from database_manager import DatabaseManager

BG_APP = "#2C3E50"
PANEL_BG = "#34495E"

db = DatabaseManager()

#----------------------------------------
# LOGIN SCREEN
#----------------------------------------
class LoginFrame(tk.Frame):
    def __init__(self, parent, controller: "HotelApp"):
        super().__init__(parent, bg=BG_APP)
        self.controller = controller

        #Entry variables are attributes
        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.role_var = tk.StringVar(value="Manager")

        #Title
        title = tk.Label(
            self,
            text="Hotel Employee Login",
            bg=BG_APP,
            fg="white",
            font=("Arial", 22, "bold")
        )
        title.pack(pady=30)

        # ----- Central panel -----
        frame = tk.Frame(self, bg=PANEL_BG, padx=25, pady=25)
        frame.pack()

        # Username / Password labels
        tk.Label(frame, text="Employee ID:", bg=PANEL_BG, fg="white").grid(
            row=0, column=0, pady=8, padx=5, sticky="e"
        )
        tk.Label(frame, text="Password:", bg=PANEL_BG, fg="white").grid(
            row=1, column=0, pady=8, padx=5, sticky="e"
        )

        # Username / Password entries
        entry_username = tk.Entry(frame, width=20, textvariable=self.username_var)
        entry_username.grid(row=0, column=1, pady=8)

        entry_password = tk.Entry(frame, width=20, show="*", textvariable=self.password_var)
        entry_password.grid(row=1, column=1, pady=8)

        # Login button
        login_btn = tk.Button(
            frame,
            text="Login",
            width=12,
            command=self.check_credentials
        )
        login_btn.grid(row=3, column=0, columnspan=2, pady=15)

        # Bind Enter key (to the whole frame / app)
        entry_password.bind("<Return>", self.check_credentials)

        # Focus username on show
        self._username_entry = entry_username

    #-----------------------------------------
    # LOGIN LOGIC
    #-----------------------------------------
    def check_credentials(self, event=None):
        #Validate ID/Password against database
        #Move to database manager in future push
        employee_id = self.username_var.get().strip()
        password = self.password_var.get().strip()

        if not employee_id or not password:
            messagebox.showerror("Login Failed", "Please enter both username and password.")
            return

        conn = None
        try:
            conn = db.connect()
            cur = conn.cursor()

            #Assume employee_id is stored exactly as user enters
            cur.execute(
                """
                SELECT employee_id, employee_password, first_name, last_name, role FROM employees
                WHERE employee_id = ?
                """, (employee_id,)
            )
            row = cur.fetchone()

            if row is None:
                messagebox.showerror("Login Failed", "Invalid Employee ID or Password.")
                return

            db_employee_id, db_password, first_name, last_name, role = row

            if password != db_password:
                messagebox.showerror("Login Failed", "Invalid Employee ID or Password.")
                return

            self.current_role = role #Stores role for other parts of app

            if role == 1:
                self.controller.show_frame("main_menu")
            else:
                self.controller.show_frame("main_menu")

            self.username_var.set("")
            self.password_var.set("")

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", str(e))
        finally:
            if conn:
                conn.close()

    def refresh(self):
        #Called when this frame is shown
        #clear fields or set focus here
        self.password_var.set("")
        self._username_entry.focus_set()
