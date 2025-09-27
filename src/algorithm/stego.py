# embed dan extract nanti pisah di file beda aja

def embed(cover_file, secret_file, encrypted, random_insertion, n_lsb, key):
    
    """
    Struct file:
        {
            "name": str,
            "content": bytes,
            "ext": str
        }
    """

    result = cover_file["content"]
    
    return result

def extract(stego_file, n_lsb, encrypted, random_insertion, key):
    
    result = b"extracted secret content"
    
    return result