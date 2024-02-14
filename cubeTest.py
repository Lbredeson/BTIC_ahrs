import pygame
import sys
import math

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 640, 480
CENTER = (WIDTH // 2, HEIGHT // 2)
WHITE = (255, 255, 255)
RED = (255, 0, 0)

def draw_cube(screen, roll, pitch):
    screen.fill(WHITE)
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

    pygame.display.flip()

def main():
    # Pygame initialization
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Cube Visualization')

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Example rotation values (you can replace these with your roll and pitch values)
        roll = math.radians(30)
        pitch = math.radians(20)

        draw_cube(screen, roll, pitch)

        # Control the speed of the visualization
        pygame.time.Clock().tick(60)

if __name__ == "__main__":
    main()
