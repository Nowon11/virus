import pygame
import sys
import math

pygame.init()

WIDTH, HEIGHT = 1000, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Driving Game")

WHITE   = (255, 255, 255)
BLUE    = (0, 0, 255)
RED     = (255, 0, 0)
GREEN   = (0, 255, 0)
BLACK   = (0, 0, 0)
YELLOW  = (255, 255, 0)

clock = pygame.time.Clock()

# Car properties
car_width, car_height = 20, 40
start_x, start_y = WIDTH // 12, HEIGHT // 12  # Start position
car_x, car_y = start_x, start_y
car_angle = 180

# Movement parameters
velocity = 0
acceleration_rate = 0.2
reverse_acceleration_rate = 0.1
max_speed = 5.5
max_reverse_speed = -2
friction = 0.15

# Walls (red) – create surfaces with per-pixel alpha
wall_surfaces = []
wall_rects = []
walls_data = [
    # bottom
    (0, 0, 10, 800),
    (0, 300, 200, 10),
    (200, 300, 10, 200),
    (200, 500, 400, 10),
    (600, 160, 10, 350),
    (600, 160, 250, 10),
    (600, 500, 250, 10),
    # top
    (0, 0, 1000, 10),
    (750, 340, 250, 10),
    (150, 0, 10, 180),
    (150, 180, 180, 10),
    (320, 180, 10, 200),
    (320, 380, 150, 10),
    (470, 0, 10, 390),
    (100, 640, 900, 10),
    (100, 465, 10, 175),
    (0, 790, 1000, 10),
    (1000, 650, 10, 500),
    (990, 0, 10, 650),
]
for data in walls_data:
    wall_surf = pygame.Surface((data[2], data[3]), pygame.SRCALPHA)
    wall_surf.fill(RED)  # fully opaque red
    wall_surfaces.append(wall_surf)
    wall_rects.append(pygame.Rect(data[0], data[1], data[2], data[3]))

# Create a world surface and mask for raycasting (only walls)
# Use SRCALPHA and fill with transparent (0 alpha)
world_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
world_surf.fill((0, 0, 0, 0))
for wall_surf, wall_rect in zip(wall_surfaces, wall_rects):
    world_surf.blit(wall_surf, wall_rect.topleft)
world_mask = pygame.mask.from_surface(world_surf)

# End zone (green) - defined separately so it doesn't act like a wall
end_surfaces = []
end_rects = []
end_data = [
    (925, 650, 75, 140),  # finish area
]
for data in end_data:
    end_surf = pygame.Surface((data[2], data[3]), pygame.SRCALPHA)
    end_surf.fill(GREEN)
    end_surfaces.append(end_surf)
    end_rects.append(pygame.Rect(data[0], data[1], data[2], data[3]))

# Timer and countdown variables
font = pygame.font.SysFont(None, 36)         # for on-screen timer
countdown_font = pygame.font.SysFont(None, 72) # for the big countdown
start_time = 0.0         # when the timer starts
final_time = None        # final time when finished
timer_running = False    # is the timer actively counting?
in_countdown = True      # start with a 3-sec countdown
countdown_value = 3      # countdown starts at 3
countdown_last_tick = 0  # to track countdown timing

def rotate_car(angle, x, y):
    """Create a rotated surface for the car and return (surface, rect)."""
    car_surf = pygame.Surface((car_width, car_height), pygame.SRCALPHA)
    pygame.draw.rect(car_surf, BLUE, (0, 0, car_width, car_height))
    rotated_surf = pygame.transform.rotate(car_surf, angle)
    rotated_rect = rotated_surf.get_rect(center=(x, y))
    return rotated_surf, rotated_rect

def reset_game():
    """Reset car to start and begin the 3-second countdown."""
    global car_x, car_y, car_angle, velocity
    global in_countdown, countdown_value, countdown_last_tick
    global timer_running, final_time

    # Reset car
    car_x, car_y = start_x, start_y
    car_angle = 180
    velocity = 0

    # Reset timer and finish info
    final_time = None
    timer_running = False

    # Start countdown
    in_countdown = True
    countdown_value = 3
    countdown_last_tick = pygame.time.get_ticks()

def cast_ray(mask, start_x, start_y, angle_degrees, max_distance=600):
    """
    Cast a ray from (start_x, start_y) in the specified angle (degrees).
    Returns the distance (in pixels) to the first wall found or max_distance.
    """
    rad = math.radians(angle_degrees)
    for dist in range(max_distance):
        test_x = int(start_x + dist * -math.sin(rad))
        test_y = int(start_y + dist * -math.cos(rad))
        if test_x < 0 or test_x >= WIDTH or test_y < 0 or test_y >= HEIGHT:
            return dist
        if mask.get_at((test_x, test_y)) == 1:
            return dist
    return max_distance

running = True
# Immediately reset to initialize the game state
reset_game()

