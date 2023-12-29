import pandas as pd
import csv
from itertools import repeat
import numpy as np
from matplotlib import pyplot as plt


f = open("newSegah.f0.csv", "r")

df = pd.read_csv("newSegah.f0.csv").to_dict()

input_file = csv.DictReader(open("newSegah.f0.csv"))

all_notes = [0.0, 138.6, 146.8, 164.8, 179.7, 196, 220, 239.9, 261.6, 277.2, 293.7, 329.6, 349.2, 359.5, 370, 392, 415.3, 440, 479.8, 493.9, 523.2, 538.6, 554.4, 587.3, 659.3, 698.5, 718.9, 784, 880, 987.8, 1046.5, 1174.6, 1318.5, 1396.9]
all_notes = []
starting_note = 55
for i in range(240):
    all_notes.append(pow(2, i/24) * starting_note)
print(all_notes[24])
exit()


synthesized_audio = []
frequency_list = []
prev_freq = False

for row in input_file:
    time, frequency, confidence = row.items()
    #print(f"Time: {time[1]}\nFreq: {frequency[1]}\nConfidence: {confidence[1]}")
    if float(confidence[1]) > 0.8:
        tempDict = [float(time[1]), float(frequency[1])]
        synthesized_audio.append(float(time[1]))
        frequency_list.append(float(frequency[1]))
        prev_freq = float(frequency[1])
    elif prev_freq:
        synthesized_audio.append(float(time[1]))
        frequency_list.append(prev_freq)
    else:
        synthesized_audio.append(float(time[1]))
        frequency_list.append(0.0)

#evaluated = evaluate(all_notes, frequency_list)
f.close()


final_freqs = []
i = 0
#for freq in frequency_list:
#    final_freqs.append(min(freq, key=lambda freq:abs(freq-a)) for a in all_notes)

final_freqs = [min(all_notes, key=lambda all_notes:abs(all_notes-a)) for a in frequency_list]

#for item in evaluated:
#    final_freqs.append([synthesized_audio[i][0], item])
#    i += 1

#print(final_freqs)


f2 = open("freqs.txt","w")
for freq in final_freqs:
    f2.write(f"100 NewFreq {freq};\n")
#for freq in frequency_list:
#    f2.write(f"100 NewFreq {freq};\n")
print(np.mean(frequency_list[30:45]))

plt.figure(1)
plt.title("Modified Pitches")
plt.xlabel("time")
plt.ylabel("pitch")
plt.plot(np.arange(0, len(final_freqs)), final_freqs)
plt.figure(2)
plt.title("Unmodified Pitches")
plt.xlabel("time")
plt.ylabel("pitch")
plt.plot(np.arange(0, len(frequency_list)), frequency_list)
plt.show()
