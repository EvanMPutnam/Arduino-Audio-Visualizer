'''
Python file to get sound from a pc and transfer it to an arduino
for audio visualization.  

Dependencies:
    pyaudio: PyAudio needs portaudio.h installed on the machine. (Conda can install this)
    numpy and scipy: For the mathy stuff
    pyserial: For communication with arduino.

    voicemeeter makes it easy to pipe the output to an input device.
'''
import pyaudio
import numpy as np
import serial
import scipy
import struct
from scipy.fftpack import fft, fftfreq
import serial.tools.list_ports
import time

#Config data
CHUNKSIZE = 1024 #Chunksize of data to get.
SAMPLE_RATE = 48000 #Sample rate of audio device
SCALE_FACTOR = 8 #Take CHUNKSIZE/SCALE_FACTOR to get LED count.  Unless HALF == True
MAG_CAP = 25000 #Cap for magnitude value.  Adjust this value to play around.

#If this value is true then it will be one continuos spectrum and not two identical halves.
HALF = False #LED Count, if True, is now (CHUNKSIZE/2)/(SCALE_FACTOR/2)

#Value to trigger debug statements
DEBUG = False

#Com port data
COM_PORT = "COM3"
COM_BAUD = 115200

#Audio device info
AUDIO_DEVICE_INDEX = 1


def magnData(data):
    data_len = len(data) 
    audioFrequency = fft(data)

    #Gets every x element.
    if HALF:
        512
        audioFrequency = audioFrequency[0:int(audioFrequency.size/2):int(SCALE_FACTOR/2)]
        magnFreq = np.abs(audioFrequency)
        magnFreq = magnFreq / float(data_len)
        magnFreq = magnFreq**2
    else:
        audioFrequency = audioFrequency[0:audioFrequency.size:SCALE_FACTOR]
        magnFreq = np.abs(audioFrequency)
        magnFreq = magnFreq / float(data_len)
        magnFreq = magnFreq**2
    if data_len % 2 > 0:
        magnFreq[1:len(magnFreq)] = magnFreq[1:len(magnFreq)] * 2
    else:
        magnFreq[1:len(magnFreq) -1] = magnFreq[1:len(magnFreq) - 1] * 2
    return magnFreq

def main():
    #Create our magnificent pyaudio object
    p = pyaudio.PyAudio()
    print(p.get_default_host_api_info()) #This prints out audio information.

    #Create comm port and connect
    print(list(serial.tools.list_ports.comports()))
    ser = serial.Serial(COM_PORT, COM_BAUD)

    #Give a little time to connect.
    time.sleep(5)
    print("Done loading COM port")

    #Printing out info on all your sound devices.
    for i in range(p.get_device_count()):
        dev = p.get_device_info_by_index(i)
        print((i, dev['name'], dev['maxInputChannels'], dev['defaultSampleRate']))


    audio_device_index = int(input("Enter Device Number: "))
    #Don't cross the streams.
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=SAMPLE_RATE, 
                    input=True, frames_per_buffer=CHUNKSIZE, input_device_index=AUDIO_DEVICE_INDEX)
    print("Done opening audio stream")


    #Print out the number of leds that should be used on the arduino.
    if HALF:
        print("Nubmer of LEDs = " + str((CHUNKSIZE/2)/(SCALE_FACTOR/2)))
    else:
        print("Nubmer of LEDs = " + str(CHUNKSIZE/SCALE_FACTOR) )

    #Main loop
    while True:
        #Get array of current audio data
        data = stream.read(CHUNKSIZE, exception_on_overflow=False)
        #Do some fancy unpacking.
        data = scipy.array(struct.unpack("%dh"%(CHUNKSIZE), data))
        #Get magnitudes of raw spectrum data.
        data = magnData(data)

        #Byte array to send to the arduino
        byteArr = []
        #Iterate over the mag data.
        for i in range(0, int(CHUNKSIZE/SCALE_FACTOR)):
            #Value from 0 to 254 to set to light
            newValue = 254*(data[i]/(MAG_CAP))
            
            #If greater than threshold set to max.
            if int(newValue) > 254:
                if DEBUG:
                    print(newValue)
                    print(data[0])
                    print("")
                byteArr.append(254)
            #Otherwise add to byte arr to send to arduino
            else:
                byteArr.append(int(newValue))
        #Append a stop bit.  Chose 255 to be the end of a sequence of bytes.  Led values 0-254.
        byteArr.append(int(255))

        #Write and flush.
        ser.write(bytearray(byteArr))
        ser.flush()
        #print(byteArr)


    #We should never hit these but whatever...
    stream.stop_stream()
    stream.close()
    p.terminate()

if __name__ == "__main__":
    main()
