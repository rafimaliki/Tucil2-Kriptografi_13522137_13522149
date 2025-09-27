"""
MP3 Audio Steganography Application
Main entry point for the steganography program
"""

from utils.io import print_splash, input_mode, input_embed, input_extract, write_file  
from algorithm.stego import embed, extract

def main():
    """Main application function."""
    try:
        print_splash()
        mode = input_mode()

        if mode == "Embed":
            cover_file, secret_file, encrypted, random_insertion, n_lsb, key = input_embed()
            
            print(f"\nEmbedding '{secret_file['filename']}' into '{cover_file['filename']}'...")
            result = embed(cover_file, secret_file, encrypted, random_insertion, n_lsb, key)
            
            output_path = write_file(result, prompt="Save stego audio file as:", ext=["mp3"])
            if output_path:
                print("Steganography embedding completed successfully!\n")
            
        elif mode == "Extract":
            stego_file, n_lsb, encrypted, random_insertion, key = input_extract()
            
            print(f"\nExtracting from '{stego_file['filename']}'...")
            result = extract(stego_file, n_lsb, encrypted, random_insertion, key)
            
            output_path = write_file(result, prompt="Save extracted secret file as:")
            if output_path:
                print("Secret file extraction completed successfully!\n")
                
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        print("Please check your inputs and try again.\n")

if __name__ == "__main__":
    main()