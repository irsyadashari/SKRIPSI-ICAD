from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, render_template, request, session

sched = BackgroundScheduler()

def job_function():
    a = 0
    print("Hello World")
    a+=1

    
sched.add_job(job_function, 'interval', seconds=10)
sched.start()