from flask import Blueprint, request, jsonify
from database.db import create_connection

logs_bp = Blueprint('logs', __name__)

@logs_bp.route('/log_activity', methods=['POST'])
def log_activity():
    data = request.json
    required = ['student_exam_id', 'log_type', 'log_details']
    for field in required:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400

    valid_log_types = ['face_detection', 'keystroke', 'screen_activity']
    if data['log_type'] not in valid_log_types:
        return jsonify({'error': f'Invalid log_type. Must be one of {valid_log_types}'}), 400

    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Monitoring_Logs (student_exam_id, log_type, log_details)
            VALUES (%s, %s, %s)
        """, (data['student_exam_id'], data['log_type'], data['log_details']))
        conn.commit()
        return jsonify({'message': 'Activity log saved'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if 'conn' in locals() and conn.is_connected():
            conn.close()

@logs_bp.route('/get_logs/<int:student_id>', methods=['GET'])
def get_logs(student_id):
    try:
        conn = create_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT ml.*
            FROM Monitoring_Logs ml
            JOIN Student_Exams se ON ml.student_exam_id = se.student_exam_id
            WHERE se.user_id = %s
        """, (student_id,))
        logs = cursor.fetchall()

        if not logs:
            return jsonify({'message': 'No logs found'}), 404
        return jsonify({'logs': logs}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if 'conn' in locals() and conn.is_connected():
            conn.close()
