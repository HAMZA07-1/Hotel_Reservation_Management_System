import os
import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import sys
from pathlib import Path
from customer_menu_frame import CustomerMenuFrame
from login_frame import LoginFrame

BG = "#2C3E50"
FG = "#ECF0F1"
BTN_BG = "#34495E"
BTN_FG = FG


def launch_staff_app(root):
    """Show the employee login frame in the same window (like logout button)."""
    if LoginFrame is None:
        messagebox.showerror("Missing module", f"Could not import LoginFrame")
        return

    # Clear root
    for w in root.winfo_children():
        w.destroy()

    # Minimal controller required by LoginFrame
    class EmployeeLoginController:
        def __init__(self, root_widget):
            self.root_widget = root_widget
            self.db = None
            self.hotel = None
            self.current_user_id = None
            self.current_user_name = None
            self.current_user_role = None
            self.frames = {}

        def show_frame(self, name):
            """Return to splash when login is cancelled or completed."""
            if name == "login_screen":
                # Go back to splash
                recreate_splash_in_window(self.root_widget)

    # Create a container frame for the login frame and back button
    container = tk.Frame(root, bg=BG)
    container.pack(fill="both", expand=True)

    # Top frame for back button
    top_frame = tk.Frame(container, bg=BG)
    top_frame.pack(fill="x", padx=10, pady=10)

    back_btn = tk.Button(
        top_frame,
        text="← Back to Splash",
        font=("TkDefaultFont", 10),
        bg=BTN_BG,
        fg=BTN_FG,
        activebackground="#3D566E",
        activeforeground=BTN_FG,
        relief="flat",
        command=lambda: recreate_splash_in_window(root)
    )
    back_btn.pack(side="left")

    # Content frame for login
    content_frame = tk.Frame(container, bg=BG)
    content_frame.pack(fill="both", expand=True)

    ctrl = EmployeeLoginController(root)
    frame = LoginFrame(content_frame, ctrl)
    frame.pack(fill="both", expand=True)


def recreate_splash_in_window(root):
    """Recreate the splash screen UI inside an existing root window."""
    # Clear existing widgets
    for w in root.winfo_children():
        w.destroy()
    
    # Main container that fills the entire window
    main_container = tk.Frame(root, bg=BG)
    main_container.pack(fill="both", expand=True)
    
    # Top spacer to push content down
    top_spacer = tk.Frame(main_container, bg=BG)
    top_spacer.pack(fill="both", expand=True)
    
    # Content frame (centered)
    content_frame = tk.Frame(main_container, bg=BG)
    content_frame.pack(fill="both", expand=False)
    
    # Title - more centered vertically and horizontally
    title = tk.Label(content_frame, text="Welcome to the Hotel", bg=BG, fg=FG, font=("Arial", 45, "bold"))
    title.pack(pady=(0, 6), padx=20)

    subtitle = tk.Label(content_frame, text="Guest Portal", bg=BG, fg=FG, font=("Arial", 14))
    subtitle.pack(pady=(0, 40), padx=20)

    # Center frame for buttons
    btn_frame = tk.Frame(content_frame, bg=BG)
    btn_frame.pack(pady=20)

    style_btn = {
        "bg": BTN_BG,
        "fg": BTN_FG,
        "activebackground": "#3D566E",
        "activeforeground": BTN_FG,
        "relief": "flat",
        "font": ("TkDefaultFont", 14),
        "width": 20,
        "height": 2,
    }

    enter_btn = tk.Button(btn_frame, text="Enter", command=lambda: open_customer_menu_in_root(root), **style_btn)
    enter_btn.grid(row=0, column=0, padx=18, pady=10)

    emp_btn = tk.Button(btn_frame, text="Employee Login", command=lambda: launch_staff_app(root), **style_btn)
    emp_btn.grid(row=0, column=1, padx=18, pady=10)

    # Bottom spacer
    bottom_spacer = tk.Frame(main_container, bg=BG)
    bottom_spacer.pack(fill="both", expand=True)
    
    # small footer note
    foot = tk.Label(root, text="For staff access use 'Employee Login'", bg=BG, fg=FG, font=("Arial", 9))
    foot.pack(side="bottom", pady=(12, 16))


