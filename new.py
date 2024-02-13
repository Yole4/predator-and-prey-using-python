import pygame
import random
import math
import tkinter as tk
from tkinter import messagebox
import time

pygame.mixer.init()
prey_move_sound = pygame.mixer.Sound("prey.wav")
audio_time = pygame.mixer.Sound("time.mp3")
kill = pygame.mixer.Sound("kill.mp3")

# Set screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Define colors
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLACK = (0, 0, 0)

# Set parameters for prey and predators
PREY_REPRODUCTION_RATE = 0.01
PREDATOR_REPRODUCTION_RATE = 0.01
PREDATOR_MORTALITY_RATE = 0
MOVEMENT_SPEED = 5
SIGHT_RANGE = 25
STEP_SIZE = 1
PREDATOR_SIZE = .40
CHANGE_DIRECTION_INTERVAL = 60
remaining_prey = 0
FLEE_DISTANCE = 150
RUN_SPEED = 2
AVOIDANCE_ANGLE = 30
REGULAR_SPEED = 1.0 
CHASE_SPEED = 1.0

class Prey:
    def __init__(self):
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(0, SCREEN_HEIGHT)
        self.direction = random.uniform(0, 2*math.pi)  # Random initial direction in radians
        self.alive = True
        
    def move(self, predators):
        speed = STEP_SIZE

        # Check if prey is being chased by any predator
        for predator in predators:
            distance = math.sqrt((self.x - predator.x)**2 + (self.y - predator.y)**2)
            if distance < FLEE_DISTANCE:
                # Calculate angle away from predator
                away_angle = math.atan2(self.y - predator.y, self.x - predator.x)
                self.direction = away_angle + AVOIDANCE_ANGLE
                # Increase movement speed
                speed = RUN_SPEED
                break

        # Move the prey
        self.x += speed * math.cos(self.direction)
        self.y += speed * math.sin(self.direction)
        
        # Wrap around screen edges
        self.x %= SCREEN_WIDTH
        self.y %= SCREEN_HEIGHT

    def collide(self, other):
        # Check if this particle collides with another
        distance = math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)
        if distance < 10:  # Radius of particles assumed to be 5
            # Calculate collision angle
            collision_angle = math.atan2(other.y - self.y, other.x - self.x)
            
            # Reflect directions
            self.direction = 2 * collision_angle - self.direction
            other.direction = 2 * collision_angle - other.direction

    def reproduce(self):
        if random.random() < PREY_REPRODUCTION_RATE:
            return Prey()
        else:
            return None

    def draw(self, screen):
        pygame.draw.circle(screen, GREEN, (int(self.x), int(self.y)), 5)
        # pygame.draw.polygon(screen, GREEN, [(self.x, self.y - 10), (self.x + 5, self.y + 5), (self.x - 5, self.y + 5)])

class Predator:
    def __init__(self):
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(0, SCREEN_HEIGHT)
        self.alive = True
        self.direction = random.uniform(0, 2*math.pi)  # Random initial direction in radians
        self.change_direction_counter = 0
        self.detected_prey = None  # Keep track of detected prey
        self.angle = 0  # Initial angle for rotation
        
    def move(self, prey_population):
        # Rotate the predator
        self.angle += 0.05  # Increment angle for rotation
        
        # Move towards prey if detected
        closest_prey = self.detect_prey(prey_population)
        if closest_prey and self.detect_distance(closest_prey) < 100:
            prey_direction = math.atan2(closest_prey.y - self.y, closest_prey.x - self.x)
            self.direction = prey_direction
            
            # Increase speed when chasing prey
            self.speed = CHASE_SPEED
        else:
            # Move randomly if no prey nearby
            self.direction += random.uniform(-0.1, 0.1)
            
            # Set regular speed when not chasing prey
            self.speed = REGULAR_SPEED
        
        # Update position based on direction and speed
        self.x += self.speed * math.cos(self.direction)
        self.y += self.speed * math.sin(self.direction)
        
        # Wrap around screen edges
        self.x %= SCREEN_WIDTH
        self.y %= SCREEN_HEIGHT
    
    def detect_prey(self, prey_population):
        # Find the closest prey
        closest_prey = None
        closest_distance = float('inf') 
        for prey in prey_population:
            distance = self.detect_distance(prey)
            if distance < closest_distance:
                closest_distance = distance
                closest_prey = prey
        return closest_prey
    
    def detect_distance(self, prey):
        # Calculate distance to a prey
        return math.sqrt((self.x - prey.x)**2 + (self.y - prey.y)**2)

    def die(self):
        if random.random() < PREDATOR_MORTALITY_RATE:
            self.alive = False

    def draw(self, screen):
        # Draw predator circle
        if self.detected_prey:
            pygame.draw.circle(screen, GREEN, (int(self.x), int(self.y)), 10) 
            self.detect_timer -= 1  
            if self.detect_timer <= 0:
                self.detected_prey = None 
        else:
            pygame.draw.circle(screen, RED, (int(self.x), int(self.y)), 7.5)
        
            num_lines = 8 
            angle_increment = 2 * math.pi / num_lines
            for i in range(num_lines):
                angle = self.angle + i * angle_increment 
                end_x = self.x + 20 * math.cos(angle)
                end_y = self.y + 20 * math.sin(angle)
                pygame.draw.line(screen, RED, (self.x, self.y), (end_x, end_y), 3)

