#script
from flask import Flask, render_template, request

from AquariumAutomation import DSTemp, JSNDistance

import RPi.GPIO as GPIO
import os
import time
import glob

app = Flask(__name__)

#Set GPIO number mode BCM
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# inisiasi pin relay
pins = {
   17 : {'name' : 'Pompa Utama', 'state' : GPIO.HIGH},
   27 : {'name' : 'Pompa Pengisap', 'state' : GPIO.HIGH},
   22 : {'name' : 'Pompa Pengisi', 'state' : GPIO.HIGH},
   23 : {'name' : 'Lampu', 'state' : GPIO.HIGH}
   }

# Mematikan aliran listrik menggunakan relay mode Normally Open
for pin in pins:
   GPIO.setup(pin, GPIO.OUT)
   GPIO.output(pin, GPIO.HIGH)
 

@app.route("/")
def main():
    return render_template('login.html')
   

@app.route("/home")
def showAllWidgets():
    # Menyimpan pin-pin relay dan memasukkan nilai "state"nya ke dalam Dictionary bernama "pins" yang telah diinisiasi sebelumnya
   for pin in pins:
   	pins[pin]['state'] = GPIO.input(pin)
    
   # memasukkan Dictionary "pins" ke dalam dictionary "templateData":
   templateData = {
   	'pins' : pins
   }
    conn=sqlite3.connect('/var/www/lab_app/tankwaterlvl.db')
	curs=conn.cursor()
	curs.execute("SELECT * FROM waterlvl WHERE id=1 )
	waterlvl = curs.fetchall()
	conn.close()
    
   return render_template('showalldata.html',mainTankWaterLvl = waterlvl[2], secondaryTankWaterLvl = waterlvl[3] ,mainTankTemperature = "20 C", secondaryTankTemperature = "30 C" ,**templateData)

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
      GPIO.output(changePin, GPIO.LOW)
      # Save the status message to be passed into the template:
      message = "Turned " + deviceName + " off."
   if action == "off":
      GPIO.output(changePin, GPIO.HIGH)
      # Save the status message to be passed into the template:
      message = "Turned " + deviceName + " on."

   # For each pin, read the pin state and store it in the pins dictionary:
   for pin in pins:
      pins[pin]['state'] = GPIO.input(pin)

   # Along with the pin dictionary, put the message into the template data dictionary:
   templateData = {
      'pins' : pins
   }
   
   return render_template('showalldata.html',mainTankWaterLvl = waterlvl[2], secondaryTankWaterLvl = waterlvl[3] ,mainTankTemperature = "20 C", secondaryTankTemperature = "30 C" ,**templateData)
    

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080,debug=True)
    
   
