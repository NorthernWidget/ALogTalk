#! /usr/bin/python

"""
ALogTalk.py: interactive front-end to usbserial.py for interaction and clock-setting 
with the ALog series of Arduino-based data loggers developed by Andrew D. Wickert

Copyright (C) 2012-2013, Andrew D. Wickert and Northern Widget LLC

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
print "************************************************************"
print "************ WELCOME TO ANDY'S LOGGER SOFTWARE! ************"
print "************************************************************"
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
  baud = sys.argv[1]
except:
  baud=14400

if baud:
  usbser = usbserial.usbserial(baud)

print "      Connecting to logger at", baud, "bits per second"
print "" 

print "*** HIT LOGGER RESET BUTTON TO ENTER SETUP (IF NOT ENTERED AUTOMATICALY) ***"
print ">> If this program gets out of sync with the logger, it may crash or behave <<"
print ">>   nonsensically. In this case, restart the logger and/or this program    <<"

line = None
while True:
  line = usbser.ser.readline()
  if line:
    if line[-2:] == '\r\n':
      print line[:-1] # Don't double-return
    else:
      print line
    usbser.key_lines(line) # Check and respond if a key line is seen



