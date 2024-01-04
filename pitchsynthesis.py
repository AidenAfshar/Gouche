import csv
import numpy as np
import statistics
from matplotlib import pyplot as plt
import argparse
import freq_note_converter
import seaborn as sns
import math

def myround(x, base=50):
    return base * round(x/base)

ap = argparse.ArgumentParser()
ap.add_argument("-f", "--file", required = True, help = "Path to the csv file containing pitches and time markers")
ap.add_argument("-t", "--time", required = False, help = "[optional] Custom range of time to read data from (e.g: -t 1,50)")
ap.add_argument("-p", "--plot", required = False, action='store_true', help = "[optional] Include to to show plot of pitches")
ap.add_argument("-c", "--hist", required = False, action='store_true', help = "[optional] Include to to a histogram of pitches")
args = vars(ap.parse_args())

# Tried using this from paper before, but wanted larger range and all quater tones (this was just Segah)
#all_notes = [0.0, 138.6, 146.8, 164.8, 179.7, 196, 220, 239.9, 261.6, 277.2, 293.7, 329.6, 349.2, 359.5, 370, 392, 415.3, 440, 479.8, 493.9, 523.2, 538.6, 554.4, 587.3, 659.3, 698.5, 718.9, 784, 880, 987.8, 1046.5, 1174.6, 1318.5, 1396.9]
all_notes = []
starting_note = 27.5
# Creating all notes with quarter tones from 55hz up 6 octaves
for i in range(240):
    frequency = (pow(2, i/24) * starting_note)
    all_notes.append(math.log(frequency/27.50)/math.log(2) * 12 * 100)

time_markers = []
cents_list = []
prev_freq = False
pitchCSV = csv.DictReader(open(args["file"]))
for row in pitchCSV:
    time, frequency, confidence = row.items()
    frequency = math.log(float(frequency[1])/27.50)/math.log(2) * 12 * 100 # Convert to cents
    #print(f"Time: {time[1]}\nFreq: {frequency[1]}\nConfidence: {confidence[1]}")
    if float(confidence[1]) > 0.9:
        time_markers.append(float(time[1]))
        cents_list.append(frequency)
        prev_freq = frequency
    elif prev_freq:
        # If low confidence, set current pitch to last high confidence pitch
        time_markers.append(float(time[1]))
        cents_list.append(prev_freq)
    else:
        # Account for empty space at begining of recording
        time_markers.append(float(time[1]))
        cents_list.append(0.0)
#print(cents_list)

#rounded_cents = [min(all_notes, key=lambda all_notes:abs(all_notes-a)) for a in cents_list]
rounded_cents = []
for cents in cents_list:
    rounded_cents.append(myround(cents))

adjusted_cents = []
step_range = 100
curr_step = 1
curr_difs = []
count = 0
cumulative_difs = []
avg_dif = 0
cumulative_dif = 0
for i in range(len(cents_list) - step_range):
    if curr_step < step_range:
        curr_step += 1
        if cents_list[i] == 0:
            curr_difs.append(0)
        else:
            curr_difs.append(rounded_cents[i] - cents_list[i])
    if curr_step == step_range:
        if cents_list[i] == 0:
            curr_difs.append(0)
            curr_step = 0
            avg_dif = sum(curr_difs)/step_range
            print(f"avg_dif: {avg_dif}")
            curr_difs = []
            for j in range(step_range):
                adjusted_cents.append(cents_list[i - step_range + j] + avg_dif)
                cents_list[i + j] = cents_list[i + j] + avg_dif
                count += 1
        else:
           curr_difs.append(rounded_cents[i] - cents_list[i])
           curr_step = 0
           avg_dif = sum(curr_difs)/step_range
           cumulative_dif += avg_dif
           curr_difs = []
           cumulative_difs.append(cumulative_dif)
           for j in range(step_range):
               adjusted_cents.append(cents_list[i - step_range + j] + avg_dif)
               #cents_list[i + j] = cents_list[i + j] + avg_dif
               rounded_cents[i + j] = rounded_cents[i + j] + avg_dif
               count += 1
    #print(f"avg_dif: {cumulative_dif}")




#adjusted_and_rounded_cents = [min(all_notes, key=lambda all_notes:abs(all_notes-a)) for a in adjusted_cents]
#adjusted_and_rounded_cents = adjusted_cents
adjusted_and_rounded_cents = []

for cents in adjusted_cents:
    adjusted_and_rounded_cents.append(myround(cents))

