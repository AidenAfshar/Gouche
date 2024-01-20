import crepe
from scipy.io import wavfile
import argparse
import os
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("-d", "--directory", required = True, help = "Path to directory containing wav files")
args = vars(ap.parse_args())

#os.mkdir(f"{args[directory]}/pitchDetector")

directory = f"{Path.cwd()}{args['directory']}"

for filename in os.listdir(directory):
    song_file = os.path.join(directory, filename)
    # checking if it is a file
    if os.path.isfile(song_file) and song_file[len(song_file) - 3:] == "wav":
        sr, audio = wavfile.read(song_file)
        time, frequency, confidence, activation = crepe.predict(audio, sr, viterbi=True)
        frequency_file = open(f"{song_file[:len(song_file)-4]}_frequencies.txt","w")
        frequency_file.write("time,frequency,confidence\n")
        for i in range(len(time)):
            frequency_file.write(f"{time[i]},{frequency[i]},{confidence[i]}\n")
        frequency_file.close()
