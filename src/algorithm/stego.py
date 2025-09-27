"""
Main steganography module
Handles embedding and extraction using LSB steganography
"""

from .lsb_stego import LSBSteganography

# Initialize steganography handler
stego_handler = LSBSteganography()

def embed(cover_file, secret_file, encrypted, random_insertion, n_lsb, key):
    """
    Embed secret file into cover audio using LSB steganography.
    
    Args:
        cover_file (dict): Cover audio file data
            {
                "filename": str,
                "content": bytes,
                "ext": str
            }
        secret_file (dict): Secret file data
            {
                "filename": str,
                "content": bytes,
                "ext": str
            }
        encrypted (bool): Whether to encrypt secret data
        random_insertion (bool): Whether to use random insertion points
        n_lsb (int): Number of LSB bits to use (1-4)
        key (str or None): Encryption/randomization key
    
    Returns:
        bytes: Stego audio file bytes
    """
    try:
        print(f"Embedding '{secret_file['filename']}' into '{cover_file['filename']}'...")
        print(f"Configuration: encrypted={encrypted}, random={random_insertion}, n_lsb={n_lsb}")
        
        result = stego_handler.embed(cover_file, secret_file, encrypted, random_insertion, n_lsb, key)
        
        print("Embedding completed successfully!")
        return result
        
    except Exception as e:
        print(f"Embedding failed: {str(e)}")
        raise

def extract(stego_file, n_lsb, encrypted, random_insertion, key):
    """
    Extract secret file from stego audio.
    
    Args:
        stego_file (dict): Stego audio file data
            {
                "filename": str,
                "content": bytes,
                "ext": str
            }
        n_lsb (int): Number of LSB bits used
        encrypted (bool): Whether secret data was encrypted
        random_insertion (bool): Whether random insertion was used
        key (str or None): Decryption/randomization key
    
    Returns:
        bytes: Extracted secret file data
    """
    try:
        print(f"Extracting from '{stego_file['filename']}'...")
        print(f"Configuration: encrypted={encrypted}, random={random_insertion}, n_lsb={n_lsb}")
        
        result = stego_handler.extract(stego_file, n_lsb, encrypted, random_insertion, key)
        
        print("Extraction completed successfully!")
        return result
        
    except Exception as e:
        print(f"Extraction failed: {str(e)}")
        raise