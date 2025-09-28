import hashlib

"""
Get the size of ID3v2 header if present, otherwise return 0.
"""
def len_ID3v2(mp3_bytes):
    if mp3_bytes[0:3] != b'ID3':
        return 0  # no ID3v2

    size_bytes = mp3_bytes[6:10]
    size = ((size_bytes[0] & 0x7F) << 21) | ((size_bytes[1] & 0x7F) << 14) | \
           ((size_bytes[2] & 0x7F) << 7) | (size_bytes[3] & 0x7F)
    total_size = size + 10  # add header
    return total_size

"""
Get the size of ID3v1 tag if present, otherwise return 0.
"""
def len_ID3v1(mp3_bytes):
    if len(mp3_bytes) < 128 or mp3_bytes[-128:-125] != b'TAG':
        return 0  # no ID3v1
    return 128


"""
Find all MPEG frame offsets in the MP3 file by scanning for frame sync patterns.
"""
def get_mpeg_frames_offset(mp3_bytes, ID3v2_size, ID3v1_size):
    frame_offsets = []
    
    start_offset = ID3v2_size
    end_offset = len(mp3_bytes) - ID3v1_size
    
    if start_offset >= end_offset or start_offset < 0 or end_offset <= 0:
        return frame_offsets
    
    current_offset = start_offset
    
    while current_offset < end_offset - 1:  
        if current_offset + 1 >= len(mp3_bytes):
            break
            
        byte1 = mp3_bytes[current_offset]
        byte2 = mp3_bytes[current_offset + 1]
        
        if byte1 == 0xFF and (byte2 & 0xE0) == 0xE0:
            if current_offset + 3 < len(mp3_bytes):  
                header = int.from_bytes(mp3_bytes[current_offset:current_offset + 4], 'big')
          
                if is_valid_mpeg_header(header):
                    frame_offsets.append(current_offset)
               
                    frame_length = calculate_frame_length(header)
                    if frame_length > 0:
                        current_offset += frame_length
                        continue
    
        current_offset += 1
    
    return frame_offsets

"""
Validate if a 32-bit header represents a valid MPEG frame header.
"""
def is_valid_mpeg_header(header):
    sync = (header >> 21) & 0x7FF          # Bits 31-21: sync word (should be 0x7FF)
    version = (header >> 19) & 0x3         # Bits 20-19: MPEG version
    layer = (header >> 17) & 0x3           # Bits 18-17: Layer description  
    bitrate = (header >> 12) & 0xF         # Bits 15-12: Bitrate index
    sampling = (header >> 10) & 0x3        # Bits 11-10: Sampling rate frequency index
    
    if sync != 0x7FF:
        return False

    if version == 1:
        return False
    
    if layer == 0: 
        return False
    
    if bitrate == 0 or bitrate == 15:
        return False
    
    if sampling == 3: 
        return False
    
    return True

