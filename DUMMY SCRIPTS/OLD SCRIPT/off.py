#script
from flask import Flask, render_template, request, session
from flask_socketio import SocketIO, send, emit
from AquariumAutomation import DSTemp, JSNDistance, Autowc
from flask_apscheduler import APScheduler
from apscheduler.schedulers.background import BackgroundScheduler
from threading import Thread, Event

import RPi.GPIO as GPIO
import os
import time
import schedule
import glob

app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = 'fishwebmonitoringsystem#'
app.config['DEBUG'] = True
socketio = SocketIO(app, always_connect=True)
scheduler = BackgroundScheduler()
thread = None


os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

#Tinggi Sensor jika tank Kosong
mainTankDistance = 72 #calibrate this
secondTankDistance = 65 #calibrate this

#cek device sensor suhu
base_dir = '/sys/bus/w1/devices/'

#sensor temperature Akuarium
device_folder1 = glob.glob(base_dir + '28*')[0]
device_file1 = device_folder1 + '/w1_slave'

#sensor temperature tanki air cadangan
device_folder2 = glob.glob(base_dir + '28*')[1]
device_file2 = device_folder2 + '/w1_slave'

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
    
   # Menyimpan pin-pin relay dan memasukkan nilai "state"nya ke dalam Dictionary bernama "pins" yang telah diinisiasi sebelumnya
    for pin in pins:
        pins[pin]['state'] = GPIO.input(pin)
    
   # memasukkan Dictionary "pins" ke dalam dictionary "templateData":
    templateData = {
        'pins' : pins
    }
   
    
    var_mainTankWaterLvl = JSNDistance.measureTank(GPIO_TRIGGER_MAIN,GPIO_ECHO_MAIN,mainTankDistance)
    var_secondaryTankWaterLvl = JSNDistance.measureTank(GPIO_TRIGGER_SECONDARY,GPIO_ECHO_SECONDARY, secondTankDistance)

    var_mainTankTemperature = DSTemp.read_temp(device_file1)
    var_secondaryTankTemperature = DSTemp.read_temp(device_file2)
    
    return render_template('home.html',mainTankWaterLvl = var_mainTankWaterLvl, secondaryTankWaterLvl = var_secondaryTankWaterLvl ,mainTankTemperature = var_mainTankTemperature, secondaryTankTemperature = var_secondaryTankTemperature ,**templateData)    

def getSensorsValue():
    var_mainTankTemperature = DSTemp.read_temp(device_file1)
    socketio.emit('main_tank_temp', 
                  {'mainTankTemp': var_mainTankTemperature,}, namespace='/home')
    socketio.send('main_tank_temp', 
                  {'mainTankTemp': var_mainTankTemperature,}, namespace='/home')
    print("Main Tank Temp : " + var_mainTankTemperature)

        
@socketio.on('main_tank_temp', namespace='/home')
def main_tank_temp(main_tank_temp):
    var_mainTankTemperature = DSTemp.read_temp(device_file1)
    send('main_tank_temp', {'mainTankTemp': var_mainTankTemperature,},broadcast=True)


scheduler.add_job(id = 'getSensorsValue', func = getSensorsValue, trigger = 'interval', seconds = 8)
scheduler.start()

if __name__ == "__main__":
#    Parameters:	
#func – callable to run
#year – year to run on
#month – month to run on
#day – day of month to run on
#week – week of the year to run on
#day_of_week – weekday to run on (0 = Monday)
#hour – hour to run on
#second – second to run on
#args – list of positional arguments to call func with
#kwargs – dict of keyword arguments to call func with
#name – name of the job
#jobstore – alias of the job store to add the job to
   
#    scheduler.add_job(id = 'waterchange', func = Autowc.start_water_changing, trigger = 'cron', day_of_week = 0)
#    scheduler.add_job(id = 'waterchange', func = Autowc.start_water_changing, trigger = 'interval', hour = 1)
#    app.run(host='0.0.0.0', port=8080,debug=True)
#    Autowc.start_water_changing()
    socketio.run(app, host='0.0.0.0', port=8080, debug=True)