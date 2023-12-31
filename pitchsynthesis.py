import csv
import numpy as np
import statistics
from matplotlib import pyplot as plt
import argparse

ap = argparse.ArgumentParser()
ap.add_argument("-f", "--file", required = True, help = "Path to the csv file containing pitches and time markers")
ap.add_argument("-t", "--time", required = False, help = "[optional] Custom range of time to read data from (e.g: -t 1,50)")
ap.add_argument("-p", "--plot", required = False, help = "[optional] Include to to show plot of pitches")
args = vars(ap.parse_args())

# Tried using this from paper before, but wanted larger range and all quater tones (this was just Segah)
#all_notes = [0.0, 138.6, 146.8, 164.8, 179.7, 196, 220, 239.9, 261.6, 277.2, 293.7, 329.6, 349.2, 359.5, 370, 392, 415.3, 440, 479.8, 493.9, 523.2, 538.6, 554.4, 587.3, 659.3, 698.5, 718.9, 784, 880, 987.8, 1046.5, 1174.6, 1318.5, 1396.9]
all_notes = []
starting_note = 55
# Creating all notes with quarter tones from 55hz up 6 octaves
for i in range(240):
    all_notes.append(pow(2, i/24) * starting_note)

time_markers = []
frequency_list = []
prev_freq = False
pitchCSV = csv.DictReader(open(args["file"]))
for row in pitchCSV:
    time, frequency, confidence = row.items()
    #print(f"Time: {time[1]}\nFreq: {frequency[1]}\nConfidence: {confidence[1]}")
    if float(confidence[1]) > 0.9 and float(frequency[1]) < 700:
        tempDict = [float(time[1]), float(frequency[1])]
        time_markers.append(float(time[1]))
        frequency_list.append(float(frequency[1]))
        prev_freq = float(frequency[1])
    elif prev_freq:
        time_markers.append(float(time[1]))
        frequency_list.append(prev_freq)
    else:
        time_markers.append(float(time[1]))
        frequency_list.append(0.0)

rounded_freqs = [min(all_notes, key=lambda all_notes:abs(all_notes-a)) for a in frequency_list]

if args["time"]:
    start_end_time = args["time"].split(',')
    start_time = int(start_end_time[0])
    end_time = int(start_end_time[1])
    if end_time > (len(rounded_freqs) - 1):
        end_time = len(rounded_freqs) - 1
    if end_time < start_time:
        end_time = start_time + 1
    if start_time < 0:
        start_time = 0
    # Multiplying by ten so seconds can be input
    rounded_freqs = rounded_freqs[start_time*10:end_time*10]

dropped_freqs = []
for i in range(1, len(rounded_freqs) - 1):
    if rounded_freqs[i] != rounded_freqs[i-1]:
        dropped_freqs.append(rounded_freqs[i])

f2 = open(f"{args['file'][:len(args['file'])-4]}_frequencies.txt","w")
for freq in rounded_freqs:
    f2.write(f"100 NewFreq {freq};\n")
f2.close()

#for freq in frequency_list:
#    f2.write(f"100 NewFreq {freq};\n")
print("DROPPED SET (repeated frequencies for held notes dropped)")
print(f"Mean: {np.mean(dropped_freqs)}")
print(f"Mode: {statistics.mode(dropped_freqs)}")
print(f"Median: {sorted(dropped_freqs)[len(dropped_freqs)//2]}\n")
print("FULL SET")
print(f"Mean: {np.mean(rounded_freqs)}")
print(f"Mode: {statistics.mode(rounded_freqs)}")
print(f"Median: {sorted(rounded_freqs)[len(rounded_freqs)//2]}")

if args["plot"]:
    plt.figure(1)
    plt.title("Modified Pitches")
    plt.xlabel("time (ms)")
    plt.ylabel("pitch (hz)")
    plt.plot(np.arange(0, len(rounded_freqs)), rounded_freqs)
    plt.axhline(y=np.mean(rounded_freqs), color='r', linestyle='-', label="mean")
    plt.axhline(y=statistics.mode(rounded_freqs), color='b', linestyle='-', label="mode")
    plt.axhline(y=statistics.mode(dropped_freqs), color='g', linestyle='-', label="dropped mode")
    leg = plt.legend(loc='upper left')

    plt.figure(2)
    plt.title("Unmodified Pitches")
    plt.xlabel("time (ms)")
    plt.ylabel("pitch (hz)")
    plt.plot(np.arange(0, len(frequency_list)), frequency_list)
    plt.axhline(y=np.mean(frequency_list), color='r', linestyle='-', label="mean")
    plt.axhline(y=statistics.mode(rounded_freqs), color='b', linestyle='-', label="mode")
    leg = plt.legend(loc='upper left')

    plt.figure(3)
    plt.title("Histogram")
    plt.hist(rounded_freqs)

    print("\nClose plots to proceed")
    plt.show()
