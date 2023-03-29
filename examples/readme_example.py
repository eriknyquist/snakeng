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
    new_state = game.process(last_direction)           # Produce new frame
    new_state_string = new_state.to_string()
    sys.stdout.write("\033[2J\n" + new_state_string)   # Clear terminal screen and print new game state
    sys.stdout.flush()                                 # Flush output
    time.sleep(0.05)
