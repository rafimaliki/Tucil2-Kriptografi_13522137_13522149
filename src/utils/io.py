import os
import sys
import questionary
from typing import Optional, List

_BLUE = "\033[38;2;77;103;125m"
_RESET = "\033[0m"
_ORANGE = "\033[38;5;208m"
_WHITE = "\033[97m"

def decode_bytes(content: bytes, encoding: str = "utf-8") -> str:
    return content.decode(encoding, errors="ignore")

def select_file(prompt: str = "Select a file", ext: Optional[List[str]] = None) -> str:
    while True:
        file_path = input(f"{prompt}: ").strip()
        if not file_path:
            print("Please enter a valid file path.")
            continue
        
        # Convert relative path to absolute if needed
        if not os.path.isabs(file_path):
            file_path = os.path.abspath(file_path)
        
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            continue
            
        if not os.path.isfile(file_path):
            print(f"Path is not a file: {file_path}")
            continue
            
        # Check extension if specified
        if ext and len(ext) > 0:
            file_ext = os.path.splitext(file_path)[1].lstrip(".").lower()
            if file_ext not in [e.lower() for e in ext]:
                print(f"Invalid file extension. Expected: {', '.join(ext)}")
                continue
        
        return file_path

def read_file(prompt: str = "Select a file", ext: Optional[List[str]] = None) -> Optional[dict]:
    print(f"{_BLUE}!{_RESET} {_WHITE}{prompt}{_RESET}")
    path = select_file(prompt, ext)
    if not path:
        return None

    filename = os.path.basename(path)
    extension = os.path.splitext(filename)[1].lstrip(".")
    with open(path, "rb") as f:
        content = f.read()

    print(f"Selected: {_ORANGE}{filename}{_RESET}")
    
    return {
        "filename": filename,
        "ext": extension,
        "content": content,
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
    print(f"{_BLUE}!{_RESET} {_WHITE}{prompt}{_RESET}")
    
    while True:
        path = input("Enter save path: ").strip()
        if not path:
            print("Please enter a valid file path.")
            continue
        
        # Convert relative path to absolute if needed
        if not os.path.isabs(path):
            path = os.path.abspath(path)
        
        # Add extension if not present and extension is specified
        if ext and len(ext) > 0:
            file_ext = os.path.splitext(path)[1].lstrip(".")
            if not file_ext:
                path += f".{ext[0]}"
        
        # Check if directory exists
        dir_path = os.path.dirname(path)
        if not os.path.exists(dir_path):
            try:
                os.makedirs(dir_path)
            except Exception as e:
                print(f"Cannot create directory: {e}")
                continue
        
        break

    filename = os.path.basename(path)

    if isinstance(content, (bytes, bytearray)):
        with open(path, "wb") as f:
            f.write(content)
    else:
        with open(path, "w", encoding="utf-8", errors="ignore") as f:
            f.write(content)
    
    abs_path = os.path.abspath(path)
    print(f"Saved: {_ORANGE}{filename}{_RESET} at {abs_path}\n")

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
    cover_file = read_file("Choose an MP3 audio file (cover)", ext=["mp3"])
    
    if not cover_file:
        raise ValueError("No cover file selected, exiting program.")

    secret_file = read_file("Choose a secret file", ext=[])
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
    
    n_lsb = read_cli(
        "Enter the number of LSBs to use (1-4): ",
        return_type=int,
        valid_inputs=[1, 2, 3, 4]
    )

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
    stego_file = read_file("Choose an MP3 audio file (stego)", ext=["mp3"])
    
    if not stego_file:
        raise ValueError("No stego file selected, exiting program.")

    n_lsb = read_cli(
        "Enter the number of LSBs used (1-4): ",
        return_type=int,
        valid_inputs=[1, 2, 3, 4]
    )

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