import numpy as np
from pieces import PieceManager
from typing import Literal
from copy import deepcopy


def get_placement(
    place: int, shape: tuple[int, int]
) -> tuple[tuple[int, int], tuple[int, int], tuple[int, int], tuple[int, int]]:
    """
    :param place: distance of the left-top piece to the left boarder (e.g. Bishop has place 2)
    :param shape: shape of the board
    :returns: 4 position tuples mirrored on the board for piece placement first two for black, last two for white
    """

    side_length = shape[0] - 1

    pos1 = (0, place)
    pos2 = (0, side_length - place)
    pos3 = (side_length, place)
    pos4 = (side_length, side_length - place)

    return pos1, pos2, pos3, pos4


def pretty_print_array(array: np.typing.NDArray):
    for row in array:
        str_row = ""
        for cell in row:
            str_row += f"{cell} "
        print(str_row)
    print()


def get_pos_inbetween(
    pos1: tuple[int, int], pos2: tuple[int, int]
) -> list[tuple[int, int]]:
    """
    :param pos1: first position
    :param pos2: second position
    :returns: list of positions inbetween pos1 and pos2
    """
    diffy = pos1[0] - pos2[0]
    diffx = pos1[1] - pos2[1]

    if diffy > 0:
        y_values = [pos2[0] + item for item in range(1, abs(diffy))]
    elif diffy < 0:
        y_values = [pos2[0] - item for item in range(1, abs(diffy))]
    elif diffy == 0:
        y_values = [pos1[0] for item in range(1, abs(diffx))]

    if diffx > 0:
        x_values = [pos2[1] + item for item in range(1, abs(diffx))]
    elif diffx < 0:
        x_values = [pos2[1] - item for item in range(1, abs(diffx))]
    elif diffx == 0:
        x_values = [pos1[1] for item in range(1, abs(diffy))]

    return list(zip(y_values, x_values))


