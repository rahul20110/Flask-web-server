from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4


from cryptography import x509
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes

from cryptography.x509.name import NameOID
from cryptography.x509 import CertificateBuilder
from datetime import datetime, timezone, timedelta

import socket
import struct
import time

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch


SERVER = "time.google.com"


def get_ntp_time():
    consumer = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    data = b'\x1b' + 47 * b'\0'
    consumer.sendto(data, (SERVER, 123))
    data, address = consumer.recvfrom(1024)
    if data:
        response = struct.unpack('!12I', data)[10]
        response -= 2208988800
        return time.ctime(response)
    

def sign_document(private_key, document):
    signature = private_key.sign(
        document,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    return signature


def verify_signature(public_key, signature, document):
    try:
        public_key.verify(
            signature,
            document,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return True
    except:
        return False
    
if __name__ == '__main__':
    pass