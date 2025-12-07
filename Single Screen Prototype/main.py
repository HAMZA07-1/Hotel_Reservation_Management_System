import os
from tkinter import ttk
from database_manager import DatabaseManager
from config import DB_PATH
import tkinter as tk
from rooms_status_frame import RoomStatusFrame
from login_frame import LoginFrame
from booking_records_frame import BookingRecordsFrame
from metrics_frame import MetricsFrame
from employee_frame import EmployeeProfileFrame
from reservation_form_frame import ReservationFormFrame
from hotel_manager import HotelManager


print("[Debug GUI] Using database at:", DB_PATH)

db = DatabaseManager("hotel.db")

BG_COLOR = "#2C3E50"
FG_COLOR = "#ECF0F1"

#---------------------------------------
# APP INITIALIZATION / PROGRAM START
#---------------------------------------
class HotelApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.hotel = HotelManager(self.db)
        #Allows DatabaseManager to call HotelManager methods
        self.db.hotel_manager = self.hotel

        # Window properties
        self.title("Hotel Management")

        # Set desired size
        app_w, app_h = 1920, 1080
        self.geometry(f"{app_w}x{app_h}")
        self.configure(bg=BG_COLOR)
        self.resizable(False, False)

        # --- Center the main window ---
        self.update_idletasks()  # ensure geometry info is ready
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()

        x = (screen_w // 2) - (app_w // 2)
        y = (screen_h // 2) - (app_h // 2)

        self.geometry(f"{app_w}x{app_h}+{x}+{y}")


        #Current User logged in info
        self.current_user_id = None
        self.current_user_role = None
        self.current_user_name = None

        #Expandable root grid
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Container for all "screens"
        self.container = tk.Frame(self, bg=BG_COLOR)
        self.container.grid(row=0, column=0, sticky="nsew")

        # Make container expand
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.frames = {}  # name -> frame instance

        #Screens made here:
        self.frames["login_screen"] = LoginFrame(self.container, self)
        self.frames["main_menu"] = MainMenuFrame(self.container, self)
        self.frames["new_reservation"] = ReservationFormFrame(self.container, self)
        self.frames["rooms_status"] = RoomStatusFrame(self.container, self)
        self.frames["booking_records"] = BookingRecordsFrame(self.container,self)
        self.frames["metrics"] = MetricsFrame(self.container, self)
        self.frames["employees"] = EmployeeProfileFrame(self.container, self)

        # Layout screens (stacked, we raise the one we want)
        for frame in self.frames.values():
            frame.grid(row=0, column=0, sticky="nsew")

        #First Frame shown on program start
        self.show_frame("main_menu")

    #def to show new screen
    def show_frame(self, name):
        frame = self.frames[name]
        frame.tkraise()
        if hasattr(frame, "refresh"):
            frame.refresh()

#-----------------------------
# MAIN MENU
#-----------------------------
class MainMenuFrame(tk.Frame):
    def __init__(self, parent, controller: "HotelApp"):
        super().__init__(parent, bg=BG_COLOR)
        self.controller = controller
        self.db = db

        # Frame fills the container
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Inner content is centered
        content = tk.Frame(self, bg=BG_COLOR)
        content.grid(row=0, column=0, sticky="n")

        # Title
        self.title_label = tk.Label(
            content,
            text="Hotel Management Main Menu",
            font=("TkDefaultFont", 28, "bold"),
            bg=BG_COLOR,
            fg=FG_COLOR
        )
        self.title_label.pack(pady=(0, 30))

        #--------------------Buttons----------------------
        # New Reservation Button
        new_reservation_btn = tk.Button(
            content,
            text="New Reservation",
            font=("TkDefaultFont", 16),
            width=20,
            command=lambda: controller.show_frame("new_reservation"),
            bg="#34495E",
            fg=FG_COLOR,
            activebackground="#3D566E",
            activeforeground=FG_COLOR,
            relief="flat"
        )
        new_reservation_btn.pack(pady=10)

        # View Rooms Button
        view_rooms_btn = tk.Button(
            content,
            text="View Rooms",
            font=("TkDefaultFont", 16),
            width=20,
            command=lambda: controller.show_frame("rooms_status"),
            bg="#34495E",
            fg=FG_COLOR,
            activebackground="#3D566E",
            activeforeground=FG_COLOR,
            relief="flat"
        )
        view_rooms_btn.pack(pady=10)

        # Booking Records Button
        booking_records_btn = tk.Button(
            content,
            text="Booking Records",
            font=("TkDefaultFont", 16),
            width=20,
            command=lambda: controller.show_frame("booking_records"),
            bg="#34495E",
            fg=FG_COLOR,
            activebackground="#3D566E",
            activeforeground=FG_COLOR,
            relief="flat"
        )
        booking_records_btn.pack(pady=10)

        # Metrics Button  (we keep a reference on self)
        self.metrics_btn = tk.Button(
            content,
            text="Metrics",
            font=("TkDefaultFont", 16),
            width=20,
            command=lambda: controller.show_frame("metrics"),
            bg="#34495E",
            fg=FG_COLOR,
            activebackground="#3D566E",
            activeforeground=FG_COLOR,
            relief="flat"
        )
        self.metrics_btn.pack(pady=10)

        # Employees Button (also keep reference)
        self.employees_btn = tk.Button(
            content,
            text="Employees",
            font=("TkDefaultFont", 16),
            width=20,
            command=lambda: controller.show_frame("employees"),
            bg="#34495E",
            fg=FG_COLOR,
            activebackground="#3D566E",
            activeforeground=FG_COLOR,
            relief="flat"
        )
        self.employees_btn.pack(pady=10)

        # Logout Button
        logout_btn = tk.Button(
            content,
            text="Logout",
            font=("TkDefaultFont", 16),
            width=20,
            command=self.logout,
            bg="#34495E",
            fg=FG_COLOR,
            activebackground="#3D566E",
            activeforeground=FG_COLOR,
            relief="flat"
        )
        logout_btn.pack(pady=10)

    def logout(self):
        #Clear current user and go back to login screen.
        self.controller.current_user_id = None
        self.controller.current_user_role = None
        self.controller.show_frame("login_screen")

    def refresh(self):
        #updates room availability based on reservation date
        self.db.update_room_availability_today()

        #Updates reservations based on date and times
        self.db.run_daily_reservation_updates()

        #Called when this menu is shown; hide buttons based on role.
        name = self.controller.current_user_name or "Guest"
        self.title_label.config(
            text=f"Welcome {name}! \nHotel Management Main Menu"
        )
        role = self.controller.current_user_role

        # Default: hide both, then selectively show
        # use pack_forget to hide and pack to show
        # But we only want to pack if they’re not already visible.

        if role == "Manager":
            # Manager sees both
            if not self.metrics_btn.winfo_ismapped():
                self.metrics_btn.pack(pady=10)
            if not self.employees_btn.winfo_ismapped():
                self.employees_btn.pack(pady=10)
        elif role == "Employee":
            # Employees cannot see these
            if self.metrics_btn.winfo_ismapped():
                self.metrics_btn.pack_forget()
            if self.employees_btn.winfo_ismapped():
                self.employees_btn.pack_forget()


if __name__ == "__main__":
    app = HotelApp()
    app.mainloop()
