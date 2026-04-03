import tkinter as tk
from tkinter import messagebox, simpledialog
import sqlite3
import hashlib
import re
from PIL import Image, ImageTk
import random
import string



root = tk.Tk()
root.title("Blood Management System")

# Background Image
image_background = Image.open("an.jpg")
image_background = ImageTk.PhotoImage(image_background)

label = tk.Label(root, image=image_background)
label.image = image_background
label.pack(fill='both', expand=True)

# -------------------- Database --------------------

def create_tables():
    conn = sqlite3.connect('blood_management.db')
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            age INTEGER,
            blood_group TEXT,
            contact TEXT,
            location TEXT,
            username TEXT UNIQUE,
            password TEXT,
            email TEXT
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS donors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            address TEXT,
            blood_group TEXT,
            condition TEXT,
            contact TEXT
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS acceptors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            address TEXT,
            condition TEXT
        )
    ''')

    conn.commit()
    conn.close()

create_tables()

# -------------------- Utilities --------------------

def validate_password(password):
    if len(password) < 8:
        return False
    if not re.search("[A-Z]", password):
        return False
    if not re.search("[a-z]", password):
        return False
    if not re.search("[0-9]", password):
        return False
    if not re.search("[^A-Za-z0-9]", password):
        return False
    return True


def generate_password():
    return ''.join(random.choices(
        string.ascii_letters + string.digits + string.punctuation, k=8
    ))

# -------------------- User Functions --------------------

def register_user():
    conn = sqlite3.connect('blood_management.db')
    c = conn.cursor()

    name = entry_name.get()
    age = entry_age.get()
    blood_group = entry_blood_group.get()
    contact = entry_contact.get()
    location = entry_location.get()
    username = entry_username.get()
    raw_password = entry_password.get()
    email = entry_email.get()

    if not validate_password(raw_password):
        messagebox.showerror(
            "Error",
            "Password must be at least 8 characters with uppercase, lowercase, digit, and special character"
        )
        return

    password = hashlib.sha256(raw_password.encode()).hexdigest()

    try:
        c.execute("""
            INSERT INTO users 
            (name, age, blood_group, contact, location, username, password, email)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, age, blood_group, contact, location, username, password, email))

        conn.commit()
        messagebox.showinfo("Success", "Registration Successful")

    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "Username already exists")

    conn.close()


def forgot_password():
    conn = sqlite3.connect('blood_management.db')
    c = conn.cursor()

    username = simpledialog.askstring("Forgot Password", "Enter your username")
    email = simpledialog.askstring("Forgot Password", "Enter your email")

    c.execute(
        "SELECT * FROM users WHERE username = ? AND email = ?",
        (username, email)
    )

    user = c.fetchone()

    if user:
        new_password = generate_password()
        hashed = hashlib.sha256(new_password.encode()).hexdigest()

        c.execute(
            "UPDATE users SET password = ? WHERE username = ?",
            (hashed, username)
        )

        conn.commit()
        messagebox.showinfo("Success", f"New Password: {new_password}")
    else:
        messagebox.showerror("Error", "Username or email not found")

    conn.close()


def login_user():
    conn = sqlite3.connect('blood_management.db')
    c = conn.cursor()

    username = entry_username_login.get()
    password = hashlib.sha256(entry_password_login.get().encode()).hexdigest()

    c.execute(
        "SELECT * FROM users WHERE username = ? AND password = ?",
        (username, password)
    )

    result = c.fetchone()

    if result:
        messagebox.showinfo("Success", "Login Successful")
        open_dashboard(result[0])
    else:
        messagebox.showerror("Error", "Invalid Username or Password")

    conn.close()

# -------------------- Dashboard --------------------

def open_dashboard(user_id):
    dashboard = tk.Toplevel(root)
    dashboard.title("Dashboard")

    bg = ImageTk.PhotoImage(Image.open("an.jpg"))
    lbl = tk.Label(dashboard, image=bg)
    lbl.image = bg
    lbl.pack(fill='both', expand=True)

    tk.Label(dashboard, text="Blood Management Dashboard", bg='white').place(x=50, y=50)

    tk.Button(dashboard, text="Add Donor", command=lambda: add_donor(user_id)).place(x=50, y=100)
    tk.Button(dashboard, text="Add Acceptor", command=lambda: add_acceptor(user_id)).place(x=50, y=150)
    tk.Button(dashboard, text="View Donors", command=view_donors).place(x=50, y=200)
    tk.Button(dashboard, text="View Acceptors", command=view_acceptors).place(x=50, y=250)
    tk.Button(dashboard, text="Nearby Donors", command=lambda: find_nearby_donors(user_id)).place(x=50, y=300)
    tk.Button(dashboard, text="Logout", command=dashboard.destroy).place(x=50, y=350)

# -------------------- Donors --------------------

def add_donor(user_id):
    win = tk.Toplevel(root)
    win.title("Add Donor")

    bg = ImageTk.PhotoImage(Image.open("an.jpg"))
    lbl = tk.Label(win, image=bg)
    lbl.image = bg
    lbl.pack(fill='both', expand=True)

    fields = ["Name", "Address", "Blood Group", "Condition", "Contact"]
    entries = []

    y = 50
    for field in fields:
        tk.Label(win, text=field, bg='white').place(x=50, y=y)
        e = tk.Entry(win)
        e.place(x=180, y=y)
        entries.append(e)
        y += 50

    tk.Button(
        win,
        text="Add Donor",
        command=lambda: save_donor(
            entries[0].get(),
            entries[1].get(),
            entries[2].get(),
            entries[3].get(),
            entries[4].get()
        )
    ).place(x=180, y=300)


def save_donor(name, address, blood_group, condition, contact):
    conn = sqlite3.connect('blood_management.db')
    c = conn.cursor()

    c.execute(
        "INSERT INTO donors VALUES (NULL, ?, ?, ?, ?, ?)",
        (name, address, blood_group, condition, contact)
    )

    conn.commit()
    conn.close()
    messagebox.showinfo("Success", "Donor Added")

# -------------------- Acceptors --------------------

def add_acceptor(user_id):
    win = tk.Toplevel(root)
    win.title("Add Acceptor")

    bg = ImageTk.PhotoImage(Image.open("an.jpg"))
    lbl = tk.Label(win, image=bg)
    lbl.image = bg
    lbl.pack(fill='both', expand=True)

    tk.Label(win, text="Name", bg='white').place(x=50, y=50)
    tk.Label(win, text="Address", bg='white').place(x=50, y=100)
    tk.Label(win, text="Condition", bg='white').place(x=50, y=150)

    e1 = tk.Entry(win)
    e2 = tk.Entry(win)
    e3 = tk.Entry(win)

    e1.place(x=150, y=50)
    e2.place(x=150, y=100)
    e3.place(x=150, y=150)

    tk.Button(
        win,
        text="Add Acceptor",
        command=lambda: save_acceptor(e1.get(), e2.get(), e3.get())
    ).place(x=150, y=200)


def save_acceptor(name, address, condition):
    conn = sqlite3.connect('blood_management.db')
    c = conn.cursor()

    c.execute(
        "INSERT INTO acceptors VALUES (NULL, ?, ?, ?)",
        (name, address, condition)
    )

    conn.commit()
    conn.close()
    messagebox.showinfo("Success", "Acceptor Added")

# -------------------- View --------------------

def view_donors():
    conn = sqlite3.connect('blood_management.db')
    c = conn.cursor()

    win = tk.Toplevel(root)
    win.title("Donors")

    c.execute("SELECT * FROM donors")
    for d in c.fetchall():
        tk.Label(win, text=str(d)).pack(anchor='w')

    conn.close()


def view_acceptors():
    conn = sqlite3.connect('blood_management.db')
    c = conn.cursor()

    win = tk.Toplevel(root)
    win.title("Acceptors")

    c.execute("SELECT * FROM acceptors")
    for a in c.fetchall():
        tk.Label(win, text=str(a)).pack(anchor='w')

    conn.close()


def find_nearby_donors(user_id):
    conn = sqlite3.connect('blood_management.db')
    c = conn.cursor()

    c.execute("SELECT location FROM users WHERE id = ?", (user_id,))
    location = c.fetchone()[0]

    win = tk.Toplevel(root)
    win.title("Nearby Donors")

    c.execute("SELECT * FROM donors WHERE address LIKE ?", ('%' + location + '%',))
    for d in c.fetchall():
        tk.Label(win, text=str(d)).pack(anchor='w')

    conn.close()

# -------------------- UI --------------------

labels = ["Name", "Age", "Blood Group", "Contact", "Location", "Username", "Password", "Email"]
entries = []

y = 50
for label_text in labels:
    tk.Label(root, text=label_text, bg='white').place(x=50, y=y)
    entry = tk.Entry(root, show='*' if label_text == "Password" else None)
    entry.place(x=150, y=y)
    entries.append(entry)
    y += 50

(
    entry_name,
    entry_age,
    entry_blood_group,
    entry_contact,
    entry_location,
    entry_username,
    entry_password,
    entry_email
) = entries

tk.Button(root, text="Register", command=register_user).place(x=80, y=450)
tk.Button(root, text="Forgot Password", command=forgot_password).place(x=180, y=450)
tk.Button(root, text="Login", command=login_user).place(x=300, y=450)

tk.Label(root, text="Username", bg='white').place(x=50, y=500)
entry_username_login = tk.Entry(root)
entry_username_login.place(x=150, y=500)

tk.Label(root, text="Password", bg='white').place(x=50, y=550)
entry_password_login = tk.Entry(root, show='*')
entry_password_login.place(x=150, y=550)

root.mainloop()