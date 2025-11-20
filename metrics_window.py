import tkinter as tk
from tkinter import ttk, messagebox
from database_manager import DatabaseManager
import sqlite3

# small dashboard for quick hotel metrics
db = DatabaseManager()


def open_metrics_window(parent=None):
	"""Open a small dashboard showing quick counts.

	If `parent` is provided this function will clear the parent's contents and
	render the dashboard inside it (so it updates the current window). If
	`parent` is None a new Toplevel will be created (fallback).
	"""

	if parent is not None:
		# reuse parent: clear and render into it
		for w in parent.winfo_children():
			w.destroy()
		container = parent
		container.config(bg="#395A7F")
	else:
		container = tk.Toplevel()
		container.title("Hotel Metrics")
		container.geometry("420x260")
		container.config(bg="#395A7F")

	tk.Label(container, text="Hotel Metrics", bg="#395A7F", fg="white", font=("Arial", 16, "bold")).pack(pady=12)

	frame = tk.Frame(container, bg="#395A7F")
	frame.pack(fill="both", expand=True, padx=12, pady=6)

	# value labels (updated by queries)
	total_rooms_var = tk.StringVar(value="-")
	available_rooms_var = tk.StringVar(value="-")
	active_res_var = tk.StringVar(value="-")
	cancelled_res_var = tk.StringVar(value="-")

	def query_count(sql, params=()):
		conn = None
		try:
			conn = db.connect()
			cur = conn.cursor()
			cur.execute(sql, params)
			row = cur.fetchone()
			return row[0] if row is not None else 0
		except sqlite3.Error as e:
			# If a table doesn't exist (e.g. reservations not created yet) treat as zero
			msg = str(e).lower()
			if "no such table" in msg:
				return 0
			# For other DB errors show an error popup
			messagebox.showerror("Database error", str(e))
			return 0
		finally:
			if conn:
				conn.close()

	def load_total_rooms():
		n = query_count("SELECT COUNT(*) FROM rooms")
		total_rooms_var.set(str(n))

	def load_available_rooms():
		n = query_count("SELECT COUNT(*) FROM rooms WHERE is_available = 1")
		available_rooms_var.set(str(n))

	def load_active_reservations():
		# Active/reserved statuses - mirror business logic
		n = query_count("SELECT COUNT(*) FROM reservations WHERE status IN (?, ?)", ("Confirmed", "Checked-in"))
		active_res_var.set(str(n))

	def load_cancelled_reservations():
		n = query_count("SELECT COUNT(*) FROM reservations WHERE status = ?", ("Cancelled",))
		cancelled_res_var.set(str(n))

	def refresh_all():
		load_total_rooms()
		load_available_rooms()
		load_active_reservations()
		load_cancelled_reservations()

	# Buttons + labels layout
	btn1 = tk.Button(frame, text="Total rooms", width=18, command=load_total_rooms)
	btn1.grid(row=0, column=0, padx=8, pady=8)
	lbl1 = tk.Label(frame, textvariable=total_rooms_var, width=10, bg="white", relief="sunken")
	lbl1.grid(row=0, column=1, padx=8, pady=8)

	btn2 = tk.Button(frame, text="Available rooms", width=18, command=load_available_rooms)
	btn2.grid(row=1, column=0, padx=8, pady=8)
	lbl2 = tk.Label(frame, textvariable=available_rooms_var, width=10, bg="white", relief="sunken")
	lbl2.grid(row=1, column=1, padx=8, pady=8)

	btn3 = tk.Button(frame, text="Active reservations", width=18, command=load_active_reservations)
	btn3.grid(row=2, column=0, padx=8, pady=8)
	lbl3 = tk.Label(frame, textvariable=active_res_var, width=10, bg="white", relief="sunken")
	lbl3.grid(row=2, column=1, padx=8, pady=8)

	btn4 = tk.Button(frame, text="Cancelled reservations", width=18, command=load_cancelled_reservations)
	btn4.grid(row=3, column=0, padx=8, pady=8)
	lbl4 = tk.Label(frame, textvariable=cancelled_res_var, width=10, bg="white", relief="sunken")
	lbl4.grid(row=3, column=1, padx=8, pady=8)

	# Refresh all button
	refresh_btn = tk.Button(container, text="Refresh all", command=refresh_all)
	refresh_btn.pack(pady=(2, 10))

	# Back button to restore main menu when rendering inside main window
	def go_back():
		if parent is not None:
			try:
				from main_window import show_home_screen
				show_home_screen()
			except Exception:
				# Fallback: clear container
				for w in container.winfo_children():
					w.destroy()
		else:
			container.destroy()

	if parent is not None:
		back_btn = tk.Button(container, text="Back", command=go_back)
		back_btn.pack(pady=(0, 6))

	# initial load
	refresh_all()

	return container

