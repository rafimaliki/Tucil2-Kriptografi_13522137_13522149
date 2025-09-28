import os
import sys
import tkinter as tk
from tkinter import filedialog
import questionary
from typing import Optional, List

_BLUE = "\033[38;2;77;103;125m"
_RESET = "\033[0m"
_ORANGE = "\033[38;5;208m"
_WHITE = "\033[97m"

def decode_bytes(content: bytes, encoding: str = "utf-8") -> str:
    return content.decode(encoding, errors="ignore")

def select_file(prompt: str = "Select a file", ext: Optional[List[str]] = None) -> str:
    root = tk.Tk()
    root.withdraw() 

    if ext and len(ext) > 0:
        filetypes = [(f"{e.upper()} files", f"*.{e}") for e in ext]
    else:
        filetypes = [("All files", "*.*")]

    file_path = filedialog.askopenfilename(title=prompt, filetypes=filetypes)
    return file_path or ""

def read_file(prompt: str = "Select a file", ext: Optional[List[str]] = None) -> Optional[dict]:
    print(f"{_BLUE}!{_RESET} {_WHITE}{prompt}{_RESET} ", end="", flush=True)
    path = select_file(prompt, ext)
    if not path:
        return None

    filename = os.path.basename(path)
    extension = os.path.splitext(filename)[1].lstrip(".")
    with open(path, "rb") as f:
        content = f.read()

    print(f"{_ORANGE}{filename}{_RESET}")
    
    return {
        "filename": filename,
        "ext": extension,
        "content": bytearray(content),
    }

def read_cli(prompt, return_type=str, valid_inputs: Optional[List] = None) -> int | str:
    if valid_inputs is None:
        valid_inputs = []
    if return_type not in (int, str):
        raise ValueError("return_type must be int or str")
    allowed = []
    for v in valid_inputs:
        if v is None:
            continue
        cand = v.strip() if isinstance(v, str) else v
        try:
            allowed.append(int(cand) if return_type is int else str(cand))
        except Exception:
            allowed.append(cand)
    while True:
        print(f"{_BLUE}!{_RESET} {_WHITE}{prompt}{_RESET}", end="", flush=True)
        try:
            raw = input()
            if return_type is int:
                try:
                    val = int(raw.strip())
                except ValueError:
                    print("invalid input, try again")
                    continue
            else:
                val = raw.strip()
        except KeyboardInterrupt:
            raise
        except Exception:
            print("invalid input, try again")
            continue
        if allowed:
            if val not in allowed:
                print("invalid option, try again")
                continue
        sys.stdout.write('\033[1A\033[2K')
        sys.stdout.write(f"{_BLUE}!{_RESET} {_WHITE}{prompt}{_RESET}{_ORANGE}{val}{_RESET}\n")
        sys.stdout.flush()
        return val

def write_file(content: str, prompt: str = "Save file as:", ext: Optional[List[str]] = None) -> Optional[str]:
    root = tk.Tk()
    root.withdraw()
    
    print(f"{_BLUE}!{_RESET} {_WHITE}{prompt}{_RESET}", end=" ", flush=True)

    if ext and len(ext) > 0:
        filetypes = [(f"{e.upper()} files", f"*.{e}") for e in ext]
        def_ext = f".{ext[0]}"
    else:
        filetypes = [("All files", "*.*")]
        def_ext = None

    path = filedialog.asksaveasfilename(title=prompt, filetypes=filetypes, defaultextension=def_ext)
    if not path:
        return None

    filename = os.path.basename(path)

    if isinstance(content, (bytes, bytearray)):
        with open(path, "wb") as f:
            f.write(content)
    else:
        with open(path, "w", encoding="utf-8", errors="ignore") as f:
            f.write(content)
    abs_path = os.path.abspath(path)

    if os.name == "nt":
        url = "file:///" + abs_path.replace("\\", "/")
    else:
        url = "file://" + abs_path

    osc_start = "\033]8;;"
    osc_end = "\033\\"
    osc_close = "\033]8;;\033\\"
    hyperlink = f"{osc_start}{url}{osc_end}{abs_path}{osc_close}"

    if sys.stdout.isatty():
        path_display = hyperlink
    else:
        path_display = abs_path

    print(f"{_ORANGE}{filename}{_RESET} at {path_display}\n")

    return path

