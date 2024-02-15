import pygame
import random
import math
import tkinter as tk
from tkinter import messagebox
import time
from tkinter import font
from tkinter import ttk

pygame.mixer.init()
prey_move_sound = pygame.mixer.Sound("prey.wav")
kill = pygame.mixer.Sound("kill.mp3")
time_up = pygame.mixer.SoundType("time.mp3")

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
PREDATOR_SIZE = .40
CHANGE_DIRECTION_INTERVAL = 60
remaining_prey = 0

class Prey:
    def __init__(self):
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(0, SCREEN_HEIGHT)
        self.direction = random.uniform(0, 2*math.pi) 
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
        # Draw arrow indicating direction
        end_x = self.x + 10 * math.cos(self.direction)
        end_y = self.y + 10 * math.sin(self.direction)
        pygame.draw.line(screen, WHITE, (self.x, self.y), (end_x, end_y))

class Predator:
    def __init__(self):
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(0, SCREEN_HEIGHT)
        self.alive = True
        self.direction = random.uniform(0, 2*math.pi) 
        self.change_direction_counter = 0
        self.detected_prey = None  
        self.angle = 0 
        
    def move(self, prey_population):
        # Rotate the predator
        self.angle += 0.05 
        
        # Move towards lone prey if detected
        closest_prey = self.detect_lone_prey(prey_population)
        if closest_prey:
            prey_direction = math.atan2(closest_prey.y - self.y, closest_prey.x - self.x)
            self.direction = prey_direction
            
            # Increase speed when chasing prey
            self.speed = CHASE_SPEED
        else:
            # Move randomly if no prey nearby
            self.direction += random.uniform(-0.1, 0.1)
            
            # Set regular speed when not chasing prey
            self.speed = 20
        
        # Update position based on direction and speed
        self.x += self.speed * math.cos(self.direction)
        self.y += self.speed * math.sin(self.direction)
        
        # Wrap around screen edges
        self.x %= SCREEN_WIDTH
        self.y %= SCREEN_HEIGHT
    
    # Helper method to detect lone prey
    def detect_lone_prey(self, prey_population):
        closest_prey = None
        closest_distance = float('inf') 
        for prey in prey_population:
            distance = self.detect_distance(prey)
            if distance < closest_distance and self.is_lone_prey(prey, prey_population):
                closest_distance = distance
                closest_prey = prey
        return closest_prey
    
    # Helper method to check if prey is isolated (low density aggregation)
    def is_lone_prey(self, prey, prey_population):
        num_neighbors = sum(1 for other in prey_population if other != prey and self.detect_distance(other) < SIGHT_RANGE)
        return num_neighbors == 0

    def detect_distance(self, prey):
        # Calculate distance to a prey
        return math.sqrt((self.x - prey.x)**2 + (self.y - prey.y)**2)

    def die(self):
        if random.random() < PREDATOR_MORTALITY_RATE:
            self.alive = False

    def draw(self, screen):
        # Draw predator circle
        pygame.draw.circle(screen, RED, (int(self.x), int(self.y)), 7.5)
        
        # Draw circular border for catch radius
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), FLEE_DISTANCE, 2)

        # Draw arrow indicating direction
        end_x = self.x + 10 * math.cos(self.direction)
        end_y = self.y + 10 * math.sin(self.direction)
        pygame.draw.line(screen, WHITE, (self.x, self.y), (end_x, end_y))

