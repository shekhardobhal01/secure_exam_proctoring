from tkinter import messagebox
import cv2
import customtkinter as ctk
from PIL import Image
import face_recognition # New import for deep learning face detection
from pynput import keyboard # type: ignore
import psutil
import pygetwindow as gw
import threading
import datetime
import time
import mysql.connector
from image import load_icon

def log_event(event_type, details, cursor, conn):
    """Log an event to the Monitoring_Logs table with proper data validation"""
    try:
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Ensure data fits in columns
        event_type = str(event_type)[:100]  # Matches VARCHAR(100)
        details = str(details)              # TEXT column can handle long strings
        
        sql = """INSERT INTO Monitoring_Logs 
                (log_type, log_details, timestamp) 
                VALUES (%s, %s, %s)"""
                
        cursor.execute(sql, (event_type, details, timestamp))
        conn.commit()
        
    except Exception as e:
        print(f"Error logging event: {e}")
        conn.rollback()

class StudentDashboard:
    def __init__(self, user_id):
        self.app = ctk.CTk()
        self.app.geometry("1100x650")
        self.app.title("ExamVolt - Student Dashboard")
        self.app.protocol("WM_DELETE_WINDOW", self.logout)
        self.user_id = user_id
        self.exam_start_time = None
        self.student_exam_id = None
        self.exam_questions = []
        self.current_question_index = 0
        self.selected_exam_id = None
        self.exam_timer = None
        self.timer_running = False
        self.remaining_time = 0
        self.timer_label = None
        self.timer_id = None
        self.option_vars = []
        self.selected_option = ctk.StringVar(value="")
        self.multiple_face_flag = False
        self.warning_popup_open = False
        self.monitoring_active = False
        self.ctrl_pressed = False
        self.alt_pressed = False
        self.restricted_apps = ["Zoom", "TeamViewer", "AnyDesk", "chrome", "firefox"]

        try:
            self.conn = mysql.connector.connect(
                host='localhost',
                user='root',
                password='4080',
                database='SecureExamProctoring'
            )
            self.cursor = self.conn.cursor(dictionary=True, buffered=True)
        except mysql.connector.Error as e:
            print(f"Error connecting to database: {e}")
            messagebox.showerror("Database Error", "Failed to connect to database. Application will exit.")
            self.app.destroy()
            return

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.setup_gui()
        self.app.mainloop()

    def setup_gui(self):
        # Header
        self.header = ctk.CTkFrame(self.app, height=60, fg_color="#2c3e50")
        self.header.pack(side="top", fill="x")
        self.header_label = ctk.CTkLabel(
            self.header,
            text="🎓 Student Dashboard",
            text_color="white",
            font=ctk.CTkFont(size=22, weight="bold")
        )
        self.header_label.pack(pady=10)

        # Sidebar
        self.sidebar = ctk.CTkFrame(self.app, width=320, corner_radius=0, fg_color="#34495e")
        self.sidebar.pack(side="left", fill="y")
        
        icon_image = load_icon()
        if icon_image:
            icon_image = icon_image.resize((100, 100), Image.Resampling.LANCZOS)
            self.profile_image = ctk.CTkImage(
                        light_image=icon_image,
                        dark_image=icon_image,
                        size=(100, 100)
                    )
            self.profile_pic = ctk.CTkLabel(self.sidebar, image=self.profile_image, text="", width=100, height=100)
        else:
            self.profile_pic = ctk.CTkLabel(self.sidebar, text="Image\nNot Found", width=100, height=100, text_color="white")
        self.profile_pic.pack(pady=15)

        # Fetch user info
        self.cursor.execute("SELECT username, role, email, full_name FROM Users WHERE user_id = %s", (self.user_id,))
        user_data = self.cursor.fetchone()
        if user_data:
            self.username = user_data.get('username', 'Unknown')
            self.role = user_data.get('role', 'Unknown')
            self.email = user_data.get('email', 'Unknown')
            self.full_name = user_data.get('full_name', 'Unknown')
        else:
            self.username = self.role = self.email = self.full_name = "Unknown"


        # Labels
        self.username_label = ctk.CTkLabel(self.sidebar, text=f"User: {self.username}", text_color="white", anchor="w")
        self.name_label = ctk.CTkLabel(self.sidebar, text=f"Name: {self.full_name}", text_color="white", anchor="w")
        self.email_label = ctk.CTkLabel(self.sidebar, text=f"Email: {self.email}", text_color="white", anchor="w")
        self.username_label.pack(pady=5, padx=10, fill="x")
        self.name_label.pack(pady=5, padx=10, fill="x")
        self.email_label.pack(pady=5, padx=10, fill="x")
        
        # Buttons
        button_font = ctk.CTkFont(size=15, weight="bold")
        self.view_exams_btn = ctk.CTkButton(self.sidebar, text="Available Exams", command=self.show_available_exams,
                      fg_color="#3498db", hover_color="#2980b9", font=button_font, height=50)
        self.start_exam_btn = ctk.CTkButton(self.sidebar, text="Start Exam", command=self.select_exam,
                      fg_color="#1abc9c", hover_color="#16a085", font=button_font, height=50)
        self.view_results_btn = ctk.CTkButton(self.sidebar, text="View Results", command=self.view_results,
                      fg_color="#2ecc71", hover_color="#27ae60", font=button_font, height=50)
        self.logout_btn = ctk.CTkButton(self.sidebar, text="Logout", command=self.logout,
                      fg_color="#e74c3c", hover_color="#c0392b", font=button_font, height=50)
        for btn in [self.view_exams_btn, self.start_exam_btn, self.view_results_btn, self.logout_btn]:
            btn.pack(pady=10, padx=10, fill="x")

        # Main Content
        self.content = ctk.CTkFrame(self.app, fg_color="#1e1e1e")
        self.content.pack(side="right", expand=True, fill="both", padx=10, pady=10)
        # Warning banner (hidden by default)
        self.warning_banner = ctk.CTkLabel(
            self.content,
            text="⚠️ Warning",
            text_color="white",
            fg_color="#e74c3c",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40,
            corner_radius=8
        )
        self.warning_banner.place_forget()  # Start hidden
        self.main_display = ctk.CTkLabel(
            self.content, text="👈 Choose an option to proceed.",
            font=ctk.CTkFont(size=16), wraplength=600, justify="left", text_color="white"
        )
        self.main_display.pack(padx=20, pady=20, anchor="nw")

        # Webcam frame
        self.camera_frame = ctk.CTkLabel(self.content)
        self.camera_frame.pack(pady=10,padx=10,anchor="ne",side="top")

        # Question frame (will be populated during exam)
        self.question_frame = ctk.CTkFrame(self.content)
        self.options_frame = ctk.CTkFrame(self.content)

        # Initialize webcam
        self.cap = None
        self.missing_face_counter = 0
        self.max_missing_face = 30  # Allow 30 frames (~10 seconds) of missing face before warning

    def show_available_exams(self):
        try:
            self.cursor.execute("""
                SELECT exam_id, exam_name, start_time, end_time
                FROM Exams
                WHERE NOW() <= end_time
            """)
            exams = self.cursor.fetchall()

            if not exams:
                self.main_display.configure(text="🚫 No upcoming exams available.")
                return

            exam_text = "📋 Upcoming Exams:\n\n"
            for exam in exams:
                exam_id = exam["exam_id"]
                name = exam["exam_name"]
                start = exam["start_time"]
                end = exam["end_time"]
                exam_text += f"📝 {exam_id}: {name}\n🕒 {start} to {end}\n\n"

            exam_text += "➡️ Use the 'Start Exam' button to begin.\n"
            self.main_display.configure(text=exam_text)

        except Exception as e:
            self.main_display.configure(text=f"❌ Error loading exams: {str(e)}")


    def select_exam(self):
        self.clear_content()  # Clear old content from main area

        label = ctk.CTkLabel(self.content, text="🔍 Select Exam", font=ctk.CTkFont(size=18))
        label.pack(pady=10)

        current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.cursor.execute("""
            SELECT exam_id, exam_name 
            FROM Exams 
            WHERE start_time <= %s AND end_time >= %s
        """, (current_time, current_time))
        exams = self.cursor.fetchall()

        if not exams:
            no_exam_label = ctk.CTkLabel(self.content, text="🚫 No exams available to start right now.")
            no_exam_label.pack(pady=10)
            return

        exam_values = [f"{exam['exam_id']} - {exam['exam_name']}" for exam in exams]
        self.exam_dropdown = ctk.CTkComboBox(self.content, values=exam_values)
        self.exam_dropdown.pack(pady=20)

        
        start_btn = ctk.CTkButton(self.content, text="Enter Exam", command=self.begin_exam)
        start_btn.pack(pady=10)
            
    def clear_content(self):
        """Clear all widgets from the content area except the main display and camera frame"""
        for widget in self.content.winfo_children():
            if widget not in [self.main_display, self.camera_frame]:
                try:
                    widget.destroy()
                except:
                    pass
            
        # Recreate frames if they were destroyed
        if not hasattr(self, 'question_frame') or not self.question_frame.winfo_exists():
            self.question_frame = ctk.CTkFrame(self.content)
        if not hasattr(self, 'options_frame') or not self.options_frame.winfo_exists():
            self.options_frame = ctk.CTkFrame(self.content)
        
        # Reset the main display text
        self.main_display.configure(text="")
        
    def begin_exam(self):
            selected = self.exam_dropdown.get()
            if not selected:
                return

            try:
                exam_id = int(selected.split(" - ")[0])
            except (ValueError, IndexError):
                messagebox.showerror("Error", "Invalid exam selection. Please try again.")
                return

            self.selected_exam_id = exam_id

            # Check if already attempted
            self.cursor.execute("SELECT student_exam_id FROM Student_Exams WHERE user_id = %s AND exam_id = %s", (self.user_id, exam_id))
            existing_exam = self.cursor.fetchone()

            if existing_exam:
                self.student_exam_id = existing_exam['student_exam_id']
                self.cursor.execute("SELECT status FROM Exam_Results WHERE student_exam_id = %s", (self.student_exam_id,))
                result = self.cursor.fetchone()
                if result and result['status'] == 'completed':
                    self.main_display.configure(text="❌ You have already completed this exam.")
                    return
            else:
                self.cursor.execute("INSERT INTO Student_Exams (user_id, exam_id) VALUES (%s, %s)", (self.user_id, exam_id))
                self.conn.commit()
                self.student_exam_id = self.cursor.lastrowid

            # Get duration
            self.cursor.execute("SELECT duration_minutes FROM Exams WHERE exam_id = %s", (exam_id,))
            result = self.cursor.fetchone()
            duration = result['duration_minutes'] if result else None
            if duration is None:
                messagebox.showerror("Error", "Could not retrieve exam duration")
                return
            self.remaining_time = duration * 60

            # Load questions
            self.cursor.execute("""
                SELECT question_id, question, option_a, option_b, option_c, option_d, answer, marks 
                FROM Questions 
                WHERE exam_id = %s ORDER BY question_id
            """, (exam_id,))
            self.exam_questions = self.cursor.fetchall()

            if not self.exam_questions:
                self.main_display.configure(text="❌ No questions found for this exam.")
                return

            self.current_question_index = 0
            self.clear_content()

            # --- LAYOUT STARTS ---
            self.camera_frame.pack(anchor="ne", side="top", padx=20, pady=10)

            # Timer at top center
            if not hasattr(self, 'timer_label') or self.timer_label is None or not self.timer_label.winfo_exists():
                self.timer_label = ctk.CTkLabel(self.content, text="", font=ctk.CTkFont(size=16, weight="bold"))

            self.timer_label.pack(anchor="n", pady=(10, 0))
            # Question & options
            self.question_frame = ctk.CTkFrame(self.content)
            self.question_frame.pack(anchor="center", pady=(30, 10))

            self.options_frame = ctk.CTkFrame(self.content)
            self.options_frame.pack(anchor="center")

            # Navigation (bottom row)
            self.nav_frame = ctk.CTkFrame(self.content)
            self.nav_frame.pack(side="bottom", fill="x", padx=20, pady=20)

            # --- Webcam, timer, monitoring ---
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                self.main_display.configure(text="❌ Webcam access failed. Exam cannot proceed without camera.")
                return

            self.monitoring_active = True
            # Start webcam monitoring
            threading.Thread(target=self.monitor_student, daemon=True).start()
            
            # Start screen monitoring thread
            threading.Thread(target=self.monitor_screen_activity, daemon=True).start()
   
            # Start keystroke monitoring
            threading.Thread(target=self.monitor_keystrokes, daemon=True).start()
                
            # Start system resource monitoring
            threading.Thread(target=self.monitor_resources, daemon=True).start()


            # Start exam
            self.exam_start_time = datetime.datetime.now()
            self.selected_option = ctk.StringVar()
            self.display_question()
            self.start_exam_timer()
            log_event("Exam Started", f"Student {self.user_id} started exam {exam_id}", self.cursor, self.conn)
    
    def display_question(self):
        try:
            # Clear previous widgets safely
            self.clear_question_widgets()

            # Check if we've reached the end of questions
            if self.current_question_index >= len(self.exam_questions):
                self.end_exam()
                return

            # Ensure frames are packed visibly
            self.question_frame.pack(fill="x", padx=20, pady=(50, 10), anchor="n")
            self.options_frame.pack(fill="x", padx=30, pady=10, anchor="n")

            # Get current question data
            question_data = self.exam_questions[self.current_question_index]
            question_id = question_data['question_id']
            question_text = question_data['question']
            option_a = question_data['option_a']
            option_b = question_data['option_b']
            option_c = question_data['option_c']
            option_d = question_data['option_d']
            correct_option = question_data['answer']
            marks = question_data['marks']
                # Display question
            question_label = ctk.CTkLabel(
                self.question_frame,
                text=f"Question {self.current_question_index + 1}/{len(self.exam_questions)} (Marks: {marks}):\n{question_text}",
                font=ctk.CTkFont(size=14, weight="bold"),
                wraplength=600,
                justify="left"
            )
            question_label.pack(pady=10, anchor="w")

            # Display options using radio buttons
            options = [option_a, option_b, option_c, option_d]
            for i, option in enumerate(options):
                if option:  # Only display if option is not empty
                    rb = ctk.CTkRadioButton(
                        self.options_frame,
                        text=option,
                        variable=self.selected_option,
                        value=str(i + 1),  # 1-4 for options A-D
                        font=ctk.CTkFont(size=12)
                    )
                    rb.pack(pady=5, anchor="w")

            # Navigation buttons - single instance
            if hasattr(self, 'content') and self.content.winfo_exists():
                # Remove any existing nav frame
                if hasattr(self, 'nav_frame') and self.nav_frame.winfo_exists():
                    self.nav_frame.destroy()

                self.nav_frame = ctk.CTkFrame(self.content)
                self.nav_frame.pack(side="bottom", fill="x", padx=30, pady=20)

                # Left (Previous)
                if self.current_question_index > 0:
                    prev_btn = ctk.CTkButton(self.nav_frame, text="Previous", command=self.prev_question)
                    prev_btn.pack(side="left", padx=10)

                # Right (Next or Submit)
                if self.current_question_index < len(self.exam_questions) - 1:
                    next_btn = ctk.CTkButton(self.nav_frame, text="Next", command=self.next_question)
                    next_btn.pack(side="right", padx=10)
                else:
                    submit_btn = ctk.CTkButton(self.nav_frame, text="Submit Exam", command=self.end_exam)
                    submit_btn.pack(side="right", padx=10)
                    

        except Exception as e:
            print(f"Error displaying question: {e}")
            if hasattr(self, 'main_display') and self.main_display.winfo_exists():
                self.main_display.configure(text=f"Error loading question: {str(e)}")
                
    def monitor_resources(self):
        try:
            while getattr(self, "monitoring_active", False):
                cpu_usage = psutil.cpu_percent(interval=1)
                memory_info = psutil.virtual_memory()
                mem_usage = memory_info.percent

                # Thresholds (adjustable)
                CPU_THRESHOLD = 85
                MEM_THRESHOLD = 90

                if cpu_usage > CPU_THRESHOLD:
                    self.log_suspicious_activity_custom(f"High CPU usage: {cpu_usage}%")
                    self.show_warning("⚠️ System CPU usage is very high.\nClose unnecessary programs.")

                if mem_usage > MEM_THRESHOLD:
                    self.log_suspicious_activity_custom(f"High Memory usage: {mem_usage}%")
                    self.show_warning("⚠️ System memory is nearly full.\nClose background apps.")

                time.sleep(5)
        except Exception as e:
            print(f"Resource monitoring error: {e}")
                

    def clear_question_widgets(self):
            if hasattr(self, 'question_frame') and self.question_frame.winfo_exists():
                for widget in self.question_frame.winfo_children():
                    widget.destroy()
            if hasattr(self, 'options_frame') and self.options_frame.winfo_exists():
                for widget in self.options_frame.winfo_children():
                    widget.destroy()
            if hasattr(self, 'nav_frame') and self.nav_frame.winfo_exists():
                self.nav_frame.destroy()

            # Clear navigation frame if it exists
            if hasattr(self, 'nav_frame') and self.nav_frame.winfo_exists():
                self.nav_frame.destroy()


    def next_question(self):
        self.save_current_answer()
        if self.current_question_index < len(self.exam_questions) - 1:
            self.current_question_index += 1
            self.selected_option.set("")  # Clear selection
            self.display_question()

    def prev_question(self):
        self.save_current_answer()
        if self.current_question_index > 0:
            self.current_question_index -= 1
            self.selected_option.set("")  # Clear selection
            self.display_question()

    def save_current_answer(self):
        if not hasattr(self, 'selected_option') or not self.selected_option.get():
            return
        
        try:
            question_data = self.exam_questions[self.current_question_index]
            question_id = question_data['question_id']
            selected_option_index = int(self.selected_option.get())  # 1 to 4

            # Get the actual answer text from the selected option
            options = [
                question_data['option_a'],
                question_data['option_b'],
                question_data['option_c'],
                question_data['option_d']
            ]

            selected_answer = options[selected_option_index - 1]  # actual selected text
            correct_answer = question_data['answer']

            is_correct = (selected_answer.strip().lower() == correct_answer.strip().lower())

            self.cursor.execute("""
                INSERT INTO Student_Answers 
            (student_exam_id, student_id, exam_id, question_id, selected_option, is_correct)
            VALUES (%s, %s, %s, %s, %s, %s)

            """,(self.student_exam_id, self.user_id, self.selected_exam_id, question_id, selected_option_index, is_correct))

            self.conn.commit()

        except Exception as e:
            print(f"Error saving answer: {e}")
            self.conn.rollback()
   
   
    def start_exam_timer(self):
        """Initialize and start the exam timer"""
        # Create timer label if it doesn't exist
        if getattr(self, 'timer_label', None) is None or not self.timer_label.winfo_exists():
            self.timer_label = ctk.CTkLabel(
                self.content,
                text="",
                font=ctk.CTkFont(size=16, weight="bold")
            )
            self.timer_label.pack(pady=10)
        # Start the timer
        self.timer_running = True
        self.update_timer()

    def update_timer(self):
        """Update the timer display each second"""
        if not self.timer_running:
            return

        # Ensure timer_label exists and is not destroyed
        if not hasattr(self, 'timer_label') or self.timer_label is None:
            return
        try:
            if not self.timer_label.winfo_exists():
                return

            if self.remaining_time <= 0:
                self.timer_label.configure(text="⏰ Time's up!")
                self.end_exam()
                return

            minutes, seconds = divmod(self.remaining_time, 60)
            self.timer_label.configure(text=f"⏰ Time Left: {minutes:02d}:{seconds:02d}")
            self.remaining_time -= 1

            self.timer_id = self.app.after(1000, self.update_timer)
        except Exception as e:
            print(f"Timer update error: {e}")

    def monitor_screen_activity(self):
        """Check foreground app and suspicious processes"""
        try:
            while getattr(self, "monitoring_active", False):
                try:
                    active_window = gw.getActiveWindow()
                    window_title = active_window.title if active_window else "Unknown"

                    # Check for restricted apps in the title
                    if any(app.lower() in window_title.lower() for app in self.restricted_apps):
                        self.log_suspicious_activity_custom(f"Restricted app detected: {window_title}")
                        self.show_warning(f"⚠️ Forbidden application detected:\n{window_title}")

                    # Check for restricted processes
                    for proc in psutil.process_iter(['name']):
                        try:
                            pname = proc.info['name'].lower()
                            if any(app.lower() in pname for app in self.restricted_apps):
                                self.log_suspicious_activity_custom(f"Restricted process running: {pname}")
                                self.show_warning(f"⚠️ Forbidden process detected:\n{pname}")
                        except:
                            continue

                except Exception as e:
                    print(f"Screen monitoring error: {e}")
                time.sleep(2)
        except Exception as e:
            print(f"Activity monitoring exception: {e}")
        
    def monitor_student(self):
        try:
            while self.monitoring_active and self.cap and self.cap.isOpened():
                ret, frame = self.cap.read()
                if not ret:
                    continue

                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                face_locations = face_recognition.face_locations(rgb_frame)
                
                 # === 🧠 1. Multiple Face Detection ===
                if len(face_locations) > 1 and not self.multiple_face_flag:
                    self.multiple_face_flag = True
                    self.log_suspicious_activity_custom("Multiple faces detected")
                    self.app.after(0, lambda: self.show_warning("⚠️ Multiple faces detected! Exam violation logged."))
                elif len(face_locations) <= 1:
                    self.multiple_face_flag = False

                # 🧠 Check face presence
                if len(face_locations) == 0:
                    self.missing_face_counter += 1
                    if self.missing_face_counter > self.max_missing_face:
                        self.missing_face_counter = 0  # Reset so popup doesn't loop rapidly
                        # 🔐 Safe warning call (only if app still exists)
                        if hasattr(self, "app") and self.app.winfo_exists():
                            self.log_suspicious_activity_custom("Face not detected for prolonged period")
                            self.app.after(0, lambda: self.show_warning("Face not detected. Please stay in front of the camera."))
                else:
                    self.missing_face_counter = 0

                # 📷 Show camera frame safely using after()
                if hasattr(self, "app") and self.app.winfo_exists():
                    resized_frame = cv2.resize(rgb_frame, (320, 240))
                    img = Image.fromarray(resized_frame)
                    imgtk = ctk.CTkImage(light_image=img, dark_image=img, size=(320, 240))
                    self.app.after(0, lambda img=imgtk: self.update_camera_feed(img))

                time.sleep(0.15)  # ⏱️ Adjust delay for smooth feed

        except Exception as e:
            print(f"Monitoring error: {e}")

        finally:
            if hasattr(self, 'cap') and self.cap:
                self.cap.release()

         
                
    def log_suspicious_activity_custom(self, description):
        try:
            self.cursor.execute("""
                INSERT INTO Suspicious_Activities 
                (student_exam_id, activity_description, severity) 
                VALUES (%s, %s, %s)
            """, (self.student_exam_id, description, "high"))
            self.conn.commit()
        except Exception as e:
            print(f"Error logging screen activity: {e}")
            
    def monitor_keystrokes(self):
        def on_press(key):
            try:
                if key == keyboard.Key.print_screen:
                    self.log_suspicious_activity_custom("PrintScreen key detected")
                    self.show_warning("⚠️ Screenshot attempt detected!")

                elif key == keyboard.Key.alt_l or key == keyboard.Key.alt_r:
                    self.alt_pressed = True

                elif key == keyboard.Key.tab and getattr(self, "alt_pressed", False):
                    self.log_suspicious_activity_custom("Alt+Tab detected")
                    self.show_warning("⚠️ App switching attempt (Alt+Tab)")

                elif hasattr(key, 'char'):
                    if key.char.lower() == 'c' and getattr(self, "ctrl_pressed", False):
                        self.log_suspicious_activity_custom("Ctrl+C (copy) detected")
                        self.show_warning("⚠️ Copy attempt (Ctrl+C)")

                    if key.char.lower() == 'v' and getattr(self, "ctrl_pressed", False):
                        self.log_suspicious_activity_custom("Ctrl+V (paste) detected")
                        self.show_warning("⚠️ Paste attempt (Ctrl+V)")
            except:
                pass

        def on_release(key):
            if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
                self.ctrl_pressed = False
            elif key == keyboard.Key.alt_l or key == keyboard.Key.alt_r:
                self.alt_pressed = False   
                
        self.ctrl_pressed = False
        self.alt_pressed = False

            # Listener thread
        with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
         listener.join()



    def update_camera_feed(self, imgtk):
        if hasattr(self, 'camera_frame') and self.camera_frame.winfo_exists():
         self.camera_frame.configure(image=imgtk)
         self.camera_frame.image = imgtk  # Keep reference

    def show_warning(self, message):
        if not hasattr(self, "app") or not self.app.winfo_exists():
            return

        if self.warning_popup_open:
            return  # ⚠️ Prevent multiple popups

        self.warning_popup_open = True  # 🚨 Lock the popup

        try:
            warning_window = ctk.CTkToplevel(self.app)
            warning_window.title("Warning")
            warning_window.geometry("400x200")
            warning_window.grab_set()
            warning_window.attributes("-topmost", True)  # Optional: bring to front

            label = ctk.CTkLabel(warning_window, text=f"⚠️ {message}", font=ctk.CTkFont(size=14))
            label.pack(pady=40)

            def close_popup():
                warning_window.destroy()
                self.warning_popup_open = False  # 🔓 Unlock after close

            btn = ctk.CTkButton(warning_window, text="I Understand", command=close_popup)
            btn.pack(pady=10)

            warning_window.protocol("WM_DELETE_WINDOW", close_popup)  # 🧹 If window is closed by X button
            self.app.after(5000, close_popup)
            
        except Exception as e:
            print(f"Warning display error: {e}")
            self.warning_popup_open = False




    def calculate_score(self):
        """Calculate total marks obtained vs total possible marks"""
        try:
            # Get total possible marks
            self.cursor.execute("""
                SELECT SUM(marks) AS total FROM Questions 
                WHERE exam_id = %s
            """, (self.selected_exam_id,))
            total_row = self.cursor.fetchone()
            total_marks = total_row['total'] if total_row and total_row['total'] else 0

            # Get marks obtained
            self.cursor.execute("""
                SELECT SUM(q.marks) AS obtained
                FROM Student_Answers sa
                JOIN Questions q ON sa.question_id = q.question_id
                WHERE sa.student_exam_id = %s AND sa.is_correct = TRUE
            """, (self.student_exam_id,))
            obtained_row = self.cursor.fetchone()
            marks_obtained = obtained_row['obtained'] if obtained_row and obtained_row['obtained'] else 0

            if total_marks > 0:
                return round((marks_obtained / total_marks) * 100)
            return 0
        except Exception as e:
            print(f"Error calculating score: {e}")
            return 0



    def end_exam(self):
        """Handle exam completion and result calculation"""
        self.monitoring_active = False
        self.save_current_answer()  # Save final question
        
        if self.cap:
            self.cap.release()
        
        # Calculate score
        score = self.calculate_score()
        print(f"Final calculated score: {score}%")  # Debug
        
        end_time = datetime.datetime.now()
        time_taken = (end_time - self.exam_start_time).total_seconds() / 60
        
        # Determine status
        status = "pass" if score >= 50 else "fail"
        print(f"Exam status: {status}")  # Debug
        
        # Store result
        try:
            self.cursor.execute("""
                INSERT INTO Exam_Results 
                (student_exam_id, score, status, time_taken_minutes) 
                VALUES (%s, %s, %s, %s)
            """, (self.student_exam_id, score, status, time_taken))
            self.conn.commit()
            print("Results saved to database")  # Debug
        except Exception as e:
            print(f"Error saving results: {e}")
            self.conn.rollback()
        
        log_event("Exam Completed", f"Student {self.user_id} completed exam {self.selected_exam_id} with score {score}%", 
                 self.cursor, self.conn)
        
        # Show result
        self.clear_content()
        result_text = f"""
        🎉 Exam Completed!
        
        Your score: {score}%
        Status: {status.capitalize()}
        Time taken: {round(time_taken, 2)} minutes
        
        You can view detailed results in the 'View Results' section.
        """
        self.main_display.configure(text=result_text)
        self.timer_running = False


    def view_results(self):
        if not hasattr(self, 'clear_content'):
            self.clear_content = lambda: None  # Fallback if not defined

        self.clear_content()
        try:
            self.cursor.execute("""
                SELECT E.exam_name, ER.score, ER.status, ER.time_taken_minutes, E.exam_id
                FROM Exam_Results ER
                JOIN Student_Exams SE ON ER.student_exam_id = SE.student_exam_id
                JOIN Exams E ON SE.exam_id = E.exam_id
                WHERE SE.user_id = %s
            """, (self.user_id,))
            results = self.cursor.fetchall()

            if not results:
                self.main_display.configure(text="🚫 No exam results found.")
                return

            result_text = "📊 Your Exam Results:\n\n"
            for row in results:
                result_text += f"""Exam: {row['exam_name']} (ID: {row['exam_id']})
                Score: {row['score']}%
                Status: {row['status'].capitalize()}
                Time Taken: {round(row['time_taken_minutes'], 1)} minutes
                --------------------------\n"""

            self.main_display.configure(text=result_text)

        except Exception as e:
            self.main_display.configure(text=f"Error loading results: {str(e)}")


    def clear_question_widgets(self):
        """Clear all question-related widgets"""
        if hasattr(self, 'question_frame') and self.question_frame.winfo_exists():
            for widget in self.question_frame.winfo_children():
                widget.destroy()
            self.question_frame.pack_forget()
        
        if hasattr(self, 'options_frame') and self.options_frame.winfo_exists():
            for widget in self.options_frame.winfo_children():
                widget.destroy()
            self.options_frame.pack_forget()
            
    def clear_content(self):
        for widget in self.content.winfo_children():
            if widget not in [self.main_display, self.camera_frame]:
                try:
                    widget.destroy()
                except:
                    pass
        self.main_display.configure(text="")

    def logout(self):
        # Set monitoring flag to False
        self.monitoring_active = False
        
        # Cancel any pending timer updates
        if hasattr(self, 'app'):
            try:
                if hasattr(self, 'timer_id'):
                    self.app.after_cancel(self.timer_id)
            except:
                pass
        
        # Release webcam if exists
        if hasattr(self, 'cap') and self.cap:
            self.cap.release()
        
        # Close database connection if exists
        if hasattr(self, 'conn'):
            try:
                # Consume any unread results
                while self.cursor.nextset():
                    pass
                self.conn.close()
            except Exception as e:
                print(f"Error closing connection: {e}")
        
        # Destroy the app window
        if hasattr(self, 'app'):
            try:
                self.app.destroy()
            except:
                pass

            
        def __del__(self):
            self.logout()