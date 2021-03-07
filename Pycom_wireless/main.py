from network import Bluetooth
import time
import ubinascii
bt = Bluetooth()
bt.start_scan(-1)

bt.init() # This is important for it to work! Put on front fo bt.start?

tilt = 0

while True:
  #time.sleep(3) #Every 3 seconds
  adv = bt.get_adv()
  if adv and bt.resolve_adv_data(adv.data, Bluetooth.ADV_NAME_CMPL) == 'LoPy':
          conn = bt.connect(adv.mac)
          services = conn.services()
          while True:
              for service in services:
                  time.sleep(0.050)
                  #  if type(service.uuid()) == bytes:
                  #      print('Reading a chars from service = {}'.format(service.uuid()))
                  #else:
                  #print('Reading b chars from service = %x' % service.uuid())
                  chars = service.characteristics()
                  for char in chars:
                      if (char.properties() & Bluetooth.PROP_READ):
                          #print('char {} value = {}'.format(char.uuid(), str(char.read())))
                          if(char.uuid() == 8224):
                            tilt = char.read()
                      else:
                          break

              time.sleep(1)
          #conn.disconnect()
          print("Data: " + tilt)
          #break
  else:
      time.sleep(0.050)
      # Starte scan her.



# from network import Bluetooth
# import binascii
# import time
# bt = Bluetooth()
# bt.start_scan(-1)
#
# def char_notify_callback(char):
#     char_value = (char.value())
#     print("Got new char: {} value: {}".format(char.uuid(), char_value))
#
#
# while True:
#   adv = bt.get_adv()
#   if adv and bt.resolve_adv_data(adv.data, Bluetooth.ADV_NAME_CMPL) == 'LoPy':
#       try:
#           conn = bt.connect(adv.mac)
#           services = conn.services()
#           for service in services:
#               time.sleep(0.050)
#               if service.uuid() == 0x1809:
#                   print('Service found')
#                   print('Reading e chars from service = {}'.format(service.uuid()))
#               else:
#                   print('Reading b chars from service = %x' % service.uuid()) #Service uuid in hex
#                   chars = service.characteristics()
#                   print(str(chars))
#                   for char in chars:
#                       if (char.properties() & Bluetooth.PROP_READ):
#                           print('char {} value = {}'.format(char.uuid(), char.value()))
#           conn.disconnect()
#           break
#       except:
#           print("Error while connecting or reading from the BLE device")
#           break
#   else:
#       time.sleep(0.050)
