from flask import Blueprint, request, jsonify
from database.db import create_connection

exam_bp = Blueprint('exam', __name__)

@exam_bp.route('/schedule_exam', methods=['POST'])
def schedule_exam():
    data = request.json
    required = ['exam_name', 'subject', 'start_time', 'end_time', 'student_id']
    
    for field in required:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400

    try:
        conn = create_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO Exams (exam_name, subject, start_time, end_time)
            VALUES (%s, %s, %s, %s)
        """, (data['exam_name'], data['subject'], data['start_time'], data['end_time']))
        
        exam_id = cursor.lastrowid

        cursor.execute("""
            INSERT INTO Student_Exams (user_id, exam_id)
            VALUES (%s, %s)
        """, (data['student_id'], exam_id))

        conn.commit()
        return jsonify({'message': 'Exam scheduled successfully'}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500

    finally:
        if 'conn' in locals() and conn.is_connected():
            conn.close()

@exam_bp.route('/get_exam/<int:student_id>', methods=['GET'])
def get_exam(student_id):
    try:
        conn = create_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT e.exam_id, e.exam_name, e.subject, e.start_time, e.end_time
            FROM Exams e
            JOIN Student_Exams se ON e.exam_id = se.exam_id
            WHERE se.user_id = %s
        """, (student_id,))

        exams = cursor.fetchall()

        if not exams:
            return jsonify({"message": "No exams found."}), 404

        return jsonify({"student_id": student_id, "exams": exams}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

    finally:
        if 'conn' in locals() and conn.is_connected():
            conn.close()
