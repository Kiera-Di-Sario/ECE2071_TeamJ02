import numpy as np
import matplotlib.pyplot as plt
import serial
import serial.tools.list_ports
import wave

devices = serial.tools.list_ports.comports()
ser = serial.Serial("COM4", 115200, timeout=1)

audio = []
SAMPLE_RATE = 5000 

state = "not accepting"

outputType = input("Output type (w for .wav, p for .png, c for .csv): ")
recordingType = input("Recording type (m for manual, d for distance): ")

if recordingType == "m":
    recordingLength = int(input("Recording time (s): "))

    for i in range(recordingLength*SAMPLE_RATE):
        read_data = ser.read(1) 
        print(read_data[0])
        audio.append(read_data[0])

elif recordingType == "d":
    ser.write(bytes([1]))

    #while state == "not accepting":
        #wait for US range
        #if ser.read(1) == accepting data:
            #state = "accepting data"
    #while state == "accepting":
        #if ser.read(1) == stop accepting:
            #state = "finished accepting"
        #else:
            #append
             
else:
    print("Invalid recording type.")

data = np.array(audio)
print(data)


if outputType == "w":
    data = data.astype(np.uint8)
    filename = 'sound.wav'
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(1)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(data.tobytes())

elif outputType == "p":
    arrayLength = data.size
    timeAxis = np.linspace(0, recordingLength, arrayLength)
    plt.plot(timeAxis, data)
    plt.xlabel("Time (s)")
    plt.ylabel("Amplitude (ADC counts)")
    plt.title("Waveform of Time VS Amplitude")
    plt.savefig("waveform.png")

elif outputType == "c":
    data = np.insert(data, 0, SAMPLE_RATE)
    np.savetxt("raw_data.csv", data, delimiter=",", fmt="%03d")
    
else:
    print("Invalid output type.")
