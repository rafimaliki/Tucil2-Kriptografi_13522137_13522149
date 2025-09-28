colors = {
    'RESET': "\033[0m",
    'BLACK': "\033[38;2;120;120;120m",   
    'RED': "\033[38;2;255;120;120m",     
    'GREEN': "\033[38;2;144;238;144m",  
    'YELLOW': "\033[38;2;255;255;153m", 
    'BLUE': "\033[38;2;119;158;203m",  
    'MAGENTA': "\033[38;2;218;112;214m",
    'CYAN': "\033[38;2;175;238;238m",    
    'WHITE': "\033[38;2;245;245;245m",  
}

"""
Parsing and printing ID3v2 tags from MP3 files.
"""
def parse_ID3v2(mp3_bytes):
    print(colors["GREEN"] + "=== ID3v2 Tag Information ===")
    
    if mp3_bytes[0:3] != b'ID3':
        print("Have ID3v2 header: NO")
        print("No ID3v2 tag found in the file.")
        return 0 
    
    print("Have ID3v2 header: YES")
    print("Starting byte: 0")
    
    major_version = mp3_bytes[3]
    minor_version = mp3_bytes[4]
    print(f"ID3v2 Version: 2.{major_version}.{minor_version}")
    
    flags = mp3_bytes[5]
    unsync = bool(flags & 0x80)
    extended = bool(flags & 0x40)
    experimental = bool(flags & 0x20)
    footer = bool(flags & 0x10)
    
    print(f"Flags: 0x{flags:02X}")
    print(f"  - Unsynchronisation: {'YES' if unsync else 'NO'}")
    print(f"  - Extended header: {'YES' if extended else 'NO'}")
    print(f"  - Experimental indicator: {'YES' if experimental else 'NO'}")
    print(f"  - Footer present: {'YES' if footer else 'NO'}")
    
    size_bytes = mp3_bytes[6:10]
    
    size = ((size_bytes[0] & 0x7F) << 21) | ((size_bytes[1] & 0x7F) << 14) | ((size_bytes[2] & 0x7F) << 7) | (size_bytes[3] & 0x7F)
    
    total_size = size + 10
    
    print(f"Tag size (excluding header): {size} bytes")
    print(f"Total tag size (including header): {total_size} bytes")
    print(f"Ending byte: {total_size - 1}")
    
    if total_size > 10 and len(mp3_bytes) >= total_size:
        print("\nFrame Information:")
        print("  Note: Payload size is the data content only (excludes frame header)")
        frame_offset = 10
        
        if extended and major_version >= 3:
            if major_version == 3:
                ext_header_size = int.from_bytes(mp3_bytes[frame_offset:frame_offset+4], 'big')
                frame_offset += 4 + ext_header_size
            elif major_version == 4:
                ext_header_size = ((mp3_bytes[frame_offset] & 0x7F) << 21) | ((mp3_bytes[frame_offset+1] & 0x7F) << 14) | ((mp3_bytes[frame_offset+2] & 0x7F) << 7) | (mp3_bytes[frame_offset+3] & 0x7F)
                frame_offset += ext_header_size
        
        frame_count = 0
        while frame_offset < total_size - 4:
            if mp3_bytes[frame_offset:frame_offset+4] == b'\x00\x00\x00\x00':
                break
                
            frame_id = mp3_bytes[frame_offset:frame_offset+4]
            if major_version >= 3:
                if major_version == 3:
                    frame_size = int.from_bytes(mp3_bytes[frame_offset+4:frame_offset+8], 'big')
                else: 
                    frame_size_bytes = mp3_bytes[frame_offset+4:frame_offset+8]
                    frame_size = ((frame_size_bytes[0] & 0x7F) << 21) | ((frame_size_bytes[1] & 0x7F) << 14) | ((frame_size_bytes[2] & 0x7F) << 7) | (frame_size_bytes[3] & 0x7F)
                frame_flags = mp3_bytes[frame_offset+8:frame_offset+10]
                frame_data_offset = frame_offset + 10
            else: 
                frame_size = int.from_bytes(mp3_bytes[frame_offset+3:frame_offset+6], 'big')
                frame_flags = b'\x00\x00'
                frame_data_offset = frame_offset + 6
            
            try:
                frame_id_str = frame_id.decode('ascii')
                header_size = 10 if major_version >= 3 else 6
                total_frame_size = header_size + frame_size
                print(f"  Frame {frame_count + 1}: {frame_id_str} (Payload: {frame_size} bytes, Total: {total_frame_size} bytes)")
                frame_count += 1
                
                if frame_count >= 10: 
                    break
                    
            except UnicodeDecodeError:
                break
            
            frame_offset += (10 if major_version >= 3 else 6) + frame_size
            
        if frame_count == 0:
            print("  No readable frames found")
        else:
            print(f"  Total frames parsed: {frame_count}")

    print("=" * 30 + colors["RESET"])
    return total_size

