import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk, ImageDraw
import sqlite3
import subprocess
import os
import threading
import time
import sys

# --- DB Setup ---
conn = sqlite3.connect("bill.db")
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
    role TEXT
)''')
cursor.execute('''
INSERT OR IGNORE INTO users (username, password, role)
VALUES ('hamid2041', 'Bh2041', 'admin')
''')
conn.commit()

# --- Function to create rounded widget background ---
def create_rounded_image(width, height, radius, color):
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle((0, 0, width, height), radius=radius, fill=color)
    return ImageTk.PhotoImage(img)

# --- Toggle Password Visibility ---
def toggle_password():
    password_entry.config(show="" if show_pass.get() else "*")

# --- Loading Screen ---
def show_loading_and_open_main(root):
    root.withdraw()  # Hide login window

    # Loading window
    loading_win = tk.Toplevel()
    loading_win.title("Loading...")
    loading_win.configure(bg="#1e1e2f")
    loading_win.resizable(False, False)

    # --- Keep always on top ---
    loading_win.attributes("-topmost", True)

    # Window size
    win_width = 500
    win_height = 200
    screen_width = loading_win.winfo_screenwidth()
    screen_height = loading_win.winfo_screenheight()
    x = int((screen_width / 2) - (win_width / 2))
    y = int((screen_height / 2) - (win_height / 2))
    loading_win.geometry(f"{win_width}x{win_height}+{x}+{y}")

    # Heading
    tk.Label(
        loading_win,
        text="LOGIN TO BISMILLAH HOSIERY ...",
        font=("Segoe UI", 16, "bold"),
        bg="#1e1e2f",
        fg="#00ffcc"
    ).pack(pady=20)

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

    def run_progress():
        # --- Open main.py turant ---
        subprocess.Popen(["main.exe"], cwd=os.getcwd())

        # --- Progress bar 0 → 100 fill (~5 sec) ---
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
            time.sleep(0.04)  # 100 × 0.05 = ~5 sec total

        # --- Close loading window ---
        loading_win.destroy()
        root.destroy()

    threading.Thread(target=run_progress, daemon=True).start()


# --- Login Function ---
def login():
    username = username_var.get().strip()
    password = password_var.get().strip()

    if not username or not password:
        messagebox.showerror("Login Failed", "Both fields are required.")
        return

    cursor.execute("SELECT id, role FROM users WHERE username=? AND password=?", (username, password))
    row = cursor.fetchone()

    if row:
        user_id, role = row
        with open("session.txt", "w") as f:
            f.write(f"{username},{role}")
        messagebox.showinfo("Login Successful", f"Welcome {username} Role: {role}")
        show_loading_and_open_main(root)
    else:
        messagebox.showerror("Login Failed", "Invalid Username or Password.")

# --- GUI Setup ---
root = tk.Tk()
root.title("BISMILLAH HOSIERY")
root_width = 650
root_height = 650

# Get screen width and height
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# Calculate position x, y
x = int((screen_width / 2) - (root_width / 2))
y = int((screen_height / 2) - (root_height / 2))

# Set geometry
root.geometry(f"{root_width}x{root_height}+{x}+{y}")
root.resizable(True, True)
# --- Background Image ---
try:
    if os.path.exists("images/gym.jpg"):
        bg_image = Image.open("images/gym.jpg")
        bg_image = bg_image.resize((650, 650), Image.Resampling.LANCZOS)
        bg_photo = ImageTk.PhotoImage(bg_image)
        bg_label = tk.Label(root, image=bg_photo)
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        bg_label.image = bg_photo
    else:
        root.configure(bg="#34495e")
except Exception as e:
    print("Background load error:", e)
    root.configure(bg="#34495e")

# --- Rounded Form Background ---
rounded_bg = create_rounded_image(340, 340, 20, "white")
bg_label_frame = tk.Label(root, image=rounded_bg, bg="white", bd=0)
bg_label_frame.place(relx=0.5, rely=0.5, anchor="center")

frame = tk.Frame(root, bg="white", highlightthickness=0)
frame.place(relx=0.5, rely=0.5, anchor="center", width=320, height=320)

tk.Label(frame, text="BISMILLAH HOSIERY", bg="white", fg="#2C3E50",
         font=("Segoe UI", 15, "bold")).pack(pady=(8, 15))

# --- Variables ---
username_var = tk.StringVar()
password_var = tk.StringVar()
show_pass = tk.BooleanVar()

# --- Username Field ---
tk.Label(frame, text="Username", bg="white", fg="#001f3f", font=("Segoe UI", 11)).pack(anchor="w", padx=15)
username_bg = create_rounded_image(260, 30, 8, "#f5f5f5")
username_bg_label = tk.Label(frame, image=username_bg, bg="white", bd=0)
username_bg_label.pack(pady=(0, 8))
username_entry = tk.Entry(frame, textvariable=username_var, font=("Segoe UI", 11),
                          relief="flat", bd=0, bg="#f5f5f5")
username_entry.place(in_=username_bg_label, relx=0.5, rely=0.5, anchor="center", width=240, height=22)

# --- Password Field ---
tk.Label(frame, text="Password", bg="white", fg="#001f3f", font=("Segoe UI", 11)).pack(anchor="w", padx=15)
password_bg = create_rounded_image(260, 30, 8, "#f5f5f5")
password_bg_label = tk.Label(frame, image=password_bg, bg="white", bd=0)
password_bg_label.pack(pady=(0, 8))
password_entry = tk.Entry(frame, textvariable=password_var, show="*", font=("Segoe UI", 11),
                          relief="flat", bd=0, bg="#f5f5f5")
password_entry.place(in_=password_bg_label, relx=0.5, rely=0.5, anchor="center", width=240, height=22)

# --- Show Password Checkbox ---
tk.Checkbutton(frame, text="Show Password", variable=show_pass, command=toggle_password,
               bg="white", fg="black", font=("Segoe UI", 9), anchor="w", relief="flat").pack(anchor="w", padx=15, pady=(0, 10))

# --- Login Button ---
login_bg = create_rounded_image(260, 35, 12, "#2C3E50")
login_bg_label = tk.Label(frame, image=login_bg, bg="white", bd=0)
login_bg_label.pack(pady=(5,0))
login_btn = tk.Button(frame, text="Login", command=login, font=("Segoe UI", 11, "bold"),
                      fg="white", bg="#2C3E50", relief="flat", bd=0, activebackground="#002b5c")
login_btn.place(in_=login_bg_label, relx=0.5, rely=0.5, anchor="center", width=240, height=28)

# --- Founder Label ---
tk.Label(frame, text="Founder: Asgher Ali", bg="white", fg="gray",
         font=("Segoe UI", 7, "italic")).pack(pady=(8, 0))

root.mainloop()