"""
Calculate the length of an MPEG frame based on its header.
"""
def calculate_frame_length(header):
    version = (header >> 19) & 0x3         # Bits 20-19: MPEG version
    layer = (header >> 17) & 0x3           # Bits 18-17: Layer description  
    bitrate_index = (header >> 12) & 0xF   # Bits 15-12: Bitrate index
    sampling_index = (header >> 10) & 0x3  # Bits 11-10: Sampling rate frequency index
    padding = (header >> 9) & 0x1          # Bit 9: Padding bit
    
    if version == 3:     
        mpeg_version = 1
    elif version == 2:
        mpeg_version = 2  
    elif version == 0:    
        mpeg_version = 2.5
    else:
        return 0  
    
    if layer == 3:      
        layer_num = 1
    elif layer == 2:     
        layer_num = 2
    elif layer == 1:    
        layer_num = 3
    else:
        return 0 
    
    if mpeg_version == 1: 
        if layer_num == 1:  
            bitrates = [0, 32, 64, 96, 128, 160, 192, 224, 256, 288, 320, 352, 384, 416, 448, 0]
        elif layer_num == 2: 
            bitrates = [0, 32, 48, 56, 64, 80, 96, 112, 128, 160, 192, 224, 256, 320, 384, 0]
        else:  
            bitrates = [0, 32, 40, 48, 56, 64, 80, 96, 112, 128, 160, 192, 224, 256, 320, 0]
    else: 
        if layer_num == 1:
            bitrates = [0, 32, 48, 56, 64, 80, 96, 112, 128, 144, 160, 176, 192, 224, 256, 0]
        else: 
            bitrates = [0, 8, 16, 24, 32, 40, 48, 56, 64, 80, 96, 112, 128, 144, 160, 0]
    
    bitrate = bitrates[bitrate_index] if bitrate_index < len(bitrates) else 0
    if bitrate == 0:
        return 0 
    
    if mpeg_version == 1: 
        sample_rates = [44100, 48000, 32000, 0]
    elif mpeg_version == 2:  
        sample_rates = [22050, 24000, 16000, 0]
    else: 
        sample_rates = [11025, 12000, 8000, 0]
    
    sample_rate = sample_rates[sampling_index] if sampling_index < len(sample_rates) else 0
    if sample_rate == 0:
        return 0  
    
    if layer_num == 1: 
        frame_length = ((12 * bitrate * 1000) // sample_rate + padding) * 4
    else: 
        if mpeg_version == 1:
            frame_length = (144 * bitrate * 1000) // sample_rate + padding
        else:  
            if layer_num == 3:
                frame_length = (72 * bitrate * 1000) // sample_rate + padding
            else:
                frame_length = (144 * bitrate * 1000) // sample_rate + padding
    
    return frame_length
 
"""
Count the number of modifiable bytes in the MP3 file.
"""
def count_modifiable_bytes(mp3_bytes, frame_offsets):
    modifiable_bytes = 0
    for i in range(len(frame_offsets) - 1):
        frame_size = frame_offsets[i + 1] - frame_offsets[i]
        modifiable_bytes += frame_size - 4  
    return modifiable_bytes

"""
Get the byte offsets of all modifiable bytes in the MP3 file.
"""
def get_modifiable_bytes_offset(mp3_bytes, frame_offsets):
    modifiable_offsets = []
    for i in range(len(frame_offsets) - 1):
        frame_start = frame_offsets[i]
        frame_end = frame_offsets[i + 1]
        modifiable_offsets.extend(range(frame_start + 4, frame_end))
    return modifiable_offsets

"""
Convert byte data to a string of bits.
"""
def byte_to_bit(byte_data):
    bits = ''.join(f'{byte:08b}' for byte in byte_data)
    return bits

"""
Convert a string of bits back to byte data.
"""
def bit_to_byte(bits):
    byte_array = bytearray()
    for i in range(0, len(bits), 8):
        byte_segment = bits[i:i+8]
        if len(byte_segment) < 8:
            byte_segment = byte_segment.ljust(8, '0')  
        byte_array.append(int(byte_segment, 2))
    
    return byte_array

"""
Shuffle the list of offsets using a key for randomness.
"""
def shuffle(offsets, key):
    shuffled = offsets[:]
    for i in range(len(shuffled) - 1, 0, -1):
        digest = hashlib.sha256(f"{key}-{i}".encode()).digest()
        j = int.from_bytes(digest, "big") % (i + 1)
        shuffled[i], shuffled[j] = shuffled[j], shuffled[i]
    return shuffled

"""
Create a secret header for the LSB steganography.
"""
def create_secret_header(num_secret_bytes, n_lsb, is_encrypted, is_random_insertion, ext):
    header = bytearray(10)
    header[0:4] = num_secret_bytes.to_bytes(4, 'big')
    header[4] = n_lsb
    flags = 0
    if is_encrypted:
        flags |= 0b00000001
    if is_random_insertion:
        flags |= 0b00000010
    header[5] = flags
    header[6:10] = ext.encode().ljust(4, b'\0')
    
    print("\nHeader:", ' '.join(f'{byte:02X}' for byte in header))
    return header

"""
Parse the secret header for the LSB steganography.
"""
def parse_secret_header(header_bytes):
    
    # print("\nHeader:", ' '.join(f'{byte:02X}' for byte in header_bytes))
    
    if len(header_bytes) != 10:
        raise ValueError("Invalid header length")
    num_secret_bytes = int.from_bytes(header_bytes[0:4], 'big')
    n_lsb = header_bytes[4]
    flags = header_bytes[5]
    is_encrypted = (flags & 0b00000001) != 0
    is_random_insertion = (flags & 0b00000010) != 0
    ext = header_bytes[6:10].rstrip(b'\0').decode()
    
    # print(f"Secret file size (in bytes): {num_secret_bytes}")
    # print(f"Number of LSBs used: {n_lsb}")
    # print(f"Is encrypted: {'Yes' if is_encrypted else 'No'}")
    # print(f"Is random insertion: {'Yes' if is_random_insertion else 'No'}")
    # print(f"File extension: {ext if ext else 'None'}")
        
    return num_secret_bytes, n_lsb, is_encrypted, is_random_insertion, ext