def print_splash():
    print("\nWelcome to the MP3 Audio File Steganography Program!\n")
    print(r""" /$$      /$$ /$$$$$$$   /$$$$$$         /$$$$$$  /$$$$$$$$ /$$$$$$$$  /$$$$$$   /$$$$$$ 
| $$$    /$$$| $$__  $$ /$$__  $$       /$$__  $$|__  $$__/| $$_____/ /$$__  $$ /$$__  $$
| $$$$  /$$$$| $$  \ $$|__/  \ $$      | $$  \__/   | $$   | $$      | $$  \__/| $$  \ $$
| $$ $$/$$ $$| $$$$$$$/   /$$$$$/      |  $$$$$$    | $$   | $$$$$   | $$ /$$$$| $$$$$$$$
| $$  $$$| $$| $$____/   |___  $$       \____  $$   | $$   | $$__/   | $$|_  $$| $$__  $$
| $$\  $ | $$| $$       /$$  \ $$       /$$  \ $$   | $$   | $$      | $$  \ $$| $$  | $$
| $$ \/  | $$| $$      |  $$$$$$/      |  $$$$$$/   | $$   | $$$$$$$$|  $$$$$$/| $$  | $$
|__/     |__/|__/       \______/        \______/    |__/   |________/ \______/ |__/  |__/
""")
    
def input_mode() -> str:
    mode = questionary.select(
        "Select mode:",
        choices=["Embed", "Extract"]
    ).ask()
    
    if not mode:
        raise ValueError("No mode selected, exiting program.")

    return mode

def input_embed() -> tuple:
    cover_file = read_file("Choose an MP3 audio file (cover):", ext=["mp3"])
    
    if not cover_file:
        raise ValueError("No cover file selected, exiting program.")

    secret_file = read_file("Choose a secret file:", ext=[])
    if not secret_file:
        raise ValueError("No secret file selected, exiting program.")

    encrypted = questionary.select(
        "Do you want to encrypt the secret file?",
        choices=["Yes", "No"]
    ).ask()

    random_insertion = questionary.select(
        "Do you want to use random insertion?",
        choices=["Yes", "No"]
    ).ask()
    
    n_lsb = questionary.select(
        "Select number of LSBs to use:",
        choices=["1", "2", "3", "4"]
    ).ask()
    n_lsb = int(n_lsb)

    if (encrypted == "Yes" or random_insertion == "Yes"):
        key = read_cli(
            "Enter the key for encryption/random insertion: ",
            return_type=str
        )
    else:
        key = None  
        
    return (
        cover_file,
        secret_file,
        encrypted == "Yes",
        random_insertion == "Yes",
        n_lsb,
        key
    )

def input_extract() -> tuple:
    stego_file = read_file("Choose an MP3 audio file (stego):", ext=["mp3"])
    
    if not stego_file:
        raise ValueError("No stego file selected, exiting program.")

    n_lsb = questionary.select(
        "Select number of LSBs to use:",
        choices=["1", "2", "3", "4"]
    ).ask()
    n_lsb = int(n_lsb)

    encrypted = questionary.select(
        "Was the secret file encrypted?",
        choices=["Yes", "No"]
    ).ask()

    random_insertion = questionary.select(
        "Was random insertion used?",
        choices=["Yes", "No"]
    ).ask()
    
    if (encrypted == "Yes" or random_insertion == "Yes"):
        key = read_cli(
            "Enter the key for decryption/random extraction: ",
            return_type=str
        )
    else:
        key = None  
    
    return (
        stego_file,
        n_lsb,
        encrypted == "Yes",
        random_insertion == "Yes",
        key
    )