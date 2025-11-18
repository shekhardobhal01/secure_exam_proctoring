import customtkinter as ctk
import mysql.connector
from tkinter import messagebox, filedialog
from customtkinter import CTkImage
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from image import load_icon
import csv


class AdminDashboard:
    def __init__(self, user_id):
        self.user_id = user_id
        self.app = ctk.CTk()

        self.app.geometry("1100x650")
        self.app.title("ExamVolt - Admin Dashboard")

        self.conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='4080',
            database='SecureExamProctoring'
        )
        self.cursor = self.conn.cursor()

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.header = ctk.CTkFrame(self.app, height=60, fg_color="#2c3e50")
        self.header.pack(side="top", fill="x")
        self.header_label = ctk.CTkLabel(
            self.header,
            text="⚙️ Admin Dashboard",
            text_color="white",
            font=ctk.CTkFont(size=22, weight="bold")
        )
        self.header_label.pack(pady=10)

        self.sidebar = ctk.CTkFrame(self.app, width=320, corner_radius=0, fg_color="#34495e")
        self.sidebar.pack(side="left", fill="y")

        icon_image = load_icon()
        if icon_image:
            icon_image = icon_image.resize((100, 100), Image.Resampling.LANCZOS)
            self.profile_image = ctk.CTkImage(dark_image=icon_image, size=(100, 100))
            self.profile_pic = ctk.CTkLabel(
                self.sidebar, image=self.profile_image, text="", width=100, height=100,
                corner_radius=10, fg_color="#22313f"
            )
        else:
            self.profile_pic = ctk.CTkLabel(
                self.sidebar, text="Image\nNot Found", width=100, height=100,
                corner_radius=10, fg_color="#22313f", text_color="white"
            )
        self.profile_pic.pack(pady=15)

        self.content = ctk.CTkFrame(self.app, fg_color="#1e1e1e")
        self.content.pack(side="right", expand=True, fill="both", padx=10, pady=10)
        self.main_display = ctk.CTkLabel(
            self.content,
            text="👈 Choose an option to manage the system.",
            font=ctk.CTkFont(size=16),
            wraplength=600,
            justify="left",
            text_color="white"
        )
        self.main_display.pack(padx=20, pady=20, anchor="nw")

        button_font = ctk.CTkFont(size=15, weight="bold")

        ctk.CTkButton(self.sidebar, text="Create Exams", command=self.create_exam_and_upload_questions,
                      fg_color="#3498db", hover_color="#2980b9", font=button_font, height=50).pack(pady=12, padx=20, fill="x")

        ctk.CTkButton(self.sidebar, text="View All Exams", command=self.view_all_exams,
                      fg_color="#1abc9c", hover_color="#16a085", font=button_font, height=50).pack(pady=12, padx=20, fill="x")

        ctk.CTkButton(self.sidebar, text="Monitor Logs", command=self.view_logs,
                      fg_color="#f39c12", hover_color="#d68910", font=button_font, height=50, text_color="black").pack(pady=12, padx=20, fill="x")

        ctk.CTkButton(self.sidebar, text="View Reports", command=self.view_reports,
              fg_color="#2ecc71", hover_color="#27ae60", font=button_font, height=50).pack(pady=12, padx=20, fill="x")

        ctk.CTkButton(self.sidebar, text="Delete Exam", command=self.delete_exam,
                      fg_color="#e67e22", hover_color="#ca6f1e", font=button_font, height=50).pack(pady=12, padx=20, fill="x")

        ctk.CTkButton(self.sidebar, text="Logout", command=self.logout,
                      fg_color="#e74c3c", hover_color="#c0392b", font=button_font, height=50).pack(pady=12, padx=20, fill="x")

        

    def create_exam_and_upload_questions(self):
        for widget in self.content.winfo_children():
            widget.destroy()

        form_title = ctk.CTkLabel(self.content, text="📝 Create New Exam & Upload Questions", font=ctk.CTkFont(size=18, weight="bold"), text_color="white")
        form_title.pack(pady=(10, 20))

        self.exam_name_entry = ctk.CTkEntry(self.content, placeholder_text="Exam Name")
        self.exam_name_entry.pack(pady=10, padx=20, fill="x")

        self.subject_entry = ctk.CTkEntry(self.content, placeholder_text="Subject")
        self.subject_entry.pack(pady=10, padx=20, fill="x")

        self.start_time_entry = ctk.CTkEntry(self.content, placeholder_text="Start Time (YYYY-MM-DD HH:MM:SS)")
        self.start_time_entry.pack(pady=10, padx=20, fill="x")

        self.end_time_entry = ctk.CTkEntry(self.content, placeholder_text="End Time (YYYY-MM-DD HH:MM:SS)")
        self.end_time_entry.pack(pady=10, padx=20, fill="x")
       
        self.duration_entry = ctk.CTkEntry(self.content, placeholder_text="Duration (minutes)")
        self.duration_entry.pack(pady=10, padx=20, fill="x")
      
        self.exam_type_var = ctk.StringVar(value="MCQ")
        self.exam_type_dropdown = ctk.CTkOptionMenu(self.content, variable=self.exam_type_var, values=["MCQ"])
        self.exam_type_dropdown.pack(pady=10, padx=20)

        submit_btn = ctk.CTkButton(self.content, text="Submit Exam", command=self.insert_exam,
                                   fg_color="#27ae60", hover_color="#1e8449")
        submit_btn.pack(pady=20)
        
        upload_questions_btn = ctk.CTkButton(self.content, text="Upload Questions", command=self.upload_questions,
                                             fg_color="#ff6f61", hover_color="#e55342")
        upload_questions_btn.pack(pady=20)
        

    def insert_exam(self):
        name = self.exam_name_entry.get()
        subject = self.subject_entry.get()
        start = self.start_time_entry.get()
        end = self.end_time_entry.get()
        duration = self.duration_entry.get()
        exam_type = self.exam_type_var.get()

        if not all([name, subject, start, end, duration, exam_type]):
            messagebox.showwarning("Input Error", "Please fill all the fields.")
            return

        try:
            # Insert exam with duration
            self.cursor.execute(
                "INSERT INTO Exams (exam_name, subject, start_time, end_time, duration_minutes, exam_type) "
                "VALUES (%s, %s, %s, %s, %s, %s)",
                (name, subject, start, end, duration, exam_type)
            )
            exam_id = self.cursor.lastrowid
            
            # Automatically enroll all students in this exam
            self.cursor.execute("SELECT user_id FROM Users WHERE role = 'student'")
            students = self.cursor.fetchall()
            
            for (student_id,) in students:
                try:
                    self.cursor.execute(
                        "INSERT INTO Student_Exams (user_id, exam_id) VALUES (%s, %s)",
                        (student_id, exam_id)
                    )
                except mysql.connector.Error as e:
                    print(f"Error enrolling student {student_id}: {e}")
            
            self.conn.commit()
            messagebox.showinfo("Success", f"Exam created and {len(students)} students enrolled successfully!")
            
        except Exception as e:
            self.conn.rollback()
            messagebox.showerror("Database Error", str(e))

    def upload_questions(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if not file_path:
            return

        try:
            # Get the most recently created exam ID
            self.cursor.execute("SELECT exam_id FROM Exams ORDER BY exam_id DESC LIMIT 1")
            result = self.cursor.fetchone()

            if result is None:
                messagebox.showerror("Error", "No exam found. Please create an exam first.")
                return

            exam_id = result[0]

            
            with open(file_path, newline="", encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                next(reader)  # Skip header row
                
                for row in reader:
                    if len(row) < 6:
                        continue  # Skip malformed rows
                    
                    question, option_a, option_b, option_c, option_d, answer = row[:6]
                    
                    try:
                        self.cursor.execute(
                            """INSERT INTO Questions 
                            (exam_id, question, option_a, option_b, option_c, option_d, answer) 
                            VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                            (exam_id, question, option_a, option_b, option_c, option_d, answer)
                        )
                    except Exception as e:
                        messagebox.showerror("Upload Error", f"Error on row {reader.line_num}: {str(e)}")
                        self.conn.rollback()
                        return
                
                self.conn.commit()
                messagebox.showinfo("Success", "Questions uploaded successfully!")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to upload questions: {str(e)}")
            self.conn.rollback()

    def view_all_exams(self):
        for widget in self.content.winfo_children():
            widget.destroy()

        title = ctk.CTkLabel(self.content, text="📚 All Exams", font=ctk.CTkFont(size=18, weight="bold"), text_color="white")
        title.pack(pady=(10, 10))

        try:
            self.cursor.execute("SELECT exam_name, subject, start_time, end_time, exam_type FROM Exams")
            exams = self.cursor.fetchall()

            for e in exams:
                info = f"{e[0]} ({e[1]} - {e[4]}): {e[2]} to {e[3]}"
                label = ctk.CTkLabel(self.content, text=info, text_color="white", anchor="w", justify="left", wraplength=700)
                label.pack(anchor="w", padx=20, pady=5)

        except Exception as e:
            messagebox.showerror("Database Error", str(e))


    def view_logs(self):
        """Displays the 10 most recent monitoring logs."""
        # Clear content area
        for widget in self.content.winfo_children():
            widget.destroy()

        title = ctk.CTkLabel(self.content, text="📜 Recent Monitoring Logs", font=ctk.CTkFont(size=18, weight="bold"), text_color="white")
        title.pack(pady=(10, 10))

        self.cursor.execute("""
            SELECT log_type, log_details, timestamp
            FROM Monitoring_Logs
            ORDER BY timestamp DESC
            LIMIT 10
        """)
        logs = self.cursor.fetchall()

        if not logs:
            ctk.CTkLabel(self.content, text="No logs found.", text_color="white").pack(anchor="w", padx=20, pady=5)
        else:
            for log_type, details, timestamp in logs:
                formatted_time = timestamp.strftime('%Y-%m-%d %H:%M:%S') if hasattr(timestamp, 'strftime') else str(timestamp)
                log_entry = f"[{formatted_time}] {log_type} - {details}"
                ctk.CTkLabel(self.content, text=log_entry, text_color="white", anchor="w", justify="left", wraplength=700).pack(anchor="w", padx=20, pady=5)


    def view_student_results(self):
        """Displays all student exam results with email, exam name, score, and status."""
        # Clear previous content
        for widget in self.content.winfo_children():
            widget.destroy()

        title = ctk.CTkLabel(self.content, text="📊 Student Results", font=ctk.CTkFont(size=18, weight="bold"), text_color="white")
        title.pack(pady=(10, 10))

        self.cursor.execute("""
            SELECT u.email, e.exam_name, r.score, r.status
            FROM Exam_Results r
            JOIN Student_Exams se ON r.student_exam_id = se.student_exam_id
            JOIN Users u ON se.user_id = u.user_id
            JOIN Exams e ON se.exam_id = e.exam_id
        """)
        results = self.cursor.fetchall()

        if not results:
            ctk.CTkLabel(self.content, text="No results available.", text_color="white").pack(anchor="w", padx=20, pady=5)
        else:
            for email, exam_name, score, status in results:
                result_text = f"{email:<30} | {exam_name:<20} | Score: {score:<5} | Status: {status}"
                ctk.CTkLabel(self.content, text=result_text, text_color="white", anchor="w", justify="left", wraplength=700).pack(anchor="w", padx=20, pady=5)

    def view_reports(self):
        for widget in self.content.winfo_children():
            widget.destroy()

        # --- Scrollable Frame Setup ---
        scroll_frame = ctk.CTkScrollableFrame(self.content, fg_color="#121212")
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # --- Page Title ---
        title = ctk.CTkLabel(
            scroll_frame,
            text="📊 Suspicious Activity Reports",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="white"
        )
        title.pack(pady=(10, 5))

        subtitle = ctk.CTkLabel(
            scroll_frame,
            text="Overview of monitoring events and violations",
            font=ctk.CTkFont(size=14),
            text_color="#bdc3c7"
        )
        subtitle.pack(pady=(0, 20))

        try:
            # === Pie Chart Section ===
            pie_frame = ctk.CTkFrame(scroll_frame, fg_color="#1e1e1e")
            pie_frame.pack(fill="x", pady=(10, 20), padx=20)

            pie_title = ctk.CTkLabel(
                pie_frame,
                text="🔍 Activity Type Distribution",
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color="white"
            )
            pie_title.pack(pady=(10, 5))

            self.cursor.execute("""
                SELECT activity_description, COUNT(*) 
                FROM Suspicious_Activities 
                GROUP BY activity_description
            """)
            activity_data = self.cursor.fetchall()

            if activity_data:
                labels = [desc if desc else "Unknown Activity" for desc, count in activity_data]
                sizes = [count for desc, count in activity_data]

                fig1, ax1 = plt.subplots(figsize=(6.5, 5.5), dpi=110, facecolor='#1e1e1e')
                ax1.pie(
                    sizes,
                    labels=labels,
                    autopct='%1.1f%%',
                    startangle=140,
                    textprops={'fontsize': 10, 'color': 'white'}
                )
                ax1.set_title("Distribution by Activity Type", fontsize=13, color='white')
                fig1.patch.set_facecolor('#1e1e1e')
                ax1.set_facecolor('#1e1e1e')

                pie_chart = FigureCanvasTkAgg(fig1, master=pie_frame)
                pie_chart.draw()
                pie_chart.get_tk_widget().pack(pady=10)
            else:
                ctk.CTkLabel(pie_frame, text="No activity data found.", text_color="white").pack(pady=10)

            # === Bar Chart Section ===
            bar_frame = ctk.CTkFrame(scroll_frame, fg_color="#1e1e1e")
            bar_frame.pack(fill="x", pady=(10, 40), padx=20)

            bar_title = ctk.CTkLabel(
                bar_frame,
                text="👤 Violations per Student",
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color="white"
            )
            bar_title.pack(pady=(10, 5))

            self.cursor.execute("""
                SELECT U.full_name, COUNT(*) 
                FROM Suspicious_Activities SA
                JOIN Student_Exams SE ON SA.student_exam_id = SE.student_exam_id
                JOIN Users U ON SE.user_id = U.user_id
                GROUP BY U.full_name
            """)
            student_data = self.cursor.fetchall()

            if student_data:
                student_names = [name for name, count in student_data]
                activity_counts = [count for name, count in student_data]

                fig2, ax2 = plt.subplots(figsize=(10, max(4, len(student_names) * 0.65)), dpi=110, facecolor='#1e1e1e')
                ax2.barh(student_names, activity_counts, color="#f39c12")

                ax2.set_xlabel("Number of Violations", fontsize=12, color="white", labelpad=10)
                ax2.set_title("Suspicious Activities by Student", fontsize=14, color="white", pad=15)
                ax2.tick_params(axis='y', labelsize=10, colors="white")
                ax2.tick_params(axis='x', labelsize=10, colors="white")
                ax2.spines['top'].set_visible(False)
                ax2.spines['right'].set_visible(False)
                ax2.spines['bottom'].set_color('gray')
                ax2.spines['left'].set_color('gray')
                fig2.patch.set_facecolor('#1e1e1e')
                ax2.set_facecolor('#1e1e1e')

                bar_chart = FigureCanvasTkAgg(fig2, master=bar_frame)
                bar_chart.draw()
                bar_chart.get_tk_widget().pack(pady=10)
            else:
                ctk.CTkLabel(bar_frame, text="No student activity data found.", text_color="white").pack(pady=10)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load reports:\n{str(e)}")


    def delete_exam(self):
        try:
            # Fetch all exams
            self.cursor.execute("SELECT exam_id, exam_name FROM Exams")
            exams = self.cursor.fetchall()
            
            if not exams:
                messagebox.showinfo("Info", "No exams available to delete")
                return

            exam_names = [e[1] for e in exams]

            # Clear previous content
            for widget in self.content.winfo_children():
                widget.destroy()

            # Create selection UI
            title = ctk.CTkLabel(self.content, text="Select Exam to Delete",font=ctk.CTkFont(size=16, weight="bold"))
            title.pack(pady=10)

            self.exam_to_delete = ctk.CTkOptionMenu(self.content, values=exam_names)
            self.exam_to_delete.pack(pady=10, padx=20)

            confirm_btn = ctk.CTkButton(
                self.content, 
                text="Confirm Deletion", 
                command=self.confirm_delete,
                fg_color="#e74c3c",  # Red color for delete action
                hover_color="#c0392b"
            )
            confirm_btn.pack(pady=20)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load exams: {str(e)}")


    def confirm_delete(self):
        try:
            # Get selected exam
            selected_exam = self.exam_to_delete.get()
            if not selected_exam:
                return

            # Get exam_id for selected exam
            self.cursor.execute("SELECT exam_id FROM Exams WHERE exam_name = %s", (selected_exam,))
            exam_id_result = self.cursor.fetchone()
            
            if not exam_id_result:
                messagebox.showerror("Error", f"Exam '{selected_exam}' not found in database.")
                return
                
            exam_id = exam_id_result[0]

            # Detailed confirmation
            confirm = messagebox.askyesno(
                "Confirm Deletion",
                f"Are you sure you want to permanently delete:\n\n"
                f"Exam: {selected_exam}\n\n"
                "This will also delete all related:\n"
                "- Student attempts\n"
                "- Exam results\n"
                "- Questions\n"
                "- Monitoring data\n\n"
                "This action cannot be undone!"
            )
            
            if not confirm:
                return

            # Start transaction
            self.cursor.execute("START TRANSACTION")

            try:
                # 1. Delete from Suspicious_Activities
                self.cursor.execute("""
                    DELETE sa FROM Suspicious_Activities sa
                    JOIN Student_Exams se ON sa.student_exam_id = se.student_exam_id
                    WHERE se.exam_id = %s
                """, (exam_id,))

                # 2. Delete from Monitoring_Logs
                self.cursor.execute("""
                    DELETE ml FROM Monitoring_Logs ml
                    JOIN Student_Exams se ON ml.student_exam_id = se.student_exam_id
                    WHERE se.exam_id = %s
                """, (exam_id,))

                # 3. Delete from Exam_Results
                self.cursor.execute("""
                    DELETE er FROM Exam_Results er
                    JOIN Student_Exams se ON er.student_exam_id = se.student_exam_id
                    WHERE se.exam_id = %s
                """, (exam_id,))

                # 4. Delete from Student_Answers
                self.cursor.execute("""
                    DELETE FROM Student_Answers 
                    WHERE exam_id = %s
                """, (exam_id,))

                # 5. Delete from Questions
                self.cursor.execute("""
                    DELETE FROM Questions 
                    WHERE exam_id = %s
                """, (exam_id,))

                # 6. Delete from Student_Exams
                self.cursor.execute("""
                    DELETE FROM Student_Exams 
                    WHERE exam_id = %s
                """, (exam_id,))

                # 7. Finally delete the exam
                self.cursor.execute("""
                    DELETE FROM Exams 
                    WHERE exam_id = %s
                """, (exam_id,))

                # Commit transaction
                self.conn.commit()
                
                messagebox.showinfo(
                    "Success", 
                    f"Exam '{selected_exam}' and all related data were successfully deleted."
                )
                self.view_all_exams()

            except mysql.connector.Error as err:
                self.conn.rollback()
                if err.errno == mysql.connector.errorcode.ER_ROW_IS_REFERENCED:
                    messagebox.showerror(
                        "Delete Error",
                        "Could not delete exam because it's still referenced by other records.\n"
                        "Please check all foreign key relationships."
                    )
                else:
                    messagebox.showerror("Database Error", f"Error deleting exam: {str(err)}")
                    
            except Exception as e:
                self.conn.rollback()
                messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete exam: {str(e)}")



    def logout(self):
        self.app.quit()

# To launch the app, instantiate the AdminDashboard class
# AdminDashboard(user_id=1)
