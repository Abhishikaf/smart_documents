
import base64
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

def password_to_key(pw):
    password=bytes(pw, 'utf-8')

    # encrypt/decrypt require the same salt
    # Which means saving the salt somewhere like .env
    # But for demo purposes, we won't bother...

    # salt is 64-128 bits
    # salt = os.urandom(16)
    salt = b"0123456789abcdef"
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=390000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password))

    return key

def encrypt_data(data, password):
    key = password_to_key(password)
    f = Fernet(key)
    encrypted_data = f.encrypt(data)

    return encrypted_data

def decrypt_data(data, password):
    key = password_to_key(password)
    f = Fernet(key)
    decrypted_data = f.decrypt(data)

    return decrypted_data

def encrypt_file(file_name, new_name, password):
    key = password_to_key(password)
    f = Fernet(key)
    with open(file_name, 'rb') as file_orig:
        orig = file_orig.read()

    encrypted = f.encrypt(orig)
    with open(new_name, 'wb') as enc_file:
        enc_file.write(encrypted)


def decrypt_file(file_name, new_name, password):
    key = password_to_key(password)
    f = Fernet(key)
    with open(file_name, 'rb') as file_orig:
        encrypted = file_orig.read()

    decrypted = f.decrypt(encrypted)
    with open(new_name, 'wb') as decrypted_file:
        decrypted_file.write(decrypted)



