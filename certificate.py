from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import PyPDF2
# from PyPDF2 import PdfReader, PdfWriter
from cryptography import x509
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
# from cryptography.x509.oid import NameOID
from cryptography.x509.name import NameOID
from cryptography.x509 import CertificateBuilder
from datetime import datetime, timezone, timedelta
import textwrap
import requests
import os
import socket
import struct
import time
import hashlib
import csv
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
# from PyPDF4 import PdfFileReader, PdfFileWriter
from PyPDF4 import PdfFileReader, PdfFileWriter
import textwrap

# Define the directory where the signed documents will be stored
DOCUMENT_DIR = 'documents/'
# Generate the root certificate and key
ROOT_CERT_FILE = 'root.cert'
ROOT_KEY_FILE = 'root.key'
if not os.path.exists(ROOT_CERT_FILE) or not os.path.exists(ROOT_KEY_FILE):
    root_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    name = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, u'Example University'),
    ])
    subject = issuer = name
    root_cert = CertificateBuilder().subject_name(subject).issuer_name(issuer).public_key(root_key.public_key()).serial_number(1000).not_valid_before(datetime.utcnow()).not_valid_after(datetime.utcnow() + timedelta(days=365)).sign(root_key, hashes.SHA256())
    with open(ROOT_KEY_FILE, 'wb') as f:
        f.write(root_key.private_bytes(encoding=serialization.Encoding.PEM, format=serialization.PrivateFormat.PKCS8, encryption_algorithm=serialization.NoEncryption()))
    with open(ROOT_CERT_FILE, 'wb') as f:
        f.write(root_cert.public_bytes(encoding=serialization.Encoding.PEM))


def generate_graduation_certificate(name, roll_number, private_key_registrar, private_key_director):
  
    document_value = name + ".pdf"
    canvas_PDF = canvas.Canvas(document_value)
    canvas_PDF.setPageSize((595.27, 841.89))
    

    # Draw border
    border_margin = 50
    canvas_PDF.rect(border_margin, border_margin, 595.27 - 2 * border_margin, 841.89 - 2 * border_margin)

    # Draw title
    title_x, title_y = 595.27 / 2, 841.89 - 100
    canvas_PDF.setFont('Helvetica-Bold', 20)
    canvas_PDF.drawCentredString(title_x, title_y, "Certificate of Graduation")
    canvas_PDF.setFont('Helvetica', 12)
    # # Draw logo at the top
    # logo_path = "style1colorlarge.png"  # replace with your logo file path
    # logo_width = 100  # adjust as needed
    # logo_height = 50  # adjust as needed
    # logo_x = (595.27 - logo_width) / 2  # center the logo
    # logo_y = title_y - logo_height - 20  # position it just below the title
    # canvas_PDF.drawImage(logo_path, logo_x, logo_y, width=logo_width, height=logo_height)

    
    var_x, var_y = 100, 700
    x_academic_roll, y_academic_roll = 100, 650
    timestamp_x, timestamp_y = 100, 600
    degree_x, degree_y = 100, 550
    signature_x, signature_y = 100, 550

   
    canvas_PDF.drawString(var_x, var_y, f"Name: {name.title()}")
    canvas_PDF.drawString(x_academic_roll, y_academic_roll, f"Roll Number: {roll_number}")
    canvas_PDF.drawString(degree_x, degree_y, f"Degree: Bachelor of Science in Computer Science")
    

   
    timestamp_str = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3] + " UTC"
    canvas_PDF.drawString(timestamp_x, timestamp_y, f"Timestamp: {timestamp_str}")

  
    data_pdf = canvas_PDF.getpdfdata()
    pdf_hash = hashlib.sha256(data_pdf).digest()

   
    signature = private_key_registrar.sign(
        pdf_hash,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )

    director_signature = private_key_director.sign(
        pdf_hash,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )

    
    signature_text = f"Registrar: {signature.hex()} Director: {director_signature.hex()}"

    
    lines = textwrap.wrap(signature_text, width=50)
    for j, line in enumerate(lines):
        y = signature_y - j * 15 
        canvas_PDF.drawString(signature_x, y, line)

    canvas_PDF.save()



   
    watermark_text = f"Issued to {roll_number} on {timestamp_str} by ABC University"
    watermark_file = "label.pdf"
    watermark_canvas = canvas.Canvas(watermark_file, pagesize=letter)
    watermark_canvas.setFont('Helvetica-Bold', 15)
    watermark_canvas.setFillColorRGB(0.5, 0.5, 0.5, 0.2)
    watermark_canvas.rotate(45)
    text_width = watermark_canvas.stringWidth(watermark_text)

    x = -6.5 * inch
    y = 0.5 * inch
    while x < 8.5 * inch:
        watermark_canvas.drawString(x, y, watermark_text)
        x += text_width + 20

    watermark_canvas.save()



  
    pdf_open = PdfFileReader(open(document_value, "rb"))
    pdf_label = PdfFileReader(open(watermark_file, "rb"))
    output = PdfFileWriter()
    for j in range(pdf_open.getNumPages()):
        page = pdf_open.getPage(j)
        page.mergePage(pdf_label.getPage(0))
        output.addPage(page)
    with open(document_value, "wb") as outputStream:
        output.write(outputStream)

    print(f"Certificate for {name} ({roll_number}) has been generated and saved as {document_value}.")

    return signature, director_signature, pdf_hash


