from utils.helper import *
from utils.logger import log_execution_time

def preprocess_secret_file(secret_file_bytes, is_encrypted, is_random_insertion, n_lsb, ext):
    secret_file_size = len(secret_file_bytes)
    
    header = create_secret_header(secret_file_size, n_lsb, is_encrypted, is_random_insertion, ext)
    
    full_secret_bytes = header + secret_file_bytes
    full_secret_bits = byte_to_bit(full_secret_bytes)
    
    return full_secret_bits

@log_execution_time
def embed(cover_file, secret_file, is_encrypted, is_random_insertion, n_lsb, key="nokey"):
    
    print("\nStarting embedding process...")
    
    mp3_bytes = cover_file.get("content")  
    secret_file_bytes = secret_file.get("content")

    secret_file_bits = preprocess_secret_file(secret_file_bytes, is_encrypted, is_random_insertion, n_lsb, secret_file.get("ext"))

    size_ID3v2 = len_ID3v2(mp3_bytes)
    size_ID3v1 = len_ID3v1(mp3_bytes)

    mpeg_frames_offset = get_mpeg_frames_offset(mp3_bytes, size_ID3v2, size_ID3v1)

    num_modifiable_bytes = count_modifiable_bytes(mp3_bytes, mpeg_frames_offset)
    
    modifiable_bytes_offset = get_modifiable_bytes_offset(mp3_bytes, mpeg_frames_offset)

    if (is_random_insertion):
        modifiable_bytes_offset = shuffle(modifiable_bytes_offset, key)
        
    
    max_secret_bits = num_modifiable_bytes * n_lsb
    
    if len(secret_file_bits) > max_secret_bits: 
        print("Secret file size with header (in bits):", len(secret_file_bits))
        print("Max secret file size (in bits):", max_secret_bits)
        
        raise ValueError("Secret file is too large to be embedded in the cover file with the given number of LSBs.")
    
    current_target_cover_byte_idx = 0
    bits_changed = 0
    bits_skipped = 0
    
    for i in range(0, 80):
        bit_to_embed = secret_file_bits[i:i+1]
        bit_to_embed = bit_to_embed.ljust(1, '0')
        
        lsb_bits = f'{mp3_bytes[modifiable_bytes_offset[current_target_cover_byte_idx]]:08b}'[-1:]
        if (lsb_bits != bit_to_embed):
            mp3_bytes[modifiable_bytes_offset[current_target_cover_byte_idx]] &= (0xFF << 1)
            mp3_bytes[modifiable_bytes_offset[current_target_cover_byte_idx]] |= int(bit_to_embed, 2)
            bits_changed += 1
        else:
            bits_skipped += 1
            
        current_target_cover_byte_idx += 1
        
        if (current_target_cover_byte_idx >= len(modifiable_bytes_offset)):
            print("No more modifiable bytes available.")
            break
    
    for i in range(80, len(secret_file_bits), n_lsb):

        bit_to_embed = secret_file_bits[i:i+n_lsb]
        bit_to_embed = bit_to_embed.ljust(n_lsb, '0')  
        
        lsb_bits = f'{mp3_bytes[modifiable_bytes_offset[current_target_cover_byte_idx]]:08b}'[-n_lsb:]
        
        if (lsb_bits != bit_to_embed):
            mp3_bytes[modifiable_bytes_offset[current_target_cover_byte_idx]] &= (0xFF << n_lsb)
            mp3_bytes[modifiable_bytes_offset[current_target_cover_byte_idx]] |= int(bit_to_embed, 2)
            bits_changed += 1
        else:
            bits_skipped += 1

        current_target_cover_byte_idx += 1
        
        if (current_target_cover_byte_idx >= len(modifiable_bytes_offset)):
            print("No more modifiable bytes available.")
            break
        
    print("Embedding process completed.")
    print(f"Bits changed: {bits_changed}")
    print(f"Bits skipped: {bits_skipped}")
    print(f"Ratio of bits changed to total bits processed: {bits_changed / (bits_changed + bits_skipped) if (bits_changed + bits_skipped) > 0 else 0:.2%}")

    return mp3_bytes