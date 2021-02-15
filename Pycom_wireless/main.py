import pycom
from network import Bluetooth
import ubinascii
bluetooth = Bluetooth()

# scan until we can connect to any BLE device around
bluetooth.start_scan(-1)
adv = None

# server_mac = "2462ABf4E63A"

while True:
    adv = bluetooth.get_adv()
    if adv:
        try:
            # vprint("Trying to connect ")
            # bluetooth.connect('2462ABf4E63A')
            bluetooth.connect(adv.mac)
        except:
            # start scanning again
            bluetooth.start_scan(-1)
            continue
        break
print("Connected to device with addr = {}".format(ubinascii.hexlify(adv.mac)))
# pycom.rgbled(0xaa0000)
