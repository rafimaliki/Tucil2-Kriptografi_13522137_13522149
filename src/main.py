from utils.io import print_splash, input_mode, input_embed, input_extract, write_file  
from algorithm.stego import embed, extract

def main():
    print_splash()
    mode = input_mode()

    if mode == "Embed":
        inputs = input_embed()
        result = embed(*inputs)
        write_file(result, prompt="Save file as:", ext=["mp3"])
    else:
        inputs = input_extract()
        result = extract(*inputs)
        
        # nanti perlu info extension dari secret file sepertinya, sementara hardcode txt
        write_file(result, prompt="Save extracted secret file as:", ext=["txt"])

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\nAn error occurred: {e}\n")