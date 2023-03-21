import time
import sys

import keyboard

from snakeng.snake import SnakeGame, SnakeDirection

FPS = 15

runtime_data = {
    'last_direction': None
}


def frame_to_string(state):
    table = []

    # Build the outer boundary/frame
    table.append(('+' + ('-' * (state.area_width - 2)) + '+').split())

    for i in range(1, state.area_height - 2):
        row = ['|']
        row.extend([' ' for x in range(state.area_width - 2)])
        row.append('|')
        table.append(row)

    scorestr = f"Score: {state.score:,}"
    header = '+--' + scorestr
    remaining = state.area_width - len(header)
    header += "-" * (remaining - 1)
    header += "+"
    table.append([c for c in header])

    # Draw the snake
    for pos in state.snake_segments:
        table[pos.y][pos.x] = '#'

    # draw the apple
    if state.apple_position is not None:
        table[state.apple_position.y][state.apple_position.x] = '*'

    rows = [''.join(row) for row in table]
    rows.reverse()
    return '\n'.join(rows)

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
    sys.stdout.write(frame_to_string(state))
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
