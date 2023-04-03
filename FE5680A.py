#!/usr/bin/env python
import sys
import math
import time
import getopt
import serial
import struct

def usage():
  print("FE 5680A Calibration Program")
  print("Options:")
  print("  -h / --help          - Print this help message")
  print("  --dev=               - The serial device to connect to. Example: /dev/ttyUSB0")
  print("  --set=               - Set frequency offset. 2,147,483,647= +383 Hz, -2,147,483,647= -383 Hz")
  print("  --save               - Save the frequency offset to EEPROM. Alternately set offset, but do not save.")
  print("  --get                - Get the current frequency offset.")
  print("  --debug              - Print additional debugging info.")
  sys.exit()

def main(argv):
  opt_dev = False
  opt_set = False
  opt_set_val = 0
  opt_save = False
  opt_get = False
  opt_debug = False

  try:
    opts, args = getopt.getopt(argv, "h", ["help","set=","dev=","save","get","debug"])
  except getopt.GetoptError as err:
    print(str(err))
    usage()
    sys.exit(2)

  for opt, arg in opts:
    if opt == '-h':
      usage()
    if opt == "--dev":
      opt_dev = arg
    if opt == "--set":
      opt_set = True
      opt_set_val = int(arg)
    if opt == "--save":
      opt_save = True
    if opt == "--get":
      opt_get = True
    if opt == "--debug":
      opt_debug = True

  # Check if --save or --set has been used at the same time as --get
  if (opt_set or opt_save) and opt_get:
    print("ERROR: Cannot --set/--save and --get at the same time. Remove conflicting flag and try again.")
    usage()

  # Check if the set value is within range
  if (opt_set_val > 2147483647 or opt_set_val < -2147483647):
    print("ERROR: --set value is out of range. Expected range: -2147483647 to 2147483647")
    usage()

  # Check if --dev was set
  if (opt_dev == False):
    print("ERROR: Please specify serial device.")
    usage()

  # Open the serial connection
  try:
  	serial_conn = serial.Serial(opt_dev, 9600, timeout=1)
  except serial.SerialException as e:
  	print("ERROR: Unable to open serial port. Exception: %s" % e)
  	usage()
  
  # Assemble the set command bytes and send them if we're doing a set operation
  chksum = False
  if opt_set == True:
    if opt_save == True:
      command = [0x2C, 0x09, 0x00, 0x25, 0x00, 0x00, 0x00, 0x00, 0x00]
    else:
      command = [0x2E, 0x09, 0x00, 0x27, 0x00, 0x00, 0x00, 0x00, 0x00]
    
    # Break up the set value into four bytes
    command[7] = opt_set_val & 0xFF
    command[6] = (opt_set_val >> 8) & 0xFF
    command[5] = (opt_set_val >> 16) & 0xFF
    command[4] = (opt_set_val >> 24) & 0xFF
    
    # Calculate the checksum
    for x in range(0,8):
      chksum ^= command[x]
    
    command[8] = chksum

    # DEBUG
    if opt_debug:
      print 'Sending Set Command: [{}]'.format(', '.join(hex(x) for x in command))
    
    if opt_save == True:
      print("Sending Set & Save Command. Set value: %d" % opt_set_val)
    else:
      print("Sending Set Command. Set value: %d" % opt_set_val)
    
    # Write out the command
    serial_conn.write(command)
    
  # Set up the read command
  command = [0x2D, 0x04, 0x00, 0x29]
  
  # Flush the serial input buffer so any further reads should be data we get back from the device
  serial_conn.reset_input_buffer()
  
  # DEBUG
  if opt_debug:
    print 'Sending Get Command: [{}]'.format(', '.join(hex(x) for x in command))
     
  # Write out the command
  serial_conn.write(command)

  # Read back the response
  response = serial_conn.read(9)
  
  # Close out the serial port
  serial_conn.close()
  
  # DEBUG
  if opt_debug:
    print 'Response Data: [{}]'.format(', '.join(hex(ord(x)) for x in response))
  
  # Check if we got the expected 9 byte response
  if (len(response) >= 9):
    # Validate that the command header is what we expect
    if (ord(response[0]) == 0x2D and ord(response[1]) == 0x09 and ord(response[2]) == 0x00 and ord(response[3]) == 0x24):
      # Calculate the checksum
      response_chksum = 0
      for i in range(4, 8):
        response_chksum ^= ord(response[i])
    
      # Unpack the returned data
      response_data = struct.unpack('>BBBBlB', response)    

      # Validate the checksum
      if (response_chksum == response_data[5]):
        # Checksum is valid
        print("Successful Read! Frequency Offset Value: %d" % response_data[4])
      else:
        # Checksum invalid
        print("ERROR: Checksum was invalid on response data. Raw data received: ")
        print(response.encode('hex'))
  
    # Command header isn't what we expected.
    else:
      print("ERROR: Unexpected response command header. Raw data received: ")
      print(response.encode('hex'))
  
  # We didn't get 9 bytes
  else:
    print("ERROR: Unexpected response length. Raw data received: ")
    print(response.encode('hex'))
  
  # We're done. Exit.
  sys.exit()

if __name__ == "__main__":
  main(sys.argv[1:])
