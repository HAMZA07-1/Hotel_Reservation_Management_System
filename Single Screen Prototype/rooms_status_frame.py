import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from typing import List, Tuple

BG_COLOR = "#395A7F"
DB_PATH = "hotel.db"

class RoomStatusFrame(tk.Frame):
    def __init__(self, parent, controller: "HotelApp"):
        super().__init__(parent, bg=BG_COLOR)
        self.controller = controller

        # State
        self.current_page = 1
        self.rows_per_page = 29
        self.result_rows: List[Tuple] = []
        self.columns = (
            "edit",
            "room_id",
            "room_number",
            "room_type",
            "smoking",
            "capacity",
            "price",
            "is_available",
        )

        # Filter vars (kept as attributes so other methods can access them)
        self.room_number_var = tk.StringVar()
        self.available_var = tk.BooleanVar(value=True)
        self.smoking_var = tk.StringVar()
        self.capacity_var = tk.StringVar()

        # Build UI
        self._create_title()
        self._create_styles()
        self._create_filter_bar()
        self._create_table()
        self._create_page_bar()
        self._bind_shortcuts()

        # initial load
        self.load_data()

    # -------------------------
    # UI build helpers
    # -------------------------
    def _create_title(self):
        title_lbl = tk.Label(
            self,
            text="Hotel Room Status",
            bg=BG_COLOR,
            fg="white",
            font=("Arial", 30, "bold"),
        )
        title_lbl.pack(pady=10)

    def _create_styles(self):
        style = ttk.Style()
        style.configure("Treeview", font=("Arial", 14), rowheight=32)
        style.configure("Treeview.Heading", font=("TkDefaultFont", 13, "bold"))

    def _create_filter_bar(self):
        filter_frame = tk.Frame(self, bg=BG_COLOR)
        filter_frame.pack(fill="x", pady=10)

        # Back button
        back_btn = tk.Button(
            filter_frame, text="Back", command=lambda: self.controller.show_frame("main_menu")
        )
        back_btn.pack(side="left", padx=10)

        # Room Number
        tk.Label(filter_frame, text="Room Number:", bg=BG_COLOR, fg="white").pack(
            side="left", padx=(20, 5)
        )
        room_number_entry = tk.Entry(filter_frame, textvariable=self.room_number_var, width=8)
        room_number_entry.pack(side="left", padx=5)
        room_number_entry.bind("<Return>", lambda e: self.load_data())

        # Available checkbox
        available_check = tk.Checkbutton(
            filter_frame,
            text="Available",
            variable=self.available_var,
            bg=BG_COLOR,
            fg="white",
            selectcolor=BG_COLOR,
            activebackground=BG_COLOR,
            activeforeground="white",
        )
        available_check.pack(side="left", padx=10)

        # Smoking dropdown
        tk.Label(filter_frame, text="Smoking:", bg=BG_COLOR, fg="white").pack(
            side="left", padx=(20, 5)
        )
        smoking_dropdown = ttk.Combobox(
            filter_frame,
            textvariable=self.smoking_var,
            values=["", "Smoking", "Non-Smoking"],
            width=12,
            state="readonly",
        )
        smoking_dropdown.current(0)
        smoking_dropdown.pack(side="left", padx=5)

        # Capacity dropdown
        tk.Label(filter_frame, text="Capacity:", bg=BG_COLOR, fg="white").pack(
            side="left", padx=(20, 5)
        )
        capacity_dropdown = ttk.Combobox(
            filter_frame,
            textvariable=self.capacity_var,
            values=["", "2", "4", "6"],
            width=5,
            state="readonly",
        )
        capacity_dropdown.current(0)
        capacity_dropdown.pack(side="left", padx=5)

        # Filter button
        refresh_btn = tk.Button(filter_frame, text="Filter", command=self.load_data)
        refresh_btn.pack(side="right", padx=10)

    def _create_table(self):
        table_frame = tk.Frame(self, bg=BG_COLOR)
        table_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # vertical scrollbar
        vsb = ttk.Scrollbar(table_frame, orient="vertical")
        vsb.pack(side="right", fill="y")

        self.tree = ttk.Treeview(
            table_frame,
            columns=self.columns,
            show="headings",
            yscrollcommand=vsb.set,
        )
        vsb.config(command=self.tree.yview)
        self.tree.pack(fill="both", expand=True)

        # headings & column widths
        labels = ["Edit", "Room ID", "Room Number", "Room Type", "Smoking", "Capacity", "Price", "Available"]
        for col, label in zip(self.columns, labels):
            self.tree.heading(col, text=label)
            if col == "edit":
                self.tree.column(col, width=80, anchor="center", stretch=False)
            elif col == "room_type":
                self.tree.column(col, width=220)
            else:
                self.tree.column(col, width=120)

        # tag styles
        self.tree.tag_configure("avail_yes", foreground="green", background="#eaffea")
        self.tree.tag_configure("avail_no", foreground="red", background="#ffecec")

        # double-click binding
        self.tree.bind("<Double-1>", self._on_tree_double_click)

    def _create_page_bar(self):
        page_frame = tk.Frame(self, bg=BG_COLOR)
        page_frame.pack(fill="x", pady=10)

        prev_btn = tk.Button(page_frame, text="<", command=lambda: self.change_page(-1))
        prev_btn.pack(side="left", padx=5)

        tk.Label(page_frame, text="Page", bg=BG_COLOR, fg="white").pack(side="left", padx=(10, 5))

        self.page_entry = tk.Entry(page_frame, width=4, justify="center")
        self.page_entry.insert(0, "1")
        self.page_entry.pack(side="left")
        self.page_entry.bind("<Return>", lambda e: self.go_to_page())

        self.max_page_label = tk.Label(page_frame, text="of 1", bg=BG_COLOR, fg="white")
        self.max_page_label.pack(side="left", padx=(5, 20))

        next_btn = tk.Button(page_frame, text=">", command=lambda: self.change_page(1))
        next_btn.pack(side="left", padx=5)

    def _bind_shortcuts(self):
        # binds on controller so arrow keys work across the app
        try:
            self.controller.bind_all("<Left>", lambda e: self.change_page(-1))
            self.controller.bind_all("<Right>", lambda e: self.change_page(1))
        except Exception:
            # controller may not support bind_all during testing; ignore safely
            pass

    # -------------------------
    # Pagination helpers
    # -------------------------
    def go_to_page(self):
        try:
            new_page = int(self.page_entry.get())
        except ValueError:
            self.page_entry.delete(0, tk.END)
            self.page_entry.insert(0, "1")
            return

        max_page = max(1, (len(self.result_rows) - 1) // self.rows_per_page + 1)
        new_page = max(1, min(new_page, max_page))
        self.current_page = new_page
        self.update_page()

    def change_page(self, amount: int):
        new_page = self.current_page + amount
        max_page = max(1, (len(self.result_rows) - 1) // self.rows_per_page + 1)
        if 1 <= new_page <= max_page:
            self.current_page = new_page
            self.update_page()

    def update_page(self):
        # clears and inserts current page rows
        self.tree.delete(*self.tree.get_children())

        page = self.current_page
        start = (page - 1) * self.rows_per_page
        end = start + self.rows_per_page
        for row in self.result_rows[start:end]:
            availability_str = row[-1]
            tag = "avail_yes" if availability_str == "Yes" else "avail_no"
            self.tree.insert("", tk.END, values=row, tags=(tag,))

        max_page = max(1, (len(self.result_rows) - 1) // self.rows_per_page + 1)
        self.page_entry.delete(0, tk.END)
        self.page_entry.insert(0, str(page))
        self.max_page_label.config(text=f"of {max_page}")

    # -------------------------
    # Data loading
    # -------------------------
    def load_data(self):
        # Convert GUI filter state → query params
        room_number = self.room_number_var.get().strip() or ""

        available_val = 1 if self.available_var.get() else 0

        if self.smoking_var.get() == "Smoking":
            smoking_val = 1
        elif self.smoking_var.get() == "Non-Smoking":
            smoking_val = 0
        else:
            smoking_val = None

        capacity_val = self.capacity_var.get() or None

        try:
            rows = self.controller.db.get_rooms_filtered(
                room_number=room_number,
                available=available_val,
                smoking=smoking_val,
                capacity=capacity_val,
            )

            # Convert DB rows to display rows
            self.result_rows = [
                (
                    "Edit",
                    r[0],  # room_id
                    r[1],  # room_number
                    r[2],  # room_type
                    "Yes" if r[3] == 1 else "No",
                    r[4],  # capacity
                    r[5],  # price
                    "Yes" if r[6] == 1 else "No",
                )
                for r in rows
            ]

        except Exception as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")
            self.result_rows = []

        self.current_page = 1
        self.update_page()

    # -------------------------
    # Edit popup + handlers
    # -------------------------
    def _on_tree_double_click(self, event):
        # Make sure we clicked on a cell and identify the clicked column by name (robust)
        region = self.tree.identify("region", event.x, event.y)
        if region != "cell":
            return

        column_id = self.tree.identify_column(event.x)  # e.g. "#3"
        try:
            col_index = int(column_id.replace("#", "")) - 1
        except Exception:
            return

        if col_index < 0 or col_index >= len(self.columns):
            return

        col_name = self.columns[col_index]
        if col_name != "edit":
            # only open editor when user double-clicks the leftmost "edit" column
            return

        row_id = self.tree.identify_row(event.y)
        if not row_id:
            return

        item = self.tree.item(row_id)
        values = item.get("values") or []
        if not values or len(values) < 8:
            return

        room_id = values[1]
        current_price = values[6]
        current_avail_str = values[7]
        self.open_edit_popup(room_id, current_price, current_avail_str)

    def open_edit_popup(self, room_id: int, current_price, current_avail_str: str):
        popup = tk.Toplevel(self)
        popup.title(f"Edit Room {room_id}")
        popup.grab_set()
        # Set size
        popup_w, popup_h = 200, 200
        popup.geometry(f"{popup_w}x{popup_h}")
        popup.configure(bg="#2C3E50")
        popup.resizable(False, False)

        # ---- Center the popup on screen ----
        popup.update_idletasks()  # ensure geometry is ready
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()

        x = (screen_w // 2) - (popup_w // 2)
        y = (screen_h // 2) - (popup_h // 2)

        popup.geometry(f"{popup_w}x{popup_h}+{x}+{y}")

        tk.Label(
            popup,
            text=f"Editing Room ID: {room_id}",
            font=("TkDefaultFont", 11, "bold"), bg="#2C3E50", fg="white"
        ).grid(row=0, column=0, columnspan=2, pady=(10, 10), padx=10)

        tk.Label(popup, text="Price:", bg="#2C3E50", fg="white").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        price_var = tk.StringVar(value=str(current_price))
        price_entry = tk.Entry(popup, textvariable=price_var, width=12)
        price_entry.grid(row=1, column=1, sticky="w", padx=5, pady=5)

        tk.Label(popup, text="Availability:", bg="#2C3E50", fg="white").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        avail_var = tk.StringVar()
        avail_dropdown = ttk.Combobox(
            popup, textvariable=avail_var, values=["Available", "Unavailable"], state="readonly", width=12
        )
        avail_dropdown.grid(row=2, column=1, sticky="w", padx=5, pady=5)
        initial_avail = "Available" if current_avail_str == "Yes" else "Unavailable"
        avail_var.set(initial_avail)

        # Button frame
        button_frame = tk.Frame(popup, bg="#2C3E50")
        button_frame.grid(row=3, column=0, columnspan=2, pady=10)

        def save_changes():
            # Validate price
            try:
                new_price = float(price_var.get())
                if new_price <= 0:
                    raise ValueError
            except:
                messagebox.showwarning("Invalid Price", "Price must be a positive number.")
                return

            new_avail_val = 1 if avail_var.get() == "Available" else 0

            try:
                self.controller.db.update_room(room_id, new_price, new_avail_val)
            except Exception as e:
                messagebox.showerror("Database Error", f"Could not save changes: {e}")
                return

            popup.destroy()
            self.load_data()

        save_btn = tk.Button(button_frame, text="Save", command=save_changes)
        save_btn.pack(side="left", padx=5)

        cancel_btn = tk.Button(button_frame, text="Cancel", command=popup.destroy)
        cancel_btn.pack(side="left", padx=5)

        price_entry.focus_set()

    # -------------------------
    # Public functions
    # -------------------------
    def refresh(self):
        """Called whenever this screen is shown"""
        self.load_data()
