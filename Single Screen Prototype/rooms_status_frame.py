import tkinter as tk
from tkinter import ttk
import sqlite3

BG_COLOR = "#395A7F"

class RoomStatusFrame(tk.Frame):
    def __init__(self, parent, controller: "HotelApp"):
        super().__init__(parent, bg=BG_COLOR)
        self.controller = controller

        # -------------Window Layout / Title-------------
        title_lbl = tk.Label(
            self,
            text="Hotel Room Status",
            bg=BG_COLOR,
            fg="white",
            font=("Arial", 30, "bold")
        )
        title_lbl.pack(pady=10)

        # ttk Style for optics
        style = ttk.Style()
        style.configure("Treeview", font=("TkDefaultFont", 23), rowheight=44)
        style.configure("Treeview.Heading", font=("TkDefaultFont", 13, "bold"))

        # -----------------------------------
        # FILTER BAR
        # -----------------------------------
        filter_frame = tk.Frame(self, bg=BG_COLOR)
        filter_frame.pack(fill="x", pady=10)

        #------------------Buttons------------------
        # Back to main menu button
        back_btn = tk.Button(
            filter_frame,
            text="Back",
            command=lambda: controller.show_frame("main_menu")
        )
        back_btn.pack(side="left", padx=10)

        # Room Number Search
        tk.Label(filter_frame, text="Room Number:", bg=BG_COLOR, fg="white").pack(
            side="left", padx=(20, 5)
        )

        room_number_var = tk.StringVar()
        room_number_entry = tk.Entry(filter_frame, textvariable=room_number_var, width=8)
        room_number_entry.pack(side="left", padx=5)

        # Available Checkbox: Checked by default
        available_var = tk.BooleanVar(value=True)
        available_check = tk.Checkbutton(
            filter_frame,
            text="Available",
            variable=available_var,
            bg=BG_COLOR,
            fg="white",
            selectcolor=BG_COLOR,
            activebackground=BG_COLOR,
            activeforeground="white"
        )
        available_check.pack(side="left", padx=10)

        # Smoking Drop Down
        tk.Label(filter_frame, text="Smoking:", bg=BG_COLOR, fg="white").pack(
            side="left", padx=(20, 5)
        )

        smoking_var = tk.StringVar()
        smoking_dropdown = ttk.Combobox(
            filter_frame,
            textvariable=smoking_var,
            values=["", "Smoking", "Non-Smoking"],
            width=12,
            state="readonly"
        )
        smoking_dropdown.current(0)
        smoking_dropdown.pack(side="left", padx=5)

        # Capacity Drop Down
        tk.Label(filter_frame, text="Capacity:", bg=BG_COLOR, fg="white").pack(
            side="left", padx=(20, 5)
        )

        capacity_var = tk.StringVar()
        capacity_dropdown = ttk.Combobox(
            filter_frame,
            textvariable=capacity_var,
            values=["", "2", "4", "6"],
            width=5,
            state="readonly"
        )
        capacity_dropdown.current(0)
        capacity_dropdown.pack(side="left", padx=5)

        # Refresh Button
        refresh_btn = tk.Button(filter_frame, text="Filter", command=lambda: load_data())
        refresh_btn.pack(side="right", padx=10)


        # ------------------------
        # TABLE SET UP
        # ------------------------
        table_frame = tk.Frame(self, bg=BG_COLOR)
        table_frame.pack(fill="both", expand=True)

        #Column definitions
        columns = (
            "edit",
            "room_id",
            "room_number",
            "room_type",
            "smoking",
            "capacity",
            "price",
            "is_available",
        )

        tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=10)
        tree.pack(fill="both", expand=True)

        #Columns set with official names and even widths except for edit and room type
        for col, label in zip(
            columns,
            ["Edit", "Room ID", "Room Number", "Room Type", "Smoking", "Capacity", "Price", "Available"],
        ):
            tree.heading(col, text=label)

            if col == "edit":
                tree.column(col, width=80, anchor="center")
            elif col == "room_type":
                tree.column(col, width=220)
            else:
                tree.column(col, width=120)

        #Tag styles for available and unavailable rooms
        tree.tag_configure("avail_yes", foreground="green", background="#eaffea")
        tree.tag_configure("avail_no", foreground="red", background="#ffecec")

        # ------------------------
        # PAGE SELECT BAR
        # ------------------------
        page_frame = tk.Frame(self, bg=BG_COLOR)
        page_frame.pack(fill="x", pady=10)

        #Set current page to 1 and entries on page to 20
        current_page = tk.IntVar(value=1)
        rows_per_page = 20
        result_rows = []

        #Back page button
        prev_btn = tk.Button(page_frame, text="<", command=lambda: change_page(-1))
        prev_btn.pack(side="left", padx=5)

        tk.Label(page_frame, text="Page", bg=BG_COLOR, fg="white").pack(
            side="left", padx=(10, 5)
        )

        #Text input for the first number that can be typed if desired
        page_entry = tk.Entry(page_frame, width=4, justify="center")
        page_entry.insert(0, "1")
        page_entry.pack(side="left")

        max_page_label = tk.Label(page_frame, text="of 1", bg=BG_COLOR, fg="white")
        max_page_label.pack(side="left", padx=(5, 20))

        #Next page button
        next_btn = tk.Button(page_frame, text=">", command=lambda: change_page(1))
        next_btn.pack(side="left", padx=5)

        # ------------------------------
        # PAGE FUNCTIONS
        # ------------------------------
        #Called when page is changed either via buttons, shortcuts, or text input + enter
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
            max_page = max(1, (len(result_rows) - 1) // rows_per_page + 1)

            if 1 <= new_page <= max_page:
                current_page.set(new_page)
                update_page()

        #------------------------------------
        # UPDATE CURRENT PAGE
        #------------------------------------
        #Updates content on page currently in view
        def update_page():
            tree.delete(*tree.get_children())

            page = current_page.get()
            start = (page - 1) * rows_per_page
            end = start + rows_per_page

            for row in result_rows[start:end]:
                availability_str = row[-1]
                tag = "avail_yes" if availability_str == "Yes" else "avail_no"
                tree.insert("", tk.END, values=row, tags=(tag,))

            max_page = max(1, (len(result_rows) + 20) // rows_per_page)
            page_entry.delete(0, tk.END)
            page_entry.insert(0, str(page))
            max_page_label.config(text=f"of {max_page}")

        # -------------------------------
        # DATA LOADING
        # -------------------------------
        #Loads data from database, needs to be separated at later point
        def load_data():
            nonlocal result_rows
            result_rows = []

            conn = None
            try:
                conn = sqlite3.connect("../hotel.db")
                cursor = conn.cursor()

                query = """
                    SELECT room_id, room_number, room_type, smoking,
                           capacity, price, is_available
                    FROM rooms
                    WHERE 1=1
                """
                params = []

                # Room Number Text Check
                if room_number_var.get().strip() != "":
                    query += " AND room_number LIKE ?"
                    params.append(f"%{room_number_var.get().strip()}%")

                # Available Checkbox Check
                if available_var.get():
                    query += " AND is_available = ?"
                    params.append(1)
                else:
                    query += " AND is_available = ?"
                    params.append(0)

                # Smoking Dropdown Check
                if smoking_var.get() == "Smoking":
                    query += " AND smoking = ?"
                    params.append(1)
                elif smoking_var.get() == "Non-Smoking":
                    query += " AND smoking = ?"
                    params.append(0)

                # Capacity Dropdown Check
                if capacity_var.get() != "":
                    query += " AND capacity = ?"
                    params.append(int(capacity_var.get()))

                cursor.execute(query, params)
                rows = cursor.fetchall()

                result_rows = [
                    (
                        "Edit",
                        r[0],
                        r[1],
                        r[2],
                        "Yes" if r[3] == 1 else "No",
                        r[4],
                        r[5],
                        "Yes" if r[6] == 1 else "No",
                    )
                    for r in rows
                ]

            except sqlite3.Error as e:
                print("Database error:", e)

            finally:
                if conn:
                    conn.close()

            current_page.set(1)
            update_page()

        # ----------------------------------
        # EDIT ROOM POPUP WINDOW
        # ----------------------------------
        #Double Click event handler
        def on_tree_double_click(event):
            region = tree.identify("region", event.x, event.y)
            if region != "cell":
                return

            column_id = tree.identify_column(event.x)
            row_id = tree.identify_row(event.y)
            if not row_id:
                return

            if column_id != "#1":  # Only targets edit column
                return

            item = tree.item(row_id)
            values = item["values"]
            if not values:
                return

            room_id = values[1]
            current_price = values[6]
            current_avail_str = values[7]

            open_edit_popup(room_id, current_price, current_avail_str)

        #Edit pop up window
        def open_edit_popup(room_id, current_price, current_avail_str):
            popup = tk.Toplevel(self)
            popup.title(f"Edit Room {room_id}")
            popup.grab_set()

            #Title
            tk.Label(
                popup,
                text=f"Editing Room ID: {room_id}",
                font=("TkDefaultFont", 11, "bold"),
            ).grid(row=0, column=0, columnspan=2, pady=(10, 10))

            #Price Field
            tk.Label(popup, text="Price:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
            price_var = tk.StringVar(value=str(current_price))
            price_entry = tk.Entry(popup, textvariable=price_var, width=10)
            price_entry.grid(row=1, column=1, sticky="w", padx=5, pady=5)

            #Availability dropdown
            tk.Label(popup, text="Availability:").grid(
                row=2, column=0, sticky="e", padx=5, pady=5
            )
            avail_var = tk.StringVar()
            avail_dropdown = ttk.Combobox(
                popup,
                textvariable=avail_var,
                values=["Available", "Unavailable"],
                state="readonly",
                width=12,
            )
            initial_avail = "Available" if current_avail_str == "Yes" else "Unavailable"
            avail_var.set(initial_avail)
            avail_dropdown.grid(row=2, column=1, sticky="w", padx=5, pady=5)

            #Frame for Buttons
            button_frame = tk.Frame(popup)
            button_frame.grid(row=3, column=0, columnspan=2, pady=10)

            #Reads values from inputs and attempts to apply changes
            #Should be separated in future updates to separate logic
            def save_changes():
                #Price
                try:
                    new_price = float(price_var.get())
                except ValueError:
                    print("Invalid Price")
                    return

                #Availability
                new_avail = avail_var.get()
                new_avail = 1 if new_avail == "Available" else 0

                #Attemps to update database
                conn2 = None
                try:
                    conn2 = sqlite3.connect("../hotel.db")
                    cursor2 = conn2.cursor()
                    cursor2.execute(
                        "UPDATE rooms SET price = ?, is_available = ? WHERE room_id = ?",
                        (new_price, new_avail, room_id),
                    )
                    conn2.commit()
                except sqlite3.Error as e:
                    print("Database error:", e)
                finally:
                    if conn2:
                        conn2.close()

                popup.destroy()
                load_data()

            #Buttons to save or cancel
            save_btn = tk.Button(button_frame, text="Save", command=save_changes)
            save_btn.pack(side="left", padx=5)

            cancel_btn = tk.Button(button_frame, text="Cancel", command=popup.destroy)
            cancel_btn.pack(side="left", padx=5)

            price_entry.focus_set()

        # ------------------------------
        # KEYBOARD SHORTCUTS & BINDINGS
        # ------------------------------
        page_entry.bind("<Return>", go_to_page) #Enter to search on page text input
        self.controller.bind_all("<Left>", lambda e: change_page(-1)) #Change page by one with left arrow
        self.controller.bind_all("<Right>", lambda e: change_page(1)) #Change page by one with right arrow
        room_number_entry.bind("<Return>", lambda e: load_data()) # Searches by room number
        tree.bind("<Double-1>", on_tree_double_click) #Double-click on edit starts event handler

        # Initial data load
        load_data()

        # Store things you might want in refresh()
        self._load_data = load_data

    def refresh(self):
        #Called whenever this screen is shown
        if hasattr(self, "_load_data"):
            self._load_data()
