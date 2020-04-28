#script
from flask import Flask, render_template, request

import RPi.GPIO as GPIO
import os
import time

app = Flask(__name__)

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO_TRIGGER = 15
GPIO_ECHO = 14

TRIGGER_TIME = 0.00001
MAX_TIME = 0.004  # max time waiting for response in case something is missed
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)  # Trigger
GPIO.setup(GPIO_ECHO, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Echo

GPIO.output(GPIO_TRIGGER, False)

# Create a dictionary called pins to store the pin number, name, and pin state:
pins = {
   17 : {'name' : 'Pompa Utama', 'state' : GPIO.LOW},
   27 : {'name' : 'Pompa Pengisap', 'state' : GPIO.LOW},
   22 : {'name' : 'Pompa Pengisi', 'state' : GPIO.LOW},
   23 : {'name' : 'Lampu', 'state' : GPIO.LOW}
   }

# Set each pin as an output and make it low:
for pin in pins:
   GPIO.setup(pin, GPIO.OUT)
   GPIO.output(pin, GPIO.LOW)

@app.route("/")
def main():
    
   # For each pin, read the pin state and store it in the pins dictionary:
   for pin in pins:
   	pins[pin]['state'] = GPIO.input(pin)
   # Put the pin dictionary into the template data dictionary:
   templateData = {
   	'pins' : pins
   }
   var_mainTankWaterLvl = measure()

   return render_template('tryBootStrap.html', **templateData, mainTankWaterLvl = var_mainTankWaterLvl)

# The function below is executed when someone requests a URL with the pin number and action in it:
@app.route("/<changePin>/<action>")
def action(changePin, action):
   # Convert the pin from the URL into an integer:
   changePin = int(changePin)
   # Get the device name for the pin being changed:
   deviceName = pins[changePin]['name']
   # If the action part of the URL is "on," execute the code indented below:
   if action == "on":
      # Set the pin high:
      GPIO.output(changePin, GPIO.HIGH)
      # Save the status message to be passed into the template:
      message = "Turned " + deviceName + " on."
   if action == "off":
      GPIO.output(changePin, GPIO.LOW)
      message = "Turned " + deviceName + " off."

   # For each pin, read the pin state and store it in the pins dictionary:
   for pin in pins:
      pins[pin]['state'] = GPIO.input(pin)

   # Along with the pin dictionary, put the message into the template data dictionary:
   templateData = {
      'pins' : pins
   }

   var_mainTankWaterLvl = measure()
   return render_template('tryBootStrap.html',mainTankWaterLvl = var_mainTankWaterLvl ,**templateData)

# This function measures a distance
def measure():
    # Pulse the trigger/echo line to initiate a measurement
    GPIO.output(GPIO_TRIGGER, True)
    time.sleep(TRIGGER_TIME)
    GPIO.output(GPIO_TRIGGER, False)

    # ensure start time is set in case of very quick return
    start = time.time()
    timeout = start + MAX_TIME

    # set line to input to check for start of echo response
    while GPIO.input(GPIO_ECHO) == 0 and start <= timeout:
        start = time.time()

    if(start > timeout):
        return -1

    stop = time.time()
    timeout = stop + MAX_TIME
    # Wait for end of echo response
    while GPIO.input(GPIO_ECHO) == 1 and stop <= timeout:
        stop = time.time()

    if(stop <= timeout):
        elapsed = stop-start
        distance = float(elapsed * 34300)/2.0
    else:
        return -1
    return distance+1


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080,debug=True)
    

