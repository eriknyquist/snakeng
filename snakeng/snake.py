import random
from dataclasses import dataclass, field
from typing import List


SLOW_SCORE_THRESHOLD = 10
MEDIUM_SCORE_THRESHOLD = 25
FAST_SCORE_THRESHOLD = 70


class Direction(object):
    """
    Enumerates all possible directions

    :cvar int LEFT: Left movement direction
    :cvar int RIGHT: Right movement direction
    :cvar int UP: Upwards movement direction
    :cvar int DOWN: Downwards movement direction
    """
    LEFT = 0
    RIGHT = 1
    UP = 2
    DOWN = 3


class Speed(object):
    """
    Enumerates all possible movement speeds for the snake

    :cvar int FASTER: Fastest movement speed (1 segment per frame)
    :cvar int FAST: Fast movement speed (1 segment every 2 frames)
    :cvar int MEDIUM: Medium movement speed (1 segment every 3 frames)
    :cvar int SLOW: Slowest movement speed (1 segment every 4 frames)
    """
    FASTER = 1
    FAST = 2
    MEDIUM = 3
    SLOW = 4


_MOVEMAP = {
    Direction.LEFT: (-1, 0),
    Direction.RIGHT: (1, 0),
    Direction.UP: (0, 1),
    Direction.DOWN: (0, -1)
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

    def __add__(self, other):
        return Position(x=self.x + other.x, y=self.y + other.y)

    def __sub__(self, other):
        return Position(x=self.x - other.x, y=self.y - other.y)

    def serialize(self):
        return [self.x, self.y]

    def deserialize(self, attrs):
        self.x = attrs[0]
        self.y = attrs[1]
        return self


def _direction_between_points(startpos, endpos, allow_jumps=False):
    ret = None
    diff = endpos - startpos

    if (not allow_jumps) and ((abs(diff.x) > 1) or (abs(diff.y) > 1)):
        return None

    if diff.x < 0:
        ret = Direction.LEFT
    elif diff.x > 0:
        ret = Direction.RIGHT
    elif diff.y < 0:
        ret = Direction.DOWN
    elif diff.y > 0:
        ret = Direction.UP

    return ret

def _serialize_snake_positions(positions):
    """
    Compress all snake segment positions to a list of only the head, tail and corner positions
    """
    ret = []
    chunk = []
    last_pos = None
    last_direction = None

    for pos in positions:
        if last_pos is None:
            chunk.append([pos.x, pos.y])
        else:
            direction = _direction_between_points(last_pos, pos)
            if direction is None:
                # Wall wrap
                if not ((chunk[-1][0] == last_pos.x) and (chunk[-1][1] == last_pos.y)):
                    chunk.append((last_pos.x, last_pos.y))

                ret.append(chunk)
                chunk = [(pos.x, pos.y)]
                last_pos = pos
            else:
                if last_direction is not None:
                    if last_direction != direction:
                        chunk.append((last_pos.x, last_pos.y))

            last_direction = direction

        last_pos = pos

    chunk.append((positions[-1].x, positions[-1].y))
    ret.append(chunk)

    return ret

def _draw_line(startpos, endpos):
    diff = endpos - startpos
    direction = _direction_between_points(startpos, endpos, allow_jumps=True)
    move = _MOVEMAP[direction]

    ret = [startpos]
    newpos = startpos
    while newpos != endpos:
        newpos = Position(x=newpos.x + move[0], y=newpos.y + move[1])
        ret.append(newpos)

    return ret

def _deserialize_snake_positions(attrs):
    """
    Convert a serialized list of snake head, tail and corner positions, to a full
    list of snake segment positions
    """
    ret = []
    for chunk in attrs:
        for i in range(len(chunk[:-1])):
            x = chunk[i][0]
            y = chunk[i][1]
            nextx = chunk[i + 1][0]
            nexty = chunk[i + 1][1]

            newps = _draw_line(Position(x=x, y=y), Position(x=nextx, y=nexty))
            if ret and (newps[0] == ret[-1]) and (len(newps) > 2):
                newps.pop(0)

            ret.extend(newps)

    return ret


@dataclass
class SnakeGameState(object):
    """
    Represents the state of the game for a single frame.

    :ivar int area_width: Width of the game area
    :ivar int area_height: Height of the game area
    :ivar list snake_segments: List of Position objects representing the current \
        position of each segment of the snake
    :ivar int snake_direction: Current movement direction of the snake, one of \
        the constants defined by the Direction class
    :ivar int snake_speed: Current movement speed of the snake, one of \
        the constants defined by the Speed class
    :ivar fixed_speed: If True, snake speed does not change relative to snake size
    :ivar int score: Number of apples the snake has collected
    :ivar apple_position: Position object representing the current position of \
        the apple, or None if there is no apple.
    :ivar bool dead: True if the snake has died
    """
    area_width: int = 120
    area_height: int = 120
    snake_segments: List = field(default_factory=lambda: [])
    snake_direction: int = Direction.UP
    snake_speed: int = Speed.SLOW
    fixed_speed: bool = False
    score: int = 0
    apple_position: Position = None
    dead: bool = False


    def serialize(self):
        """
        Serialize the instance to a dict suitable for use with json.dump

        :return: serialized data as a dict
        :rtype: dict
        """
        return {
            'area_width': self.area_width,
            'area_height': self.area_height,
            'snake_segments': _serialize_snake_positions(self.snake_segments),
            'snake_direction': self.snake_direction,
            'score': self.score,
            'apple_position': self.apple_position.serialize(),
            'snake_speed': self.snake_speed,
            'fixed_speed': self.fixed_speed
        }

    def deserialize(self, attrs):
        """
        Load the instance with values from a serialized dict

        :param dict attrs: dict containing instance values
        """
        self.area_width = attrs['area_width']
        self.area_height = attrs['area_height']
        self.snake_segments = _deserialize_snake_positions(attrs['snake_segments'])
        self.snake_direction = attrs['snake_direction']
        self.score = attrs['score']
        self.apple_position = Position().deserialize(attrs['apple_position'])
        self.snake_speed = attrs['snake_speed']
        self.fixed_speed = attrs['fixed_speed']
        return self

    def to_string(self, frame_corner_char='+', frame_horiz_char='-', frame_vert_char='|',
                  snake_head_left_char='<', snake_head_right_char='>', snake_head_up_char='^',
                  snake_head_down_char='v', snake_body_char='#', apple_char='@', space_char=' '):
        """
        Convert the instance to an ASCII string representing the current game state

        :param str frame_corner_char: Character to use when drawing the corners of the \
            game area boundary
        :param str frame_horiz_char: Character to use when drawing the horizontal (top and bottom) \
            sides of the game area boundary
        :param str frame_horiz_char: Character to use when drawing the vertical (left and right) \
            sides of the game area boundary
        :param str snake_head_left_char: Character to use for the snake head when snake is \
            moving in the left direction
        :param str snake_head_right_char: Character to use for the snake head when snake is \
            moving in the right direction
        :param str snake_head_up_char: Character to use for the snake head when snake is \
            moving in the up direction
        :param str snake_head_down_char: Character to use for the snake head when snake is \
            moving in the down direction
        :param str snake_body_char: Character to use when drawing the snake body segments
        :param str apple_char: Character to use when drawing the apple
        :param str space_char: Character to use when drawing empty space
        """
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
        if self.snake_direction == Direction.UP:
            snake_head_char = snake_head_up_char
        elif self.snake_direction == Direction.DOWN:
            snake_head_char = snake_head_down_char
        elif self.snake_direction == Direction.LEFT:
            snake_head_char = snake_head_left_char
        elif self.snake_direction == Direction.RIGHT:
            snake_head_char = snake_head_right_char

        snakehead = self.snake_segments[-1]
        table[snakehead.y][snakehead.x] = snake_head_char

        # draw the apple
        if self.apple_position is not None:
            table[self.apple_position.y][self.apple_position.x] = apple_char

        rows = [''.join(row) for row in table]
        rows.reverse()
        return '\n'.join(rows)

    def __str__(self):
        return self.to_string()

    def __repr__(self):
        return self.__str__()


class SnakeGame(object):
    """
    Represents a single instance of a snake game
    """
    def __init__(self, width=40, height=30, wall_wrap=True, initial_direction=Direction.DOWN,
                 fixed_speed=None):
        """
        :param int width: Game area width, in units of snake body segments
        :param int height: Game area height, in units of snake body segments
        :param bool wall_wrap: If True, the snake will die when it hits a wall. If False, \
            the snake will 'teleport' through the wall and continue from the opposite wall.
        :param int initial_direction: Initial movement direction for the snake. Expected to \
            be one of the values defined under the Direction class.
        :param int fixed_speed: If unset, then the snake speed will automatically increase as \
            the snake size increases. If set to one of the values defined under the Speed \
            class, then the snake speed will be set to the specified speed for the duration of \
            the game, with no speed increases.
        """
        head_pos = Position(x=int(width / 2), y=int(height / 2))

        self.state = SnakeGameState(area_width=width, area_height=height, snake_direction=initial_direction)
        self.state.snake_segments.append(head_pos)

        self.state.apple_position = self._new_apple_position()
        self.wall_wrap = wall_wrap
        self.snake_move_ticks = 0
        self.queued_moves = []

        self.table = [[0 for _ in range(width)] for _ in range(height)]
        self.table[head_pos.y][head_pos.x] = 1

        if fixed_speed is not None:
            self.state.fixed_speed = True
            self.state.snake_speed = fixed_speed

    def deserialize(self, game_state):
        """
        Deserialize a saved game state from a dict and populate this instance with it

        :param dict game_state: saved game state to deserialize
        """
        self.state.deserialize(game_state)
        self.table = [[0 for _ in range(self.state.area_width)] for _ in range(self.state.area_height)]
        for pos in self.state.snake_segments:
            self.table[pos.y][pos.x] = 1

    def serialize(self):
        """
        Serialize the current game state to a dict suitable for json.dump

        :return: serialized game state as dict
        :rtype: dict
        """
        return self.state.serialize()

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
            ret = Direction.LEFT
        elif x >= (self.state.area_width - 1):
            ret = Direction.RIGHT
        elif y <= 0:
            ret = Direction.DOWN
        elif y >= (self.state.area_height - 1):
            ret = Direction.UP

        return ret

    def _new_head(self):
        if self.snake_move_ticks < self.state.snake_speed:
            return None

        while self.queued_moves:
            new_direction = self.queued_moves.pop(0)
            if new_direction != self.state.snake_direction:
                self.state.snake_direction = new_direction
                break

        xadd, yadd = _MOVEMAP[self.state.snake_direction]
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
                if collision_dir == Direction.LEFT:
                    newx = self.state.area_width - 2
                elif collision_dir == Direction.RIGHT:
                    newx = 1
                elif collision_dir == Direction.UP:
                    newy = 1
                elif collision_dir == Direction.DOWN:
                    newy = self.state.area_height - 2

        return Position(x=newx, y=newy)

    def _opposite_dirs(self, dir1, dir2):
        dirs = [dir1, dir2]
        if (Direction.UP in dirs) and (Direction.DOWN in dirs):
            return True
        elif (Direction.LEFT in dirs) and (Direction.RIGHT in dirs):
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

        if self.table[new_head.y][new_head.x] == 1:
            # Snake has hit itself
            self.state.dead = True

        self.state.snake_segments.append(new_head)
        self.table[new_head.y][new_head.x] = 1

        # Check if hit apple, delete apple and increment score if so
        if new_head == self.state.apple_position:
            self.state.apple_position = self._new_apple_position()
            self.state.score += 1
        else:
            tail = self.state.snake_segments.pop(0)
            self.table[tail.y][tail.x] = 0

        # Check if we crossed a score threshold
        if not self.state.fixed_speed:
            if self.state.snake_speed == Speed.SLOW:
                if self.state.score >= SLOW_SCORE_THRESHOLD:
                    self.state.snake_speed = Speed.MEDIUM
            elif self.state.snake_speed == Speed.MEDIUM:
                if self.state.score >= MEDIUM_SCORE_THRESHOLD:
                    self.state.snake_speed = Speed.FAST
            elif self.state.snake_speed == Speed.FAST:
                if self.state.score >= FAST_SCORE_THRESHOLD:
                    self.state.snake_speed = Speed.FASTER

        return self.state
