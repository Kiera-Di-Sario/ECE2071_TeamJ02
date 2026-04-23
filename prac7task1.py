import numpy as np
import wave
import serial
import serial.tools.list_ports
import time


devices = serial.tools.list_ports.comports()
ser = serial.Serial("COM3", 115200, timeout=1)

#we want this in the processing stm - so in c!! ###############################
audio = []

SAMPLE_RATE = 9500
start_time = time.time()

for i in range(5*SAMPLE_RATE):
    #instead of this, it receives from uart1
    read_data = ser.read(1)

    print(read_data[0])
    audio.append(read_data[0])

data = np.array(audio)
print(data)

data = (data - data.min() / data.max())
data = data * 255
data = data.astype(np.uint8)

#then transmit to computer via uart2

#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

filename = 'sound.wav'
with wave.open(filename, 'wb') as wf:
    wf.setnchannels(1)
    wf.setsampwidth(1)
    wf.setframerate(SAMPLE_RATE)
    wf.writeframes(data.tobytes())