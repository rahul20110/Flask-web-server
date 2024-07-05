from flask import Flask, redirect, request, send_file, render_template, url_for
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

from cryptography import x509
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.x509.name import NameOID
from cryptography.x509 import CertificateBuilder
from datetime import datetime, timezone, timedelta

import os

import csv
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch


from registration import save_registration_details
from utils import *
import os
from certificate import generate_graduation_certificate, generate_academic_report

NTP_SERVER = "time.google.com"

app = Flask(__name__)
app.debug = True

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        student_full_name = request.form['graduate_name']
        student_roll_no = request.form['roll_number']
        student_phone_no = request.form['phone_number']
        student_dob = request.form['dob']
        password_hash = request.form['hashed_password']

        save_registration_details(student_full_name, student_roll_no, student_phone_no, student_dob, password_hash)

        return "Registration successful!"
    else:
        return render_template('registration.html')

@app.route('/', methods=['POST'])
def get_student_info():    
    student_full_name = request.form['graduate_name']
    student_roll_no = request.form['roll_number']
    student_dob = request.form['dob']
    password_hash = request.form['hashed_password']

    print(f"dob: {student_dob}")
    print(f"password: {password_hash}")

    with open('database.csv', mode='r') as file:
        csv_reader = csv.reader(file)
        found = False
        for csv_row in csv_reader:
            print(csv_row)
            if csv_row[1] == student_roll_no and csv_row[0] == student_full_name.lower() and csv_row[2] == student_dob:
                found = True
                print(csv_row[4])
                print(password_hash)
                if csv_row[4].strip() == password_hash:
                    registrar_private_key_crypto = rsa.generate_private_key(public_exponent=65537, key_size=2048)
                    registrar_public_key_crypto = registrar_private_key_crypto.public_key()

                    director_private_key_crypto = rsa.generate_private_key(public_exponent=65537, key_size=2048)
                    director_public_key_crypto = director_private_key_crypto.public_key()

                    print(csv_row[4] == password_hash)
                    sign_reg, sign_dir, hashed_pdf = generate_graduation_certificate(student_full_name, student_roll_no, registrar_private_key_crypto, director_private_key_crypto)
                    signature_registrar_grade, signature_director_grade, pdf_hash_grade = generate_academic_report(student_full_name, student_roll_no, registrar_private_key_crypto, director_private_key_crypto)

                    check_registrar = verify_signature(registrar_public_key_crypto, sign_reg, hashed_pdf)
                    check_director = verify_signature(director_public_key_crypto, sign_dir, hashed_pdf)

                    if check_registrar and check_director:
                        print("Document is digitally signed by both Registrar and Director")
                        return render_template('download_files.html', degree_name=f"{student_full_name}.pdf", grade_name=f"{student_full_name}_gradecard.pdf")

                    else:
                        print("Document signature is invalid")
                        return "Document signature is invalid"

                else:
                    return "Authentication Failed: Incorrect Password"
        if not found:
            return "Authentication Failed: Roll Number not found in the database"

@app.route('/download/<filename>', methods=['GET'])
def download_pdf(filename):
    file_path = f"{filename}"
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return "Error: File not found"

if __name__ == '__main__':
    app.run(port=8080)