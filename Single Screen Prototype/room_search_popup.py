import tkinter as tk
from tkinter import ttk, messagebox

class RoomSearchPopup(tk.Toplevel):
    def __init__(self, parent, controller, check_in, check_out, num_guests, include_smoking):
        super().__init__(parent)
        self.parent_frame = parent
        controller.current_frame = parent

        self.title("Available Rooms")
        self.controller = controller

        # Set size
        popup_w, popup_h = 600, 600
        self.geometry(f"{popup_w}x{popup_h}")
        self.configure(bg="#2C3E50")
        self.resizable(False, False)

        # ---- Center the popup on screen ----
        self.update_idletasks()  # ensure geometry is ready
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()

        x = (screen_w // 2) - (popup_w // 2)
        y = (screen_h // 2) - (popup_h // 2)

        self.geometry(f"{popup_w}x{popup_h}+{x}+{y}")
        # ------------------------------------

        tk.Label(self, text="Available Rooms", bg="#2C3E50", fg="white",
                 font=("Arial", 18, "bold")).pack(pady=10)


        # Treeview
        columns = ("room_number", "capacity", "price")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=12)
        self.tree.pack(padx=20, pady=10, fill="both", expand=True)

        self.tree.heading("room_number", text="Room Number",
                          command=lambda: self.sort_column("room_number", False))

        self.tree.heading("capacity", text="Capacity",
                          command=lambda: self.sort_column("capacity", False))

        self.tree.heading("price", text="Price",
                          command=lambda: self.sort_column("price", False))

        for col in columns:
            self.tree.column(col, anchor="center")

        # Query available rooms
        results = controller.db.get_available_rooms(
            check_in, check_out, num_guests, include_smoking
        )

        if not results:
            messagebox.showinfo("No Rooms", "No rooms meet the criteria.")
            self.destroy()
            return

        # Insert results
        for room_id, room_number, capacity, price in results:
            self.tree.insert(
                "",
                "end",
                iid=str(room_id),  # store room_id internally
                values=(room_number, capacity, f"${price:,.2f}")
            )

        # Choose button
        ttk.Button(self, text="Select Room", command=self.select_room)\
            .pack(pady=10)

    def select_room(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showerror("Error", "Please select a room.")
            return

        # selected = iid = room_id
        room_id = int(selected)

        room_values = self.tree.item(selected, "values")
        room_number = room_values[0]  # correct now

        # Send the selection back to the parent ReservationFormFrame
        self.controller.current_frame.set_selected_room(room_id, room_number)

        messagebox.showinfo("Room Selected", f"Room {room_number} selected.")
        self.destroy()

    def sort_column(self, col, reverse):
        # Get all rows as (id, values)
        data = [(self.tree.set(k, col), k) for k in self.tree.get_children("")]

        # Convert numeric columns to numbers for proper sorting
        if col in ("capacity", "price"):
            data.sort(key=lambda t: float(t[0].replace("$", "").replace(",", "")), reverse=reverse)
        else:
            data.sort(reverse=reverse)

        # Reorder rows
        for index, (val, k) in enumerate(data):
            self.tree.move(k, "", index)

        # Reverse sort direction next click
        self.tree.heading(col, command=lambda: self.sort_column(col, not reverse))