import tkinter.font as tkFont
import os
import sys
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from itertools import cycle
from config import gemini_api_key

g_paid_sum =0  
debounce_timer = None
debounce_timer_cust = None







# -------------------- Settings --------------------
def open_settings():
    messagebox.showinfo("Settings", "Settings window opened (stub)")

# -------------------- GUI Setup --------------------
root = tk.Tk()
root.title("Tota Billing System")
#root.geometry("1450x700")
root.state("zoomed")
root.configure(bg="#ffffff")  # main bg

# -------------------- Colors --------------------
sidebar_bg = "#4181C8"
sidebar_hover = "#566573"
sidebar_fg = "white"
main_bg = "#f0f2f5"
main_fg = "#333333"
# -------------------- Hover Effect --------------------
def on_enter(e):
    e.widget['bg'] = sidebar_hover
def on_leave(e):
    e.widget['bg'] = sidebar_bg

# -------------------- Main Frames --------------------
main_frame = tk.Frame(root, bg=main_bg)
main_frame.pack(fill="both", expand=True)

menu_frame = tk.Frame(main_frame, width=280, bg=sidebar_bg)
menu_frame.pack(side="left", fill="y")
menu_frame.pack_propagate(False) 

content_frame = tk.Frame(main_frame, bg=main_bg)
content_frame.pack(side="right", fill="both", expand=True)

# --------------------  Label --------------------
gym_label_var = tk.StringVar(value="Billing System")
gym_label = tk.Label(content_frame, textvariable=gym_label_var,
                     font=("Segoe UI", 22, "bold"),
                     bg=main_bg, fg=main_fg)
gym_label.pack(pady=20)

# -------------------- User Info -------------------

user_info_frame = tk.Frame(menu_frame, bg="#4181C8", bd=0)
user_info_frame.pack(fill="x", pady=20, padx=10)

text_label = tk.Label(
    user_info_frame, 
    text="Tota Dashboard",  # <- یہاں '=' ضروری ہے
    font=("Arial", 16, "bold"),  # font size بڑھا دیا heading کے لیے
    bg="#4181C8", 
    fg="white"
)
text_label.pack(padx=10, pady=10, anchor="center")  # heading center میں آئے



# -------------------- Tabs --------------------
member_tab = tk.Frame(content_frame, bg=main_bg)
attendance_tab = tk.Frame(content_frame, bg=main_bg)
info_tab = tk.Frame(content_frame, bg=main_bg)

for frame in (member_tab, attendance_tab, info_tab):
    frame.place(relwidth=1, relheight=1)

# -------------------- DB Setup --------------------
import sqlite3
import tkinter as tk
from tkinter import messagebox
from tkcalendar import DateEntry  # pip install tkcalendar

conn = sqlite3.connect("tota.db")
cursor = conn.cursor()


# ------------------ Customers Table ------------------
cursor.execute('''
CREATE TABLE IF NOT EXISTS customers (
    customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_name TEXT NOT NULL,
    phone_number TEXT,
    description TEXT
)
''')
conn.commit()

# ------------------ Bills Table ------------------
cursor.execute('''
CREATE TABLE IF NOT EXISTS bills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,   -- auto-incremented internal ID
    bill_id TEXT,                           -- customer-specific counter (1-1, 1-2, etc.)
    customer_id INTEGER,
    date TEXT,
    item TEXT,
    weight REAL,
    fee_unit REAL,
    amount REAL,
    entry_type TEXT,
    
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
)
''')
conn.commit()



