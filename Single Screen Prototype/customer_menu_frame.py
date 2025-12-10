import os
import sys
import subprocess
from pathlib import Path
from tkinter import messagebox
from tkinter import ttk

# Ensure repository root is on sys.path so imports from repo root work
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)
    
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
class CustomerMenuFrame(tk.Frame):
    def __init__(self, parent, controller=None):
        """Embed-able CustomerMenuFrame. Accepts (parent, controller) like other frames.

        If `controller` is not provided, this frame will act as its own controller
        for internal navigation (suitable for previews).
        """
        super().__init__(parent, bg=BG_COLOR)

        # Controller pattern: prefer provided controller, DON'T fall back to self
        # (self doesn't have show_splash, show_frame, etc.)
        self.controller = controller

        # Use the global db instance
        self.db = db
        self.hotel = HotelManager(self.db)
        # Allow DatabaseManager to reference HotelManager if needed
        self.db.hotel_manager = self.hotel

        # Current User logged in info
        self.current_user_id = None
        self.current_user_role = None
        self.current_user_name = None

        # Container for internal frames (keeps same pattern as HotelApp)
        self.container = tk.Frame(self, bg=BG_COLOR)
        self.container.pack(fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        # Screens created inside this container
        # Pass the actual controller (not self) to child frames
        self.frames["login_screen"] = LoginFrame(self.container, self.controller or self)
        self.frames["main_menu"] = MainMenuFrame(self.container, self.controller or self)
        self.frames["new_reservation"] = ReservationFormFrame(self.container, self.controller or self)

        for frame in self.frames.values():
            frame.grid(row=0, column=0, sticky="nsew")

        # Show main menu initially
        self.show_frame("main_menu")

    def show_frame(self, name):
        frame = self.frames.get(name)
        if frame is None:
            return
        frame.tkraise()
        if hasattr(frame, "refresh"):
            try:
                frame.refresh()
            except Exception:
                pass

#-----------------------------
# MAIN MENU
#-----------------------------
class MainMenuFrame(tk.Frame):
    def __init__(self, parent, controller):
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
        print("[DEBUG] logout() called")
        self.controller.current_user_id = None
        self.controller.current_user_role = None
        
        # If the controller can show the splash, prefer that (embedded splash flow)
        if hasattr(self.controller, "show_splash"):
            print("[DEBUG] Controller has show_splash, calling it...")
            try:
                self.controller.show_splash()
                print("[DEBUG] show_splash completed successfully")
                return
            except Exception as e:
                print(f"[DEBUG] show_splash failed: {e}")
                pass
        else:
            print("[DEBUG] Controller does NOT have show_splash attribute")
        
        # Fallback: close the top-level window
        print("[DEBUG] Using fallback: destroying top-level window")
        try:
            top = self.winfo_toplevel()
            top.destroy()
        except Exception:
            pass

    def refresh(self):
        #updates room availability based on reservation date
        self.db.update_room_availability_today()

        #Updates reservations based on date and times
        self.db.run_daily_reservation_updates()
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

    def launch_employee_app(self):
        """Launch the staff app (`main.py`) in a new process."""
        # main.py is expected in the same folder (Single Screen Prototype/main.py)
        main_path = Path(__file__).resolve().parent / "main.py"
        if not main_path.exists():
            messagebox.showerror("Not found", f"Could not find staff app at:\n{main_path}")
            return
        try:
            subprocess.Popen([sys.executable, str(main_path)])
        except Exception as e:
            messagebox.showerror("Launch failed", f"Failed to start staff app:\n{e}")
            return

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Customer Menu Preview")
    root.geometry("900x600")
    app = CustomerMenuFrame(root)
    app.pack(fill="both", expand=True)
    root.mainloop()