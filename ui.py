import pygame
from pygame._sdl2 import Window
from game import Game
import pieces
from typing import Literal

TEST = False

WINDOW_SIZE = (800, 600)
RATIO = 16 / 9
RATIO_SIZE = (1600, 900)

FONT_SIZE_SCALE = 0.02

BLACK = (0, 0, 0)
LIGHT_GREY = (158, 158, 158)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
DARK_GREY = (90, 90, 90)
DARK_BLUE = (11, 11, 255)
LIGHT_BLUE = (138, 199, 219)
GREEN = (50, 205, 50)

pygame.init()


def next_color(color) -> str:
    if color == "white":
        return "black"
    if color == "black":
        return "white"


class ObjectManager:
    def __init__(self, font_size: int = 36):
        self.background_img = pygame.image.load("img/wood-591631_1920.jpg")
        self.setting_button_img = pygame.image.load("img/settings.png")

        self.T_black = pygame.image.load("img/pieces/black-rook.png")
        self.T_white = pygame.image.load("img/pieces/white-rook.png")

        self.N_black = pygame.image.load("img/pieces/black-knight.png")
        self.N_white = pygame.image.load("img/pieces/white-knight.png")

        self.B_black = pygame.image.load("img/pieces/black-bishop.png")
        self.B_white = pygame.image.load("img/pieces/white-bishop.png")

        self.Q_black = pygame.image.load("img/pieces/black-queen.png")
        self.Q_white = pygame.image.load("img/pieces/white-queen.png")

        self.K_black = pygame.image.load("img/pieces/black-king.png")
        self.K_white = pygame.image.load("img/pieces/white-king.png")

        self.P_black = pygame.image.load("img/pieces/black-pawn.png")
        self.P_white = pygame.image.load("img/pieces/white-pawn.png")

        self.font_size = font_size

        self.font = pygame.font.Font("freesansbold.ttf", self.font_size)
        self.big_font = pygame.font.Font("freesansbold.ttf", self.font_size * 2)

        button_width = 180
        button_height = 50

        self.fullscreen_font = self.font.render("Fullscreen", True, BLACK)
        self.fullscreen_button = pygame.Rect(
            (RATIO_SIZE[0] - button_width) / 2,
            (RATIO_SIZE[1] - button_height) / 2 - 30,
            button_width,
            button_height,
        )

        self.exit_font = self.font.render("Exit", True, BLACK)
        self.exit_button = pygame.Rect(
            (RATIO_SIZE[0] - button_width) / 2,
            (RATIO_SIZE[1] - button_height) / 2 + 30,
            button_width,
            button_height,
        )

        self.windowed_font = self.font.render("Windowed", True, BLACK)
        self.windowed_button = self.fullscreen_button.copy()

        self.setting_button = pygame.transform.scale(self.setting_button_img, (40, 40))

        self.board_boarder = pygame.Rect(0, 0, 800, 800)

        self.board_boarder.center = (RATIO_SIZE[0] / 2, RATIO_SIZE[1] / 2)

        self.tile = pygame.Rect(self.board_boarder[0], self.board_boarder[1], 100, 100)

        self.white_player_font = self.font.render("White player", True, BLACK)
        self.black_player_font = self.font.render("Black player", True, BLACK)

        self.game_over_font = self.big_font.render("", True, RED)

    def render_fonts(self, font_size: int):
        """
        :param font_size: New font size
        """
        self.font_size = font_size

        self.font = pygame.font.Font("freesansbold.ttf", self.font_size)

        self.fullscreen_font = self.font.render("Fullscreen", True, BLACK)
        self.exit_font = self.font.render("Exit", True, BLACK)
        self.windowed_font = self.font.render("Windowed", True, BLACK)

    def render_cur_player_fonts(
        self, cur_player_color: Literal["white", "black"] = "white"
    ):
        """
        renders player fonts, the current player is writen in green and the other in red
        :param cur_player_color: color of current player
        """
        if cur_player_color == "white":
            self.white_player_font = self.font.render("White player", True, GREEN)
            self.black_player_font = self.font.render("Black player", True, RED)
        elif cur_player_color == "black":
            self.white_player_font = self.font.render("White player", True, RED)
            self.black_player_font = self.font.render("Black player", True, GREEN)

    def render_game_over_font(self, lost_color: Literal["white", "black", "none"]):
        if lost_color == "white":
            won = "black"
        elif lost_color == "black":
            won = "white"

        if lost_color == "none":
            self.game_over_font = self.big_font.render("Draw", True, RED)
        else:
            self.game_over_font = self.big_font.render(f"{won} player won", True, RED)


