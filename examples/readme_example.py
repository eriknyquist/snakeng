import sys
import time
import keyboard
from snakeng.snake import SnakeGame, SnakeDirection

last_direction = SnakeDirection.DOWN

# Callback function to save the last arrow keypress
def keypress_event(e):
    global last_direction
    if e.name == 'up':
        last_direction = SnakeDirection.UP
    elif e.name == 'down':
        last_direction = SnakeDirection.DOWN
    elif e.name == 'left':
        last_direction = SnakeDirection.LEFT
    elif e.name == 'right':
        last_direction = SnakeDirection.RIGHT

# Register callback function
keyboard.on_press(keypress_event)

game = SnakeGame()

while True:
    new_state = game.process(last_direction)  # Produce new frame
    sys.stdout.write("\033[2J\n")             # Clear terminal screen
    sys.stdout.write(new_state.to_string())   # Print new game state
    sys.stdout.flush()                        # Flush output
    time.sleep(0.05)
