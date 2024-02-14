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

def draw_cube(screen, roll, pitch):
    cube_size = 50  # Adjust the cube size
    cube_center = (CENTER[0], CENTER[1] + cube_size)  # Adjust cube center

    # Calculate cube rotation angles based on pitch and roll
    roll_angle = math.radians(roll)
    pitch_angle = math.radians(pitch)

    # Define cube vertices
    vertices = [
        (-cube_size, -cube_size, -cube_size),
        (-cube_size, cube_size, -cube_size),
        (cube_size, cube_size, -cube_size),
        (cube_size, -cube_size, -cube_size),
        (-cube_size, -cube_size, cube_size),
        (-cube_size, cube_size, cube_size),
        (cube_size, cube_size, cube_size),
        (cube_size, -cube_size, cube_size)
    ]

    # Define colors for each face
    face_colors = [
        (255, 0, 0),    # Red
        (0, 255, 0),    # Green
        (0, 0, 255),    # Blue
        (255, 255, 0),  # Yellow
        (255, 0, 255),  # Magenta
        (0, 255, 255),  # Cyan
    ]

    # Rotate and project the cube vertices
    rotated_vertices = []
    for vertex in vertices:
        x, y, z = vertex

        # Rotate around the X-axis (pitch)
        y_rotated = y * math.cos(pitch_angle) - z * math.sin(pitch_angle)
        z_rotated = y * math.sin(pitch_angle) + z * math.cos(pitch_angle)

        # Rotate around the Y-axis (roll)
        x_rotated = x * math.cos(roll_angle) + z_rotated * math.sin(roll_angle)
        z_rotated = -x * math.sin(roll_angle) + z_rotated * math.cos(roll_angle)

        # Perspective projection
        depth = 500  # Arbitrary depth value
        scale = depth / (depth + z_rotated)
        x_projected = int(cube_center[0] + scale * x_rotated)
        y_projected = int(cube_center[1] + scale * y_rotated)

        rotated_vertices.append((x_projected, y_projected))

    # Draw each face of the cube with backface culling
    faces = [
        (0, 1, 2, 3),
        (4, 5, 6, 7),
        (0, 4, 7, 3),
        (1, 5, 6, 2),
        (0, 1, 5, 4),
        (2, 3, 7, 6),
    ]

    viewer_vector = np.array([0, 0, -1])  # Vector pointing towards the viewer

    for i, face in enumerate(faces):
        # Calculate the normal vector of the face
        normal_vector = np.cross(np.array(vertices[face[1]]) - np.array(vertices[face[0]]),
                                 np.array(vertices[face[2]]) - np.array(vertices[face[0]]))
        
        # Check the sign of the dot product with the viewer vector
        dot_product = np.dot(normal_vector, viewer_vector)
        
        if dot_product < 0:
            pygame.draw.polygon(screen, face_colors[i], [rotated_vertices[j] for j in face])

    # Draw cube edges
    edges = [
        (0, 1), (1, 2), (2, 3), (0, 3),
        (4, 5), (5, 6), (6, 7), (4, 7),
        (0, 4), (1, 5), (2, 6), (3, 7)
    ]

    for edge in edges:
        start = rotated_vertices[edge[0]]
        end = rotated_vertices[edge[1]]
        pygame.draw.line(screen, (0, 0, 0), start, end, 2)  # Black lines for edges




def calibrate_sensor(sox, num_samples=1000):
    gyro_bias = np.zeros(3)
    for _ in range(num_samples):
        gyro_bias += np.array(sox.gyro)
    return gyro_bias / num_samples

manual_gyro_bias = np.array([0.006795875774952921, -0.0014508049407202864, -0.002443460952792061])

def quaternion_to_euler(q):
    w, x, y, z = q
    # Only allow rotation around x and y axes
    roll = np.arctan2(2.0 * (w * x + y * z), 1.0 - 2.0 * (x**2 + y**2))
    pitch = np.arcsin(2.0 * (w * y - x * z))
    return np.degrees(roll), np.degrees(pitch)

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
        draw_cube(screen, roll, pitch)
        pygame.time.Clock().tick(60)
        pygame.display.flip()

if __name__ == "__main__":
    ahrs_main()