om = ObjectManager()


class Frame(pygame.surface.Surface):
    def __init__(self, surface: pygame.Surface):
        self.screen = surface

        super().__init__(RATIO_SIZE, pygame.SRCALPHA, 32)

        self.width, self.height = self.get_size()

        self.rect: pygame.Rect = pygame.Rect(0, 0, 0, 0)

    def calculate_rect(self):
        """
        calculates the position and size of the frame in the window
        """
        win_width, win_height = self.screen.get_size()
        self.width = win_width
        self.height = int(win_width / RATIO)

        if self.height > win_height:
            self.height = win_height
            self.width = int(win_height * RATIO)

        x_offset = (win_width - self.width) // 2
        y_offset = (win_height - self.height) // 2

        self.rect = pygame.Rect(x_offset, y_offset, self.width, self.height)

    def calc_element_rect(self, element_rect: pygame.Rect):
        """
        transforms the given rectangle from frame koordinates to window koordinates
        to place the element inside the frame
        :param element_rect: rectangle of an element relative to the frame (e.g. (0, 0) top-left corner of the frame)
        :returns: rectangle to blit on the screen
        """
        scale_x = self.rect.width / self.get_width()
        scale_y = self.rect.height / self.get_height()
        return pygame.Rect(
            self.rect.x + element_rect.x * scale_x,
            self.rect.y + element_rect.y * scale_y,
            element_rect.width * scale_x,
            element_rect.height * scale_y,
        )

    def show(self):
        """
        renders the frame and updates attributes to fit screen size
        """
        font_size = int(self.rect.width * FONT_SIZE_SCALE)
        om.render_fonts(font_size)
        self.calculate_rect()

        if TEST:
            pygame.draw.rect(self.screen, WHITE, self.rect)


class SettingFrame(Frame):
    def __init__(self, surface: pygame.Surface):
        super().__init__(surface)
        self.window_type = "window"

        self.exit_button: pygame.Rect = None
        self.windowed_button: pygame.Rect = None
        self.fullscreen_button: pygame.Rect = None

        self.load_exit_button()
        self.load_windowed_button()
        self.load_fullscreen_button()

    def load_fullscreen_button(self):
        """
        draws fullscreen button on the screen
        """
        self.fullscreen_button = self.calc_element_rect(om.fullscreen_button)
        pygame.draw.rect(self.screen, LIGHT_GREY, self.fullscreen_button)

        text_rect = om.fullscreen_font.get_rect(center=self.fullscreen_button.center)
        self.screen.blit(om.fullscreen_font, text_rect)

    def load_exit_button(self):
        """
        draws exit button on the screen
        """
        self.exit_button = self.calc_element_rect(om.exit_button)
        pygame.draw.rect(self.screen, LIGHT_GREY, self.exit_button)

        text_rect = om.exit_font.get_rect(center=self.exit_button.center)
        self.screen.blit(om.exit_font, text_rect)

    def load_windowed_button(self):
        """
        draws windowed button on the screen
        """
        self.windowed_button = self.calc_element_rect(om.windowed_button)
        pygame.draw.rect(self.screen, LIGHT_GREY, self.windowed_button)

        text_rect = om.windowed_font.get_rect(center=self.windowed_button.center)
        self.screen.blit(om.windowed_font, text_rect)

    def load_frame(self):
        """
        blits frame on screen
        """
        self.show()
        if self.window_type == "window":
            self.load_fullscreen_button()
        elif self.window_type == "fullscreen":
            self.load_windowed_button()
        self.load_exit_button()


