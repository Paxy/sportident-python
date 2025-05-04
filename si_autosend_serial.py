#!/usr/bin/env python3
#
#    Copyright (C)    2019  Per Magnusson <per.magnusson@gmail.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
This example reads the station programmed to autosend the data and redirects to UART1 port to be transfered over Meshtastic network
Sample of read data:
53|233177|12:14:09
53|233385|12:14:32
53|233173|12:14:37
53|233174|12:14:46
53|233176|12:14:55
"""

from sireader2 import SIReader, SIReaderException, SIReaderControl
import sys
import serial


try:
    si = SIReader()
    reader=SIReaderControl(si)
    print('Connected to station on port ' + si.port)
except:
    print('Failed to connect to an SI station on any of the available serial ports.')
    exit()


ser = serial.Serial(
  port='/dev/ttyS1',
  baudrate=57600,
  bytesize=8,
  parity='N',
  stopbits=1,
  timeout=1
)

while True:    
    punches=reader.autosend_punch()
    if len(punches) > 0:
        message = f"{punches[0]}|{punches[1]}|{punches[2].time().isoformat(timespec='seconds')}\r\n"
        bmsg=message.encode('utf-8')
        ser.write(bmsg)
        print(message)




