from network import Bluetooth
import time
import ubinascii
import binascii
import struct

bt = Bluetooth()
bt.start_scan(-1)

bt.init() # This is important for it to work! Put on front fo bt.start?

def acc_recieve_array():
        #x_acc_char.value(b)
    pass

tilt = 0
i = 0
T = []
data_1 = 0
initialWait = 0

while True:
  #time.sleep(3) #Every 3 seconds
  adv = bt.get_adv()
  if adv and bt.resolve_adv_data(adv.data, Bluetooth.ADV_NAME_CMPL) == 'LoPy':
          conn = bt.connect(adv.mac)
          services = conn.services()
          while True:
              for service in services:
                  chars = service.characteristics()
                  for char in chars:
                      # print(char.uuid())
                      # descriptor = char.read_descriptor(0x2902)
                      # print(descriptor)
                      if char.uuid() == 0x2020:
                          #print("Hello! ", hex(char.uuid()))
                          if len(char.read()) < 3:
                              time.sleep(0.001)
                              #print("Initial wait completed")
                              pass
                          else:
                              data_0 = struct.unpack("I", char.read())
                              x_data = struct.unpack("f", char.read())
                              y_data = struct.unpack("f", char.read())
                              z_data = struct.unpack("f", char.read())


                              if len(T) < int(data_0[0]):
                                  add = [int(data_0[0]), x_data, y_data, z_data]
                                  T.append(add)
                                  data_1 = data_0
                                  pass


                              if int(data_0[0]) > 50:
                                  print(T)
                                  time.sleep(20)
                                  pass
                          #data_0 = int(binascii.hexlify(char.read()),16)
                          #print("char:", data_0[0])
                          # data_0 = int(binascii.uhexlify(char.read()),16)
                          # if data_0 > data_1:
                          #     print("r: ", data_0)
                          #     data_1 = int(binascii.hexlify(char.read()),16)
                          #     pass
                          #print("v: ", char.value())


                          #add =
                          #time.sleep(0.3)
                          #pass
                      # print("uuid: ", hex(char.uuid()))
                      # print("char_read: ",char.value())


              # for service in services:
              #     time.sleep(0.050)
              #     # if type(service.uuid()) == bytes:
              #     #     print('Reading a chars from service = {}'.format(service.uuid()))
              #     # else:
              #     #     print('Reading b chars from service = %x' % service.uuid())
              #     chars = service.characteristics()
              #     for char in chars:
              #         if (char.properties() & Bluetooth.PROP_READ):
              #             print('char {} value = {}'.format(char.uuid(), str(char.read())))
              #             if(char.uuid() == 0x2020):
              #                 iteration = char.read()
              #                 unpacked_data = ubinascii.unhexlify(iteration)
              #                 i = i + 1
              #                 add = []
              #                 T.append(add)
              #                 print("Hello:",iteration,"Unpack: ",unpacked_data)
              #             if(char.uuid() == 0x2021):
              #                 print("darkness")
              #
              #         else:
              #             break
              #time.sleep(1)
          #conn.disconnect()
              # i = i + 1
              # add = [iteration,char.uuid()]
              # T.append(add)
              # print("Array: " + str(T))
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
