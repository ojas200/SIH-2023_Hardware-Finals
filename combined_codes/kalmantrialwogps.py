import mpu6050
import time
import numpy as np

# Create a new Mpu6050 object
mpu6050_sensor = mpu6050.mpu6050(0x68)

# Define a function to read the sensor data
def read_sensor_data():
    # Read the accelerometer values
    accelerometer_data = mpu6050_sensor.get_accel_data()

    # Read the gyroscope values
    gyroscope_data = mpu6050_sensor.get_gyro_data()

    # Read temp
    temperature = mpu6050_sensor.get_temp()

    return accelerometer_data, gyroscope_data, temperature

# Kalman Filter Initialization
# State [x, x_dot]
x = np.array([[0.0], [0.0]])  # Initial state (for simplicity, assume initial temp is 0 and no initial velocity)
P = np.array([[1000.0, 0.0], [0.0, 1000.0]])  # Initial covariance
A = np.array([[1.0, 1.0], [0.0, 1.0]])  # State transition matrix
H = np.array([[1.0, 0.0]])  # Measurement matrix
Q = np.array([[1e-3, 0.0], [0.0, 1e-3]])  # Process noise covariance
R = np.array([[0.01]])  # Measurement noise covariance

def kalman_filter(x, P, measurement):
    # Prediction step
    x = np.dot(A, x)
    P = np.dot(np.dot(A, P), A.T) + Q

    # Update step
    y = measurement - np.dot(H, x)
    S = np.dot(np.dot(H, P), H.T) + R
    K = np.dot(np.dot(P, H.T), np.linalg.inv(S))
    x = x + np.dot(K, y)
    P = P - np.dot(np.dot(K, H), P)

    return x, P

# Start a while loop to continuously read the sensor data
while True:
    # Read the sensor data
    accelerometer_data, gyroscope_data, temperature = read_sensor_data()

    # Perform Kalman filtering on temperature
    x, P = kalman_filter(x, P, np.array([[temperature]]))

    # Print the data
    print("Filtered Temp:", x[0, 0])
    print("Accelerometer data:", accelerometer_data)
    print("Gyroscope data:", gyroscope_data)

    # Wait for 1 second
    time.sleep(1)