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
WIDTH, HEIGHT = 640, 380
CENTER = (WIDTH // 2, HEIGHT // 2)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

def pitch_angle_to_color(angle):
    # Convert the pitch angle to a color gradient centered on 0
    if 30 <= angle <= 90:
        normalized_angle = (angle - 30) / 60.0  # Normalize pitch angle to range [0, 1] between 30 and 90 degrees
        r = 255  # Red component
        g = int(255 * (1 - normalized_angle))  # Green component
        b = 0  # Blue component
        return r, g, b
    elif -30 <= angle <= 30:
        normalized_angle = abs(angle) / 30.0  # Normalize pitch angle to range [0, 1] between -30 and 30 degrees
        r = int(255 * normalized_angle)  # Red component, adjusted for a single gradient
        g = 255  # Green component
        b = 0  # Blue component
        return r, g, b
    elif -90 <= angle < -30:
        normalized_angle = (angle + 90) / 60.0  # Normalize pitch angle to range [0, 1] between -90 and -30 degrees
        r = 255  # Red component
        g = int(255 * (normalized_angle))  # Green component
        b = 0  # Blue component
        return r, g, b
    else:
        return RED

def roll_angle_to_color(angle):
    # Convert the roll angle to a color gradient centered on 0
    if 30 <= angle <= 90:
        normalized_angle = (angle - 30) / 60.0  # Normalize roll angle to range [0, 1] between 30 and 90 degrees
        r = 255  # Red component
        g = int(255 * (1 - normalized_angle))  # Green component
        b = 0  # Blue component
        return r, g, b
    elif -30 <= angle <= 30:
        normalized_angle = abs(angle) / 30.0  # Normalize roll angle to range [0, 1] between -30 and 30 degrees
        r = int(255 * normalized_angle)  # Red component, adjusted for a single gradient
        g = 255  # Green component
        b = 0  # Blue component
        return r, g, b
    elif -90 <= angle < -30:
        normalized_angle = (angle + 90) / 60.0  # Normalize roll angle to range [0, 1] between -90 and -30 degrees
        r = 255  # Red component
        g = int(255 * (normalized_angle))  # Green component
        b = 0  # Blue component
        return r, g, b
    else:
        return RED


def draw_horizon(screen, roll, pitch, pitch_block_pos, roll_block_pos):
    screen.fill(WHITE)

    # Draw pitch ruler on the left
    pitch_ruler_width = 10
    pitch_ruler_height = HEIGHT
    pitch_ruler_rect = pygame.Rect(0, 0, pitch_ruler_width, pitch_ruler_height)

    # Determine pitch ruler color gradient
    pitch_color = pitch_angle_to_color(pitch)
    pygame.draw.rect(screen, pitch_color, pitch_ruler_rect)

    # Draw pitch ruler numbers with fading effect
    pitch_interval = 10
    for angle in range(-40, 41, pitch_interval):
        if -40 <= angle <= 40:
            rotated_angle = angle - roll
            pitch_line_y = CENTER[1] - int((pitch_ruler_height / 180) * rotated_angle)
            alpha = int(255 * (1 - abs(angle) / 40))  # Fade in/out based on distance from current pitch
            font = pygame.font.Font(None, 24)
            text = font.render(str(angle), True, (BLUE[0], BLUE[1], BLUE[2], alpha))
            text_rect = text.get_rect(center=(pitch_ruler_width * 3, pitch_line_y))
            screen.blit(text, text_rect)

    # Draw pitch marker
    pitch_marker_y = CENTER[1]
    pygame.draw.polygon(screen, BLUE, [(pitch_ruler_width * 4, pitch_marker_y),
                                       (pitch_ruler_width * 5, pitch_marker_y + 10),
                                       (pitch_ruler_width * 5, pitch_marker_y - 10)])

    # Draw roll ruler on the top
    roll_ruler_width = WIDTH
    roll_ruler_height = 10
    roll_ruler_rect = pygame.Rect(0, 0, roll_ruler_width, roll_ruler_height)

    # Determine roll ruler color gradient
    roll_color = roll_angle_to_color(roll)
    pygame.draw.rect(screen, roll_color, roll_ruler_rect)

    # Draw roll ruler numbers with fading effect
    roll_interval = 10
    for angle in range(-40, 41, roll_interval):
        if -40 <= angle <= 40:
            rotated_angle = angle + pitch
            roll_line_x = CENTER[0] + int((roll_ruler_width / 180) * rotated_angle)
            alpha = int(255 * (1 - abs(angle) / 40))  # Fade in/out based on distance from current roll
            font = pygame.font.Font(None, 24)
            text = font.render(str(angle), True, (BLUE[0], BLUE[1], BLUE[2], alpha))
            text_rect = text.get_rect(center=(roll_line_x, roll_ruler_height * 3))
            screen.blit(text, text_rect)

    # Draw roll marker
    roll_marker_x = CENTER[0]
    pygame.draw.polygon(screen, GREEN, [(roll_marker_x - 10, roll_ruler_height * 4),
                                        (roll_marker_x + 10, roll_ruler_height * 4),
                                        (roll_marker_x, roll_ruler_height * 3)])

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
def draw_cube(screen, roll, pitch):
  
    cube_size = 50  # Adjust the cube size

    # Cube center at the center of the screen
    cube_center = (CENTER[0], CENTER[1])

    # Define cube vertices
    vertices = [
        (-cube_size / 2, -cube_size / 2, -cube_size / 2),
        (-cube_size / 2, cube_size / 2, -cube_size / 2),
        (cube_size / 2, cube_size / 2, -cube_size / 2),
        (cube_size / 2, -cube_size / 2, -cube_size / 2),
        (-cube_size / 2, -cube_size / 2, cube_size / 2),
        (-cube_size / 2, cube_size / 2, cube_size / 2),
        (cube_size / 2, cube_size / 2, cube_size / 2),
        (cube_size / 2, -cube_size / 2, cube_size / 2)
    ]

    # Rotate and project the cube vertices
    rotated_vertices = []
    for vertex in vertices:
        x, y, z = vertex

        # Rotate around the X-axis (pitch)
        y_rotated = y * math.cos(pitch) - z * math.sin(pitch)
        z_rotated = y * math.sin(pitch) + z * math.cos(pitch)

        # Rotate around the Y-axis (roll)
        x_rotated = x * math.cos(roll) + z_rotated * math.sin(roll)
        z_rotated = -x * math.sin(roll) + z_rotated * math.cos(roll)

        # Perspective projection
        depth = 500  # Arbitrary depth value
        scale = depth / (depth + z_rotated)
        x_projected = int(cube_center[0] + scale * x_rotated)
        y_projected = int(cube_center[1] + scale * y_rotated)

        rotated_vertices.append((x_projected, y_projected))

    # Draw cube edges
    edges = [
        (0, 1), (1, 2), (2, 3), (0, 3),
        (4, 5), (5, 6), (6, 7), (4, 7),
        (0, 4), (1, 5), (2, 6), (3, 7)
    ]

    for edge in edges:
        start = rotated_vertices[edge[0]]
        end = rotated_vertices[edge[1]]
        pygame.draw.line(screen, RED, start, end, 2)

def ahrs_main():
    i2c = board.I2C()
    sox = ISM330DHCX(i2c)
    
    num_samples = 10  # Increase the number of samples
    
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

    # Initial positions of moving blocks
    pitch_block_pos = CENTER[1]
    roll_block_pos = CENTER[0]
    
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
        draw_horizon(screen, roll, pitch, pitch_block_pos, roll_block_pos)
        draw_cube(screen, roll, pitch)
        # Control the speed of the visualization
        pygame.time.Clock().tick(60)

if __name__ == "__main__":
    ahrs_main()
