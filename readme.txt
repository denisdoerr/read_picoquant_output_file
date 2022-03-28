This folder contains demo programs (incl source code) for reading
out files from MHLib Programming Library for MultiHarp 150/160 (https://github.com/PicoQuant/MH150-Demos)

This is just a demo it is  not designed to 
routinely convert these files to ASCII. This would in most cases be 
inefficient and of little practical value. The objective is to enable 
users to write their own file reading and analysis programs.
The code is based on the Picoquant demo Read_PTU.py   (https://github.com/PicoQuant/PicoQuant-Time-Tagged-File-Format-Demos/tree/master/PTU/Python)
as sample files "T3_1Mhz_dark.out" , "T2_1Mhz_dark.out" can be used for T3 mode and T2 mode respectively 

Unlike the ptu files, the out files do not contain a haeder, i.e. some parameters like T2 or T3 format or the time resolution and the repetition rate of the laser have to be entered by hand.  This demo is written for MultiHarp 150/160, if someone uses another TCSPC device, he can simply replace the corresponding part of the code. for this, depending on the device matching function (readHT2 or readHT2 or readPT3 or readPT2) and "recordType" must be selected (see Read_PTU.py script 
https://github.com/PicoQuant/PicoQuant-Time-Tagged-File-Format-Demos/tree/master/PTU/Python) 
