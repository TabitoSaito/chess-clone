from typing import Literal
import numpy as np


def invert_pos(pos_list):
    return [(pos[0] * (-1), pos[1] * (-1)) for pos in pos_list]


class Piece:
    def __init__(
        self,
        possible_pos: list[tuple[int, int]],
        possible_strikes: list[tuple[int, int]],
        color: Literal["white", "black"],
        can_jump=False,
    ):
        self.cur_pos: tuple[int, int] = (0, 0)
        self.color = color.lower()
        self.can_jump = can_jump
        self.en_passant_possible = False
        if self.color == "black":
            self.possible_pos: list[tuple[int, int]] = invert_pos(possible_pos)
            self.possible_strikes: list[tuple[int, int]] = invert_pos(possible_strikes)
        elif self.color == "white":
            self.possible_pos: list[tuple[int, int]] = possible_pos
            self.possible_strikes: list[tuple[int, int]] = possible_strikes
        else:
            raise ValueError("Only black or white are allowed as colores!")

        self.strike_array: np.typing.NDArray = np.zeros(shape=(0, 0), dtype=int)
        self.numbercode_array: np.typing.NDArray = np.zeros(shape=(0, 0), dtype=int)

    def move_to(self, pos: tuple[int, int]):
        x_diff = pos[0] - self.cur_pos[0]
        y_diff = pos[1] - self.cur_pos[1]

        new_possible_pos = [
            (old_pos[0] + x_diff, old_pos[1] + y_diff) for old_pos in self.possible_pos
        ]
        new_possible_strikes = [
            (old_pos[0] + x_diff, old_pos[1] + y_diff)
            for old_pos in self.possible_strikes
        ]

        self.possible_pos = new_possible_pos
        self.possible_strikes = new_possible_strikes
        self.cur_pos = pos


def drop_duplicates(old_list: list) -> list:
    return list(dict.fromkeys(old_list))


def gen_possible_pos_tower() -> list[tuple[int, int]]:
    possible_pos = []
    for i in range(-7, 8):
        horizontal = (0, i)
        vertical = (i, 0)
        possible_pos.append(horizontal)
        possible_pos.append(vertical)
    return drop_duplicates(possible_pos)


def gen_possible_pos_bishop() -> list[tuple[int, int]]:
    possible_pos = []
    for i in range(-7, 8):
        axis1 = (i, i)
        axis2 = (-i, i)
        possible_pos.append(axis1)
        possible_pos.append(axis2)
    return drop_duplicates(possible_pos)


def gen_possible_pos_knight() -> list[tuple[int, int]]:
    possible_pos = [(2, 1), (2, -1), (-2, 1), (-2, -1)]
    new_possible_pos = possible_pos.copy()
    for pos in possible_pos:
        new_possible_pos.append(pos[::-1])
    return drop_duplicates(new_possible_pos)


def gen_possible_pos_king() -> list[tuple[int, int]]:
    possible_pos = [(1, 0), (-1, 0), (1, 1), (-1, 1), (-1, -1)]
    new_possible_pos = possible_pos.copy()
    for pos in possible_pos:
        new_possible_pos.append(pos[::-1])
    return drop_duplicates(new_possible_pos)


def check_key(dictionary, key, response=None):
    try:
        value = dictionary[key]
    except KeyError:
        value = response
    return value


class PieceManager:
    def __init__(self, pieces: dict[object, int] | None = None):
        if pieces:
            self.tower_place = check_key(pieces, self.Rook)
            self.knight_place = check_key(pieces, self.Knight)
            self.bishop_place = check_key(pieces, self.Bishop)

            self.queen_place = check_key(pieces, self.Queen, 3)
            self.king_place = check_key(pieces, self.King, 4)

            self.high_pieces = {
                k: v for (k, v) in pieces.items() if k != self.King or k != self.Queen
            }
        else:
            self.tower_place = 0
            self.knight_place = 1
            self.bishop_place = 2

            self.queen_place = 3
            self.king_place = 4

            self.high_pieces = {
                self.Rook: self.tower_place,
                self.Knight: self.knight_place,
                self.Bishop: self.bishop_place,
            }

    class Rook(Piece):
        def __init__(self, color: Literal["white", "black"] = "black"):
            super().__init__(
                possible_pos=gen_possible_pos_tower(),
                possible_strikes=gen_possible_pos_tower(),
                color=color,
            )
            self.sym = "T"

    class Knight(Piece):
        def __init__(self, color: Literal["white", "black"] = "black"):
            super().__init__(
                possible_pos=gen_possible_pos_knight(),
                possible_strikes=gen_possible_pos_knight(),
                color=color,
                can_jump=True,
            )
            self.sym = "N"
            self.moved = False

    class Bishop(Piece):
        def __init__(self, color: Literal["white", "black"] = "black"):
            super().__init__(
                possible_pos=gen_possible_pos_bishop(),
                possible_strikes=gen_possible_pos_bishop(),
                color=color,
            )
            self.sym = "B"

    class Queen(Piece):
        def __init__(self, color: Literal["white", "black"] = "black"):
            super().__init__(
                possible_pos=gen_possible_pos_tower() + gen_possible_pos_bishop(),
                possible_strikes=gen_possible_pos_tower() + gen_possible_pos_bishop(),
                color=color,
            )
            self.sym = "Q"

    class King(Piece):
        def __init__(self, color: Literal["white", "black"] = "black"):
            super().__init__(
                possible_pos=gen_possible_pos_king(),
                possible_strikes=gen_possible_pos_king(),
                color=color,
            )
            self.sym = "K"
            self.moved = False

    class Pawn(Piece):
        def __init__(self, color: Literal["white", "black"] = "black"):
            super().__init__(
                possible_pos=[(-1, 0), (-2, 0)],
                possible_strikes=[(-1, 1), (-1, -1)],
                color=color,
            )
            self.sym = "P"
            self.moved = False

        def en_passant(self) -> dict[tuple[int, int], tuple[int, int]]:
            """returns a dict containing the pos were the pawn would move as key
            and the pos the pawn would strike as value"""
            if self.color == "white":
                pos_dict = {
                    self.possible_strikes[0]: (self.cur_pos[0], self.cur_pos[1] + 1),
                    self.possible_strikes[1]: (self.cur_pos[0], self.cur_pos[1] - 1),
                }
            else:
                pos_dict = {
                    self.possible_strikes[0]: (self.cur_pos[0], self.cur_pos[1] - 1),
                    self.possible_strikes[1]: (self.cur_pos[0], self.cur_pos[1] + 1),
                }

            return pos_dict
