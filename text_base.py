from game import Game
from pieces import PieceManager

HIGH_PIECES = {
    PieceManager.Rook: 0,
    PieceManager.Knight: 1,
    PieceManager.Bishop: 2,
}

game = Game()

while not game.game_end():
    print(game.killed_black)
    print(game.killed_white)
    valid = False
    while not valid:
        game.board.pretty_print_board()
        row = input("Select row: ")
        col = input("Select colum: ")
        piece = game.board.board[int(row), int(col)]
        if piece is not None:
            if piece.color == game.cur_player.color:
                moves = game.get_piece_possible_moves(piece)
                if len(moves) > 0:
                    print(f"Possible moves: {moves}")
                    new_row = input("Move to row: ")
                    new_col = input("Move to colum: ")
                    game.move_piece(piece.cur_pos, (int(new_row), int(new_col)))
                    valid = True
                else:
                    print("no possible moves")
            else:
                print("That is not your piece")
        else:
            print("No piece in this cell")
    match game.test_check():
        case "black":
            print("balck king is in check")
        case "white":
            print("white king is in check")

    game.next_player()
