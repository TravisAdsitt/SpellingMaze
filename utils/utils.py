from enum import Enum


class GridDirection(Enum):
    North = "North"
    South = "South"
    West = "West"
    East = "East"

    @classmethod
    def get_opposite_direction(cls, direction: "GridDirection") -> "GridDirection":
        if direction == cls.East:
            return cls.West
        if direction == cls.West:
            return cls.East
        if direction == cls.North:
            return cls.South
        if direction == cls.South:
            return cls.North