class Tile:
    def __init__(
        self, screen: pygame.Surface, x: int, y: int, color: Literal["white", "black"]
    ):
        self.screen = screen
        self.cords = (y, x)
        self.color = color
        if color == "black":
            self.normal_color_code = DARK_GREY
            self.sub_color_code = DARK_BLUE
        elif color == "white":
            self.normal_color_code = WHITE
            self.sub_color_code = LIGHT_BLUE
        self.cur_color = self.normal_color_code
        self.content = None
        self.rect = pygame.Rect(0, 0, 0, 0)

    def load_content(self):
        """
        blits chess piece in the center of the tile if associated with one
        """
        if self.content is not None:
            img_code = f"{self.content.sym}_{self.content.color}"
            piece_img: pygame.Surface = getattr(om, img_code)
            piece_img_scaled = pygame.transform.scale(piece_img, self.rect.size)
            piece_rect = piece_img_scaled.get_rect()
            piece_rect.center = self.rect.center
            self.screen.blit(piece_img_scaled, piece_rect)


class GameFrame(Frame):
    def __init__(self, surface: pygame.Surface):
        super().__init__(surface)
        self.game = Game()
        self.board_rect = pygame.Rect(0, 0, 0, 0)
        self.tiles: list[Tile] = []
        self.change_tiles: list[Tile] = []
        self.setup_tiles()
        self.pawn_reached_end = False
        self.changeable_pawn: pieces.PieceManager.Pawn = None

        self.white_player_rect = pygame.Rect(0, 0, 0, 0)
        self.black_player_rect = pygame.Rect(0, 0, 0, 0)

    def setup_tiles(self):
        """
        generates tiles for the board and populates tiles attribute
        """
        color = "black"
        for i in range(0, 8):
            color = next_color(color)
            for j in range(0, 8):
                self.tiles.append(Tile(self.screen, i, j, color))
                color = next_color(color)

    def resize_board(self):
        """
        resizes board on frame and centers it
        """
        rect = om.board_boarder
        rect.center = self.get_rect().center
        self.board_rect = self.calc_element_rect(rect)

    def resize_tiles(self):
        """
        resizes tiles on frame
        """
        self.resize_board()
        tile_width, tile_height = (
            int(self.board_rect.width / 8),
            int(self.board_rect.height / 8),
        )
        for tile in self.tiles:
            tile.rect = pygame.Rect(
                self.board_rect[0] + (tile.cords[1] * tile_width),
                self.board_rect[1] + (tile.cords[0] * tile_height),
                tile_width,
                tile_height,
            )

    def load_tiles(self):
        """
        draws tiles of the gameboard with current game state on the screen
        """
        self.resize_tiles()
        for tile in self.tiles:
            pygame.draw.rect(self.screen, tile.cur_color, tile.rect)
            tile.content = self.game.board.board[tile.cords]
            tile.load_content()

    def load_boarder(self):
        """
        draws a black boarder around the board
        """
        rect = self.tiles[0].rect
        board_rect = pygame.Rect(tuple(rect[:2]) + (rect[-1] * 8, rect[-1] * 8))
        pygame.draw.rect(self.screen, BLACK, board_rect, 1)

    def show_select_field(self, color: Literal["white", "black"]):
        """
        draws the select field for when a pawn reaches the other side of the board
        :param color: color of the pieces
        """
        if color == "white":
            tile_color = "black"
        elif color == "black":
            tile_color = "white"

        self.change_tiles: list[Tile] = []

        rock_tile = Tile(self.screen, 0, 0, tile_color)
        rock_tile.content = pieces.PieceManager.Rook(color)
        self.change_tiles.append(rock_tile)

        knight_tile = Tile(self.screen, 1, 0, tile_color)
        knight_tile.content = pieces.PieceManager.Knight(color)
        self.change_tiles.append(knight_tile)

        bishop_tile = Tile(self.screen, 2, 0, tile_color)
        bishop_tile.content = pieces.PieceManager.Bishop(color)
        self.change_tiles.append(bishop_tile)

        queen_tile = Tile(self.screen, 3, 0, tile_color)
        queen_tile.content = pieces.PieceManager.Queen(color)
        self.change_tiles.append(queen_tile)

        self.resize_board()

        tile_width, tile_height = (
            int(self.board_rect.width / 8),
            int(self.board_rect.height / 8),
        )
        tile_start = (
            self.board_rect.center[0] - tile_width * 2,
            self.board_rect.center[1] - tile_height / 2,
        )
        for tile in self.change_tiles:
            tile.rect = pygame.Rect(
                tile_start[0] + tile_width * tile.cords[1],
                tile_start[1],
                tile_width,
                tile_height,
            )
            pygame.draw.rect(self.screen, tile.normal_color_code, tile.rect)
            pygame.draw.rect(self.screen, BLACK, tile.rect, 1)
            tile.load_content()

    def load_players(self):
        """
        blits the players on the screen to show witch turn it is
        """
        self.white_player_rect = om.white_player_font.get_rect()
        self.white_player_rect.center = (RATIO_SIZE[0] * (1 / 8), RATIO_SIZE[1] / 25)
        self.white_player_rect = self.calc_element_rect(self.white_player_rect)

        self.black_player_rect = om.black_player_font.get_rect()
        self.black_player_rect.center = (RATIO_SIZE[0] * (7 / 8), RATIO_SIZE[1] / 25)
        self.black_player_rect = self.calc_element_rect(self.black_player_rect)

        om.render_cur_player_fonts(self.game.cur_player.color)

        background_white_rect = pygame.Rect(
            self.white_player_rect.x,
            self.white_player_rect.y,
            om.white_player_font.get_rect().width,
            om.white_player_font.get_rect().height,
        )

        pygame.draw.rect(self.screen, WHITE, background_white_rect)
        self.screen.blit(om.white_player_font, self.white_player_rect)

        background_black_rect = pygame.Rect(
            self.black_player_rect.x,
            self.black_player_rect.y,
            om.black_player_font.get_rect().width,
            om.black_player_font.get_rect().height,
        )

        pygame.draw.rect(self.screen, WHITE, background_black_rect)
        self.screen.blit(om.black_player_font, self.black_player_rect)

    def load_killed_pieces(self):
        tile_width = self.tiles[0].rect.width * (3 / 4)
        tile_height = self.tiles[0].rect.height * (3 / 4)

        cur_row = 0
        cur_col = 0

        start_x = self.white_player_rect.center[0] - 2 * tile_width
        start_y = self.white_player_rect.center[1] + self.board_rect.height * (1 / 25)

        for piece in self.game.killed_white:
            tile = Tile(self.screen, x=cur_col, y=cur_row, color="white")
            tile.rect = pygame.Rect(
                start_x + (cur_col * tile_width),
                start_y + (cur_row * tile_height),
                tile_width,
                tile_height,
            )
            tile.content = piece
            tile.load_content()

            if cur_col == 3:
                cur_col = 0
                cur_row += 1
            else:
                cur_col += 1

        cur_row = 0
        cur_col = 0

        start_x = self.black_player_rect.center[0] - 2 * tile_width
        start_y = self.black_player_rect.center[1] + self.board_rect.height * (1 / 25)

        for piece in self.game.killed_black:
            tile = Tile(self.screen, x=cur_col, y=cur_row, color="black")
            tile.rect = pygame.Rect(
                start_x + (cur_col * tile_width),
                start_y + (cur_row * tile_height),
                tile_width,
                tile_height,
            )
            tile.content = piece
            tile.load_content()

            if cur_col == 3:
                cur_col = 0
                cur_row += 1
            else:
                cur_col += 1

    def load_frame(self):
        """
        blits frame on screen
        """
        self.show()
        self.load_tiles()
        self.load_boarder()
        self.load_players()
        self.load_killed_pieces()
        if self.pawn_reached_end:
            self.show_select_field(self.game.cur_player.color)


