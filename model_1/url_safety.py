from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

# Ensure the Fernet key is available and valid
def get_cipher_suite():
    try:
        if not settings.FERNET_KEY:
            raise ImproperlyConfigured("FERNET_KEY is missing in the settings.")
        
        cipher_suite = Fernet(settings.FERNET_KEY)
        return cipher_suite
    except ValueError as e:
        raise ImproperlyConfigured(f"Invalid FERNET_KEY in settings: {e}")

# Encrypt data
def encrypt_data(data: str) -> str:
    """Encrypts the data using the secret key"""
    cipher_suite = get_cipher_suite()
    encrypted_data = cipher_suite.encrypt(data.encode())
    return encrypted_data.decode()

# Decrypt data
def decrypt_data(encrypted_data: str) -> str:
    """Decrypts the data using the secret key"""
    cipher_suite = get_cipher_suite()
    
    try:
        decrypted_data = cipher_suite.decrypt(encrypted_data.encode())
        return decrypted_data.decode()
    except InvalidToken:
        raise ValueError("The provided encrypted data is invalid or has been tampered with.")
    except Exception as e:
        raise ValueError(f"An error occurred during decryption: {str(e)}")

