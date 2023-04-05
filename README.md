# FE5680A Calibration Tool
This is a quick tool I put together in python for communicating with a FE5680A Rubidium Reference over the built in serial port. It allows for reading the currently programmed offset value, as well as setting the offset value, either temporarily or to the EEPROM to survive power cycles.

This tool was written for Python 2.7, and requires the serial library. (I know things should be written for Python 3. Python 2.7 is all I had available on the older system I have connected to my FE5680A. It should not be difficult to update for Python 3.)

## Options
```
nigel@time:~ $ sudo python FE5680A.py -h
FE 5680A Calibration Program
Options:
  -h / --help  \- Print this help message
  --dev=   \- The serial device to connect to. Example: /dev/ttyUSB0
  --set=   \- Set frequency offset. 2,147,483,647= +383 Hz, -2,147,483,647= -383 Hz
  --save   \- Save the frequency offset to EEPROM. Alternately set offset, but do not save.
  --get  \- Get the current frequency offset.
  --debug  \- Print additional debugging info.
```
`--dev` is used to set what serial device should be used to communicate with the reference, and is a required option.

`--set` is used to configure the offset on the reference. This is given in a raw integer value between -2147483647 and 2147483647. Do *NOT* enter your desired Hz offset here. You will need to either calculate the desired ratio, or trial and error your value until you reach the desired calibration.

`--save` is used to save the `--set` value to EEPROM to survive future power cycles. `--save` *MUST* be used in combination with `--set`.

`--get` is used to read the current offset value from the device. This is a default option and will be run if no options are set, as well as after any `--set` operation, as the device does not return confirmation data from a `--set` command alone.

`--debug` outputs additional debugging data consisting of the raw hexadecimal values for commands being sent to the device as well as the device response data.

### Example Get
```
nigel@time:~ $ sudo python FE5680A.py --dev="/dev/ttyUSB2" --get
Successful Read! Frequency Offset Value: -330
```

### Example Set without Save
```
nigel@time:~ $ sudo python FE5680A.py --dev="/dev/ttyUSB2" --set=-332
Sending Set Command. Set value: -332
Successful Read! Frequency Offset Value: -332
```

### Example Set with Save
```
nigel@time:~ $ sudo python FE5680A.py --dev="/dev/ttyUSB2" --set=-332 --save
Sending Set & Save Command. Set value: -332
Successful Read! Frequency Offset Value: -332
```

## References
There are a number of references available for these devices, though some resources are no longer available, which led me to put together this tool. A quick list of references I saw, but is by no means exhaustive:
- https://www.ka7oei.com/10_MHz_Rubidium_FE-5680A.html
- https://www.qsl.net/zl1bpu/PROJ/Ruby4.htm
- https://www.rdrelectronics.com/skip/feb/FE-5680A.pdf
- https://www.qsl.net/zl1bpu/PROJ/FEI%20specs.pdf
- https://hamwan.org/files/FE/FE-5680A%20Technical%20Manual.pdf
- https://www.febo.com/pipermail/time-nuts/2011-March/055351.html
- https://www.febo.com/pipermail/time-nuts/2011-April/056256.html
