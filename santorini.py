# t4_updated.py
import arcade
import random
import math
import os
import pyglet
from enum import Enum
from typing import List, Tuple, Optional, Any

# ---- CONFIG ----
BOARD_SIZE = 5
CELL_SIZE = 120
PADDING = 40
SCREEN_WIDTH = BOARD_SIZE * CELL_SIZE + 420
SCREEN_HEIGHT = BOARD_SIZE * CELL_SIZE + PADDING * 2
SCREEN_TITLE = "Santorini"

# Visual / audio assets (edit filenames as you like)
# ---- CONFIG ----
# import os

ASSET_DIR = os.path.dirname(os.path.abspath(__file__))

def asset(*parts):
    return os.path.join(ASSET_DIR, *parts)

BACKGROUND_IMAGE = asset("background.jpg")     # <-- no leading slash
BOARD_BG_IMAGE   = asset("board_frame.png")
BACKGROUND_MUSIC = asset("mainbgm.mp3")
WIN_MUSIC        = asset("win_bgm.mp3")
LOSE_MUSIC       = asset("lose_bgm.mp3")
SND_PLACE        = asset("place.wav")
SND_MOVE         = asset("move.wav")
SND_BUILD        = asset("build.wav")
SND_WIN          = asset("win_bgm.wav")
FONT_FILE        = asset("Montserrat-Regular.ttf")


# Colors
BG_FALLBACK_TOP = arcade.color.AIR_SUPERIORITY_BLUE
BG_FALLBACK_BOTTOM = arcade.color.LIGHT_CYAN
BOARD_PANEL = arcade.color.ALMOND
CELL_COLOR = arcade.color.ANTIQUE_WHITE
GRID_COLOR = arcade.color.DARK_GRAY
BLOCK_COLORS = [arcade.color.GRAY, arcade.color.SILVER, arcade.color.LIGHT_GRAY]
DOME_COLOR = arcade.color.ROYAL_BLUE
PLAYER1_COLOR = arcade.color.ELECTRIC_CRIMSON
PLAYER2_COLOR = arcade.color.SPRING_GREEN
SELECTED_COLOR = arcade.color.GOLD
POSSIBLE_MOVE_COLOR = arcade.color.AZURE
BUILD_COLOR = arcade.color.CORAL
UI_BG = (255,255,255,220)

# Derived offsets
BOARD_PIXEL_SIZE = BOARD_SIZE * CELL_SIZE
BOARD_OFFSET_X = PADDING + 20
BOARD_OFFSET_Y = (SCREEN_HEIGHT - BOARD_PIXEL_SIZE) // 2
UI_PANEL_X = BOARD_OFFSET_X + BOARD_PIXEL_SIZE + 20
UI_PANEL_WIDTH = SCREEN_WIDTH - UI_PANEL_X - PADDING

MAX_WORKERS_PER_PLAYER = 2

# --- Safe Arcade compatibility shim (kept from original) ---
_orig_draw_lrtb_filled = getattr(arcade, "draw_lrtb_rectangle_filled", None)
_orig_draw_lrbt_filled = getattr(arcade, "draw_lrbt_rectangle_filled", None)
_orig_draw_lrtb_outline = getattr(arcade, "draw_lrtb_rectangle_outline", None)
_orig_draw_lrbt_outline = getattr(arcade, "draw_lrbt_rectangle_outline", None)
_orig_draw_lrwh_textured = getattr(arcade, "draw_lrwh_rectangle_textured", None)
_orig_draw_rectangle_filled = getattr(arcade, "draw_rectangle_filled", None)
_orig_draw_rectangle_outline = getattr(arcade, "draw_rectangle_outline", None)
_orig_draw_polygon_filled = getattr(arcade, "draw_polygon_filled", None)
_orig_draw_line = getattr(arcade, "draw_line", None)

def _safe_draw_rectangle_filled(x, y, width, height, color):
    left = x - width / 2
    right = x + width / 2
    top = y + height / 2
    bottom = y - height / 2
    if _orig_draw_rectangle_filled:
        return _orig_draw_rectangle_filled(x, y, width, height, color)
    if _orig_draw_lrtb_filled:
        return _orig_draw_lrtb_filled(left, right, top, bottom, color)
    if _orig_draw_lrbt_filled:
        return _orig_draw_lrbt_filled(left, right, bottom, top, color)
    if _orig_draw_polygon_filled:
        return _orig_draw_polygon_filled([(left, bottom), (left, top), (right, top), (right, bottom)], color)
    return None

def _safe_draw_rectangle_outline(x, y, width, height, color, border_width=1):
    left = x - width / 2
    right = x + width / 2
    top = y + height / 2
    bottom = y - height / 2
    if _orig_draw_rectangle_outline:
        return _orig_draw_rectangle_outline(x, y, width, height, color, border_width)
    if _orig_draw_lrtb_outline:
        return _orig_draw_lrtb_outline(left, right, top, bottom, color, border_width)
    if _orig_draw_lrbt_outline:
        return _orig_draw_lrbt_outline(left, right, bottom, top, color, border_width)
    if _orig_draw_line:
        _orig_draw_line(left, bottom, left, top, color, border_width)
        _orig_draw_line(left, top, right, top, color, border_width)
        _orig_draw_line(right, top, right, bottom, color, border_width)
        _orig_draw_line(right, bottom, left, bottom, color, border_width)
        return None
    return None

def _safe_lrtb_filled(left, right, top, bottom, color):
    if _orig_draw_lrtb_filled:
        return _orig_draw_lrtb_filled(left, right, top, bottom, color)
    if _orig_draw_lrbt_filled:
        return _orig_draw_lrbt_filled(left, right, bottom, top, color)
    if _orig_draw_polygon_filled:
        return _orig_draw_polygon_filled([(left, bottom), (left, top), (right, top), (right, bottom)], color)
    return None

def _safe_lrtb_outline(left, right, top, bottom, color, border_width=1):
    if _orig_draw_lrtb_outline:
        return _orig_draw_lrtb_outline(left, right, top, bottom, color, border_width)
    if _orig_draw_lrbt_outline:
        return _orig_draw_lrbt_outline(left, right, bottom, top, color, border_width)
    if _orig_draw_line:
        _orig_draw_line(left, bottom, left, top, color, border_width)
        _orig_draw_line(left, top, right, top, color, border_width)
        _orig_draw_line(right, top, right, bottom, color, border_width)
        _orig_draw_line(right, bottom, left, bottom, color, border_width)
        return None
    return None