class GameBoard:
    def __init__(self, game_size: int, pm: PieceManager):
        self.game_size = game_size
        self.pm = pm
        self.board = np.empty(shape=(self.game_size, self.game_size), dtype=np.object_)
        self.side = self.board.shape[0] - 1
        self.setup_board()

        self.black_kill_array = np.zeros(
            shape=(self.game_size, self.game_size), dtype=int
        )
        self.white_kill_array = np.zeros(
            shape=(self.game_size, self.game_size), dtype=int
        )

    def setup_board(self):
        self.setup_high_pieces()
        self.setup_king_queen()
        self.setup_pawns()
        self.update_piece_arrays()

    def get_numbercode_array(self, piece) -> np.typing.NDArray:
        """
        Numbercode in returned array:\n
        0 = can't move there\n
        1 = can move there\n
        2 = can strike enemy there\n
        3 = move with en_passant\n
        4 = strike with en_passant\n

        :param piece: a Piece object from PieceManager Class (e.g. Tower)

        :returns: an array with numbers 0 to 4 symbolising the possible moves the piece can make
        """
        move_array = self.get_move_array(piece)
        strike_array = self.get_strike_array(piece, move_array)
        numbercode_array = self.get_en_passant_array(piece, strike_array)
        return numbercode_array

    def get_move_array(
        self, piece, array: np.typing.NDArray = None
    ) -> np.typing.NDArray:
        """
        :param piece: a Piece object from PieceManager Class (e.g. Tower)
        :param array: an array with Numbercodes, if empty a new one will be made
        :returns: an array with 1s were the piece can move
        """
        if array is None:
            array = np.zeros(shape=(self.game_size, self.game_size), dtype=int)

        move_array = array.copy()
        moves = self.cut_list_to_board(piece.possible_pos)
        for move_pos in moves:
            # loop through possible moves and get the cell at the pos
            cell = self.board[move_pos]
            if cell is None:
                free = True
                if not piece.can_jump:
                    # check if a piece is in the way
                    for pos in get_pos_inbetween(piece.cur_pos, move_pos):
                        if self.board[pos] is not None:
                            free = False
                if free:
                    move_array[move_pos] = 1

        return move_array

    def get_strike_array(
        self, piece, array: np.typing.NDArray = None
    ) -> np.typing.NDArray:
        """
        :param piece: a Piece object from PieceManager Class (e.g. Tower)
        :param array: an array with Numbercodes, if empty a new one will be made
        :returns: an array with 2s were the piece can strike an enemy
        """
        if array is None:
            array = np.zeros(shape=(self.game_size, self.game_size), dtype=int)
        strike_array = array.copy()
        strikes = self.cut_list_to_board(piece.possible_strikes)
        for strike_pos in strikes:
            cell = self.board[strike_pos]
            if cell is None:
                pass
            # check if the piece in the cell is an enemy
            elif cell.color != piece.color:
                free = True
                if not piece.can_jump:
                    # check if a piece is in the way
                    for pos in get_pos_inbetween(piece.cur_pos, strike_pos):
                        if self.board[pos] is not None:
                            free = False
                if free:
                    strike_array[strike_pos] = 2

        return strike_array

    def get_en_passant_array(
        self, piece, array: np.typing.NDArray = None
    ) -> np.typing.NDArray:
        """
        :param piece: a Piece object from PieceManager Class (e.g. Tower)
        :param array: an array with Numbercodes, if empty a new one will be made
        :returns: an array with 3 and 4s were the piece can perform an en_passant
        """
        if array is None:
            array = np.zeros(shape=(self.game_size, self.game_size), dtype=int)
        passant_array = array.copy()
        if type(piece) is PieceManager.Pawn:
            passant_dict = self.cut_dict_to_board(piece.en_passant())
            # loop through possible moves
            for move_pos, strike_pos in passant_dict.items():
                # check if en passant is possible with the move
                if passant_array[move_pos] == 0 and self.board[strike_pos] is not None:
                    if self.board[strike_pos].en_passant_possible:
                        if self.board[strike_pos].color != piece.color:
                            passant_array[move_pos] = 3
                            passant_array[strike_pos] = 4

        return passant_array

    def setup_high_pieces(self):
        """
        populates the gameboard with the selected highpieces
        """
        for piece, place in self.pm.high_pieces.items():
            positions = get_placement(place=place, shape=self.board.shape)
            for pos in positions[0:2]:
                p = piece(color="black")
                p.move_to(pos)
                self.board[pos] = p
            for pos in positions[-2:]:
                p = piece(color="white")
                p.move_to(pos)
                self.board[pos] = p

    def setup_king_queen(self):
        """
        populates the gameboard with the kings and queens
        """
        k = self.pm.King("black")
        k.move_to((0, self.pm.king_place))
        self.board[(0, self.pm.king_place)] = k

        q = self.pm.Queen("black")
        q.move_to((0, self.pm.queen_place))
        self.board[(0, self.pm.queen_place)] = q

        k = self.pm.King("white")
        k.move_to((self.side, self.pm.king_place))
        self.board[(self.side, self.pm.king_place)] = k

        q = self.pm.Queen("white")
        q.move_to((self.side, self.pm.queen_place))
        self.board[(self.side, self.pm.queen_place)] = q

    def setup_pawns(self):
        """
        populates the gameboard with the pawns
        """
        for x in range(0, self.side + 1):
            p = self.pm.Pawn("black")
            p.move_to((1, x))
            self.board[1, x] = p

        for x in range(0, self.side + 1):
            p = self.pm.Pawn("white")
            p.move_to((self.side - 1, x))
            self.board[self.side - 1, x] = p

    def update_piece_arrays(self):
        """
        updates the strike_array and the numbercode_array attribute of the pieces on the board
        """
        for row in self.board:
            for cell in row:
                if cell is not None:
                    cell.strike_array = self.get_strike_array(cell)
                    cell.numbercode_array = self.get_numbercode_array(cell)

    def update_color_kill_arrays(self):
        """
        updates the array with all possible strike positions for white and black
        """
        self.black_kill_array = np.zeros(
            shape=(self.game_size, self.game_size), dtype=int
        )
        self.white_kill_array = np.zeros(
            shape=(self.game_size, self.game_size), dtype=int
        )

        for row in self.board:
            for cell in row:
                if cell is not None:
                    strike_array = self.get_strike_array(cell)
                    passant_array = self.get_en_passant_array(cell)
                    if cell.color == "white":
                        self.white_kill_array[strike_array == 2] = 2
                        self.white_kill_array[passant_array == 4] = 2
                    elif cell.color == "black":
                        self.black_kill_array[strike_array == 2] = 2
                        self.black_kill_array[passant_array == 4] = 2

    def get_kings_pos(self) -> tuple[tuple[int, int], tuple[int, int]]:
        """
        :returns: the positions of both kings, first white then black
        """
        white_king_pos, black_king_pos = "killed", "killed"

        for row in self.board:
            for cell in row:
                if type(cell) is PieceManager.King:
                    if cell.color == "white":
                        white_king_pos = cell.cur_pos
                    elif cell.color == "black":
                        black_king_pos = cell.cur_pos

        return white_king_pos, black_king_pos

    def pretty_print_board(self):
        """
        pretty prints the current game state
        """
        for row in self.board:
            str_row = ""
            for cell in row:
                try:
                    str_row += f" {cell.sym}"
                except AttributeError:
                    str_row += f" 0"
            print(str_row)
        print()

    def move_piece(self, pos1: tuple[int, int], pos2: tuple[int, int]):
        """
        :param pos1: position of the piece that should be moved
        :param pos2: target position

        :returns: piece that got killed or None
        """
        piece = self.board[pos1]
        if type(piece) is PieceManager.Pawn:
            if not piece.moved:
                piece.possible_pos.pop(-1)
                piece.moved = True
                if abs(pos1[0] - pos2[0]) == 2:
                    piece.en_passant_possible = True

        action = piece.numbercode_array[pos2]

        target_piece = None

        if action == 2:
            target_piece = self.board[pos2]
        elif action == 3:
            match piece.color:
                case "black":
                    pos = (pos2[0] - 1, pos2[1])
                    target_piece = self.board[pos]
                case "white":
                    pos = (pos2[0] + 1, pos2[1])
                    target_piece = self.board[pos]

            self.board[pos] = None

        self.board[pos1] = None
        piece.move_to(pos2)
        self.board[pos2] = piece
        self.update_piece_arrays()
        self.update_color_kill_arrays()

        return target_piece

    def replace_pawn(self, piece, replace_with: str):
        match replace_with:
            case "T":
                new_piece = self.pm.Rook(color=piece.color)
            case "N":
                new_piece = self.pm.Knight(color=piece.color)
            case "B":
                new_piece = self.pm.Bishop(color=piece.color)
            case "Q":
                new_piece = self.pm.Queen(color=piece.color)

        new_piece.move_to(piece.cur_pos)
        self.board[piece.cur_pos] = new_piece

    def pawn_reached_end(self, pos: tuple[int, int]) -> bool:
        """
        :param pos: position of the piece
        :returns: True if the pawn piece reched the end of the board
        """
        piece = self.board[pos]
        if type(piece) is PieceManager.Pawn:
            if piece.color == "white":
                return piece.cur_pos[0] == 0
            elif piece.color == "black":
                return piece.cur_pos[0] == self.game_size - 1

    def cut_list_to_board(
        self, pos_list: list[tuple[int, int]]
    ) -> list[tuple[int, int]]:
        """
        takes a list of position tuples and cuts everything that is out of bounds
        """
        new_list = [
            (x, y)
            for x, y in pos_list
            if self.game_size - 1 >= x >= 0 and self.game_size - 1 >= y >= 0
        ]
        return new_list

    def cut_dict_to_board(
        self, pos_dict: dict[tuple[int, int], tuple[int, int]]
    ) -> dict[tuple[int, int], tuple[int, int]]:
        """
        takes a dict of position tuples and cuts everything that is out of bounds
        """
        new_dict = {
            k: v
            for k, v in pos_dict.items()
            if self.game_size - 1 >= k[0] >= 0
            and self.game_size - 1 >= k[1] >= 0
            and self.game_size - 1 >= v[0] >= 0
            and self.game_size - 1 >= v[1] >= 0
        }
        return new_dict


