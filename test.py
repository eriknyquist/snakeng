import time
import sys

import keyboard

from snakeng.snake import SnakeGame, SnakeDirection

FPS = 15

runtime_data = {
    'last_direction': None
}


def keypress_event(e):
    ret = None

    if e.name == 'up':
        ret = SnakeDirection.UP
    elif e.name == 'down':
        ret = SnakeDirection.DOWN
    elif e.name == 'left':
        ret = SnakeDirection.LEFT
    elif e.name == 'right':
        ret = SnakeDirection.RIGHT

    runtime_data['last_direction'] = ret

def draw_screen(state):
    sys.stdout.write(chr(27) + "[2J\n")
    sys.stdout.write(str(state))
    sys.stdout.flush()


def main():
    game = SnakeGame()
    frame_delta = 1.0 / float(FPS)
    keyboard.on_press(keypress_event)

    while True:
        new_state = game.process(runtime_data['last_direction'])
        draw_screen(new_state)

        if new_state.dead:
            return

        time.sleep(frame_delta)

if __name__ == "__main__":
    main()
