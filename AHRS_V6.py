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
RED = (255, 0, 0)
IMAGE_SCALE = 0.3

def pitch_angle_to_color(angle):
    # Convert the pitch angle to a color gradient centered on 0
    if 30 <= angle <= 90:
        normalized_angle = (angle - 30) / 60.0
        r = 255
        g = int(255 * (1 - normalized_angle))
        b = 0
        return r, g, b
    elif -30 <= angle <= 30:
        normalized_angle = abs(angle) / 30.0
        r = int(255 * normalized_angle)
        g = 255
        b = 0
        return r, g, b
    elif -90 <= angle < -30:
        normalized_angle = (angle + 90) / 60.0
        r = 255
        g = int(255 * (normalized_angle))
        b = 0
        return r, g, b
    else:
        return RED

def roll_angle_to_color(angle):
    # Convert the roll angle to a color gradient centered on 0
    if 30 <= angle <= 90:
        normalized_angle = (angle - 30) / 60.0
        r = 255
        g = int(255 * (1 - normalized_angle))
        b = 0
        return r, g, b
    elif -30 <= angle <= 30:
        normalized_angle = abs(angle) / 30.0
        r = int(255 * normalized_angle)
        g = 255
        b = 0
        return r, g, b
    elif -90 <= angle < -30:
        normalized_angle = (angle + 90) / 60.0
        r = 255
        g = int(255 * (normalized_angle))
        b = 0
        return r, g, b
    else:
        return RED

def draw_horizon(screen, roll, pitch):
    screen.fill(WHITE)

    pitch_ruler_width = 10
    pitch_ruler_height = HEIGHT
    pitch_ruler_rect = pygame.Rect(0, 0, pitch_ruler_width, pitch_ruler_height)

    pitch_color = pitch_angle_to_color(roll)
    pygame.draw.rect(screen, pitch_color, pitch_ruler_rect)

    pitch_interval = 10
    for angle in range(-40, 41, pitch_interval):
        if -40 <= angle <= 40:
            rotated_angle = angle - roll
            pitch_line_y = CENTER[1] - int((pitch_ruler_height / 180) * rotated_angle)
            alpha = int(255 * (1 - abs(angle) / 40))
            font = pygame.font.Font(None, 24)
            text = font.render(str(angle), True, (RED[0], RED[1], RED[2], alpha))
            text_rect = text.get_rect(center=(pitch_ruler_width * 3, pitch_line_y))
            screen.blit(text, text_rect)

    pitch_marker_y = CENTER[1]
    pygame.draw.polygon(screen, RED, [(pitch_ruler_width * 4, pitch_marker_y),
                                       (pitch_ruler_width * 5, pitch_marker_y + 10),
                                       (pitch_ruler_width * 5, pitch_marker_y - 10)])

    roll_ruler_width = WIDTH
    roll_ruler_height = 10
    roll_ruler_rect = pygame.Rect(0, 0, roll_ruler_width, roll_ruler_height)

    roll_color = roll_angle_to_color(pitch)
    pygame.draw.rect(screen, roll_color, roll_ruler_rect)

    roll_interval = 10
    for angle in range(-40, 41, roll_interval):
        if -40 <= angle <= 40:
            rotated_angle = angle + pitch
            roll_line_x = CENTER[0] + int((roll_ruler_width / 180) * rotated_angle)
            alpha = int(255 * (1 - abs(angle) / 40))
            font = pygame.font.Font(None, 24)
            text = font.render(str(angle), True, (RED[0], RED[1], RED[2], alpha))
            text_rect = text.get_rect(center=(roll_line_x, roll_ruler_height * 3))
            screen.blit(text, text_rect)

    roll_marker_x = CENTER[0]
    pygame.draw.polygon(screen, RED, [(roll_marker_x - 10, roll_ruler_height * 4),
                                        (roll_marker_x + 10, roll_ruler_height * 4),
                                        (roll_marker_x, roll_ruler_height * 3)])

    pygame.display.flip()


def rotate_image(image, angle):
    # Rotate the image
    rotated_image = pygame.transform.rotate(image, angle)
    return rotated_image

def scale_image(image, scale_factor):
    # Scale down the image
    scaled_width = int(image.get_width() * scale_factor)
    scaled_height = int(image.get_height() * scale_factor)
    scaled_image = pygame.transform.scale(image, (scaled_width, scaled_height))
    return scaled_image

def quaternion_to_euler(q):
    """Convert quaternion to roll and pitch angles."""
    w, x, y, z = q
    roll = np.arctan2(2.0 * (w * x + y * z), 1.0 - 2.0 * (x**2 + y**2))
    pitch = np.arcsin(2.0 * (w * y - z * x))
    return np.degrees(roll), np.degrees(pitch)

def calibrate_sensor(sox, num_samples=1000):
    gyro_bias = np.zeros(3)
    for _ in range(num_samples):
        gyro_bias += np.array(sox.gyro)
    return gyro_bias / num_samples

manual_gyro_bias = np.array([0.006795875774952921, -0.0014508049407202864, -0.002443460952792061])
def ahrs_main():
    i2c = board.I2C()
    sox = ISM330DHCX(i2c)
    
    num_samples = 10
    
    gyro_bias = calibrate_sensor(sox)
    
    gyro_data = np.zeros((num_samples, 3))
    accel_data = np.zeros((num_samples, 3))
    
    madgwick = Madgwick()
    Q = np.tile([1., 0., 0., 0.], (num_samples, 1))
    
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('AHRS Visualization')

    # Load image
    image = pygame.image.load("/home/raspberry/Accel/Rover GUI Images/Ortho_Rear_PNG.PNG")  # Replace "image.png" with the path to your image
    scaled_image = scale_image(image, IMAGE_SCALE)
    while True:
        for t in range(num_samples):
            gyro_tuple = sox.gyro
            gyro_data[t] = np.array(gyro_tuple) - gyro_bias - manual_gyro_bias
            accel_tuple = sox.acceleration
            accel_data[t] = np.array(accel_tuple)
            Q[t] = madgwick.updateIMU(Q[t - 1], gyr=gyro_data[t], acc=accel_data[t])
        
        roll, pitch = quaternion_to_euler(Q[-1])

        # Pygame-based AHRS visualization
        draw_horizon(screen, roll, pitch)
        
        
        # Rotate the image and draw it on the screen
        rotated_image = rotate_image(scaled_image, roll)  # Rotate based on roll angle
        screen.blit(rotated_image, (WIDTH + rotated_image.get_width())// 2, (HEIGHT - rotated_image.get_height()) // 2)
        
        pygame.time.Clock().tick(60)
        pygame.display.flip()

if __name__ == "__main__":
    ahrs_main()
