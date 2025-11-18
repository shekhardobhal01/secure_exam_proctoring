
select * from users;
select * from Exams;
select * from Student_Exams;
select * from Monitoring_Logs;
select * from Suspicious_Activities;
select * from Exam_Results;
SET FOREIGN_KEY_CHECKS = 1;
SET SQL_SAFE_UPDATES = 0;

DELETE FROM exams WHERE exam_id =100;
SET FOREIGN_KEY_CHECKS = 1;
SET SQL_SAFE_UPDATES = 1;
delete from users;
ALTER TABLE Users AUTO_INCREMENT = 1;
ALTER TABLE Exams AUTO_INCREMENT = 1;
ALTER TABLE Student_Exams AUTO_INCREMENT = 1;
ALTER TABLE Monitoring_Logs AUTO_INCREMENT = 1;
ALTER TABLE Suspicious_Activities AUTO_INCREMENT = 1;
ALTER TABLE Exam_Results AUTO_INCREMENT = 1;





