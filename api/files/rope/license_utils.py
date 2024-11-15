from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import logging
import requests
import hashlib
import uuid
import winreg
import platform
import wmi
import base64
from cryptography.fernet import Fernet
import os
import pytz

# 首先定义基础路径
BASE_DIR = Path(__file__).resolve().parent.parent
TOOLS_DIR = BASE_DIR / 'tools'
LICENSE_FILE = TOOLS_DIR / 'license.enc'
REG_PATH = r"SOFTWARE\LiveFaceX"
REG_NAME = "InstallID"

# 确保目录存在
TOOLS_DIR.mkdir(parents=True, exist_ok=True)

# 设置日志
logging.basicConfig(level=logging.DEBUG)

# 添加文件日志
log_file = TOOLS_DIR / 'license.log'
file_handler = logging.FileHandler(log_file)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logging.getLogger().addHandler(file_handler)

# 从环境变量或配置获取 API key
try:
    from rope.config import CONFIG
    LEMONSQUEEZY_API_KEY = os.getenv('LEMONSQUEEZY_API_KEY') or CONFIG.get('api_key')
except ImportError:
    LEMONSQUEEZY_API_KEY = os.getenv('LEMONSQUEEZY_API_KEY')

# 从环境变量获取是否允许测试模式
ALLOW_TEST_MODE = os.getenv('ALLOW_TEST_MODE', 'false').lower() == 'true'

def get_hardware_id():
    """获取硬件唯一标识"""
    try:
        c = wmi.WMI()
        
        # 获取CPU信息
        cpu_info = c.Win32_Processor()[0]
        cpu_id = cpu_info.ProcessorId.strip()
        
        # 获取主板序列号
        board_info = c.Win32_BaseBoard()[0]
        board_id = board_info.SerialNumber.strip()
        
        # 获取BIOS信息
        bios_info = c.Win32_BIOS()[0]
        bios_id = bios_info.SerialNumber.strip()
        
        # 组合硬件信息并生成唯一标识
        hardware_str = f"{cpu_id}:{board_id}:{bios_id}"
        return hashlib.sha256(hardware_str.encode()).hexdigest()
    except Exception as e:
        logging.error(f"Error getting hardware ID: {e}")
        return None

def store_in_registry(key, value):
    """将信息存储到注册表"""
    try:
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, REG_PATH) as registry_key:
            winreg.SetValueEx(registry_key, key, 0, winreg.REG_SZ, value)
        return True
    except Exception as e:
        logging.error(f"Error storing in registry: {e}")
        return False

def read_from_registry(key):
    """从注册表读取信息"""
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0, winreg.KEY_READ) as registry_key:
            value, _ = winreg.QueryValueEx(registry_key, key)
            return value
    except Exception:
        return None

def encrypt_data(data):
    """加密数据"""
    try:
        key = Fernet.generate_key()
        cipher_suite = Fernet(key)
        encrypted_data = cipher_suite.encrypt(json.dumps(data).encode())
        return base64.b64encode(key).decode(), base64.b64encode(encrypted_data).decode()
    except Exception as e:
        logging.error(f"Error encrypting data: {e}")
        return None, None

def decrypt_data(key, encrypted_data):
    """解密数据"""
    try:
        cipher_suite = Fernet(base64.b64decode(key.encode()))
        decrypted_data = cipher_suite.decrypt(base64.b64decode(encrypted_data.encode()))
        return json.loads(decrypted_data.decode())
    except Exception as e:
        logging.error(f"Error decrypting data: {e}")
        return None