def generate_academic_report(name, roll_number, private_key_registrar, private_key_director):
    
    document_value = name + "_gradecard.pdf"
    canvas_PDF = canvas.Canvas(document_value)
    canvas_PDF.setPageSize((595.27, 841.89))
    # Draw border
    border_margin = 50
    canvas_PDF.rect(border_margin, border_margin, 595.27 - 2 * border_margin, 841.89 - 2 * border_margin)

    # Draw title
    title_x, title_y = 595.27 / 2, 841.89 - 100
    canvas_PDF.setFont('Helvetica-Bold', 20)
    canvas_PDF.drawCentredString(title_x, title_y, "Academic Report")
    canvas_PDF.setFont('Helvetica', 12)

   
    var_x, var_y = 100, 700
    x_academic_roll, y_academic_roll = 100, 650
    timestamp_x, timestamp_y = 100, 600
    signature_x, signature_y = 100, 550  
    grade_x, grade_y = 100, 550  

    
    canvas_PDF.drawString(var_x, var_y, f"Name: {name.title()}")
    canvas_PDF.drawString(x_academic_roll, y_academic_roll, f"Roll Number: {roll_number}")
    canvas_PDF.drawString(grade_x, grade_y, f"Grade: X")
    possible_grades = ['A', 'B', 'C', 'D', 'E', 'F']
    possible_courses = ['Mathematics', 'Physics', 'Chemistry', 'Biology', 'Computer Science']
    for i, course in enumerate(possible_courses):
        canvas_PDF.drawString(grade_x, grade_y - (i + 1) * 50, f"{course}: {possible_grades[i % len(possible_grades)]}")


    
    timestamp_str = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3] + " UTC"
    canvas_PDF.drawString(timestamp_x, timestamp_y, f"Timestamp: {timestamp_str}")

   
    data_pdf = canvas_PDF.getpdfdata()
    pdf_hash = hashlib.sha256(data_pdf).digest()

    
    signature = private_key_registrar.sign(
        pdf_hash,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )

    director_signature = private_key_director.sign(
        pdf_hash,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )

  
    signature_text = f"Registrar: {signature.hex()} Director: {director_signature.hex()}"

    
    lines = textwrap.wrap(signature_text, width=50) 
    for j, line in enumerate(lines):
        y = signature_y - j * 15  
        canvas_PDF.drawString(signature_x, y, line)

    canvas_PDF.save()



  
    watermark_text = f"Issued to {roll_number} on {timestamp_str} by ABC University"
    watermark_file = "label.pdf"
    watermark_canvas = canvas.Canvas(watermark_file, pagesize=letter)
    watermark_canvas.setFont('Helvetica-Bold', 15)
    watermark_canvas.setFillColorRGB(0.5, 0.5, 0.5, 0.2)
    watermark_canvas.rotate(45)
    text_width = watermark_canvas.stringWidth(watermark_text)

    x = -6.5 * inch
    y = 0.5 * inch
    while x < 8.5 * inch:
        watermark_canvas.drawString(x, y, watermark_text)
        x += text_width + 20

    watermark_canvas.save()



   
    pdf_open = PdfFileReader(open(document_value, "rb"))
    pdf_label = PdfFileReader(open(watermark_file, "rb"))
    output = PdfFileWriter()
    for j in range(pdf_open.getNumPages()):
        page = pdf_open.getPage(j)
        page.mergePage(pdf_label.getPage(0))
        output.addPage(page)
    with open(document_value, "wb") as outputStream:
        output.write(outputStream)

    print(f"Certificate for {name} ({roll_number}) has been generated and saved as {document_value}.")

    return signature, director_signature, pdf_hash

if __name__ == '__main__':
    pass