def _safe_lrwh_rectangle_textured(x, y, width, height, texture):
    if _orig_draw_lrwh_textured:
        return _orig_draw_lrwh_textured(x, y, width, height, texture)
    return _safe_draw_rectangle_filled(x + width/2, y + height/2, width, height, (0,0,0,0))

if not hasattr(arcade, "draw_rectangle_filled"):
    arcade.draw_rectangle_filled = _safe_draw_rectangle_filled
if not hasattr(arcade, "draw_rectangle_outline"):
    arcade.draw_rectangle_outline = _safe_draw_rectangle_outline
if not hasattr(arcade, "draw_lrtb_rectangle_filled"):
    if _orig_draw_lrtb_filled or _orig_draw_lrbt_filled or _orig_draw_polygon_filled:
        arcade.draw_lrtb_rectangle_filled = _safe_lrtb_filled
if not hasattr(arcade, "draw_lrtb_rectangle_outline"):
    if _orig_draw_lrtb_outline or _orig_draw_lrbt_outline or _orig_draw_line:
        arcade.draw_lrtb_rectangle_outline = _safe_lrtb_outline
if not hasattr(arcade, "draw_lrwh_rectangle_textured"):
    arcade.draw_lrwh_rectangle_textured = _safe_lrwh_rectangle_textured
# --- End shim ---

class GameState(Enum):
    MAIN_MENU = 0
    SETTINGS_MENU = 1
    DIFFICULTY_MENU = 2
    SETUP = 3
    PLAYER_MOVE = 4
    PLAYER_BUILD = 5
    AI_THINKING = 6
    GAME_OVER = 7

class Player:
    def __init__(self, player_id: int, color: Any, is_ai: bool = False):
        self.player_id = player_id
        self.color = color
        self.is_ai = is_ai
        self.workers: List[Tuple[int,int]] = []

