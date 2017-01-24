# package installation instructions: https://pythonhosted.org/PyDAQmx/

# this software controls any i2c enabled device through an NI USB-6501 using PCA9564 I2C Bus
# input format:
# data lines: port 0 line 0:7
# control lines: port 2 line 0:4 (sequentally wire line 0: write strobe...line 4: A1 address input)
# interrupt line: port 1 line 0

from PyDAQmx import *
import numpy as np
import time

# the following takes in bits from external file and formats them to be used by NI DAQ to be sent to the i2c bus
# the byte list is a list that contains lists of bits that correspond to a single byte
# read about format for sending bytes to bus in text file that is in the same folder as this file
byte_list = []
text = open('bytes_to_send.txt', 'r')
text_length = int(text.tell())

counter = 0
bit_count = 0
bit_list = [0] * 8
while(True):
    if(bit_count == 8):
        bit_count = 0
        bit_list.reverse() # this function present for orientation of bits being sent and wiring with DAQ
                           # comment out this function as needed for specific microcontroller communications
        byte_list.append(list(bit_list))
    val = text.read(1)
    if(val == '' or val == '#'):
        break
    bit_list[bit_count] = int(val)
    bit_count += 1
    counter += 1

# print byte_list
text.close()

# The following code initializes communication between the NI DAQ and the I2C Bus.
# Then the data is sent through the bus to a microcontroller.


data = Task() # for the data module
control1 = Task() # for the control module
control2 = Task() # for using 2 different ports
interrupt = Task()
data_readback = Task() # for reading back from data lines

#set up for small daq
data.CreateDOChan("Dev2/port0/line0:7","",DAQmx_Val_ChanPerLine*5) #change from 5 to 8 for DAQ 9174
control1.CreateDOChan("Dev2/port2/line0:2","",DAQmx_Val_ChanPerLine*3)
control2.CreateDOChan("Dev2/port2/line3:4","",DAQmx_Val_ChanPerLine*2)
interrupt.CreateDIChan("Dev2/port1/line0","",DAQmx_Val_ChanPerLine)

data.StartTask()
control1.StartTask()
control2.StartTask()
interrupt.StartTask()

# test for i2c bus functionality
# to initialize everything to 0
# the following code is for the NI-cDAQ 9174
# data.WriteDigitalLines(1,1,10.0,DAQmx_Val_GroupByChannel,np.array([0,0,0,0,0,0,0,0], dtype = np.uint8),None,None)
# time.sleep(.01)
# control.WriteDigitalLines(1,1,10.0,DAQmx_Val_GroupByChannel,np.array([0,0,0], dtype = np.uint8),None,None)
# time.sleep(.01)
# data.WriteDigitalLines(1,1,10.0,DAQmx_Val_GroupByChannel,slave_address,None,None)
# time.sleep(.01)
# control.WriteDigitalLines(1,1,10.0,DAQmx_Val_GroupByChannel,np.array([1,0,0], dtype = np.uint8),None,None)
# time.sleep(.01)
# data.WriteDigitalLines(1,1,10.0,DAQmx_Val_GroupByChannel,np.array([1,0,1,0,0,0,1,1], dtype = np.uint8),None,None)
# control.WriteDigitalLines(1,1,10.0,DAQmx_Val_GroupByChannel,np.array([0,0,1], dtype = np.uint8),None,None)
# time.sleep(.01)
# control.WriteDigitalLines(1,1,10.0,DAQmx_Val_GroupByChannel,np.array([1,0,1], dtype = np.uint8),None,None)
# data.WriteDigitalLines(1,1,10.0,DAQmx_Val_GroupByChannel,np.array([1,0,1,0,0,1,1,1], dtype = np.uint8),None,None)
# time.sleep(.01)
# control.WriteDigitalLines(1,1,10.0,DAQmx_Val_GroupByChannel,np.array([0,0,1], dtype = np.uint8),None,None)
# time.sleep(.01)
# control.WriteDigitalLines(1,1,10.0,DAQmx_Val_GroupByChannel,np.array([1,0,1], dtype = np.uint8),None,None)
# data.WriteDigitalLines(1,1,10.0,DAQmx_Val_GroupByChannel,np.array([1,0,1,0,0,0,1,1], dtype = np.uint8),None,None)
# control.WriteDigitalLines(1,1,10.0,DAQmx_Val_GroupByChannel,np.array([0,0,1], dtype = np.uint8),None,None)
# time.sleep(.01)
# control.WriteDigitalLines(1,1,10.0,DAQmx_Val_GroupByChannel,np.array([1,0,1], dtype = np.uint8),None,None)