def open_customer_menu_in_root(root):
    """Destroy splash widgets and show the CustomerMenuFrame inside the same root."""
    if CustomerMenuFrame is None:
        messagebox.showerror("Missing module", f"Could not import CustomerMenuFrame:\n{ImportError}")
        return

    # Clear root
    for w in root.winfo_children():
        w.destroy()

    # Minimal controller required by CustomerMenuFrame
    class FakeController:
        def __init__(self, root_widget):
            self.container = root_widget
            self.root_widget = root_widget  # Store reference for show_splash
            self.db = None
            self.hotel = None
            self.current_user_id = None
            self.current_user_name = None
            self.current_user_role = None  # Add role attribute
            self.frames = {}

        def show_frame(self, name):
            # Not used in this lightweight embedding, but present for compatibility
            pass
            
        def show_splash(self):
            """Recreate splash screen in the same window."""
            print("[DEBUG] show_splash() called!")
            # Clear the current content
            for w in self.root_widget.winfo_children():
                w.destroy()
            
            # Recreate the splash screen UI in the same window
            recreate_splash_in_window(self.root_widget)
            print("[DEBUG] Splash screen recreated!")

    ctrl = FakeController(root)
    frame = CustomerMenuFrame(root, ctrl)
    frame.pack(fill="both", expand=True)
    # If frame has refresh, call it
    if hasattr(frame, "refresh"):
        try:
            frame.refresh()
        except Exception:
            pass


def create_splash():
    root = tk.Tk()
    root.title("Welcome")
    # modest default size — will be centered and non-resizable
    w, h = 1920, 1080
    root.geometry(f"{w}x{h}")
    root.configure(bg=BG)
    root.resizable(False, False)

    # center on screen
    root.update_idletasks()
    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()
    x = (sw - w) // 2
    y = (sh - h) // 2
    root.geometry(f"{w}x{h}+{x}+{y}")

    # Main container that fills the entire window
    main_container = tk.Frame(root, bg=BG)
    main_container.pack(fill="both", expand=True)
    
    # Top spacer to push content down
    top_spacer = tk.Frame(main_container, bg=BG)
    top_spacer.pack(fill="both", expand=True)
    
    # Content frame (centered)
    content_frame = tk.Frame(main_container, bg=BG)
    content_frame.pack(fill="both", expand=False)

    # Title
    title = tk.Label(content_frame, text="Welcome to the Hotel", bg=BG, fg=FG, font=("Arial", 45, "bold"))
    title.pack(pady=(0, 6), padx=20)

    subtitle = tk.Label(content_frame, text="Customer Portal", bg=BG, fg=FG, font=("Arial", 14))
    subtitle.pack(pady=(0, 40), padx=20)

    # Center frame for buttons
    btn_frame = tk.Frame(content_frame, bg=BG)
    btn_frame.pack(pady=20)

    style_btn = {
        "bg": BTN_BG,
        "fg": BTN_FG,
        "activebackground": "#3D566E",
        "activeforeground": BTN_FG,
        "relief": "flat",
        "font": ("TkDefaultFont", 14),
        "width": 20,
        "height": 2,
    }

    def on_enter():
        open_customer_menu_in_root(root)

    enter_btn = tk.Button(btn_frame, text="Enter", command=on_enter, **style_btn)
    enter_btn.grid(row=0, column=0, padx=18, pady=10)

    emp_btn = tk.Button(btn_frame, text="Employee Login", command=lambda: launch_staff_app(root), **style_btn)
    emp_btn.grid(row=0, column=1, padx=18, pady=10)

    # Bottom spacer
    bottom_spacer = tk.Frame(main_container, bg=BG)
    bottom_spacer.pack(fill="both", expand=True)
    
    # small footer note
    foot = tk.Label(root, text="For staff access use 'Employee Login'", bg=BG, fg=FG, font=("Arial", 9))
    foot.pack(side="bottom", pady=(12, 16))

    return root


if __name__ == "__main__":
    app = create_splash()
    app.mainloop()