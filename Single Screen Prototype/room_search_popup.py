from PIL import Image, ImageTk
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
        popup_w, popup_h = 1600, 1000
        self.geometry(f"{popup_w}x{popup_h}")
        self.configure(bg="#2C3E50")
        self.resizable(False, False)

        # ---- Center the popup on screen ----
        self.update_idletasks()
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()

        x = (screen_w // 2) - (popup_w // 2)
        y = (screen_h // 2) - (popup_h // 2)

        self.geometry(f"{popup_w}x{popup_h}+{x}+{y}")
        # ------------------------------------

        tk.Label(self, text="Available Rooms", bg="#2C3E50", fg="white",
                 font=("Arial", 18, "bold")).pack(pady=10)


        columns = ("room_number", "capacity", "price", "smoking")

        # Container frame for side-by-side layout
        content_frame = tk.Frame(self, bg="#2C3E50")
        content_frame.pack(padx=20, pady=10, fill="both", expand=True)

        # LEFT SIDE → Treeview
        columns = ("room_number", "capacity", "price", "smoking")
        self.tree = ttk.Treeview(content_frame, columns=columns, show="headings", height=12)
        self.tree.pack(side="left", fill="both", expand=True, padx=(0, 10))

        # Headings with sortable clicks
        self.tree.heading("room_number", text="Room Number",
                          command=lambda: self.sort_column("room_number", False))
        self.tree.heading("capacity", text="Capacity",
                          command=lambda: self.sort_column("capacity", False))
        self.tree.heading("price", text="Price",
                          command=lambda: self.sort_column("price", False))
        self.tree.heading("smoking", text="Smoking",
                          command=lambda: self.sort_column("smoking", False))

        # Format columns
        for col in columns:
            self.tree.column(col, anchor="center")

        # Query available rooms
        # MUST RETURN smoking field now
        results = controller.db.get_available_rooms(
            check_in, check_out, num_guests, include_smoking
        )

        if not results:
            messagebox.showinfo("No Rooms", "No rooms meet the criteria.")
            self.destroy()
            return

        # Insert results
        for room_id, room_number, capacity, price, smoking in results:
            smoking_text = "Yes" if smoking == 1 else "No"
            self.tree.insert(
                "",
                "end",
                iid=str(room_id),
                values=(room_number, capacity, f"${price:,.2f}", smoking_text)
            )

        ttk.Button(self, text="Select Room", command=self.select_room)\
            .pack(pady=10)

        # RIGHT SIDE → Hotel Map Visual
        try:
            img = Image.open("Images/Hotel_Map.png")

            # Resize if needed (optional)
            img = img.resize((550, 800), Image.LANCZOS)

            self.map_image = ImageTk.PhotoImage(img)

            img_label = tk.Label(content_frame, image=self.map_image, bg="#2C3E50")
            img_label.pack(side="right", fill="y")

        except Exception as e:
            print("Error loading map image:", e)

    def select_room(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showerror("Error", "Please select a room.")
            return

        room_id = int(selected)
        room_values = self.tree.item(selected, "values")
        room_number = room_values[0]

        self.controller.current_frame.set_selected_room(room_id, room_number)
        messagebox.showinfo("Room Selected", f"Room {room_number} selected.")
        self.destroy()

    def sort_column(self, col, reverse):
        # Get all rows as (value, id)
        data = [(self.tree.set(k, col), k) for k in self.tree.get_children("")]

        # Numeric sort columns
        if col in ("capacity", "price"):
            data.sort(key=lambda t: float(t[0].replace("$", "").replace(",", "")), reverse=reverse)

        # Sort Yes/No logically instead of alphabetically
        elif col == "smoking":
            data.sort(key=lambda t: 0 if t[0] == "Yes" else 1, reverse=reverse)

        else:
            data.sort(reverse=reverse)

        # Reorder rows
        for index, (val, k) in enumerate(data):
            self.tree.move(k, "", index)

        self.tree.heading(col, command=lambda: self.sort_column(col, not reverse))