class UiBrain:
    def __init__(self):
        self.screen = pygame.display.set_mode(
            WINDOW_SIZE, pygame.DOUBLEBUF | pygame.RESIZABLE
        )
        Window.from_display_module().maximize()

        self.clock = pygame.time.Clock()
        self.tickrate = 60

        self.selected_piece: pieces.Piece = pieces.Piece(
            possible_pos=[], possible_strikes=[], color="white"
        )

        self.screen.blit(om.background_img, (0, 0))
        self.setting_button_rect: pygame.Rect = om.setting_button.get_rect()

        self.setting_frame = SettingFrame(self.screen)
        self.game_frame = GameFrame(self.screen)

        self.cur_frame = self.game_frame

        self.toggle = False

        self.game_over = False

    def resize_screen(self, size: tuple[int, int]):
        """
        resizes the screen if not in fullscreen
        :param size: size of the window
        """
        if not self.toggle:
            self.screen = pygame.display.set_mode(
                size, pygame.DOUBLEBUF | pygame.RESIZABLE
            )
        self.toggle = False

    def update_background(self):
        """
        blits the background image on the screen
        """
        self.screen.blit(
            pygame.transform.scale(om.background_img, self.screen.get_rect().size),
            (0, 0),
        )

    def toggle_fullscreen(self):
        """
        switches between fullscreen and windowed
        """
        if self.setting_frame.window_type == "window":
            Window.from_display_module().restore()
            self.screen = pygame.display.set_mode(
                (0, 0), pygame.DOUBLEBUF | pygame.FULLSCREEN
            )
            self.setting_frame.window_type = "fullscreen"
        else:
            self.screen = pygame.display.set_mode(
                WINDOW_SIZE, pygame.DOUBLEBUF | pygame.RESIZABLE
            )
            self.setting_frame.window_type = "window"
            Window.from_display_module().maximize()
        self.toggle = True

    def load_setting_button(self):
        """
        blits the setting button on the screen to reach the game settings
        """
        rect = self.cur_frame.calc_element_rect(om.setting_button.get_rect())
        setting_button_scaled = pygame.transform.scale(om.setting_button_img, rect[-2:])
        self.screen.blit(setting_button_scaled, (4, 4))
        self.setting_button_rect = pygame.Rect((4, 4) + tuple(rect[-2:]))

    def check_toggle_clicked(self, pos: tuple[int, int]):
        if self.cur_frame == self.setting_frame:
            if self.setting_frame.fullscreen_button.collidepoint(
                pos
            ) or self.setting_frame.windowed_button.collidepoint(pos):
                self.toggle_fullscreen()
            if self.setting_frame.exit_button.collidepoint(pos):
                pygame.quit()

    def switch_setting_frame(self):
        """
        switch from setting frame to game frame or the other way around
        """
        if self.cur_frame == self.setting_frame:
            self.cur_frame = self.game_frame
        elif self.cur_frame == self.game_frame:
            self.cur_frame = self.setting_frame

    def select_piece(self, pos: tuple[int, int]):
        """
        trys to select a piece and saves it in selected_piece attribute
        :param pos: position of the piece to select
        :return:
        """
        piece = self.game_frame.game.board.board[pos]
        if piece is not None:
            if piece.color == self.game_frame.game.cur_player.color:
                moves = self.game_frame.game.get_piece_possible_moves(piece)
                self.selected_piece = piece
                for tile in self.game_frame.tiles:
                    if tile.cords in moves:
                        tile.cur_color = tile.sub_color_code
                    else:
                        tile.cur_color = tile.normal_color_code

    def try_move_selected_piece(self, pos: tuple[int, int]):
        """
        moves the selected piece if the select screen isn't open
        :param pos: new position for the piece
        """
        if not self.game_frame.pawn_reached_end:
            if pos in self.game_frame.game.get_piece_possible_moves(
                self.selected_piece
            ):
                self.game_frame.game.move_piece(self.selected_piece.cur_pos, pos)
                if self.game_frame.game.board.pawn_reached_end(pos):
                    self.game_frame.pawn_reached_end = True
                    self.game_frame.changeable_pawn = self.game_frame.game.board.board[
                        pos
                    ]

                self.unselect_all()
                if not self.game_frame.pawn_reached_end:
                    self.game_frame.game.next_player()

    def unselect_all(self):
        """
        unselects all pieces
        """
        self.selected_piece = pieces.Piece(
            possible_pos=[], possible_strikes=[], color="white"
        )
        for tile in self.game_frame.tiles:
            tile.cur_color = tile.normal_color_code

    def load_game_over(self):
        """
        blits the game over text on the screen
        """
        om.render_game_over_font(self.game_frame.game.test_checkmate())
        text_rect = om.game_over_font.get_rect(center=self.screen.get_rect().center)
        self.screen.blit(om.game_over_font, text_rect)
        self.game_over = True

    def mainloop(self):
        """
        mainloop of the ui
        """
        self.cur_frame.load_frame()
        if self.game_over:
            self.load_game_over()

        self.load_setting_button()
        pygame.display.flip()
        self.clock.tick(self.tickrate)


