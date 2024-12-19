from flask import Flask, request, jsonify, render_template, redirect, url_for
from werkzeug.utils import secure_filename
import sqlite3
import os

app = Flask(__name__)

# Configure upload folder and allowed extensions
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the uploads folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# SQLite database setup
def init_db():
    conn = sqlite3.connect("admissions.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS students (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        guardian_name TEXT NOT NULL,
                        guardian_phone TEXT NOT NULL,
                        student_phone TEXT,
                        dob TEXT NOT NULL,
                        address TEXT NOT NULL,
                        class TEXT NOT NULL,
                        subjects TEXT,
                        photo_path TEXT,
                        fees REAL NOT NULL
                    )''')
    conn.commit()
    conn.close()

init_db()

# Subject fees structure
SUBJECT_FEES = {
    "bengali": 500,
    "history": 400,
    "geography": 450,
    "sanskrit": 350,
    "english": 600,
    "computer": 700
}

# Utility function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Calculate total fees based on subjects
def calculate_fees(selected_subjects):
    return sum(SUBJECT_FEES.get(subject.strip().lower(), 0) for subject in selected_subjects)

# Route: Home Page
@app.route('/')
def home():
    return "<h1>Welcome to the Admission Server</h1><p>Use the API to submit or manage admissions.</p>"

# Route: Submit Admission
@app.route('/submit', methods=['POST'])
def submit_admission():
    try:
        # Get form data
        name = request.form['name']
        guardian_name = request.form['guardian-name']
        guardian_phone = request.form['guardian-phone']
        student_phone = request.form.get('student-phone', '')
        dob = request.form['dob']
        address = request.form['address']
        class_name = request.form['class']
        selected_subjects = request.form.getlist('subjects')
        subjects = ", ".join(selected_subjects)

        # Calculate total fees
        fees = calculate_fees(selected_subjects)

        # Handle photo upload
        photo = request.files.get('photo')
        photo_path = None
        if photo and allowed_file(photo.filename):
            filename = secure_filename(photo.filename)
            photo_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            photo.save(photo_path)

        # Save to database
        conn = sqlite3.connect("admissions.db")
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO students (name, guardian_name, guardian_phone, student_phone, dob, address, class, subjects, photo_path, fees)
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                       (name, guardian_name, guardian_phone, student_phone, dob, address, class_name, subjects, photo_path, fees))
        conn.commit()
        conn.close()

        return jsonify({"message": "Admission submitted successfully!", "fees": fees}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route: Admin View (List All Students)
@app.route('/admin', methods=['GET'])
def admin_view():
    try:
        conn = sqlite3.connect("admissions.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM students")
        students = cursor.fetchall()
        conn.close()

        # Format student data for better readability
        students_list = []
        for student in students:
            students_list.append({
                "id": student[0],
                "name": student[1],
                "guardian_name": student[2],
                "guardian_phone": student[3],
                "student_phone": student[4],
                "dob": student[5],
                "address": student[6],
                "class": student[7],
                "subjects": student[8],
                "photo_path": student[9],
                "fees": student[10]
            })

        # Return data as JSON
        return jsonify({"students": students_list}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
