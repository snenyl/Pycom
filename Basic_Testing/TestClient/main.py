from network import Bluetooth
import ubinascii
import time

bluetooth = Bluetooth()
BLEConnected = False

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

def char1_cb_handler(chr, data):

    # The data is a tuple containing the triggering event and the value if the event is a WRITE event.
    # We recommend fetching the event and value from the input parameter, and not via characteristic.event() and characteristic.value()
    events, value = data
    if  events & Bluetooth.CHAR_WRITE_EVENT:
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
bluetooth.advertise(False)
#
srv1 = bluetooth.service(uuid=b'1234567890123456',isprimary=True)
chr1 = srv1.characteristic(uuid=b'ab34567890123456',properties=Bluetooth.PROP_READ, value=0)
char1_cb = chr1.callback(trigger=Bluetooth.CHAR_WRITE_EVENT, handler=char1_cb_handler)
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


adv = None
while True:
    adv = bluetooth.get_adv()
    if adv and bt.resolve_adv_data(adv.data, Bluetooth.ADV_NAME_CMPL) == 'LoPy':
        try:
            conn = bluetooth.connect(adv.mac)
            services = conn.services()
            for service in services:
                time.sleep(0.050)
                if type(service.uuid()) == bytes:
                    print('Reading chars from service = {}'.format(service.uuid()))
                else:
                    print('Reading chars from service = %x' % service.uuid())
                chars = service.characteristics()
                for char in chars:
                    if (char.properties() & Bluetooth.PROP_WRITE):
                         print('char {} value = {}'.format(char.uuid(), char.write(b'x0f')))
        except:
            # start scanning again
            bluetooth.start_scan(-1)
            continue
        #break
    if BLEConnected:
        time.sleep(1)
