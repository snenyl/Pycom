"""
This is the server side which read the data from the IMU and send it to the
Gateway.



"""



from network import Bluetooth
import ubinascii
import time
import machine
import struct

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
        writeToServer()
    elif events & Bluetooth.CLIENT_DISCONNECTED:
        BLEConnected = False
        print("Client disconnected")
        goToSleepfor(3)
        return(0)

def char1_cb_handler(chr, data):

    # The data is a tuple containing the triggering event and the value if the event is a WRITE event.
    # We recommend fetching the event and value from the input parameter, and not via characteristic.event() and characteristic.value()
    events, value = data
    if  events & Bluetooth.CHAR_WRITE_EVENT:
        print("Write request with value = {}".format(value))
    else:
        print('Read request on char 1')

def char2_cb_handler(chr, data):
    # The value is not used in this callback as the WRITE events are not processed.
    events, value = data
    if  events & Bluetooth.CHAR_READ_EVENT:
        print('Read request on char 2')

def char21_cb_handler(chr, data):
    # The value is not used in this callback as the WRITE events are not processed.
    events, value = data
    if  events & Bluetooth.CHAR_READ_EVENT:
        print('Read request on char 21')

bluetooth = Bluetooth()
bluetooth.set_advertisement(name='LoPy', service_uuid=b'1234567890123456')
bluetooth.callback(trigger=Bluetooth.CLIENT_CONNECTED | Bluetooth.CLIENT_DISCONNECTED, handler=conn_cb)
bluetooth.advertise(True)

srv1 = bluetooth.service(uuid=0x2020, nbr_chars=1 ,isprimary=True)
#
chr1 = srv1.characteristic(uuid=0x2020, properties=Bluetooth.PROP_READ, value=0x837233)
char1_cb = chr1.callback(trigger=Bluetooth.CHAR_WRITE_EVENT, handler=char1_cb_handler)

# srv2 = bluetooth.service(uuid=1234, nbr_chars=2 ,isprimary=True)
# chr2 = srv2.characteristic(uuid=4567, value=0x1234)
# char2_cb = chr2.callback(trigger=Bluetooth.CHAR_READ_EVENT, handler=char2_cb_handler)
# chr21 = srv2.characteristic(uuid=4568, value=0x4321)
# char21_cb = chr2.callback(trigger=Bluetooth.CHAR_READ_EVENT, handler=char21_cb_handler)

# dataArray = [4, 0.384736286, 0.764539453, -0.738283483]
# dataArray_byte = bytearray(struct.pack("q", )))

#Max char size 0xFFFFFFFF Not correnct

while True:
    if BLEConnected:
        print("hello!")
        # print(dataArray)
        # print(dataArray_byte)
        # # adv = bluetooth.get_adv()
        # chr1.value(dataArray_byte)
        # print(conn)
        time.sleep(1)

    else:
        time.sleep(0.1)
        #bluetooth.advertise(True)
