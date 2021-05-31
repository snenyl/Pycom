"""
This is the client side (Gateway) which read the data from the server node and
send it to the NodeRED Server though MQTT.

The client read the data off the server by using notify.

"""


from network import Bluetooth
import ubinascii
import time
from LIS2HH12 import LIS2HH12
from umqtt.simple2 import MQTTClient
from network import WLAN
import machine
import struct

bluetooth = Bluetooth()
BLEConnected = False

def PrivateWlanConfiguration():
    wlan = WLAN(mode=WLAN.STA)
    wlan.connect(ssid='OnePlus_7T_Pro', auth=(WLAN.WPA2, 'pycomTestingFacilityAtUiA'))
    while not wlan.isconnected():
        machine.idle()
    print("WiFi connected succesfully")
    print(wlan.ifconfig())
    pass

AccData = [[0, 0.384736286, 0.764539453, -0.738283483],
           [1, 0.335393275, 0.787328572, -1.059825923],
           [2, 0.387439833, 0.783275892, -1.032749873],
           [3, 0.394380345, 0.729525939, -1.132498242],
           [4, 0.387325897, 0.792395934, -1.027387233]]

def acc_write_array(duration): #Interrupt pin.
    for x in range(duration):
        add = [x, li.acceleration()]
        T.append(add)
    pass

# MQTT
def sub_cb(topic, msg):
    print((topic, msg))


# client = MQTTClient("TestDeviceGPy", "broker.hivemq.com",user="your_username", password="your_api_key", port=1883) IKT520_LAB1
def mainMQTT(server="broker.hivemq.com"):
    print("Connecting to MQTT server")
    c = MQTTClient("umqtt_client", server)
    c.connect()
    for x in range(0, len(AccData)):
        print("Publishing")
        PublishThis_ba = bytearray(struct.pack("b", AccData[x][0])) + bytearray(struct.pack("e", AccData[x][1])) + bytearray(struct.pack("e", AccData[x][2])) + bytearray(struct.pack("e", AccData[x][3]))
        # PublishThis_ba = T[x]
        c.publish(b"IKT520_LAB1", PublishThis_ba)
        pass

    c.disconnect()

def conn_cb (bt_o):
    events = bt_o.events()
    global BLEConnected
    if  events & Bluetooth.CLIENT_CONNECTED:
        BLEConnected = True
        print("Client connected")
        #print("Connected to device with addr = {}".format(ubinascii.hexlify(adv.mac)))
    elif events & Bluetooth.CLIENT_DISCONNECTED:
        BLEConnected = False
        print("Client disconnected")
        bluetooth.start_scan(-1)
        return(0)

def char_notify_callback(char):
    char_value = (char.value())
    print("Got new char: {} value: {}".format(char.uuid(), char_value))

def char1_cb_handler(chr, data):
    # The data is a tuple containing the triggering event and the value if the event is a WRITE event.
    # We recommend fetching the event and value from the input parameter, and not via characteristic.event() and characteristic.value()
    events, value = data
    if  events & Bluetooth.CHAR_READ_EVENT:
        print("Write request with value = {}".format(value))
    else:
        print('Read request on char 1')
#
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
#
#
bluetooth.set_advertisement(name='LoPy', service_uuid=b'1234567890123456')
bluetooth.callback(trigger=Bluetooth.CLIENT_CONNECTED | Bluetooth.CLIENT_DISCONNECTED, handler=conn_cb)
# bluetooth.callback(trigger=Bluetooth.CHAR_NOTIFY_EVENT, handler=conn_notify_cb)

bluetooth.advertise(False)
#
srv1 = bluetooth.service(uuid=b'1234567890123456',isprimary=True)
chr1 = srv1.characteristic(uuid=b'ab34567890123456',properties=Bluetooth.PROP_READ, value=0)
char1_cb = chr1.callback(trigger=Bluetooth.CHAR_READ_EVENT, handler=char1_cb_handler)


#
# srv2 = bluetooth.service(uuid=1234, nbr_chars=2 ,isprimary=True)
# chr2 = srv2.characteristic(uuid=4567, value=0x1234)
# char2_cb = chr2.callback(trigger=Bluetooth.CHAR_READ_EVENT, handler=char2_cb_handler)
# chr21 = srv2.characteristic(uuid=4568, value=0x4321)
# char21_cb = chr2.callback(trigger=Bluetooth.CHAR_READ_EVENT, handler=char21_cb_handler)



# scan until we can connect to any BLE device around

bt = Bluetooth()
bluetooth.start_scan(-1)
adv = None

PrivateWlanConfiguration() # Wlan Network configuration
mainMQTT()

adv = None
while True:
    adv = bluetooth.get_adv()
    if adv and bt.resolve_adv_data(adv.data, Bluetooth.ADV_NAME_CMPL) == 'LoPy':
        try:
            conn = bluetooth.connect(adv.mac)
            services = conn.services()
            print("Services: ", services)
            for service in services:
              time.sleep(0.050)
              if type(service.uuid()) == bytes:
                  print('Reading chars from service = {}'.format(service.uuid()))
              else:
                  print('Reading chars from service = %x' % service.uuid())
              chars = service.characteristics()
              for char in chars:
                  print("Char: ", chars)
                  # print(char.properties())
                  if (char.properties() & Bluetooth.PROP_READ): #
                      print('char {} value = {}'.format(char.uuid(), char.read()))
                      # for ii in range(200):
                      #     if char.uuid() == 0x2020:
                      #         # global T
                      #         T[ii] = char.read()
                      #         dataOut = char.read()
                      #         print("Hi! ", dataOut)
                      #     pass
                      #     if char.uuid() == 8225:
                      #         dataOut_x = char.read()
                      #         print("You ", dataOut)
                      #     pass
            conn.disconnect()
            #mainMQTT()
            break
        except:
            pass
    else:
        time.sleep(0.050)



    #     #break
    # if BLEConnected:
    #     # if service.uuid() == 0x2020:
    #     #     for char in chars:
    #     #     chars = service.characteristics()
    #     #     if chars.uuid() == 0x2020:
    #     #         print("Reading array")
    #     #         pass
    #     time.sleep(5)
    #     print("BLEConnected")
