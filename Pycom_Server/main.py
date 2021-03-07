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


BLEConnected = False


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

def acc_write_array(duration):
    for x in range(duration):
        add = [x, int(li.pitch()*1000)]
        T.append(add)
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

srv = Bluetooth().service(uuid=0x3040, isprimary=True, nbr_chars=1, start=True)

char1 = srv.characteristic(uuid=0x2020, properties=Bluetooth.PROP_READ, value=0xFF0000)

                           # Bluetooth.PROP_BROADCAST | Bluetooth.PROP_NOTIFY

# char3 = srv.characteristic(uuid=54321, properties=Bluetooth.PROP_INDICATE |
#                            Bluetooth.PROP_BROADCAST | Bluetooth.PROP_NOTIFY, value=0x00ff00)
#
# char2 = srv.characteristic(uuid=64321, value=0xff00)

# char1_cb = char2.callback(
#     trigger=Bluetooth.CHAR_WRITE_EVENT, handler=char1_cb_handler)


T = []

li = LIS2HH12(py)
li.set_odr(6)

while True:
    #time.sleep(0.1)

    acc_roll = int(li.roll()*1000)
    acc_pitch = int(li.pitch()*1000)
    # json = ujson.dumps({"h": h, "c": c, "v": apin()})

    time.sleep(5)

    acc_write_array(50)
    print(T)


    # for x in range(10):
    #     add = [x, int(li.pitch()*1000)]
    #     T.append(add)
    #     print(T)
    # else:
    #     print('Completed')

    if BLEConnected:
        #char1.value(0x42)
        char1.value(T)
        #char3.value(acc_pitch)
        #print("Roll: " + str(acc_roll) + "Pitch: " + str(acc_pitch))
