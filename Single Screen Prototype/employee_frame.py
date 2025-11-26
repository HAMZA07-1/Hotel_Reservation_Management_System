import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from database_manager import DatabaseManager

BG_APP = "#2C3E50"
PANEL_BG = "#34495E"

db = DatabaseManager()

class EmployeeProfileFrame(tk.Frame):
    def __init__(self, parent, controller: "HotelApp"):
        super().__init__(parent, bg=BG_APP)
        self.controller = controller

        # currently selected employee data
        self.current_employee_id = None

        # StringVars for form fields
        self.search_id_var = tk.StringVar()
        self.search_name_var = tk.StringVar()

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
        self.country_var = tk.StringVar()

        # ---------- Title ----------
        title = tk.Label(
            self,
            text="Employee Profiles",
            bg=BG_APP,
            fg="white",
            font=("Arial", 22, "bold")
        )
        title.pack(pady=20)

        # ---------- Top: Search Panel ----------
        search_frame = tk.Frame(self, bg=PANEL_BG, padx=20, pady=15)
        search_frame.pack(pady=10)

        # Search by ID
        tk.Label(search_frame, text="Employee ID:", bg=PANEL_BG, fg="white").grid(
            row=0, column=0, padx=5, pady=5, sticky="e"
        )
        entry_search_id = tk.Entry(search_frame, width=15, textvariable=self.search_id_var)
        entry_search_id.grid(row=0, column=1, padx=5, pady=5)

        # Search by Name (partial match)
        tk.Label(search_frame, text="Name (partial):", bg=PANEL_BG, fg="white").grid(
            row=0, column=2, padx=5, pady=5, sticky="e"
        )
        entry_search_name = tk.Entry(search_frame, width=20, textvariable=self.search_name_var)
        entry_search_name.grid(row=0, column=3, padx=5, pady=5)

        search_btn = tk.Button(
            search_frame,
            text="Search",
            width=12,
            command=self.search_employees
        )
        search_btn.grid(row=0, column=4, padx=10, pady=5)

        # Listbox of results
        tk.Label(search_frame, text="Results:", bg=PANEL_BG, fg="white").grid(
            row=1, column=0, padx=5, pady=(10,5), sticky="nw"
        )

        self.results_listbox = tk.Listbox(search_frame, width=50, height=6)
        self.results_listbox.grid(row=1, column=1, columnspan=3, padx=5, pady=(10,5), sticky="w")

        # When user selects a result, load that employee
        self.results_listbox.bind("<<ListboxSelect>>", self.on_result_select)

        # ---------- Middle: Form Panel ----------
        form_frame = tk.Frame(self, bg=PANEL_BG, padx=20, pady=20)
        form_frame.pack(pady=10, fill="x")

        # Row 0: ID (read-only), Role (read-only)
        tk.Label(form_frame, text="Employee ID:", bg=PANEL_BG, fg="white").grid(
            row=0, column=0, padx=5, pady=5, sticky="e"
        )
        entry_emp_id = tk.Entry(form_frame, width=15, textvariable=self.emp_id_var, state="readonly")
        entry_emp_id.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        tk.Label(form_frame, text="Role:", bg=PANEL_BG, fg="white").grid(
            row=0, column=2, padx=5, pady=5, sticky="e"
        )
        entry_role = tk.Entry(form_frame, width=15, textvariable=self.role_var, state="readonly")
        entry_role.grid(row=0, column=3, padx=5, pady=5, sticky="w")

        # Row 1: First & Last name (read-only for now; you can make editable if you want)
        tk.Label(form_frame, text="First Name:", bg=PANEL_BG, fg="white").grid(
            row=1, column=0, padx=5, pady=5, sticky="e"
        )
        entry_first = tk.Entry(form_frame, width=20, textvariable=self.first_name_var, state="readonly")
        entry_first.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        tk.Label(form_frame, text="Last Name:", bg=PANEL_BG, fg="white").grid(
            row=1, column=2, padx=5, pady=5, sticky="e"
        )
        entry_last = tk.Entry(form_frame, width=20, textvariable=self.last_name_var, state="readonly")
        entry_last.grid(row=1, column=3, padx=5, pady=5, sticky="w")

        # Row 2: Phone
        tk.Label(form_frame, text="Phone:", bg=PANEL_BG, fg="white").grid(
            row=2, column=0, padx=5, pady=5, sticky="e"
        )
        entry_phone = tk.Entry(form_frame, width=20, textvariable=self.phone_var)
        entry_phone.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        # Row 3: Address Line 1
        tk.Label(form_frame, text="Address Line 1:", bg=PANEL_BG, fg="white").grid(
            row=3, column=0, padx=5, pady=5, sticky="e"
        )
        entry_addr1 = tk.Entry(form_frame, width=35, textvariable=self.addr1_var)
        entry_addr1.grid(row=3, column=1, columnspan=3, padx=5, pady=5, sticky="w")

        # Row 4: Address Line 2
        tk.Label(form_frame, text="Address Line 2:", bg=PANEL_BG, fg="white").grid(
            row=4, column=0, padx=5, pady=5, sticky="e"
        )
        entry_addr2 = tk.Entry(form_frame, width=35, textvariable=self.addr2_var)
        entry_addr2.grid(row=4, column=1, columnspan=3, padx=5, pady=5, sticky="w")

        # Row 5: City / State
        tk.Label(form_frame, text="City:", bg=PANEL_BG, fg="white").grid(
            row=5, column=0, padx=5, pady=5, sticky="e"
        )
        entry_city = tk.Entry(form_frame, width=20, textvariable=self.city_var)
        entry_city.grid(row=5, column=1, padx=5, pady=5, sticky="w")

        tk.Label(form_frame, text="State/Prov:", bg=PANEL_BG, fg="white").grid(
            row=5, column=2, padx=5, pady=5, sticky="e"
        )
        entry_state = tk.Entry(form_frame, width=15, textvariable=self.state_var)
        entry_state.grid(row=5, column=3, padx=5, pady=5, sticky="w")

        # Row 6: Postal / Country
        tk.Label(form_frame, text="Postal Code:", bg=PANEL_BG, fg="white").grid(
            row=6, column=0, padx=5, pady=5, sticky="e"
        )
        entry_postal = tk.Entry(form_frame, width=15, textvariable=self.postal_var)
        entry_postal.grid(row=6, column=1, padx=5, pady=5, sticky="w")

        tk.Label(form_frame, text="Country:", bg=PANEL_BG, fg="white").grid(
            row=6, column=2, padx=5, pady=5, sticky="e"
        )
        entry_country = tk.Entry(form_frame, width=15, textvariable=self.country_var)
        entry_country.grid(row=6, column=3, padx=5, pady=5, sticky="w")

        # ---------- Bottom: Buttons ----------
        button_frame = tk.Frame(self, bg=BG_APP)
        button_frame.pack(pady=15)

        save_btn = tk.Button(
            button_frame,
            text="Save Changes",
            width=15,
            command=self.save_changes
        )
        save_btn.pack(side="left", padx=10)

        back_btn = tk.Button(
            button_frame,
            text="Back",
            width=10,
            command=lambda: controller.show_frame("main_menu")
        )
        back_btn.pack(side="left", padx=10)

        # Bind Enter in search fields to trigger search
        entry_search_id.bind("<Return>", lambda e: self.search_employees())
        entry_search_name.bind("<Return>", lambda e: self.search_employees())

    # ---------------------------------
    # Searching employees
    # ---------------------------------
    def search_employees(self):
        """Search by ID or partial name and show in listbox."""
        self.results_listbox.delete(0, tk.END)

        emp_id = self.search_id_var.get().strip()
        name_part = self.search_name_var.get().strip()

        conn = None
        try:
            conn = db.connect()
            cur = conn.cursor()

            base_query = """
                SELECT employee_id, first_name, last_name, role
                FROM employees
                WHERE 1=1
            """
            params = []

            if emp_id:
                base_query += " AND employee_id = ?"
                params.append(emp_id)

            if name_part:
                base_query += " AND (first_name || ' ' || last_name) LIKE ?"
                params.append(f"%{name_part}%")

            base_query += " ORDER BY last_name, first_name"

            cur.execute(base_query, params)
            rows = cur.fetchall()

            for r in rows:
                eid, first, last, role = r
                display = f"{eid} - {first} {last} ({role})"
                self.results_listbox.insert(tk.END, display)

            if not rows:
                self.results_listbox.insert(tk.END, "No employees found.")

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", str(e))
        finally:
            if conn:
                conn.close()

    def on_result_select(self, event):
        """When user selects an employee in the listbox, load their details."""
        selection = self.results_listbox.curselection()
        if not selection:
            return

        text = self.results_listbox.get(selection[0])
        if text.startswith("No employees"):
            return

        # Expect format: "id - First Last (Role)"
        try:
            eid = text.split(" - ", 1)[0].strip()
        except Exception:
            return

        self.load_employee(eid)

    def load_employee(self, employee_id):
        """Load full details for an employee and populate form fields."""
        conn = None
        try:
            conn = db.connect()
            cur = conn.cursor()

            cur.execute(
                """
                SELECT employee_id, first_name, last_name, role,
                       phone_number,
                       address_line1, address_line2,
                       city, state_province, postal_code, country
                FROM employees
                WHERE employee_id = ?
                """,
                (employee_id,)
            )
            row = cur.fetchone()
            if row is None:
                messagebox.showerror("Error", "Employee not found.")
                return

            (
                eid, first, last, role,
                phone,
                addr1, addr2,
                city, state, postal, country
            ) = row

            self.current_employee_id = eid

            # Fill vars
            self.emp_id_var.set(str(eid))
            self.first_name_var.set(first or "")
            self.last_name_var.set(last or "")
            self.role_var.set(role or "")

            self.phone_var.set(phone or "")
            self.addr1_var.set(addr1 or "")
            self.addr2_var.set(addr2 or "")
            self.city_var.set(city or "")
            self.state_var.set(state or "")
            self.postal_var.set(postal or "")
            self.country_var.set(country or "")

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", str(e))
        finally:
            if conn:
                conn.close()

    # ---------------------------------
    # Saving changes
    # ---------------------------------
    def save_changes(self):
        """Save phone/address changes for the current employee."""
        if not self.current_employee_id:
            messagebox.showwarning("No employee selected", "Please select an employee first.")
            return

        conn = None
        try:
            conn = db.connect()
            cur = conn.cursor()

            cur.execute(
                """
                UPDATE employees
                SET phone_number   = ?,
                    address_line1  = ?,
                    address_line2  = ?,
                    city           = ?,
                    state_province = ?,
                    postal_code    = ?,
                    country        = ?
                WHERE employee_id  = ?
                """,
                (
                    self.phone_var.get().strip() or None,
                    self.addr1_var.get().strip() or None,
                    self.addr2_var.get().strip() or None,
                    self.city_var.get().strip() or None,
                    self.state_var.get().strip() or None,
                    self.postal_var.get().strip() or None,
                    self.country_var.get().strip() or None,
                    self.current_employee_id,
                )
            )
            conn.commit()
            messagebox.showinfo("Success", "Employee information updated.")

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", str(e))
        finally:
            if conn:
                conn.close()

    # ---------------------------------
    # Refresh when shown
    # ---------------------------------
    def refresh(self):
        """Called when this frame is shown."""
        # Clear search + listbox, keep existing selection if you want
        self.search_id_var.set("")
        self.search_name_var.set("")
        self.results_listbox.delete(0, tk.END)
