import tkinter as tk
from tkinter import ttk, messagebox

BG_APP = "#2C3E50"
PANEL_BG = "#34495E"

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
        tk.Label(frame, text="Username:", bg=PANEL_BG, fg="white").grid(
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

        # Role selection
        tk.Label(frame, text="Role:", bg=PANEL_BG, fg="white").grid(
            row=2, column=0, pady=8, padx=5, sticky="e"
        )

        role_dropdown = ttk.Combobox(
            frame,
            textvariable=self.role_var,
            state="readonly",
            width=18,
            values=("Manager", "Employee")
        )
        role_dropdown.current(0)
        role_dropdown.grid(row=2, column=1, pady=8)

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
        """Validate the entered username/password/role."""
        username = self.username_var.get()
        password = self.password_var.get()
        role = self.role_var.get()

        # Manager login
        if role == "Manager" and username == "admin" and password == "password":
            #Go to manager home
            self.controller.show_frame("main_menu")
            #clear fields after success
            self.username_var.set("")
            self.password_var.set("")
            return

        # Employee login
        if role == "Employee" and username == "employee" and password == "1234":
            # Go to an employee screen
            # self.controller.show_frame("employee_home")
            self.controller.show_frame("main_menu")
            self.username_var.set("")
            self.password_var.set("")
            return

        # Otherwise fail
        messagebox.showerror("Login Failed", "Invalid username or password")

    def refresh(self):
        #Called when this frame is shown
        #clear fields or set focus here
        self.password_var.set("")
        self._username_entry.focus_set()
