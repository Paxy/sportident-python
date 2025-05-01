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
Script to read out the data from an SI card and sends to UART1.

The idea is to use RPi like device as getway from USB connected SI to Meshtastic network.
Exmaple reads the SI card and sends over UART data to Meshtastic ESP device connected 
from RPi UART to ESP any GPIO port. Meshtastic is than configured to receive UART over
specified GPIO and trasfer the data as text to dafault channel using Meshtastic network.

Sample of the data:
N-7011111|F-12:31:16|H-11:41:04|54-11:43:21|39-11:47:35|52-11:55:07|44-12:02:26|38-12:04:34|70-12:10:00|62-12:11:59|45-12:17:19|47-12:27:13|100-12:30:12

Due to Meshtastic limit of 250 (including node name) characters, if the message is longer than 230 characters, the message
is splitted to 230 character each.

Example author: Petar Bojovic <petar.bojovic@paxy.in.rs>
"""

from sireader2 import SIReader, SIReaderException, SIReaderControl, SIReaderReadout
from time import sleep
from datetime import datetime
import json
import sys
import serial

from datetime import datetime

def pack_data(card_number, card_data):
    # Start with just the card number
    data = "N-" + str(card_number)
    
    # Handle special fields first with custom prefixes
    special_fields = {
        'start': 'S-',
        'finish': 'F-',
        'check': 'H-',  
        'clear': 'C-' 
    }
    
    # Process special fields in specific order
    for field, prefix in special_fields.items():
        if field in card_data and card_data[field] is not None:
            val = card_data[field]
            if isinstance(val, datetime):
                data += f"|{prefix}{val.time().isoformat(timespec='seconds')}"
    
    # Process punches (numeric control codes)
    if 'punches' in card_data:
        for control_code, punch_time in card_data['punches']:
            if punch_time is not None and isinstance(punch_time, datetime):
                data += f"|{control_code}-{punch_time.time().isoformat(timespec='seconds')}"
    
    return data

def send_data_in_chunks(result, ser):
    
    # Split into chunks of max 230 characters
    chunk_size = 230
    chunks = [result[i:i+chunk_size] for i in range(0, len(result), chunk_size)]
    
    for chunk in chunks:
        # Add termination and encode
        message = (chunk + '\r\n').encode('utf-8')
        
        # Send the chunk
        ser.write(message)
        
        # Optional: Add small delay between chunks if needed
        sleep(2)
    

try:
    if len(sys.argv) > 1:
        # Use command line argument as serial port name
        si = SIReaderReadout(port = sys.argv[1])
    else:
        # Find serial port automatically
        si = SIReaderReadout()
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
    # wait for a card to be inserted into the reader
    while not si.poll_sicard():
        sleep(1)

    # some properties are now set
    card_number = si.sicard
    card_type = si.cardtype

    # read out card data
    card_data = si.read_sicard()

    # beep
    si.ack_sicard()

    result = pack_data(card_number, card_data) 

    send_data_in_chunks(result, ser)

    print(result)

    while not si.poll_sicard():
        sleep(1)