# code for small NI DAQ
sent_byte = 0
while(sent_byte<len(byte_list)):
    print byte_list[sent_byte]
    # initialize everything to 0 and control to do nothing
    data.WriteDigitalLines(1,1,10.0,DAQmx_Val_GroupByChannel,np.array([0,0,0,0,0,0,0,0], dtype = np.uint8),None,None)
    control1.WriteDigitalLines(1,1,10.0,DAQmx_Val_GroupByChannel,np.array([1,1,0], dtype = np.uint8),None,None)
    control2.WriteDigitalLines(1,1,10.0,DAQmx_Val_GroupByChannel,np.array([0,1], dtype = np.uint8),None,None)
    # control 1 = write/read strobe, chip enable
    # control 2 = register selection (on page 5 of PCA9564 data sheet)

    # data for data register
    data.WriteDigitalLines(1,1,10.0,DAQmx_Val_GroupByChannel,np.array(byte_list[sent_byte], dtype = np.uint8),None,None)
    # load data into data register
    control1.WriteDigitalLines(1,1,10.0,DAQmx_Val_GroupByChannel,np.array([0,1,0], dtype = np.uint8),None,None)
    control1.WriteDigitalLines(1,1,10.0,DAQmx_Val_GroupByChannel,np.array([1,1,0], dtype = np.uint8),None,None)
    # select control register
    control2.WriteDigitalLines(1,1,10.0,DAQmx_Val_GroupByChannel,np.array([1,1], dtype = np.uint8),None,None)
    # master transmitter initialization
    if(sent_byte == 0):
        data.WriteDigitalLines(1,1,10.0,DAQmx_Val_GroupByChannel,np.array([1,1,1,0,0,0,1,0], dtype = np.uint8),None,None)
        # load data into control register
        control1.WriteDigitalLines(1,1,10.0,DAQmx_Val_GroupByChannel,np.array([0,1,0], dtype = np.uint8),None,None)
        control1.WriteDigitalLines(1,1,10.0,DAQmx_Val_GroupByChannel,np.array([1,1,0], dtype = np.uint8),None,None)
        # master transmitter with start bit
        data.WriteDigitalLines(1,1,10.0,DAQmx_Val_GroupByChannel,np.array([1,1,1,1,0,1,1,0], dtype = np.uint8),None,None)
        time.sleep(0.5)
    else:
        #master transmitter continuation for nth byte
        data.WriteDigitalLines(1,1,10.0,DAQmx_Val_GroupByChannel,np.array([1,1,1,0,0,0,1,0], dtype = np.uint8),None,None) # deasserts signal interrupt
    # load into control register one more time to send next byte
    control1.WriteDigitalLines(1,1,10.0,DAQmx_Val_GroupByChannel,np.array([0,1,0], dtype = np.uint8),None,None)
    control1.WriteDigitalLines(1,1,10.0,DAQmx_Val_GroupByChannel,np.array([1,1,0], dtype = np.uint8),None,None)
    sent_byte += 1
    # stop command after succesful transmission of other bytes
    if(sent_byte == len(byte_list)):
        data.WriteDigitalLines(1,1,10.0,DAQmx_Val_GroupByChannel,np.array([1,1,1,0,1,0,1,0], dtype = np.uint8),None,None)
        # load into control register to send stop command
        control1.WriteDigitalLines(1,1,10.0,DAQmx_Val_GroupByChannel,np.array([0,1,0], dtype = np.uint8),None,None)
        control1.WriteDigitalLines(1,1,10.0,DAQmx_Val_GroupByChannel,np.array([1,1,0], dtype = np.uint8),None,None)
    # time.sleep(.5)

# for reading from interrupt output
# Python might be slow enough to where reading interrupt is pretty much unnecessary
buff = np.array([1], dtype = np.uint8)
x = 0
while(x<10):
    interrupt.ReadDigitalLines(1, -1,DAQmx_Val_GroupByChannel,buff,1,None,None,None)
    print buff
    time.sleep(.01)
    x+=1




# switch to reading mode of data lines so status register can be read back from microcontrollers.
data.StopTask()
status_code = np.array([0,0,0,0,0,0,0,0], dtype = np.uint8)
data_readback.CreateDIChan("Dev2/port0/line0:7","",DAQmx_Val_ChanPerLine*8)
# access status register
control2.WriteDigitalLines(1,1,10.0,DAQmx_Val_GroupByChannel,np.array([0,0], dtype = np.uint8),None,None)
# load status register to parallel data bus
control1.WriteDigitalLines(1,1,10.0,DAQmx_Val_GroupByChannel,np.array([1,1,0], dtype = np.uint8),None,None)
control1.WriteDigitalLines(1,1,10.0,DAQmx_Val_GroupByChannel,np.array([1,0,0], dtype = np.uint8),None,None)
control1.WriteDigitalLines(1,1,10.0,DAQmx_Val_GroupByChannel,np.array([1,1,0], dtype = np.uint8),None,None)
# read error status from register and display in terminal
data_readback.ReadDigitalLines(1, -1,DAQmx_Val_GroupByChannel,status_code,8,None,None,None)
print status_code




# data.StopTask() # stopped above when I needed to use same lines to read out
control1.StopTask()
control2.StopTask()
interrupt.StopTask()
data_readback.StopTask()
