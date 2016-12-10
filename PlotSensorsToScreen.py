#! /usr/bin/python

import usbserial
import sys
import time
import numpy as np
import datetime
from datetime import datetime as dt
import matplotlib
matplotlib.use('GTKAgg')
from matplotlib import pyplot as plt
import time

#plt.ion()
hfmt = matplotlib.dates.DateFormatter('%H:%M:%S')

try:
  baud = sys.argv[1]
except:
  baud=38400


points = None
  
if baud:
  usbser = usbserial.USBserial(baud)
  
  fig = plt.figure(figsize=(18,12))
  ax1 = fig.add_subplot(231)
  ax2 = fig.add_subplot(232)
  ax3 = fig.add_subplot(234)
  ax4 = fig.add_subplot(235)
  ax5 = fig.add_subplot(236)
  plt.show(False)
  plt.draw()
  #plt.tight_layout()

  for ax in [ax1, ax2, ax3, ax4, ax5]:
    start = dt.now()-datetime.timedelta(minutes=1)
    end = dt.now()+datetime.timedelta(minutes=1)
    ax.set_xlim(start, end)
    ax.xaxis_date()
    ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%H:%M:%S'))
  fig.autofmt_xdate()
  fig.tight_layout()
    
  while(True):
    if dt.now() > (end - datetime.timedelta(minutes=0.1)):
      for ax in [ax1, ax2, ax3, ax4, ax5]:
        start = dt.now()-datetime.timedelta(minutes=1)
        end = dt.now()+datetime.timedelta(minutes=1)
        ax.set_xlim(start, end)
        ax.xaxis_date()
    #line = ''
    #newchar = usbser.ser.read()
    #print newchar
    #while newchar != '\n':
    #  line += newchar
    line = usbser.ser.readline()
    try:
      line_list = line.split(',')
      line_array = np.array(line_list[:-1]).astype(float)
      print line_array
    except:
      continue
    if len(line_array) == 7:
      t = dt.fromtimestamp(line_array[0])

      P_kPa = line_array[1]/10.
      ax1.set_ylim(99, 102)
      ax1.plot(t, P_kPa, 'ko-')
      ax1.set_ylabel('Pressure [kPa]', fontsize=16)
      
      T_degC = line_array[2]
      ax2.set_ylim(15, 30)
      ax2.plot(t, T_degC, 'ko-')
      ax2.set_ylabel('Temperature [degrees C]', fontsize=16)

      distance_mm = line_array[3]/1000.
      distance_mm_error = line_array[4]/1000.
      ax3.set_ylim(0, 5)
      ax3.errorbar(t, distance_mm, yerr=distance_mm_error, fmt='ko-')
      ax3.set_ylabel('Distance [m]', fontsize=16)

      force_sensor_analog = line_array[5]
      ax4.plot(t, force_sensor_analog, 'ko-')
      ax4.set_ylabel('Force Sensor Analog Reading [ADC value]', fontsize=16)

      pressure_mm_H2O = line_array[6] * 6894.76 / 9800
      ax5.plot(t, pressure_mm_H2O, 'ko-')
      ax5.set_ylabel('Pressure [mm water]', fontsize=16)
      
      """
      wind_speed_m_s = line_array[-3]
      ax4.set_ylim(0, 10)
      ax4.plot(t, wind_speed_m_s, 'ko-')
      ax4.set_ylabel('Wind Speed [m/s]', fontsize=16)
      """

      fig.canvas.draw()
      

  """
  fig = plt.figure(figsize=(18,12))
  ax = fig.add_subplot(111)
  plt.show(False)
  plt.draw()

  ax.set_xlim(dt.now(), dt.now()+datetime.timedelta(minutes=20))
    
  i = 0
  while(True):
    i += 10
    t = dt.fromtimestamp(line_array[0]+time.mktime(dt.now().timetuple())+i)
    T = line_array[1]+i/10
    Hz = line_array[2]+i/100
    points = ax.plot(t, T, 'ko')[0]
    fig.canvas.draw()
  """
  