while running:
    # 1) Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Press R to reset
    keys = pygame.key.get_pressed()
    if keys[pygame.K_r]:
        reset_game()

    # 2) Store previous position and angle
    prev_x, prev_y = car_x, car_y
    prev_angle = car_angle

    # 3) Process input (only if not in countdown)
    if not in_countdown:
        if keys[pygame.K_LEFT]:
            car_angle += 3
        if keys[pygame.K_RIGHT]:
            car_angle -= 3

        if keys[pygame.K_UP]:
            velocity = min(velocity + acceleration_rate, max_speed)
        elif keys[pygame.K_DOWN]:
            if velocity > 0:
                velocity = max(velocity - acceleration_rate, 0)
            else:
                velocity = max(velocity - reverse_acceleration_rate, max_reverse_speed)
        else:
            if velocity > 0:
                velocity = max(velocity - friction, 0)
            elif velocity < 0:
                velocity = min(velocity + friction, 0)

    # 4) Move the car (if not in countdown)
    if not in_countdown:
        rad = math.radians(car_angle)
        dx = -math.sin(rad) * velocity
        dy = -math.cos(rad) * velocity
        car_x += dx
        car_y += dy

    # 5) Check collision with walls
    rotated_car, car_rect = rotate_car(car_angle, car_x, car_y)
    car_mask = pygame.mask.from_surface(rotated_car)
    collision = False
    for wall_surf, wall_rect in zip(wall_surfaces, wall_rects):
        wall_mask = pygame.mask.from_surface(wall_surf)
        offset = (wall_rect.left - car_rect.left, wall_rect.top - car_rect.top)
        if car_mask.overlap(wall_mask, offset):
            collision = True
            break

    if collision:
        # Revert to previous position and angle if collision occurs
        car_x, car_y = prev_x, prev_y
        car_angle = prev_angle
        velocity = 0

    # Check overlap with end zone (if timer is running and we haven't finished yet)
    if timer_running and final_time is None:
        for end_surf, end_rect in zip(end_surfaces, end_rects):
            end_mask = pygame.mask.from_surface(end_surf)
            offset = (end_rect.left - car_rect.left, end_rect.top - car_rect.top)
            if car_mask.overlap(end_mask, offset):
                # Car has reached the finish area
                final_time = (pygame.time.get_ticks() - start_time) / 1000.0
                timer_running = False
                break

    # 6) Handle countdown logic
    if in_countdown:
        current_ticks = pygame.time.get_ticks()
        if current_ticks - countdown_last_tick >= 1000:
            countdown_value -= 1
            countdown_last_tick += 1000
            if countdown_value <= 0:
                in_countdown = False
                timer_running = True
                start_time = pygame.time.get_ticks()

    # 7) Cast 5 rays from the car to detect walls
    ray_offsets = [-30, -15, 0, 15, 30]
    ray_distances = []
    for offset in ray_offsets:
        ray_angle = car_angle + offset
        dist = cast_ray(world_mask, car_x, car_y, ray_angle, max_distance=10000)
        ray_distances.append(dist)
    print(ray_distances)  # Debug output

    # 8) Draw everything
    screen.fill(WHITE)

    # Draw walls
    for wall_surf, wall_rect in zip(wall_surfaces, wall_rects):
        screen.blit(wall_surf, wall_rect.topleft)

    # Draw end zone
    for end_surf, end_rect in zip(end_surfaces, end_rects):
        screen.blit(end_surf, end_rect.topleft)

    # Draw the car
    rotated_car, car_rect = rotate_car(car_angle, car_x, car_y)
    screen.blit(rotated_car, car_rect.topleft)

    # Draw sensor rays in yellow
    for offset, dist in zip(ray_offsets, ray_distances):
        r_angle = math.radians(car_angle + offset)
        end_x = car_x + dist * -math.sin(r_angle)
        end_y = car_y + dist * -math.cos(r_angle)
        pygame.draw.line(screen, YELLOW, (car_x, car_y), (end_x, end_y), 2)

    # Display the timer
    if final_time is not None:
        time_text = f"Time: {final_time:.2f}s"
    else:
        if timer_running:
            elapsed = (pygame.time.get_ticks() - start_time) / 1000.0
            time_text = f"Time: {elapsed:.2f}s"
        else:
            time_text = "Time: 0.00s"
    timer_surf = font.render(time_text, True, BLACK)
    screen.blit(timer_surf, (10, 10))

    # Display countdown if active
    if in_countdown:
        cd_text = str(countdown_value)
        countdown_surf = countdown_font.render(cd_text, True, BLACK)
        cd_rect = countdown_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(countdown_surf, cd_rect)

    # Display the speed in the bottom left corner
    speed_text = f"Speed: {abs(velocity):.2f}"
    speed_surf = font.render(speed_text, True, BLACK)
    screen.blit(speed_surf, (10, HEIGHT - 40))

    pygame.display.flip()
    clock.tick(60)