if args["time"]:
    start_end_time = args["time"].split(',')
    start_time = int(start_end_time[0])
    end_time = int(start_end_time[1])
    if end_time > (len(rounded_cents) - 1):
        end_time = len(rounded_cents) - 1
    if end_time < start_time:
        end_time = start_time + 1
    if start_time < 0:
        start_time = 0
    # Multiplying by ten so seconds can be input
    rounded_cents = rounded_cents[start_time*10:end_time*10]
    cents_list = cents_list[start_time*10:end_time*10]
    adjusted_and_rounded_cents = adjusted_and_rounded_cents[start_time*10:end_time*10]
    adjusted_cents = adjusted_cents[start_time*10:end_time*10]
    cumulative_difs = cumulative_difs[start_time//10:end_time//10]

print("--------------Cumulative_dif--------------------")
print(cumulative_difs)
print("--------------Cents_list--------------------")
print(cents_list)
print("---------------Rounded_list-------------------")
print(rounded_cents)

#print(cents_list)
#print(adjusted_cents)
D4Count = 0
rounded_notes = []
for cents in adjusted_and_rounded_cents:
    val = freq_note_converter.from_freq(27.5 * pow(2, (cents/1200)))
    note = f"{val.note}{val.octave}"
    if val.offset_from_note < -0.4:
        rounded_notes.append(f"{note}c")
    elif val.offset_from_note > 0.4:
        rounded_notes.append(f"{note}s")
    else:
        rounded_notes.append(note)
#print(rounded_notes)

dropped_freqs = []
for i in range(1, len(rounded_cents) - 1):
    if rounded_cents[i] != rounded_cents[i-1]:
        dropped_freqs.append(rounded_cents[i])

f2 = open(f"{args['file'][:len(args['file'])-4]}_frequencies.txt","w")
for freq in rounded_cents:
    f2.write(f"100 NewFreq {freq};\n")
f2.close()

"""
#for freq in cents_list:
#    f2.write(f"100 NewFreq {freq};\n")
print("DROPPED SET (repeated frequencies for held notes dropped)")
print(f"Mean: {np.mean(dropped_freqs)}")
print(f"Mode: {statistics.mode(dropped_freqs)}")
print(f"Median: {sorted(dropped_freqs)[len(dropped_freqs)//2]}\n")
print("FULL SET")
print(f"Mean: {np.mean(rounded_cents)}")
print(f"Mode: {statistics.mode(rounded_cents)}")
print(f"Median: {sorted(rounded_cents)[len(rounded_cents)//2]}")
"""


if args["plot"]:
    plt.figure(1)
    plt.title("Modified Pitches")
    plt.xlabel("time (ms)")
    plt.ylabel("pitch (hz)")
    plt.plot(np.arange(0, len(rounded_cents)), rounded_cents)
    plt.axhline(y=np.mean(rounded_cents), color='r', linestyle='-', label="mean")
    plt.axhline(y=statistics.mode(rounded_cents), color='b', linestyle='-', label="mode")
    plt.axhline(y=statistics.mode(dropped_freqs), color='g', linestyle='-', label="dropped mode")
    leg = plt.legend(loc='upper left')

    plt.figure(2)
    plt.title("Unmodified Pitches")
    plt.xlabel("time (ms)")
    plt.ylabel("pitch (hz)")
    plt.plot(np.arange(0, len(cents_list)), cents_list)
    plt.axhline(y=np.mean(cents_list), color='r', linestyle='-', label="mean")
    plt.axhline(y=statistics.mode(rounded_cents), color='b', linestyle='-', label="mode")
    leg = plt.legend(loc='upper left')
    """
    newfreqs = []
    for cents in adjusted_and_rounded_cents:
        newfreqs.append(27.5 * pow(2, (cents/1200)))
    plt.hist(newfreqs)
    """

    plt.figure(3)
    plt.title("NEW Pitches")
    plt.xlabel("time (ms)")
    plt.ylabel("pitch (hz)")
    plt.plot(np.arange(0, len(cumulative_difs)), cumulative_difs)
    plt.plot(np.arange(0, len(adjusted_and_rounded_cents)), adjusted_and_rounded_cents)
    plt.axhline(y=np.mean(adjusted_and_rounded_cents), color='r', linestyle='-', label="mean")
    leg = plt.legend(loc='upper left')

    if not args["hist"]:
        print("\nClose plots to proceed")
        plt.show()

if args["hist"]:
    plt.figure(4)
    plt.title("Histogram")
    sns.countplot(rounded_notes)
    print("\nClose plots to proceed")
    plt.show()
