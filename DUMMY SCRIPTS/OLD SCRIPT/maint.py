#script
from flask import Flask, render_template, request

from AquariumAutomation import DSTemp, JSNDistance

import RPi.GPIO as GPIO
import os
import time
import schedule
import glob
import sqlite3
import threading
import _thread

app = Flask(__name__)

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

#Tinggi Sensor jika tank Kosong
mainTankDistance = 38 #calibrate this
secondTankDistance = 45 #calibrate this

#cek device sensor suhu
base_dir = '/sys/bus/w1/devices/'

#sensor temperature Akuarium
#device_folder1 = glob.glob(base_dir + '28*')[0]
#device_file1 = device_folder1 + '/w1_slave'

#sensor temperature tanki air cadangan
#device_folder2 = glob.glob(base_dir + '28*')[1]
#device_file2 = device_folder2 + '/w1_slave'

#Set GPIO number mode BCM
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

#Pin untuk sensor ultrasonic water lvl akuarium
GPIO_TRIGGER_MAIN = 15
GPIO_ECHO_MAIN = 14

#Pin untuk sensor ultrasonic water lvl tanki air cadangan
GPIO_TRIGGER_SECONDARY = 25
GPIO_ECHO_SECONDARY = 24

#inisiasi mode pin untuk sensor ultrasonic
GPIO.setup(GPIO_TRIGGER_MAIN, GPIO.OUT)  # Trigger main
GPIO.setup(GPIO_TRIGGER_SECONDARY, GPIO.OUT)  # Trigger secondary
GPIO.setup(GPIO_ECHO_MAIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Echo Main
GPIO.setup(GPIO_ECHO_SECONDARY, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Echo Secondary

GPIO.output(GPIO_TRIGGER_MAIN, False)
GPIO.output(GPIO_TRIGGER_SECONDARY, False)

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
    

@app.route("/login")
def login_page():
    return render_template('login.html')
    

@app.route("/home")
def main():
    
#    var_mainTankWaterLvl = JSNDistance.measureTank(GPIO_TRIGGER_MAIN,GPIO_ECHO_MAIN,mainTankDistance)
#    var_secondaryTankWaterLvl = JSNDistance.measureTank(GPIO_TRIGGER_SECONDARY,GPIO_ECHO_SECONDARY, secondTankDistance)
#    
#    var_mainTankTemperature = DSTemp.read_temp(device_file1)
#    var_secondaryTankTemperature = DSTemp.read_temp(device_file2)
    
    #Panggil fungsi Water Change disini supaya nilai buttonnya ikut terefresh jika program terpanggil
    
    
    
    # Menyimpan pin-pin relay dan memasukkan nilai "state"nya ke dalam Dictionary bernama "pins" yang telah diinisiasi sebelumnya
    for pin in pins:
        pins[pin]['state'] = GPIO.input(pin)
    
   # memasukkan Dictionary "pins" ke dalam dictionary "templateData":
    templateData = {
        'pins' : pins
    }
    
    return render_template('app.html',mainTankWaterLvl = 20, secondaryTankWaterLvl = 25 ,mainTankTemperature = 24, secondaryTankTemperature = 25 ,**templateData)


#def turnOffAlldevices(pins):
#    #matikan semua elektronik when something wrong
#    for pin in pins:
#        GPIO.output(pin, GPIO.HIGH)
        
def automateWaterCleaning():
    #simulate water change
    waterlvl = 20
    while waterlvl > 9:
        GPIO.output(17, GPIO.LOW)
        waterlvl -= 1
        time.sleep(1)
    else:
        GPIO.output(17, GPIO.HIGH)    
    
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
    _thread.start_new_thread(automateWaterCleaning,("second Thread",))
    

