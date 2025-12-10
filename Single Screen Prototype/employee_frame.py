import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from database_manager import DatabaseManager
import random

BG_APP = "#2C3E50"
PANEL_BG = "#34495E"

db = DatabaseManager()


class EmployeeProfileFrame(tk.Frame):
    def __init__(self, parent, controller: "HotelApp"):
        super().__init__(parent, bg=BG_APP)
        self.controller = controller

        # Search field variables
        self.search_id_var = tk.StringVar()
        self.search_name_var = tk.StringVar()
        self.search_role_var = tk.StringVar(value="")

        # Employee vars
        self.emp_id_var = tk.StringVar()
        self.first_name_var = tk.StringVar()
        self.last_name_var = tk.StringVar()
        self.role_var = tk.StringVar()
        self.phone_var = tk.StringVar()
        self.addr1_var = tk.StringVar()
        self.addr2_var = tk.StringVar()
        self.city_var = tk.StringVar()
        self.state_var = tk.StringVar()
        self.postal_var = tk.StringVar()

        # ---------- Title ----------
        title = tk.Label(
            self, text="Employee Profiles",
            bg=BG_APP, fg="white",
            font=("Arial", 30, "bold")
        )
        title.pack(pady=20)

        # ---------- Search Panel ----------
        search_frame = tk.Frame(self, bg=PANEL_BG, padx=20, pady=15)
        search_frame.pack(pady=10)

        # ID search
        tk.Label(search_frame, text="Employee ID:", bg=PANEL_BG, fg="white").grid(
            row=0, column=0, padx=5, pady=5, sticky="e"
        )
        entry_search_id = tk.Entry(search_frame, width=15, textvariable=self.search_id_var)
        entry_search_id.grid(row=0, column=1, padx=5, pady=5)

        # Name search
        tk.Label(search_frame, text="Name (partial):", bg=PANEL_BG, fg="white").grid(
            row=0, column=2, padx=5, pady=5, sticky="e"
        )
        entry_search_name = tk.Entry(search_frame, width=20, textvariable=self.search_name_var)
        entry_search_name.grid(row=0, column=3, padx=5, pady=5)

        # Role dropdown
        tk.Label(search_frame, text="Role:", bg=PANEL_BG, fg="white").grid(
            row=0, column=4, padx=5, pady=5, sticky="e"
        )
        role_dropdown = ttk.Combobox(
            search_frame,
            textvariable=self.search_role_var,
            values=["", "Manager", "Employee"],
            width=12,
            state="readonly"
        )
        role_dropdown.grid(row=0, column=5, padx=5, pady=5)
        role_dropdown.bind("<<ComboboxSelected>>", lambda e: self.reload_employee_list())

        # Search button
        search_btn = tk.Button(
            search_frame, text="Search", width=12, command=self.search_employees
        )
        search_btn.grid(row=0, column=6, padx=10, pady=5)

        # Results label
        tk.Label(
            search_frame, text="Results:", bg=PANEL_BG,
            fg="white", font=("Arial", 12, "bold")
        ).grid(row=1, column=0, padx=5, pady=(15, 5), sticky="ne")

        # Results listbox
        self.results_listbox = tk.Listbox(
            search_frame, width=60, height=8, font=("Arial", 12)
        )
        self.results_listbox.grid(
            row=1, column=1, columnspan=6, padx=10, pady=(15, 5), sticky="w"
        )
        self.results_listbox.bind("<<ListboxSelect>>", self.on_result_select)

        self.load_all_employees()

        # ---------- Bottom Buttons ----------
        button_frame = tk.Frame(self, bg=BG_APP)
        button_frame.pack(pady=15)

        back_btn = tk.Button(
            button_frame, text="Back", width=10,
            command=lambda: controller.show_frame("main_menu")
        )
        back_btn.pack(side="left", padx=10)


        new_btn = tk.Button(
            button_frame,
            text="Add New Employee",
            width=15,
            command=self.open_new_employee_popup
        )
        new_btn.pack(side="left", padx=10)

        entry_search_id.bind("<Return>", lambda e: self.search_employees())
        entry_search_name.bind("<Return>", lambda e: self.search_employees())

    # ---------------------------------------------------------------------
    # SEARCHING
    # ---------------------------------------------------------------------
    def search_employees(self):
        self.results_listbox.delete(0, tk.END)

        emp_id = self.search_id_var.get().strip()
        name = self.search_name_var.get().strip()
        role = self.search_role_var.get().strip()

        rows = db.search_employees(
            emp_id=emp_id if emp_id else None,
            name=name if name else None,
            role=role if role else None
        )

        if not rows:
            self.results_listbox.insert(tk.END, "No employees found.")
            return

        for eid, first, last, role in rows:
            self.results_listbox.insert(tk.END, f"{eid} - {first} {last} ({role})")

    def load_all_employees(self):
        self.results_listbox.delete(0, tk.END)
        role = self.search_role_var.get().strip()

        rows = db.load_all_employees(role if role else None)

        if not rows:
            self.results_listbox.insert(tk.END, "No employees found.")
            return

        for eid, first, last, role in rows:
            self.results_listbox.insert(tk.END, f"{eid} - {first} {last} ({role})")

    def reload_employee_list(self):
        if self.search_id_var.get().strip() or self.search_name_var.get().strip():
            self.search_employees()
        else:
            self.load_all_employees()

    def refresh(self):
        self.search_id_var.set("")
        self.search_name_var.set("")
        self.search_role_var.set("")
        self.load_all_employees()

    # ---------------------------------------------------------------------
    # PROFILE POPUP UTILITIES
    # ---------------------------------------------------------------------
    def create_profile_row(self, parent, label, value, key, editable=False):
        row = tk.Frame(parent, bg=PANEL_BG)
        row.pack(anchor="w", pady=4)

        tk.Label(row, text=f"{label}: ", fg="white", bg=PANEL_BG,
                 font=("Arial", 12, "bold")).pack(side="left")

        if editable:
            var = tk.StringVar(value=value or "")
            entry = tk.Entry(row, textvariable=var, width=30)
            entry.pack(side="left", padx=5)
            self.active_profile_entries[key] = var
            self.active_profile_widgets[key] = entry
        else:
            lbl = tk.Label(row, text=value or "—",
                           fg="white", bg=PANEL_BG,
                           font=("Arial", 12))
            lbl.pack(side="left")
            self.active_profile_widgets[key] = lbl

    def center_window(self, window):
        window.update_idletasks()
        w = window.winfo_width()
        h = window.winfo_height()
        sw = window.winfo_screenwidth()
        sh = window.winfo_screenheight()
        x = (sw // 2) - (w // 2)
        y = (sh // 2) - (h // 2)
        window.geometry(f"{w}x{h}+{x}+{y}")

    # ---------------------------------------------------------------------
    # PROFILE VIEW POPUP
    # ---------------------------------------------------------------------
    def on_result_select(self, event):
        selection = self.results_listbox.curselection()
        if not selection:
            return

        text = self.results_listbox.get(selection[0])
        if "No employees found" in text:
            return

        eid = text.split(" - ")[0]
        self.open_employee_profile_popup(eid)

    def open_employee_profile_popup(self, employee_id):
        data = db.get_employee_details(employee_id)
        if not data:
            return

        (
            eid, password, first, last, role,
            phone, addr1, addr2,
            city, state, postal
        ) = data

        popup = tk.Toplevel(self)
        popup.title(f"Employee Profile - {first} {last}")
        popup.configure(bg=BG_APP)
        popup.geometry("420x550")
        popup.grab_set()

        # Title
        tk.Label(
            popup, text=f"{first} {last}",
            font=("Arial", 20, "bold"),
            fg="white", bg=BG_APP
        ).pack(pady=15)

        # Card
        card = tk.Frame(popup, bg=PANEL_BG, padx=20, pady=20)
        card.pack(fill="both", expand=True, pady=10)

        self.active_profile_widgets = {}
        self.active_profile_entries = {}

        # Employee ID
        self.create_profile_row(card, "Employee ID", str(eid), "employee_id")

        # Password with toggle
        pw_frame = tk.Frame(card, bg=PANEL_BG)
        pw_frame.pack(anchor="w", pady=6)

        tk.Label(
            pw_frame, text="Password:", fg="white",
            bg=PANEL_BG, font=("Arial", 12, "bold")
        ).pack(side="left")

        masked_var = tk.StringVar(value="*" * len(password))
        lbl_pw = tk.Label(
            pw_frame, textvariable=masked_var, fg="white",
            bg=PANEL_BG, font=("Arial", 12)
        )
        lbl_pw.pack(side="left", padx=5)

        def toggle_pw():
            if masked_var.get().startswith("*"):
                masked_var.set(password)
                btn_toggle.config(text="Hide")
            else:
                masked_var.set("*" * len(password))
                btn_toggle.config(text="Show")

        btn_toggle = tk.Button(pw_frame, text="Show", width=6, command=toggle_pw)
        btn_toggle.pack(side="left", padx=8)

        # General fields
        self.create_profile_row(card, "Role", role, "role")
        self.create_profile_row(card, "Phone", phone, "phone")
        self.create_profile_row(card, "Address 1", addr1, "addr1")
        self.create_profile_row(card, "Address 2", addr2, "addr2")
        self.create_profile_row(card, "City", city, "city")
        self.create_profile_row(card, "State", state, "state")
        self.create_profile_row(card, "Postal Code", postal, "postal")

        # Buttons
        btn_frame = tk.Frame(popup, bg=BG_APP)
        btn_frame.pack(pady=15)

        tk.Button(btn_frame, text="Edit", width=12,
                  command=lambda: self._enter_edit_mode(popup, eid)).pack(
            side="left", padx=10
        )
        tk.Button(btn_frame, text="Close", width=12,
                  command=popup.destroy).pack(
            side="left", padx=10
        )

        self.center_window(popup)

    # ---------------------------------------------------------------------
    # EDIT MODE POPUP
    # ---------------------------------------------------------------------
    def _enter_edit_mode(self, old_popup, employee_id):
        old_popup.destroy()
        self.open_employee_edit_popup(employee_id)

    def format_edit_phone(self, var, entry_widget):
        """
        Auto-format a phone number in the edit popup as (123)-456-7890.
        Works with the edit_vars dictionary and its corresponding Entry widget.
        """
        raw = "".join(ch for ch in var.get() if ch.isdigit())
        raw = raw[:10]  # limit to 10 digits

        formatted = ""

        if len(raw) >= 1:
            formatted = "(" + raw[:3]
        if len(raw) >= 3:
            formatted = "(" + raw[:3] + ")"
        if len(raw) >= 4:
            formatted += "-" + raw[3:6]
        if len(raw) >= 7:
            formatted += "-" + raw[6:10]

        # Only update if changed
        if formatted != var.get():
            var.set(formatted)
            self.after_idle(lambda: entry_widget.icursor(tk.END))

    def open_employee_edit_popup(self, employee_id=None, create_mode=False):
        """
        Opens the popup to edit an existing employee OR create a new employee.
        If create_mode=True, the popup is blank and acts as a 'New Employee' window.
        """

        if not create_mode:
            # Editing existing employee
            data = db.get_employee_details(employee_id)
            if not data:
                return

            (
                eid, password, first, last, role,
                phone, addr1, addr2,
                city, state, postal
            ) = data
        else:
            # Creating a new employee
            eid = None
            password = ""
            first = ""
            last = ""
            role = "Employee"
            phone = ""
            addr1 = ""
            addr2 = ""
            city = ""
            state = ""
            postal = ""

        popup = tk.Toplevel(self)
        popup.title("Create New Employee" if create_mode else f"Edit Employee - {first} {last}")
        popup.configure(bg=BG_APP)
        popup.geometry("420x600")
        popup.grab_set()

        tk.Label(
            popup,
            text="Create New Employee" if create_mode else f"Editing {first} {last}",
            font=("Arial", 20, "bold"),
            fg="white",
            bg=BG_APP
        ).pack(pady=15)

        card = tk.Frame(popup, bg=PANEL_BG, padx=20, pady=20)
        card.pack(fill="both", expand=True, pady=10)

        # -------------------------------------------------------
        # EDITABLE FIELDS (used for both new + edit mode)
        # -------------------------------------------------------
        self.edit_vars = {}

        def make_entry(label, initial, key):
            frame = tk.Frame(card, bg=PANEL_BG)
            frame.pack(anchor="w", pady=4)

            tk.Label(
                frame, text=f"{label}: ",
                fg="white", bg=PANEL_BG,
                font=("Arial", 12, "bold")
            ).pack(side="left")

            var = tk.StringVar(value=initial or "")
            tk.Entry(frame, textvariable=var, width=30).pack(side="left")
            self.edit_vars[key] = var

        make_entry("Password", password, "password")
        make_entry("First Name", first, "first")
        make_entry("Last Name", last, "last")

        # --- Phone With Auto-Formatting ---
        phone_frame = tk.Frame(card, bg=PANEL_BG)
        phone_frame.pack(anchor="w", pady=4)

        tk.Label(
            phone_frame, text="Phone: ",
            fg="white", bg=PANEL_BG,
            font=("Arial", 12, "bold")
        ).pack(side="left")

        phone_var = tk.StringVar(value=phone or "")
        phone_entry = tk.Entry(phone_frame, textvariable=phone_var, width=30)
        phone_entry.pack(side="left")

        self.edit_vars["phone"] = phone_var
        phone_entry.bind("<KeyRelease>", lambda e: self.format_edit_phone(phone_var, phone_entry))

        make_entry("Address 1", addr1, "addr1")
        make_entry("Address 2", addr2, "addr2")
        make_entry("City", city, "city")
        make_entry("State", state, "state")
        make_entry("Postal Code", postal, "postal")

        # --- Role Dropdown ---
        role_frame = tk.Frame(card, bg=PANEL_BG)
        role_frame.pack(anchor="w", pady=4)

        tk.Label(
            role_frame, text="Role: ",
            fg="white", bg=PANEL_BG,
            font=("Arial", 12, "bold")
        ).pack(side="left")

        role_var = tk.StringVar(value=role)
        role_dropdown = ttk.Combobox(
            role_frame,
            textvariable=role_var,
            values=["Manager", "Employee"],
            width=28,
            state="readonly"
        )
        role_dropdown.pack(side="left")

        self.edit_vars["role"] = role_var

        # --------------------------
        # Bottom Buttons
        # --------------------------
        btn_frame = tk.Frame(popup, bg=BG_APP)
        btn_frame.pack(pady=15)

        # CREATE MODE BUTTON
        if create_mode:
            def create_employee():
                try:
                    unique_id = db.generate_unique_employee_id()

                    success = db.create_employee(
                        unique_id,
                        self.edit_vars["password"].get(),
                        self.edit_vars["first"].get(),
                        self.edit_vars["last"].get(),
                        self.edit_vars["role"].get(),
                        self.edit_vars["phone"].get(),
                        self.edit_vars["addr1"].get(),
                        self.edit_vars["addr2"].get(),
                        self.edit_vars["city"].get(),
                        self.edit_vars["state"].get(),
                        self.edit_vars["postal"].get()
                    )

                    if success:
                        messagebox.showinfo("Success", f"Employee created. ID: {unique_id}")
                        popup.destroy()
                        self.load_all_employees()
                    else:
                        messagebox.showerror("Error", "Failed to create employee.")


                except Exception as e:
                    messagebox.showerror("Database Error", str(e))

                finally:
                    conn.close()

            tk.Button(btn_frame, text="Create Employee", width=15, command=create_employee).pack(
                side="left", padx=10)

        else:
            # EDIT MODE BUTTONS ----------------------------------------
            def save_changes():
                try:
                    success = db.update_employee(
                        employee_id,
                        self.edit_vars["password"].get(),
                        self.edit_vars["first"].get(),
                        self.edit_vars["last"].get(),
                        self.edit_vars["role"].get(),
                        self.edit_vars["phone"].get(),
                        self.edit_vars["addr1"].get(),
                        self.edit_vars["addr2"].get(),
                        self.edit_vars["city"].get(),
                        self.edit_vars["state"].get(),
                        self.edit_vars["postal"].get()
                    )

                    if success:
                        messagebox.showinfo("Success", "Employee updated successfully.")
                        popup.destroy()
                        self.load_all_employees()
                    else:
                        messagebox.showerror("Error", "Failed to update employee.")

                except Exception as e:
                    messagebox.showerror("Database Error", str(e))
                finally:
                    conn.close()

            # --- DELETE EMPLOYEE BUTTON ---
            delete_frame = tk.Frame(popup, bg=BG_APP)
            delete_frame.pack(pady=(0, 10))

            delete_btn = tk.Button(
                delete_frame,
                text="Delete Employee",
                width=20,
                fg="white",
                bg="#AA0000",
                activebackground="#CC0000",
                command=lambda: self.delete_employee_record(employee_id, popup)
            )
            delete_btn.pack()

            # Save & Cancel buttons
            tk.Button(btn_frame, text="Save", width=12, command=save_changes).pack(side="left", padx=10)

        tk.Button(btn_frame, text="Cancel", width=12, command=popup.destroy).pack(side="left", padx=10)

        self.center_window(popup)

    def open_new_employee_popup(self):
        """Open the employee editor in create-new mode."""
        self.open_employee_edit_popup(employee_id=None, create_mode=True)


    def delete_employee_record(self, employee_id, popup):
        """Delete an employee after confirmation."""
        answer = messagebox.askyesno(
            "Delete Employee",
            "Are you sure you want to delete this employee?\n"
            "This action cannot be undone."
        )
        if not answer:
            return

        try:
            success = db.delete_employee(employee_id)

            if success:
                messagebox.showinfo("Deleted", "Employee removed.")
                popup.destroy()
                self.load_all_employees()
            else:
                messagebox.showerror("Error", "Failed to delete employee.")

            messagebox.showinfo("Deleted", "Employee has been removed from the system.")
            popup.destroy()
            self.load_all_employees()

        except Exception as e:
            messagebox.showerror("Database Error", str(e))
        finally:
            conn.close()



    def generate_unique_employee_id(self):
        """Generate a unique 5-digit employee ID (10000–99999)."""
        try:
            conn = db.connect()
            cur = conn.cursor()

            while True:
                new_id = random.randint(10000, 99999)

                cur.execute("SELECT 1 FROM employees WHERE employee_id = ?", (new_id,))
                exists = cur.fetchone()

                if not exists:
                    return new_id

        finally:
            conn.close()
