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
        self.frames["reservation_lookup"] = ReservationLookupFrame(self.container, self.controller or self)

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
            command=lambda: self.controller.show_frame("new_reservation"),
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
            command=lambda: self.controller.show_frame("rooms_status"),
            bg="#34495E",
            fg=FG_COLOR,
            activebackground="#3D566E",
            activeforeground=FG_COLOR,
            relief="flat"
        )
        view_rooms_btn.pack(pady=10)

        # Reservation Lookup Button
        def show_lookup():
            # Get the parent CustomerMenuFrame
            parent = self.master.master  # self.master is container, container.master is CustomerMenuFrame
            if hasattr(parent, 'show_frame'):
                parent.show_frame("reservation_lookup")
        
        lookup_btn = tk.Button(
            content,
            text="Lookup Reservation",
            font=("TkDefaultFont", 16),
            width=20,
            command=show_lookup,
            bg="#34495E",
            fg=FG_COLOR,
            activebackground="#3D566E",
            activeforeground=FG_COLOR,
            relief="flat"
        )
        lookup_btn.pack(pady=10)

        # Return to Menu Button
        return_btn = tk.Button(
            content,
            text="Return to Menu",
            font=("TkDefaultFont", 16),
            width=20,
            command=self.logout,
            bg="#34495E",
            fg=FG_COLOR,
            activebackground="#3D566E",
            activeforeground=FG_COLOR,
            relief="flat"
        )
        return_btn.pack(pady=10)

    def logout(self):
        #Clear current user and go back to splash screen.
        print("[DEBUG] logout() called")
        self.controller.current_user_id = None
        self.controller.current_user_role = None
        
        # If the controller has show_frame, use it to go to splash_screen
        if hasattr(self.controller, "show_frame"):
            print("[DEBUG] Controller has show_frame, showing splash_screen...")
            try:
                self.controller.show_frame("splash_screen")
                print("[DEBUG] Splash screen shown successfully")
                return
            except Exception as e:
                print(f"[DEBUG] show_frame failed: {e}")
                pass
        
        # If the controller can show the splash, try that (embedded splash flow)
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

#-----------------------------
# RESERVATION LOOKUP FRAME
#-----------------------------
class ReservationLookupFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_COLOR)
        self.controller = controller
        self.db = db
        self.hotel = HotelManager(self.db)

        # Title
        title = tk.Label(
            self,
            text="Find My Reservation",
            font=("TkDefaultFont", 24, "bold"),
            bg=BG_COLOR,
            fg=FG_COLOR
        )
        title.pack(pady=20)

        # Search bar frame
        top = tk.Frame(self, bg=BG_COLOR)
        top.pack(fill="x", padx=10, pady=10)

        tk.Label(top, text="Email:", bg=BG_COLOR, fg=FG_COLOR).grid(
            row=0, column=0, sticky="e", padx=5, pady=5
        )
        self.email_var = tk.StringVar()
        email_entry = tk.Entry(top, textvariable=self.email_var, width=30)
        email_entry.grid(row=0, column=1, sticky="w", padx=5, pady=5)

        tk.Label(top, text="Reservation ID:", bg=BG_COLOR, fg=FG_COLOR).grid(
            row=0, column=2, sticky="e", padx=5, pady=5
        )
        self.res_id_var = tk.StringVar()
        res_id_entry = tk.Entry(top, textvariable=self.res_id_var, width=10)
        res_id_entry.grid(row=0, column=3, sticky="w", padx=5, pady=5)

        # Results table
        cols = (
            "reservation_id",
            "guest_name",
            "email",
            "room_number",
            "check_in",
            "check_out",
            "status",
            "total_price",
        )

        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=10)
        for c in cols:
            self.tree.heading(c, text=c.replace("_", " ").title())
            self.tree.column(c, anchor="center", width=90)

        self.tree.column("guest_name", width=140)
        self.tree.column("email", width=170)
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        # Bottom buttons
        bottom = tk.Frame(self, bg=BG_COLOR)
        bottom.pack(fill="x", padx=10, pady=8)

        tk.Button(bottom, text="Search", width=12, command=self.do_search).pack(
            side="left", padx=5
        )
        tk.Button(
            bottom, text="Cancel Reservation", width=18, command=self.do_cancel
        ).pack(side="left", padx=5)
        tk.Button(bottom, text="Return to Menu", width=15, command=self.return_to_menu).pack(
            side="right", padx=5
        )

        # Bind enter keys
        email_entry.bind("<Return>", lambda e: self.do_search())
        res_id_entry.bind("<Return>", lambda e: self.do_search())

    def clear_rows(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

    def do_search(self):
        self.clear_rows()

        email = self.email_var.get().strip()
        res_raw = self.res_id_var.get().strip()

        if not email and not res_raw:
            messagebox.showwarning("Missing Info", "Enter email and/or reservation ID.")
            return

        res_id = None
        if res_raw:
            try:
                res_id = int(res_raw)
            except ValueError:
                messagebox.showerror("Bad ID", "Reservation ID must be a number.")
                return

        try:
            rows = self.hotel.search_reservation(
                reservation_id=res_id,
                email=email or None,
            )
        except Exception as ex:
            messagebox.showerror("Error", f"Search failed:\n{ex}")
            return

        if not rows:
            messagebox.showinfo("No Results", "No matching reservations were found.")
            return

        for r in rows:
            full_name = f"{r['first_name']} {r['last_name']}"
            price = float(r["total_price"] or 0.0)

            self.tree.insert(
                "",
                "end",
                values=(
                    r["reservation_id"],
                    full_name,
                    r["email"],
                    r["room_number"],
                    r["check_in_date"],
                    r["check_out_date"],
                    r["status"],
                    f"${price:.2f}",
                ),
            )

    def do_cancel(self):
        from datetime import datetime, date
        
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("No Selection", "Click a reservation row first.")
            return

        vals = self.tree.item(selected, "values")
        if not vals:
            return

        res_id = int(vals[0])
        status = vals[6]
        check_in_str = vals[4]

        # Only allow guests to cancel future Confirmed reservations
        if status != "Confirmed":
            messagebox.showinfo(
                "Not Allowed",
                "Only reservations with status 'Confirmed' can be cancelled here.",
            )
            return

        try:
            ci = datetime.strptime(check_in_str, "%Y-%m-%d").date()
        except ValueError:
            ci = date.today()

        if ci <= date.today():
            messagebox.showinfo(
                "Too Late",
                "Check-in day has started or passed.\nPlease contact the front desk.",
            )
            return

        if not messagebox.askyesno("Confirm", "Cancel this reservation?"):
            return

        try:
            receipt = self.hotel.cancel_reservation(res_id)
        except Exception as ex:
            messagebox.showerror("Error", f"Cancellation failed:\n{ex}")
            return

        msg = (
            f"Reservation {receipt['reservation_id']} cancelled.\n\n"
            f"Original Price: ${receipt['original_price']:.2f}\n"
            f"Cancellation Fee: ${receipt['cancellation_fee']:.2f}\n"
            f"Refund: ${receipt['refund_amount']:.2f}\n"
            f"Reason: {receipt['reason']}"
        )
        messagebox.showinfo("Cancelled", msg)
        self.do_search()  # refresh

    def return_to_menu(self):
        # Get the parent CustomerMenuFrame
        parent = self.master.master  # self.master is container, container.master is CustomerMenuFrame
        if hasattr(parent, 'show_frame'):
            parent.show_frame("main_menu")

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Customer Menu Preview")
    root.geometry("900x600")
    app = CustomerMenuFrame(root)
    app.pack(fill="both", expand=True)
    root.mainloop()