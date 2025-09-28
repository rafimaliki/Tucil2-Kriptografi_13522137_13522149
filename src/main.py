from utils.io import print_splash, input_mode, input_embed, input_extract, write_file  
from algorithm.extract import extract
from algorithm.embed import embed

from utils.io import read_file

def main():
    
    cover_file = read_file("Choose an MP3 audio file (cover):", ext=["mp3"])
    secret_file = read_file("Choose a secret file:", ext=[])

    result = embed(cover_file, secret_file, False, True, 1, "I, am, Atomic!")
    write_file(result, prompt="Save file as:", ext=["mp3"])

    # print_splash()
    # mode = input_mode()

    # if mode == "Embed":
    #     inputs = input_embed()
    #     result = embed(*inputs)
    #     write_file(result, prompt="Save file as:", ext=["mp3"])
    # else: # mode == "Extract"
    #     inputs = input_extract()
    #     result = extract(*inputs)
        
    #     # nanti perlu info extension dari secret file sepertinya, sementara hardcode txt
    #     write_file(result, prompt="Save extracted secret file as:", ext=["txt"])

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\nAn error occurred: {e}\n")