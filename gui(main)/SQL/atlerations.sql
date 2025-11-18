USE SecureExamProctoring;

SET SQL_SAFE_UPDATES = 1;
TRUNCATE TABLE users;

desc users;


SELECT * FROM exams;
	

select* FROM Users;
select* FROM Exams;
ALTER TABLE student_exams AUTO_INCREMENT = 1000;
SET FOREIGN_KEY_CHECKS = 0;

-- Now run your DELETE or UPDATE
DELETE FROM exams WHERE exam_id =1000;
SET FOREIGN_KEY_CHECKS = 1;

select* FROM Student_Exams;
select* FROM Monitoring_Logs;
select* FROM Suspicious_Activities;
select* FROM Exam_Results;


ALTER TABLE users CHANGE password_hash password VARCHAR(255);

SET SQL_SAFE_UPDATES = 1;

delete from USERS where user_id=3;
ALTER TABLE Users ;
delete from users;

SET FOREIGN_KEY_CHECKS = 0;

-- Now run your DELETE or UPDATE
DELETE FROM users WHERE user_id =3;

SET FOREIGN_KEY_CHECKS = 1;




-- Admin user
INSERT INTO Exams (exam_name, subject, start_time, end_time)
VALUES 
('Math Midterm', 'Mathematics', '2025-04-10 10:00:00', '2025-04-10 12:00:00'),
('Physics Final', 'Physics', '2025-04-15 14:00:00', '2025-04-15 16:00:00');


INSERT INTO Student_Exams (user_id, exam_id)
VALUES 
(1001, 1),
(1001, 2);


DELETE FROM Exam_Results;
DELETE FROM Suspicious_Activities;
DELETE FROM Monitoring_Logs;
DELETE FROM Student_Exams;
DELETE FROM Exams;
DELETE FROM Users;






ALTER TABLE users AUTO_INCREMENT = 1000;


USE SecureExamProctoring;




ALTER TABLE Exams ADD COLUMN duration_minutes INT;
ALTER TABLE Exam_Results ADD COLUMN time_taken_minutes INT;
ALTER TABLE Exam_Results ADD COLUMN timestamp DATETIME DEFAULT CURRENT_TIMESTAMP;
select * from Exam_Results;
ALTER TABLE Exams ADD COLUMN exam_type VARCHAR(255);




ALTER TABLE results ADD COLUMN exam_id INT;


-- Assuming user_id = 1 is Aman, and exam_id = 1 and 2 are from above
DESCRIBE Exam_Results;
DESCRIBE Student_Exams;
DESCRIBE Users;
DESCRIBE Exams;

SELECT u.email, e.exam_name, r.score, r.status
FROM Exam_Results r
JOIN Student_Exams se ON r.student_exam_id = se.student_exam_id
JOIN Users u ON se.user_id = u.user_id
JOIN Exams e ON se.exam_id = e.exam_id;




SET SQL_SAFE_UPDATES = 0;
SET SQL_SAFE_UPDATES = 1;

drop table Questions;
SET FOREIGN_KEY_CHECKS = 0;
SET FOREIGN_KEY_CHECKS = 1;

SET SESSION wait_timeout = 28800;
SET GLOBAL max_allowed_packet = 268435456;

SHOW TABLES;

-- Rename 'question_text' to 'question'
ALTER TABLE Questions 
CHANGE COLUMN question_text question TEXT NOT NULL;

-- Rename 'opt1' to 'option1'
ALTER TABLE Questions 
CHANGE COLUMN option_a option1 VARCHAR(255) NOT NULL;

-- Repeat for other columns (option2, option3, option4, answer)
ALTER TABLE Questions 
CHANGE COLUMN option_b option2 VARCHAR(255) NOT NULL;

ALTER TABLE Questions 
CHANGE COLUMN option_c option3 VARCHAR(255) NOT NULL;

ALTER TABLE Questions 
CHANGE COLUMN option_d option4 VARCHAR(255) NOT NULL;

ALTER TABLE Questions 
CHANGE COLUMN correct_option answer VARCHAR(255) NOT NULL;


desc questions;






