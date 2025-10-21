import tkinter as tk
from tkinter import ttk
from database_manager import DatabaseManager

# make a db object so we can fetch the rooms easily
db = DatabaseManager()

def open_room_status_window(parent):
    """Show all the rooms and their current availability in a table."""
    
    # create new popup window
    win = tk.Toplevel(parent)
    win.title("Room Status")
    win.geometry("700x450")
    win.config(bg="#395A7F")

    title_lbl = tk.Label(win, text="Hotel Room Status", bg="#395A7F", fg="white",
                         font=("Arial", 16, "bold"))
    title_lbl.pack(pady=10)

    # define the columns for the table
    columns = ("Room ID", "Number", "Type", "Capacity", "Price", "Availability")
    table = ttk.Treeview(win, columns=columns, show="headings")

    for col in columns:
        table.heading(col, text=col)
        table.column(col, width=100, anchor="center")
    table.pack(pady=15, fill="both", expand=True)

    # function to refresh / reload the data
    def refresh_table():
        # clear old data
        for item in table.get_children():
            table.delete(item)

        # fetch new data from db
        try:
            all_rooms = db.get_all_rooms()
            for r in all_rooms:
                room_id, num, rtype, cap, price, avail = r
                status = "Available" if avail == 1 else "Occupied"
                table.insert("", "end", values=(room_id, num, rtype, cap, price, status))
        except Exception as e:
            print("Error loading rooms:", e)

    # add a button to manually reload data
    refresh_btn = tk.Button(win, text="Refresh Data", command=refresh_table)
    refresh_btn.pack(pady=10)

    # load data first time
    refresh_table()