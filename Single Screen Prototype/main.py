import os
from tkinter import ttk
from database_manager import DatabaseManager
from config import DB_PATH
import tkinter as tk
from rooms_status_frame import RoomStatusFrame
from login_frame import LoginFrame
from booking_records_frame import BookingRecordsFrame


print("[Debug GUI] Using database at:", DB_PATH)

db = DatabaseManager(DB_PATH)

BG_COLOR = "#2C3E50"
FG_COLOR = "#ECF0F1"

#---------------------------------------
# APP INITIALIZATION / PROGRAM START
#---------------------------------------
class HotelApp(tk.Tk):
    def __init__(self):
        super().__init__()
        #Window properties
        self.title("Hotel Management")
        self.geometry("1920x1080")
        self.configure(bg=BG_COLOR)

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
        #self.frames["new_reservation"] = NewReservationFrame(self.container, self)
        self.frames["rooms_status"] = RoomStatusFrame(self.container, self)
        self.frames["booking_records"] = BookingRecordsFrame(self.container,self)
        #self.frames["metrics"] = MetricsFrame(self.container, self)
        #self.frames["Employees"] = EmployeesFrame(self.container, self)

        # Layout screens (stacked, we raise the one we want)
        for frame in self.frames.values():
            frame.grid(row=0, column=0, sticky="nsew")

        #First Frame shown on program start
        self.show_frame("main_menu")

    #def to show new screen
    def show_frame(self, name):
        frame = self.frames[name]
        frame.tkraise()
        if name == "rooms":
            frame.refresh()

#-----------------------------
# MAIN MENU
#-----------------------------
class MainMenuFrame(tk.Frame):
    def __init__(self, parent, controller: "HotelApp"):
        super().__init__(parent, bg=BG_COLOR)

        # Frame fills the container
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Inner content is centered
        content = tk.Frame(self, bg=BG_COLOR)
        content.grid(row=0, column=0, sticky="n")

        # Title
        title = tk.Label(
            content,
            text="Hotel Management Main Menu",
            font=("TkDefaultFont", 28, "bold"),
            bg=BG_COLOR,
            fg=FG_COLOR
        )
        title.pack(pady=(0, 30))

        #--------------------Buttons----------------------
        #New Reservation Button
        new_reservation_btn = tk.Button(
            content,
            text="New Reservation",
            font=("TkDefaultFont", 16),
            width=20,
            command=lambda: controller.show_frame("rooms"),
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

        #Booking Records Button
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

        #Metrics Button
        metrics_btn = tk.Button(
            content,
            text="Metrics",
            font=("TkDefaultFont", 16),
            width=20,
            command=lambda: controller.show_frame("rooms"),
            bg="#34495E",
            fg=FG_COLOR,
            activebackground="#3D566E",
            activeforeground=FG_COLOR,
            relief="flat"
        )
        metrics_btn.pack(pady=10)

        #Employees Button
        employees_btn = tk.Button(
            content,
            text="Employees",
            font=("TkDefaultFont", 16),
            width=20,
            command=lambda: controller.show_frame("rooms"),
            bg="#34495E",
            fg=FG_COLOR,
            activebackground="#3D566E",
            activeforeground=FG_COLOR,
            relief="flat"
        )
        employees_btn.pack(pady=10)

        #Logout Button
        logout_btn = tk.Button(
            content,
            text="Logout",
            font=("TkDefaultFont", 16),
            width=20,
            command=lambda: controller.show_frame("login_screen"),
            bg="#34495E",
            fg=FG_COLOR,
            activebackground="#3D566E",
            activeforeground=FG_COLOR,
            relief="flat"
        )
        logout_btn.pack(pady=10)


if __name__ == "__main__":
    app = HotelApp()
    app.mainloop()
