<<<<<<< Updated upstream
import numpy as np
import wave
import serial
import serial.tools.list_ports
import time


devices = serial.tools.list_ports.comports()
ser = serial.Serial("COM3", 115200, timeout=1)

audio = []

SAMPLE_RATE = 9500
start_time = time.time()

for i in range(5*SAMPLE_RATE):
    read_data = ser.read(1)

    print(read_data[0])
    audio.append(read_data[0])

data = np.array(audio)
print(data)

#we want this in the processing stm - so in c!! ###############################

#data is received from the sampling stm

#add moving average here

#scaling
data = (data - data.min() / data.max())
data = data * 255
data = data.astype(np.uint8)

#then transmit to computer via uart2
#the ser.read in line 18 would be picking up this^

#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

filename = 'sound.wav'
with wave.open(filename, 'wb') as wf:
    wf.setnchannels(1)
    wf.setsampwidth(1)
    wf.setframerate(SAMPLE_RATE)
    wf.writeframes(data.tobytes())
=======
#Team J02

import numpy as np
import matplotlib.pyplot as plt

import serial
import serial.tools.list_ports

import wave

import time

devices = serial.tools.list_ports.comports()
ser = serial.Serial("COM5", 921600, timeout=0.2)

audio = []
SAMPLE_RATE = 22050

#first output file will be triggered by data still being sent before python tells it to stop
#it should be discarded
distanceFirst = 0

def to_wav(data, ver = -1):
    '''
    to_wav converts an array to a .wav file

    Args:
        data: the array of ints to be converted
        ver: trigger mode only: the time period the data was recorded over
    Returns:
        None
    '''
    data = data.astype(np.uint8)

    if ver == -1:
        filename = f'J01_sound_{SAMPLE_RATE}.wav'
    else:
        filename = f'J01_sound_{ver}_{SAMPLE_RATE}.wav'

    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(1)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(data.tobytes())

def to_png(data, recordingLength, ver = -1):
    '''
    to_png converts an array of data into a line graph

    Args:
        data: the array to be converted
        recordingLength: the duration of the period the data was taken
        ver: trigger mode only: the time period the data was recorded over
            -1: manual mode, so no specifier  needed
    Returns: 
        None
    '''
    arrayLength = data.size
    timeAxis = np.linspace(0, recordingLength, arrayLength)
    plt.figure() 
    plt.plot(timeAxis, data)

    plt.xlabel("Time (s)")
    plt.ylabel("Amplitude (ADC counts)")
    plt.title("Waveform of Time VS Amplitude")
    plt.ylim(0, 255)

    if ver == -1:
        plt.savefig(f"J02_waveform_{SAMPLE_RATE}.png")
    else:
        plt.savefig(f"J02_waveform_{ver}_{SAMPLE_RATE}.png")

def to_csv(data, ver = -1):
    '''
    to_csv converts an array of data into a single column csv file
    
    Args:
        data: the array to be converted
    Returns:
        None
    '''
    data = np.insert(data, 0, SAMPLE_RATE)
    if ver == -1:
        np.savetxt(f"J02_raw_data_{SAMPLE_RATE}.csv", data, delimiter=",", fmt="%03d")
    else:
        np.savetxt(f"J02_raw_data_{ver}_{SAMPLE_RATE}.csv", data, delimiter=",", fmt="%03d")


outputType = input("Output type (w for .wav, p for .png, c for .csv): ")
recordingType = input("Recording type (m for manual, d for distance): ")

if recordingType == "m":
    recordingLength = int(input("Recording time (s): "))

    ser.reset_input_buffer()
    time.sleep(0.5)

    for i in range(recordingLength*SAMPLE_RATE):
        readData = ser.read(1) 
        audio.append(readData[0])
        
    
    data = np.array(audio)

    if outputType == "w":
        to_wav(data)
    elif outputType == "p":
        to_png(data, recordingLength)
    elif outputType == "c":
        to_csv(data)
    else:
        print("Invalid output type.")

elif recordingType == "d":

    ser.write(bytes([1]))
    state = "not accepting"
    fileCounter = 0

    try:
        print("Initialising...")
        time.sleep(2.7) #make sure stm is sending nothing
        ser.reset_input_buffer()
        print("Ready!")
        while True: #loop until keyboard interrupt
            
            #wait for start bit
            while state == "not accepting":
                readData = ser.read(1)

                #wait for STM to send first value
                if readData != b'':
                    state = "accepting data"
                    startTime = time.time()
                    audio.append(readData[0])

            #wait for STM to stop sending data
            while state == "accepting data":
                readData = ser.read(1)

                if readData == b'':
                    endTime = time.time()
                    state = "not accepting"

                    if distanceFirst == 0:
                        distanceFirst = 1
                        break
                    
                    data = np.array(audio)

                    if outputType == "w":
                        to_wav(data, fileCounter)
                    elif outputType == "p":
                        recordingLength = endTime - startTime
                        to_png(data, recordingLength, fileCounter)
                    elif outputType == "c":
                        to_csv(data, fileCounter)
                    else:
                        print("Invalid output type.")

                    audio = []
                    fileCounter += 1
                    startTime = time.time()
                    
                    break
                else:
                    audio.append(readData[0])

    except KeyboardInterrupt:
        ser.write(bytes([0]))
        print("Exiting distance trigger mode.")

else:
    print("Invalid recording type.")


>>>>>>> Stashed changes
