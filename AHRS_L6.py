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
            rotated_angle = angle + pitch 
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
            rotated_angle = roll - angle
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

def draw_angle_markers(screen, center, radius, current_angle, is_pitch=False):
    """Draw static angle markers like a protractor around a circle, and a moving marker for the current angle."""
    font = pygame.font.Font(None, 24)
    marker_length = 10  # Length of the marker lines extending out from the circle

    # Define angles for static markers
    for angle in range(-90, 91, 30):  # Range from -90 to 90 with a step of 30
        # Adjust the drawing angle based on whether it is pitch or roll
        if is_pitch:
            draw_angle = angle
        else:
            draw_angle = 90 - angle  # To place 0 at the top for roll

        rad_angle = math.radians(draw_angle)
        inner_pos = (center[0] + radius * math.cos(rad_angle), center[1] - radius * math.sin(rad_angle))
        outer_pos = (center[0] + (radius + marker_length) * math.cos(rad_angle),
                     center[1] - (radius + marker_length) * math.sin(rad_angle))
        
        # Draw marker line
        pygame.draw.line(screen, RED, inner_pos, outer_pos, 2)

        # Draw angle text
        text = font.render(str(angle), True, RED)
        text_rect = text.get_rect(center=(outer_pos[0], outer_pos[1] - 10))
        screen.blit(text, text_rect)

    # Draw moving marker for current angle
    current_draw_angle = -current_angle if is_pitch else 90 - current_angle
    current_rad = math.radians(current_draw_angle)
    marker_pos = (center[0] + radius * math.cos(current_rad), center[1] - radius * math.sin(current_rad))
    pygame.draw.circle(screen, RED, marker_pos, 5)  # Moving marker



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

    # Font for data boxes and angle markers
    font = pygame.font.Font(None, 24)

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

        # Draw horizon remains unchanged

        # Define circle properties
        circle_radius = 100
        left_circle_center = (WIDTH // 4, HEIGHT // 2)  # Center for the left image (Roll)
        right_circle_center = (3 * WIDTH // 4, HEIGHT // 2)  # Center for the right image (Pitch)

        # Rotate and blit the images to the back buffer, negating the angles to correct rotation direction
        rotated_left_image, new_position_left = rotate_image(left_image, -roll_angle, left_circle_center)
        back_buffer.blit(rotated_left_image, new_position_left)

        rotated_right_image, new_position_right = rotate_image(right_image, -pitch_angle, right_circle_center)
        back_buffer.blit(rotated_right_image, new_position_right)

        # Draw circles around the images
        pygame.draw.circle(back_buffer, RED, left_circle_center, circle_radius, 2)
        pygame.draw.circle(back_buffer, RED, right_circle_center, circle_radius, 2)

        # Draw angle markers and moving marker for roll
        draw_angle_markers(back_buffer, left_circle_center, circle_radius, roll_angle)

        # Draw angle markers and moving marker for pitch
        draw_angle_markers(back_buffer, right_circle_center, circle_radius, pitch_angle, is_pitch=True)

        # Draw data boxes for roll and pitch
        roll_text = font.render(f"Roll: {roll_angle:.3f}°", True, RED)
        pitch_text = font.render(f"Pitch: {-pitch_angle:.3f}°", True, RED)

        # Position data boxes
        roll_text_rect = roll_text.get_rect(topright=(WIDTH - 10, 10))
        pitch_text_rect = pitch_text.get_rect(topright=(WIDTH - 10, 30))

        # Blit data boxes onto the back buffer
        back_buffer.blit(roll_text, roll_text_rect)
        back_buffer.blit(pitch_text, pitch_text_rect)

        # Blit the back buffer to the screen
        screen.blit(back_buffer, (0, 0))

        # Update the display
        pygame.display.flip()

        # Cap the frame rate
        clock.tick(60)


if __name__ == "__main__":
    ahrs_main()

#((WIDTH - rotated_left_image.get_width()) // 4, (HEIGHT - rotated_left_image.get_height()) // 2))
