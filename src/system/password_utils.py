"""Utilities for password hashing with fallback mechanisms."""
import logging
from typing import Optional, Tuple
import hashlib
import os
import base64

logger = logging.getLogger(__name__)

class PasswordHasher:
    """Password hashing utility with bcrypt fallback."""
    
    def __init__(self):
        self.use_bcrypt = False
        try:
            import bcrypt
            self.bcrypt = bcrypt
            self.use_bcrypt = True
            logger.info("Using bcrypt for password hashing")
        except ImportError:
            logger.warning("bcrypt not available, using fallback implementation")
            self.bcrypt = None
    
    def _fallback_gensalt(self, rounds: int = 12) -> bytes:
        """Generate a salt using os.urandom when bcrypt is not available.
        
        Args:
            rounds: Work factor for hash generation (ignored in fallback)
            
        Returns:
            A random salt as bytes
        """
        return os.urandom(16)
    
    def _fallback_hashpw(self, password: bytes, salt: bytes) -> bytes:
        """Fallback password hashing when bcrypt is not available.
        Uses PBKDF2-HMAC-SHA256 with 100,000 iterations.
        
        Args:
            password: The password to hash
            salt: The salt to use
            
        Returns:
            The hashed password
        """
        dk = hashlib.pbkdf2_hmac('sha256', password, salt, 100_000)
        # Format similarly to bcrypt: $2b$rounds$salt+hash
        encoded = base64.b64encode(salt + dk).decode('ascii')
        return f"$2x${encoded}".encode()
    
    def _fallback_checkpw(self, password: bytes, hashed: bytes) -> bool:
        """Check password against hash using fallback implementation.
        
        Args:
            password: The password to check
            hashed: The hashed password to check against
            
        Returns:
            True if password matches, False otherwise
        """
        try:
            # Parse stored hash - format is $2x$salt+hash in base64
            if not hashed.startswith(b'$2x$'):
                return False
            
            decoded = base64.b64decode(hashed[4:])
            salt, stored_dk = decoded[:16], decoded[16:]
            
            # Hash the provided password
            dk = hashlib.pbkdf2_hmac('sha256', password, salt, 100_000)
            return stored_dk == dk
            
        except Exception as e:
            logger.error(f"Error checking password: {e}")
            return False
    
    def gensalt(self, rounds: int = 12) -> bytes:
        """Generate a salt for password hashing.
        
        Args:
            rounds: Work factor for bcrypt (ignored in fallback)
            
        Returns:
            A salt suitable for password hashing
        """
        if self.use_bcrypt:
            return self.bcrypt.gensalt(rounds)
        return self._fallback_gensalt(rounds)
    
    def hashpw(self, password: bytes, salt: Optional[bytes] = None) -> bytes:
        """Hash a password using either bcrypt or fallback implementation.
        
        Args:
            password: The password to hash as bytes
            salt: Optional salt to use, will generate if not provided
            
        Returns:
            The hashed password as bytes
        """
        if not salt:
            salt = self.gensalt()
            
        if self.use_bcrypt:
            return self.bcrypt.hashpw(password, salt)
        return self._fallback_hashpw(password, salt)
    
    def checkpw(self, password: bytes, hashed: bytes) -> bool:
        """Check if a password matches a hash.
        
        Args:
            password: The password to check as bytes
            hashed: The hash to check against as bytes
            
        Returns:
            True if password matches hash, False otherwise
        """
        if self.use_bcrypt and hashed.startswith(b'$2b$'):
            return self.bcrypt.checkpw(password, hashed)
        elif hashed.startswith(b'$2x$'):
            return self._fallback_checkpw(password, hashed)
        return False

# Global instance
hasher = PasswordHasher()