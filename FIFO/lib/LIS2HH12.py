#!/usr/bin/env python
#
# Copyright (c) 2020, Pycom Limited.
#
# This software is licensed under the GNU GPL version 3 or any
# later version, with permitted additional terms. For more information
# see the Pycom Licence v1.0 document supplied with this file, or
# available at https://www.pycom.io/opensource/licensing
#

import math
import time
import struct
from machine import Pin


FULL_SCALE_2G = const(0)
FULL_SCALE_4G = const(2)
FULL_SCALE_8G = const(3)

ODR_POWER_DOWN = const(0)
ODR_10_HZ = const(1)
ODR_50_HZ = const(2)
ODR_100_HZ = const(3)
ODR_200_HZ = const(4)
ODR_400_HZ = const(5)
ODR_800_HZ = const(6)

ACC_G_DIV = 1000 * 65536

#FIFO CTRL Standard
FIFO_BYPASS = const(0)
FIFO_FIFO_MODE = const(1)
FIFO_STREAM_MODE = const(2)
FIFO_STREAM_MODE_FIFO_TRIGGER = const(3)
FIFO_BYPASS_STREAM_TRIGGER = const(4)
FIFO_BYPASS_FIFO_TRIGGER = const(7)

#FIFO CTRL Standard (FTH)
FTH_1_SAMPLE = const(0) # Need to be fixed (not working)
FTH_4_SAMPLE = const(4) # Need to be fixed (not working)
FTH_8_SAMPLE = const(8) # Need to be fixed (not working)
FTH_10_SAMPLE = const(30) # Working
FTH_16_SAMPLE = const(16) # Need to be fixed (not working)
FTH_20_SAMPLE = const(20) # Need to be fixed (not working)
FTH_30_SAMPLE = const(30) # Need to be fixed (not working)



