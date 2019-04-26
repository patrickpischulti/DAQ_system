import os
import sys
import matplotlib.pyplot as plt
import numpy as np
import time
import random
import picamera
import Adafruit_DHT
from time import sleep
from datetime import datetime
from daqhats import hat_list, HatIDs, mcc118

def my_plotter(ax, data1, data2, param_dict):
    """
    A helper function to make a graph

    Parameters
    ----------
    ax : Axes
        The axes to draw to

    data1 : array
       The x data

    data2 : array
       The y data

    param_dict : dict
       Dictionary of kwargs to pass to ax.plot

    Returns
    -------
    out : list
        list of artists added
    """
    out = ax.plot(data1, data2, **param_dict)
    return out

def set_parameters(arguments):
    if arguments.find('-r') != -1:
        rampMode = True
        print('Its set!')

set_parameters(str(sys.argv))

timeRamp = float(sys.argv[1])
timeInterval = float(sys.argv[2])

#File path
startTime = datetime.now()
filePath = "/home/pi/Desktop/tests/" + startTime.strftime("%Y-%m-%d-%H%M%S")
logFileName = filePath + "/logfile.txt"
figureName = filePath + "/figure.png"

try:
    os.mkdir(filePath)
except OSError:
    print("Failed to create the directory %s" % filePath)
else:
    print("Successfully created the directory %s" % filePath)

#print('Arg 1 = ' + timeRamp + ' Arg 2 = ' + timeInterval)

#Initialize DHT22
sensor = Adafruit_DHT.DHT22
pin = 4

#Initialize MCC daqhat boards
# get hat list of MCC daqhat boards
board_list = hat_list(filter_by_id = HatIDs.ANY)
if not board_list:
    print("No boards found")
    sys.exit()

f = open(logFileName, "x")
f = open(logFileName, "a")

#Frequency in Hz and convert into seconds
freqRamp = 1
delayRamp = 1/freqRamp

runDAQ = True

#date = datetime.now().strftime("%Y%m%d_%H-%M-%S")
#print(date)

timeData = []
yData = []

i = 0
j = 0
startTime = time.time()

while i < timeRamp:
    if i == 0:
        print('Started ramping recording at %s...' %time.ctime())
        #print('Run = %s' %i)
    timeElapsed = time.time() - startTime

    timeData.append(round(timeElapsed,0))
    yData.append(round(float(random.random())*1000,0))

    #Capture Photo
    picName = str(timeElapsed) + '.jpg'
    completeFilePath = filePath +"/"+ picName

    with picamera.PiCamera() as camera:
        camera.resolution = (1280,720)
        camera.capture(completeFilePath)
        #print("Captured at: " + picTime)

    #Capture Envrionmental conditions
    humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
    f.write("Test number: " + str(timeElapsed))

    #Read Analog input
    for entry in board_list:
        if entry.id == HatIDs.MCC_118:
            #print("Board {}: MCC 118".format(entry.address))
            board = mcc118(entry.address)
            x_out = board.a_in_read(0)
            y_out = board.a_in_read(1)
            z_out = board.a_in_read(2)
            #print("Ch {0}: {1:.3f}".format(0, x_out))
            #print("Ch {0}: {1:.3f}".format(1, y_out))
            #print("Ch {0}: {1:.3f}".format(2, z_out))

    sleep(delayRamp)
    i += 1

print('Finished ramping recording finished at %s ' %time.ctime())

#x = np.arange(0, 10, 0.2)
#y = np.arrange(2,4,5,4,6)
#fig1, ax = plt.subplots()
#ax.plot(x, y)
#fig1.savefig('/Users/patrickpischulti/Pictures/fig.png')

try:
    while runDAQ == True:
        if j == 0:
            print('Main DAQ started at %s...' %time.ctime())
        #print('DAQ loop iteration = %s' %j)

        timeElapsed = time.time() - startTime
        timeData.append(round(timeElapsed,0))
        yData.append(round(float(random.random())*1000,0))

        #Capture Photo
        picName = str(timeElapsed) + '.jpg'
        completeFilePath = filePath +"/"+ picName

        with picamera.PiCamera() as camera:
            camera.resolution = (1280,720)
            camera.capture(completeFilePath)
            #print("Captured at: " + picTime)

        #Capture Envrionmental conditions
        humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
        f.write("Test number: " + str(timeElapsed))

        #Read Analog input
        for entry in board_list:
            if entry.id == HatIDs.MCC_118:
                #print("Board {}: MCC 118".format(entry.address))
                board = mcc118(entry.address)
                x_out = board.a_in_read(0)
                y_out = board.a_in_read(1)
                z_out = board.a_in_read(2)
                #print("Ch {0}: {1:.3f}".format(0, x_out))
                #print("Ch {0}: {1:.3f}".format(1, y_out))
                #print("Ch {0}: {1:.3f}".format(2, z_out))

        j += 1
        sleep(timeInterval)

except KeyboardInterrupt:
    for x in timeData:
      print(x)

    fig, ax = plt.subplots(1, 1)
    my_plotter(ax, timeData, yData, {'marker': 'x'})
    fig.savefig(figureName)

    print('...DAQ Stopped!')
