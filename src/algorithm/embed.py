from utils.helper import *
from utils.logger import log_execution_time

def write_header_bits(cover_bytes, offsets, header_bits):
    for i in range(0, 80):
        bit_to_embed = header_bits[i:i+1]
        bit_to_embed = bit_to_embed.ljust(1, '0')
        
        lsb_bits = f'{cover_bytes[offsets[i]]:08b}'[-1:]
        if (lsb_bits != bit_to_embed):
            cover_bytes[offsets[i]] &= (0xFF << 1)
            cover_bytes[offsets[i]] |= int(bit_to_embed, 2)
    return cover_bytes

def write_secret_bits(cover_bytes, offsets, secret_bits, n_lsb):
    for i in range(0, len(secret_bits), n_lsb):
        bit_to_embed = secret_bits[i:i+n_lsb]
        bit_to_embed = bit_to_embed.ljust(n_lsb, '0')  
        
        index = (i // n_lsb) + 80  
        
        lsb_bits = f'{cover_bytes[offsets[index]]:08b}'[-n_lsb:]
        
        if (lsb_bits != bit_to_embed):
            cover_bytes[offsets[index]] &= (0xFF << n_lsb)
            cover_bytes[offsets[index]] |= int(bit_to_embed, 2)
    return cover_bytes

@log_execution_time
def embed(cover_file, secret_file, is_encrypted, is_random_insertion, n_lsb, key="nokey"):
    
    print("\nStarting embedding process...")
    
    cover_bytes = cover_file.get("content")  
    secret_file_bytes = secret_file.get("content")

    size_ID3v2 = len_ID3v2(cover_bytes)
    size_ID3v1 = len_ID3v1(cover_bytes)

    mpeg_frames_offset = get_mpeg_frames_offset(cover_bytes, size_ID3v2, size_ID3v1)
    num_modifiable_bytes = count_modifiable_bytes(cover_bytes, mpeg_frames_offset)

    is_space_available = len(secret_file_bytes)*8 <= (num_modifiable_bytes - 10) * n_lsb

    if not is_space_available:
        print("Secret file size (in bytes):", len(secret_file_bytes))
        print("Max secret file size (in bytes):", (num_modifiable_bytes - 10) * n_lsb // 8)
        
        raise ValueError("Secret file is too large to be embedded in the cover file with the given number of LSBs.")
    
    modifiable_bytes_offset = get_modifiable_bytes_offset(cover_bytes, mpeg_frames_offset)
    
    header_offsets = modifiable_bytes_offset[0:80]
    secret_offsets = modifiable_bytes_offset[80:]

    if (is_random_insertion):
        if not key:
            raise ValueError("A key is required for random insertion.")
        secret_offsets = shuffle(secret_offsets, key)
        
    secret_header_bits = byte_to_bit(create_secret_header(len(secret_file_bytes), n_lsb, is_encrypted, is_random_insertion, secret_file.get("ext")))
    secret_file_bits = byte_to_bit(secret_file_bytes)
    
    # if (is_encrypted):
    #     if (not key):
    #         raise ValueError("A key is required for encryption.")
    #     secret_file_bits = encrypt_bits(secret_file_bits, key)

    result_bytes = write_header_bits(cover_bytes, header_offsets, secret_header_bits)
    result_bytes = write_secret_bits(result_bytes, secret_offsets, secret_file_bits, n_lsb)

    print("Embedding process completed.")

    return result_bytes