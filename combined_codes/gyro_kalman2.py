import time
import numpy as np
from filterpy.kalman import KalmanFilter
import mpu6050

# Function to get initial GPS data
def get_initial_gps_data():
    return {'latitude': 40.7128, 'longitude': -74.0060, 'elevation': 10.0}

# Create a new Mpu6050 object
mpu6050_sensor = mpu6050.mpu6050(0x68)

# Sensor Fusion Logic
def fuse_data(gps_data, mpu_data):
    fused_data = {
        'acceleration': mpu_data['acceleration'],
        'gyroscope': mpu_data['gyroscope'],
        'latitude': gps_data['latitude'],
        'longitude': gps_data['longitude'],
        'elevation': gps_data['elevation']
    }
    return fused_data

# Kalman Filter Initialization
def initialize_kalman_filter(initial_state):
    kf = KalmanFilter(dim_x=9, dim_z=6)
    dt = 1.0
    # Define the observation matrix H
    kf.H = np.array([
        [1, 0, 0, 0, 0, 0, 0, 0, 0],  # Latitude
        [0, 1, 0, 0, 0, 0, 0, 0, 0],  # Longitude
        [0, 0, 1, 0, 0, 0, 0, 0, 0],  # Elevation
        [0, 0, 0, 1, 0, 0, 0, 0, 0],  # Acceleration x
        [0, 0, 0, 0, 1, 0, 0, 0, 0],  # Acceleration y
        [0, 0, 0, 0, 0, 1, 0, 0, 0]   # Acceleration z
    ])
    kf.R = np.diag([0.1, 0.1, 0.1, 0.1, 0.1, 0.1])
    kf.Q = 1e-4 * np.eye(9)
    kf.P *= 1e2
    
    # ... (rest of the Kalman filter parameters initialization)
    return kf

# Kalman Filter Update
def update_kalman_filter(kf, measurement):
    measurement_column = measurement.reshape(-1, 1)  # Ensure measurement is a column vector
    kf.update(measurement_column)

# Kalman Filter Prediction
def predict_path(kf):
    kf.predict()
    return kf.x[:3]

def main():
    initial_gps_coords = get_initial_gps_data()
    initial_state = [
        initial_gps_coords['latitude'],
        initial_gps_coords['longitude'],
        initial_gps_coords['elevation'],
        0, 0, 0, 0, 0, 0
    ]

    kf = initialize_kalman_filter(initial_state)

    try:
        while True:
            gps_data = initial_gps_coords
            mpu_data = {
                'acceleration': mpu6050_sensor.get_accel_data(),
                'gyroscope': mpu6050_sensor.get_gyro_data()
            }

            fused_data = fuse_data(gps_data, mpu_data)

            measurement = np.array([
                gps_data['latitude'], gps_data['longitude'], gps_data['elevation'],
                fused_data['acceleration']['x'], fused_data['acceleration']['y'], fused_data['acceleration']['z']
            ])

            update_kalman_filter(kf, measurement)

            next_path = predict_path(kf)
            print("Predicted Next Path:", next_path)

            time.sleep(1)

    except KeyboardInterrupt:
        print("Program terminated by user.")

if __name__ == "__main__":
    main()