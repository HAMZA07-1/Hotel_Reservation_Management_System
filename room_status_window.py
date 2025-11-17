import tkinter as tk
from tkinter import ttk
from database_manager import DatabaseManager
import sqlite3

# make a db object so we can fetch the rooms easily
db = DatabaseManager()

def open_room_status_window(parent):
    """Show all the rooms and their current availability in a table."""

    # Window Properties
    win = tk.Toplevel(parent)
    win.title("Room Status")
    win.geometry("1000x650")
    win.config(bg="#395A7F")

    #Main title
    #title_lbl = tk.Label(win, text="Hotel Room Status", bg="#395A7F", fg="white",
    #                    font=("Arial", 16, "bold"))
    #title_lbl.pack(pady=10)

    #ttk Style for optics
    style = ttk.Style()
    style.configure("Treeview", font=("TkDefaultFont", 11), rowheight=28)
    style.configure("Treeview.Heading", font=("TkDefaultFont", 12, "bold"))

    #--------------------
    # FILTER BAR
    #--------------------
    filter_frame = tk.Frame(win)
    filter_frame.pack(fill="x", pady=10)
    filter_frame.config(bg="#395A7F")

    #----------------Room Number Search-----------------
    tk.Label(filter_frame, text="Room Number:").pack(side="left", padx=(20,5))

    room_number_var=tk.StringVar()
    room_number_entry = tk.Entry(filter_frame, textvariable=room_number_var, width=8)
    room_number_entry.pack(side="left", padx=5)

    #----------Available Checkbox: Checked by default-----------
    available_var = tk.BooleanVar(value=True)

    available_check = tk.Checkbutton(filter_frame, text="Available", variable=available_var)
    available_check.pack(side="left", padx=10)

    #----------Smoking Drop Down Button----------------
    tk.Label(filter_frame, text="Smoking:").pack(side="left", padx=(20,5))

    smoking_var = tk.StringVar()
    smoking_dropdown = ttk.Combobox(
        filter_frame,
        textvariable=smoking_var,
        values=["", "Smoking", "Non-Smoking"],
        width = 12,
        state = "readonly"
    )
    smoking_dropdown.current(0)
    smoking_dropdown.pack(side="left", padx=5)

    #-------------Capacity Drop Down Button--------------
    tk.Label(filter_frame, text="Capacity:").pack(side="left", padx=(20,5))

    capacity_var = tk.StringVar()
    capacity_dropdown = ttk.Combobox(
        filter_frame,
        textvariable = capacity_var,
        values=["", "2", "4", "6"],
        width = 5,
        state = "readonly"
    )
    capacity_dropdown.current(0)
    capacity_dropdown.pack(side="left", padx=5)

    #----------------Refresh Button---------------------
    refresh_btn = tk.Button(filter_frame, text="Filter", command=lambda: load_data())
    refresh_btn.pack(side="right", padx=10)

    #------------------------
    # TABLE SET UP
    #------------------------
    # define the columns for the table
    columns = ("room_id", "room_number", "room_type", "smoking", "capacity", "price", "is_available")
    tree = ttk.Treeview(win, columns=columns, show="headings", height=15)
    tree.pack(fill="both", expand=True)

    for col, label in zip(columns, ["Room ID", "Room Number", "Room Type", "Smoking", "Capacity", "Price", "Available"]):
        tree.heading(col, text=label)
        tree.column(col, width=120)

    #------------------------
    # PAGE SELECT
    #------------------------
    page_frame= tk.Frame(win)
    page_frame.pack(fill="x", pady=10)

    #Set current page to 1 and entries to 10
    current_page = tk.IntVar(value=1)
    rows_per_page = 10
    result_rows = []

    prev_btn = tk.Button(page_frame, text="<", command=lambda: change_page(-1))
    prev_btn.pack(side="left", padx=5)

    tk.Label(page_frame,text="Page").pack(side="left", padx=(10,5))

    page_entry=tk.Entry(page_frame, width=4, justify="center")
    page_entry.insert(0,"1")
    page_entry.pack(side="left")

    max_page_label = tk.Label(page_frame, text="of 1")
    max_page_label.pack(side="left", padx=(5,20))

    def go_to_page(*args):
        try:
            new_page = int(page_entry.get())
        except ValueError:
            page_entry.delete(0, tk.END)
            page_entry.insert(0, "1")
            return

        max_page = max(1, (len(result_rows) - 1) // rows_per_page + 1)

        new_page = max(1, min(new_page, max_page))

        current_page.set(new_page)
        update_page()



    def change_page(amount):
        new_page = current_page.get() + amount
        max_page = max(1, (len(result_rows) -1) // rows_per_page + 1)

        if 1 <= new_page <= max_page:
            current_page.set(new_page)
            update_page()

    next_btn = tk.Button(page_frame, text=">", command = lambda: change_page(1))
    next_btn.pack(side="left", padx=5)

    #------------------------------
    # UPDATE CURRENT PAGE
    #------------------------------
    def update_page():
        tree.delete(*tree.get_children())

        page = current_page.get()
        start = (page - 1) * rows_per_page
        end = start + rows_per_page

        for row in result_rows[start:end]:
            tree.insert("", tk.END, values=row)

        max_page = max(1, ((len(result_rows) + 10) // rows_per_page))
        page_entry.delete(0, tk.END)
        page_entry.insert(0, str(page))
        max_page_label.config(text=f"of {max_page}")


    #-------------------------------
    # DATA LOADING FUNCTION
    #-------------------------------
    def load_data():
        nonlocal result_rows
        result_rows = []

        try:
            conn = sqlite3.connect("hotel.db")
            cursor = conn.cursor()

            query = "SELECT room_id, room_number, room_type, smoking, capacity, price, is_available from rooms WHERE 1=1"
            params = []

        # Room Number Text Check
            if room_number_var.get().strip() != "":
                query += " AND room_number LIKE ?"
                params.append(f"%{room_number_var.get().strip()}%")

        #Available checkbox check
            if available_var.get():
                query += " AND is_available = ?"
                params.append(1)
            else:
                query += " AND is_available = ?"
                params.append(0)

        #Smoking checkbox check
            if smoking_var.get() == "Smoking":
                query += " AND smoking = ?"
                params.append(1)
            elif smoking_var.get() == "Non-Smoking":
                query += " AND smoking = ?"
                params.append(0)

        #Capacity dropdown check
            if capacity_var.get() != "":
                query += " AND capacity = ?"
                params.append(int(capacity_var.get()))

            cursor.execute(query, params)
            rows = cursor.fetchall()

            result_rows = rows = [
                (r[0], r[1], r[2], "Yes" if r[3] == 1 else "No", r[4], r[5], "Yes" if r[6] == 1 else "No")
                for r in rows
            ]

        except sqlite3.Error as e:
            print(f"Database error:", e)

        finally:
            if conn:
                conn.close()

        current_page.set(1)
        update_page()

    # ------------------------------
    # KEYBOARD SHORTCUTS
    #-------------------------------
    page_entry.bind("<Return>", go_to_page) #Enter to search on page select
    win.bind("<Left>", lambda e: change_page(-1)) #change pages with left and right arrows
    win.bind("<Right>", lambda e: change_page(1))
    room_number_entry.bind("<Return>", lambda e: load_data()) #Room Number search with Enter key

    load_data()
    return win