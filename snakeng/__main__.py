import time
import sys
import threading
import sched
import argparse

import keyboard

from snakeng.snake import SnakeGame, SnakeSpeed, SnakeDirection

scheduler = sched.scheduler(time.time, time.sleep)

runtime_data = {
    'last_direction': None,
    'paused': False,
    'scheduler_event': None
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
    elif e.name == 'p':
        runtime_data['paused'] = not runtime_data['paused']

    runtime_data['last_direction'] = ret

def draw_screen(state):
    sys.stdout.write("\033[2J\n")
    sys.stdout.write(state.to_string())
    sys.stdout.flush()


def process_frame(game, frame_time):
    runtime_data["scheduler_event"] = scheduler.enterabs(time.time() + frame_time, 0, process_frame, argument=(game, frame_time))

    if not runtime_data['paused']:
        new_state = game.process(runtime_data['last_direction'])
        draw_screen(new_state)

        if new_state.dead:
            scheduler.cancel(runtime_data["scheduler_event"])


def main():
    parser = argparse.ArgumentParser(prog='snakeng',
                                     description='Simple terminal-based snake game showing how to use snakeng to implement a game',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('-x', '--width', default=40, type=int, help='Game area width in characters')
    parser.add_argument('-y', '--height', default=30, type=int, help='Game area height in characters')
    parser.add_argument('-s', '--fixed-speed', default=None, choices=['slow', 'medium', 'fast', 'faster'],
                        help='Sets the snake speed for the whole game. If unset, the snake speed will '
                        'automatically increase as the snake size increases.')
    parser.add_argument('-f', '--fps', default=24, type=int, help='Framerate in frames per second')
    args = parser.parse_args()

    speed = None
    if args.fixed_speed is not None:
        args_speed = args.fixed_speed.lower()
        if args_speed == 'slow':
            speed = SnakeSpeed.SLOW
        elif args_speed == 'medium':
            speed = SnakeSpeed.MEDIUM
        elif args_speed == 'fast':
            speed = SnakeSpeed.FAST
        elif args_speed == 'faster':
            speed = SnakeSpeed.FASTER

    game = SnakeGame(width=args.width, height=args.height, fixed_speed=speed)
    frame_time = 1.0 / float(args.fps)
    keyboard.on_press(keypress_event)

    runtime_data["scheduler_event"] = scheduler.enterabs(time.time() + frame_time, 0, process_frame, argument=(game, frame_time))
    scheduler.run()

if __name__ == "__main__":
    main()
