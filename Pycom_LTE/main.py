from network import Bluetootht
import time
# import ujson
import pycom
# from pysense import Pysense
# from machine import I2C
# from machine import ADC
# from network import Bluetooth
# from SHT35 import SHT35
# from LIS2HH12 import LIS2HH12

from network import LTE

lte = LTE()
print("Intializing...")
lte.init([carrier='standard’, psm_period_value=0, psm_period_unit=LTE.PSM_PERIOD_DISABLED, psm_active_value=0, psm_active_unit=LTE.PSM_ACTIVE_DISABLED])
print("Attaching...")
lte.attach([band=None, apn=None, cid=None, type=LTE.IP, legacyattach=True])
print("Network attached: " + lte.isattached())