def run_simulation(num_prey, prey_speed, num_predators, predator_speed, avoid_speed, avoid_angle, chase_speed, chase_radius):
    global remaining_prey
    global STEP_SIZE
    global REGULAR_SPEED
    global RUN_SPEED
    global AVOIDANCE_ANGLE
    global CHASE_SPEED
    global FLEE_DISTANCE

    STEP_SIZE = prey_speed
    REGULAR_SPEED = predator_speed
    RUN_SPEED = avoid_speed
    AVOIDANCE_ANGLE = avoid_angle
    CHASE_SPEED = chase_speed
    FLEE_DISTANCE = chase_radius
    
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
            time_up.play()
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

    window_width = 300 
    window_height = 100
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

    separator = ttk.Separator(input_window, orient='vertical')
    separator.grid(row=0, column=2, rowspan=5, sticky='ns', padx=20)

    tk.Label(input_window, text="Prey", font=font.Font(size=18)).grid(row=0, column=0, columnspan=2, pady=10)
    tk.Label(input_window, text="Predator", font=font.Font(size=18)).grid(row=0, column=3, columnspan=4, pady=10)
    # tk.Label(input_window, text="").grid(row=1, column=0)

    tk.Label(input_window, text="Population:", anchor="w", justify="left").grid(row=1, column=0, padx=(30,10), pady=5, sticky="w")
    entry_prey = tk.Entry(input_window, width=10)
    entry_prey.grid(row=1, column=1, padx=5, pady=5)

    tk.Label(input_window, text="Speed:", anchor="w", justify="left").grid(row=2, column=0, padx=(30,10), pady=5, sticky="w")
    entry_prey_speed = tk.Entry(input_window, width=10)
    entry_prey_speed.grid(row=2, column=1, padx=5, pady=5)
    entry_prey_speed.insert(0, "1")

    tk.Label(input_window, text="Avoid Speed:", anchor="w", justify="left").grid(row=3, column=0, padx=(30,10), pady=5, sticky="w")
    entry_prey_avoid_speed = tk.Entry(input_window, width=10)
    entry_prey_avoid_speed.grid(row=3, column=1, padx=5, pady=5)
    entry_prey_avoid_speed.insert(0, "2")

    tk.Label(input_window, text="Avoid Angle:", anchor="w", justify="left").grid(row=4, column=0, padx=(30,10), pady=5, sticky="w")
    avoid_angle = tk.Entry(input_window, width=10)
    avoid_angle.grid(row=4, column=1, padx=5, pady=5)
    avoid_angle.insert(0, "30")

    tk.Label(input_window, text="Population:", anchor="w", justify="left").grid(row=1, column=3, pady=5, sticky="w")
    entry_predators = tk.Entry(input_window, width=10)
    entry_predators.grid(row=1, column=4, padx=5, pady=5)

    tk.Label(input_window, text="Speed:", anchor="w", justify="left").grid(row=2, column=3, pady=5, sticky="w")
    entry_predator_speed = tk.Entry(input_window, width=10)
    entry_predator_speed.grid(row=2, column=4, padx=5, pady=5)
    entry_predator_speed.insert(0, "1")

    tk.Label(input_window, text="Chase Speed:", anchor="w", justify="left").grid(row=3, column=3, pady=5, sticky="w")
    entry_predator_chase_speed = tk.Entry(input_window, width=10)
    entry_predator_chase_speed.grid(row=3, column=4, padx=5, pady=5)
    entry_predator_chase_speed.insert(0, "1.1")

    tk.Label(input_window, text="Chase Radius:", anchor="w", justify="left").grid(row=4, column=3, pady=5, sticky="w")
    chase_redius = tk.Entry(input_window, width=10)
    chase_redius.grid(row=4, column=4, padx=5, pady=5)
    chase_redius.insert(0, "150")

    def submit():
        try:
            num_prey = int(entry_prey.get())
            prey_speed = float(entry_prey_speed.get())
            num_predators = int(entry_predators.get())
            predator_speed = float(entry_predator_speed.get())
            avoid_speed = float(entry_prey_avoid_speed.get())
            avoid_angles = float(avoid_angle.get())
            chase_speed = float(entry_predator_chase_speed.get())
            chase_radiuss = int(chase_redius.get())

            if num_prey <= 0:
                messagebox.showerror("Prey Error", "Number of prey must be at least 1!")
            elif prey_speed < 0:
                messagebox.showerror("Prey Speed Error", "Speed of prey must be greater than 0!")
            elif num_predators <= 0:
                messagebox.showerror("Predator Error", "Number of predators must be at least 1!")
            elif predator_speed < 0:
                messagebox.showerror("Predator Speed Error", "Speed of predators must be greater than 0!")
            elif avoid_speed < 0:
                messagebox.showerror("Prey Avoid Speed Error", "Avoid speed must greater than 0!")
            elif avoid_angles < 0:
                messagebox.showerror("Prey Avoid Angle Error", "Avoid angle must greater than 0!")
            elif chase_speed < 0:
                messagebox.showerror("Predator Chase Speed Error", "Chase Speed must greater than 0!")
            elif chase_radiuss < 0:
                messagebox.showerror("Predator Chase Radius Error", "Chase Radius must greater than 0!")
            else:
                input_window.destroy()
                run_simulation(num_prey, prey_speed, num_predators, predator_speed, avoid_speed, avoid_angles, chase_speed, chase_radiuss)
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers.")

    button_submit = tk.Button(input_window, text="Submit", command=submit)
    button_submit.grid(row=5, column=0, columnspan=4, pady=20, padx=(110, 0), sticky='ew')

    # Center the input window on the screen
    window_width = 420
    window_height = 250
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
