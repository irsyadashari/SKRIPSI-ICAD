import time
import board
import busio
import math
import adafruit_ads1x15.ads1015 as ADS
import adafruit_ads1x15.ads1115 as ADC
from adafruit_ads1x15.analog_in import AnalogIn

# Create the I2C bus
i2c = busio.I2C(board.SCL, board.SDA)

# Create the ADC object using the I2C bus
#ads = ADS.ADS1015(i2c)
ads = ADC.ADS1115(i2c)

# Create single-ended input on channel 0
#chan = AnalogIn(ads, ADS.P0)
chan = AnalogIn(ads, ADC.P0)

# Create differential input between channel 0 and 1
#chan = AnalogIn(ads, ADS.P0, ADS.P1)

print("{:>5}\t{:>5}".format('raw', 'v'))

while True:
    ntu = (-26.7641 * chan.voltage) + 135.0524 
#    ntu = -1120.4*math.sqrt(chan.voltage)+5742.3*chan.voltage-4353.8
    print("{:>5}\t{:>.2f}\tNTU :{:>.2f}".format(chan.value, chan.voltage,ntu))
    time.sleep(1.5)