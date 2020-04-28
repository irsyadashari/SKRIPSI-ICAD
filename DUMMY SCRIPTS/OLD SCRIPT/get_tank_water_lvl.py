# this is a crontab job for taking the water lvl from background

import sqlite3
import sys
import RPi.GPIO as GPIO
import os
import time
import schedule
import glob

from AquariumAutomation import JSNDistance

#Tinggi Sensor jika tank Kosong
mainTankDistance = 38 #calibrate this
secondTankDistance = 45 #calibrate this

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

#Kasih idle dlu
GPIO.output(GPIO_TRIGGER_MAIN, False)
GPIO.output(GPIO_TRIGGER_SECONDARY, False)

def store_water_lvl(main_tank, second_tank):
    conn=sqlite3.connect('/var/www/lab_app/tankwaterlvl.db')
    curs=conn.cursor()
    curs.execute("""UPDATE waterlvl SET maintank=(?) WHERE id=1""", (main_tank,))
    curs.execute("""UPDATE waterlvl SET secondtank=(?) WHERE id=1""", (second_tank,))
    curs.execute("SELECT * FROM waterlvl") 
    temp = curs.fetchall()
    for row in temp:
        print(row[2])
        print(row[3])
    conn.commit()
    conn.close()
    
    
main_tank_wlvl = JSNDistance.measureTank(GPIO_TRIGGER_MAIN,GPIO_ECHO_MAIN,mainTankDistance)

second_tank_wlvl = JSNDistance.measureTank(GPIO_TRIGGER_SECONDARY,GPIO_ECHO_SECONDARY, secondTankDistance)
#main_tank_wlvl = 6
#second_tank_wlvl = 7 

if main_tank_wlvl is not None and second_tank_wlvl is not None:
    store_water_lvl(float(main_tank_wlvl),float(second_tank_wlvl))
else:
	store_water_lvl(0,0)
    

    

    