def run_simulation(num_prey, num_predators):
    global remaining_prey
    
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Predator and Prey Simulation")

    # Create prey and predator populations
    prey_population = [Prey() for _ in range(num_prey)]
    predator_population = [Predator() for _ in range(num_predators)]

    # Main loop
    clock = pygame.time.Clock()
    running = True

    # Stopwatch variables
    start_time = time.time()
    stopwatch_font = pygame.font.Font(None, 25)

    # Create back button
    back_button = pygame.Rect(20, 20, 60, 35)
    font = pygame.font.Font(None, 25)
    back_text = font.render("Stop", True, WHITE)

    while running:
        screen.fill(BLACK)

        start = time.time()

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if back_button.collidepoint(event.pos): 
                        pygame.quit()
                        return get_user_input()

        # Move prey
        for prey in prey_population:
            prey.move(predator_population)  
            prey.draw(screen)
            new_prey = prey.reproduce()

        # Move predators and handle interactions with prey
        for predator in predator_population:
            predator.move(prey_population)  
            predator.draw(screen)
            prey_to_remove = None
            for prey in prey_population:
                # Check for collision between predator and prey
                distance = math.sqrt((predator.x - prey.x)**2 + (predator.y - prey.y)**2)
                if distance < SIGHT_RANGE:  # Radius of predator and prey assumed to be 10
                    prey_to_remove = prey
                    predator.die()
                    remaining_prey += 1
                    # prey_move_sound.stop()
                    kill.play()
                    break 
            if prey_to_remove:
                prey_population.remove(prey_to_remove)

        # Remove dead predators
        predator_population = [predator for predator in predator_population if predator.alive]

        # Display remaining prey count and time at the bottom
        remaining_prey_count = len(prey_population)

        time_text_surface = font.render(f"Prey Remaining: {remaining_prey_count}", True, WHITE)
        time_text_rect = time_text_surface.get_rect(midbottom=(SCREEN_WIDTH // 2, SCREEN_HEIGHT))
        screen.blit(time_text_surface, time_text_rect)

        # Draw back button
        pygame.draw.rect(screen, GREEN, back_button)
        screen.blit(back_text, (back_button.x + 10, back_button.y + 10))

        # Stopwatch
        elapsed_time = time.time() - start_time
        minutes = int(elapsed_time // 60)
        seconds = int(elapsed_time % 60)
        stopwatch_text = f"{minutes:02d}:{seconds:02d}"
        stopwatch_surface = stopwatch_font.render(stopwatch_text, True, WHITE)
        stopwatch_rect = stopwatch_surface.get_rect(topright=(SCREEN_WIDTH - 20, 20))
        screen.blit(stopwatch_surface, stopwatch_rect)

        if remaining_prey_count == 0:
            pygame.quit()
            results(stopwatch_text)

        # Update display
        pygame.display.flip()
        clock.tick(60)

    # Quit pygame
    pygame.quit()

def results(stopwatch_text):

    root = tk.Tk()
    root.withdraw()

    input_window = tk.Toplevel(root)
    input_window.title("Results")

    predator_kill = tk.Label(input_window, text="Execution Time: ")
    predator_entry = tk.Label(input_window, text=stopwatch_text)
    predator_kill.pack()
    predator_entry.pack()

    okay_button = tk.Button(input_window, text="Play Again", command=lambda: [input_window.destroy(), get_user_input()])
    okay_button.pack()

    window_width = 300  # Adjust as needed
    window_height = 100  # Adjust as needed
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    input_window.geometry(f"{window_width}x{window_height}+{x}+{y}")

    input_window.mainloop()

def get_user_input():
    root = tk.Tk()
    root.withdraw()

    input_window = tk.Toplevel(root)
    input_window.title("Predator and Prey")

    # welcome = tk.Label(input_window, text="Predator and Prey", font=("Arial", 15), padx=10, pady=5)
    # welcome.pack()

    label_prey = tk.Label(input_window, text="Enter number of prey:")
    label_prey.pack()
    entry_prey = tk.Entry(input_window)
    entry_prey.pack()

    label_predators = tk.Label(input_window, text="Enter number of predators:")
    label_predators.pack()
    entry_predators = tk.Entry(input_window)
    entry_predators.pack()

    def submit():
        try:
            num_prey = int(entry_prey.get())
            num_predators = int(entry_predators.get())
            if num_prey <= 0:
                messagebox.showerror("Prey Error", "Number of prey must have at least 1!")
            elif num_predators <= 0:
                messagebox.showerror("Predator Error", "Number of predator must have at least 1!")
            else:
                input_window.destroy()
                run_simulation(num_prey, num_predators)
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers.")

    button_submit = tk.Button(input_window, text="Submit", command=submit)
    button_submit.pack()

    # Center the input window on the screen
    window_width = 350  # Adjust as needed
    window_height = 150  # Adjust as needed
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    input_window.geometry(f"{window_width}x{window_height}+{x}+{y}")

    input_window.mainloop()


def main():
    get_user_input()

if __name__ == "__main__":
    main()
