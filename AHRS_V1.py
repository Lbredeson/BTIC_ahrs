import pygame
import sys
import math
import board
import busio
from adafruit_lsm6ds.ism330dhcx import ISM330DHCX
from ahrs.filters import Madgwick
import numpy as np

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 400, 400
CENTER = (WIDTH // 2, HEIGHT // 2)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)

def draw_horizon(screen, roll, pitch):
    screen.fill(WHITE)
    
    # Draw horizon
    pygame.draw.rect(screen, BLUE, (0, CENTER[1], WIDTH, 2))
    
    # Draw pitch indicator line
    pitch_angle = pitch
    pitch_line_length = 50
    pitch_line_x = CENTER[0] + int(pitch_line_length * math.cos(math.radians(pitch_angle)))
    pitch_line_y = CENTER[1] - int(pitch_line_length * math.sin(math.radians(pitch_angle)))
    pygame.draw.line(screen, BLUE, CENTER, (pitch_line_x, pitch_line_y), 2)
    
    # Draw roll indicator line
    roll_angle = roll
    roll_line_length = 50
    roll_line_x = CENTER[0] + int(roll_line_length * math.sin(math.radians(roll_angle)))
    roll_line_y = CENTER[1] - int(roll_line_length * math.cos(math.radians(roll_angle)))
    pygame.draw.line(screen, BLUE, CENTER, (roll_line_x, roll_line_y), 2)

    pygame.display.flip()

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

def ahrs_main():
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
    
    # Pygame initialization
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('AHRS Visualization')
    
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
        
        # Example usage of quaternion to euler conversion
        roll, pitch = quaternion_to_euler(Q[-1])
        print("Roll:", roll, "degrees")
        print("Pitch:", pitch, "degrees")

        # Pygame-based AHRS visualization
        draw_horizon(screen, roll, pitch)

        # Control the speed of the visualization
        pygame.time.Clock().tick(60)

if __name__ == "__main__":
    ahrs_main()
