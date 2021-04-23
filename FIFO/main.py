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
#from machine import Pin
import machine
from umqtt.simple2 import MQTTClient
from network import WLAN

AccData = [[0, 0.384736286, 0.764539453, -0.738283483],
           [1, 0.335393275, 0.787328572, -1.059825923],
           [2, 0.387439833, 0.783275892, -1.032749873],
           [3, 0.394380345, 0.729525939, -1.132498242],
           [4, 0.387325897, 0.792395934, -1.027387233]]

def PrivateWlanConfiguration():
    wlan = WLAN(mode=WLAN.STA)
    wlan.connect(ssid='OnePlus_7T_Pro', auth=(WLAN.WPA2, 'pycomTestingFacilityAtUiA'))
    while not wlan.isconnected():
        machine.idle()
    print("WiFi connected succesfully")
    print(wlan.ifconfig())
    pass

def mainMQTT(server="broker.hivemq.com"):
    print("Connecting to MQTT server")
    c = MQTTClient("umqtt_client", server)
    c.connect()
    for x in range(0, len(A)):
        print("Publishing")
        # PublishThis_ba = bytearray(struct.pack("b", A[x][0])) + bytearray(A[x][1]) + bytearray(A[x][2]) + bytearray(A[x][3])
        PublishThis_ba = bytearray(struct.pack("b", A[x][0])) + bytearray(struct.pack("f", A[x][1])) + bytearray(struct.pack("f", A[x][2])) + bytearray(struct.pack("f", A[x][3]))
        # PublishThis_ba = T[x]
        c.publish(b"IKT520_LAB1", PublishThis_ba)
        pass

    c.disconnect()


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
        return(0)

def BLEDisconnect():
    adv = Bluetooth().get_adv()
    conn = Bluetooth().connect(adv.mac)
    conn.disconnect()
    return(0)




def char1_cb_handler(chr, data):
    events, value = data
    if events & Bluetooth.CHAR_WRITE_EVENT:
        print("Write request")
    elif events & Bluetooth.CHAR_READ_EVENT:
        print("Read Request")

def acc_write_array(duration): #Interrupt pin.
    for x in range(duration):
        add = [x, li.acceleration()]
        T.append(add)
    pass

def acc_write_array_RAW(duration): #Interrupt pin.
    for x in range(duration):
        add = [x, li.accelerationOneGoRaw()]
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

        # print("Iteration:", iteration)
        # print("X data:",x_data)
        # print("Y data:",y_data)
        # print("Z data:",z_data)

        # x_data_hex = binascii.hexlify(struct.pack('<f', x_data)
        iteration_data_byte = bytearray(struct.pack("I", iteration))
        x_data_byte = bytearray(struct.pack("f", x_data))
        y_data_byte = bytearray(struct.pack("f", y_data))
        z_data_byte = bytearray(struct.pack("f", z_data))
        print(iteration_data_byte, x_data_byte, y_data_byte, z_data_byte)
        # packed_x_data = binascii.hexlify(x_data_byte)
        # print(packed_x_data)

        # print(str(x_data_hex))

        iteration_char.value(iteration_data_byte)
        x_acc_char.value(x_data_byte)
        y_acc_char.value(y_data_byte)
        z_acc_char.value(z_data_byte)

        #Convert x_data string to hex and trunktate
        time.sleep(0.15)
        #x_acc_char.value(x_data)
        # y_acc_char.value(y_data)
        # z_acc_char.value(z_data)
        #x_acc_char.value(b)
        if x >= len(T)-1:
            print("Sent everything, waiting for disconnect...")
            BLEDisconnect()
            return(0)
    pass

def acc_write_fifo(duration): #Interrupt pin.

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

iteration_char = srv.characteristic(uuid=0x14, properties=Bluetooth.PROP_READ, value=0x00000000) #Total 16bit per char
x_acc_char = srv.characteristic(uuid=0x15, properties=Bluetooth.PROP_READ, value=0x00000000) #Total 16bit per char
y_acc_char = srv.characteristic(uuid=0x16, properties=Bluetooth.PROP_READ, value=0x00000000) #Total 16bit per char
z_acc_char = srv.characteristic(uuid=0x17, properties=Bluetooth.PROP_READ, value=0x00000000) #Total 16bit per char

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
# li.set_odr(6) # 0x20
# # ODR_10_HZ
# # ODR_50_HZ
# # ODR_100_HZ
# # ODR_200_HZ
# # ODR_400_HZ
# # ODR_800_HZ
#
# # change the full-scale to 2g
# li.set_full_scale(0) #0x23
# # FULL_SCALE_2G -
# # FULL_SCALE_4G -
# # FULL_SCALE_8G -
#
# # set the interrupt pin as active low and open drain
# # li.set_register(CTRL5_REG, 3, 0, 3)

#Configuration:

# n_interrupts = 0
# n_interrupts_max = 200
#
# def pin_handler(arg):
#     global n_interrupts
#     n_interrupts = n_interrupts + 1
#
#
# p_in = Pin('P13', mode=Pin.IN, pull=Pin.PULL_UP)
# p_in.callback(Pin.IRQ_FALLING, pin_handler) # Pin.IRQ_FALLING | Pin.IRQ_RISING, pin_handler

T = []

# for unit in range(0,200):
#     T.append(li.accelerationOneGoRaw())
#     pass

# for unit in range(0,100):
#     A.append(li.fifoDataRead(10))
#     pass

PrivateWlanConfiguration()

acc_write_array_RAW(200)

print("RAW: ",T[0][1])

A = []


Test_data_unit = T[199][1] #f83f

ACC_G_DIV = 1000 * 65536
_mult = 4000/ACC_G_DIV

value_after_unpack_array_x=[]


for iteration_conversion in range(0,len(T)):
    Test_data_unit = T[iteration_conversion][1]
    Test_data_unit_array = bytearray(Test_data_unit)
    value_after_unpack_array_x = struct.unpack('<h', Test_data_unit_array[0:2])
    value_after_unpack_array_y = struct.unpack('<h', Test_data_unit_array[2:4])
    value_after_unpack_array_z = struct.unpack('<h', Test_data_unit_array[4:6])

    #print(value_after_unpack_array_x)

    output_test = [iteration_conversion,value_after_unpack_array_x[0] * _mult, value_after_unpack_array_y[0] * _mult, value_after_unpack_array_z[0] * _mult,]
    A.append(output_test)
    pass


# print("A: ", A)
#
# print("A_select: ", A[1][2])

 # Converting to byte array









# print("Output test: ",output_test_x, output_test_y, output_test_z)



#print(bytearray(struct.pack("h", Test_data_unit)))

#print(A)
#print(list[0],list[2],list[4])


mainMQTT()

print(A)

while True:


    pass
