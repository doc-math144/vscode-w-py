import pygame
import numpy as np
from itertools import cycle
from config import SCREEN_WIDTH, SCREEN_HEIGHT, CUBE_COLORS, BACKGROUND_COLOR

# Initialize variables
colors = cycle(CUBE_COLORS)
cube_color = next(colors)
last_color_change = pygame.time.get_ticks()
color_change_delay = 1000  # 1 second

# Define vertices, edges, and faces
vertices = np.array([
    [-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1],
    [-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1]
], dtype=np.float32)

edges = [
    [0, 1], [1, 2], [2, 3], [3, 0],
    [4, 5], [5, 6], [6, 7], [7, 4],
    [0, 4], [1, 5], [2, 6], [3, 7]
]

faces = [
    [0, 1, 2, 3], [4, 5, 6, 7],
    [0, 1, 5, 4], [2, 3, 7, 6],
    [1, 2, 6, 5], [0, 3, 7, 4]
]

def rotate(vertices, angle_x, angle_y, angle_z):
    rotated_vertices = []
    for vertex in vertices:
        x, y, z = vertex
        
        # Rotation around X-axis
        new_y = y * np.cos(angle_x) - z * np.sin(angle_x)
        new_z = y * np.sin(angle_x) + z * np.cos(angle_x)
        y, z = new_y, new_z
        
        # Rotation around Y-axis
        new_x = x * np.cos(angle_y) + z * np.sin(angle_y)
        new_z = -x * np.sin(angle_y) + z * np.cos(angle_y)
        x, z = new_x, new_z
        
        # Rotation around Z-axis
        new_x = x * np.cos(angle_z) - y * np.sin(angle_z)
        new_y = x * np.sin(angle_z) + y * np.cos(angle_z)
        x, y = new_x, new_y
        
        rotated_vertices.append([x, y, z])
    return rotated_vertices

def project(vertex):
    SCALE = 100
    DISTANCE = 5
    x, y, z = vertex
    # Simple perspective projection
    z += 4  # Move cube away from camera
    projection_x = x * SCALE / (z + DISTANCE) + SCREEN_WIDTH // 2
    projection_y = y * SCALE / (z + DISTANCE) + SCREEN_HEIGHT // 2
    return (int(projection_x), int(projection_y))

def draw_cube(screen, angle_x, angle_y, angle_z):
    global cube_color, last_color_change
    current_time = pygame.time.get_ticks()
    
    # Clear the screen
    screen.fill(BACKGROUND_COLOR)
    
    # Rotate the cube
    rotated_vertices = rotate(vertices, angle_x, angle_y, angle_z)
    
    # Draw faces
    face_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    for face in faces:
        points = [project(rotated_vertices[vertex]) for vertex in face]
        pygame.draw.polygon(face_surface, (*cube_color, 128), points)
    screen.blit(face_surface, (0, 0))
    
    # Draw edges
    for edge in edges:
        points = [project(rotated_vertices[vertex]) for vertex in edge]
        pygame.draw.line(screen, cube_color, points[0], points[1], 2)
