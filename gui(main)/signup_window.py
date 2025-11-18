import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import mysql.connector
import hashlib
import re

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

def is_strong_password(password):
    return (
        len(password) >= 8 and
        any(c.isupper() for c in password) and
        any(c.islower() for c in password) and
        any(c.isdigit() for c in password) and
        any(c in r"!@#$%^&*()-_=+[{]}\\|;:'\",<.>/?`~" for c in password)
    )

def signup_window(root):
    root.destroy()
    win = tk.Tk()
    win.title("Sign Up - ExamVault")
    win.state('zoomed')
    win.configure(bg="#121212")

    container = tk.Frame(win, bg="#121212")
    container.pack(fill="both", expand=True)

    left_frame = tk.Frame(container, bg="#121212", width=win.winfo_screenwidth()//2)
    left_frame.pack(side="left", fill="both", expand=True)

    try:
        image = Image.open("image.png")
        image = image.resize((600, 400))
        image = ImageTk.PhotoImage(image)
        tk.Label(left_frame, image=image, bg="#121212").pack(expand=True)
        left_frame.image = image
    except:
        tk.Label(left_frame, text="[Image Missing]", fg="white", bg="#121212", font=("Arial", 16)).pack(expand=True)

    right_frame = tk.Frame(container, bg="#181818", width=win.winfo_screenwidth()//2)
    right_frame.pack(side="right", fill="both", expand=True, padx=80, pady=40)

    tk.Label(right_frame, text="Create Account", font=("Arial", 36, "bold"), fg="white", bg="#181818").pack(pady=(10, 20))
    tk.Label(right_frame, text="Join ExamVault and start secure exams today.", font=("Arial", 14), fg="gray", bg="#181818").pack(pady=(0, 30))

    def create_input(parent, label_text, is_password=False):
        frame = tk.Frame(parent, bg="#181818")
        frame.pack(fill="x", pady=(0, 20))
        tk.Label(frame, text=label_text, font=("Arial", 12), fg="white", bg="#181818").pack(anchor="w")
        entry = tk.Entry(frame, font=("Arial", 14), bg="#2a2a2a", fg="white", relief="flat", insertbackground="white", show="*" if is_password else "")
        entry.pack(fill="x", ipady=10)
        return entry

    name_entry = create_input(right_frame, "Full Name")
    username_entry = create_input(right_frame, "Username")
    email_entry = create_input(right_frame, "Email")
    password_entry = create_input(right_frame, "Password", is_password=True)

    role_var = tk.StringVar(value="student")
    role_frame = tk.Frame(right_frame, bg="#181818")
    role_frame.pack(fill="x", pady=(0, 30))
    tk.Label(role_frame, text="Role:", font=("Arial", 14), fg="white", bg="#181818").pack(side="left", padx=(0, 10))
    tk.Radiobutton(role_frame, text="Student", variable=role_var, value="student", bg="#181818", fg="white", selectcolor="#2a2a2a", font=("Arial", 12)).pack(side="left", padx=10)
    tk.Radiobutton(role_frame, text="Admin", variable=role_var, value="admin", bg="#181818", fg="white", selectcolor="#2a2a2a", font=("Arial", 12)).pack(side="left", padx=10)

    def register():
        name = name_entry.get()
        username = username_entry.get()
        email = email_entry.get()
        pwd = password_entry.get()
        role = role_var.get()

        if not name or not username or not email or not pwd:
            messagebox.showwarning("Incomplete Data", "Please fill all fields.")
            return
        if not is_valid_email(email):
            messagebox.showerror("Invalid Email", "Please enter a valid email address.")
            return
        if not is_strong_password(pwd):
            messagebox.showerror("Weak Password", "Password must be 8+ characters, include uppercase, lowercase, digits, and special characters.")
            return

        try:
            conn = mysql.connector.connect(host="localhost", user="root", password="4080", database="SecureExamProctoring")
            cursor = conn.cursor()
            cursor.execute("INSERT INTO Users (full_name, username, email, password_hash, role) VALUES (%s, %s, %s, %s, %s)",
                           (name, username, email, hash_password(pwd), role))
            conn.commit()
            messagebox.showinfo("Success", "Registration complete! You can now log in.")
            win.destroy()
        except mysql.connector.IntegrityError:
            messagebox.showerror("Error", "This email or username is already registered.")
        except Exception as e:
            messagebox.showerror("Database Error", f"Error: {str(e)}")
        finally:
            if 'conn' in locals():
                conn.close()

    tk.Button(
        right_frame, text="Sign Up", font=("Arial", 12, "bold"),
        bg="#28a745", fg="white", relief="flat",
        activebackground="#218838", activeforeground="white",
        command=register, height=1, width=25
    ).pack(pady=20)

    tk.Label(
        right_frame,
        text="Already have an account? Please login from the main screen.",
        font=("Arial", 12), fg="gray", bg="#181818"
    ).pack(pady=10)

    win.mainloop()
