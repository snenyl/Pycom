from network import Bluetooth
import ubinascii
import time

def goToSleepfor(sleepvalue):
    print("Going to sleep for ", str(sleepvalue) ," seconds")
    time.sleep(sleepvalue)
    pass


def writeToServer():
    adv = bluetooth.get_adv()
    print("Writing to client with MAC: {}".format(ubinascii.hexlify(adv.mac)))

    print(adv)
    # services = connection.services()
    # print(services)
    # for service in services:
    #     print(service.uuid())

    # bt = Bluetooth()
    # conn = bt.connect(adv.mac)
    # services = conn.services()
    # print(services)
    # bluetooth.disconnect_client()#adv.mac
    return(0)

def conn_cb (bt_o):
    events = bt_o.events()
    if  events & Bluetooth.CLIENT_CONNECTED:
        print("Client connected")
        writeToServer()
    elif events & Bluetooth.CLIENT_DISCONNECTED:
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

srv1 = bluetooth.service(uuid=b'1234567890123456', isprimary=True)
chr1 = srv1.characteristic(uuid=b'ab34567890123456', value=5)
char1_cb = chr1.callback(trigger=Bluetooth.CHAR_WRITE_EVENT | Bluetooth.CHAR_READ_EVENT, handler=char1_cb_handler)

srv2 = bluetooth.service(uuid=1234, nbr_chars=2 ,isprimary=True)
chr2 = srv2.characteristic(uuid=4567, value=0x1234)
char2_cb = chr2.callback(trigger=Bluetooth.CHAR_READ_EVENT, handler=char2_cb_handler)
chr21 = srv2.characteristic(uuid=4568, value=0x4321)
char21_cb = chr2.callback(trigger=Bluetooth.CHAR_READ_EVENT, handler=char21_cb_handler)



while True:
    pass
