import tkinter as tk
from tkinter import ttk

# Try to import the customer UI function
try:
    from customer_window import open_customer_window
except Exception:
    open_customer_window = None

BG_COLOR = "#2C3E50"
FG_COLOR = "#ECF0F1"
PANEL_BG = "#34495E"


class CustomerMenuFrame(tk.Frame):
    """
    Small main-menu frame for customer actions.
    Designed to match the Single Screen Prototype style and to call
    `open_customer_window(...)` to render the customer-facing UI.
    """

    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_COLOR)
        self.controller = controller

        # Title
        title = tk.Label(
            self,
            text="Customer Portal",
            font=("TkDefaultFont", 20, "bold"),
            bg=BG_COLOR,
            fg=FG_COLOR,
        )
        title.pack(pady=(20, 18))

        # Info label (shows current logged-in user if any)
        self.info_label = tk.Label(self, text="", bg=BG_COLOR, fg=FG_COLOR, font=("TkDefaultFont", 10))
        self.info_label.pack(pady=(0, 12))

        # Buttons container
        content = tk.Frame(self, bg=BG_COLOR)
        content.pack()

        btn_style = {
            "font": ("TkDefaultFont", 14),
            "width": 26,
            "bg": PANEL_BG,
            "fg": FG_COLOR,
            "activebackground": "#3D566E",
            "activeforeground": FG_COLOR,
            "relief": "flat",
        }

        view_btn = tk.Button(content, text="View My Reservations", command=self.open_my_reservations, **btn_style)
        view_btn.pack(pady=8)

        guest_lookup_btn = tk.Button(content, text="Lookup By Email / ID", command=self.open_lookup, **btn_style)
        guest_lookup_btn.pack(pady=8)

        create_btn = tk.Button(content, text="Create New Reservation", command=self.open_create_flow, **btn_style)
        create_btn.pack(pady=8)

        back_btn = tk.Button(content, text="Back to Main Menu", command=lambda: controller.show_frame("main_menu"), **btn_style)
        back_btn.pack(pady=16)

    def refresh(self):
        """Called when the frame is shown — update info label."""
        name = getattr(self.controller, "current_user_name", None)
        uid = getattr(self.controller, "current_user_id", None)
        if name:
            self.info_label.config(text=f"Signed in: {name} (ID {uid})")
        else:
            self.info_label.config(text="Not signed in. Guests may lookup by email or ID.")

    def _ensure_customer_ui(self):
        if open_customer_window is None:
            tk.messagebox.showerror("Missing module", "customer_window.py not found or has import errors.")
            return False
        return True

    def open_my_reservations(self):
        """Open the customer UI pre-filled for the logged-in user (if any)."""
        if not self._ensure_customer_ui():
            return
        guest_id = getattr(self.controller, "current_user_id", None)
        # If no logged-in guest, open the lookup flow inside the main container
        open_customer_window(parent=self.controller.container, db=getattr(self.controller, "db", None),
                             hotel=getattr(self.controller, "hotel", None), guest_id=guest_id)

    def open_lookup(self):
        """Open the customer UI in lookup mode (no preselected guest)."""
        if not self._ensure_customer_ui():
            return
        open_customer_window(parent=self.controller.container, db=getattr(self.controller, "db", None),
                             hotel=getattr(self.controller, "hotel", None), guest_id=None)

    def open_create_flow(self):
        """Open the customer UI and focus new-reservation section (same view covers booking)."""
        if not self._ensure_customer_ui():
            return
        open_customer_window(parent=self.controller.container, db=getattr(self.controller, "db", None),
                             hotel=getattr(self.controller, "hotel", None), guest_id=getattr(self.controller, "current_user_id", None))