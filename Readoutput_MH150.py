# Read_OUT.py    Read binary files recorded by PQ device (MH150) with demo library
# This is demo code. Use at your own risk. No warranties.
# Denis Doerr, PicoQUant GmbH, March 2022

# Note that marker events have a lower time resolution and may therefore appear 
# in the file slightly out of order with respect to regular (photon) event records.
# This is by design. Markers are designed only for relatively coarse 
# synchronization requirements such as image scanning. 

# T Mode data are written to an output file [filename]
# We do not keep it in memory because of the huge amout of memory
# this would take in case of large files. Of course you can change this, 
# e.g. if your files are not too big. 
# Otherwise it is best process the data on the fly and keep only the results.

import time
import sys
import struct
import io
import os


# global variables
global syncrate 
global inputfile
global outputfile
global recNum
global oflcorrection
global truensync
global globRes
global numRecords
global isT2

# manual input, from here the settings are defined 

isT2=False #put "False" here if you analyse file measured in T3 mode and "True" if you analyse file measured in T3 mode
syncrate =999993.333333  #use here syncrate of your Laser.
#In T2 mode this value is not used. 
#We use   999993.333333 Hz value from our laserdriver for our demo.

globRes=8.000000e-11  #use here time resolution of TCSPC device.
#In T3 mode this value is not used. 
#We use  the max time resolution 8.000000e-11 s   of Mh150 for our demo.

   
#for T2 data use the max resolution 8.000000e-11 s  of Mh150, for T3 date the max resilution is 1/reprate
#Note the global resolution is dependent on min resolution of your device (see manual)
#and binning selected in your record software  in our example we use Mh150 with binning 0

# input file path 
inputfilepath="T3_1Mhz_dark.out" 
#outputfile path (is automatically created by adding output to the beginning of the inputfile name )
outputfilepath="output_" + inputfilepath.rstrip(".out")+".txt"
#outputfile=outputfilepath
inputfile = open(inputfilepath, "rb") #inputfile
outputfile = io.open(outputfilepath, "w+", encoding="utf-16le")

#end of manual input 

def gotOverflow(count):
    global outputfile, recNum
    outputfile.write("%u OFL * %2x\n" % (recNum, count))

def gotMarker(timeTag, markers):
    global outputfile, recNum
    outputfile.write("%u MAR %2x %u\n" % (recNum, markers, timeTag))

def gotPhoton(timeTag, channel, dtime):
    global outputfile, isT2, recNum
    if isT2==True:
        outputfile.write("%u CHN %1x %u %8.0lf\n" % (recNum, channel, timeTag,\
                         (timeTag * globRes * 1e12)))
       
    else:
        outputfile.write("%u CHN %1x %u %8.0lf %10u\n" % (recNum, channel,\
                         timeTag, (timeTag * globRes * 1e9), dtime))
        
        
#records number from filesize, works  becouse the file has no header
#number of records (numRecords)  is file size (in bytes) /record length (32 bites or 4 bytes) 

file_size = os.path.getsize(inputfilepath)
numRecords=int(file_size/4)
print('number of records is ',numRecords)     
        
        

#definition of reading routine for the file recorded  T3 and T2 Modes readHT3 and readHT2 respectively
#Note for this example we use Multiharp 150 
#but for different devices from picoquant you will need different reading routins, 
#all individual cases are listed in the script readptu.py (https://github.com/PicoQuant/PicoQuant-Time-Tagged-File-Format-Demos/tree/master/PTU/Python)

def readHT3(version):
#Note the version in "readHT3(version)""   could be 1 o 2 for this example we use Multiharp 150
#where version needs to be set to = 2 the settings for other devices see  script readptu.py
#https://github.com/PicoQuant/PicoQuant-Time-Tagged-File-Format-Demos/tree/master/PTU/Python
    
    global inputfile, outputfile, recNum, oflcorrection, numRecords
    
    T3WRAPAROUND = 1024
    for recNum in range(0, numRecords):
        try:
            recordData = "{0:0{1}b}".format(struct.unpack("<I", inputfile.read(4))[0], 32)
        except:
            print("The file ended earlier than expected, at record %d/%d."\
                  % (recNum, numRecords))
            exit(0)
        
        special = int(recordData[0:1], base=2)
        channel = int(recordData[1:7], base=2)
        dtime = int(recordData[7:22], base=2)
        nsync = int(recordData[22:32], base=2)
