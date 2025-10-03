import numpy as np
import librosa
import tempfile
import io
import os, sys
import contextlib

@contextlib.contextmanager
def suppress_os_stderr():
    devnull = os.open(os.devnull, os.O_WRONLY)
    old_stderr = os.dup(2) 
    os.dup2(devnull, 2)     
    os.close(devnull)
    try:
        yield
    finally:
        os.dup2(old_stderr, 2)  
        os.close(old_stderr)

def calculate_psnr(original_bytes, embedded_bytes):
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
        f.write(original_bytes)
        original_path = f.name
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
        f.write(embedded_bytes)
        embedded_path = f.name

    with suppress_os_stderr():
        original_audio, sr1 = librosa.load(original_path, sr=None, mono=True)
    with suppress_os_stderr():
        embedded_audio, sr2 = librosa.load(embedded_path, sr=None, mono=True)

    if sr1 != sr2:
        raise ValueError("Error occured during PSNR calculation")

    min_len = min(len(original_audio), len(embedded_audio))
    original_audio = original_audio[:min_len]
    embedded_audio = embedded_audio[:min_len]

    P0 = np.mean(original_audio ** 2)
    P1 = np.mean(embedded_audio ** 2)

    numerator = P1 ** 2
    denominator = P1**2 + P0**2 - 2 * P1 * P0
    if denominator == 0:
        return float("inf")

    return 10 * np.log10(numerator / denominator)
