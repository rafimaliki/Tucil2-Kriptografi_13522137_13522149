"""
LSB Steganography Implementation
Clean implementation for MP3 audio steganography
"""

import numpy as np
import struct
import random
from typing import Tuple, Optional
from .mp3_handler import MP3Handler
from .vigenere import ExtendedVigenere, key_to_seed

class LSBSteganography:
    def __init__(self):
        self.mp3_handler = MP3Handler()
        
    def embed(self, cover_file: dict, secret_file: dict, encrypted: bool, 
              random_insertion: bool, n_lsb: int, key: Optional[str]) -> bytes:
        """
        Embed secret file into cover MP3 using LSB steganography.
        """
        # Load cover audio
        samples, metadata = self.mp3_handler.load_from_bytes(cover_file["content"])
        original_samples = samples.copy()
        
        # Prepare secret data
        secret_data = secret_file["content"]
        
        # Encrypt if requested
        if encrypted:
            if not key:
                raise ValueError("Key required for encryption")
            cipher = ExtendedVigenere(key)
            secret_data = cipher.encrypt(secret_data)
        
        # Create header with file info
        header = self._create_header(secret_file["ext"], len(secret_data), encrypted, random_insertion, n_lsb)
        total_data = header + secret_data
        
        # Check capacity
        capacity = self.mp3_handler.calculate_capacity(samples, n_lsb)
        if len(total_data) > capacity:
            raise ValueError(f"File too large. Maximum capacity: {capacity} bytes, required: {len(total_data)} bytes")
        
        # Generate embedding positions
        if random_insertion and key:
            positions = self._generate_positions(samples.size, len(total_data) * 8 // n_lsb, key)
        else:
            positions = list(range(len(total_data) * 8 // n_lsb))
        
        # Embed data using LSB
        stego_samples = self._embed_lsb(samples, total_data, n_lsb, positions)
        
        # Calculate and display PSNR
        psnr = self.mp3_handler.calculate_psnr(original_samples, stego_samples)
        print(f"PSNR: {psnr:.2f} dB")
        
        # Convert back to MP3 bytes
        return self.mp3_handler.samples_to_bytes(stego_samples, metadata)
    
    def extract(self, stego_file: dict, n_lsb: int, encrypted: bool, 
                random_insertion: bool, key: Optional[str]) -> bytes:
        """
        Extract secret file from stego MP3.
        """
        # Load stego audio
        samples, _ = self.mp3_handler.load_from_bytes(stego_file["content"])
        
        # Extract header first (fixed 16 bytes)
        header_positions = self._get_header_positions(samples.size, random_insertion, key, n_lsb)
        header_data = self._extract_lsb(samples, 16, n_lsb, header_positions)
        
        # Parse header
        ext, file_size, flags = self._parse_header(header_data)
        
        # Extract secret data
        data_positions = self._get_data_positions(samples.size, file_size, random_insertion, key, n_lsb)
        secret_data = self._extract_lsb(samples, file_size, n_lsb, data_positions)
        
        # Decrypt if needed
        if encrypted and key:
            cipher = ExtendedVigenere(key)
            secret_data = cipher.decrypt(secret_data)
        
        return secret_data
    
    def _create_header(self, extension: str, file_size: int, encrypted: bool, 
                      random_insertion: bool, n_lsb: int) -> bytes:
        """Create 16-byte header with file information."""
        # Extension (8 bytes, padded with zeros)
        ext_bytes = extension.encode('utf-8')[:8].ljust(8, b'\x00')
        
        # File size (4 bytes, little-endian)
        size_bytes = struct.pack('<I', file_size)
        
        # Flags (1 byte: encrypted=bit0, random=bit1, n_lsb=bits2-5)
        flags = 0
        if encrypted:
            flags |= 0x01
        if random_insertion:
            flags |= 0x02
        flags |= (n_lsb & 0x0F) << 2
        
        # Padding (3 bytes)
        return ext_bytes + size_bytes + bytes([flags]) + b'\x00\x00\x00'
    
    def _parse_header(self, header_data: bytes) -> Tuple[str, int, int]:
        """Parse header to extract file information."""
        if len(header_data) < 16:
            raise ValueError("Invalid header size")
        
        ext = header_data[:8].rstrip(b'\x00').decode('utf-8', errors='replace')
        file_size = struct.unpack('<I', header_data[8:12])[0]
        flags = header_data[12]
        
        return ext, file_size, flags
    
    def _generate_positions(self, total_samples: int, num_positions: int, key: str) -> list:
        """Generate random positions for embedding/extraction."""
        seed = key_to_seed(key)
        random.seed(seed)
        
        if num_positions > total_samples:
            raise ValueError("Not enough samples for embedding")
        
        return sorted(random.sample(range(total_samples), num_positions))
    
    def _get_header_positions(self, total_samples: int, random_insertion: bool, 
                             key: Optional[str], n_lsb: int) -> list:
        """Get positions for header extraction."""
        header_bits = 16 * 8  # 16 bytes * 8 bits
        positions_needed = header_bits // n_lsb
        
        if random_insertion and key:
            return self._generate_positions(total_samples, positions_needed, key)[:positions_needed]
        else:
            return list(range(positions_needed))
    
    def _get_data_positions(self, total_samples: int, file_size: int, random_insertion: bool, 
                           key: Optional[str], n_lsb: int) -> list:
        """Get positions for data extraction."""
        header_bits = 16 * 8
        data_bits = file_size * 8
        header_positions = header_bits // n_lsb
        data_positions_needed = data_bits // n_lsb
        
        if random_insertion and key:
            total_positions = self._generate_positions(total_samples, header_positions + data_positions_needed, key)
            return total_positions[header_positions:]
        else:
            return list(range(header_positions, header_positions + data_positions_needed))
    
    def _embed_lsb(self, samples: np.ndarray, data: bytes, n_lsb: int, positions: list) -> np.ndarray:
        """Embed data into samples using LSB technique."""
        stego_samples = samples.copy().flatten().astype(np.int32)
        
        # Convert data to bits
        bits = []
        for byte in data:
            for i in range(8):
                bits.append((byte >> i) & 1)
        
        # Create masks
        lsb_mask = (1 << n_lsb) - 1
        clear_mask = ~lsb_mask & 0xFFFF  # Mask to clear LSBs
        
        # Embed bits
        bit_idx = 0
        for pos in positions:
            if bit_idx >= len(bits):
                break
            
            # Get n_lsb bits to embed
            embed_value = 0
            for i in range(n_lsb):
                if bit_idx < len(bits):
                    embed_value |= (bits[bit_idx] << i)
                    bit_idx += 1
            
            # Embed into sample
            stego_samples[pos] = (stego_samples[pos] & clear_mask) | embed_value
        
        # Restore original shape and type
        stego_samples = stego_samples.astype(samples.dtype)
        return stego_samples.reshape(samples.shape)
    
    def _extract_lsb(self, samples: np.ndarray, num_bytes: int, n_lsb: int, positions: list) -> bytes:
        """Extract data from samples using LSB technique."""
        flat_samples = samples.flatten().astype(np.int32)
        lsb_mask = (1 << n_lsb) - 1
        
        # Extract bits
        bits = []
        for pos in positions:
            if len(bits) >= num_bytes * 8:
                break
            
            lsb_value = flat_samples[pos] & lsb_mask
            
            # Extract individual bits
            for i in range(n_lsb):
                if len(bits) >= num_bytes * 8:
                    break
                bits.append((lsb_value >> i) & 1)
        
        # Convert bits to bytes
        result = []
        for i in range(0, len(bits), 8):
            if i + 7 < len(bits):
                byte_val = 0
                for j in range(8):
                    byte_val |= (bits[i + j] << j)
                result.append(byte_val)
        
        return bytes(result[:num_bytes])