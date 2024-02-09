import pygame
import random
import math
import tkinter as tk
from tkinter import messagebox

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
SIGHT_RANGE = 10
STEP_SIZE = 1
PREDATOR_SIZE = .40
CHANGE_DIRECTION_INTERVAL = 60
remaining_prey = 0

class Prey:
    def __init__(self):
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(0, SCREEN_HEIGHT)
        self.direction = random.uniform(0, 2*math.pi)  # Random initial direction in radians
        self.alive = True

    def move(self):
        # Move the particle
        self.x += STEP_SIZE * math.cos(self.direction)
        self.y += STEP_SIZE * math.sin(self.direction)
        
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

class Predator:
    def __init__(self):
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(0, SCREEN_HEIGHT)
        self.alive = True
        self.direction = random.uniform(0, 2*math.pi)  # Random initial direction in radians
        self.change_direction_counter = 0
        self.detected_prey = None  # Keep track of detected prey

    def move_towards_prey(self, prey_population):
        for prey in prey_population:
            dx = prey.x - self.x
            dy = prey.y - self.y
            dist = (dx**2 + dy**2)**0.5
            if dist <= SIGHT_RANGE:
                self.detected_prey = prey  # Update detected prey
                self.x += MOVEMENT_SPEED * dx / dist
                self.y += MOVEMENT_SPEED * dy / dist
                self.x = max(0, min(SCREEN_WIDTH, self.x))
                self.y = max(0, min(SCREEN_HEIGHT, self.y))
                return prey
        self.detected_prey = None  # Reset detected prey if none is found
        return None

    def move(self):
        # Move the predator in a random direction
        new_x = self.x + PREDATOR_SIZE * math.cos(self.direction)
        new_y = self.y + PREDATOR_SIZE * math.sin(self.direction)
        
        # Check if the new position is outside the screen boundaries
        if new_x < 0 or new_x > SCREEN_WIDTH:
            self.direction = math.pi - self.direction  # Reflect direction horizontally
        if new_y < 0 or new_y > SCREEN_HEIGHT:
            self.direction = -self.direction  # Reflect direction vertically
        
        # Update position after potential reflection
        self.x += PREDATOR_SIZE * math.cos(self.direction)
        self.y += PREDATOR_SIZE * math.sin(self.direction)
        
        # Wrap around screen edges
        self.x %= SCREEN_WIDTH
        self.y %= SCREEN_HEIGHT

    def die(self):
        if random.random() < PREDATOR_MORTALITY_RATE:
            self.alive = False

    def draw(self, screen):
        # Draw predator circle
        if self.detected_prey:
            print("test")
            pygame.draw.circle(screen, GREEN, (int(self.x), int(self.y)), 10)  # Change color if prey detected
            self.detect_timer -= 1  # Decrement the detect timer
            if self.detect_timer <= 0:
                self.detected_prey = None  # Reset detected prey after the timer expires
        else:
            pygame.draw.circle(screen, RED, (int(self.x), int(self.y)), 10)

def run_simulation(num_prey, num_predators, predator_limit):
    global remaining_prey
    # Initialize pygame
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Predator and Prey Simulation")

    # Create prey and predator populations
    prey_population = [Prey() for _ in range(num_prey)]
    predator_population = [Predator() for _ in range(num_predators)]

    # Main loop
    clock = pygame.time.Clock()
    running = True
    time_remaining = predator_limit * 3600  # Convert hours to seconds

    # Create back button
    back_button = pygame.Rect(20, 20, 60, 35)
    font = pygame.font.Font(None, 25)
    back_text = font.render("Stop", True, WHITE)

    while running and time_remaining > 0:
        screen.fill(BLACK)
    
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if back_button.collidepoint(event.pos):  # Check if back button is clicked
                        pygame.quit()
                        return get_user_input()

        # Move prey
        for prey in prey_population:
            prey.move()
            prey.draw(screen)
            new_prey = prey.reproduce()

        # Move predators and handle interactions with prey
        for predator in predator_population:
            predator.move()  # Move the predator randomly
            predator.draw(screen)
            prey_to_remove = None
            for prey in prey_population:
                # Check for collision between predator and prey
                distance = math.sqrt((predator.x - prey.x)**2 + (predator.y - prey.y)**2)
                if distance < 10:  # Radius of predator and prey assumed to be 10
                    prey_to_remove = prey
                    predator.die()
                    remaining_prey += 1
                    break  # Exit the loop since a collision occurred
            if prey_to_remove:
                prey_population.remove(prey_to_remove)

        # Remove dead predators
        predator_population = [predator for predator in predator_population if predator.alive]

        # Display remaining prey count and time at the bottom

        remaining_prey_count = len(prey_population)
        prey_text_surface = font.render(f"Prey Remaining: {remaining_prey_count}", True, WHITE)
        prey_text_rect = prey_text_surface.get_rect(midbottom=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 20))
        screen.blit(prey_text_surface, prey_text_rect)

        remaining_time_text = f"Time Remaining: {time_remaining // 3600} minutes, {(time_remaining % 3600) // 60} seconds"
        time_text_surface = font.render(remaining_time_text, True, WHITE)
        time_text_rect = time_text_surface.get_rect(midbottom=(SCREEN_WIDTH // 2, SCREEN_HEIGHT))
        screen.blit(time_text_surface, time_text_rect)

        font = pygame.font.Font(None, 20)


        # Draw back button
        pygame.draw.rect(screen, GREEN, back_button)
        screen.blit(back_text, (back_button.x + 10, back_button.y + 10))

        # Update display
        pygame.display.flip()
        clock.tick(60)
        time_remaining -= 1

    # Quit pygame
    pygame.quit()
    if time_remaining == 0:
        results()

def results():
    global remaining_prey

    root = tk.Tk()
    root.withdraw()

    input_window = tk.Toplevel(root)
    input_window.title("Results")

    predator_kill = tk.Label(input_window, text="Predator Kill/s: ")
    predator_entry = tk.Label(input_window, text=remaining_prey)
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

    label_limit = tk.Label(input_window, text="Enter predator limit (minutes):")
    label_limit.pack()
    entry_limit = tk.Entry(input_window)
    entry_limit.pack()

    def submit():
        try:
            num_prey = int(entry_prey.get())
            num_predators = int(entry_predators.get())
            predator_limit = int(entry_limit.get())
            if num_prey <= 0:
                messagebox.showerror("Prey Error", "Number of prey must have at least 1!")
            elif num_predators <= 0:
                messagebox.showerror("Predator Error", "Number of predator must have at least 1!")
            elif predator_limit <= 0:
                messagebox.showerror("Limit Error", "Time limit must have at least 1 minute!")
            else:
                input_window.destroy()
                run_simulation(num_prey, num_predators, predator_limit)
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers.")

    button_submit = tk.Button(input_window, text="Submit", command=submit)
    button_submit.pack()

    # Center the input window on the screen
    window_width = 400  # Adjust as needed
    window_height = 200  # Adjust as needed
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
