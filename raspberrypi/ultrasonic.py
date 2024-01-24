import RPi.GPIO as GPIO
import time

# Define GPIO pins
trigger_pin = 12
echo_pin = 13


# Set up GPIO mode and pins
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)  # Disable GPIO warnings
GPIO.setup(trigger_pin, GPIO.OUT)
GPIO.setup(echo_pin, GPIO.IN)
stop_time = 0.0;

def measure_distance():
    # Send a trigger pulse
    GPIO.output(trigger_pin, GPIO.HIGH)
    time.sleep(0.00001)
    GPIO.output(trigger_pin, GPIO.LOW)

    # Wait for the echo pulse
    start_time = time.time()
    while GPIO.input(echo_pin) == 0:
        if time.time() - start_time > 1.0:
            print("Timeout waiting for echo pulse (LOW)")
            break

    
    while GPIO.input(echo_pin) == 1:
        if time.time() - start_time > 1.0:
            print("Timeout waiting for echo pulse (HIGH)")
            break
    else:
        stop_time = time.time()
        print("Echo pulse received successfully")

    # Calculate distance in centimeters
    elapsed_time = stop_time - start_time
    speed_of_sound = 34300  # Speed of sound in cm/s
    distance = (elapsed_time * speed_of_sound) / 2

    return distance

try:
    while True:
        # Measure distance and print the result
        distance = measure_distance()
        print(f'Distance: {distance:.2f} cm')
        time.sleep(1)

except KeyboardInterrupt:
    pass
finally:
    GPIO.cleanup()