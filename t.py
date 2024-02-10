import pygame
import math

# Initialize Pygame
pygame.init()

# Set up the screen
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Rotating Lines")

# Define colors
RED = (255, 0, 0)

class RotatingLines:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = 0

    def update(self):
        self.angle += 0.02  # Adjust the rotation speed here

    def draw(self, screen):
        pygame.draw.circle(screen, RED, (int(self.x), int(self.y)), 7.5)
        num_lines = 8
        angle_increment = 2 * math.pi / num_lines
        for i in range(num_lines):
            angle = self.angle + i * angle_increment
            end_x = self.x + 20 * math.cos(angle)
            end_y = self.y + 20 * math.sin(angle)
            pygame.draw.line(screen, RED, (self.x, self.y), (end_x, end_y), 3)

# Main function
def main():
    clock = pygame.time.Clock()

    # Create RotatingLines object
    rotating_lines = RotatingLines(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

    # Main loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Update
        rotating_lines.update()

        # Draw
        screen.fill((255, 255, 255))  # Fill the screen with white
        rotating_lines.draw(screen)
        pygame.display.flip()

        # Cap the frame rate
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
