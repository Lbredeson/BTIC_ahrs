import pygame
import sys
import math

def draw_angle_markers(screen, center, radius, start_angle, end_angle, current_angle, draw_text=True):
    """Draw static angle markers and a moving marker for the current angle."""
    # Define angles for static markers
    angles = range(start_angle, end_angle + 1, 30)  # Adjust step for more or fewer markers

    for angle in angles:
        # Calculate marker position
        rad_angle = math.radians(angle)
        end_pos = (center[0] + radius * math.cos(rad_angle), center[1] - radius * math.sin(rad_angle))
        
        # Draw marker line
        pygame.draw.line(screen, RED, center, end_pos, 2)

        # Optionally draw angle text
        if draw_text:
            font = pygame.font.Font(None, 24)
            text = font.render(str(angle), True, RED)
            screen.blit(text, end_pos)

    # Draw moving marker for current angle
    current_rad = math.radians(current_angle)
    marker_pos = (center[0] + radius * math.cos(current_rad), center[1] - radius * math.sin(current_rad))
    pygame.draw.circle(screen, RED, marker_pos, 5)  # Moving marker

def ahrs_main():
    # Initialization code remains the same...

    while True:
        # Event handling and back buffer clearing code remains the same...

        # Define circle properties
        circle_radius = 100
        left_circle_center = (WIDTH // 4, HEIGHT // 2)  # Center for the left image (Roll)
        right_circle_center = (3 * WIDTH // 4, HEIGHT // 2)  # Center for the right image (Pitch)

        # Draw circles around the images
        pygame.draw.circle(back_buffer, RED, left_circle_center, circle_radius, 2)
        pygame.draw.circle(back_buffer, RED, right_circle_center, circle_radius, 2)

        # Draw angle markers and moving marker for roll
        draw_angle_markers(back_buffer, left_circle_center, circle_radius, -90, 90, roll_angle, draw_text=False)

        # Draw angle markers and moving marker for pitch (Inverted angle range for pitch)
        draw_angle_markers(back_buffer, right_circle_center, circle_radius, 90, -90, -pitch_angle, draw_text=False)

        # Rotate and blit the images to the back buffer remains the same...

        # Update the display and frame rate control code remains the same...

if __name__ == "__main__":
    ahrs_main()
