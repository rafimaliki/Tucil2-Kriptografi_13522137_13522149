"""
Extended Vigenère Cipher Implementation
Supports encryption/decryption of any byte values (0-255)
"""

class ExtendedVigenere:
    def __init__(self, key: str):
        """
        Initialize Extended Vigenère cipher with a key.
        
        Args:
            key (str): The encryption key (max 25 characters)
        """
        if len(key) > 25:
            raise ValueError("Key length must not exceed 25 characters")
        if not key:
            raise ValueError("Key cannot be empty")
        
        self.key = key
        self.key_bytes = [ord(c) for c in key]
    
    def encrypt(self, data: bytes) -> bytes:
        """
        Encrypt data using Extended Vigenère cipher.
        
        Args:
            data (bytes): Data to encrypt
            
        Returns:
            bytes: Encrypted data
        """
        if not data:
            return b""
        
        encrypted = []
        key_len = len(self.key_bytes)
        
        for i, byte_val in enumerate(data):
            key_byte = self.key_bytes[i % key_len]
            encrypted_byte = (byte_val + key_byte) % 256
            encrypted.append(encrypted_byte)
        
        return bytes(encrypted)
    
    def decrypt(self, data: bytes) -> bytes:
        """
        Decrypt data using Extended Vigenère cipher.
        
        Args:
            data (bytes): Data to decrypt
            
        Returns:
            bytes: Decrypted data
        """
        if not data:
            return b""
        
        decrypted = []
        key_len = len(self.key_bytes)
        
        for i, byte_val in enumerate(data):
            key_byte = self.key_bytes[i % key_len]
            decrypted_byte = (byte_val - key_byte) % 256
            decrypted.append(decrypted_byte)
        
        return bytes(decrypted)

def key_to_seed(key: str) -> int:
    """
    Convert string key to integer seed for random number generation.
    
    Args:
        key (str): String key
        
    Returns:
        int: Integer seed value
    """
    seed = 0
    for char in key:
        seed = (seed * 31 + ord(char)) % (2**32 - 1)
    return seed