def validate_activation_code(activation_code):
    """使用 Lemonsqueezy API 验证激活码"""
    try:
        if not activation_code:
            return None
            
        # 获取硬件ID
        hardware_id = get_hardware_id()
        if not hardware_id:
            return None
            
        # 使用 Lemonsqueezy API 验证激活码
        headers = {
            'Authorization': f'Bearer {LEMONSQUEEZY_API_KEY}',
            'Accept': 'application/json'
        }
        
        # 验证许可密钥
        validate_url = 'https://api.lemonsqueezy.com/v1/licenses/validate'
        validate_data = {'license_key': activation_code}
        
        response = requests.post(validate_url, json=validate_data, headers=headers)
        logging.debug(f"License validation response: {response.text}")
        
        if not response.ok:
            logging.error(f"License validation failed: {response.text}")
            return None
            
        license_data = response.json()
        
        # 检查许可证状态
        if not license_data.get('valid'):
            logging.error("License is not valid")
            return None
            
        # 获取许可证详细信息
        license_key_data = license_data.get('license_key', {})
        
        # 检查是否为测试模式 - 开发环境可以注释这段代码
        if not ALLOW_TEST_MODE and license_key_data.get('test_mode'):
            logging.error("License is in test mode")
            return None
        
        # 激活许可证
        activate_url = 'https://api.lemonsqueezy.com/v1/licenses/activate'
        activate_data = {
            'license_key': activation_code,
            'instance_name': hardware_id
        }
        
        activate_response = requests.post(activate_url, json=activate_data, headers=headers)
        logging.debug(f"License activation response: {activate_response.text}")
        
        if not activate_response.ok:
            logging.error(f"License activation failed: {activate_response.text}")
            return None
            
        # 设置许可证有效期
        # 使用 UTC 时间作为基准
        generation_date = datetime.now(timezone.utc)
        
        # 从 license_key_data 中获取过期时间
        if 'expires_at' in license_key_data:
            # 将 UTC 时间字符串转换为 datetime 对象
            expires_at = license_key_data['expires_at'].replace('Z', '+00:00')
            expiration_date = datetime.fromisoformat(expires_at)
            
            # 确保时间是 UTC 时间
            if expiration_date.tzinfo is None:
                expiration_date = pytz.UTC.localize(expiration_date)
            
            # 转换为用户本地时间
            local_tz = datetime.now().astimezone().tzinfo
            expiration_date = expiration_date.astimezone(local_tz)
            generation_date = generation_date.astimezone(local_tz)
            
            # 去除时区信息，保持本地时间
            expiration_date = expiration_date.replace(tzinfo=None)
            generation_date = generation_date.replace(tzinfo=None)
            
            logging.info(f"UTC expiration: {expires_at}")
            logging.info(f"Local expiration: {expiration_date}")
        else:
            # 如果没有过期时间，使用本地时间
            generation_date = datetime.now()
            expiration_date = generation_date + timedelta(days=30)
        
        logging.info(f"License validated successfully. Expires at: {expiration_date}")
        return generation_date, expiration_date
        
    except requests.exceptions.RequestException as e:
        logging.error(f"Network error: {e}")
        raise LicenseValidationError("网络连接失败")
    except json.JSONDecodeError:
        logging.error("Invalid API response")
        raise LicenseValidationError("服务器响应无效")

def save_license_info(activation_code, generation_date, expiration_date):
    """保存许可证信息"""
    try:
        TOOLS_DIR.mkdir(parents=True, exist_ok=True)
        
        # 获取硬件ID
        hardware_id = get_hardware_id()
        if not hardware_id:
            raise Exception("无法获取硬件信息")
        
        # 准备许可证信息，确保日期格式统一
        license_info = {
            "activation_code": activation_code,
            "hardware_id": hardware_id,
            "generation_date": generation_date.strftime("%Y-%m-%d"),
            "expiration_date": expiration_date.strftime("%Y-%m-%d"),
            "timezone": str(datetime.now().astimezone().tzinfo)
        }

        # 加密许可证信息
        key, encrypted_data = encrypt_data(license_info)
        if not key or not encrypted_data:
            raise Exception("加密许可证信息失败")

        # 保存到文件
        with open(LICENSE_FILE, 'w') as f:
            json.dump({
                "key": key,
                "data": encrypted_data
            }, f)
            
        # 保存到注册表
        if not store_in_registry(REG_NAME, hardware_id):
            raise Exception("保存注册表信息失败")
            
    except Exception as e:
        logging.error(f"Error saving license info: {e}")
        raise

def check_license():
    """检查许可证是否有效"""
    try:
        if not LICENSE_FILE.exists():
            return False

        # 检查硬件ID
        current_hardware_id = get_hardware_id()
        if not current_hardware_id:
            return False

        # 检查注册表
        stored_hardware_id = read_from_registry(REG_NAME)
        if not stored_hardware_id or stored_hardware_id != current_hardware_id:
            return False

        # 读取并解密许可证信息
        with open(LICENSE_FILE, 'r') as f:
            encrypted_license = json.load(f)
            
        license_info = decrypt_data(encrypted_license['key'], encrypted_license['data'])
        if not license_info:
            return False

        # 验证硬件ID
        if license_info['hardware_id'] != current_hardware_id:
            return False

        # 验证过期时间，使用相同的日期格式
        expiration_date = datetime.strptime(license_info['expiration_date'], "%Y-%m-%d")
        if expiration_date < datetime.now():
            return False

        return True
        
    except Exception as e:
        logging.error(f"Error checking license: {e}")
        return False

def get_remaining_days():
    """获取剩余天数"""
    try:
        if not LICENSE_FILE.exists():
            return 0

        # 读取并解密许可证信息
        with open(LICENSE_FILE, 'r') as f:
            encrypted_license = json.load(f)
            
        license_info = decrypt_data(encrypted_license['key'], encrypted_license['data'])
        if not license_info:
            return 0
        
        expiration_date = datetime.strptime(license_info['expiration_date'], "%Y-%m-%d")
        remaining = expiration_date - datetime.now()
        return max(0, remaining.days)
        
    except Exception as e:
        logging.error(f"Error getting remaining days: {e}")
        return 0

# 导出需要的函数
__all__ = [
    'validate_activation_code',
    'save_license_info',
    'check_license',
    'get_remaining_days',
]
