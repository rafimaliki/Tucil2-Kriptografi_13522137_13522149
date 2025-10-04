# MP3 Audio File Steganography Program

> Tugas Kecil 2 IF4020 Kriptografi

<div style="text-align: justify;">
A comprehensive steganography application that enables users to hide secret data within MP3 audio files using the LSB (Least Significant Bit) technique. This program can embed and extract hidden messages from MP3 files while maintaining audio quality and providing encryption and randomization features for enhanced security.
</div>

<br>

<div align="center">
  <img src="screenshots/Screenshot 2025-10-04 093359.png" alt="Program Screenshot" width="800">
  <br>
  <em>Screenshot of the MP3 Steganography Program interface</em>
</div>

## Features

- **LSB Steganography**: Hide data in the least significant bits of MP3 audio frames
- **Multiple LSB Support**: Choose between 1-4 LSBs for different capacity vs. quality trade-offs
- **Encryption**: Optional encryption of secret data using key-based encryption
- **Random Insertion**: Randomize the placement of hidden data for additional security
- **User-friendly Interface**: Interactive command-line interface with file dialogs

## Program Description

<div style="text-align: justify;">
This steganography tool works by analyzing MP3 file structure, identifying MPEG audio frames, and embedding secret data into the modifiable portions of these frames. The program carefully avoids corrupting essential audio data by skipping frame headers and focusing on the audio payload sections where modifications won't affect playback quality.
</div>

## 1. Requirements

- Python 3.8 or higher installed on the system
- Dependencies: listed in `requirements.txt` (e.g., `questionary`)

## 2. Setup Instructions

1. Create a Virtual Environment

   ```bash
   python -m venv .venv
   ```

2. Activate the Virtual Environment

   ```bash
   venv\Scripts\Activate
   ```

3. Install Dependencies

   ```bash
   pip install -r requirements.txt
   ```

## 3. Run the Program

1. Navigate to the `src` folder:

   ```bash
   cd src
   ```

2. Run the main script:

   ```bash
   py main.py
   ```

## 4. Usage

### Embedding a Secret File

1. Run the program and select "Embed" mode
2. Choose an MP3 file as the cover medium
3. Select the secret file you want to hide
4. Configure encryption and randomization options
5. Set the number of LSBs (1-4) to use
6. Provide encryption/randomization key if needed
7. Save the resulting stego MP3 file

### Extracting a Secret File

1. Run the program and select "Extract" mode
2. Choose the stego MP3 file containing hidden data
3. Enter the key used during embedding (if applicable)
4. The program will extract and save the hidden file

## Team Members

| No. | NIM      | Name                | Contribution                       |
| --- | -------- | ------------------- | ---------------------------------- |
| 1   | 13522137 | Ahmad Rafi Maliki   | LSB embedding/extracting algorithm |
| 2   | 13522149 | Muhammad Dzaki Arta | Encryption, testing                |

## References

1. Kaspersky. (t.t.). What is Steganography? Kaspersky Resource Center. Accessed on October 4, 2025, from https://www.kaspersky.com/resource-center/definitions/what-is-steganography

2. Alghamdi, A. (2023). Audio Steganography Method Using Least Significant Bit (LSB) Encoding Technique. ResearchGate. Accessed on October 4, 2025, from https://www.researchgate.net/publication/369708559_Audio_Steganography_Method_Using_Least_Significant_Bit_LSB_Encoding_Technique

3. ITM Web of Conferences. (2022). Adaptation for Vigenère Cipher Method for Auto Binary Files Ciphering. In ITM Web of Conferences (Vol. 46, p. 01017). EDP Sciences. Accessed on October 4, 2025, from https://www.itm-conferences.org/articles/itmconf/pdf/2022/02/itmconf_icacs2022_01017.pdf
