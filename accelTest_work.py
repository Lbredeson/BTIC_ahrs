import time
import board
import busio
from adafruit_lsm6ds.ism330dhcx import ISM330DHCX
from ahrs.filters import Madgwick
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from multiprocessing import Process,Queue

def calibrate_sensor(sox, num_samples=1000):
    """Calibrate gyroscope bias."""
    gyro_bias = np.zeros(3)
    for _ in range(num_samples):
        gyro_bias += np.array(sox.gyro)
    return gyro_bias / num_samples
manual_gyro_bias = np.array([0.006795875774952921, -0.0014508049407202864, -0.002443460952792061])
def quaternion_to_euler(q):
    """Convert quaternion to roll and pitch angles."""
    w, x, y, z = q
    roll = np.arctan2(2.0 * (w * x + y * z), 1.0 - 2.0 * (x**2 + y**2))
    pitch = np.arcsin(2.0 * (w * y - z * x))
    return np.degrees(roll), np.degrees(pitch)

def plot_ahrs(q):
    """Plot 3D visualization of Pitch and Roll"""
    fig = plt.figure()
    ax = fig.add_subplot(111,projection='3d')
    
    ax.set_xlim([-180,180])
    ax.set_ylim([-180,180])
    ax.set_zlim([0,180])
    
    ax.set_xlabel('Roll (deg)')
    ax.set_ylabel('Pitch (deg)')
    ax.set_zlabel('Yaw (deg)')
    
    while True:
        try:
            Q = q.get_nowait()
        except queue.Empty:
            continue
        
        
        roll, pitch = quaternion_to_euler(Q[-1])
        
        ax.cla() #Clears previous plot
        ax.set_xlim([-180,180])
        ax.set_ylim([-180,180])
        ax.set_zlim([0,180])
        
        ax.set_xlabel('Roll (deg)')
        ax.set_ylabel('Pitch (deg)')
        ax.set_zlabel('Yaw (deg)')
        
        ax.scatter(roll,pitch,0, c='r', marker='o')
        plt.show()
        

def main():
    i2c = board.I2C()
    sox = ISM330DHCX(i2c)
    
    num_samples = 1
    
    # Calibrate the gyroscope
    gyro_bias = calibrate_sensor(sox)
    
    # Initialize arrays to store gyroscope and accelerometer data
    gyro_data = np.zeros((num_samples, 3))
    accel_data = np.zeros((num_samples, 3))
    
    madgwick = Madgwick()
    Q = np.tile([1., 0., 0., 0.], (num_samples, 1))  # Allocate for quaternions
    
    q = Queue()
    
    visualization_process = Process(target = plot_ahrs, args = (q,))
    visualization_process.start()
 
    while True:
        for t in range(num_samples):
            # Get the raw gyroscope data as a tuple
            gyro_tuple = sox.gyro
            
            # Apply manual bias correction
            gyro_data[t] = np.array(gyro_tuple) - gyro_bias - manual_gyro_bias
    
            # Store gyroscope data in the array after bias correction
            gyro_data[t] = np.array(gyro_tuple) - gyro_bias
    
            # Get the raw accelerometer data as a tuple
            accel_tuple = sox.acceleration
    
            # Store accelerometer data in the array
            accel_data[t] = np.array(accel_tuple)
    
            # Update Madgwick filter
            Q[t] = madgwick.updateIMU(Q[t - 1], gyr=gyro_data[t], acc=accel_data[t])
        
        q.put(Q)    
        # Example usage of quaternion to euler conversion
        roll, pitch = quaternion_to_euler(Q[-1])
        """print("Roll:", roll, "degrees")
        print("Pitch:", pitch, "degrees") """

if __name__ == "__main__":
    main()



