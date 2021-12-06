# importing libraries 
from genericpath import exists
import speech_recognition as sr 
import os 
from pydub import AudioSegment
from pydub.silence import split_on_silence
from pathlib import Path
from tqdm import tqdm

# folder for corresponding .wav files
original_audio_files = r"C:\Repos\speech-to-text\audio"

# create a speech recognition object
r = sr.Recognizer()

# a function that splits the audio file into chunks
# and applies speech recognition
def get_large_audio_transcription(path):
    # open the audio file using pydub
    sound = AudioSegment.from_wav(path)  
    # split audio sound where silence is 700 miliseconds or more and get chunks
    chunks = split_on_silence(sound,
        # experiment with this value for your target audio file
        min_silence_len = 500,
        # adjust this per requirement
        silence_thresh = sound.dBFS-14,
        # keep the silence for 1 second, adjustable as well
        keep_silence=500,
    )
    folder_name = "audio-chunks"
    # create a directory to store the audio chunks
    if not os.path.isdir(folder_name):
        os.mkdir(folder_name)
    whole_text = ""
    # process each chunk 
    for i, audio_chunk in enumerate(chunks, start=1):
        # export audio chunk and save it in
        # the `folder_name` directory.
        file_name = Path(path).stem
        chunk_filename = os.path.join(folder_name, f"{file_name}_chunk{i}.wav")
        audio_chunk.export(chunk_filename, format="wav")
        # recognize the chunk
        with sr.AudioFile(chunk_filename) as source:
            audio_listened = r.record(source)
            # try converting it to text
            try:
                text = r.recognize_google(audio_listened)
            except sr.UnknownValueError as e:
                #print("Error:", str(e))
                pass
            else:
                text = f"{text.capitalize()}. "
                #print(chunk_filename, ":", text)
                whole_text += text
                f = open("text-output.txt", "a")
                f.write("[{}] - {}".format(chunk_filename, text))
                f.write("\n")
                f.close()
    # return the text for all chunks detected
    return whole_text

def search_text_input(file_name, string_to_search):
    line_number = 0
    list_of_results = []
    # Open the file in read only mode
    with open(file_name, 'r') as read_obj:
        # Read all lines in the file one by one
        for line in read_obj:
            # For each line, check if line contains the string
            line_number += 1
            if string_to_search in line:
                # If yes, then add the line number & line as a tuple in the list
                list_of_results.append((line_number, line.rstrip()))
    # output the search result to console
    print("Total matches: {}".format(len(list_of_results)))
    for res in list_of_results:
        print("Line #{} : {}".format(res[0], res[1]))

def ask_for_user_input():
    search_string = input("Search for..?: ")
    search_text_input("text-output.txt", search_string)
    question = input("Continue with search? [y]/[n]: ")
    if question == "n":
        quit()
    elif question == "y":
        search_string = input("Search for..?: ")
        search_text_input("text-output.txt", search_string)
        question = input("Continue with search? [y]/[n]: ")
    else:
        print("Invalid Input! - Try again")

def search_for_audio_files(audio_file_path):
    audio_files = []
    audio_snippets_folder = audio_file_path
    for file in os.listdir(audio_snippets_folder):
            audio_files.append(os.path.join(audio_snippets_folder, file))
    return audio_files

if __name__ == "__main__":

    # check if output file already exists or not
    if not os.path.exists("text-output.txt"):

        # if output file does not exists, begin with speech to text
        for audio_track in tqdm(search_for_audio_files(original_audio_files), desc="Processing audio files..."):
            get_large_audio_transcription(audio_track)
        
        # ask user to search for a word in all audio files
        ask_for_user_input()
        
    # if output file already exists, user can directly search words from it without processing audio files first
    else:
        while True:
            ask_for_user_input()