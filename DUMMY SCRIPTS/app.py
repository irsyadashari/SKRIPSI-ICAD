#script
from flask import Flask, render_template, request, session, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_socketio import SocketIO, send, emit
from AquariumAutomation import DSTemp, JSNDistance, Autowc, CurrentACS, SENTurbidity
from flask_apscheduler import APScheduler
from threading import Thread, Event
from flask_wtf import FlaskForm 
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

import RPi.GPIO as GPIO
import os
import time
import schedule
import glob

app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = 'fishwebmonitoringsystem'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////var/www/lab_app/login.db'
Bootstrap(app)
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
app.config['DEBUG'] = True
scheduler = APScheduler()
thread = None

#Inisiasi skema table dalam table database
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))

#Memuat id user yang sedang login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

#inisiasi atribut dalam login page
class LoginForm(FlaskForm):
    username = StringField('username', validators=[InputRequired(), Length(min=6, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=6, max=80)])
    remember = BooleanField('remember me')

#Inisiasi mode Bus 1-Wire
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

#Tinggi Sensor jika tank Kosong
mainTankDistance = 72 #calibrate this
secondTankDistance = 63 #calibrate this

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

#Membuat pin stand by di posisi LOW
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
 
GPIO.output(17, GPIO.LOW)
GPIO.output(23, GPIO.LOW)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()  
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if user.password == form.password.data:
                login_user(user, remember=form.remember.data)
                return redirect(url_for('main'))
        
    return render_template('login.html', form=form)
    
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route("/")
def forwarding():
    return redirect(url_for('login'))

@app.route("/home")
@login_required
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
    
#    hour, minutes = CurrentACS.get_battery_estimated_life(50,CurrentACS.get_current_values(1),20)
    hour, minutes = CurrentACS.get_battery_estimated_life(50,4.187,20)
    
    return render_template('home.html',mainTankWaterLvl = var_mainTankWaterLvl, secondaryTankWaterLvl = var_secondaryTankWaterLvl ,mainTankTemperature = var_mainTankTemperature, secondaryTankTemperature = var_secondaryTankTemperature ,**templateData, hour=str("%.0f" % hour), minutes=str("%.0f" % minutes), powerMode="Baterai")    



#scheduler.add_job(id = 'waterchange', func = Autowc.detect_water_change, trigger = 'interval', hour = 24)

#scheduler.start()

if __name__ == "__main__":
   app.run(host='0.0.0.0', port=8080,debug=True)
