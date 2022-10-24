import numpy as np
import mne
import matplotlib.pyplot as plt
#Takes period segment, voltage threshold, min spike duration in seconds, max spike duration in seconds, and the sampling frequency, returns the amount of spikes in the segment udner those conditions.
def spikeamount(segment, spike_thresh, spike_min, spike_max, samp_freq):
    sample_count = 0
    spikes = 0
    spike_min = spike_min*samp_freq
    spike_max = spike_max*samp_freq
    for sample in segment:
        if sample > spike_thresh:
            sample_count += 1
        elif sample_count > spike_min and sample_count < spike_max:
            spikes += 1
            sample_count = 0
        else:
            sample_count = 0
    return spikes

#Takes a period as list of samples, desired segment length in seconds and the sampling frequency, returns a list of segments of the period {{},{},...{}}
def splitperiod(period, segment_length, sampling_freq):
    segments = []
    current_segment = []
    sample_seglen = segment_length * sampling_freq
    for i, sample in enumerate(period):
        current_segment.append(sample)
        if i%sample_seglen == 0 and i!=0:
            segments.append(current_segment)
            current_segment = []
    return segments
#takes list of spike amounts, returns list of smoothed spike amounts (smoothed spike amount is the average of M neighbour spike amount)
def smoothspikes(spikes, M):
    smoothspikes = []
    window_min = -(M//2)
    window_max = M//2
    for spike in spikes:
        curravg = 0
        if window_min<0:
            for i in range(0,M):
                curravg+=spikes[i]
            smoothspikes.append(curravg/M)
        elif window_max>=len(spikes):
            for i in range (0,M):
                curravg+=spikes[len(spikes)-1-i]
            smoothspikes.append(curravg/M)
        else:
            for i in range(window_min, window_max+1):
                curravg+=spikes[i]
            smoothspikes.append(curravg/M)
        window_min +=1
        window_max +=1
    return smoothspikes


testperiod = [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,2,3,1,1,1,1,1,1,3,3,3,3,3,3,3,3,3,3,1,1,1,1,1,1,1,1,1,1]
testspikes = [1,2,3,4,5,6,7,8,9]
print(len(testperiod))
print(splitperiod(testperiod, 3, 1))
for segment in splitperiod(testperiod, 3,1):
   # print(spikeamount(segment, 1, 1, 3, 1))
   next
print(smoothspikes(testspikes, 3))

file = "chb01_01.edf" #interictal data
data = mne.io.read_raw_edf(file)
raw_data = data.get_data()
# you can get the metadata included in the file and a list of all channels:
info = data.info
channels = data.ch_names
print(len(channels))
print(channels[20])
print(raw_data[0])
channels = []
for channel in raw_data:
    channels.append(splitperiod(channel, 5, 256))
#segments = splitperiod(raw_data[0], 5, 256)
spikes = []
for i,channel in enumerate(channels):
    spikes.append([])
    for segment in channel:
        spikes[i].append(spikeamount(segment, 0.0001,0.04, 0.07, 256))
smoothedspikes = []

for channel in spikes:
    smoothedspikes.append(smoothspikes(channel, 7))

maxspikes_inter = 0

for channel in smoothedspikes:
    for spikes in channel:
        if spikes>maxspikes_inter:
            maxspikes_inter = spikes
print(maxspikes_inter)

#file = "chb01_04.edf"
#data = mne.io.read_raw_edf(file)
#raw_data = data.get_data()
#channels = []
#for channel in raw_data:
 #   channels.append(splitperiod(channel,5,256))
#spikes = []
#for i, channel in enumerate(channels):
   # spikes.append([])
  #  for segment in channel:
 #       spikes[i].append(spikeamount(segment, 0.0001,0.04,0.07,256))
#smoothedspikes = []
#for channel in spikes:
 #   smoothedspikes.append(smoothspikes(channel,7))

#alarms = []
#for channel in smoothedspikes:
    #isdumped = 0
    #for i,spikes in enumerate(channel):
     #   if spikes>maxspikes_inter*1.3:
    #        if isdumped == 0:
   #             alarms.append(i*5)
  #              isdumped = 1
 #           print("Alarm at"+str(i*5)+"seconds")
#print(alarms)

#data = [0,0,0,0,0,0,0,0,0,0,4,4,4,0,0,0,0,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,0,0,0,0,0]
#smooth_data = smoothspikes(data,4)
#print(smooth_data)

#print(spikeamount(smooth_data, 2.99,1,4,1))

import os
# assign directory
directory = 'database'

# iterate over files in
# that directory
for filename in os.listdir(directory):
    f = os.path.join(directory, filename)
    # checking if it is a file
    if os.path.isfile(f):
        raw_data = mne.io.read_raw_edf(f).get_data()
        channels = []
        for channel in raw_data:
            channels.append(splitperiod(channel,5,256))
        spikes = []
        for i, channel in enumerate(channels):
            spikes.append([])
            for segment in channel:
                spikes[i].append(spikeamount(segment, 0.0001,0.04,0.07,256))
        smoothedspikes = []
        for channel in spikes:
            smoothedspikes.append(smoothspikes(channel,3))
        x = []
        y = []
        for channel in smoothedspikes:
            for val in channel:
                if x.count(val)==0:
                    x.append(val)
                    y.append(1)
        x.sort()
        for channel in smoothedspikes:
            for val in channel:
                y[x.index(val)] +=1
        print(x)
        plt.plot(x,y)
        plt.show()

        alarms = []
        for channel in smoothedspikes:
            alarm = []
            for i, spikes in enumerate(channel):
                if spikes>maxspikes_inter*1:
                    alarm.append(i)
            alarms.append(alarm)
        lowest_alarm = 999999
        equal = 1
        for i,channel in enumerate(alarms):
            for alarm in channel:
                equal = 1
                for j in range(0,len(alarms)):
                    if j!=i:
                        for sample in alarms[j]:
                            if sample == alarm:
                                equal +=1
                                if equal == 3:
                                    equal =1
                                    if sample*5 < lowest_alarm:
                                        lowest_alarm = sample*5
        print("Earliest alarm at " +str(lowest_alarm)+"sec in file "+f)



