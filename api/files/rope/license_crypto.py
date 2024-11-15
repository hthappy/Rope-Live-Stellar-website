from pathlib import Path
import os
from cryptography.fernet import Fernet
import base64
import json

BASE_DIR = Path(__file__).resolve().parent.parent
LICENSE_KEY_PATH = BASE_DIR / 'tools' / 'license.key'
LICENSE_ENC_PATH = BASE_DIR / 'tools' / 'license.enc'

# 使用一个固定的字符串作为密钥
# 注意：在实际应用中，应该使用更安全的方法来管理这个密钥
SECRET_KEY = b'a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6'  # 32字节长的字符串

def get_fernet_key():
    return base64.urlsafe_b64encode(SECRET_KEY)

def load_key():
    if not os.path.exists(LICENSE_KEY_PATH):
        return generate_key()
    with open(LICENSE_KEY_PATH, 'rb') as key_file:
        key = key_file.read()
    return key

# 使用这个函数来获取密钥，它会在需要时生成新的密钥
def get_or_create_key():
    return load_key()

# 加密函数
def encrypt_data(data):
    key = get_or_create_key()
    f = Fernet(key)
    return f.encrypt(data.encode())

# 解密函数
def decrypt_data(encrypted_data):
    key = get_or_create_key()
    f = Fernet(key)
    return f.decrypt(encrypted_data).decode()

def save_encrypted_license(license_info):
    encrypted_data = encrypt_data(json.dumps(license_info))
    os.makedirs(os.path.dirname(LICENSE_ENC_PATH), exist_ok=True)
    with open(LICENSE_ENC_PATH, 'wb') as f:
        f.write(encrypted_data)

def load_decrypted_license():
    if not os.path.exists(LICENSE_ENC_PATH):
        print("License file does not exist")
        return None
    
    try:
        with open(LICENSE_ENC_PATH, 'rb') as f:
            encrypted_data = f.read()
        decrypted_data = decrypt_data(encrypted_data)
        license_info = json.loads(decrypted_data)
        return license_info
    except Exception as e:
        print(f"Error loading or decrypting license: {e}")
    return None

def encrypt_license(data):
    f = Fernet(get_fernet_key())
    return f.encrypt(data.encode()).decode()

def decrypt_license(encrypted_data):
    f = Fernet(get_fernet_key())
    try:
        decrypted_data = f.decrypt(encrypted_data.encode())
        return decrypted_data.decode()
    except Exception as e:
        print(f"Decryption error: {type(e).__name__}: {str(e)}")
        return None

def generate_key():
    return Fernet.generate_key()

# 如果需要，可以添加保存和加载加密许可证的函数
def save_encrypted_license(license_data, file_path='license.dat'):
    with open(file_path, 'w') as f:
        f.write(encrypt_license(license_data))

def load_decrypted_license(file_path='license.dat'):
    try:
        with open(file_path, 'r') as f:
            return decrypt_license(f.read())
    except FileNotFoundError:
        return None
