from utils.io import print_splash, input_mode, input_embed, input_extract, write_file  
from algorithm.extract import extract
from algorithm.embed import embed

def main():
    print_splash()
    mode = input_mode()

    if mode == "Embed":
        inputs = input_embed()
        result = embed(*inputs)
        write_file(result, prompt="Save file as:", ext=["mp3"])

    else:  # mode == "Extract"
        inputs = input_extract()
        try:
            result, ext = extract(*inputs)
            write_file(result, prompt="Save extracted secret file as:", ext=[ext])
        except Exception as e:
            print("Extraction failed: The file may be corrupt or you may have entered the wrong key.\n")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\nAn error occurred: {e}\n")
