import pygame
import math
from pygame.math import Vector2

# --- Initialization ---
pygame.init()
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Ball in a Rotating Hexagon with Gravity Slider")
clock = pygame.time.Clock()

# --- Simulation Parameters ---
# Gravity (we will adjust the y-component via the slider)
gravity_value = 500.0  # initial gravity magnitude (pixels per second^2)
gravity = Vector2(0, gravity_value)

# Air damping factor
air_damping = 0.99

# Ball parameters
ball_radius = 15
ball_pos = Vector2(width / 2, height / 2)
ball_vel = Vector2(200, -50)  # initial velocity

# Hexagon parameters
hex_center = Vector2(width / 2, height / 2)
hex_radius = 250        # distance from center to each vertex
num_sides = 6           # hexagon (6 sides)
rotation_angle = 0.0    # current rotation angle (radians)
angular_velocity = math.radians(30)  # rotation speed: 30 degrees per second

# Collision response parameters
restitution = 0.8       # bounciness (1.0 would be perfectly elastic)
wall_friction = 0.9     # friction factor (reduces tangential velocity on contact)

# --- Slider Parameters for Gravity Adjustment ---
slider_rect = pygame.Rect(50, height - 40, 300, 10)  # the slider's background bar
slider_knob_radius = 8                              # radius of the slider knob
slider_min = 0.0                                    # minimum gravity value
slider_max = 1000.0                                 # maximum gravity value
slider_value = gravity_value                        # current slider value (matches gravity_value)
dragging_slider = False

def get_slider_knob_position():
    """Map the current slider value to an (x,y) coordinate on the slider."""
    ratio = (slider_value - slider_min) / (slider_max - slider_min)
    x = slider_rect.x + ratio * slider_rect.width
    y = slider_rect.y + slider_rect.height // 2
    return (int(x), int(y))

# --- Main Loop ---
running = True
while running:
    dt = clock.tick(60) / 1000.0  # Delta time in seconds

    # --- Event Handling ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            knob_pos = get_slider_knob_position()
            # If the mouse click is close enough to the slider knob, start dragging.
            if math.hypot(mouse_pos[0] - knob_pos[0], mouse_pos[1] - knob_pos[1]) < slider_knob_radius + 2:
                dragging_slider = True

        elif event.type == pygame.MOUSEBUTTONUP:
            dragging_slider = False

        elif event.type == pygame.MOUSEMOTION:
            if dragging_slider:
                # Update slider_value based on the mouse's x position, clamped to slider boundaries.
                mouse_x = event.pos[0]
                mouse_x = max(slider_rect.x, min(slider_rect.x + slider_rect.width, mouse_x))
                ratio = (mouse_x - slider_rect.x) / slider_rect.width
                slider_value = slider_min + ratio * (slider_max - slider_min)
                gravity_value = slider_value  # update gravity magnitude
                gravity = Vector2(0, gravity_value)

    # --- Update Simulation ---
    # Update hexagon rotation.
    rotation_angle += angular_velocity * dt

    # Apply gravity and air damping to the ball.
    ball_vel += gravity * dt
    ball_vel *= air_damping
    ball_pos += ball_vel * dt

    # Compute the current hexagon vertices.
    vertices = []
    for i in range(num_sides):
        angle = rotation_angle + i * (2 * math.pi / num_sides)
        x = hex_center.x + hex_radius * math.cos(angle)
        y = hex_center.y + hex_radius * math.sin(angle)
        vertices.append(Vector2(x, y))

    # --- Collision Detection and Response ---
    # Check for collisions between the ball and each edge of the hexagon.
    for i in range(num_sides):
        A = vertices[i]
        B = vertices[(i + 1) % num_sides]
        edge = B - A

        # Find the closest point Q on segment AB to the ball's center.
        if edge.length_squared() != 0:
            t = (ball_pos - A).dot(edge) / edge.length_squared()
        else:
            t = 0
        t = max(0, min(1, t))
        Q = A + t * edge

        # Check for collision: if the distance is less than the ball's radius, we have an overlap.
        dist = (ball_pos - Q).length()
        if dist < ball_radius:
            # --- Collision Occurred ---
            penetration = ball_radius - dist

            # Compute collision normal (pointing from the wall to the ball).
            if dist != 0:
                collision_normal = (ball_pos - Q).normalize()
            else:
                # Degenerate case: choose a perpendicular to the edge.
                collision_normal = Vector2(-edge.y, edge.x).normalize()

            # Compute the wall’s velocity at point Q (due to the hexagon's rotation).
            r = Q - hex_center
            wall_vel = Vector2(-angular_velocity * r.y, angular_velocity * r.x)

            # Compute ball's relative velocity (ball velocity minus wall velocity).
            rel_vel = ball_vel - wall_vel

            # Decompose relative velocity into normal and tangential components.
            vn = rel_vel.dot(collision_normal) * collision_normal
            vt = rel_vel - vn

            # Reflect the normal component (with restitution) and apply friction to the tangential.
            vn = -restitution * vn
            vt = vt * wall_friction

            # The new relative velocity.
            new_rel_vel = vn + vt

            # Update ball velocity (convert back to world coordinates).
            ball_vel = new_rel_vel + wall_vel

            # Push the ball out of the wall so it no longer penetrates.
            ball_pos = Q + collision_normal * ball_radius

    # --- Drawing ---
    screen.fill((0, 0, 0))  # Clear screen with black.

    # Draw hexagon (outline).
    hex_points = [(v.x, v.y) for v in vertices]
    pygame.draw.polygon(screen, (0, 255, 0), hex_points, 3)

    # Draw ball (filled circle).
    pygame.draw.circle(screen, (255, 0, 0), (int(ball_pos.x), int(ball_pos.y)), ball_radius)

    # Draw slider background.
    pygame.draw.rect(screen, (100, 100, 100), slider_rect)
    # Draw slider knob.
    knob_pos = get_slider_knob_position()
    pygame.draw.circle(screen, (200, 200, 200), knob_pos, slider_knob_radius)

    # Draw a text label for the current gravity value.
    font = pygame.font.SysFont(None, 24)
    text_surface = font.render(f"Gravity: {int(gravity_value)}", True, (255, 255, 255))
    screen.blit(text_surface, (slider_rect.x, slider_rect.y - 30))

    pygame.display.flip()

pygame.quit()
