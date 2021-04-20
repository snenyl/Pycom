"""
This is the server side which read the data from the IMU and send it to the
Gateway.

"""

from array import *
import pycom
from pysense import Pysense
from network import Bluetooth
import ubinascii
import time
import machine
import struct
from LIS2HH12 import LIS2HH12

pycom.heartbeat(False)
py = Pysense()

# ----------- IMU Setings: -----------
li = LIS2HH12(py)
# enable acceleration readings at 50Hz
li.set_odr(6)
# ODR_10_HZ
# ODR_50_HZ
# ODR_100_HZ
# ODR_200_HZ
# ODR_400_HZ
# ODR_800_HZ

# change the full-scale to 4g
li.set_full_scale(0)
# FULL_SCALE_2G -
# FULL_SCALE_4G -
# FULL_SCALE_8G -

# set the interrupt pin as active low and open drain
# li.set_register(CTRL5_REG, 3, 0, 3)

BLEConnected = False

"""
0, 0.384736286, 0.764539453, -0.738283483
1, 0.335393275, 0.787328572, -1.059825923
2, 0.387439833, 0.783275892, -1.032749873
3, 0.394380345, 0.729525939, -1.132498242
4, 0.387325897, 0.792395934, -1.027387233
"""

#No need to send all of the data the sensor is 12bit; divide by 2^(-1)g result in smallest acceleration of 0.00048
AccData = [[0, 0.384736286, 0.764539453, -0.738283483],
           [1, 0.335393275, 0.787328572, -1.059825923],
           [2, 0.387439833, 0.783275892, -1.032749873],
           [3, 0.394380345, 0.729525939, -1.132498242],
           [4, 0.387325897, 0.792395934, -1.027387233]]

readArrayIndex = 0

def acc_write_array(): #Interrupt pin.
    global T
    T=[]
    for x in range(200):
        add = [x, li.acceleration()]
        T.append(add)
    pass


def writeToServer():
    bt = Bluetooth()
    adv = bluetooth.get_adv()
    print("Writing to client with MAC: {}".format(ubinascii.hexlify(adv.mac)))
    global connectedMAC
    connectedMAC = adv.mac
    print(connectedMAC)
    # return(0)
    pass

def goToSleepfor(sleepvalue):
    sleepvalue_ms = sleepvalue*1000
    print("Going to sleep for", str(sleepvalue) ,"seconds")
    machine.deepsleep(sleepvalue_ms)
    pass


def conn_cb (bt_o):
    events = bt_o.events()
    global BLEConnected
    if  events & Bluetooth.CLIENT_CONNECTED:
        BLEConnected = True
        print("Client connected")
        #writeToServer()
    elif events & Bluetooth.CLIENT_DISCONNECTED:
        BLEConnected = False
        print("Client disconnected")
        goToSleepfor(10)
        return(0)

def char1_cb_handler(chr, data):
    # The data is a tuple containing the triggering event and the value if the event is a WRITE event.
    # We recommend fetching the event and value from the input parameter, and not via characteristic.event() and characteristic.value()
    events, value = data
    global readArrayIndex
    if  events & Bluetooth.CHAR_READ_EVENT:
        print('Read request on char 1 {}', T[readArrayIndex][0])
        readArrayIndex = readArrayIndex + 1

        iteration = T[readArrayIndex][0]
        x_data = T[readArrayIndex][1][0]
        y_data = T[readArrayIndex][1][1]
        z_data = T[readArrayIndex][1][2]

        iteration_ba = bytearray(struct.pack("b", iteration))
        x_data_ba = bytearray(struct.pack("f", x_data))
        y_data_ba = bytearray(struct.pack("f", y_data))
        z_data_ba = bytearray(struct.pack("f", z_data))

        print(iteration, x_data, y_data, z_data)

        chr1.value(0x03)
        chr_x.value(x_data_ba)
        chr_y.value(y_data_ba)
        chr_z.value(z_data_ba)
        # chr_x.value(bytearray(struct.pack("f", x_data)))




# def char2_cb_handler(chr, data):
#     # The value is not used in this callback as the WRITE events are not processed.
#     events, value = data
#     if  events & Bluetooth.CHAR_READ_EVENT:
#         print('Read request on char 2')
#
# def char21_cb_handler(chr, data):
#     # The value is not used in this callback as the WRITE events are not processed.
#     events, value = data
#     if  events & Bluetooth.CHAR_READ_EVENT:
#         print('Read request on char 21')

bluetooth = Bluetooth()
bluetooth.set_advertisement(name='LoPy', service_uuid=0x283B52D274704517BC39E852B24739EA)
bluetooth.callback(trigger=Bluetooth.CLIENT_CONNECTED | Bluetooth.CLIENT_DISCONNECTED, handler=conn_cb)
bluetooth.advertise(True)

srv1 = bluetooth.service(uuid=0x6CADF9A03F4B4A228CBD283788B9EE5C, nbr_chars=4 ,isprimary=True)
# srv2 = bluetooth.service(uuid=0x2021, nbr_chars=3 ,isprimary=True)
#
chr1 = srv1.characteristic(uuid=0x283B52D274704517BC39E852B24739EA, properties=Bluetooth.PROP_READ, value=0x000000)
char1_cb = chr1.callback(trigger=Bluetooth.CHAR_READ_EVENT, handler=char1_cb_handler)
chr_x = srv1.characteristic(uuid=0x0CE418AAE6164546B5EE3EC89E5975D9, properties=Bluetooth.PROP_READ, value=0x000000)
chr_y = srv1.characteristic(uuid=0x80725E09370E4BD0A0A7DFB7E40BD31A, properties=Bluetooth.PROP_READ, value=0x000000)
chr_z = srv1.characteristic(uuid=0xF35C90EF359A4E83BF5D209F9C3F1E6D, properties=Bluetooth.PROP_READ, value=0x000000)

# char1_cb = chr_x.callback(trigger=Bluetooth.CHAR_READ_EVENT, handler=none)

# srv2 = bluetooth.service(uuid=1234, nbr_chars=2 ,isprimary=True)
# chr2 = srv2.characteristic(uuid=4567, value=0x1234)
# char2_cb = chr2.callback(trigger=Bluetooth.CHAR_READ_EVENT, handler=char2_cb_handler)
# chr21 = srv2.characteristic(uuid=4568, value=0x4321)
# char21_cb = chr2.callback(trigger=Bluetooth.CHAR_READ_EVENT, handler=char21_cb_handler)

# dataArray = [4, 0.384736286, 0.764539453, -0.738283483]
# dataArray_byte = bytearray(struct.pack("q", )))

#Max char size 0xFFFFFFFF Not correnct

writeOnlyOnce=0

while True:
    if BLEConnected:
        print("hello!")
        if writeOnlyOnce<1:
            writeOnlyOnce=1
            acc_write_array()
            print(T)


        # print(dataArray)
        # print(dataArray_byte)
        # # adv = bluetooth.get_adv()
        # chr1.value(dataArray_byte)
        # print(conn)
        time.sleep(1)

    else:
        time.sleep(0.1)
        #bluetooth.advertise(True)
