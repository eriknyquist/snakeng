import time
import sys
import threading
import sched
import json
import argparse

import keyboard

from snakeng.snake import SnakeGame, Speed, Direction

scheduler = sched.scheduler(time.time, time.sleep)

runtime_data = {
    'paused': False,
    'scheduler_event': None
}

dirmap = {'up': Direction.UP, 'down': Direction.DOWN, 'left': Direction.LEFT, 'right': Direction.RIGHT}
speedmap = {'slow': Speed.SLOW, 'medium': Speed.MEDIUM, 'fast': Speed.FAST, 'faster': Speed.FASTER}


def process_frame(game, frame_time):
    runtime_data["scheduler_event"] = scheduler.enterabs(time.time() + frame_time, 0, process_frame, argument=(game, frame_time))

    if not runtime_data['paused']:
        new_state = game.process()
        new_state_string = new_state.to_string()
        sys.stdout.write("\033[2J\n" + new_state_string)
        sys.stdout.flush()

        if new_state.dead:
            scheduler.cancel(runtime_data["scheduler_event"])


def main():
    parser = argparse.ArgumentParser(prog='snakeng',
                                     description="Simple terminal-based snake game showing how "
                                     "to use snakeng. Use arrow keys to change snake direction, "
                                     "use 'p' to pause, and use 'Ctrl-C' to quit.",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('-x', '--width', default=40, type=int, help='Game area width in characters.')
    parser.add_argument('-y', '--height', default=30, type=int, help='Game area height in characters.')
    parser.add_argument('-f', '--fps', default=24, type=int, help='Framerate in frames per second.')
    parser.add_argument('-s', '--fixed-speed', default=None, choices=['slow', 'medium', 'fast', 'faster'],
                        help='Sets the snake speed for the whole game. If unset, the snake speed will '
                        'automatically increase as the snake size increases.')
    parser.add_argument('-w', '--wall-death', default=False, action='store_true', help='If True, snake '
                        'will die if it hits a wall. Default behaviour is to "wrap around" and come out of '
                        'the opposite wall.')
    parser.add_argument('-o', '--output-file', default=None, type=str, help='If set, the game state will be'
                        ' saved to the specified filename when you quit with Ctrl-C.')
    parser.add_argument('-i', '--input-file', default=None, type=str, help='If set, the game state will be'
                        ' loaded from the specified filename.')
    parser.add_argument('-p', '--permanent-apples', default=False, action='store_true', help='If True, apples '
                        'will stay forever until collected. Default is to disappear after a fixed number of '
                        'frames.')
    parser.add_argument('-a', '--apple-ticks', default=None, type=int, help='Specifies the number of frames '
                        'before an uncollected apple disappears. Can only be used if -p is not set. Default is '
                        'to use the width or height of the game area, whichever is larger.')
    args = parser.parse_args()

    if args.permanent_apples and (args.apple_ticks is not None):
        print("Error: -a/--apple-ticks can not be used if -p/--permanent-apples is set")
        return

    speed = None
    if args.fixed_speed is not None:
        args_speed = args.fixed_speed.lower()
        speed = speedmap.get(args_speed)

    game = SnakeGame(width=args.width, height=args.height, fixed_speed=speed, wall_wrap=not args.wall_death,
                     apples_disappear=not args.permanent_apples, apple_disappear_ticks=args.apple_ticks)

    if args.input_file is not None:
        with open(args.input_file, 'r') as fh:
            game.deserialize(json.load(fh))

    frame_time = 1.0 / float(args.fps)

    def keypress_event(e):
        newdir = dirmap.get(e.name, None)
        if newdir is None:
            if e.name == 'p':
                runtime_data['paused'] = not runtime_data['paused']
        else:
            game.direction_input(newdir)

    keyboard.on_press(keypress_event)

    try:
        process_frame(game, frame_time)
        scheduler.run()
    except KeyboardInterrupt:
        if args.output_file:
            with open(args.output_file, 'w') as fh:
                json.dump(game.serialize(), fh)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        pass
