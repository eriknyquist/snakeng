import sys
import time
import keyboard
from snakeng.snake import SnakeGame, Direction

# Maps key names from 'keyboard' lib to snakeng.Direction values
dirmap = {'up': Direction.UP, 'down': Direction.DOWN, 'left': Direction.LEFT, 'right': Direction.RIGHT}

# Create game instance
game = SnakeGame()

# Callback function to save the last arrow keypress
def keypress_event(e):
    global last_direction
    new_direction = dirmap.get(e.name, None)
    if new_direction is not None:
        game.direction_input(new_direction)

# Register callback function
keyboard.on_press(keypress_event)

while True:
    new_state = game.process()                             # Produce new frame
    sys.stdout.write("\033[2J\n" + new_state.to_string())  # Clear terminal screen and print new game state
    sys.stdout.flush()                                     # Flush output
    time.sleep(0.05)
