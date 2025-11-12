"""Two-Factor Authentication for Daur-AI v2.0"""
import logging
import secrets
import time
from typing import Optional, Dict, Tuple
from datetime import datetime, timedelta
from enum import Enum
import hashlib
import hmac

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    import pyotp
    PYOTP_AVAILABLE = True
except ImportError:
    PYOTP_AVAILABLE = False
    logger.warning("pyotp not available")

try:
    from twilio.rest import Client
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False
    logger.warning("twilio not available")


class TwoFactorMethod(Enum):
    TOTP = "totp"
    SMS = "sms"
    EMAIL = "email"
    BACKUP_CODES = "backup_codes"


class TOTPAuthenticator:
    def __init__(self, user_id: int):
        if not PYOTP_AVAILABLE:
            raise ImportError("pyotp is required")
        
        self.user_id = user_id
        self.secret = pyotp.random_base32()
        self.totp = pyotp.TOTP(self.secret)
    
    def get_provisioning_uri(self, issuer_name: str = "Daur-AI") -> str:
        return self.totp.provisioning_uri(
            name=f"user_{self.user_id}",
            issuer_name=issuer_name
        )
    
    def verify_token(self, token: str) -> bool:
        try:
            return self.totp.verify(token)
        except Exception as e:
            logger.error(f"Error verifying TOTP: {e}")
            return False
    
    def get_secret(self) -> str:
        return self.secret


class SMSAuthenticator:
    def __init__(self, account_sid: str, auth_token: str, from_number: str):
        if not TWILIO_AVAILABLE:
            raise ImportError("twilio is required")
        
        self.client = Client(account_sid, auth_token)
        self.from_number = from_number
        self.codes: Dict[str, Dict] = {}
    
    def send_code(self, phone_number: str) -> bool:
        try:
            code = secrets.randbelow(1000000)
            code_str = str(code).zfill(6)
            
            message = self.client.messages.create(
                body=f"Your Daur-AI verification code is: {code_str}",
                from_=self.from_number,
                to=phone_number
            )
            
            self.codes[phone_number] = {
                "code": code_str,
                "created_at": datetime.now(),
                "attempts": 0
            }
            
            logger.info(f"SMS code sent to {phone_number}")
            return True
        except Exception as e:
            logger.error(f"Error sending SMS: {e}")
            return False
    
    def verify_code(self, phone_number: str, code: str) -> bool:
        if phone_number not in self.codes:
            return False
        
        code_data = self.codes[phone_number]
        
        if code_data["code"] != code:
            code_data["attempts"] += 1
            if code_data["attempts"] >= 3:
                del self.codes[phone_number]
            return False
        
        if datetime.now() - code_data["created_at"] > timedelta(minutes=10):
            del self.codes[phone_number]
            return False
        
        del self.codes[phone_number]
        logger.info(f"SMS code verified for {phone_number}")
        return True


class EmailAuthenticator:
    def __init__(self, smtp_config: Dict):
        self.smtp_config = smtp_config
        self.codes: Dict[str, Dict] = {}
    
    def send_code(self, email: str) -> bool:
        try:
            code = secrets.randbelow(1000000)
            code_str = str(code).zfill(6)
            
            self.codes[email] = {
                "code": code_str,
                "created_at": datetime.now(),
                "attempts": 0
            }
            
            logger.info(f"Email code generated for {email}: {code_str}")
            return True
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return False
    
    def verify_code(self, email: str, code: str) -> bool:
        if email not in self.codes:
            return False
        
        code_data = self.codes[email]
        
        if code_data["code"] != code:
            code_data["attempts"] += 1
            if code_data["attempts"] >= 3:
                del self.codes[email]
            return False
        
        if datetime.now() - code_data["created_at"] > timedelta(minutes=15):
            del self.codes[email]
            return False
        
        del self.codes[email]
        logger.info(f"Email code verified for {email}")
        return True


class BackupCodeGenerator:
    @staticmethod
    def generate_codes(count: int = 10) -> list:
        codes = []
        for _ in range(count):
            code = secrets.token_hex(4).upper()
            codes.append(code)
        return codes
    
    @staticmethod
    def hash_code(code: str) -> str:
        return hashlib.sha256(code.encode()).hexdigest()
    
    @staticmethod
    def verify_code(code: str, hashed: str) -> bool:
        return hashlib.sha256(code.encode()).hexdigest() == hashed


class TwoFactorAuthManager:
    def __init__(self):
        self.user_2fa: Dict[int, Dict] = {}
    
    def enable_totp(self, user_id: int) -> Tuple[str, str]:
        totp = TOTPAuthenticator(user_id)
        uri = totp.get_provisioning_uri()
        
        self.user_2fa[user_id] = {
            "method": TwoFactorMethod.TOTP,
            "secret": totp.get_secret(),
            "enabled": False,
            "created_at": datetime.now()
        }
        
        logger.info(f"TOTP enabled for user {user_id}")
        return uri, totp.get_secret()
    
    def verify_totp(self, user_id: int, token: str) -> bool:
        if user_id not in self.user_2fa:
            return False
        
        user_data = self.user_2fa[user_id]
        if user_data["method"] != TwoFactorMethod.TOTP:
            return False
        
        totp = pyotp.TOTP(user_data["secret"])
        return totp.verify(token)
    
    def enable_sms(self, user_id: int, phone_number: str) -> bool:
        self.user_2fa[user_id] = {
            "method": TwoFactorMethod.SMS,
            "phone_number": phone_number,
            "enabled": False,
            "created_at": datetime.now()
        }
        
        logger.info(f"SMS 2FA enabled for user {user_id}")
        return True
    
    def enable_email(self, user_id: int, email: str) -> bool:
        self.user_2fa[user_id] = {
            "method": TwoFactorMethod.EMAIL,
            "email": email,
            "enabled": False,
            "created_at": datetime.now()
        }
        
        logger.info(f"Email 2FA enabled for user {user_id}")
        return True
    
    def generate_backup_codes(self, user_id: int) -> list:
        codes = BackupCodeGenerator.generate_codes()
        hashed_codes = [BackupCodeGenerator.hash_code(code) for code in codes]
        
        if user_id in self.user_2fa:
            self.user_2fa[user_id]["backup_codes"] = hashed_codes
        
        logger.info(f"Backup codes generated for user {user_id}")
        return codes
    
    def verify_backup_code(self, user_id: int, code: str) -> bool:
        if user_id not in self.user_2fa:
            return False
        
        user_data = self.user_2fa[user_id]
        if "backup_codes" not in user_data:
            return False
        
        for hashed in user_data["backup_codes"]:
            if BackupCodeGenerator.verify_code(code, hashed):
                user_data["backup_codes"].remove(hashed)
                logger.info(f"Backup code verified for user {user_id}")
                return True
        
        return False
    
    def is_2fa_enabled(self, user_id: int) -> bool:
        return user_id in self.user_2fa and self.user_2fa[user_id].get("enabled", False)
    
    def get_2fa_method(self, user_id: int) -> Optional[TwoFactorMethod]:
        if user_id not in self.user_2fa:
            return None
        return self.user_2fa[user_id].get("method")
    
    def disable_2fa(self, user_id: int) -> bool:
        if user_id in self.user_2fa:
            del self.user_2fa[user_id]
            logger.info(f"2FA disabled for user {user_id}")
            return True
        return False
