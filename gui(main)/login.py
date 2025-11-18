import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from signup_window import signup_window
import mysql.connector
import hashlib
from student_dashboard import StudentDashboard
from admin_dashboard import AdminDashboard

class ExamVaultApp:
    def __init__(self, root):
        self.root = root
        root.title("ExamVault - Secure Exam Proctoring")
        root.geometry(f"{root.winfo_screenwidth()}x{root.winfo_screenheight()}")
        root.configure(bg="#121212")

        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)

        container = tk.Frame(root, bg="#121212")
        container.grid(sticky="nsew")
        container.columnconfigure(0, weight=1)
        container.columnconfigure(1, weight=1)
        container.rowconfigure(0, weight=1)

        # Left Panel (Image)
        left_frame = tk.Frame(container, bg="#1e1e1e")
        left_frame.grid(row=0, column=0, sticky="nsew")

        try:
            image = Image.open("image.png")
            image = image.resize((500, 300))
            image = ImageTk.PhotoImage(image)
            logo = tk.Label(left_frame, image=image, bg="#1e1e1e")
            logo.image = image
            logo.pack(fill="both", expand=True)
        except Exception as e:
            messagebox.showerror("Image Load Error", f"Failed to load image.png\n\n{str(e)}")

        # Right Panel (Login Form)
        right_frame = tk.Frame(container, bg="#181818")
        right_frame.grid(row=0, column=1, sticky="nsew")

        content_frame = tk.Frame(right_frame, bg="#181818")
        content_frame.pack(expand=True, padx=60, pady=40)

        tk.Label(content_frame, text="Login to ExamVault", font=("Arial", 32, "bold"), fg="white", bg="#181818").pack(pady=(10, 20))

        def create_labeled_input(label_text, is_password=False):
            frame = tk.Frame(content_frame, bg="#181818")
            frame.pack(fill="x", pady=(0, 20))
            tk.Label(frame, text=label_text, font=("Arial", 12), fg="white", bg="#181818").pack(anchor="w")
            entry = tk.Entry(frame, font=("Arial", 14), bg="#2a2a2a", fg="white", relief="flat",
                             insertbackground="white", show="*" if is_password else "")
            entry.pack(fill="x", ipady=8)
            return entry

        self.email_entry = create_labeled_input("Email")
        self.password_entry = create_labeled_input("Password", is_password=True)

        # Role Selection
        role_frame = tk.Frame(content_frame, bg="#181818")
        role_frame.pack(fill="x", pady=(0, 20))

        self.role_var = tk.StringVar(value="student")

        tk.Label(role_frame, text="Login as:", font=("Arial", 14), fg="white", bg="#181818").pack(side="left", padx=(0, 10))
        tk.Radiobutton(role_frame, text="Student", variable=self.role_var, value="student",
                       font=("Arial", 12), bg="#181818", fg="white", selectcolor="#2a2a2a").pack(side="left", padx=(0, 20))
        tk.Radiobutton(role_frame, text="Admin", variable=self.role_var, value="admin",
                       font=("Arial", 12), bg="#181818", fg="white", selectcolor="#2a2a2a").pack(side="left")

        # Password Hash Function
        def hash_password(password):
            return hashlib.sha256(password.encode()).hexdigest()

        # Login Logic
        def handle_login():
            email = self.email_entry.get()
            pwd = self.password_entry.get()
            role = self.role_var.get()

            if not email or not pwd:
                messagebox.showwarning("Missing Fields", "Please enter both email and password.")
                return

            try:
                conn = mysql.connector.connect(
                    host="localhost",
                    user="root",
                    password="4080",
                    database="SecureExamProctoring"
                )
                cursor = conn.cursor()
                cursor.execute("SELECT password_hash, role, user_id FROM Users WHERE email=%s", (email,))
                result = cursor.fetchone()

                if result:
                    stored_hash, db_role, user_id = result  # Fetch user_id along with password and role
                    if hash_password(pwd) == stored_hash and role == db_role:
                        messagebox.showinfo("Success", f"Welcome, {email} ({role.capitalize()})!")
                        self.root.destroy()

                        if role == "student":
                            dashboard = StudentDashboard(user_id)
                        else:
                            dashboard = AdminDashboard(user_id)

                        dashboard.app.mainloop()
                            
                    else:
                        messagebox.showerror("Login Failed", "Incorrect password or role.")
                else:
                    messagebox.showerror("Login Failed", "User not found.")
            except Exception as e:
                messagebox.showerror("Database Error", str(e))
            finally:
                if 'conn' in locals():
                    conn.close()

        # Login Button
        def make_button(master, text, bg, hover_bg, command):
            btn = tk.Button(master, text=text, font=("Arial", 14, "bold"), fg="white", bg=bg,
                            activebackground=hover_bg, relief="flat", cursor="hand2", command=command)
            btn.pack(fill="x", pady=10, ipady=8)
            btn.bind("<Enter>", lambda e: btn.config(bg=hover_bg))
            btn.bind("<Leave>", lambda e: btn.config(bg=bg))
            return btn

        make_button(content_frame, "Login", "#007BFF", "#0056b3", handle_login)

        # Sign Up Prompt
        signup_frame = tk.Frame(content_frame, bg="#181818")
        signup_frame.pack(pady=(5, 0))

        tk.Label(signup_frame, text="Don't have an account?", font=("Arial", 10), fg="#cccccc", bg="#181818").pack(side="left")

        signup_label = tk.Label(signup_frame, text="Sign up", font=("Arial", 10, "bold"),
                                fg="#28a745", bg="#181818", cursor="hand2")
        signup_label.pack(side="left", padx=5)
        signup_label.bind("<Button-1>", lambda e: self.open_signup())

    def open_signup(self):
        signup_window(self.root)

if __name__ == "__main__":
    root = tk.Tk()
    app = ExamVaultApp(root)
    root.mainloop()
