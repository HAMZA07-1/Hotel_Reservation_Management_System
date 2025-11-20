import os
from tkinter import ttk
from database_manager import DatabaseManager
from config import DB_PATH
import tkinter as tk
from tkinter import messagebox
from reservation_window import open_reservation_window
from room_status_window import open_room_status_window
from booking_records_window import open_booking_records_window

print("[Debug GUI] Using database at:", DB_PATH)

db = DatabaseManager(DB_PATH)

# main window
root = tk.Tk()
root.title("Hotel Reservation Management System")
root.geometry("700x450")
root.config(bg="#2C3E50")     # student friendly “hotel dark blue”

# ---------------------------
# LOGIN LOGIC
# ---------------------------
def check_credentials(event=None):
    username = entry_username.get()
    password = entry_password.get()
    role = role_var.get()     # <-- USE the dropdown

    # Manager login
    if role == "Manager" and username == "admin" and password == "password":
        show_home_screen()
        return

    # Employee login
    if role == "Employee" and username == "employee" and password == "1234":
        show_employee_screen()
        return

    # Otherwise fail
    messagebox.showerror("Login Failed", "Invalid username or password")

# ---------------------------
# LOGIN SCREEN
# ---------------------------
def show_login_screen():
    global entry_username, entry_password, role_var

    # Clear window
    for widget in root.winfo_children():
        widget.destroy()

    root.config(bg="#2C3E50")

    tk.Label(
        root,
        text="Hotel Employee Login",
        bg="#2C3E50", fg="white",
        font=("Arial", 22, "bold")
    ).pack(pady=30)

    # Central frame
    frame = tk.Frame(root, bg="#34495E", padx=25, pady=25)
    frame.pack()

    # Username + password
    tk.Label(frame, text="Username:", bg="#34495E", fg="white").grid(row=0, column=0, pady=8, padx=5)
    tk.Label(frame, text="Password:", bg="#34495E", fg="white").grid(row=1, column=0, pady=8, padx=5)

    entry_username = tk.Entry(frame, width=20)
    entry_username.grid(row=0, column=1, pady=8)

    entry_password = tk.Entry(frame, width=20, show="*")
    entry_password.grid(row=1, column=1, pady=8)

    # Role selection
    tk.Label(frame, text="Role:", bg="#34495E", fg="white").grid(row=2, column=0, pady=8, padx=5)

    role_var = tk.StringVar()
    role_dropdown = ttk.Combobox(frame, textvariable=role_var, state="readonly", width=18)
    role_dropdown['values'] = ("Manager", "Employee")
    role_dropdown.current(0)
    role_dropdown.grid(row=2, column=1, pady=8)

    # Login button
    tk.Button(
        frame,
        text="Login",
        width=12,
        command=check_credentials
    ).grid(row=3, column=0, columnspan=2, pady=15)

    # Bind Enter
    root.bind("<Return>", check_credentials)

# ---------------------------
# MAIN MENU
# ---------------------------
# ---------------------------
# MAIN MENU
# ---------------------------
def show_home_screen():
    for widget in root.winfo_children():
        widget.destroy()

    tk.Label(
        root,
        text="Main Menu",
        font=("Arial", 22, "bold"),
        bg="#2C3E50",
        fg="white"
    ).pack(pady=30)

    button_frame = tk.Frame(root, bg="#2C3E50")
    button_frame.pack()

    tk.Button(button_frame, text="Reservations", width=20, height=2,
              command=lambda: open_reservation_window(root, db)).pack(pady=10)

    tk.Button(button_frame, text="Room Status", width=20, height=2,
              command=lambda: open_room_status_window(root)).pack(pady=10)

    tk.Button(button_frame, text="Booking Records", width=20, height=2,
              command=lambda: open_booking_records_window(root)).pack(pady=10)

    tk.Button(root, text="Logout", width=10, command=show_login_screen).pack(pady=40)


# ---------------------------
# EMPLOYEE MENU
# ---------------------------
def show_employee_screen():
    for widget in root.winfo_children():
        widget.destroy()

    tk.Label(
        root,
        text="Employee Menu",
        font=("Arial", 22, "bold"),
        bg="#2C3E50",
        fg="white"
    ).pack(pady=30)

    button_frame = tk.Frame(root, bg="#2C3E50")
    button_frame.pack()

    tk.Button(button_frame, text="Reservations", width=20, height=2,
              command=lambda: open_reservation_window(root, db)).pack(pady=10)

    tk.Button(root, text="Logout", width=10, command=show_login_screen).pack(pady=40)


# ---------------------------
# START PROGRAM
# ---------------------------
show_login_screen()
root.mainloop()
