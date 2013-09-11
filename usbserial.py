"""
usberial.py: object-oriented much-easier-than-before interaction and clock-setting 
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

import glob
import sys
from datetime import datetime as dt # I know Serial has "time", but my code is written for this separately
import socket
import re
import time
from select import select
import random

class usbserial(object):
  import serial # Keep serial objects inside self
                # THIS IS THE ONLY NON-STANDARD LIBRARY NEEDED

  """
  Made to work with the data loggers designed by Andy Wickert
  
  Hard-coded for 57600 baud rate (easy to change this)
  
  There will be some dependancy on the code on the loggers, but I will try to 
  abstract/generalize/limit this as much as possible
  """

  def __init__(self):
    self.port = None # Default to this
    self.logger_name = None
    # Instantiate serial connection as part of this
    self.scan()
    if self.port:
      print "Created Serial object for communications"
      self.ser = self.serial.Serial(self.port, 57600, timeout=1)
    else:
      sys.exit("Logger does not seem to be connected. Exiting.")

  def scan(self, mode="Automatic"):
    """
    Scan for available ports. Return a list of device names (should be just 1 USB, plugged in).

    Original "scanlinux":
    Scan for serial ports.
    adapters.

    Uses pySerial (http://pyserial.sf.net)
    (C) 2009 <cliechti@gmx.net>

    Changes by Andy Wickert, 22 Dec 2010:
    * Name changed ("USB" appended)
    * Printing of variable stopped
    * Only search for USB serial and give a varname
    * Error message and exit for port out of range

    7-8 February 2010 (ADW): made cross-platform and more modular
    """

    self.port = None # Default to this - in case not going through __init__

    if mode == "manual" or mode == "Manual" or mode == "M" or mode == "m":
      # Should be uncommon, but have an option to choose to do it manually
      print "Manual mode selected"
      self.port = self.manual_port_define()
    else:
      # Linux
      if sys.platform[:5] == 'linux': # let's just check first 5, since this should still work if Linux goes up from 2.X... I hope
        #print "Rock on, geek! You're using Linux."
        print "OS = Linux :)"
        # First scan for FTDI, then scan for ATmel/ACM
        self.portlocs = ['/dev/ttyUSB*', '/dev/ttyACM*']
        for portloc in self.portlocs:
          if self.port == None:
            self.findUSB(portloc)
          else:
            break
      # Mac
      elif sys.platform == 'darwin':
        print "You're using a Mac! Starving artist with a sense of style?"
        # Try cu first, calling unit supposed to be better
        self.portlocs = ['/dev/cu.usbserial*', '/dev/tty.usbserial*']
        for portloc in self.portlocs:
          if self.port == None:
            self.findUSB(portloc)
          else:
            break
      elif sys.platform[:3] == 'win': 
        #print "You're using Windows."
        print "You're using Windows.\nWait, you got this working on Windows? Excellent! Tell me how!"
        print "Automatic serial port selection doesn't work as easily in Windows,\n\
              so it hasn't been implemented - sorry!"
        self.manual_port_define()
    # Check http://stackoverflow.com/questions/1205383/listing-serial-com-ports-on-windows
    # for how to do this better in Windows
    #          Serial port autoselection is a bit more difficult in Windows, so be\n\
    #          prepared to need to enter the serial port number (COM3, COM4, ...)\n\
    #          manually.'
    #    port_acquired = 0
    #    while port_acquired == 0 and portnum < 20:
      else:
        unrecognized_OS()
        
  def findUSB(self, portloc):

    portseek = glob.glob(portloc) # Hope there's only one that comes up for this!

    if len(portseek) > 1: # Error message & quit if 2+ ports found. If this happens, may have to do manually
      print 'portseek: >1 USB serial port (' + portloc + ') found'
      print 'ports found:', portseek
      print 'Can not tell where to write data. Manual selection required.'
      self.manual_port_define()
    elif len(portseek) == 0: # Error message & quit if no ports are found.
      print 'No USB serial ports (' + portloc + ') found.'
      if portloc == self.portlocs[-1]:
        print ""
        print "No additional locations to automatically search for ports."
        print "(ttyUSB* = FTDI; ttyACM* = Arduino UNO ATmel USB/Serial.)"
        print 'Can not tell where to write data. Manual selection required.'
        self.manual_port_define()
      else:
        print "Trying next USB/Serial mount location..."
    else:
      print "Serial port acquired:",
      print portseek[0]
      self.port = portseek[0]


  def manual_port_define(self):

    print ""
    print 'Follow the instructions to manually set  the port, or type "q" to quit.'
    print ""
    if sys.platform[:3] == 'win':
      portnum = raw_input('Please type the COM port number (e.g., "3" for COM3) to which the\n\
                           Arduino-based device is attached.\n>>>COM: ')
      self.port = 'COM' + str(portnum) # Should already be string, but just in case
    else:
      self.port = raw_input('Please type your serial port path (e.g., /dev/ttyUSB0).\n>>>Port path = ')
      
    if self.port == 'q':
      sys.exit("\n\t>>> Could not find communications port. Ta ta!. <<<\n")

  def unrecognized_OS(self):
    print 'Sorry! Your operating system is not recognized. We search for\n\
           serial ports on Linux (linux*), Mac (darwin), and Windows (win*)\n\
           ... what year is it, and what OS are you using?\n\
           Switching to manual input.'
    self.manual_port_define()


  def DS3231_set(self):
    """
    Set a DS3231 Real-time clock (RTC)
    For use with my modified version of Eric Ayars RTC library
    Should work just as well with the DS3232
    Or (I'd bet) with most other Dallas/Maxim I2C interface RTCs

    Written by Andy Wickert, 14--15 May 2011
     
    Uses DateTime, pySerial, and my usbserial module

    INPUT STRING IN THE FOMRAT:
    yymmddDhhmmssx
    e.g., "1105092190115x" for 2011 May 9 Monday 7:01:15pm
    (from Eric's blog, http://hacks.ayars.org/)
    I do not follow this day-of-week convention; I follow python's in that I
    have 1=Monday (not 1=Sunday-->7=Saturday, as here)
    
    I don't account for latency between the device and the computer; 
    I should add now += 2 or something after dt.utcnow()
    """
    
    # Get port if needed; should be already set, but...
    if self.port:
      pass
    else:
      self.scan()

    # Get UTC time
    now = dt.utcnow()
    now = dt.timetuple(now)

    # Get numbers and make strings
    # Year
    # MUST FORMAT STRINGS TO BE ZERO-PADDED
    year = "%02d"%(now[0]-2000) # get last 2 digits; will work until 2100
    month = "%02d"%(now[1])
    day = "%02d"%(now[2])
    day_of_week = str(now[6]+1) # 0--6 --> 1--7, where 1=Monday--7=Sunday
    hour = "%02d"%(now[3])
    minute = "%02d"%(now[4])
    second = "%02d"%(now[5])

    # Combine into date setting string to send
    time = year + month + day + day_of_week + hour + minute + second + 'x'

    # And send it to set the time
    self.ser.write(time)
    
    # And print some human-readable output
    self.name()
    print time + ' sent'


  def key_lines(self, line):
    """
    Respond to logger's prompts
    """
    
    if self.logger_name == None and line.startswith("<"):
      # Get logger's name
      #self.logger_name = re.findall('\<.*\>', line)[0]
      self.logger_name = re.findall('(?<=\<)(.*?)(?=\>)', line)[0]

    # Then regex out the logger name, leaving only the message
    line = re.split('\<.*\>\:\s', line)[-1]
    
    if line.startswith("********************** Logger"):
      # Have to tell logger that Python terminal is here!
      self.ser.write("p")
      # Placed the funny comments over here: stack overflow otherwise
      self.logger_comments()
    elif line.startswith("HELLO, COMPUTER"):
      # Have to tell logger that Python terminal is here!
      self.name()
      print "Hello, " + self.logger_name + "."
      self.ser.write("p")
    elif line.startswith("Current UNIX time stamp according to logger is") or line.startswith("UNIX TIME STAMP ON MY WATCH IS:"):
      # Get and print human-readable time
      time.sleep(2)
      print line
      line2 = line[:-2] # rmv \r\n
      #try:
      logger_time_stamp = int(re.findall('\d*$', line2)[0])
      #except:
      #  logger_time_stamp = -9999 # use this as an error value, for before the clock has been set at all
      computer_time_stamp = int(round(time.time(),0)) # b/c integer precision on logger
      self.name()
      print "[Computer] - human-readable UTC time is:", dt.utcfromtimestamp(logger_time_stamp)
      time.sleep(1.5)
      diff = computer_time_stamp - logger_time_stamp
      self.name()
      print "Logger clock is <", str(diff), "> second(s) behind computer clock"
      if abs(diff) > 30:
        self.name()
        print "The clocks need to be reset! (Logger may or may not realize.)"
    elif line.startswith("Uh-oh: that doesn't sound right"):
      # Need to reset clock
      time.sleep(1.5)
      self.name()
      print "Got that, logger."
      time.sleep(1.5)
      self.name()
      print "Please give me your time over the next 5 seconds."
      time.sleep(1.5)
      self.time_compare()
      self.time_set()
    elif line.startswith("How does that compare to you, computer?"):
      self.time_compare()
    elif line.startswith("Would you like to set the"):
      self.choose_to_set_clock()
    elif line.startswith("Logger initialization complete"):
      # Put an extra space in there before the rest of the logger info comes in.
      print ""
    elif line.startswith("Now beginning to log."):
      time.sleep(1.5)
      print "<" + self.logger_name + ">: ",
      print "... and remember, don't drop me into a moulin by 'mistake'!"


  def choose_to_set_clock(self):
    time.sleep(1.5)
    self.name()
    print ("Defaulting Y to in 10 seconds...")
    self.clock_set_choice = None
    while self.clock_set_choice != 'y' and self.clock_set_choice != 'Y' and self.clock_set_choice != 'n' and self.clock_set_choice != 'N':
      self.name();
      self.clock_set_choice = raw_input("Set clock? y/n: ")
      self.ser.write(self.clock_set_choice)
      if self.clock_set_choice == 'y':
        # Send along time to set
        time.sleep(0.1)
        self.time_set()
      else:
        print self.ser.readline()
    print self.ser.readline()

  def logger_comments(self):
    gs = random.randint(0,10)
    print "<" + self.logger_name + ">: ",
    if gs == 0:
      print "<" + self.logger_name + ">: ",
      print("Greetings, fellow travelers!")
      time.sleep(1.5)
      print "<" + self.logger_name + ">: ",
      print "Well, you're traveling, at least. I can't move on my own..."
    elif gs == 1:
      print "<" + self.logger_name + ">: ",
      print "My creator whispered to me that he would really like"
      print "                         to go to the field sometime..."
    elif gs == 2:
      print "Hey - mobile organics!" 
      time.sleep(1.5)
      print "<" + self.logger_name + ">: ",
      print "Did you bring me that Harry Potter box set?"
      time.sleep(1.5)
      print "<" + self.logger_name + ">: ",
      print "...it sure gets awfully boring up here all by myself..."
    elif gs == 3:
      print "<" + self.logger_name + ">: ",
      print "What's the temperature? How much snow?"
      time.sleep(1.5)
      print "<" + self.logger_name + ">: ",
      print "Demands, demands, demands."
    elif gs == 4:
      print "<" + self.logger_name + ">: ",
      print "To the bat cave!"
    elif gs == 5:
      print "<" + self.logger_name + ">: ",
      print "Quick! Close my case! I'm naked!"
    elif gs == 6:
      print "<" + self.logger_name + ">: ",
      print "Please make sure that I am securely affixed."
    elif gs == 7:
      print "How would you like to be strapped to a pole and abandoned?"
      time.sleep(1.5)
      print "<" + self.logger_name + ">: ",
      print "So tell me WHY I'm still working for you...?"
    elif gs == 8:
      print "<" + self.logger_name + ">: ",
      print "Could you tell me a story?"
      time.sleep(1.5)
      print "<" + self.logger_name + ">: ",
      print "And then I'll retell it to the wolves and bears and turtles."
      time.sleep(1.5)
      print "<<ALPHA WOLF: awooooooooooooooooooooooooooooo.>>"
      time.sleep(1.5)
      print "<<TURTLE: [SILENCE]>>"
    elif gs == 9:
      print "Wheeeeeee! Aren't you happy to be outdoors?"
    print "******************************************************************"
    print ""
    time.sleep(1.5)

  def time_compare(self):
    time.sleep(2)
    self.ser.write("g")
    print ""
    print "External device time  |  Computer time              " 
    print "----------------------------------------------------"
    line = None
    i = 0
    while i < 5:
      line = self.ser.readline()
      if line:
        utcin = int(line)
        print dt.utcfromtimestamp(utcin), "  |  ", dt.utcnow()
        #print line, "  |  ", dt.utcnow()
        line = None
        i += 1
        # ADD FILE WRITING PART!
    print "----------------------------------------------------"
    print ""

  def time_set(self):
    self.name()
    print("OK, logger. I am now transferring my time to you.");
    time.sleep(1.5)
    self.name()
    print("There may be a little latency, but you shouldn't lag my time by");
    time.sleep(1.5)
    self.name()
    print("more than a couple seconds.");
    time.sleep(1.5)
    self.DS3231_set()
    print self.ser.readline()
    print "External device time  |  Computer time              " 
    print "----------------------------------------------------"
    line = None
    i = 0
    while i < 5:
      line = self.ser.readline()
      if line:
        line = line[:-2]
        print line, "  |  ", dt.utcnow()
        line = None
        i += 1
    print "----------------------------------------------------"
    print ""
    self.name()
    print("Hopefully that's better - otherwise, no idea what went wrong!")      
  
  def name(self):
    """
    print computer's name
    """
    print("<" + socket.gethostname() + ">: "),


