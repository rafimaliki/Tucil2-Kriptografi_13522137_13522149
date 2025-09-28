from utils.helper import *
from utils.logger import log_execution_time

def retrieve_header_bits(stego_bytes, modifiable_bytes_offset):
    n_lsb = 1
    header_bits = ''
    num_bits = 10 * 8
    for i in range(num_bits // n_lsb):
        byte_offset = modifiable_bytes_offset[i]
        byte_value = stego_bytes[byte_offset]
        lsb_bits = f'{byte_value:08b}'[-n_lsb:]
        header_bits += lsb_bits
        
    return header_bits

def retrieve_secret_bits(stego_bytes, modifiable_bytes_offset, total_secret_bits, n_lsb):
    secret_bits = ''
    header_bits_used = 10 * 8  
    start_index = header_bits_used // n_lsb  
    
    for i in range(total_secret_bits // n_lsb):
        byte_offset = modifiable_bytes_offset[start_index + i]
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
    
    if key:
        modifiable_bytes_offset = shuffle(modifiable_bytes_offset, key)
    
    header_bits = retrieve_header_bits(stego_bytes, modifiable_bytes_offset)
    
    num_secret_bytes, n_lsb, is_encrypted, is_random_insertion, ext = parse_secret_header(bit_to_byte(header_bits))
    
    total_secret_bits = num_secret_bytes * 8
    
    secret_bits = retrieve_secret_bits(stego_bytes, modifiable_bytes_offset, total_secret_bits, n_lsb)
    secret_bytes = bit_to_byte(secret_bits)
    
    print(f"Successfully extracted {len(secret_bytes)} bytes of secret data")
    
    return bytes(secret_bytes), ext