#Note in case of T3 measurements the the 32 bits records consist of overflows bit 0-1 channel number bit 1-7
#time  between sync and photoevent bits 7-22 number of sync pulses bits 22-32
        if special == 1:
            if channel == 0x3F: # Overflow 0x3F
                # Number of overflows in nsync. If 0 or old version, it's an
                # old style single overflow
                if nsync == 0 or version == 1:
                    oflcorrection += T3WRAPAROUND
                    gotOverflow(1)
                else:
                    oflcorrection += T3WRAPAROUND * nsync
                    gotOverflow(nsync)
            if channel >= 1 and channel <= 15: # markers
                truensync = oflcorrection + nsync
                gotMarker(truensync, channel)
        else: # regular input channel
            truensync = oflcorrection + nsync
            gotPhoton(truensync, channel, dtime)
        if recNum % 100000 == 0:
            sys.stdout.write("\rProgress: %.1f%%" % (float(recNum)*100/float(numRecords)))
            sys.stdout.flush()

def readHT2(version):
#Note the version in "readHT2(version)""   could be 1 o 2 for this example we use Multiharp 150
#where version needs to be set to = 2 the settings for other devices see  script readptu.py 
#https://github.com/PicoQuant/PicoQuant-Time-Tagged-File-Format-Demos/tree/master/PTU/Python
    global inputfile, outputfile, recNum, oflcorrection, numRecords
    T2WRAPAROUND_V1 = 33552000
    T2WRAPAROUND_V2 = 33554432
    for recNum in range(0, numRecords):
        try:
            recordData = "{0:0{1}b}".format(struct.unpack("<I", inputfile.read(4))[0], 32)
        except:
            print("The file ended earlier than expected, at record %d/%d."\
                  % (recNum, numRecords))
            exit(0)
        
        special = int(recordData[0:1], base=2)
        channel = int(recordData[1:7], base=2)
        timetag = int(recordData[7:32], base=2)
#Note in case of T2 measurements the the 32 bits record consist of overflows bit 0-1 channel number bit 1-7
#time  tag for registered photon 7-32 
        if special == 1:
            if channel == 0x3F: # Overflow 0x3F
                # Number of overflows in nsync. If old version, it's an
                # old style single overflow
                if version == 1:
                    oflcorrection += T2WRAPAROUND_V1
                    gotOverflow(1)
                else:
                    if timetag == 0: # old style overflow, shouldn't happen
                        oflcorrection += T2WRAPAROUND_V2
                        gotOverflow(1)
                    else:
                        oflcorrection += T2WRAPAROUND_V2 * timetag
                        gotOverflow(timetag)
            if channel >= 1 and channel <= 15: # markers
                truetime = oflcorrection + timetag
                gotMarker(truetime, channel)
            if channel == 0: # sync
                truetime = oflcorrection + timetag
                gotPhoton(truetime, 0, 0)
        else: # regular input channel
            truetime = oflcorrection + timetag
            gotPhoton(truetime, channel+1, 0)
        if recNum % 100000 == 0:
            sys.stdout.write("\rProgress: %.1f%%" % (float(recNum)*100/float(numRecords)))
            sys.stdout.flush()

            
outputfile.write("\n-----------------------\n")
oflcorrection=0   
if isT2 == False:  
    globRes =1/syncrate
    print("MultiHarp T3 data")
    outputfile.write(" T3 data\n")
    outputfile.write("\nrecord# chan   nsync truetime/ns dtime\n")
    readHT3(2) 
#Note the version in "readHT3(version)""   could be 1 o 2 for this example we use Multiharp 150
#where version needs to be set to = 2 the settings for other devices see  script readptu.py 
   
elif isT2 == True:
    print(" T2 data")
    outputfile.write("MultiHarp T2 data\n")
    outputfile.write("\nrecord# chan   nsync truetime/ps\n")
    readHT2(2)  
#Note the version in "readHT2(version)""   could be 1 o 2 for this example we use Multiharp 150
#where version needs to be set to = 2 the settings for other devices see  script readptu.py     
       
inputfile.close()
outputfile.close()
print(

)
print('Done processed number of records ', recNum+1 )
