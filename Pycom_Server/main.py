from network import Bluetooth
import time
from array import *
# import ujson
import pycom
from pysense import Pysense
# from machine import I2C
# from machine import ADC
# from network import Bluetooth
# from SHT35 import SHT35
from LIS2HH12 import LIS2HH12
import ubinascii
import binascii
import struct


BLEConnected = False

largest_number = 2 #If 2g is selected
smallest_number = largest_number / 2**12 # 12bit sensor


def connectionCallback(e):
    events = e.events()
    global BLEConnected
    if events & Bluetooth.CLIENT_CONNECTED:
        BLEConnected = True
        print("Client connected")
    elif events & Bluetooth.CLIENT_DISCONNECTED:
        BLEConnected = False
        print("Client disconnected")



def char1_cb_handler(chr, data):
    events, value = data
    if events & Bluetooth.CHAR_WRITE_EVENT:
        print("Write request")
        pycom.rgbled(int.from_bytes(bytearray(value), 'big'))
    elif events & Bluetooth.CHAR_READ_EVENT:
        print("Read Request")

def acc_write_array(duration): #Interrupt pin.
    for x in range(duration):
        add = [x, li.acceleration()]
        T.append(add)
    pass

def acc_send_array():
    for x in range(len(T)):
        a,b=T[x]
        print(str(a) + ' ' + str(b))
        print(T[x])

        iteration = T[x][0]
        x_data = T[x][1][0]
        y_data = T[x][1][1]
        z_data = T[x][1][2]

        print("Iteration:", iteration)
        print("X data:",x_data)
        print("Y data:",y_data)
        print("Z data:",z_data)

        # x_data_hex = binascii.hexlify(struct.pack('<f', x_data)
        x_data_byte = bytearray(struct.pack("f", x_data))
        y_data_byte = bytearray(struct.pack("f", y_data))
        z_data_byte = bytearray(struct.pack("f", x_data))
        print(x_data_byte, y_data_byte, z_data_byte)
        # packed_x_data = binascii.hexlify(x_data_byte)
        # print(packed_x_data)

        # print(str(x_data_hex))

        iteration_char.value(iteration)
        x_acc_char.value(x_data_byte)
        y_acc_char.value(y_data_byte)
        z_acc_char.value(z_data_byte)

        #Convert x_data string to hex and trunktate
        time.sleep(0.5)
        #x_acc_char.value(x_data)
        # y_acc_char.value(y_data)
        # z_acc_char.value(z_data)
        #x_acc_char.value(b)
    pass


# apin = ADC().channel(pin='P16')

pycom.heartbeat(False)
py = Pysense()

# sensor = SHT35(I2C(0, I2C.MASTER, baudrate=20000))
# Bluetooth().set_pin(463523)

Bluetooth().init()
Bluetooth().set_advertisement(name='LoPy', service_uuid=0x3040) # Service in dec

Bluetooth().callback(trigger=Bluetooth.CLIENT_CONNECTED |
                     Bluetooth.CLIENT_DISCONNECTED, handler=connectionCallback)

Bluetooth().advertise(True)

srv = Bluetooth().service(uuid=0x3040, isprimary=True, nbr_chars=4, start=True)

iteration_char = srv.characteristic(uuid=0x2020, properties=Bluetooth.PROP_READ, value=0xFFFF) #Total 16bit per char
x_acc_char = srv.characteristic(uuid=0x2021, properties=Bluetooth.PROP_READ, value=0xFF00) #Total 16bit per char
y_acc_char = srv.characteristic(uuid=0x2022, properties=Bluetooth.PROP_READ, value=0xFF00) #Total 16bit per char
z_acc_char = srv.characteristic(uuid=0x2023, properties=Bluetooth.PROP_READ, value=0xFF00) #Total 16bit per char

                           # Bluetooth.PROP_BROADCAST | Bluetooth.PROP_NOTIFY

# char3 = srv.characteristic(uuid=54321, properties=Bluetooth.PROP_INDICATE |
#                            Bluetooth.PROP_BROADCAST | Bluetooth.PROP_NOTIFY, value=0x00ff00)
#
# char2 = srv.characteristic(uuid=64321, value=0xff00)

# char1_cb = char2.callback(
#     trigger=Bluetooth.CHAR_WRITE_EVENT, handler=char1_cb_handler)


T = []

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




while True:
#    acc_roll = int(li.roll()*1000)
#    acc_pitch = int(li.pitch()*1000)
    T = [] # Reset array


    start_time = time.time()*1000
    acc_write_array(1000)
    end_time = time.time()*1000
    duration_time_ms = (end_time - start_time)
    print(duration_time_ms)
    #print('Written ' str(len(T)) + ' lines in ' + str(duration_time))
    #print(T)

    if BLEConnected:
        # char1.value(0xACFF)
        # x_acc_char.value(0x34F3BD43)
        # y_acc_char.value(0x36F3CE21)
        # z_acc_char.value(0x38F3AD68)

        acc_send_array()
        #a = 0xFFFF
        #char1.value(a)
        #char1.value(T)
        #char3.value(acc_pitch)
        #print("Roll: " + str(acc_roll) + "Pitch: " + str(acc_pitch))
