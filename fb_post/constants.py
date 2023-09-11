from enum import Enum


class ReactionType(Enum):
    WOW = 1
    LIT = 2
    LOVE = 3
    HAHA = 4
    THUMBS_UP = 5
    THUMBS_DOWN = 6
    ANGRY = 7
    SAD = 8

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]
