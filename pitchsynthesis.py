import pandas as pd
import csv
from itertools import repeat

f = open("newSegah.f0.csv", "r")

df = pd.read_csv("newSegah.f0.csv").to_dict()

input_file = csv.DictReader(open("newSegah.f0.csv"))

all_notes = [138.6, 146.8, 164.8, 179.7, 196, 220, 239.9, 261.6, 277.2, 293.7, 329.6, 349.2, 359.5, 370, 392, 415.3, 440, 479.8, 493.9, 523.2, 538.6, 554.4, 587.3, 659.3, 698.5, 718.9, 784, 880, 987.8, 1046.5, 1174.6, 1318.5, 1396.9]

def evaluate(expected_values, measurements):
    if not expected_values:
        raise ValueError('Expected values should be a non-empty sequence.')
    expected_values = sorted(expected_values)
    measurements = sorted(measurements)
    expected_iter = iter(expected_values)
    left_value = next(expected_iter)
    try:
        right_value = next(expected_iter)
    except StopIteration:
        # there is only one expected value
        yield from repeat(left_value,
                          len(measurements))
        return
    for evaluated_count, measurement in enumerate(measurements):
        while measurement > right_value:
            try:
                left_value, right_value = right_value, next(expected_iter)
            except StopIteration:
                # rest of the measurements are closer to max expected value
                yield from repeat(right_value,
                                  len(measurements) - evaluated_count)
                return

        def key(expected_value):
            return abs(expected_value - measurement)

        yield min([left_value, right_value],
                  key=key)



synthesized_audio = []
frequency_list = []
prev_freq = False

for row in input_file:
    time, frequency, confidence = row.items()
    #print(f"Time: {time[1]}\nFreq: {frequency[1]}\nConfidence: {confidence[1]}")
    if float(confidence[1]) > 0.8:
        tempDict = [float(time[1]), float(frequency[1])]
        synthesized_audio.append(tempDict)
        frequency_list.append(float(frequency[1]))
        prev_freq = float(frequency[1])
    elif prev_freq:
        synthesized_audio.append([float(time[1]), prev_freq])
        frequency_list.append(prev_freq)
    else:
        synthesized_audio.append([float(time[1]), 0.0])
        frequency_list.append(0.0)

evaluated = evaluate(all_notes, frequency_list)
f.close()

final_freqs = []
i = 0

for item in evaluated:
    final_freqs.append([synthesized_audio[i][0], item])
    i += 1

print(final_freqs)

f2 = open("freqs.txt","w+")
for freq in final_freqs:
    f2.write(f"{freq[0]}, {freq[1]}\n")