class EventManager:
    def __init__(self, ui: UiBrain):
        self.ui = ui
        self.events = []
        self.cur_event = None

    def manage_events(self, events: list[pygame.event.Event]):
        """
        manages events of pygame
        :param events: list of pygame events (pygame.event.get())
        """
        self.events = events
        for self.cur_event in self.events:
            self.check_quit()
            self.check_resize()
            self.check_options_button()

            if self.ui.cur_frame == self.ui.setting_frame:
                self.check_return_to_game_frame()
                self.check_setting_buttons()

            if self.ui.cur_frame == self.ui.game_frame:
                if not self.ui.game_frame.pawn_reached_end:
                    self.check_player_actions()
                else:
                    self.check_change_pawn()

    def check_quit(self):
        if self.cur_event.type == pygame.QUIT:
            pygame.quit()

    def check_resize(self):
        if self.cur_event.type == pygame.VIDEORESIZE:
            self.ui.resize_screen(self.cur_event.size)

    def check_return_to_game_frame(self):
        if self.cur_event.type == pygame.KEYDOWN:
            if self.cur_event.key == pygame.K_ESCAPE:
                self.ui.cur_frame = self.ui.game_frame

    def check_setting_buttons(self):
        """
        checks if setting buttons (e.g. fullscreen button) have been clicked and handles them appropriately
        """
        if self.cur_event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()

            if self.ui.setting_frame.fullscreen_button.collidepoint(
                pos
            ) or self.ui.setting_frame.windowed_button.collidepoint(pos):
                self.ui.toggle_fullscreen()
            if self.ui.setting_frame.exit_button.collidepoint(pos):
                pygame.quit()

    def check_options_button(self):
        """
        checks if the setting wheel has been clicked and opens or closes the settings window
        """
        if self.cur_event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()

            if self.ui.setting_button_rect.collidepoint(pos):
                self.ui.switch_setting_frame()

    def check_player_actions(self):
        """
        checks for player actions (e.g. select a piece) and handles them appropriately
        :return:
        """
        if self.cur_event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            for tile in self.ui.game_frame.tiles:
                if tile.rect.collidepoint(pos):
                    self.ui.select_piece(tile.cords)
                    self.ui.try_move_selected_piece(tile.cords)
                    self.ui.game_over = self.ui.game_frame.game.game_end()

    def check_change_pawn(self):
        """
        checks if a piece from the select screen has been chosen and changes the pawn into the chosen piece
        """
        if self.cur_event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            for tile in self.ui.game_frame.change_tiles:
                if tile.rect.collidepoint(pos):
                    self.ui.game_frame.game.board.replace_pawn(
                        self.ui.game_frame.changeable_pawn, tile.content.sym
                    )
                    self.ui.game_frame.pawn_reached_end = False
                    self.ui.game_frame.game.next_player()