# -------------------- Billing Tab --------------------
def create_bill_action():
    # Clear previous widgets
    for widget in attendance_tab.winfo_children():
        widget.destroy()

    # ---------------- Back Button ----------------
    def back_to_billing_home():
        attendance_tab_home()  # call the function to recreate home

    back_btn = tk.Button(attendance_tab, text="← Back", font=("Segoe UI", 12, "bold"),
                         bg="#ff6347", fg="white", activebackground="#e5533d",
                         command=back_to_billing_home)
    back_btn.pack(anchor="ne", padx=10, pady=10)

    # ---------------- Customer Details ----------------
    customer_frame = tk.LabelFrame(attendance_tab, text="کسٹمر کی معلومات ✅",
                                   font=("Segoe UI", 18, "bold"),
                                   bg=main_bg, fg=main_fg, padx=20, pady=10)
    customer_frame.pack(fill="x", padx=5, pady=(5,5))


    tk.Label(customer_frame, text="فون نمبر:", font=("Segoe UI", 15,"bold"),
             bg=main_bg, fg="#333").grid(row=0, column=1, sticky="w", pady=(0,5))

    phone_entry = tk.Entry(customer_frame, font=("Segoe UI",15,"bold"), width=20)
    phone_entry.grid(row=1, column=1, padx=(0,20), pady=(0,10))

    tk.Label(customer_frame, text="تاریخ:", font=("Segoe UI", 15,"bold"),
             bg=main_bg, fg="#333").grid(row=0, column=2, sticky="w", pady=(0,5))



    tk.Label(customer_frame, text="تفصیل:", font=("Segoe UI", 15,"bold"),
             bg=main_bg, fg="#333").grid(row=0, column=3, sticky="w", pady=(0,5))
    
    # Multi-line Textbox (instead of Entry)
    description_entry = tk.Text(customer_frame, font=("Segoe UI", 12), width=25, height=3)
    description_entry.grid(row=1, column=3, padx=(0,20), pady=(0,10))





    tk.Label(customer_frame, text="سبقہ بل ", font=("Segoe UI", 15,"bold"),
             bg=main_bg, fg="#333").grid(row=2, column=3, sticky="w", padx=(20,5), pady=(0,10))

    date_entry = DateEntry(customer_frame, font=("Segoe UI", 12), width=12,
                           background='darkblue', foreground='white', borderwidth=2)
    date_entry.grid(row=1, column=2, pady=(0,10))



    tk.Label(customer_frame, text="کسٹمر کا نام:", font=("Segoe UI", 15,"bold"),
             bg=main_bg, fg="#333").grid(row=0, column=0, sticky="w", pady=(0,5))

    customer_var = tk.StringVar()
    customer_name_entry = tk.Entry(customer_frame, textvariable=customer_var,
                                font=("Segoe UI", 12), width=18)
    customer_name_entry.grid(row=1, column=0, padx=(0, 20), pady=(0, 10))

    # ---------------- Suggestion Listbox ----------------
    bold_font = tkFont.Font(family="Segoe UI", size=12, weight="bold")
    customer_suggestion_box = tk.Listbox(customer_frame, height=3, width=18, font=bold_font)
    customer_suggestion_box.place_forget()  # hide initially

    # --- Agent Define (same as search box agent) ---
    from agents import Agent, Runner
    from config import config

    customer_agent = Agent(
        name="Customer Name Agent",
        instructions=(
            "Tum Roman Urdu me likhe gaye naam ko Urdu me convert karo "
            "aur uske 3-4 milte julte full name suggestions do. "
            "Sirf naam likho, aur har naam nayi line me ho."
        )
    )

    debounce_timer_cust = None
    loading_job_cust = None

    # ---------------- Loading Spinner ----------------
    def animate_loading_cust():
        dots = ["Loading", "Loading.", "Loading..", "Loading..."]
        current = customer_suggestion_box.get(0) if customer_suggestion_box.size() > 0 else ""
        try:
            idx = dots.index(current)
        except ValueError:
            idx = 0
        next_text = dots[(idx + 1) % len(dots)]
        customer_suggestion_box.delete(0, tk.END)
        customer_suggestion_box.insert(tk.END, next_text)

        global loading_job_cust
        loading_job_cust = customer_frame.after(400, animate_loading_cust)

        # ---------------- Suggestion Placement ----------------
    def place_customer_suggestion_box():
        customer_frame.update_idletasks()
        x = customer_name_entry.winfo_x()
        y = customer_name_entry.winfo_y()

        # Thoda adjust karo
        adjusted_x = x = 0    # agar right ja raha hai to 0 ya -2 kar do
        adjusted_y = y  + 0  # niche karna hai to + value
                                                                # upar karna hai to - value
        customer_suggestion_box.place(x=adjusted_x, y=adjusted_y)
        customer_suggestion_box.lift()
    # ---------------- Fetch Suggestions (Agent call) ----------------
    def fetch_customer_suggestions(query):
        global loading_job_cust
        customer_suggestion_box.delete(0, tk.END)
        customer_suggestion_box.insert(tk.END, "Loading")
        place_customer_suggestion_box()
        animate_loading_cust()

        try:
            result = Runner.run_sync(customer_agent, query, run_config=config)
            urdu_text = result.final_output.strip()

            # Stop spinner
            if loading_job_cust:
                customer_frame.after_cancel(loading_job_cust)
                loading_job_cust = None

            # Fill with suggestions
            customer_suggestion_box.delete(0, tk.END)
            for line in urdu_text.split("\n"):
                if line.strip():
                    customer_suggestion_box.insert(tk.END, line.strip())

            customer_suggestion_box.config(height=min(customer_suggestion_box.size(), 6))
            place_customer_suggestion_box()

        except Exception as e:
            if loading_job_cust:
                customer_frame.after_cancel(loading_job_cust)
                loading_job_cust = None
            customer_suggestion_box.delete(0, tk.END)
            customer_suggestion_box.insert(tk.END, f"Error: {e}")
            place_customer_suggestion_box()

    # ---------------- Debounce Search ----------------
    def update_customer_suggestions(event=None):
        global debounce_timer_cust
        typed = customer_var.get().strip()

        if not typed:
            customer_suggestion_box.place_forget()
            return

        if debounce_timer_cust:
            customer_frame.after_cancel(debounce_timer_cust)

        debounce_timer_cust = customer_frame.after(500, lambda: fetch_customer_suggestions(typed))

    # ---------------- Fill from Suggestion ----------------
    def fill_customer_from_suggestion(event):
        selection = customer_suggestion_box.curselection()
        if selection:
            choice = customer_suggestion_box.get(selection[0])
            if not choice.startswith("Loading") and not choice.startswith("Error"):
                customer_name_entry.delete(0, tk.END)
                customer_name_entry.insert(0, choice)
            customer_suggestion_box.place_forget()

    # ---------------- Bindings ----------------
    customer_name_entry.bind("<KeyRelease>", update_customer_suggestions)
    customer_suggestion_box.bind("<ButtonRelease-1>", fill_customer_from_suggestion)
    customer_suggestion_box.bind("<Double-Button-1>", fill_customer_from_suggestion)

    # ---------------- Due Balance Field ----------------
    due_balance_var = tk.StringVar()
    due_balance_entry = tk.Entry(customer_frame, font=("Segoe UI", 12),
                                 textvariable=due_balance_var, width=15, state="readonly")
    due_balance_entry.grid(row=2, column=2, padx=(0,20), pady=(0,10))

    # ---------------- Search Button ----------------
    def search_due_balance():
        try:
            name = customer_name_entry.get().strip()
            if not name:
                messagebox.showwarning("Warning", "Please enter a customer name.")
                return

            # --- Customer ID aur Description nikal lo ---
            cursor.execute("SELECT customer_id, description FROM customers WHERE customer_name = ?", (name,))
            result = cursor.fetchone()
            if not result:
                messagebox.showinfo("Info", "Customer not found.")
                due_balance_var.set("0")
                description_entry.delete("1.0", tk.END)   # clear description box
                return
            
            customer_id, description = result

            # --- Description show kar do (chahe due ho ya na ho) ---
            description_entry.delete("1.0", tk.END)   # clear old text
            if description:
                description_entry.insert(tk.END, description)
            else:
                description_entry.insert(tk.END, "No description available")

            # --- Due Balance calculate kar lo ---
            cursor.execute("""
                SELECT SUM(amount) 
                FROM bills 
                WHERE customer_id = ? AND entry_type = 'Due'
            """, (customer_id,))
            result = cursor.fetchone()
            due_amount = result[0] if result[0] is not None else 0
            due_balance_var.set(str(due_amount))

        except Exception as e:
            messagebox.showerror("Error", f"Error fetching due balance: {e}")

    search_btn = tk.Button(customer_frame, text="Search", font=("Segoe UI", 12, "bold"),
                           bg="#28a745", fg="white", activebackground="#218838",
                           command=search_due_balance)
    search_btn.grid(row=2, column=1, padx=(0,10), pady=(0,10))



    # ---------------- Bill Items ----------------
    bill_frame = tk.LabelFrame(attendance_tab, text="بل آئٹمز ✅",
                               font=("Segoe UI", 17, "bold"),
                               bg=main_bg, fg=main_fg, padx=5, pady=5)
    bill_frame.pack(fill="x", padx=20, pady=(0,5))

    # ---------------- Item Mapping Dictionary ----------------
    item_map = {
        "kali fles": "کالی فلیس",
        "kodi kat": "کوڑی کاٹ",
        "lal kat": "لال کاٹ",
        "pink kat": "پنک کاٹ",
        "brown kat": "براؤن کاٹ",
        "blue kat": "بلیو کاٹ",
        "kali kat": "کالی کاٹ",
        "mongya kat": "مونگیا کاٹ",
        "rang dar kat": "رنگ دار کاٹ",
        "nabi kat": "نابی کاٹ",
        "1/2 number kat": "1/2 نمبر کاٹ",
        "vip kat": "vip کاٹ",
        "meter up fles": "میٹر اپ فلیس",
        "foot fles": "فُٹ فلیس",
        "kodi rassi": "کوڑی رسی",
        "kodi orlak": "کوڑی اورلاک",
        "kachra": "کچرا",
        "ballan": "بَلَن",
        "1/2 number orlak": "1/2 نمبر اورلاک",
        "pink orlak": "پنک اورلاک",
        "brown orlak": "براؤن اورلاک",
        "kali orlak": "کالی اورلاک",
        "mongya orlak": "مونگیا اورلاک",
        "lal orlak": "لال اورلاک",
        "rang dar orlak": "رنگ دار اورلاک",
        "nabi orlak": "نابی اورلاک",
        "grey orlak": "گرے اورلاک",
        "grey kat": "گرے کاٹ",
        "sawa number kat": "ساوا نمبر کاٹ",
        "pari": "پارئی",
        "kali pc": "کالی پی سی",
        "khali kon": "خالی کون",
        "rang dar kon": "رنگ دار کون",
        "number 1 nalkee": "نمبر ایک نلکی",
        "number 2 nalkee": "نمبر دو نلکی",
        "semika": "سیمیکا",
        "tuwaee avarlack": "تویئ اورلاک",
        "paraee caat": "پارئی کاٹ",
        "paraee avarlack": "پارئی اورلاک",
        "garay faleece": "گرے فلیس",
        "garay pc": "pc گرے ",
        "sawa garay": "ساوا گرے",
        "damage": "ڈیمیج",
        "damage faleece": "ڈیمیج فلیس",
        "damage jersey": "ڈیمیج جرسی",
        "lastic": "لاسٹک",
        "lastic roll": "لاسٹک رول",
        "dori": "ڈوری",
        "tasma": "تسمہ",
        "kori catan": "کورئ کاٹن",
        "white faleece": "وائٹ فلیس",
        "white pc": "وائٹ پی سی",
        "blue faleece": "بلیو فلیس",
        "back&front": "بیک اینڈ فرنٹ",
        "print": "پرنٹ",
        "h. d": "H. D",
        "dang": "ڈینگ",
        "catan tuwaee": "کاٹن تویئ",
        "laycra": "لائکرا",
        "kali catan": "کالی کاٹن",
        "shalfa": "شالفا",
        "poyster": "پولیسٹر",
        "foot meter": "فٹ میٹر",
        "mix nalki": "مکس نلکی",
        "gata": "گٹا",
        "kali khali koon": "کالی خالی کون",
        "rangdaar khali koon": "رنگدار خالی کون",
        "rib dai": "ریب ڈائی",
        "badar mounchi": "بدڑ مونچی",
        "foot mix": "فٹ مکس"
    }


 
   # ---------------- Column Headings ----------------
    headers = ["آئٹم کا نام", "وزن", "نرخ", "روپے", "Entry Type", "Add Item"]
    for col, text in enumerate(headers):
        tk.Label(
            bill_frame,
            text=text,
            font=("Segoe UI", 17,"bold"),
            bg=main_bg,
            fg="#333"
        ).grid(row=0, column=col, padx=5, pady=5, sticky="w")

    # ---------------- Entry Row ----------------
    item_var = tk.StringVar()
    item_entry = tk.Entry(
        bill_frame,
        font=("Segoe UI", 12),
        textvariable=item_var,
        width=15
    )
    item_entry.grid(row=1, column=0, padx=5, pady=5, sticky="W")

    weight_entry = tk.Entry(bill_frame, font=("Segoe UI", 12), width=8)
    weight_entry.grid(row=1, column=1, padx=5, pady=5)

    fee_entry = tk.Entry(bill_frame, font=("Segoe UI", 12), width=8)
    fee_entry.grid(row=1, column=2, padx=5, pady=5)

    total_var = tk.StringVar()
    total_entry = tk.Entry(bill_frame, font=("Segoe UI", 12), textvariable=total_var, state="readonly", width=10)
    total_entry.grid(row=1, column=3, padx=5, pady=5) 
    
    entry_type_var = tk.StringVar(value="Unpaid")
    entry_type_dropdown = tk.OptionMenu(bill_frame, entry_type_var, "Paid", "Unpaid")
    entry_type_dropdown.config(width=8)
    entry_type_dropdown.grid(row=1, column=4, padx=5, pady=5)


    # ---------------- Suggestion Listbox ----------------
    bold_font = tkFont.Font(family="Segoe UI", size=12, weight="bold")
    suggestion_box = tk.Listbox(bill_frame, height=3, width=15, font=bold_font)
    suggestion_box.grid(row=2, column=0, padx=5, pady=5, sticky="w")
    suggestion_box.lower()  # Start hidden



    # ---------------- Show/Hide Suggestion ----------------
    def show_suggestions(event=None):
        update_suggestions()
        suggestion_box.lift()

    def hide_suggestions(event=None):
        suggestion_box.lower()

    # ---------------- Auto Suggest Function ----------------
    def update_suggestions(*args):
        typed = item_var.get().strip().lower()
        suggestion_box.delete(0, tk.END)
        if typed == "":
            suggestion_box.lower()
            return
        matches = [item_map[key] for key in item_map if key.startswith(typed)]
        if matches:
            for m in matches:
                suggestion_box.insert(tk.END, m)
            suggestion_box.lift()
        else:
            suggestion_box.lower()

    def fill_from_suggestion(event):
        selection = suggestion_box.curselection()
        if selection:
            item_var.set(suggestion_box.get(selection[0]))
            suggestion_box.lower()

    # ---------------- Bindings ----------------
    item_entry.bind("<Button-1>", show_suggestions)
    item_entry.bind("<FocusOut>", hide_suggestions)
    item_var.trace_add("write", update_suggestions)
    suggestion_box.bind("<Double-Button-1>", fill_from_suggestion)

    # ---------------- Live Total Calculation ----------------
    def calculate_total(*args):
        try:
            weight = float(weight_entry.get()) if weight_entry.get() else 0
            fee = float(fee_entry.get()) if fee_entry.get() else 0
            total_var.set(str(weight * fee))  # quantity removed
        except:
            total_var.set("0")

    weight_entry.bind("<KeyRelease>", calculate_total)
    fee_entry.bind("<KeyRelease>", calculate_total)

    # ===================== NEW: SHOW BILL (Queue) AREA =====================
    # Container Frame for Show Bill
    show_frame = tk.Frame(bill_frame, bg=main_bg)
    # Place it under the input row + suggestion row
    show_frame.grid(row=3, column=0, columnspan=6, sticky="nsew", padx=5, pady=(10, 5))
    bill_frame.grid_rowconfigure(3, weight=1)
    bill_frame.grid_columnconfigure(0, weight=1)

    # Treeview + Scrollbar
    columns = ("آئٹم کا نام	", "وزن", "نرخ", "روپے", "EntryType")
    tree = ttk.Treeview(show_frame, columns=columns, show="headings", height=4)
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=120, anchor="center")

    scrollbar = ttk.Scrollbar(show_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)

    tree.grid(row=0, column=0, sticky="nsew")
    scrollbar.grid(row=0, column=1, sticky="ns")

    show_frame.grid_rowconfigure(0, weight=1)
    show_frame.grid_columnconfigure(0, weight=1)

    # ---------------- Footer Frame ----------------
    footer_frame = tk.Frame(bill_frame, bg=main_bg)
    footer_frame.grid(row=4, column=0, columnspan=6, sticky="es", padx=5, pady=(8, 5))
    footer_frame.grid_columnconfigure(0, weight=1)

    # ---------------- Grand Total ----------------
    grand_total_var = tk.StringVar(value="0.0")
    tk.Label(
        footer_frame,
        text="Grand Total:",
        font=("Segoe UI", 12, "bold"),
        bg=main_bg,
        fg="#333"
    ).grid(row=0, column=0, sticky="e", padx=(5,5))

    grand_total_label = tk.Label(
        footer_frame,
        textvariable=grand_total_var,
        font=("Segoe UI", 12, "bold"),
        bg=main_bg,
        fg="#111",
        width=12,
        anchor="w"
    )
    grand_total_label.grid(row=0, column=1, sticky="w", padx=(5,15))

    # ---------------- Paid Field ----------------
    tk.Label(
        footer_frame,
        text="وصول:",
        font=("Segoe UI", 12, "bold"),
        bg=main_bg,
        fg="#333"
    ).grid(row=0, column=2, sticky="w", padx=(5,5))

    paid_var = tk.StringVar(value="0.0")
    paid_entry = tk.Entry(
        footer_frame,
        font=("Segoe UI", 12, "bold"),
        textvariable=paid_var,
        width=10
    )
    paid_entry.grid(row=0, column=3, sticky="w", padx=(5,5))
    
    
    discount_label = tk.Label(
        footer_frame,
        text="discount",
        font=("Segoe UI", 12, "bold"),
        bg=main_bg,
        fg="#333"
    ).grid(row=0, column=5, sticky="w", padx=(5,5))
    
    discount_var = tk.StringVar()

    # --- Discount Entry ---
    discount_entry = tk.Entry(
        footer_frame, font=("Segoe UI", 12), width=10,
        textvariable=discount_var
    )
    discount_entry.grid(row=0, column=6, padx=8, sticky="w")

    # ---------------- Pending items store ----------------
    pending_items = []  # each item: dict(item, weight, fee_unit, total, entry_type)

    # ---------------- Refresh Tree + Grand Total (live minus Paid & Discount) ----------------
    def refresh_tree_and_totals():
        # Clear tree
        for row in tree.get_children():
            tree.delete(row)
        
        # Calculate total of all pending items
        total_sum = 0.0
        for it in pending_items:
            tree.insert("", tk.END, values=(
                it["item"], f'{it["weight"]}', f'{it["fee_unit"]}', f'{it["total"]}', it["entry_type"]
            ))
            total_sum += it["total"]
        
        # Get due balance
        try:
            due_amount = float(due_balance_var.get()) if due_balance_var.get() else 0.0
        except ValueError:
            due_amount = 0.0

        # Get discount amount
        try:
            discount_amount = float(discount_var.get()) if discount_var.get() else 0.0
        except ValueError:
            discount_amount = 0.0

        # Subtract discount from due balance
        due_after_discount = max(due_amount - discount_amount, 0.0)

        # Total including due after discount
        total_with_due = total_sum + due_after_discount

        # Get paid amount
        try:
            paid_amount = float(paid_var.get()) if paid_var.get() else 0.0
        except ValueError:
            paid_amount = 0.0

        # Remaining Grand Total = (Total + Due after discount) - Paid
        remaining_total = total_with_due - paid_amount
        if remaining_total < 0:
            remaining_total = 0.0  # Avoid negative total
        
        grand_total_var.set(f"{remaining_total:.2f}")


    # ---------------- Live Update Paid ----------------
    def update_grand_total_on_paid(*args):
        refresh_tree_and_totals()

    paid_var.trace_add("write", update_grand_total_on_paid)

    # ---------------- Live Update Discount ----------------
    def update_grand_total_on_discount(*args):
        refresh_tree_and_totals()

    discount_var.trace_add("write", update_grand_total_on_discount)


    # ---------------- Add Item ----------------
    def add_item_to_queue():
        try:
            item = item_var.get().strip()
            if not item:
                messagebox.showwarning("Missing", "Item required.")
                return
            weight = float(weight_entry.get()) if weight_entry.get() else 0.0
            fee_unit = float(fee_entry.get()) if fee_entry.get() else 0.0
            total = weight * fee_unit
            entry_type = entry_type_var.get()

            pending_items.append({
                "item": item,
                "weight": weight,
                "fee_unit": fee_unit,
                "total": total,
                "entry_type": entry_type
            })
            # Clear input row
            item_var.set("")
            weight_entry.delete(0, tk.END)
            fee_entry.delete(0, tk.END)
            total_var.set("")
            suggestion_box.lower()

            refresh_tree_and_totals()

        except Exception as e:
            messagebox.showerror("Error", f"Error adding item: {e}")

    # ---------------- Save All (to DB) + Print Bill ----------------
    import webbrowser
    import os
    from datetime import datetime
    def save_all_items():
        global g_paid_sum
        try:
            customer_name = customer_name_entry.get().strip()
            phone = phone_entry.get().strip()
            date_val = date_entry.get()
            description = description_entry.get("1.0", tk.END).strip()

            if not customer_name:
                messagebox.showwarning("Missing", "Customer name required.")
                return

            # Ensure customer exists
            cursor.execute("SELECT customer_id FROM customers WHERE customer_name = ?", (customer_name,))
            result = cursor.fetchone()
            if result:
                customer_id = result[0]
            else:
                cursor.execute(
                    "INSERT INTO customers (customer_name, phone_number, description) VALUES (?,?, ?)",
                    (customer_name, phone, description)
                )
                conn.commit()
                customer_id = cursor.lastrowid

            # ------------------ BILL ID + COUNTER LOGIC ------------------
            cursor.execute("""
                SELECT bill_id FROM bills 
                WHERE customer_id = ? AND entry_type = 'Paid'
                ORDER BY id DESC LIMIT 1
            """, (customer_id,))
            last_cleared = cursor.fetchone()

            if last_cleared and last_cleared[0]:
                parts = last_cleared[0].split('-')
                counter = int(parts[1]) + 1 if len(parts) == 2 else 1
            else:
                counter = 1

            bill_id = f"{customer_id}-{counter}"
            # -----------------------------------------------------------

            # Paid amount
            try:
                paid_amount = float(paid_var.get()) if paid_var.get() else 0.0
            except ValueError:
                paid_amount = 0.0

            items_to_save = []

            # -------- If pending_items is empty, handle only DUE entries ----------
            if not pending_items:
                cursor.execute("""
                    SELECT id, item, weight, fee_unit, amount
                    FROM bills
                    WHERE customer_id = ? AND entry_type = 'Due'
                    ORDER BY id
                """, (customer_id,))
                dues = cursor.fetchall()

                for due_id, item, weight, fee_unit, due_amt in dues:
                    if paid_amount > 0:
                        if paid_amount >= due_amt:
                            paid_here = due_amt
                            remaining_amt = 0.0
                            cursor.execute("UPDATE bills SET amount = 0, entry_type = 'Cleared' WHERE id = ?", (due_id,))
                            paid_amount -= due_amt
                        else:
                            paid_here = paid_amount
                            remaining_amt = round(due_amt - paid_amount, 2)
                            cursor.execute("UPDATE bills SET amount = ? WHERE id = ?", (remaining_amt, due_id))
                            paid_amount = 0.0
                    else:
                        paid_here = 0.0
                        remaining_amt = due_amt

                    conn.commit()

                    items_to_save.append({
                        "item": item,
                        "weight": weight,
                        "fee_unit": fee_unit,
                        "total": float(due_amt),
                        "paid": float(paid_here),
                        "remaining": float(remaining_amt)
                    })

                # ✅ Always update description
                new_description = description_entry.get("1.0", tk.END).strip()
                cursor.execute("UPDATE customers SET description = ? WHERE customer_id = ?", (new_description, customer_id))
                conn.commit()

            # -------- Case: pending_items present (normal save + possible due update) ----------
            else:
                for it in pending_items:
                    if isinstance(it, dict):
                        item_copy = dict(it)
                    else:
                        item_copy = {"item": str(it), "weight": 0, "fee_unit": 0, "total": float(it)}
                    items_to_save.append(item_copy)

                for it in items_to_save:
                    it_total = float(it.get("total", 0.0))
                    if paid_amount >= it_total:
                        it["paid"] = it_total
                        it["entry_type"] = "Unpaid"   
                        paid_amount -= it_total
                        it["remaining"] = 0.0
                    else:
                        it["paid"] = float(paid_amount)
                        it["entry_type"] = "Unpaid"  # ✅ partial paid
                        it["remaining"] = round(it_total - paid_amount, 2)
                        paid_amount = 0.0

                # Insert/Save each new item into bills with bill_id
                for it in items_to_save:
                    cursor.execute('''
                        INSERT INTO bills (bill_id, customer_id, date, item, weight, fee_unit, amount, entry_type)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (bill_id, customer_id, date_val, it["item"], it["weight"], it["fee_unit"], it["total"], it["entry_type"]))
                conn.commit()

                # Handle remaining unpaid amount as Due
                remaining_due = sum(it["remaining"] for it in items_to_save if it.get("entry_type") == "Unpaid")
                if remaining_due > 0:
                    cursor.execute("""
                        SELECT id FROM bills
                        WHERE customer_id = ? AND entry_type = 'Due'
                        LIMIT 1
                    """, (customer_id,))
                    existing_due = cursor.fetchone()
                    if existing_due:
                        cursor.execute("UPDATE bills SET amount = amount + ? WHERE id = ?", (remaining_due, existing_due[0]))
                    else:
                        cursor.execute('''
                            INSERT INTO bills (bill_id, customer_id, date, item, weight, fee_unit, amount, entry_type)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (bill_id, customer_id, date_val, 0, 0, 0, remaining_due, "Due"))
                    conn.commit()

            # ------------------- ✅ Discount Handling -------------------
            # ------------------- ✅ Discount Handling (Apply on both Due + Unpaid) -------------------
            try:
                discount_amount = float(discount_var.get()) if discount_var.get() else 0.0
            except ValueError:
                discount_amount = 0.0

            if discount_amount > 0:
                # -------- Step 1: Apply discount equally on ALL Due entries --------
                cursor.execute("""
                    SELECT id, amount FROM bills
                    WHERE customer_id = ? AND entry_type = 'Due'
                    ORDER BY id ASC
                """, (customer_id,))
                due_entries = cursor.fetchall()

                if due_entries:
                    n_due = len(due_entries)
                    per_due_discount = round(discount_amount / n_due, 2)

                    for due_id, due_amt in due_entries:
                        new_due = max(0, due_amt - per_due_discount)
                        cursor.execute("UPDATE bills SET amount = ? WHERE id = ?", (new_due, due_id))
                    conn.commit()

                # -------- Step 2: Apply discount equally on ALL Unpaid entries --------
                cursor.execute("""
                    SELECT id, amount FROM bills
                    WHERE customer_id = ? AND entry_type = 'Unpaid'
                    ORDER BY id ASC
                """, (customer_id,))
                unpaid_entries = cursor.fetchall()

                if unpaid_entries:
                    n_unpaid = len(unpaid_entries)
                    per_unpaid_discount = round(discount_amount / n_unpaid, 2)

                    for unpaid_id, unpaid_amt in unpaid_entries:
                        new_unpaid = max(0, unpaid_amt - per_unpaid_discount)
                        cursor.execute("UPDATE bills SET amount = ? WHERE id = ?", (new_unpaid, unpaid_id))
                    conn.commit()

                # -------- Step 3: Insert discount entry for record --------
                cursor.execute('''
                    INSERT INTO bills (bill_id, customer_id, date, item, weight, fee_unit, amount, entry_type)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (bill_id, customer_id, date_val, "Discount", 0, 0, float(discount_var.get()), "Discount"))
                conn.commit()

            # -------- Strict Guard: Only mark Unpaid -> Paid if Due == 0 ----------
            cursor.execute("""
                SELECT SUM(amount) FROM bills
                WHERE customer_id = ? AND entry_type = 'Due'
            """, (customer_id,))
            total_due = cursor.fetchone()[0] or 0.0

            if total_due == 0:
                cursor.execute("""
                    UPDATE bills
                    SET entry_type = 'Paid'
                    WHERE customer_id = ? AND entry_type = 'Unpaid'
                """, (customer_id,))
                conn.commit()

            # -------- Build Payment record ----------
            total_paid_sum = sum(float(i.get("paid", 0.0)) for i in items_to_save)
            print("DEBUG: total_paid_sum =", total_paid_sum)  # ✅ Debugging
            if total_paid_sum > 0:
                cursor.execute('''
                    INSERT INTO bills (bill_id,customer_id, date, item, weight, fee_unit, amount, entry_type)
                    VALUES (?,?, ?, ?, ?, ?, ?, ?)
                ''', (bill_id, customer_id, date_val, "Payment", 0, 0, total_paid_sum, "Payment"))
                conn.commit()

            # Clear queue & UI
            pending_items.clear()
            refresh_tree_and_totals()
            phone_entry.delete(0, tk.END)
            description_entry.delete("1.0", tk.END)
            messagebox.showinfo("Success", "All items saved and bill generated!")

        except Exception as e:
            messagebox.showerror("Error", f"Error saving items: {e}")


    # ---------------- Buttons ----------------
    add_btn = tk.Button(
        bill_frame, text="ADD ITEM", font=("Segoe UI", 12, "bold"),
        bg="#1e90ff", fg="white", activebackground="#1c86ee",
        command=add_item_to_queue
    )
    add_btn.grid(row=1, column=5, padx=5, pady=5)

    save_all_btn = tk.Button(
        footer_frame, text="Save All & Print", font=("Segoe UI", 12, "bold"),
        bg="#28a745", fg="white", activebackground="#218838",
        command=save_all_items
    )
    save_all_btn.grid(row=0, column=7, sticky="e", padx=8)

# -------------------- Original Billing Tab View --------------------
import tkinter as tk
from tkinter import ttk
import webbrowser




def attendance_tab_home():
    # Clear tab first
    for widget in attendance_tab.winfo_children():
        widget.destroy()

    # Create Bill Button (right aligned)
    create_bill_btn = tk.Button(attendance_tab, text="Create Bill",
                                font=("Segoe UI", 14, "bold"),
                                bg="#1e90ff", fg="white",
                                activebackground="#1c86ee",
                                activeforeground="white",
                                width=15, height=1,
                                command=create_bill_action)
    create_bill_btn.pack(pady=(40, 20), padx=20, anchor="e")

    # Heading
    billing_heading = tk.Label(attendance_tab, text="Bills Management",
                               font=("Segoe UI", 22, "bold"),
                               bg=main_bg, fg=main_fg, anchor="w")
    billing_heading.pack(fill="x", padx=20, pady=(50, 10))

    # Subheading
    billing_subheading = tk.Label(attendance_tab, text="Manage and track all your bills",
                                  font=("Segoe UI", 14),
                                  bg=main_bg, fg="#555555", anchor="w")
    billing_subheading.pack(fill="x", padx=20, pady=(0, 20))

    # ================= SEARCH & FILTER ROW =================

    # ================= SEARCH & FILTER ROW =================
    filter_frame = tk.Frame(attendance_tab, bg=main_bg)
    filter_frame.pack(fill="x", padx=20, pady=(20, 15))

    # --- Search Box ---
    search_label = tk.Label(filter_frame, text="Search:", font=("Segoe UI", 12),
                            bg=main_bg, fg=main_fg)
    search_label.pack(side="left", padx=(0, 5))

    search_var = tk.StringVar()
    search_entry = tk.Entry(filter_frame, textvariable=search_var,
                            font=("Segoe UI", 12), width=25)
    search_entry.pack(side="left", padx=(0, 20))

    # ---------------- Suggestion Listbox ----------------
    bold_font = tkFont.Font(family="Segoe UI", size=12, weight="bold")
    customer_suggestion_box = tk.Listbox(attendance_tab, height=3, width=25, font=bold_font)
    customer_suggestion_box.place_forget()  # hide initially

    # --- Agent Define (use your own config imports above) ---
    from agents import Agent, Runner
    from config import config

    my_agent = Agent(
        name="Name Suggestion Agent",
        instructions=(
            "Tum Roman Urdu me likhe gaye naam ko Urdu me convert karo "
            "aur uske 3-4 milte julte full name suggestions do. "
            "Sirf naam likho, aur har naam nayi line me ho."
        )
    )

    debounce_timer = None
    loading_job = None

    # ---------------- Loading Spinner ----------------
    def animate_loading():
        dots = ["Loading", "Loading.", "Loading..", "Loading..."]
        current = customer_suggestion_box.get(0) if customer_suggestion_box.size() > 0 else ""
        try:
            idx = dots.index(current)
        except ValueError:
            idx = 0
        next_text = dots[(idx + 1) % len(dots)]
        customer_suggestion_box.delete(0, tk.END)
        customer_suggestion_box.insert(tk.END, next_text)

        global loading_job
        loading_job = attendance_tab.after(400, animate_loading)

    # ---------------- Suggestion Placement ----------------
    def place_suggestion_box():
        attendance_tab.update_idletasks()
        x = search_entry.winfo_rootx() - attendance_tab.winfo_rootx()
        y = search_entry.winfo_rooty() - attendance_tab.winfo_rooty() + search_entry.winfo_height()
        customer_suggestion_box.place(x=x, y=y)
        customer_suggestion_box.lift()

    # ---------------- Fetch Suggestions (Agent call) ----------------
    def fetch_suggestions(query):
        global loading_job
        customer_suggestion_box.delete(0, tk.END)
        customer_suggestion_box.insert(tk.END, "Loading")
        place_suggestion_box()
        animate_loading()

        try:
            result = Runner.run_sync(my_agent, query, run_config=config)
            urdu_text = result.final_output.strip()

            # Stop spinner
            if loading_job:
                attendance_tab.after_cancel(loading_job)
                loading_job = None

            # Fill with suggestions
            customer_suggestion_box.delete(0, tk.END)
            for line in urdu_text.split("\n"):
                if line.strip():
                    customer_suggestion_box.insert(tk.END, line.strip())

            customer_suggestion_box.config(height=min(customer_suggestion_box.size(), 6))
            place_suggestion_box()

        except Exception as e:
            if loading_job:
                attendance_tab.after_cancel(loading_job)
                loading_job = None
            customer_suggestion_box.delete(0, tk.END)
            customer_suggestion_box.insert(tk.END, f"Error: {e}")
            place_suggestion_box()

    # ---------------- Debounce Search ----------------
    def update_customer_suggestions(event=None):
        global debounce_timer
        typed = search_var.get().strip()

        if not typed:
            customer_suggestion_box.place_forget()
            return

        if debounce_timer:
            attendance_tab.after_cancel(debounce_timer)

        debounce_timer = attendance_tab.after(500, lambda: fetch_suggestions(typed))

    # ---------------- Fill from Suggestion ----------------
    def fill_customer_from_suggestion(event):
        selection = customer_suggestion_box.curselection()
        if selection:
            choice = customer_suggestion_box.get(selection[0])
            if not choice.startswith("Loading") and not choice.startswith("Error"):
                search_entry.delete(0, tk.END)
                search_entry.insert(0, choice)
            customer_suggestion_box.place_forget()

    # ---------------- Bindings ----------------
    search_entry.bind("<KeyRelease>", update_customer_suggestions)
    customer_suggestion_box.bind("<ButtonRelease-1>", fill_customer_from_suggestion)
    customer_suggestion_box.bind("<Double-Button-1>", fill_customer_from_suggestion)

    # --- Date From ---
    from_label = tk.Label(filter_frame, text="From:", font=("Segoe UI", 12),
                        bg=main_bg, fg=main_fg)
    from_label.pack(side="left", padx=(0, 5))

    from_date = DateEntry(filter_frame, font=("Segoe UI", 12), width=12,
                        background="darkblue", foreground="white", borderwidth=2)
    from_date.pack(side="left", padx=(0, 20))

    # --- Date To ---
    to_label = tk.Label(filter_frame, text="To:", font=("Segoe UI", 12),
                        bg=main_bg, fg=main_fg)
    to_label.pack(side="left", padx=(0, 5))

    to_date = DateEntry(filter_frame, font=("Segoe UI", 12), width=12,
                        background="darkblue", foreground="white", borderwidth=2)
    to_date.pack(side="left", padx=(0, 20))

    # --- Filter Button ---
    def apply_filter():
        for widget in bills_tree.get_children():
            bills_tree.delete(widget)

        query = """
            SELECT 
                b.bill_id, 
                c.customer_name, 
                b.date,
                SUM(CASE WHEN b.entry_type='Paid' OR b.entry_type='Unpaid' THEN b.amount ELSE 0 END) AS total_amount,
                SUM(CASE WHEN b.entry_type='Paid' THEN b.amount ELSE 0 END) AS paid_amount,
                SUM(CASE WHEN b.entry_type='Due' THEN b.amount ELSE 0 END) AS remaining_amount
            FROM bills b
            JOIN customers c ON b.customer_id = c.customer_id
            WHERE 1=1
        """

        params = []

        # --- Search by name / phone / bill_id ---
        search_text = search_var.get().strip()
        if search_text:
            query += " AND (c.customer_name LIKE ? OR c.phone_number LIKE ? OR b.bill_id LIKE ?)"
            like = f"%{search_text}%"
            params.extend([like, like, like])

        # --- Date filter (Windows format: M/D/YY) ---
        from_val = from_date.get_date().strftime("%#m/%#d/%y")
        to_val   = to_date.get_date().strftime("%#m/%#d/%y")
        if from_val and to_val:
            query += " AND b.date BETWEEN ? AND ?"
            params.extend([from_val, to_val])

        query += " GROUP BY b.bill_id, c.customer_name, b.date ORDER BY b.bill_id DESC"

        cursor.execute(query, params)
        filtered_bills = cursor.fetchall()

        for idx, bill in enumerate(filtered_bills):
            tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
            bills_tree.insert("", "end", values=bill, tags=(tag,))

    filter_btn = tk.Button(filter_frame, text="Apply Filter",
                        font=("Segoe UI", 12, "bold"),
                        bg="#1e90ff", fg="white",
                        activebackground="#1c86ee", activeforeground="white",
                        command=apply_filter)
    filter_btn.pack(side="left", padx=(10, 0))
  

        # Treeview for all bill
    # Assume `attendance_tab`, `cursor`, `print_bill`, main_bg, main_fg are already defined in your GUI

    # --- Treeview styling ---
    style = ttk.Style()
    style.theme_use("default")

    # Style for rows
    style.configure("Custom.Treeview",
                    background="#f9f9f9",
                    foreground="#333333",
                    rowheight=35,
                    fieldbackground="#f9f9f9",
                    font=("Segoe UI", 12))

    # Style for headers
    style.configure("Custom.Treeview.Heading",
                    background="#1e90ff",
                    foreground="white",
                    font=("Segoe UI", 14, "bold"))

    # Hover & selected row colors
    style.map("Custom.Treeview",
            background=[('selected', '#87cefa')],
            foreground=[('selected', 'black')])

    # --- Columns ---
    columns = ("Bill ID", "Customer", "Date", "Total", "Paid")
    bills_tree = ttk.Treeview(attendance_tab, columns=columns, show="headings", height=15, style="Custom.Treeview")

    for col in columns:
        bills_tree.heading(col, text=col)
        bills_tree.column(col, anchor="center")

    bills_tree.pack(fill="both", expand=True, padx=20, pady=20)

    # --- Fetch all bills summary ---
    cursor.execute("""
        SELECT 
            b.bill_id, 
            c.customer_name, 
            b.date,
            SUM(CASE WHEN b.entry_type IN ('Paid', 'Unpaid') THEN b.amount ELSE 0 END) AS total_amount,
            CASE 
                WHEN SUM(CASE WHEN b.entry_type='Paid' THEN 1 ELSE 0 END) > 0 THEN
                    SUM(CASE WHEN b.entry_type='Paid' THEN b.amount ELSE 0 END)
                ELSE
                    SUM(CASE WHEN b.entry_type='Payment' THEN b.amount ELSE 0 END)
            END AS paid_amount
        FROM bills b
        JOIN customers c ON b.customer_id = c.customer_id
        GROUP BY b.bill_id, c.customer_name
        ORDER BY b.bill_id DESC
        """)
    bills = cursor.fetchall()

    # --- Insert into Treeview with alternating row colors ---
    for idx, bill in enumerate(bills):
        tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
        bills_tree.insert("", "end", values=bill, tags=(tag,))

    # Row colors for zebra-striping
    bills_tree.tag_configure('evenrow', background="#f9f9f9")
    bills_tree.tag_configure('oddrow', background="#e6f2ff")

    # --- Bind double-click to print ---
    def on_row_click(event):
        selected_item = bills_tree.selection()
        if selected_item:
            bill_id = bills_tree.item(selected_item[0])['values'][0]
            print_bill(bill_id)

    bills_tree.bind("<Double-1>", on_row_click)

    # --- Hover effect ---
    def on_motion(event):
        region = bills_tree.identify("region", event.x, event.y)
        if region == "cell":
            row_id = bills_tree.identify_row(event.y)
            # Reset all rows
            for r in bills_tree.get_children():
                bills_tree.item(r, tags=('evenrow' if bills_tree.index(r)%2==0 else 'oddrow',))
            # Highlight hovered row
            if row_id:
                bills_tree.item(row_id, tags=('hover',))
                bills_tree.tag_configure('hover', background="#d1f0ff")

    def on_leave(event):
        for r in bills_tree.get_children():
            bills_tree.item(r, tags=('evenrow' if bills_tree.index(r)%2==0 else 'oddrow',))

    bills_tree.bind("<Motion>", on_motion)
    bills_tree.bind("<Leave>", on_leave)


    def print_bill(bill_id):
        global g_paid_sum

        # Fetch customer info
        cursor.execute("""
            SELECT b.customer_id, b.date, c.customer_name, c.phone_number,c.description
            FROM bills b
            JOIN customers c ON b.customer_id = c.customer_id
            WHERE b.bill_id = ?
        """, (bill_id,))
        result = cursor.fetchone()
        if not result:
            return

        customer_id, bill_date, customer_name, phone,description = result

        # Fetch all items for this bill
        cursor.execute("""
            SELECT item, weight, fee_unit, amount, entry_type
            FROM bills
            WHERE bill_id = ?
        """, (bill_id,))
        items = cursor.fetchall()

        # Rows for HTML table with Status column
        rows_html = "\n".join([f"""
            <tr>
                <td>{i[0]}</td>
                <td>{i[1]}</td>
                <td>{i[2]}</td>
                <td>{i[3]:.2f}</td>
                
            </tr>
        """ for i in items if i[4] not in ("Due", "Payment","Discount")])

        total_sum = sum(i[3] for i in items if i[4] in ("Paid", "Unpaid"))

        # --- Adjusted g_paid_sum calculation ---
        paid_entries = [float(i[3]) for i in items if i[4] == "Paid"]
        payment_entries = [float(i[3]) for i in items if i[4] == "Payment"]

        if paid_entries:
            g_paid_sum = sum(paid_entries)  # Paid entries ka sum
        else:
            g_paid_sum = sum(payment_entries) if payment_entries else 0.0  # Payment ka total sum

        # Remaining due
        remaining =      sum(i[3] for i in items if i[4] == "Due")
        total_discount = sum(i[3] for i in items if i[4]== "Discount")
        discount_html = f"<div>Discount: {total_discount:.2f}</div>" if total_discount > 0 else ""
        # HTML content with CSS/design
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8"/>
<title>Bill - {customer_name}</title>
<style>
body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 20px; background: #f4f6f8; color: #333; }}
.card {{
    display: flex;
    flex-direction: column;
    max-width: 950px;
    margin: 24px auto;
    background: #fff;
    border-radius: 15px;
    overflow: hidden;
    box-shadow: 0 8px 30px rgba(0,0,0,0.15);
}}
.content {{ flex-grow: 1; }}
.header {{ background: #e0e0e0; color: #000; text-align: center; padding: 35px 35px 10px 35px; position: relative; }}
.header h1 {{ font-size: 35px; margin: 0; letter-spacing: 2px; }}
.header h2 {{ font-size: 20px; margin: 6px 0 20px 0; font-weight: 500; opacity: 0.9; }}
.owner-boxes {{ position: absolute; top: 25px; left: 35px; right: 35px; display: flex; justify-content: space-between; }}
.owner-column {{ display: flex; flex-direction: column; gap: 0px; }}
.owner-card {{ background: #f9f9f9; border: 1px solid #000; padding: 6px 8px; border-radius: 8px; font-size: 12px; text-align: center; min-width: 110px; }}
.subheading {{ background: #f5f5f5; padding: 16px; text-align: center; font-size: 16px; font-weight: bold; color: #000; border-bottom: 2px solid #000; }}
.bill-info {{ padding: 16px; font-size: 14px; background: #f5f5f5; border-left: 4px solid #000; border-radius: 6px; display: flex; justify-content: space-between; flex-wrap: wrap; }}
table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
th, td {{ border: 1px solid #000; padding: 10px 10px; text-align: center; font-size: 12px; }}
th {{ background: #e0e0e0; font-weight: bold; }}
td {{ background: #fff; }}
tr:hover td {{ background: #f1f1f1; }}
.totals {{ display: flex; flex-direction: column; align-items: flex-end; margin-top: 20px; padding: 0 16px; }}
.totals div {{ margin-top: 6px; background: #f5f5f5; display: inline-block; padding: 8px 12px; border-radius: 6px; border: 1px solid #000; font-weight: bold; }}
.actions {{ margin-top: 20px; padding: 0 18px 18px; }}
.btn {{ padding: 12px 22px; border: none; background: #000; color: white; cursor: pointer; border-radius: 10px; font-weight: bold; transition: all 0.2s; }}
.btn:hover {{ background: #333; }}
.customer-name {{ font-size: 16px; }}
.footer {{ text-align: center; margin-top: 20px; font-size: 14px; color: gray; }}
@media print {{ 
    body {{ background: white !important;
    -webkit-print-color-adjust: exact; }} 
    .actions {{ display: none; }} 
    th, td {{ border: 1px solid #000 !important; }}
    .footer {{ color: black; }}
    .header {{
    background: #e0e0e0 !important;
    color: #000 !important;
    padding: 20px 15px 5px 15px !important; }} 
    }}
</style>
</head>
<body>
<div class="card">
    <div class="content">
        <div class="header">
            <div class="owner-boxes">
                <div class="owner-column">
                    <div class="owner-card">اصغر علی گجر<br/>0300-4924455</div>
                    <div class="owner-card">عمر اصغر گجر<br/>0301-4657736</div>
                </div>
                <div class="owner-column">
                    <div class="owner-card">عادل اصغر گجر<br/>0332-4328210</div>
                    <div class="owner-card">عامر اصغر گجر<br/>0303-4161739</div>
                </div>
            </div>
            <h1>بسم اللہ ہوزری</h1>
            <h2>Bismillah Hosiery</h2>
        </div>
        <div class="subheading">
            ڈیلر آل ہوزری ویسٹ کٹ پیس، پولیسٹر، فیبرک، یارن، تھریڈ اینڈ کالرز گارمنٹس وغیرہ
        </div>
        <div class="bill-info">
            <div><strong>Bill No:</strong> {bill_id}</div>
            <div><strong>تاریخ:</strong> {bill_date}</div>
            <div><strong> نام:</strong> <span class="customer-name">{customer_name}</span></div>
            <div><strong>Phone:</strong> {phone}</div>
        </div>
        <table>
        <thead>
            <tr>
                <th>آئٹم کا نام</th>
                <th>وزن</th>
                <th>نرخ</th>
                <th>کل</th>
                
            </tr>
        </thead>
        <tbody>
            {rows_html}
        </tbody>
        </table>
        <div class="description" style="text-align: center; margin: 10px 0; font-weight: bold;">
            <div>تفصیل:</div>
            <div style="font-weight: normal; margin-top: 5px;">{description}</div>
        </div>
        <div class="totals">
            <div>کل رقم: {total_sum:.2f}</div>
            {discount_html}
            <div>وصول: {g_paid_sum:.2f}</div>
            <div>باقی: {remaining:.2f}</div>
        </div>
        <div class="actions">
            <button class="btn" onclick="window.print()">Print</button>
        </div>
    </div> <!-- content ends -->

    <!-- Footer inside card but at bottom -->
    <!--
        <div class="footer">
            <div>Powered by Zohan Tech Solutions</div>
            <div>zohaib92shah@gmail.com</div>
        </div>
    -->
    
</div>
</body>
</html>
"""
        # Write HTML and open in browser
        with open("temp_bill.html", "w", encoding="utf-8") as f:
            f.write(html_content)
        webbrowser.open("temp_bill.html")
    
# -------------------- Initialize Billing Tab --------------------
attendance_tab_home()

def show_frame(f):
    f.tkraise()

#------------------show dashbord----------
import datetime
from tkcalendar import DateEntry
import platform
import tkinter as tk
from tkinter import ttk
import datetime
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
def member_tab_home(show_dashboard=True):
    # Clear tab first
    for widget in member_tab.winfo_children():
        widget.destroy()

    # Agar dashboard dikhana hai
    if show_dashboard:
        # ----- HEADER -----
        header_frame = tk.Frame(member_tab, bg="#4181C8", height=120)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)

        header_label = tk.Label(header_frame, text="Main Dashboard", font=("Segoe UI", 30, "bold"),
                                bg="#4181C8", fg="#ffffff")
        header_label.pack(side="left", padx=30, pady=30)

        subheader_label = tk.Label(header_frame, text="Welcome! To Hamid",
                                   font=("Segoe UI", 14), bg="#4181C8", fg="#dcdcdc")
        subheader_label.pack(side="left", padx=30, pady=45)

        # ----- OPTION BUTTON -----
        view_bills_btn = tk.Button(member_tab, text="📑 All Bills View", font=("Segoe UI", 14, "bold"),
                                   bg="#ffffff", fg="#4181C8", relief="flat", padx=20, pady=10,
                                   cursor="hand2", command=lambda: member_tab_home(show_dashboard=False))
        view_bills_btn.pack(pady=40)

        bill_count_frame = tk.Frame(member_tab, bg="#f0f2f5")
        bill_count_frame.pack(fill="x", padx=30, pady=(0,10))

        # Platform-specific date format
        if platform.system() == "Windows":
            date_format = "%#m/%#d/%y"
        else:
            date_format = "%-m/%-d/%y"

        today_date = datetime.datetime.now().strftime(date_format)

        # Today bills count
        cursor.execute("SELECT COUNT(DISTINCT bill_id) FROM bills WHERE date=?", (today_date,))
        today_bill_count = cursor.fetchone()[0]

        # Total bills count
        cursor.execute("SELECT COUNT(DISTINCT bill_id) FROM bills")
        total_bill_count = cursor.fetchone()[0]

        tk.Label(
            bill_count_frame, 
            text=f"Today Bills: {today_bill_count}", 
            font=("Segoe UI", 14, "bold"), 
            bg="#f0f2f5", fg="#1e90ff"
        ).pack(side="left", padx=10, pady=10)

        tk.Label(
            bill_count_frame, 
            text=f"Total Bills: {total_bill_count}", 
            font=("Segoe UI", 14, "bold"), 
            bg="#f0f2f5", fg="#28a745"
        ).pack(side="left", padx=30, pady=10)

        # ----- SALES GRAPH (7-day weekly) -----
        today = datetime.datetime.now()
        seven_days_ago = today - datetime.timedelta(days=6)
        start_date = seven_days_ago.strftime("%#m/%#d/%y") if platform.system() == "Windows" else seven_days_ago.strftime("%-m/%-d/%y")
        end_date = today.strftime("%#m/%#d/%y") if platform.system() == "Windows" else today.strftime("%-m/%-d/%y")

        cursor.execute("""
            SELECT date, SUM(amount) as total_sale
            FROM bills
            WHERE date BETWEEN ? AND ? AND entry_type IN ('Paid','Unpaid')
            GROUP BY date
            ORDER BY date ASC
        """, (start_date, end_date))
        sales_data = cursor.fetchall()

        # Ensure all 7 days represented
        dates = []
        sales = []
        for i in range(7):
            day = seven_days_ago + datetime.timedelta(days=i)
            day_str = day.strftime("%#m/%#d/%y") if platform.system() == "Windows" else day.strftime("%-m/%-d/%y")
            dates.append(day_str)
            sale = next((row[1] for row in sales_data if row[0]==day_str), 0)
            sales.append(sale)

        # --- Figure setup ---
        fig = Figure(figsize=(6, 2.5), dpi=100)  # Wider figure
        ax = fig.add_subplot(111)

        max_sale = max(sales) if sales else 1  # Avoid division by zero

        # Define 7 attractive colors for 7 days
        color_palette = ["#FFD700", "#FFA500", "#FF4500", "#1E90FF", "#32CD32", "#FF69B4", "#8A2BE2"]
        bars = ax.bar(dates, sales, color=color_palette, edgecolor="#444444", linewidth=1.2, width=0.4)  # thinner bars

        ax.set_title("Weekly Sales ", fontsize=14, fontweight="bold")
        ax.set_xlabel("Date")
        ax.set_ylabel("Total Sale")
        ax.set_ylim(0, max(1, max_sale * 1.2 if max_sale > 0 else 1))

        ax.tick_params(axis='x', rotation=45)

        # Display sale values on bars and highlight highest
        for bar, sale, date in zip(bars, sales, dates):
            height = bar.get_height()
            # Show date on highest sale bar
            ax.text(
                bar.get_x() + bar.get_width()/2., 
                height + max_sale*0.02, 
                f'{date if sale==max_sale else ""}', 
                ha='center', va='bottom', fontsize=10, fontweight='bold', color="#000000"
            )
            # Show sale value on bar
            ax.text(
                bar.get_x() + bar.get_width()/2., 
                height/2, 
                f'{sale:.0f}', 
                ha='center', va='center', fontsize=10, color="#ffffff" if sale<max_sale*0.4 else "#000000"
            )

        # Embed in Tkinter
        canvas = FigureCanvasTkAgg(fig, master=member_tab)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", padx=30, pady=(0,20))
    else:
        # ----- HEADER -----
        header_frame = tk.Frame(member_tab, bg="#4181C8", height=120)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)

        header_label = tk.Label(header_frame, text="Bills Dashboard", font=("Segoe UI", 30, "bold"),
                                bg="#4181C8", fg="#ffffff")
        header_label.pack(side="left", padx=30, pady=30)

        subheader_label = tk.Label(header_frame, text="Manage, track, and view all bills in style",
                                   font=("Segoe UI", 14), bg="#4181C8", fg="#dcdcdc")
        subheader_label.pack(side="left", padx=30, pady=45)

        # ----- BACK BUTTON -----
        back_btn = tk.Button(header_frame, text="← Back", font=("Segoe UI", 12, "bold"),
                             bg="#ffffff", fg="#1e3c72", relief="flat", padx=12, pady=6,
                             cursor="hand2", command=lambda: member_tab_home(show_dashboard=True))
        back_btn.pack(side="right", padx=30, pady=35)
        back_btn.bind("<Enter>", lambda e: back_btn.config(bg="#f0f0f0"))
        back_btn.bind("<Leave>", lambda e: back_btn.config(bg="#ffffff"))
        

        # ----- FILTER CARD -----
        filter_card = tk.Frame(member_tab, bg="#f5f5f5", bd=0)
        filter_card.pack(fill="x", padx=30, pady=20)
        filter_card.config(highlightbackground="#ccc", highlightthickness=1)

        # Status filter
        tk.Label(filter_card, text="Status:", font=("Segoe UI", 12, "bold"), bg="#f5f5f5").pack(side="left", padx=10, pady=10)
        status_var = tk.StringVar(value="Paid")
        status_menu = ttk.Combobox(filter_card, textvariable=status_var, state="readonly", values=["Paid", "All","Unpaid"])
        status_menu.pack(side="left", padx=10, pady=10)

        # Date filter
        # From date
        tk.Label(filter_card, text="From:", font=("Segoe UI", 12), bg="#f5f5f5").pack(side="left", padx=(20,5))
        from_date = DateEntry(filter_card, date_pattern='m/d/yy')
        from_date.pack(side="left", padx=5, pady=10)

        # To date
        tk.Label(filter_card, text="To:", font=("Segoe UI", 12), bg="#f5f5f5").pack(side="left", padx=(20,5))
        to_date = DateEntry(filter_card, date_pattern='m/d/yy')
        to_date.pack(side="left", padx=5, pady=10)
        # Quick filter
        tk.Label(filter_card, text="Quick Filter:", font=("Segoe UI", 12, "bold"), bg="#f5f5f5").pack(side="left", padx=(20,5))
        quick_var = tk.StringVar(value="Today")
        quick_filter = ttk.Combobox(filter_card, textvariable=quick_var, state="readonly", values=["Today", "This Week", "This Month", "This Year"])
        quick_filter.pack(side="left", padx=5, pady=10)

        # ----- MINI CARD STYLE BILLS VIEW -----
        bills_canvas = tk.Canvas(member_tab, bg="#f0f2f5", height=400)
        bills_scroll = tk.Scrollbar(member_tab, orient="vertical", command=bills_canvas.yview)
        bills_scroll.pack(side="right", fill="y")
        bills_canvas.pack(fill="both", expand=True, padx=30, pady=(0,20))
        bills_canvas.configure(yscrollcommand=bills_scroll.set)
        bills_frame = tk.Frame(bills_canvas, bg="#f0f2f5")
        bills_canvas.create_window((0,0), window=bills_frame, anchor="nw")

        # Update scrollregion dynamically
        def update_scroll(event):
            bills_canvas.configure(scrollregion=bills_canvas.bbox("all"))
        bills_frame.bind("<Configure>", update_scroll)

        # ----- GRAND TOTAL LABEL -----
        total_lbl = tk.Label(member_tab, text="Grand Total: 0.00", font=("Segoe UI", 16, "bold"),
                             bg="#f0f2f5", fg="green")
        total_lbl.pack(fill="x", padx=30, pady=(5,20))



        def update_date_range(*args):
            today = datetime.date.today()
            quick = quick_var.get()

            if quick == "Today":
                from_date.set_date(today)
                to_date.set_date(today)
            elif quick == "This Week":
                start = today - datetime.timedelta(days=today.weekday())  # Monday
                end = start + datetime.timedelta(days=6)  # Sunday
                from_date.set_date(start)
                to_date.set_date(end)
            elif quick == "This Month":
                start = today.replace(day=1)
                if today.month == 12:
                    end = today.replace(day=31)
                else:
                    end = today.replace(month=today.month+1, day=1) - datetime.timedelta(days=1)
                from_date.set_date(start)
                to_date.set_date(end)
            elif quick == "This Year":
                start = today.replace(month=1, day=1)
                end = today.replace(month=12, day=31)
                from_date.set_date(start)
                to_date.set_date(end)




        # ----- LOAD BILLS FUNCTION -----
        def load_bills():
            for widget in bills_frame.winfo_children():
                widget.destroy()

            status = status_var.get()
            from_val = from_date.get().strip()
            to_val = to_date.get().strip()

            params = []

            # Base query for bills
            query = """
            SELECT 
                b.bill_id,
                c.customer_name,
                b.date,
                b.entry_type,
                SUM(b.amount) AS total_amount,
                (SELECT IFNULL(SUM(amount),0) 
                FROM bills 
                WHERE bill_id = b.bill_id AND entry_type='Payment') AS paid_amount
            FROM bills b
            JOIN customers c ON b.customer_id = c.customer_id
            WHERE 1=1
            """

            # Status filter
            if status == "Paid":
                query += " AND b.entry_type='Paid'"
            elif status == "Unpaid":
                query += " AND b.entry_type='Unpaid'"
            elif status == "All":
                query += " AND b.entry_type IN ('Paid','Unpaid')"

            # Date filter
            if from_val and to_val:
                query += " AND b.date BETWEEN ? AND ?"
                params.extend([from_val, to_val])

            query += " GROUP BY b.bill_id, c.customer_name, b.date ORDER BY b.bill_id DESC"

            cursor.execute(query, params)
            bills = cursor.fetchall()

            grand_total = 0
            total_sale = 0   # sirf Paid
            total_remaining = 0  # sirf Unpaid remaining

            for bill in bills:
                entry_type = bill[3]          # Paid / Unpaid
                total_value = bill[4]         # Total of this type
                paid_value = bill[5]          # Already paid amount (for Unpaid)
                remaining = total_value - paid_value if entry_type == "Unpaid" else 0

                # Grand Total = Paid + Unpaid
                grand_total += total_value

                # Total Sale = sirf Paid amount
                total_sale += paid_value

                # Total Remaining = sirf Unpaid remaining
                total_remaining += remaining

                # Display cards
                card = tk.Frame(bills_frame, bg="#ffffff", bd=0, relief="raised")
                card.pack(fill="x", pady=8, padx=5)

                tk.Label(card, text=f"Bill ID: {bill[0]}", font=("Segoe UI", 12, "bold"), bg="#ffffff").pack(side="left", padx=15)
                tk.Label(card, text=f"Customer: {bill[1]}", font=("Segoe UI", 12), bg="#ffffff").pack(side="left", padx=15)
                tk.Label(card, text=f"Date: {bill[2]}", font=("Segoe UI", 12), bg="#ffffff").pack(side="left", padx=15)
                tk.Label(card, text=f"Type: {entry_type}", font=("Segoe UI", 12), bg="#ffffff").pack(side="left", padx=15)

                tk.Label(card, text=f"Total: {total_value:.2f}", font=("Segoe UI", 12), bg="#ffffff").pack(side="left", padx=15)

                if entry_type == "Unpaid":
                    tk.Label(card, text=f"Paid: {paid_value:.2f}", font=("Segoe UI", 12), bg="#ffffff", fg="#28a745").pack(side="left", padx=15)
                    tk.Label(card, text=f"Remaining: {remaining:.2f}", font=("Segoe UI", 12), bg="#ffffff", fg="#dc3545").pack(side="left", padx=15)
                else:
                    tk.Label(card, text=f"Remaining: 0.00", font=("Segoe UI", 12), bg="#ffffff", fg="#dc3545").pack(side="left", padx=15)

            # Update labels
            total_lbl.config(text=f"Grand Total: {grand_total:.2f}    |    Total Sale (Paid): {total_sale:.2f}    |    Total Due: {total_remaining:.2f}")








        # Bind filters
        status_menu.bind("<<ComboboxSelected>>", lambda e: load_bills())
        from_date.bind("<<DateEntrySelected>>", lambda e: load_bills())
        to_date.bind("<<DateEntrySelected>>", lambda e: load_bills())
        quick_filter.bind("<<ComboboxSelected>>", lambda e: load_bills())
        quick_filter.bind("<<ComboboxSelected>>", update_date_range)

        load_bills()


# -------------------- Initialize Billing Tab --------------------
member_tab_home()





# -------------------- Sidebar Button Helper --------------------
def add_sidebar_button(text, command=None, tab=None):
    btn = tk.Button(menu_frame, text=text, font=("Segoe UI", 12),
                    bg=sidebar_bg, fg=sidebar_fg, bd=0, relief="flat",
                    activebackground=sidebar_hover, activeforeground=sidebar_fg,
                    height=2,anchor="w", justify="left")
    btn.pack(fill="x", padx=20, pady=5)
    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)
    
    if command:  # agar koi function diya hai
        btn.config(command=command)
    elif tab:  # agar koi tab diya hai
        btn.config(command=lambda: show_frame(tab))
    return btn


def open_main():
    
    subprocess.Popen(["python", "main.py"])
    
    sys.exit()



import threading
import time

def show_loading_and_open_main(root):
    # Hide main.py window
    root.withdraw()

    # Loading window
    loading_win = tk.Toplevel()
    loading_win.title(" Loading...")
    loading_win.configure(bg="#1e1e2f")
    loading_win.resizable(False, False)

    # --- Keep always on top ---
    loading_win.attributes("-topmost", True)

    # Window size
    win_width = 500
    win_height = 200

    # Screen size
    screen_width = loading_win.winfo_screenwidth()
    screen_height = loading_win.winfo_screenheight()

    # Center position
    x = int((screen_width / 2) - (win_width / 2))
    y = int((screen_height / 2) - (win_height / 2))

    # Apply geometry
    loading_win.geometry(f"{win_width}x{win_height}+{x}+{y}")

    # Heading
    label = tk.Label(
        loading_win,
        text=" Initializing ...",
        font=("Segoe UI", 16, "bold"),
        bg="#1e1e2f",
        fg="#00ffcc"
    )
    label.pack(pady=20)

    # Progress bar style
    style = ttk.Style()
    style.theme_use("clam")
    style.configure(
        "TProgressbar",
        thickness=25,
        troughcolor="#2b2b40",
        background="#00ffcc",
        bordercolor="#1e1e2f",
        lightcolor="#00ffaa",
        darkcolor="#008866"
    )

    progress = ttk.Progressbar(
        loading_win,
        style="TProgressbar",
        length=400,
        mode="determinate",
        maximum=100
    )
    progress.pack(pady=20)

    # Status text
    status = tk.Label(
        loading_win,
        text="Preparing system...",
        font=("Segoe UI", 12),
        bg="#1e1e2f",
        fg="white"
    )
    status.pack(pady=10)

    def run_loading():
        # 1. Turant main.py open karo
        subprocess.Popen(["main.exe"], cwd=os.getcwd())

        # 2. Progress bar dheere-dheere fill karo (5 sec total)
        for i in range(101):
            progress["value"] = i

            if i < 30:
                status.config(text="🔍 Checking modules...")
            elif i < 60:
                status.config(text="⚡ Loading resources...")
            elif i < 90:
                status.config(text="🛰️ Connecting To dashboard...")
            else:
                status.config(text="✅ Dashboard Ready to Use ...")

            loading_win.update_idletasks()
            time.sleep(0.04)  # 100 × 0.05 = 5 sec

        # 3. Close loading screen
        loading_win.destroy()

        # 4. Close root window
        root.destroy()

    threading.Thread(target=run_loading, daemon=True).start()







# -------------------- Sidebar Buttons --------------------
dashboard_btn = add_sidebar_button("💾 Dashboard", tab=member_tab)
billing_btn = add_sidebar_button("📝 Billing", tab=attendance_tab)
#customer_btn = add_sidebar_button("👥 Customer", tab=info_tab)
#settings_btn = add_sidebar_button("⚙️ Settings", command=open_settings)
logout_btn = add_sidebar_button("Back",command=lambda: show_loading_and_open_main(root))
#exit_btn = add_sidebar_button("❌ Exit", command=root.quit)


# -------------------- Welcome Label --------------------
tk.Label(content_frame, text="Welcome to Billing System",
         font=("Segoe UI", 20, "bold"),
         bg=main_bg, fg=main_fg).place(relx=0.5, rely=0.05, anchor="n")

# -------------------- Show Default Tab --------------------
show_frame(member_tab)

# -------------------- Start --------------------
root.mainloop()
