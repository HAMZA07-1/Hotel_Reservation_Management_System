import tkinter as tk
from tkinter import messagebox

#main window properties
root = tk.Tk()
root.title("Hotel Reservation Management Project")
root.geometry("600x400")
root.config(bg="#395A7F")

#Quit button function
def quit_application():
    root.quit()

#Login credentials check
def check_credentials(event=None):
    username = entry_username.get()
    password = entry_password.get()

    if username == "admin" and password == "password":
        login_frame.pack_forget()
        show_home_screen()
    else:
        messagebox.showerror("Login Failed", "Invalid username or password")

def show_login_screen():
    global login_frame
    # Frame for login details
    login_frame = tk.Frame(root, bg="#395A7F")
    login_frame.place(relx=0.5, rely=0.4, anchor="center")

    #Welcome message
    title_label = tk.Label(root, text="Welcome Hotel Employee",bg="#395A7F", fg="white", font=("Arial", 20, "bold"))
    title_label.place(relx=0.5, rely=0.1, anchor="n")

    root.bind("<Return>", lambda event: check_credentials())

    # Username and Password Labels and Entries
    label_username = tk.Label(login_frame, text="Username:", bg="#395A7F", fg="white")
    label_username.grid(row=0, column=0, padx=10, pady=5, sticky="w")

    global entry_username
    entry_username = tk.Entry(login_frame)
    entry_username.grid(row=0, column=1, padx=10, pady=5)

    label_password = tk.Label(login_frame, text="Password:", bg="#395A7F", fg="white")
    label_password.grid(row=1, column=0, padx=10, pady=5)

    global entry_password
    entry_password = tk.Entry(login_frame, show="*")
    entry_password.grid(row=1, column=1, padx=10, pady=5)

    # Login and Quit buttons
    login_button = tk.Button(login_frame, text="Login", command=check_credentials)
    login_button.grid(row=2, column=0, columnspan=2, pady=10)

    quit_button = tk.Button(root, text="Quit", command=quit_application)
    quit_button.place(relx=0.95, rely=0.95, anchor="se")


#Function to display home screen
def show_home_screen():
    # Create a new window for the menu
    menu_window = tk.Frame(root, bg="#395A7F")
    menu_window.pack(fill="both", expand=True)

    # Title for the menu
    menu_label = tk.Label(menu_window, text="Main Menu", bg="#395A7F", fg="white", font=("Arial", 18, "bold"))
    menu_label.pack(pady=20)

    # Reservations button
    reservations_button = tk.Button(menu_window, text="Reservations", width=20, height=2)
    reservations_button.pack(pady=10)

    # Room Status button
    room_status_button = tk.Button(menu_window, text="Room Status", width=20, height=2)
    room_status_button.pack(pady=10)

    # Booking Records button
    booking_records_button = tk.Button(menu_window, text="Booking Records", width=20, height=2)
    booking_records_button.pack(pady=10)

#Program start
show_login_screen()
root.mainloop()