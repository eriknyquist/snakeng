import random
from dataclasses import dataclass, field
from typing import List


SLOW_SCORE_THRESHOLD = 10
MEDIUM_SCORE_THRESHOLD = 25
FAST_SCORE_THRESHOLD = 70


class SnakeDirection(object):
    """
    Enumerates all possible directions
    """
    LEFT = 0     # Left arrow
    RIGHT = 1    # Right arrow
    UP = 2       # Up arrow
    DOWN = 3     # Down arrow

class SnakeSpeed(object):
    """
    Enumerates all possible movement speeds for the snake
    """
    FASTER = 1
    FAST = 2
    MEDIUM = 3
    SLOW = 4


MOVEMAP = {
    SnakeDirection.LEFT: (-1, 0),
    SnakeDirection.RIGHT: (1, 0),
    SnakeDirection.UP: (0, 1),
    SnakeDirection.DOWN: (0, -1)
}


@dataclass
class Position(object):
    """
    Position of an object within the game area
    """
    x: int = 0
    y: int = 0

    def __hash__(self):
        return hash((self.x, self.y))

    def __eq__(self, other):
        return (self.x == other.x) and (self.y == other.y)

    def __neq__(self, other):
        return not self.__eq__(other)

    def serialize(self):
        return {'x': self.x, 'y': self.y}

    def deserialize(self, attrs):
        self.x = attrs['x']
        self.y = attrs['y']
        return self


@dataclass
class SnakeGameState(object):
    """
    Represents the state of the game for a single frame
    """
    area_width: int = 120
    area_height: int = 120
    snake_segments: List = field(default_factory=lambda: [])
    snake_direction: int = SnakeDirection.UP
    score: int = 0
    apple_position: Position = None
    dead: bool = False

    def serialize(self):
        return {
            'area_width': self.area_width,
            'area_height': self.area_height,
            'snake_segments': [x.serialize() for x in self.snake_segments],
            'snake_direction': self.snake_direction,
            'score': self.score,
            'apple_position': self.apple_position.serialize()
        }

    def deserialize(self, attrs):
        self.area_width = attrs['area_width']
        self.area_height = attrs['area_height']
        self.snake_segments = [Position().deserialize(x) for x in attrs['snake_segments']]
        self.snake_direction = attrs['snake_direction']
        self.score = attrs['score']
        self.apple_position = attrs['apple_position']
        return self

    def to_string(self, frame_corner_char='+', frame_horiz_char='-', frame_vert_char='|',
                  snake_head_left_char='<', snake_head_right_char='>', snake_head_up_char='^',
                  snake_head_down_char='v', snake_body_char='#', apple_char='@', space_char=' '):
        table = []

        # Build the outer boundary/frame
        table.append([c for c in (frame_corner_char + (frame_horiz_char * (self.area_width - 2)) + frame_corner_char)])

        for i in range(0, self.area_height - 2):
            row = [frame_vert_char]
            row.extend([space_char for x in range(self.area_width - 2)])
            row.append(frame_vert_char)
            table.append(row)

        scorestr = f"Score: {self.score:,}"
        header = frame_corner_char + (frame_horiz_char * 2) + scorestr
        remaining = self.area_width - len(header)
        header += frame_horiz_char * (remaining - 1)
        header += frame_corner_char
        table.append([c for c in header])

        # Draw the snake
        for pos in self.snake_segments[:-1]:
            table[pos.y][pos.x] = snake_body_char

        snake_head_char = '#'
        if self.snake_direction == SnakeDirection.UP:
            snake_head_char = snake_head_up_char
        elif self.snake_direction == SnakeDirection.DOWN:
            snake_head_char = snake_head_down_char
        elif self.snake_direction == SnakeDirection.LEFT:
            snake_head_char = snake_head_left_char
        elif self.snake_direction == SnakeDirection.RIGHT:
            snake_head_char = snake_head_right_char

        snakehead = self.snake_segments[-1]
        table[snakehead.y][snakehead.x] = snake_head_char

        # draw the apple
        if self.apple_position is not None:
            table[self.apple_position.y][self.apple_position.x] = apple_char

        rows = [''.join(row) for row in table]
        rows.reverse()
        return '\n'.join(rows)

    def __repr__(self):
        return self.__str__()


