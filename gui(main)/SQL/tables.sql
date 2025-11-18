CREATE DATABASE SecureExamProctoring;
USE SecureExamProctoring;

create TABLE Users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    role ENUM('student', 'admin')
);
CREATE TABLE Exams (
    exam_id INT PRIMARY KEY AUTO_INCREMENT,
    exam_name VARCHAR(100) NOT NULL,
    subject VARCHAR(100) NOT NULL,
    start_time DATETIME NOT NULL,
    end_time DATETIME NOT NULL,
    duration_minutes INT,
    exam_type VARCHAR(255)
);
CREATE TABLE Student_Exams (
    student_exam_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    exam_id INT,
    FOREIGN KEY (user_id) REFERENCES Users(user_id),
    FOREIGN KEY (exam_id) REFERENCES Exams(exam_id)
);
CREATE TABLE Monitoring_Logs (
    log_id INT PRIMARY KEY AUTO_INCREMENT,
    student_exam_id INT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    log_type VARCHAR(100) NOT NULL,
    log_details TEXT,
    FOREIGN KEY (student_exam_id) REFERENCES Student_Exams(student_exam_id)
);
CREATE TABLE Suspicious_Activities (
    activity_id INT PRIMARY KEY AUTO_INCREMENT,
    student_exam_id INT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    activity_description TEXT,
    severity ENUM('low', 'medium', 'high'),
    FOREIGN KEY (student_exam_id) REFERENCES Student_Exams(student_exam_id)
);
CREATE TABLE Exam_Results (
    result_id INT PRIMARY KEY AUTO_INCREMENT,
    student_exam_id INT,
    score INT,
    status ENUM('pass', 'fail'),
    time_taken_minutes INT,
    FOREIGN KEY (student_exam_id) REFERENCES Student_Exams(student_exam_id)
);
CREATE TABLE Questions (
    question_id INT AUTO_INCREMENT PRIMARY KEY,
    exam_id INT,
    question TEXT NOT NULL,
    option_a VARCHAR(255),
    option_b VARCHAR(255),
    option_c VARCHAR(255),
    option_d VARCHAR(255),
    answer CHAR(1),
    marks INT DEFAULT 1,
    FOREIGN KEY (exam_id) REFERENCES Exams(exam_id) ON DELETE CASCADE
);
CREATE TABLE Student_Answers (
	student_exam_id INT,
    answer_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT,
    exam_id INT,
    question_id INT,
    selected_option CHAR(1),
    is_correct BOOLEAN,
    FOREIGN KEY (student_id) REFERENCES Users(user_id),
    FOREIGN KEY (exam_id) REFERENCES Exams(exam_id),
    FOREIGN KEY (question_id) REFERENCES Questions(question_id)
);
USE SecureExamProctoring;

select* from exams;


SELECT * FROM users;


