class Player:
    def __init__(self, color):
        self.color: Literal["black", "white"] = color
        self.lost = False


class Game:
    def __init__(self, game_size: int = 8, high_pieces: dict = None):
        self.pm = PieceManager(pieces=high_pieces)
        self.game_size = game_size
        self.board = GameBoard(self.game_size, self.pm)
        self.player_0 = Player("white")
        self.player_1 = Player("black")

        self.killed_white = []
        self.killed_black = []

        self.players = [self.player_0, self.player_1]
        self.cur_player = self.players[0]

        self.in_check = "none"

    def move_piece(self, pos1, pos2):
        killed_piece = self.board.move_piece(pos1, pos2)
        if killed_piece is not None:
            if killed_piece.color == "white":
                self.killed_white.append(killed_piece)
            elif killed_piece.color == "black":
                self.killed_black.append(killed_piece)

    def next_player(self):
        if self.cur_player.color == "white":
            self.cur_player = self.players[1]
        else:
            self.cur_player = self.players[0]

        for row in self.board.board:
            for cell in row:
                if cell is not None:
                    if cell.color == self.cur_player.color:
                        cell.en_passant_possible = False

    def test_check(self) -> Literal["both", "black", "white", "none"]:
        """
        :returns: the color of the king which is in check or none if nether is in check or both if both are in check
        """
        kings_pos = self.board.get_kings_pos()

        if kings_pos[0] == "killed" or kings_pos[1] == "killed":
            return "both"
        if (
            self.board.black_kill_array[kings_pos[0]] != 0
            and self.board.white_kill_array[kings_pos[1]] != 0
        ):
            return "both"
        if self.board.black_kill_array[kings_pos[0]] != 0:
            return "white"
        elif self.board.white_kill_array[kings_pos[1]] != 0:
            return "black"
        else:
            return "none"

    def test_checkmate(self) -> Literal["black", "white", "none"]:
        if self.in_check != "both" or self.in_check != "none":
            response = self.all_players_can_move()
            if not response[0]:
                return response[1]
            else:
                return "none"

    def test_draw(self) -> bool:
        """
        :returns: True if the game is a draw
        """
        if self.in_check == "none":
            return not self.all_players_can_move()[0]

    def game_end(self) -> bool:
        """
        :returns: True if the game ends
        """

        self.in_check = self.test_check()

        if self.test_checkmate() != "none":
            return True
        if self.test_draw():
            return True
        return False

    def get_piece_possible_moves(
        self, piece, return_type: Literal["list", "array"] = "list"
    ) -> np.typing.NDArray | list[tuple[int, int]]:
        """
        :param piece: a Piece object from PieceManager Class (e.g. Tower)
        :param return_type: specifies the return type of the func
        :returns: an array or a list with possible moves for the piece
        """
        piece_possible_array = piece.numbercode_array.copy()
        piece_possible_moves = (
            list(zip(*np.where(piece.numbercode_array == 1)))
            + list(zip(*np.where(piece.numbercode_array == 2)))
            + list(zip(*np.where(piece.numbercode_array == 3)))
        )
        piece_possible_moves = [(x.item(), y.item()) for x, y in piece_possible_moves]

        remove_list = []

        for pos in piece_possible_moves:
            game = deepcopy(self)
            piece_copy = deepcopy(piece)
            game.board.move_piece(piece_copy.cur_pos, pos)
            if game.test_check() == piece_copy.color or game.test_check() == "both":
                piece_possible_array[pos] = 0
                remove_list.append(pos)

        piece_possible_moves = [
            item for item in piece_possible_moves if item not in remove_list
        ]

        if return_type == "array":
            return piece_possible_array
        elif return_type == "list":
            return piece_possible_moves

    def all_players_can_move(self) -> tuple[bool, Literal["black", "white", "none"]]:
        """
        :returns: True and "none" if both players can move or False and the color of the player that can't move
        """
        white = False
        black = False
        for row in self.board.board:
            for cell in row:
                if cell is not None:
                    movement_list = self.get_piece_possible_moves(cell)
                    if len(movement_list) > 0:
                        if cell.color == "white":
                            white = True
                        elif cell.color == "black":
                            black = True
        if white and black:
            return True, "none"
        elif black:
            return False, "white"
        elif white:
            return False, "black"