class LIS2HH12:

    ACC_I2CADDR = const(30) #1E

    PRODUCTID_REG = const(0x0F)
    CTRL1_REG = const(0x20)
    CTRL2_REG = const(0x21)
    CTRL3_REG = const(0x22)
    CTRL4_REG = const(0x23)
    CTRL5_REG = const(0x24)
    ACC_X_L_REG = const(0x28)
    ACC_X_H_REG = const(0x29)
    ACC_Y_L_REG = const(0x2A)
    ACC_Y_H_REG = const(0x2B)
    ACC_Z_L_REG = const(0x2C)
    ACC_Z_H_REG = const(0x2D)
    ACT_THS = const(0x1E)
    ACT_DUR = const(0x1F)
    FIFO_CTRL = const(0x2E)
    FIFO_SRC = const(0x2F)

    SCALES = {FULL_SCALE_2G: 4000, FULL_SCALE_4G: 8000, FULL_SCALE_8G: 16000}
    ODRS = [0, 10, 50, 100, 200, 400, 800]

    def __init__(self, pysense = None, sda = 'P22', scl = 'P21'):
        if pysense is not None:
            self.i2c = pysense.i2c
        else:
            from machine import I2C
            self.i2c = I2C(0, mode=I2C.MASTER, pins=(sda, scl))

        self.odr = 0
        self.full_scale = 0
        self.x = 0
        self.y = 0
        self.z = 0
        self.int_pin = None
        self.act_dur = 0
        self.debounced = False

        whoami = self.i2c.readfrom_mem(ACC_I2CADDR , PRODUCTID_REG, 1)
        if (whoami[0] != 0x41):
            raise ValueError("LIS2HH12 not found")

        # enable acceleration readings at 800Hz
        self.set_odr(ODR_800_HZ)

        # change the full-scale to 2g
        self.set_full_scale(FULL_SCALE_2G)

        # set the interrupt pin as active low and open drain
        self.set_register(CTRL5_REG, 3, 0, 3)

        # set FIFO control registry (FIFO_MODE)            set_register(self, register, value, offset, mask):
        self.set_register(FIFO_CTRL, FIFO_STREAM_MODE, 5, 7)

        # set FIFO control registry (FIFO_FTH)                set_register(self, register, value, offset, mask):
        self.set_register(FIFO_CTRL, FTH_10_SAMPLE, 0, 4)

        #FIFO Enable:
        #config_Reg3 = b'\xc2' #11000010 - Enable FIFO and set FIFO threshold signal on INT1
        config_Reg3 = b'\xc1' #11000001 - Enable FIFO and data ready on INT1
        self.i2c.writeto_mem(ACC_I2CADDR, CTRL3_REG, config_Reg3)

        #control3 = bytearray(0x01010101)
        #self.i2c.writeto_mem(ACC_I2CADDR, CTRL3_REG, control3)
        #self.set_register(CTRL3_REG, 0, 0, 8)



        # Enable activity interrupt:

        # make a first read; comment this out, makes the readings go slow.
        #self.acceleration()

    def acceleration(self):
        x = self.i2c.readfrom_mem(ACC_I2CADDR , ACC_X_L_REG, 2)
        self.x = struct.unpack('<h', x)
        y = self.i2c.readfrom_mem(ACC_I2CADDR , ACC_Y_L_REG, 2)
        self.y = struct.unpack('<h', y)
        z = self.i2c.readfrom_mem(ACC_I2CADDR , ACC_Z_L_REG, 2)
        self.z = struct.unpack('<h', z)
        _mult = self.SCALES[self.full_scale] / ACC_G_DIV
        return (self.x[0] * _mult, self.y[0] * _mult, self.z[0] * _mult)
        #return(self.x, self.y, self.z)
    def accelerationOneGoRaw(self):
        xyz = self.i2c.readfrom_mem(ACC_I2CADDR , ACC_X_L_REG, 6) #Reading 6byte after 0x28, 2byte for each direction
        return (xyz)

    def fifoControlRead(self):
        fifo_output = self.i2c.readfrom_mem(ACC_I2CADDR , FIFO_CTRL, 1)
        return (fifo_output)

    def fifoSourceRead(self):
        fifo_output = self.i2c.readfrom_mem(ACC_I2CADDR , FIFO_SRC, 1)
        return (fifo_output)

    def fifoDataRead(self, samples):
        fifo_output = self.i2c.readfrom_mem(ACC_I2CADDR , ACC_X_L_REG, 6*samples)
        return (fifo_output)

    def roll(self):
        x,y,z = self.acceleration()
        rad = math.atan2(-x, z)
        return (180 / math.pi) * rad

    def pitch(self):
        x,y,z = self.acceleration()
        rad = -math.atan2(y, (math.sqrt(x*x + z*z)))
        return (180 / math.pi) * rad

    def set_register(self, register, value, offset, mask):
        reg = bytearray(self.i2c.readfrom_mem(ACC_I2CADDR, register, 1))
        reg[0] &= ~(mask << offset)
        reg[0] |= ((value & mask) << offset)
        self.i2c.writeto_mem(ACC_I2CADDR, register, reg)

    def set_full_scale(self, scale):
        self.set_register(CTRL4_REG, scale, 4, 3)
        self.full_scale = scale

    def set_odr(self, odr):
        self.set_register(CTRL1_REG, odr, 4, 7)
        self.odr = odr

    def set_high_pass(self, hp):
        self.set_register(CTRL2_REG, 1 if hp else 0, 2, 1)

    def enable_activity_interrupt(self, threshold, duration, handler=None):
        # Threshold is in mg, duration is ms
        self.act_dur = duration

        if threshold > self.SCALES[self.full_scale]:
            error = "threshold %d exceeds full scale %d" % (threshold, self.SCALES[self.full_scale])
            print(error)
            raise ValueError(error)

        if threshold < self.SCALES[self.full_scale] / 128:
            error = "threshold %d below resolution %d" % (threshold, self.SCALES[self.full_scale]/128)
            print(error)
            raise ValueError(error)

        if duration > 255 * 1000 * 8 / self.ODRS[self.odr]:
            error = "duration %d exceeds max possible value %d" % (duration, 255 * 1000 * 8 / self.ODRS[self.odr])
            print(error)
            raise ValueError(error)

        if duration < 1000 * 8 / self.ODRS[self.odr]:
            error = "duration %d below resolution %d" % (duration, 1000 * 8 / self.ODRS[self.odr])
            print(error)
            raise ValueError(error)

        _ths = int(127 * threshold / self.SCALES[self.full_scale]) & 0x7F
        _dur = int((duration * self.ODRS[self.odr]) / 1000 / 8)

        self.i2c.writeto_mem(ACC_I2CADDR, ACT_THS, _ths)
        self.i2c.writeto_mem(ACC_I2CADDR, ACT_DUR, _dur)

        # enable the activity/inactivity interrupt
        # self.set_register(CTRL3_REG, 1, 5, 1)

        self._user_handler = handler
        self.int_pin = Pin('P13', mode=Pin.IN)
        self.int_pin.callback(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler=self._int_handler)

        # return actual used threshold and duration
        return (_ths * self.SCALES[self.full_scale] / 128, _dur * 8 * 1000 / self.ODRS[self.odr])

    def activity(self):
        if not self.debounced:
            time.sleep_ms(self.act_dur)
            self.debounced = True
        if self.int_pin():
            return True
        return False

    def _int_handler(self, pin_o):
        if self._user_handler is not None:
            self._user_handler(pin_o)
        else:
            if pin_o():
                print('Activity interrupt')
            else:
                print('Inactivity interrupt')
