# MP3 Audio Steganography

**Tucil2-Kriptografi_13522137_13522149**

Aplikasi steganografi untuk menyisipkan dan mengekstrak berkas rahasia ke dalam berkas audio MP3 menggunakan metode Multiple Least Significant Bit (Multiple-LSB) dengan dukungan enkripsi Extended Vigenère Cipher.

## 🌟 Fitur Utama

### 🔒 LSB Steganography
- **Multiple LSB**: Mendukung 1-4 bit LSB untuk penyisipan data
- **Kapasitas Otomatis**: Kalkulasi kapasitas maksimum penyisipan
- **PSNR Analysis**: Perhitungan kualitas audio setelah steganografi

### 🔐 Enkripsi Opsional  
- **Extended Vigenère Cipher**: Enkripsi berkas rahasia sebelum penyisipan
- **Key Support**: Kunci maksimal 25 karakter
- **Full Byte Range**: Mendukung semua nilai byte (0-255)

### 🎲 Random Insertion
- **Pseudo-random Positioning**: Posisi penyisipan acak berdasarkan key
- **Enhanced Security**: Menyulitkan deteksi steganografi
- **Deterministic**: Reproducible dengan key yang sama

### 📁 Universal File Support
- **Cover Audio**: File MP3 (mono atau stereo)
- **Secret Files**: Semua tipe file (txt, png, pdf, exe, dll.)
- **Metadata Preservation**: Menyimpan ekstensi dan ukuran file asli

## 🛠️ Teknologi

- **Python 3.8+**
- **pydub**: Pemrosesan audio MP3 
- **numpy**: Operasi array numerik
- **questionary**: Interactive CLI interface
- **tkinter**: GUI file picker

## 📦 Installation

### Prerequisites
```bash
# Install Python 3.8 or higher
python --version
```

### Setup
```bash
# Clone repository
git clone https://github.com/rafimaliki/Tucil2-Kriptografi_13522137_13522149.git
cd Tucil2-Kriptografi_13522137_13522149

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
# source venv/bin/activate

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

## Cara Penggunaan

### Menjalankan Aplikasi
```bash
cd src
python main.py
```

### Mode Embed (Penyisipan)
1. Pilih **"Embed"** dari menu
2. Pilih berkas MP3 sebagai cover audio
3. Pilih berkas rahasia yang akan disisipkan
4. Konfigurasi opsi:
   - **Enkripsi**: Ya/Tidak
   - **Random Insertion**: Ya/Tidak
   - **Jumlah LSB**: 1-4 bit
   - **Key**: Diperlukan jika enkripsi atau random insertion aktif
5. Program akan menampilkan PSNR dan menyimpan stego-audio

### Mode Extract (Ekstraksi)
1. Pilih **"Extract"** dari menu
2. Pilih berkas MP3 stego-audio
3. Masukkan konfigurasi yang sama dengan saat embedding:
   - **Jumlah LSB**: Harus sama dengan saat embed
   - **Enkripsi**: Ya/Tidak (sesuai saat embed)
   - **Random Insertion**: Ya/Tidak (sesuai saat embed)  
   - **Key**: Harus sama dengan saat embed
4. Program akan mengekstrak dan menyimpan berkas rahasia

## Contoh Penggunaan

### Contoh 1: Penyisipan Sederhana
```
Mode: Embed
Cover: music.mp3
Secret: document.pdf
Encrypted: No
Random Insertion: No
N-LSB: 2
Key: (tidak diperlukan)
```

### Contoh 2: Penyisipan dengan Keamanan Maksimal
```
Mode: Embed  
Cover: audio.mp3
Secret: confidential.txt
Encrypted: Yes
Random Insertion: Yes
N-LSB: 3
Key: MySecretKey123
```

## Testing

Jalankan test suite untuk memverifikasi implementasi:

```bash
cd test
python test_steganography.py
```

Test akan memverifikasi:
- Extended Vigenère Cipher
- MP3 Handler functionality  
- Full steganography workflow dengan berbagai konfigurasi

## Struktur Proyek

```
Tucil2-Kriptografi_13522137_13522149/
├── src/
│   ├── main.py                    # Entry point aplikasi
│   ├── algorithm/
│   │   ├── __init__.py
│   │   ├── stego.py              # Main steganography interface
│   │   ├── lsb_stego.py          # LSB steganography implementation
│   │   ├── vigenere.py           # Extended Vigenère cipher
│   │   └── mp3_handler.py        # MP3 audio processing
│   └── utils/
│       ├── __init__.py
│       └── io.py                 # I/O utilities dan user interface
├── files/
│   ├── input/                    # Contoh file input
│   └── output/                   # Hasil output
├── test/
│   └── test_steganography.py     # Test suite
├── requirements.txt              # Python dependencies
└── README.md                     # Dokumentasi ini
```

## 🔍 Algoritma & Implementasi

### LSB Steganography
- Menggunakan n-bit LSB dari setiap sample audio
- Menyimpan metadata di awal area data (32 bytes tetap)
- Mendukung audio mono dan stereo

### Extended Vigenère Cipher
- Implementasi cipher Vigenère untuk byte values 0-255
- Key expansion dengan modular arithmetic
- Enkripsi: `C = (P + K) mod 256`
- Dekripsi: `P = (C - K) mod 256`

### Random Insertion Algorithm
- Konversi key string ke integer seed
- Menggunakan Python's random module dengan seed
- Generate posisi acak tanpa collision
- Deterministic: seed yang sama menghasilkan posisi yang sama

## 📈 Analisis Kapasitas

| N-LSB | Kapasitas per detik | Kapasitas per MB |
|-------|-------------------|------------------|
| 1 bit | ~5.5 KB/s         | ~350 KB/MB       |
| 2 bit | ~11 KB/s          | ~700 KB/MB       |
| 3 bit | ~16.5 KB/s        | ~1 MB/MB         |
| 4 bit | ~22 KB/s          | ~1.4 MB/MB       |

*Berdasarkan audio 44.1kHz stereo*

## Batasan & Catatan

- **Format Audio**: Hanya mendukung MP3 (input dan output)
- **Ukuran Key**: Maksimal 25 karakter
- **Memory Usage**: Memuat seluruh audio ke memory
- **Quality**: Semakin besar N-LSB, semakin terdengar noise pada audio
- **Compatibility**: Memerlukan Python 3.8+ dan ffmpeg untuk pydub

## Troubleshooting

### Error: "Import pydub could not be resolved"
```bash
pip install pydub
# Jika masih error, install ffmpeg
```

### Error: "File too large"
- Kurangi ukuran berkas rahasia
- Gunakan N-LSB yang lebih besar (trade-off dengan kualitas)
- Gunakan berkas cover audio yang lebih panjang

### Error: "Key required for encryption/random insertion"  
- Pastikan memberikan key ketika enkripsi atau random insertion dipilih
- Key tidak boleh kosong

## Authors

- **13522137** - Contributor 1
- **13522149** - Contributor 2
