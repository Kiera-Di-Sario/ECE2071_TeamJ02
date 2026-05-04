import numpy as np
import matplotlib.pyplot as plt
import serial
import serial.tools.list_ports
import wave
import time

devices = serial.tools.list_ports.comports()
ser = serial.Serial("COM4", 115200, timeout=1)

audio = []
SAMPLE_RATE = 5000 

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
        filename = 'sound.wav'
    else:
        filename = f'sound_{ver}.wav'

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

    if ver == -1:
        plt.savefig("waveform.png")
    else:
        plt.savefig(f"waveform_{ver}.png")

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
        np.savetxt("raw_data.csv", data, delimiter=",", fmt="%03d")
    else:
        np.savetxt(f"raw_data_{ver}.csv", data, delimiter=",", fmt="%03d")


outputType = input("Output type (w for .wav, p for .png, c for .csv): ")
recordingType = input("Recording type (m for manual, d for distance): ")

if recordingType == "m":
    recordingLength = int(input("Recording time (s): "))

    for i in range(recordingLength*SAMPLE_RATE):
        readData = ser.read(1) 

        #actual code
        audio.append(readData[0])
    
    data = np.array(audio)
    print(data)


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
        while True: #loop until keyboard interrupt
            
            #wait for start bit
            while state == "not accepting":
                readData = ser.read(1)


                #wait for US range
                if readData[0] == 1:
                    state = "accepting data"

            #wait for stop bit
            startTime = time.time()
            while state == "accepting data":
                readData = ser.read(1)

                if readData[0] == 4:
                    endTime = time.time()
                    state = "not accepting"
                    
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


