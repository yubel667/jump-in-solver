import enum
import numpy as np
from typing import List

class Loc:
    def __init__(self, y, x):
        self.y = y
        self.x = x

class Orientation(enum.Enum):
    HORIZONTAL = 1
    VERTICAL = 2

class Direction(enum.Enum):
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4

# mushroom is part of setup.
class Mushroom:
    def __init__(self, loc):
        self.loc = loc

class Hole:
    def __init__(self, loc):
        self.loc = loc

def get_holes():
    # 5 fixed holes on the board.
    return [Hole(0,0), Hole(4,0), Hole(2,2), Hole(0,4), Hole(4,4)]

# Base class for game pieces.
class GamePiece:
    pass

class Rabbit(GamePiece):
    def __init__(self, loc):
        self.loc = loc

    def get_identifier():
        return f"{self.loc.y}{self.loc.x}"

class Fox(GamePiece):
    # If orientation is horizontal, takes space (y,x) and (y,x+1)
    # If orientation is vertical, takes space (y,x) and (y+1, x)
    def __init__(self, loc, orientation):
        self.loc = loc
        self.orientation = orientation

    def get_identifier():
        orientation_id = 1 if self.orientation == Orientation.HORIZONTAL else 2
        returnf f"{self.loc.y}{self.loc.x}{orientation_id}"

class BoardSetup:
    # holes never changes.
    HOLES = get_holes()
    def __init__(self, mushrooms: List[Mushrom]):
        self.mushrooms = mushrooms
        self.holes_set = set() # for O(1) lookup.
        for hole in self.HOLES:
            self.holes_set.add((hole.loc.y, hole.loc.x))

# a board state from the game.
class BoardState:
    def __init__(self, setup: BoardSetup, rabbits: List[Rabbit], foxes: List[Fox]):
        self.setup = setup
        self.rabbits = rabbits
        self.foxes = foxes

    # String identifier for DFS in the same board set up.
    def get_identifier() -> str:
        rabbit_id = "".join(sorted([r.get_identifier() for r in self.rabbits]))
        fox_id = "".join(sorted([f.get_identifier() for f in self.foxes]))
        return f"{rabbit_id},{fox_id}"

    def get_is_finished() -> bool:
        # all rabbit reached hole locations.
        for rabbit in self.rabbits:
            if (rabbit.loc.y. rabbit.loc.x) not in self.setup.holes_set:
                return False
        return True
    
    # a boolean map for all obstacles.
    def build_obstacle_map(self) -> np.array:
        obstacle_map = np.full((5,5), False)
        # mushroom, rabbit and fox takes space.
        for mushroom in self.setup.mushrooms:
            obstacle_map[mushroom.loc.y][mushroom.loc.x] = True
        for rabbit in self.rabbits:
            obstacle_map[rabbit.loc.y][rabbit.loc.x] = True
        for fox in self.foxes:
            if fox.orientation == Orientation.HORIZONTAL:
                obstacle_map[fox.loc.y][fox.loc.x] = True
                obstacle_map[fox.loc.y][fox.loc.x + 1] = True
            else:
                assert fox.orientation == Orientation.VERTICAL
                obstacle_map[fox.loc.y][fox.loc.x] = True
                obstacle_map[fox.loc.y+1][fox.loc.x] = True
        return obstacle_map

    def is_in_boundary(self, loc: Loc) -> bool:
        return loc.y >= 0 and loc.y < 5 and loc.x >= 0 and loc.x < 5

    # Return None means rabbit cannot jump to that direction.
    # Return Loc means rabbit can jump to that location.
    def get_rabbit_jump_location(self, loc: Loc, direction: Direction, obstacle_map: np.array) -> Loc | None:
        if direction == Direction.UP:
            target = Loc(loc.y - 1, loc.x)
        elif direction == Direction.LEFT:
            target = Loc(loc.y, loc.x - 1)
        elif direction == Direction.RIGHT:
            target = Loc(loc.y, loc.x + 1)
        else:
            assert direction == Direction.DOWN
            target = Loc(loc.y + 1, loc.x)
    
        if not self.is_in_boundary(target):
            return None # cannot jump out.
        if not obstacle_map[target.y, target.x]:
            return None # at least need to jump 1 space.
        # jump through obstacles.
        while obstacle_map[target.y][target.x]:
            if direction == Direction.UP:
                target.y -=1
            elif direction == Direction.DOWN:
                target.y +=1
            elif direction == Direction.LEFT:
                target.x -=1
            else:
                assert direction == Direction.RIGHT
                target.x +=1

            if not self.is_in_boundary(target):
                return None # cannot jump out.
        # land on first non-obstacle location.
        return target

    def get_fox_slide_location(self, fox: Fox, direction: Direction, obstacle_map: np.array) -> Loc | None:
        if fox.orientation == Orientation.HORIZONTAL:
            if direction == Direction.LEFT:
                target = Loc(fox.loc.y, fox.loc.x - 1)
            elif direction == Direction.RIGHT:
                # fox is 2 tile
                target = Loc(fox.loc.y, fox.loc.x + 2)
            else:
                return None # cannot move virtically
        else:
            assert fox.orientation == Orientation.VERTICAL
            if direction == Direction.UP:
                target = Loc(fox.loc.y - 1, fox.loc.x)
            elif direction == Direction.DOWN:
                # fox is 2 tile
                target = Loc(fox.loc.y + 2, fox.loc.x)
            else:
                return None # cannot move horizontally
        if not self.is_in_boundary(target):
            return None # cannot slide out.
        if obstacle_map[target.y, target.x]:
            return False # blocsked
        return True

    # Explore neighbour states for DFS.
    def get_neighbour_states(self) -> "List[BoardState]":
        neighbour_states = []
        obstacle_map = self.build_obstacle_map()
        for direction in [Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT]:
            for i, rabbit in enumerate(self.rabbits):
                jump_location = self.get_rabbit_jump_location(rabbit.loc, direction, obstacle_map)
                if jump_location is not None:
                    new_rabbits = self.rabbits[:]
                    new_rabbits[i] = Rabbit(jump_location)
                    return BoardState(self, self.setup, new_rabbits, self.foxes)
            for i, fox in enumerate(self.foxes):
                slide_location = self.get_fox_slide_location(fox, direction, obstacle_map)
                if slide_location is not None:
                    new_foxes = self.foxes[:]
                    new_foxes[i] = Fox(slide_location, fox.orientation)
                    return BoardState(self, self.setup, self.rabbits, new_foxes)
        return neighbour_states