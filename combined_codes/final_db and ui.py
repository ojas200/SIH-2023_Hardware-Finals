from flask import Flask, render_template
import random
import time
import string
import pynmea2
import bmpsensor
import smbus
from time import sleep
import RPi.GPIO as GPIO
import mysql.connector

app = Flask(__name__)

# Ultrasonic initialisation
trigger_pin = 18
echo_pin = 27

# Set up GPIO mode and pins
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(trigger_pin, GPIO.OUT)
GPIO.setup(echo_pin, GPIO.IN)

def measure_distance():
    # Send a trigger pulse
    GPIO.output(trigger_pin, GPIO.HIGH)
    time.sleep(0.00001)
    GPIO.output(trigger_pin, GPIO.LOW)

    # Wait for the echo pulse
    start_time = time.time()
    stop_time = start_time  # Initialize stop_time

    while GPIO.input(echo_pin) == 0:
        if time.time() - start_time > 1.0:
            print("Timeout waiting for echo pulse (LOW)")
            break

    start_time = time.time()
    while GPIO.input(echo_pin) == 1:
        if time.time() - start_time > 1.0:
            print("Timeout waiting for echo pulse (HIGH)")
            break
        stop_time = time.time()  # Update stop_time

    else:
        print("Echo pulse received successfully")
        elapsed_time = stop_time - start_time
        speed_of_sound = 34300  # Speed of sound in cm/s
        distance = (elapsed_time * speed_of_sound) / 2

        return distance

# Function to calculate elevation
def elevation_from_pressure(pressure): 
     # Constants
     sea_level_pressure = 101325  # Pa
     lapse_rate = 0.0065  # degrees Celsius per meter
    
     temperature_at_sea_level = 15.0  
     temperature_at_elevation = temperature_at_sea_level - lapse_rate * ((pressure / sea_level_pressure) ** (1 / 5.257))
    
     elevation = (temperature_at_sea_level - temperature_at_elevation) / lapse_rate
     return elevation

@app.route('/')
def index():
    # BMP
    temp, pressure, altitude = bmpsensor.readBmp180()

    # Calculate elevation
    calculated_elevation = elevation_from_pressure(pressure)
  
    # GPS
    port="/dev/ttyAMA0"
    ser=serial.Serial(port, baudrate=9600, timeout=0.5)
    dataout = pynmea2.NMEAStreamReader()
    newdata=ser.readline()
    if newdata.startswith(b'$GPGSA'):
        newmsg=pynmea2.parse(newdata.decode('utf-8'))
        lat=newmsg.latitude
        lng=newmsg.longitude

    # Measure depth (ultrasonic)
    distance = measure_distance()

    # Establish connection to the database
    connection = mysql.connector.connect(
        host="localhost",
        user="sih",  # Replace with your MySQL username
        password="elgear123!",  # Replace with your MySQL password
        database="mine_data"  # Replace with your database name
    )

    # Create a cursor object to execute SQL queries
    cursor = connection.cursor()

    # Fetch readings from the database
    cursor.execute("SELECT Latitude, Longitude, Elevation, Temperature, Depth, Ore_Concentration FROM new_ore_data")
    db_rows = cursor.fetchall()
    db_readings1 = [row[0] for row in db_rows]
    db_readings2 = [row[1] for row in db_rows]
    db_readings3 = [row[2] for row in db_rows]
    db_readings5 = [row[5] for row in db_rows]
    # Sensor readings
    sensor_reading1 = temp
    sensor_reading2 = pressure
    sensor_reading3 = calculated_elevation               #Take from sensors

    # Find the nearest value
    nearest_value1 = [x - sensor_reading1 for x in db_readings1]
    nearest_value2 = [x - sensor_reading2 for x in db_readings2]
    nearest_value3 = [x - sensor_reading3 for x in db_readings3]

    l = []
    for i in range(len(nearest_value1)):
        sum_values = nearest_value1[i] + nearest_value2[i] + nearest_value3[i]
        r = sum_values / 3
        if r < 1:
            l.append(r)

    x = min(l)
    y = l.index(x)
    print(db_rows[y - 1])
    nearest_value = [column[0] for column in db_rows]
    print(f"Sensor Reading: {sensor_reading1, sensor_reading2, sensor_reading3}")
    print(f"Nearest Value from Database: {nearest_value}")

    # Close the cursor and connection
    cursor.close()
    connection.close()

    return render_template('index.html', latitude=lat, longitude=lng, elevation=calculated_elevation,
                           sensor_reading1=sensor_reading1, sensor_reading2=sensor_reading2, sensor_reading3=sensor_reading3, depth=distance)

if __name__ == '__main__':
    app.run(debug=True)
