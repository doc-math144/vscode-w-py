import pygame
from graphics import cube_color, colors, last_color_change, color_change_delay

# Global variables for rotation angles
angle_x = 0
angle_y = 0 
angle_z = 0

def handle_input():
    global angle_x, angle_y, angle_z, cube_color, last_color_change
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False  # Exit the game loop
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                current_time = pygame.time.get_ticks()
                if current_time - last_color_change > color_change_delay:
                    cube_color = next(colors)
                    last_color_change = current_time
    
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        angle_y -= 0.05
    if keys[pygame.K_RIGHT]:
        angle_y += 0.05
    if keys[pygame.K_UP]:
        angle_x -= 0.05
    if keys[pygame.K_DOWN]:
        angle_x += 0.05
    if keys[pygame.K_a]:
        angle_z -= 0.05
    if keys[pygame.K_d]:
        angle_z += 0.05
    
    return angle_x, angle_y, angle_z