class GameBoard:
    def __init__(self):
        self.board = [[0 for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.workers = [[0 for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]

    def get_height(self, r:int, c:int) -> int:
        if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
            return self.board[r][c]
        return -1

    def has_worker(self, r:int, c:int) -> int:
        if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
            return self.workers[r][c]
        return -1

    def place_worker(self, r:int, c:int, pid:int) -> bool:
        if (0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and self.workers[r][c] == 0 and self.board[r][c] < 4):
            self.workers[r][c] = pid
            return True
        return False

    def can_move(self, fr, fc, tr, tc) -> bool:
        if not (0 <= tr < BOARD_SIZE and 0 <= tc < BOARD_SIZE): return False
        if abs(fr - tr) > 1 or abs(fc - tc) > 1: return False
        if fr == tr and fc == tc: return False
        if self.workers[tr][tc] != 0 or self.board[tr][tc] >= 4: return False
        if self.board[tr][tc] > self.board[fr][fc] + 1: return False
        return True

    def move_worker(self, fr, fc, tr, tc) -> bool:
        if self.can_move(fr, fc, tr, tc):
            pid = self.workers[fr][fc]
            self.workers[fr][fc] = 0
            self.workers[tr][tc] = pid
            return True
        return False

    def force_move(self, fr, fc, tr, tc):
        pid = self.workers[fr][fc]
        self.workers[fr][fc] = 0
        self.workers[tr][tc] = pid

    def can_build(self, wr, wc, br, bc) -> bool:
        if not (0 <= br < BOARD_SIZE and 0 <= bc < BOARD_SIZE): return False
        if abs(wr - br) > 1 or abs(wc - bc) > 1: return False
        if self.workers[br][bc] != 0 or self.board[br][bc] >= 4: return False
        return True

    def build(self, r, c) -> bool:
        if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and self.workers[r][c] == 0 and self.board[r][c] < 4:
            self.board[r][c] += 1
            return True
        return False

    def get_possible_moves(self, r, c):
        out=[]
        for dr in (-1,0,1):
            for dc in (-1,0,1):
                if dr==0 and dc==0: continue
                nr, nc = r+dr, c+dc
                if self.can_move(r,c,nr,nc):
                    out.append((nr,nc))
        return out

    def get_possible_builds(self, r, c):
        out=[]
        for dr in (-1,0,1):
            for dc in (-1,0,1):
                if dr==0 and dc==0: continue
                br, bc = r+dr, c+dc
                if self.can_build(r,c,br,bc):
                    out.append((br,bc))
        return out

class SantoriniAI:
    def __init__(self, player_id:int, depth:int=3):
        self.player_id = player_id
        self.opponent_id = 2 if player_id==1 else 1
        self.depth = depth

    def evaluate_board(self, board:GameBoard) -> float:
        score = 0
        ai_workers=[]
        op_workers=[]
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if board.workers[r][c]==self.player_id: ai_workers.append((r,c))
                elif board.workers[r][c]==self.opponent_id: op_workers.append((r,c))
        for r,c in ai_workers:
            if board.board[r][c] == 3: return 1000
        for r,c in op_workers:
            if board.board[r][c] == 3: return -1000
        score += sum(board.board[r][c] for r,c in ai_workers)*8
        score -= sum(board.board[r][c] for r,c in op_workers)*6
        score += sum(len(board.get_possible_moves(r,c)) for r,c in ai_workers)*2
        score -= sum(len(board.get_possible_moves(r,c)) for r,c in op_workers)*1.5
        center = BOARD_SIZE//2
        for r,c in ai_workers:
            score += max(0, 4 - (abs(r-center)+abs(c-center)))
        for r,c in op_workers:
            score -= max(0, 4 - (abs(r-center)+abs(c-center)))
        return score

    def minimax(self, board:GameBoard, depth:int, alpha:float, beta:float, maximizing:bool):
        if depth==0:
            return self.evaluate_board(board), None
        current = self.player_id if maximizing else self.opponent_id
        worker_positions=[]
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if board.workers[r][c]==current:
                    worker_positions.append((r,c))
        if not any(board.get_possible_moves(r,c) for r,c in worker_positions):
            return (-1000 if maximizing else 1000), None
        best_move=None
        if maximizing:
            value = float('-inf')
            for wp in worker_positions:
                r,c = wp
                possible_moves = board.get_possible_moves(r,c)
                for nr,nc in possible_moves:
                    pid = board.workers[r][c]
                    board.force_move(r,c,nr,nc)
                    if board.board[nr][nc] == 3:
                        board.workers[r][c] = pid
                        board.workers[nr][nc] = 0
                        return 1000, (wp,(nr,nc),None)
                    builds = board.get_possible_builds(nr,nc)
                    if not builds:
                        sc,_ = self.minimax(board, depth-1, alpha, beta, False)
                        if sc > value:
                            value = sc
                            best_move = (wp,(nr,nc),None)
                        alpha = max(alpha, sc)
                        board.workers[r][c] = pid
                        board.workers[nr][nc] = 0
                        if beta <= alpha:
                            return value, best_move
                        continue
                    for br,bc in builds:
                        board.board[br][bc] += 1
                        sc,_ = self.minimax(board, depth-1, alpha, beta, False)
                        board.board[br][bc] -= 1
                        if sc > value:
                            value = sc
                            best_move = (wp,(nr,nc),(br,bc))
                        alpha = max(alpha, sc)
                        if beta <= alpha:
                            board.workers[r][c] = pid
                            board.workers[nr][nc] = 0
                            return value, best_move
                    board.workers[r][c] = pid
                    board.workers[nr][nc] = 0
            return value, best_move
        else:
            value = float('inf')
            for wp in worker_positions:
                r,c = wp
                possible_moves = board.get_possible_moves(r,c)
                for nr,nc in possible_moves:
                    pid = board.workers[r][c]
                    board.force_move(r,c,nr,nc)
                    if board.board[nr][nc] == 3:
                        board.workers[r][c] = pid
                        board.workers[nr][nc] = 0
                        return -1000, (wp,(nr,nc),None)
                    builds = board.get_possible_builds(nr,nc)
                    if not builds:
                        sc,_ = self.minimax(board, depth-1, alpha, beta, True)
                        if sc < value:
                            value = sc
                            best_move = (wp,(nr,nc),None)
                        beta = min(beta, sc)
                        board.workers[r][c] = pid
                        board.workers[nr][nc] = 0
                        if beta <= alpha:
                            return value, best_move
                        continue
                    for br,bc in builds:
                        board.board[br][bc] += 1
                        sc,_ = self.minimax(board, depth-1, alpha, beta, True)
                        board.board[br][bc] -= 1
                        if sc < value:
                            value = sc
                            best_move = (wp,(nr,nc),(br,bc))
                        beta = min(beta, sc)
                        if beta <= alpha:
                            board.workers[r][c] = pid
                            board.workers[nr][nc] = 0
                            return value, best_move
                    board.workers[r][c] = pid
                    board.workers[nr][nc] = 0
            return value, best_move

    def get_best_move(self, board:GameBoard):
        _, mv = self.minimax(board, self.depth, float('-inf'), float('inf'), True)
        return mv

class SantoriniGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, resizable=False)

        # Settings
        self.bgm_on = True
        self.sfx_on = True
        self.ai_difficulty_depth = 3  # default (difficult)
        self.background_texture = None
        self.board_bg_texture = None

        if os.path.exists(BACKGROUND_IMAGE):
            try:
                self.background_texture = arcade.load_texture(BACKGROUND_IMAGE)
            except Exception as e:
                print("Background load failed:", e)
                self.background_texture = None

        if os.path.exists(BOARD_BG_IMAGE):
            try:
                self.board_bg_texture = arcade.load_texture(BOARD_BG_IMAGE)
            except Exception as e:
                print("Board background load failed:", e)
                self.board_bg_texture = None

        arcade.set_background_color(BG_FALLBACK_BOTTOM)

        # sound containers; music_player is a pyglet player for looped bgm
        self.sounds = {}
        self.music_player = None   # looping main bgm player
        self.outro_player = None   # one-shot win/lose player

        # fonts
        self.custom_font = None
        if os.path.exists(FONT_FILE):
            try:
                arcade.load_font(FONT_FILE)
                self.custom_font = FONT_FILE
            except Exception:
                self.custom_font = None

        # Game & UI state
        self.reset_game_state(minimal=True)

        # Load sounds according to settings
        self.load_sounds()

    def reset_game_state(self, minimal=False):
        self.board = GameBoard()
        self.current_player = 1
        self.game_state = GameState.MAIN_MENU if minimal else GameState.SETUP
        self.selected_worker: Optional[Tuple[int,int]] = None
        self.workers_placed = 0
        self.move_made = False
        self.winner: Optional[int] = None

        self.player1 = Player(1, PLAYER1_COLOR, is_ai=False)
        self.player2 = Player(2, PLAYER2_COLOR, is_ai=True)
        self.ai = SantoriniAI(2, depth=self.ai_difficulty_depth)

        self.possible_moves: List[Tuple[int,int]] = []
        self.possible_builds: List[Tuple[int,int]] = []
        self.animations: List[dict] = []

        self.ui_title_size = 22
        self.ui_text_size = 14

    def load_sounds(self):
        def try_load(name):
            if os.path.exists(name):
                try:
                    return arcade.load_sound(name)
                except Exception as e:
                    print("Sound load failed:", name, e)
            else:
                print("Sound file missing:", name)
            return None

        self.sounds['place'] = try_load(SND_PLACE)
        self.sounds['move']  = try_load(SND_MOVE)
        self.sounds['build'] = try_load(SND_BUILD)
        self.sounds['win']   = try_load(SND_WIN)

        # Background music: only start if bgm_on is True
        if self.bgm_on and os.path.exists(BACKGROUND_MUSIC):
            try:
                src = pyglet.media.load(BACKGROUND_MUSIC)
                player = pyglet.media.Player()
                player.queue(src)
                player.loop = True
                player.volume = 0.25
                player.play()
                self.music_player = player
                print("BGM started (pyglet player).")
            except Exception as e:
                print("Bg music load failed (pyglet):", e)
                self.music_player = None
        else:
            if not os.path.exists(BACKGROUND_MUSIC):
                print("BGM file not found:", BACKGROUND_MUSIC)
            self.music_player = None

    def toggle_bgm(self):
        self.bgm_on = not self.bgm_on
        if self.bgm_on:
            # start music
            if not self.music_player and os.path.exists(BACKGROUND_MUSIC):
                try:
                    src = pyglet.media.load(BACKGROUND_MUSIC)
                    player = pyglet.media.Player()
                    player.queue(src)
                    player.loop = True
                    player.volume = 0.25
                    player.play()
                    self.music_player = player
                except Exception as e:
                    print("Failed to start bgm:", e)
        else:
            # stop music
            try:
                if self.music_player:
                    self.music_player.pause()
                    self.music_player.next_source()
            except Exception:
                pass
            self.music_player = None

    def toggle_sfx(self):
        self.sfx_on = not self.sfx_on

    def play_sfx(self, key):
        if not self.sfx_on:
            return
        snd = self.sounds.get(key)
        if snd:
            try:
                arcade.play_sound(snd)
            except Exception:
                pass

    def play_outro_music(self, winner_pid: int):
        # stop looping bgm temporarily
        try:
            if self.music_player:
                self.music_player.pause()
        except Exception:
            pass

        # stop any currently playing outro
        try:
            if self.outro_player:
                self.outro_player.pause()
                self.outro_player.next_source()
        except Exception:
            pass

        pick = WIN_MUSIC if winner_pid == 1 else LOSE_MUSIC
        if os.path.exists(pick):
            try:
                src = pyglet.media.load(pick)
                player = pyglet.media.Player()
                player.queue(src)
                player.loop = False
                player.volume = 0.35
                player.play()
                self.outro_player = player
            except Exception as e:
                print("Failed to play outro:", e)
                self.outro_player = None
        else:
            print("Outro file not found:", pick)
            self.outro_player = None

    def rebuild_player_workers_from_board(self):
        self.player1.workers = []
        self.player2.workers = []
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                w = self.board.workers[r][c]
                if w == 1:
                    self.player1.workers.append((r,c))
                elif w == 2:
                    self.player2.workers.append((r,c))

    # ----- UI helper: buttons -----
    def draw_button(self, center_x, center_y, width, height, text, hover=False):
        # subtle two-part fill to fake a gradient
        color_top = (245, 245, 245) if not hover else (230, 230, 255)
        color_bottom = (210, 210, 210) if not hover else (190, 190, 230)

        left, right = center_x - width/2, center_x + width/2
        top, mid, bottom = center_y + height/2, center_y, center_y - height/2

        arcade.draw_lrtb_rectangle_filled(left, right, top, mid, color_top)
        arcade.draw_lrtb_rectangle_filled(left, right, mid, bottom, color_bottom)

        arcade.draw_rectangle_outline(center_x, center_y, width, height, (90, 90, 120), 2)
        arcade.draw_text(text, center_x, center_y - 2, (30, 30, 60),
                        14, anchor_x="center", anchor_y="center", bold=True)


    def button_hit(self, bx, by, bw, bh, x, y):
        left = bx - bw/2
        right = bx + bw/2
        bottom = by - bh/2
        top = by + bh/2
        return left <= x <= right and bottom <= y <= top

    # ----- Core drawing -----
    def on_draw(self):
        self.clear()
        # background: either image full-screen or gradient fallback
        if self.background_texture:
            arcade.draw_lrwh_rectangle_textured(0, 0, self.width, self.height, self.background_texture)
            # subtle dark overlay so UI stands out
            arcade.draw_lrtb_rectangle_filled(0, self.width, self.height, 0, (0,0,0,40))
        else:
            arcade.draw_rectangle_filled(self.width/2, self.height*0.66, self.width, self.height*0.66, BG_FALLBACK_TOP)
            arcade.draw_rectangle_filled(self.width/2, self.height*0.33, self.width, self.height*0.66, BG_FALLBACK_BOTTOM)

        # Draw decorated board background (if present) behind the board panel
        panel_x = BOARD_OFFSET_X + BOARD_PIXEL_SIZE/2
        panel_y = BOARD_OFFSET_Y + BOARD_PIXEL_SIZE/2
        panel_w = BOARD_PIXEL_SIZE + 24
        panel_h = BOARD_PIXEL_SIZE + 24

        if self.board_bg_texture:
            # draw texture centered behind the board (scaled to panel size)
            arcade.draw_lrwh_rectangle_textured(BOARD_OFFSET_X-12, BOARD_OFFSET_Y-12, panel_w, panel_h, self.board_bg_texture)
            # a subtle frame overlay
            arcade.draw_lrtb_rectangle_outline(BOARD_OFFSET_X-12, BOARD_OFFSET_X-12+panel_w, BOARD_OFFSET_Y-12+panel_h, BOARD_OFFSET_Y-12, GRID_COLOR, 3)
        else:
            # fallback plain panel
            arcade.draw_rectangle_filled(panel_x, panel_y, panel_w, panel_h, BOARD_PANEL)
            arcade.draw_rectangle_outline(panel_x, panel_y, panel_w, panel_h, GRID_COLOR, 3)

        # Dispatch by state
        if self.game_state == GameState.MAIN_MENU:
            self.draw_main_menu()
        elif self.game_state == GameState.SETTINGS_MENU:
            self.draw_settings_menu()
        elif self.game_state == GameState.DIFFICULTY_MENU:
            self.draw_difficulty_menu()
        else:
            # in-game drawing
            self.draw_board()
            self.draw_ui()

            # If game over show popup modal
            if self.game_state == GameState.GAME_OVER:
                self.draw_game_over_popup()

    # ---- Menu screens ----
    def draw_main_menu(self):
        title_y = SCREEN_HEIGHT - 110
        arcade.draw_text("Santorini", SCREEN_WIDTH/2, title_y, GRID_COLOR, 48, anchor_x="center", bold=True)
        subtitle = "Menu"
        arcade.draw_text(subtitle, SCREEN_WIDTH/2, title_y - 46, (40,40,40), 14, anchor_x="center")

        # Buttons: Play, Settings, Exit
        btn_w, btn_h = 260, 48
        mid_x = SCREEN_WIDTH/2
        start_y = SCREEN_HEIGHT/2 + 40
        play_y = start_y
        settings_y = start_y - 80
        exit_y = start_y - 160

        # Draw Play button (has submenu for difficulty)
        self.draw_button(mid_x, play_y, btn_w, btn_h, "Play")
        self.draw_button(mid_x, settings_y, btn_w, btn_h, "Settings")
        self.draw_button(mid_x, exit_y, btn_w, btn_h, "Exit")

        # small hint
        arcade.draw_text("Click Play to choose difficulty", SCREEN_WIDTH/2, exit_y - 60, (90,90,90), 12, anchor_x="center")

    def draw_settings_menu(self):
        title_y = SCREEN_HEIGHT - 110
        arcade.draw_text("Settings", SCREEN_WIDTH/2, title_y, GRID_COLOR, 36, anchor_x="center", bold=True)

        mid_x = SCREEN_WIDTH/2
        start_y = SCREEN_HEIGHT/2 + 20
        btn_w, btn_h = 320, 48
        bgm_y = start_y
        sfx_y = start_y - 80
        back_y = start_y - 200

        self.draw_button(mid_x, bgm_y, btn_w, btn_h, f"BGM: {'On' if self.bgm_on else 'Off'}")
        self.draw_button(mid_x, sfx_y, btn_w, btn_h, f"SFX: {'On' if self.sfx_on else 'Off'}")
        self.draw_button(mid_x, back_y, 180, 44, "Back")

        arcade.draw_text("Toggle background music and sound effects.", mid_x, sfx_y - 80, (70,70,70), 12, anchor_x="center")

    def draw_difficulty_menu(self):
        title_y = SCREEN_HEIGHT - 110
        arcade.draw_text("Difficulty", SCREEN_WIDTH/2, title_y, GRID_COLOR, 36, anchor_x="center", bold=True)

        mid_x = SCREEN_WIDTH/2
        start_y = SCREEN_HEIGHT/2 + 20
        btn_w, btn_h = 220, 48
        easy_y = start_y
        hard_y = start_y - 80
        back_y = start_y - 200

        self.draw_button(mid_x, easy_y, btn_w, btn_h, "Easy (AI: Depth 2)")
        self.draw_button(mid_x, hard_y, btn_w, btn_h, "Difficult (AI: Depth 4)")
        self.draw_button(mid_x, back_y, 180, 44, "Back")

        arcade.draw_text("Easy = faster but weaker AI. Difficult = stronger.", mid_x, hard_y - 80, (70,70,70), 12, anchor_x="center")

    # ----- Board + UI (in-game) -----
    def draw_board(self):
        anim_overlays = {"move": [], "drop": []}
        for anim in self.animations:
            if anim['type'] == 'move':
                anim_overlays['move'].append(anim)
            elif anim['type'] == 'drop':
                anim_overlays['drop'].append(anim)

        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                x = BOARD_OFFSET_X + col * CELL_SIZE + CELL_SIZE/2
                y = BOARD_OFFSET_Y + (BOARD_SIZE - 1 - row) * CELL_SIZE + CELL_SIZE/2

                cell_color = CELL_COLOR
                if (row, col) in self.possible_moves:
                    cell_color = POSSIBLE_MOVE_COLOR
                elif (row, col) in self.possible_builds:
                    cell_color = BUILD_COLOR

                arcade.draw_rectangle_filled(x, y, CELL_SIZE-6, CELL_SIZE-6, cell_color)
                arcade.draw_rectangle_outline(x, y, CELL_SIZE-6, CELL_SIZE-6, GRID_COLOR, 2)

                height = self.board.get_height(row, col)
                if height > 0:
                    for level in range(min(height, 3)):
                        block_size = CELL_SIZE - 26 - level * 10
                        block_y = y - (CELL_SIZE/2 - 20) + level * 18
                        arcade.draw_rectangle_filled(x, block_y, block_size, block_size*0.6, BLOCK_COLORS[level])
                        arcade.draw_rectangle_outline(x, block_y, block_size, block_size*0.6, GRID_COLOR, 1)
                if height >= 4:
                    dome_y = y + (CELL_SIZE/2 - 22)
                    arcade.draw_circle_filled(x, dome_y, 24, DOME_COLOR)
                    arcade.draw_circle_outline(x, dome_y, 24, GRID_COLOR, 2)

                worker_id = self.board.has_worker(row, col)

                skip_static = False
                for anim in anim_overlays['move']:
                    if tuple(anim.get('from', (-1,-1))) == (row,col):
                        skip_static = True
                        break
                for anim in anim_overlays['move']:
                    if tuple(anim.get('to', (-2,-2))) == (row,col):
                        skip_static = True
                        break

                if worker_id > 0 and not skip_static:
                    ped_y = y + (min(height,3) * 18) - 6
                    arcade.draw_ellipse_filled(x, ped_y - 6, CELL_SIZE*0.5, 18*0.6, (0,0,0,40))
                    worker_color = PLAYER1_COLOR if worker_id == 1 else PLAYER2_COLOR
                    radius = 26
                    if self.selected_worker == (row, col):
                        arcade.draw_circle_filled(x, ped_y + 10, radius+6, SELECTED_COLOR)
                    arcade.draw_circle_filled(x, ped_y + 10, radius, worker_color)
                    arcade.draw_circle_outline(x, ped_y + 10, radius, GRID_COLOR, 3)
                    symbol = "A" if worker_id == 1 else "B"
                    arcade.draw_text(symbol, x, ped_y + 4, GRID_COLOR, 18, anchor_x="center", anchor_y="center", bold=True)

        for anim in list(self.animations):
            if anim['type'] == 'move':
                frac = min(1.0, anim['t'] / anim['dur'])
                sx, sy = self.cell_center_pixel(anim['from'][0], anim['from'][1])
                tx, ty = self.cell_center_pixel(anim['to'][0], anim['to'][1])
                lift = math.sin(frac*math.pi) * 18
                cx = sx + (tx - sx) * frac
                cy = sy + (ty - sy) * frac + lift
                radius = 26
                color = PLAYER1_COLOR if anim['player']==1 else PLAYER2_COLOR
                arcade.draw_ellipse_filled(cx, cy - 6, CELL_SIZE*0.5, 18*0.6, (0,0,0,40))
                arcade.draw_circle_filled(cx, cy + 10, radius, color)
                arcade.draw_circle_outline(cx, cy + 10, radius, GRID_COLOR, 3)
                arcade.draw_text("A" if anim['player']==1 else "B", cx, cy + 4, GRID_COLOR, 18, anchor_x="center", anchor_y="center", bold=True)

            elif anim['type'] == 'drop':
                frac = min(1.0, anim['t'] / anim['dur'])
                tx, ty = self.cell_center_pixel(anim['to'][0], anim['to'][1])
                drop_y = ty + (1.0 - frac) * 80
                color = PLAYER1_COLOR if anim['player']==1 else PLAYER2_COLOR
                radius = 26 * (0.8 + 0.2*frac)
                arcade.draw_ellipse_filled(tx, drop_y - 6, CELL_SIZE*0.5, 18*0.6, (0,0,0,30))
                arcade.draw_circle_filled(tx, drop_y + 10, radius, color)
                arcade.draw_circle_outline(tx, drop_y + 10, radius, GRID_COLOR, 3)
                arcade.draw_text("A" if anim['player']==1 else "B", tx, drop_y + 4, GRID_COLOR, 18, anchor_x="center", anchor_y="center", bold=True)

    def draw_ui(self):
        panel_left = UI_PANEL_X
        panel_right = UI_PANEL_X + UI_PANEL_WIDTH
        panel_top = SCREEN_HEIGHT - PADDING
        panel_bottom = PADDING
        arcade.draw_lrtb_rectangle_filled(panel_left, panel_right, panel_top, panel_bottom, UI_BG)
        arcade.draw_lrtb_rectangle_outline(panel_left, panel_right, panel_top, panel_bottom, GRID_COLOR, 2)
        arcade.draw_text("Santorini", panel_left + 16, panel_top - 28, GRID_COLOR, self.ui_title_size, bold=True)
        status_y = panel_top - 70
        if self.game_state == GameState.SETUP:
            status_text = f"Setup — place worker {self.workers_placed + 1}/4"
        elif self.game_state == GameState.PLAYER_MOVE:
            status_text = f"Player {self.current_player} — Select worker"
        elif self.game_state == GameState.PLAYER_BUILD:
            status_text = f"Player {self.current_player} — Choose build location"
        elif self.game_state == GameState.AI_THINKING:
            status_text = "AI thinking..."
        elif self.game_state == GameState.GAME_OVER:
            status_text = f"Game Over! Player {self.winner} wins!"
        else:
            status_text = ""
        arcade.draw_text(status_text, panel_left + 16, status_y, GRID_COLOR, self.ui_text_size)
        instr_y = status_y - 36
        instructions = [
            "Left click: Select / Move / Build",
            "Right click: Deselect",
        ]
        for i, t in enumerate(instructions):
            arcade.draw_text(t, panel_left + 16, instr_y - i*20, (60,60,60), 12)
        # Legend
        legend_y = instr_y - 80
        arcade.draw_text("Legend", panel_left + 16, legend_y, GRID_COLOR, 14, bold=True)
        arcade.draw_rectangle_filled(panel_left + 36, legend_y - 28, 24, 16, PLAYER1_COLOR)
        arcade.draw_text("Human (You)", panel_left + 56, legend_y - 34, (40,40,40), 12)
        arcade.draw_rectangle_filled(panel_left + 36, legend_y - 58, 24, 16, PLAYER2_COLOR)
        arcade.draw_text("AI", panel_left + 56, legend_y - 64, (40,40,40), 12)
        # Counts
        counts_y = legend_y - 110
        blocks = sum(1 for r in range(BOARD_SIZE) for c in range(BOARD_SIZE) if 1 <= self.board.board[r][c] <= 3)
        domes = sum(1 for r in range(BOARD_SIZE) for c in range(BOARD_SIZE) if self.board.board[r][c] >= 4)
        arcade.draw_text(f"Built Blocks: {blocks}", panel_left + 16, counts_y, (40,40,40), 12)
        arcade.draw_text(f"Domes: {domes}", panel_left + 16, counts_y - 22, (40,40,40), 12)

        # Restart (outside popup)
        restart_x = panel_left + UI_PANEL_WIDTH/2
        restart_y = panel_bottom + 36
        self.draw_button(restart_x, restart_y, 140, 40, "Restart")

    # ----- Game Over popup -----
    def draw_game_over_popup(self):
        # semi-transparent overlay
        arcade.draw_lrtb_rectangle_filled(0, self.width, self.height, 0, (0,0,0,120))
        box_w = 380
        box_h = 200
        cx = self.width/2
        cy = self.height/2
        # popup background
        arcade.draw_rectangle_filled(cx, cy, box_w, box_h, (245,245,245,240))
        arcade.draw_rectangle_outline(cx, cy, box_w, box_h, GRID_COLOR, 3)
        # title & text
        title = "Game Over"
        subtitle = f"Player {self.winner} wins!"
        arcade.draw_text(title, cx, cy + 50, GRID_COLOR, 28, anchor_x="center", bold=True)
        arcade.draw_text(subtitle, cx, cy + 16, (60,60,60), 16, anchor_x="center")
        # Buttons: Restart and Main Menu
        btn_w = 140
        btn_h = 40
        restart_x = cx - 90
        mainmenu_x = cx + 90
        btn_y = cy - 50
        self.draw_button(restart_x, btn_y, btn_w, btn_h, "Restart")
        self.draw_button(mainmenu_x, btn_y, btn_w, btn_h, "Main Menu")

        # store popup button rects for click handling
        self._popup_restart_rect = (restart_x, btn_y, btn_w, btn_h)
        self._popup_mainmenu_rect = (mainmenu_x, btn_y, btn_w, btn_h)

    # ----- Input handling -----
    def on_mouse_press(self, x:int, y:int, button:int, modifiers:int):
        if self.game_state == GameState.MAIN_MENU:
            self.handle_main_menu_click(x,y)
            return
        elif self.game_state == GameState.SETTINGS_MENU:
            self.handle_settings_menu_click(x,y)
            return
        elif self.game_state == GameState.DIFFICULTY_MENU:
            self.handle_difficulty_menu_click(x,y)
            return

        # If game over, check popup buttons first
        if self.game_state == GameState.GAME_OVER:
            # popup buttons exist only when popup was drawn; guard with hasattr
            if hasattr(self, "_popup_restart_rect"):
                rx, ry, rw, rh = self._popup_restart_rect
                if self.button_hit(rx, ry, rw, rh, x, y):
                    self.restart_game()
                    return
            if hasattr(self, "_popup_mainmenu_rect"):
                mx, my, mw, mh = self._popup_mainmenu_rect
                if self.button_hit(mx, my, mw, mh, x, y):
                    # return to main menu and stop outro music; keep settings
                    self.game_state = GameState.MAIN_MENU
                    try:
                        if self.outro_player:
                            self.outro_player.pause()
                            self.outro_player.next_source()
                    except Exception:
                        pass
                    # Resume main bgm if enabled
                    if self.bgm_on and self.music_player:
                        try:
                            self.music_player.play()
                        except Exception:
                            pass
                    return

        if button == arcade.MOUSE_BUTTON_LEFT:
            row, col = self.screen_to_board(x,y)
            if row is not None and col is not None:
                self.handle_click(row, col)
                return

            # check Restart button region (outside popup)
            panel_left = UI_PANEL_X
            restart_x = panel_left + UI_PANEL_WIDTH/2
            restart_y = PADDING + 36
            if self.button_hit(restart_x, restart_y, 140, 40, x, y):
                self.restart_game()
        elif button == arcade.MOUSE_BUTTON_RIGHT:
            self.selected_worker = None
            self.possible_moves = []
            self.possible_builds = []

    # Menu click handlers
    def handle_main_menu_click(self, x, y):
        btn_w, btn_h = 260, 48
        mid_x = SCREEN_WIDTH/2
        start_y = SCREEN_HEIGHT/2 + 40
        play_y = start_y
        settings_y = start_y - 80
        exit_y = start_y - 160
        if self.button_hit(mid_x, play_y, btn_w, btn_h, x, y):
            self.game_state = GameState.DIFFICULTY_MENU
        elif self.button_hit(mid_x, settings_y, btn_w, btn_h, x, y):
            self.game_state = GameState.SETTINGS_MENU
        elif self.button_hit(mid_x, exit_y, btn_w, btn_h, x, y):
            arcade.close_window()

    def handle_settings_menu_click(self, x, y):
        mid_x = SCREEN_WIDTH/2
        start_y = SCREEN_HEIGHT/2 + 20
        btn_w, btn_h = 320, 48
        bgm_y = start_y
        sfx_y = start_y - 80
        back_y = start_y - 200
        if self.button_hit(mid_x, bgm_y, btn_w, btn_h, x, y):
            self.toggle_bgm()
        elif self.button_hit(mid_x, sfx_y, btn_w, btn_h, x, y):
            self.toggle_sfx()
        elif self.button_hit(mid_x, back_y, 180, 44, x, y):
            self.game_state = GameState.MAIN_MENU

    def handle_difficulty_menu_click(self, x, y):
        mid_x = SCREEN_WIDTH/2
        start_y = SCREEN_HEIGHT/2 + 20
        btn_w, btn_h = 220, 48
        easy_y = start_y
        hard_y = start_y - 80
        back_y = start_y - 200
        if self.button_hit(mid_x, easy_y, btn_w, btn_h, x, y):
            self.ai_difficulty_depth = 2
            self.start_new_game_with_selected_difficulty()
        elif self.button_hit(mid_x, hard_y, btn_w, btn_h, x, y):
            self.ai_difficulty_depth = 4
            self.start_new_game_with_selected_difficulty()
        elif self.button_hit(mid_x, back_y, 180, 44, x, y):
            self.game_state = GameState.MAIN_MENU

    def start_new_game_with_selected_difficulty(self):
        # initialize a fresh game and set AI depth
        self.reset_game_state(minimal=False)
        self.ai = SantoriniAI(2, depth=self.ai_difficulty_depth)
        self.game_state = GameState.SETUP
        # ensure main bgm is playing if enabled
        if self.bgm_on and self.music_player:
            try:
                self.music_player.play()
            except Exception:
                pass

    # Game click handlers (in-game)
    def handle_click(self, row:int, col:int):
        if self.game_state == GameState.SETUP:
            self.handle_setup_click(row, col)
        elif self.game_state == GameState.PLAYER_MOVE and self.current_player == 1:
            self.handle_move_click(row, col)
        elif self.game_state == GameState.PLAYER_BUILD and self.current_player == 1:
            self.handle_build_click(row, col)

    def handle_setup_click(self, row:int, col:int):
        if self.current_player == 1 and len(self.player1.workers) >= MAX_WORKERS_PER_PLAYER: return
        if self.current_player == 2 and len(self.player2.workers) >= MAX_WORKERS_PER_PLAYER: return
        if self.board.place_worker(row, col, self.current_player):
            anim = {'type':'drop', 'player':self.current_player, 'to':(row,col), 't':0.0, 'dur':0.35, 'on_complete':None}
            self.animations.append(anim)
            self.play_sfx('place')
            if self.current_player == 1:
                self.player1.workers.append((row,col))
            else:
                self.player2.workers.append((row,col))
            self.workers_placed += 1
            if self.workers_placed >= MAX_WORKERS_PER_PLAYER * 2:
                self.game_state = GameState.PLAYER_MOVE
                self.current_player = 1
            else:
                self.current_player = 2 if self.current_player == 1 else 1
                if self.current_player == 2:
                    self.ai_place_worker()

    def ai_place_worker(self):
        if len(self.player2.workers) >= MAX_WORKERS_PER_PLAYER: return
        empties=[]
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if self.board.workers[r][c]==0:
                    empties.append((r,c))
        if empties:
            r,c = random.choice(empties)
            if self.board.place_worker(r,c,2):
                anim = {'type':'drop', 'player':2, 'to':(r,c), 't':0.0, 'dur':0.35, 'on_complete':None}
                self.animations.append(anim)
                self.play_sfx('place')
                self.player2.workers.append((r,c))
                self.workers_placed += 1
                self.current_player = 1
                if self.workers_placed >= MAX_WORKERS_PER_PLAYER * 2:
                    self.game_state = GameState.PLAYER_MOVE

    def handle_move_click(self, row:int, col:int):
        if self.board.has_worker(row,col) == self.current_player:
            self.selected_worker = (row,col)
            self.possible_moves = self.board.get_possible_moves(row,col)
            self.possible_builds = []
        elif self.selected_worker and (row,col) in self.possible_moves:
            oldr,oldc = self.selected_worker
            moved = self.board.move_worker(oldr,oldc,row,col)
            if moved:
                anim = {'type':'move', 'player':self.current_player, 'from':(oldr,oldc), 'to':(row,col), 't':0.0, 'dur':0.28, 'on_complete':None}
                self.animations.append(anim)
                self.rebuild_player_workers_from_board()
                self.play_sfx('move')
                if self.board.get_height(row,col) == 3:
                    # declare winner and play outro music
                    self.winner = self.current_player
                    anim['on_complete'] = lambda: self.declare_winner(self.current_player)
                    self.game_state = GameState.GAME_OVER
                    return
                anim['on_complete'] = lambda r=row, c=col: self.start_build_phase(r,c)
                self.selected_worker = (row,col)
                self.possible_moves = []
                self.possible_builds = []
                self.move_made = True

    def start_build_phase(self, row:int, col:int):
        self.possible_builds = self.board.get_possible_builds(row,col)
        self.game_state = GameState.PLAYER_BUILD

    def handle_build_click(self, row:int, col:int):
        if self.selected_worker and (row,col) in self.possible_builds:
            if self.board.build(row,col):
                self.play_sfx('build')
                self.selected_worker = None
                self.possible_moves = []
                self.possible_builds = []
                self.end_turn()

    def declare_winner(self, pid:int):
        self.winner = pid
        # play small fx and then play extended outro music for win/loss
        self.play_sfx('win')
        self.play_outro_music(pid)
        self.game_state = GameState.GAME_OVER

    def end_turn(self):
        self.current_player = 2 if self.current_player == 1 else 1
        self.move_made = False
        if self.current_player == 2:
            self.game_state = GameState.AI_THINKING
        else:
            self.game_state = GameState.PLAYER_MOVE

    def on_update(self, delta_time: float):
        to_remove=[]
        for anim in self.animations:
            anim['t'] += delta_time
            if anim['t'] >= anim['dur']:
                if anim.get('on_complete'):
                    try:
                        anim['on_complete']()
                    except Exception as e:
                        print("Anim on_complete error:", e)
                to_remove.append(anim)
        for a in to_remove:
            if a in self.animations:
                self.animations.remove(a)

        if self.game_state == GameState.AI_THINKING:
            if not self.animations:
                self.ai_make_move()

    def ai_make_move(self):
        self.rebuild_player_workers_from_board()
        # make sure AI has the selected depth
        self.ai.depth = self.ai_difficulty_depth
        best = self.ai.get_best_move(self.board)
        if best:
            (orow,ocol),(nrow,ncol),build = best
            moved = self.board.move_worker(orow,ocol,nrow,ncol)
            if moved:
                anim = {'type':'move','player':2,'from':(orow,ocol),'to':(nrow,ncol),'t':0.0,'dur':0.35,'on_complete':None}
                if self.board.get_height(nrow,ncol) == 3:
                    anim['on_complete'] = lambda: self.declare_winner(2)
                else:
                    def after_move_build(br=build, nrow=nrow, ncol=ncol):
                        if br:
                            br_r, br_c = br
                            if self.board.can_build(nrow,ncol,br_r,br_c):
                                self.board.build(br_r,br_c)
                                self.play_sfx('build')
                        self.rebuild_player_workers_from_board()
                        self.end_turn()
                    anim['on_complete'] = after_move_build
                self.animations.append(anim)
                self.rebuild_player_workers_from_board()
                self.play_sfx('move')
            else:
                self.end_turn()
        else:
            # If AI has no moves, human wins
            self.declare_winner(1)

    # ----- Helpers -----
    def cell_center_pixel(self, row:int, col:int) -> Tuple[float,float]:
        x = BOARD_OFFSET_X + col * CELL_SIZE + CELL_SIZE/2
        y = BOARD_OFFSET_Y + (BOARD_SIZE - 1 - row) * CELL_SIZE + CELL_SIZE/2
        return x, y

    def screen_to_board(self, x:int, y:int) -> Tuple[Optional[int], Optional[int]]:
        if (BOARD_OFFSET_X <= x <= BOARD_OFFSET_X + BOARD_PIXEL_SIZE and
            BOARD_OFFSET_Y <= y <= BOARD_OFFSET_Y + BOARD_PIXEL_SIZE):
            col = int((x - BOARD_OFFSET_X) // CELL_SIZE)
            row = BOARD_SIZE - 1 - int((y - BOARD_OFFSET_Y) // CELL_SIZE)
            if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE:
                return row, col
        return None, None

    # ----- Restart -----
    def restart_game(self):
        # Stop outro music if playing
        try:
            if self.outro_player:
                self.outro_player.pause()
                self.outro_player.next_source()
        except Exception:
            pass

        # Reset game state
        self.reset_game_state(minimal=False)
        self.ai = SantoriniAI(2, depth=self.ai_difficulty_depth)

        # Restart main bgm if enabled
        if self.bgm_on:
            # reload or resume
            if self.music_player:
                try:
                    self.music_player.play()
                except Exception:
                    pass
            else:
                # try to start it
                if os.path.exists(BACKGROUND_MUSIC):
                    try:
                        src = pyglet.media.load(BACKGROUND_MUSIC)
                        player = pyglet.media.Player()
                        player.queue(src)
                        player.loop = True
                        player.volume = 0.25
                        player.play()
                        self.music_player = player
                    except Exception as e:
                        print("Failed to start bgm on restart:", e)

# ----- Entrypoint -----
def main():
    game = SantoriniGame()
    arcade.run()

if __name__ == "__main__":
    main()