class SnakeGame(object):
    """
    Represents a single instance of a snake game
    """
    def __init__(self, width=40, height=30, wall_wrap=True, initial_direction=SnakeDirection.DOWN):
        self.state = SnakeGameState(area_width=width, area_height=height, snake_direction=initial_direction)
        self.state.snake_segments.append(Position(x=int(width / 2), y=int(height / 2)))
        self.state.apple_position = self._new_apple_position()
        self.wall_wrap = wall_wrap
        self.snake_ticks_per_move = SnakeSpeed.SLOW
        self.snake_move_ticks = 0
        self.queued_moves = []

    def _new_apple_position(self):
        ret = self.state.snake_segments[-1]
        while ret in self.state.snake_segments:
            xval = random.randrange(1, self.state.area_width - 2)
            yval = random.randrange(1, self.state.area_height - 2)
            ret = Position(x=xval, y=yval)

        return ret

    def _wall_collision(self, x, y):
        ret = None
        if x <= 0:
            ret = SnakeDirection.LEFT
        elif x >= (self.state.area_width - 1):
            ret = SnakeDirection.RIGHT
        elif y <= 0:
            ret = SnakeDirection.DOWN
        elif y >= (self.state.area_height - 1):
            ret = SnakeDirection.UP

        return ret

    def _new_head(self):
        if self.snake_move_ticks < self.snake_ticks_per_move:
            return None

        while self.queued_moves:
            new_direction = self.queued_moves.pop(0)
            if new_direction != self.state.snake_direction:
                self.state.snake_direction = new_direction
                break

        xadd, yadd = MOVEMAP[self.state.snake_direction]
        self.snake_move_ticks = 0
        curr_head = self.state.snake_segments[-1]
        newx = curr_head.x + xadd
        newy = curr_head.y + yadd

        collision_dir = self._wall_collision(newx, newy)
        if collision_dir is not None:
            if not self.wall_wrap:
                self.state.dead = True
            else:
                # Wrap new snake head position around to the opposite wall
                if collision_dir == SnakeDirection.LEFT:
                    newx = self.state.area_width - 2
                elif collision_dir == SnakeDirection.RIGHT:
                    newx = 1
                elif collision_dir == SnakeDirection.UP:
                    newy = 1
                elif collision_dir == SnakeDirection.DOWN:
                    newy = self.state.area_height - 2

        return Position(x=newx, y=newy)

    def _opposite_dirs(self, dir1, dir2):
        dirs = [dir1, dir2]
        if (SnakeDirection.UP in dirs) and (SnakeDirection.DOWN in dirs):
            return True
        elif (SnakeDirection.LEFT in dirs) and (SnakeDirection.RIGHT in dirs):
            return True

        return False

    def process(self, direction_input=None):
        """
        Process a single frame of the game, and return the new game state

        :param SnakeGameInput direction_input: direction key currently being pressed, if any

        :return: New game state
        :rtype: SnakeGameState
        """
        if self.state.dead:
            return

        if direction_input is not None:
            if not self._opposite_dirs(direction_input, self.state.snake_direction):
                self.queued_moves.append(direction_input)

        # Handle adding a new head segment in the current direction
        new_head = self._new_head()

        self.snake_move_ticks += 1

        if new_head is None:
            return self.state

        self.state.snake_segments.append(new_head)

        # Check if hit apple, delete apple and increment score if so
        if new_head == self.state.apple_position:
            self.state.apple_position = self._new_apple_position()
            self.state.score += 1
        else:
            self.state.snake_segments.pop(0)

        # If there are any duplicate positions in the snake segments, snake has hit itself
        if len(self.state.snake_segments) != len(set(self.state.snake_segments)):
            self.state.dead = True

        # Check if we crossed a score threshold
        if self.snake_ticks_per_move == SnakeSpeed.SLOW:
            if self.state.score >= SLOW_SCORE_THRESHOLD:
                self.snake_ticks_per_move = SnakeSpeed.MEDIUM
        elif self.snake_ticks_per_move == SnakeSpeed.MEDIUM:
            if self.state.score >= MEDIUM_SCORE_THRESHOLD:
                self.snake_ticks_per_move = SnakeSpeed.FAST
        elif self.snake_ticks_per_move == SnakeSpeed.FAST:
            if self.state.score >= FAST_SCORE_THRESHOLD:
                self.snake_ticks_per_move = SnakeSpeed.FASTER

        return self.state
