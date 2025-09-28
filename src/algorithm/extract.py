from utils.helper import *
from utils.logger import log_execution_time

def read_header_bits(stego_bytes, offsets):
    header_bits = ''
    num_bits = 10 * 8
    for i in range(num_bits):
        byte_offset = offsets[i]
        byte_value = stego_bytes[byte_offset]
        lsb_bits = f'{byte_value:08b}'[-1:]
        header_bits += lsb_bits
        
    return header_bits

def read_secret_bits(stego_bytes, offsets, total_secret_bits, n_lsb):
    secret_bits = ''
    header_bits_used = 10 * 8  
    start_index = header_bits_used // n_lsb  
    
    for i in range(total_secret_bits // n_lsb):
        byte_offset = offsets[start_index + i]
        byte_value = stego_bytes[byte_offset]
        lsb_bits = f'{byte_value:08b}'[-n_lsb:]
        secret_bits += lsb_bits
    
    return secret_bits

@log_execution_time
def extract(stego_file, key):
    
    print("\nStarting extraction process...")
    
    stego_bytes = stego_file.get("content")

    size_ID3v2 = len_ID3v2(stego_bytes)
    size_ID3v1 = len_ID3v1(stego_bytes)

    mpeg_frames_offset = get_mpeg_frames_offset(stego_bytes, size_ID3v2, size_ID3v1)

    modifiable_bytes_offset = get_modifiable_bytes_offset(stego_bytes, mpeg_frames_offset)

    header_offsets = modifiable_bytes_offset[0:80]
    secret_offsets = modifiable_bytes_offset[80:]

    header_bits = read_header_bits(stego_bytes, header_offsets)
    parsed_header = parse_secret_header(header_bits)

    num_secret_bytes = parsed_header.get("num_secret_bytes")
    n_lsb = parsed_header.get("n_lsb")
    is_encrypted = parsed_header.get("is_encrypted")
    is_random_insertion = parsed_header.get("is_random_insertion")
    ext = parsed_header.get("ext")

    if is_random_insertion:
        if not key:
            raise ValueError("A key is required for random insertion.")
        secret_offsets = shuffle(secret_offsets, key)

    secret_bits = read_secret_bits(stego_bytes, secret_offsets, num_secret_bytes * 8, n_lsb)
    
    # if is_encrypted:
    #     if not key:
    #         raise ValueError("A key is required for decryption.")
    #     secret_bits = decrypt_bits(secret_bits, key)
        
    secret_bytes = bit_to_byte(secret_bits)
    
    print(f"Successfully extracted {len(secret_bytes)} bytes of secret data")
    
    return bytes(secret_bytes), ext