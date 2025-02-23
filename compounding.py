import pygame
import math
import sys

# --- Configuration ---
BOARD_SIZE = 8
WINDOW_SIZE = 800  # We'll use an 800x800 window
SQUARE_SIZE = WINDOW_SIZE // BOARD_SIZE
BACKGROUND_COLOR = (30, 30, 30)
LIGHT_COLOR = (220, 220, 220)
DARK_COLOR = (100, 100, 100)
HIGHLIGHT_COLOR = (255, 100, 100)
TEXT_COLOR = (0, 0, 0)
FPS = 1  # One square per second (adjust as desired)

# --- Utility Function ---
def format_number(n):
    """Return a formatted string: if number is huge, use scientific notation."""
    if n < 1e6:
        return str(n)
    else:
        return f"{n:.2e}"

# --- Initialize Pygame ---
pygame.init()
screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE + 100))  # Extra space for cumulative text
pygame.display.set_caption("Rice Doubling: A Compounding Animation")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 28)
big_font = pygame.font.SysFont(None, 36)

# --- Pre-calculate Grain Amounts ---
# For square i (0-indexed), grains = 2**i. The cumulative total up to square i is (2^(i+1)-1).
grain_values = [2 ** i for i in range(BOARD_SIZE * BOARD_SIZE)]
cumulative_values = [2 ** (i + 1) - 1 for i in range(BOARD_SIZE * BOARD_SIZE)]

# --- Helper Functions for Drawing ---
def draw_board(current_index):
    """Draw the chessboard with numbers. Highlight the square at current_index."""
    for idx in range(BOARD_SIZE * BOARD_SIZE):
        row = idx // BOARD_SIZE
        col = idx % BOARD_SIZE
        # Optional: For a more traditional chessboard, you can reverse the row order:
        # row = BOARD_SIZE - 1 - (idx // BOARD_SIZE)
        rect = pygame.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE + 100, SQUARE_SIZE, SQUARE_SIZE)
        # Choose color based on position
        if (row + col) % 2 == 0:
            color = LIGHT_COLOR
        else:
            color = DARK_COLOR

        # Highlight the current square (if within range)
        if idx == current_index:
            color = HIGHLIGHT_COLOR

        pygame.draw.rect(screen, color, rect)
        pygame.draw.rect(screen, (0, 0, 0), rect, 2)  # border

        # If this square has been “filled”, show the number of grains.
        if idx <= current_index:
            text = font.render(format_number(grain_values[idx]), True, TEXT_COLOR)
            text_rect = text.get_rect(center=rect.center)
            screen.blit(text, text_rect)

def draw_cumulative(current_index):
    """Display the cumulative total of grains up to the current square."""
    if current_index < 0:
        total = 0
    else:
        total = cumulative_values[current_index]
    text = big_font.render(f"Cumulative grains: {format_number(total)}", True, (255, 255, 255))
    text_rect = text.get_rect(center=(WINDOW_SIZE // 2, 50))
    screen.blit(text, text_rect)

# --- Main Animation Loop ---
current_square = -1  # Start before the first square

running = True
while running:
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Advance the animation (move to the next square)
    current_square += 1
    if current_square >= BOARD_SIZE * BOARD_SIZE:
        current_square = BOARD_SIZE * BOARD_SIZE - 1  # Stop at the last square

    # Draw background and cumulative total area.
    screen.fill(BACKGROUND_COLOR)
    draw_cumulative(current_square)
    draw_board(current_square)

    pygame.display.flip()

    # If we've filled all squares, you can either pause or restart.
    if current_square == BOARD_SIZE * BOARD_SIZE - 1:
        # Pause for a while then exit, or reset animation by uncommenting below:
        pygame.time.wait(5000)
        running = False
        # To restart: current_square = -1

pygame.quit()
sys.exit()