"""
Parsing and printing ID3v1 tags from MP3 files.
"""
def parse_ID3v1(mp3_bytes):
    print(colors["YELLOW"] + "=== ID3v1 Tag Information ===")
    
 
    if len(mp3_bytes) < 128 or mp3_bytes[-128:-125] != b'TAG':
        print("Have ID3v1 header: NO")
        print("No ID3v1 tag found in the file.")
        print("=" * 30)
        return 0 

    print("Have ID3v1 header: YES")
    
    file_size = len(mp3_bytes)
    starting_byte = file_size - 128
    ending_byte = file_size - 1
    
    print(f"Starting byte: {starting_byte}")
    print(f"Ending byte: {ending_byte}")
    print("Size in bytes: 128")
    
    tag_data = mp3_bytes[-128:]

    try:
        title = tag_data[3:33].rstrip(b'\x00').decode('latin-1', errors='ignore')
        artist = tag_data[33:63].rstrip(b'\x00').decode('latin-1', errors='ignore')
        album = tag_data[63:93].rstrip(b'\x00').decode('latin-1', errors='ignore')
        year = tag_data[93:97].rstrip(b'\x00').decode('latin-1', errors='ignore')
      
        if tag_data[125] == 0 and tag_data[126] != 0:
            comment = tag_data[97:125].rstrip(b'\x00').decode('latin-1', errors='ignore')
            track = tag_data[126]
            version = "1.1"
            print(f"ID3v1 Version: {version}")
            print(f"Track Number: {track}")
        else:
            comment = tag_data[97:127].rstrip(b'\x00').decode('latin-1', errors='ignore')
            version = "1.0"
            print(f"ID3v1 Version: {version}")
        
        genre_byte = tag_data[127]
        
        genres = [
            "Blues", "Classic Rock", "Country", "Dance", "Disco", "Funk", "Grunge",
            "Hip-Hop", "Jazz", "Metal", "New Age", "Oldies", "Other", "Pop", "R&B",
            "Rap", "Reggae", "Rock", "Techno", "Industrial", "Alternative", "Ska",
            "Death Metal", "Pranks", "Soundtrack", "Euro-Techno", "Ambient",
            "Trip-Hop", "Vocal", "Jazz+Funk", "Fusion", "Trance", "Classical",
            "Instrumental", "Acid", "House", "Game", "Sound Clip", "Gospel", "Noise",
            "Alternative Rock", "Bass", "Soul", "Punk", "Space", "Meditative",
            "Instrumental Pop", "Instrumental Rock", "Ethnic", "Gothic", "Darkwave",
            "Techno-Industrial", "Electronic", "Pop-Folk", "Eurodance", "Dream",
            "Southern Rock", "Comedy", "Cult", "Gangsta", "Top 40", "Christian Rap",
            "Pop/Funk", "Jungle", "Native American", "Cabaret", "New Wave",
            "Psychedelic", "Rave", "Showtunes", "Trailer", "Lo-Fi", "Tribal",
            "Acid Punk", "Acid Jazz", "Polka", "Retro", "Musical", "Rock & Roll",
            "Hard Rock"
        ]
        
        if genre_byte < len(genres):
            genre = genres[genre_byte]
        else:
            genre = f"Unknown ({genre_byte})"
        
        print("\nTag Content:")
        print(f"  Title: {title if title else '(empty)'}")
        print(f"  Artist: {artist if artist else '(empty)'}")
        print(f"  Album: {album if album else '(empty)'}")
        print(f"  Year: {year if year else '(empty)'}")
        print(f"  Comment: {comment if comment else '(empty)'}")
        print(f"  Genre: {genre}")
        
        print(f"\nRaw genre byte: {genre_byte}")
        print(f"Tag identifier: {tag_data[0:3]}")
        
    except Exception as e:
        print(f"Error parsing ID3v1 tag content: {e}")
        print("Raw tag data (hex):", tag_data[:20].hex())
    
    print("=" * 30 + colors["RESET"])
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
Parse and print details from a 4-byte MPEG frame header.
"""
def parse_mpeg_frame_header(header_bytes: bytes):
    if len(header_bytes) != 4:
        raise ValueError("Header must be exactly 4 bytes")

    header = int.from_bytes(header_bytes, byteorder="big")

    sync = (header >> 21) & 0x7FF
    version_id = (header >> 19) & 0b11
    layer = (header >> 17) & 0b11
    protection = (header >> 16) & 0b1
    bitrate_index = (header >> 12) & 0xF
    sampling_rate_index = (header >> 10) & 0b11
    padding = (header >> 9) & 0b1
    private = (header >> 8) & 0b1
    channel_mode = (header >> 6) & 0b11
    mode_extension = (header >> 4) & 0b11
    copyright_bit = (header >> 3) & 0b1
    original = (header >> 2) & 0b1
    emphasis = header & 0b11

    versions = {0b00: "MPEG Version 2.5", 0b10: "MPEG Version 2", 0b11: "MPEG Version 1"}
    layers = {0b01: "Layer III", 0b10: "Layer II", 0b11: "Layer I"}
    channel_modes = {0b00: "Stereo", 0b01: "Joint Stereo", 0b10: "Dual Channel", 0b11: "Mono"}
    sampling_rates = {
        0b00: "44100 Hz",
        0b01: "48000 Hz",
        0b10: "32000 Hz",
        0b11: "reserved"
    }

    print(colors["MAGENTA"] + "=== MPEG Frame Header ===")
    print(f"Sync: {'OK' if sync == 0x7FF else 'Invalid'}")
    print(f"Version: {versions.get(version_id, 'reserved')}")
    print(f"Layer: {layers.get(layer, 'reserved')}")
    print(f"CRC Protection: {'No' if protection else 'Yes'}")
    print(f"Bitrate Index: {bitrate_index}")
    print(f"Sampling Rate: {sampling_rates.get(sampling_rate_index, 'reserved')}")
    print(f"Padding: {padding}")
    print(f"Private Bit: {private}")
    print(f"Channel Mode: {channel_modes.get(channel_mode, 'reserved')}")
    print(f"Mode Extension: {mode_extension}")
    print(f"Copyright: {copyright_bit}")
    print(f"Original: {original}")
    print(f"Emphasis: {emphasis}")
    print("="*25 + colors["RESET"])

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