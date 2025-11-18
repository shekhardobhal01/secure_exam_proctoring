import cv2
import customtkinter as ctk
from PIL import Image, ImageTk
import threading
import datetime
import mysql.connector

# Database Logging Function
def log_event(event_type, details, cursor, conn):
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    sql = "INSERT INTO Monitoring_Logs (log_type, log_details, timestamp) VALUES (%s, %s, %s)"
    values = (event_type, details, timestamp)
    cursor.execute(sql, values)
    conn.commit()

# Main Dashboard Class
class ExamVoltDashboard:
    def __init__(self, user_role):
        self.app = ctk.CTk()
        self.app.geometry("1100x650")
        self.app.title("ExamVolt - Secure Exam Portal")

        self.user_role = user_role
        self.profile_image = None

        self.conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='4080',
            database='SecureExamProctoring'
        )
        self.cursor = self.conn.cursor()

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Header
        self.header = ctk.CTkFrame(self.app, height=60, fg_color="#3498db")
        self.header.pack(side="top", fill="x")
        self.header_label = ctk.CTkLabel(
            self.header,
            text="🎓 Welcome to ExamVolt - Secure Exam Portal",
            text_color="white",
            font=ctk.CTkFont(size=22, weight="bold")
        )
        self.header_label.pack(pady=10)

        # Sidebar
        self.sidebar = ctk.CTkFrame(self.app, width=200, corner_radius=0, fg_color="#2c3e50")
        self.sidebar.pack(side="left", fill="y")

        # Profile picture and Upload button
        self.profile_pic = ctk.CTkLabel(
            self.sidebar, text="Upload\nPhoto", width=100, height=100,
            corner_radius=10, fg_color="#34495e", text_color="white"
        )
        self.profile_pic.pack(pady=15)

        self.upload_btn = ctk.CTkButton(
            self.sidebar, text="Upload Photo", command=self.upload_image,
            fg_color="#3498db", hover_color="#2980b9", text_color="white"
        )
        self.upload_btn.pack(pady=(0, 15), padx=10, fill="x")

        # Camera Feed Frame
        self.camera_frame = ctk.CTkLabel(self.app)
        self.camera_frame.pack(pady=20)

        # Main content frame
        self.content = ctk.CTkFrame(self.app, fg_color="#1e1e1e")
        self.content.pack(side="right", expand=True, fill="both", padx=10, pady=10)
        self.main_display = ctk.CTkLabel(
            self.content,
            text="👈 Choose an option from the menu to get started with ExamVolt.",
            font=ctk.CTkFont(size=16),
            wraplength=600,
            justify="left",
            text_color="white"
        )
        self.main_display.pack(padx=20, pady=20, anchor="nw")

        # Setup face detection and camera feed
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        self.cap = cv2.VideoCapture(0)
        self.missing_face_counter = 0

        self.update_camera_feed()

        # Start the application
        self.app.mainloop()

    def upload_image(self):
        from tkinter import filedialog
        path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg *.png")])
        if path:
            img = Image.open(path).resize((100, 100))
            self.profile_image = ctk.CTkImage(light_image=img, dark_image=img, size=(100, 100))
            self.profile_pic.configure(image=self.profile_image, text="")

    def update_camera_feed(self):
        ret, frame = self.cap.read()
        if ret:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)

            # Handling No Face Detected (Phone use or user moved away)
            if len(faces) == 0:
                self.missing_face_counter += 1
                if self.missing_face_counter >= 30:  # 30 frames without a face detected
                    event_details = "Student might be using a phone or left the screen."
                    print("🚨 Face not detected for long!")
                    threading.Thread(target=log_event, args=("No Face Detected", event_details, self.cursor, self.conn)).start()

            else:
                self.missing_face_counter = 0  # Reset counter if face is detected

                # Handling Multiple Faces Detected (Possibly cheating or others in the room)
                if len(faces) > 1:
                    event_details = f"{len(faces)} faces detected."
                    print(f"🚨 Multiple faces detected: {len(faces)}")
                    threading.Thread(target=log_event, args=("Multiple Faces Detected", event_details, self.cursor, self.conn)).start()


            # Draw rectangles around faces
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # Convert frame to ImageTk
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            img_tk = ImageTk.PhotoImage(image=img)

            # Update the camera feed in Tkinter window
            self.camera_frame.configure(image=img_tk)
            self.camera_frame.image = img_tk

        # Keep calling update_camera_feed every 10ms to update the frame
        self.app.after(10, self.update_camera_feed)

# Create the instance of the ExamVoltDashboard class and pass the user role
if __name__ == "__main__":
    user_role = "student"  # You can change this as needed
    ExamVoltDashboard(user_role)
