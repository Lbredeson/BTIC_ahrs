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
WIDTH, HEIGHT = 800, 800
CENTER = (WIDTH // 2, HEIGHT // 2)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)

def draw_horizon(screen, roll, pitch):
    screen.fill(WHITE)

    # Draw pitch ruler on the left
    pitch_ruler_width = 30
    pitch_ruler_height = HEIGHT
    pitch_ruler_rect = pygame.Rect(0, 0, pitch_ruler_width, pitch_ruler_height)
    pygame.draw.rect(screen, BLUE, pitch_ruler_rect)

    # Draw pitch ruler numbers
    pitch_interval = 10
    for angle in range(-90, 91, pitch_interval):
        pitch_line_y = CENTER[1] - int((pitch_ruler_height / 180) * angle)
        pygame.draw.line(screen, BLUE, (pitch_ruler_width, pitch_line_y), (pitch_ruler_width * 2, pitch_line_y), 2)
        font = pygame.font.Font(None, 24)
        text = font.render(str(angle), True, BLUE)
        text_rect = text.get_rect(center=(pitch_ruler_width * 3, pitch_line_y))
        screen.blit(text, text_rect)

    # Draw pitch marker
    pitch_marker_y = CENTER[1] - int((pitch_ruler_height / 180) * pitch)
    pygame.draw.circle(screen, BLUE, (pitch_ruler_width * 4, pitch_marker_y), 10)

    # Draw roll ruler on the top
    roll_ruler_width = WIDTH
    roll_ruler_height = 30
    roll_ruler_rect = pygame.Rect(0, 0, roll_ruler_width, roll_ruler_height)
    pygame.draw.rect(screen, BLUE, roll_ruler_rect)

    # Draw roll ruler numbers
    roll_interval = 10
    for angle in range(-90, 91, roll_interval):
        roll_line_x = CENTER[0] + int((roll_ruler_width / 180) * angle)
        pygame.draw.line(screen, BLUE, (roll_line_x, roll_ruler_height), (roll_line_x, roll_ruler_height * 2), 2)
        font = pygame.font.Font(None, 24)
        text = font.render(str(angle), True, BLUE)
        text_rect = text.get_rect(center=(roll_line_x, roll_ruler_height * 3))
        screen.blit(text, text_rect)

    # Draw roll marker
    roll_marker_x = CENTER[0] + int((roll_ruler_width / 180) * roll)
    pygame.draw.circle(screen, BLUE, (roll_marker_x, roll_ruler_height * 4), 10)

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
    
    num_samples = 100
    
    # Calibrate the gyroscope
    gyro_bias = calibrate_sensor(sox)
    
    # Initialize arrays to store gyroscope and accelerometer data
    gyro_data = np.zeros((num_samples, 3))
    accel_data = np.zeros((num_samples, 3))
    accelerometer_data_rate = 6700
    gyroscope_data_rate = 6700
    
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
