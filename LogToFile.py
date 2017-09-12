#! /usr/bin/python

"""
LogToFile.py
  Writes the contents received over USB/Serial to a file

Copyright (C) 2016, Andrew D. Wickert
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
Contact:
Andrew D. Wickert
Northern Widget LLC
andy@northernwidget.com
"""

import usbserial
import sys

print ""
print "**************************************************************"
print "*********** WELCOME TO Simple Clock Set for ALog! ************"
print "**************************************************************"
print ""
print "                       00000000000         " 
print "                     000         000       " 
print "                    00   _         00      " 
print "                   0    /            0     " 
print "                   \   /|             \    " 
print "                    \  | \__           \   " 
print "                     \  \__  0000000000 \  " 
print "                      \    000        000  " 
print "                       \ 000   ------   000" 
print "                        000   | ALOG |  000" 
print "                         000   ------   000" 
print "                           000        000  " 
print "                             0000000000    " 
print "" 


try:
  fileName = sys.argv[1]
  print ""
  print "Will append data to the end of", fileName
  print "or create a new file with that name if it does not exist."
  print ""
except:
  sys.exit('First argument must be log file name')

try:
  baud = sys.argv[2]
except:
  baud=38400

usbser = usbserial.USBserial(baud)

print "" 
print "      Connecting to logger at", baud, "bits per second"
print "" 

f = open(fileName)

while True:
  line = usbser.ser.readline()
  f.write(line)

