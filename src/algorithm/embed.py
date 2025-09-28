from utils.mp3processing import parse_ID3v2, parse_ID3v1, get_mpeg_frames_offset, parse_mpeg_frame_header, count_modifiable_bytes, get_modifiable_bytes_offset
import hashlib

def get_bits(byte_data):
    bits = ''.join(f'{byte:08b}' for byte in byte_data)
    return bits

def shuffle(offsets, key):
    shuffled = offsets[:]
    for i in range(len(shuffled) - 1, 0, -1):
        digest = hashlib.sha256(f"{key}-{i}".encode()).digest()
        j = int.from_bytes(digest, "big") % (i + 1)
        shuffled[i], shuffled[j] = shuffled[j], shuffled[i]
    return shuffled

def embed(cover_file, secret_file, encrypted, random_insertion, n_lsb, key="nokey"):
    
    mp3_bytes = cover_file.get("content")  
    secret_file_bytes = secret_file.get("content")
    
    secret_file_bits = get_bits(secret_file_bytes)
    
    size_ID3v2 = parse_ID3v2(mp3_bytes)
    size_ID3v1 = parse_ID3v1(mp3_bytes)
    
    mpeg_frames_offset = get_mpeg_frames_offset(mp3_bytes, size_ID3v2, size_ID3v1)
    print(f"MPEG frame offsets: {mpeg_frames_offset[:5]} ... {mpeg_frames_offset[-5:]} (total {len(mpeg_frames_offset)} frames found)")

    parse_mpeg_frame_header(mp3_bytes[mpeg_frames_offset[0]:mpeg_frames_offset[0]+4])
    
    num_modifiable_bytes = count_modifiable_bytes(mp3_bytes, mpeg_frames_offset)
    print("Modifiable bytes:", num_modifiable_bytes)
    
    modifiable_bytes_offset = get_modifiable_bytes_offset(mp3_bytes, mpeg_frames_offset)
    modifiable_bytes_offset = shuffle(modifiable_bytes_offset, key)
    print("Offsets of modifiable bytes:", modifiable_bytes_offset[:10], "...")
    
    max_secret_bits = num_modifiable_bytes * n_lsb
    print("Max secret file size (in bytes):", max_secret_bits // 8)
    
    if len(get_bits(secret_file_bytes)) > max_secret_bits:
        print("Secret file size (in bytes):", len(secret_file_bytes))
        print("Max secret file size (in bytes):", max_secret_bits // 8)
        
        raise ValueError("Secret file is too large to be embedded in the cover file with the given number of LSBs.")
    
    print("Starting embedding process...")
    
    current_target_cover_byte_idx = 0
    bits_changed = 0
    bits_skipped = 0
    
    for i in range(0, len(secret_file_bits), n_lsb):

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