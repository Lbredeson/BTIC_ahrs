import pygame
import sys
import math

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 640,380
CENTER = (WIDTH // 2, HEIGHT // 2)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
IMAGE_SCALE_FACTOR = 0.35  # Adjust the scale factor as needed
PITCH_ROLL_SPEED = 1  # Adjust the speed of pitch and roll adjustments

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

    pitch_color = pitch_angle_to_color(pitch)
    pygame.draw.rect(screen, pitch_color, pitch_ruler_rect)

    pitch_interval = 10
    for angle in range(-40, 41, pitch_interval):
        if -40 <= angle <= 40:
            rotated_angle = angle - pitch 
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

    roll_color = roll_angle_to_color(roll)
    pygame.draw.rect(screen, roll_color, roll_ruler_rect)

    roll_interval = 10
    for angle in range(-40, 41, roll_interval):
        if -40 <= angle <= 40:
            rotated_angle = roll + angle
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

def rotate_image(image, angle, circle_center):
    """Rotate an image around its center and calculate the new position to keep it centered at a given point."""
    # Rotate the image
    rotated_image = pygame.transform.rotate(image, angle)
    # Get the new image's size
    w, h = rotated_image.get_size()
    # Calculate the new position to keep the image centered on the circle center
    image_center = (circle_center[0] - w // 2, circle_center[1] - h // 2)
    
    return rotated_image, image_center


def scale_image(image, scale_factor):
    # Scale down the image
    scaled_width = int(image.get_width() * scale_factor)
    scaled_height = int(image.get_height() * scale_factor)
    scaled_image = pygame.transform.scale(image, (scaled_width, scaled_height))
    return scaled_image

def ahrs_main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('AHRS Visualization')

    # Load and scale the images
    left_image = pygame.image.load("Rover GUI Images/Ortho_Rear_PNG.PNG")  # Ensure correct path
    left_image = scale_image(left_image, IMAGE_SCALE_FACTOR)

    right_image = pygame.image.load("Rover GUI Images/Ortho_Right_PNG.PNG")  # Ensure correct path
    right_image = scale_image(right_image, IMAGE_SCALE_FACTOR)

    # Create back buffer surface
    back_buffer = pygame.Surface((WIDTH, HEIGHT))

    # Initial pitch and roll angles
    pitch_angle = 0
    roll_angle = 0

    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    pitch_angle += PITCH_ROLL_SPEED
                elif event.key == pygame.K_DOWN:
                    pitch_angle -= PITCH_ROLL_SPEED
                elif event.key == pygame.K_LEFT:
                    roll_angle -= PITCH_ROLL_SPEED
                elif event.key == pygame.K_RIGHT:
                    roll_angle += PITCH_ROLL_SPEED

        # Clear the back buffer
        back_buffer.fill(WHITE)

        # Draw horizon
        draw_horizon(back_buffer, roll_angle, pitch_angle)
        
        # Define circle centers for each image
        left_circle_center = (WIDTH // 4, HEIGHT // 2)  # Center for the left image
        right_circle_center = (3 * WIDTH // 4, HEIGHT // 2)  # Center for the right image

        # Rotate and blit the left image to the back buffer
        rotated_left_image, new_position_left = rotate_image(left_image, roll_angle, left_circle_center)
        back_buffer.blit(rotated_left_image, new_position_left)

        # Rotate and blit the right image to the back buffer
        rotated_right_image, new_position_right = rotate_image(right_image, pitch_angle, right_circle_center)
        back_buffer.blit(rotated_right_image, new_position_right)

        # Blit the back buffer to the screen
        screen.blit(back_buffer, (0, 0))

        # Update the display
        pygame.display.flip()

        # Cap the frame rate
        clock.tick(60)

if __name__ == "__main__":
    ahrs_main()


#((WIDTH - rotated_left_image.get_width()) // 4, (HEIGHT - rotated_left_image.get_height()) // 2))
