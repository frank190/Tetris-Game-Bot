from copy import deepcopy
from random import randrange as rand
import pygame, sys
import random

# The configuration
cell_size = 30
cols = 10
rows = 22
maxfps = 60

colors = [
    (0, 0, 0),
    (220, 0, 20),
    (60, 165, 50),
    (100, 100, 255),
    (255, 90, 0),
    (255, 200, 40),
    (160, 50, 210),
    (70, 230, 210),
    (35, 35, 35)  # Helper color for background grid
]

# Define the shapes of the single parts
tetris_shapes = [
    [[1, 1, 1],
     [0, 1, 0]],

    [[0, 2, 2],
     [2, 2, 0]],

    [[3, 3, 0],
     [0, 3, 3]],

    [[4, 0, 0],
     [4, 4, 4]],

    [[0, 0, 5],
     [5, 5, 5]],

    [[6, 6, 6, 6]],

    [[7, 7],
     [7, 7]]
]

seven_bag = True
ai = True
bags = []


def rotate_clockwise(shape):
    return [[shape[y][x]
             for y in range(len(shape))]
            for x in range(len(shape[0]) - 1, -1, -1)]


def check_collision(board, shape, offset):
    off_x, off_y = offset
    for cy, row in enumerate(shape):
        for cx, cell in enumerate(row):
            try:
                if cell and board[cy + off_y][cx + off_x]:
                    return True
            except IndexError:
                return True
    return False


def remove_row(board, row):
    del board[row]
    return [[0 for i in range(cols)]] + board


def join_matrixes(mat1, mat2, mat2_off):
    off_x, off_y = mat2_off
    for cy, row in enumerate(mat2):
        for cx, val in enumerate(row):
            mat1[cy + off_y - 1][cx + off_x] += val
    return mat1


def new_board():
    board = [[0 for x in range(cols)]
             for y in range(rows)]
    board += [[1 for x in range(cols)]]

    return board


def score_calculation(board):
    # Ref: https://codemyroad.wordpress.com/2013/04/14/tetris-ai-the-near-perfect-player/
    score = 0
    height_sum = 0
    hole_sum = 0
    bumpiness_sum = 0
    clear_sum = 0

    # Height_sum
    for j in range(len(board[0])):
        height_col = 22
        for i in range(len(board)):
            if board[i][j] == 0:
                height_col -= 1
            else:
                break
        height_sum += height_col

    # Hole_sum

    # Bumpiness_sum

    # Clear_sum
    for j in range(len(board[0])):
        c_flag = True
        for i in range (len(board)):
            if board[i][j] != 0:
                continue
            else:
                c_flag = False
                break
        if c_flag:
            clear_sum += 1
    clear_sum -= 1

    coeff = [-0.510066, 0.760666, -0.35665, -0.184483]

    score = coeff[0] * height_sum + coeff[1] * clear_sum + coeff[2] * hole_sum + coeff[3] * bumpiness_sum

    return score


class TetrisApp(object):
    # Game Window Initialization
    def __init__(self):
        pygame.init()
        pygame.key.set_repeat(250, 25)
        self.width = cell_size * (cols + 6)
        self.height = cell_size * rows
        self.rlim = cell_size * cols
        self.bground_grid = [[8 if x % 2 == y % 2 else 0 for x in range(cols)] for y in range(rows)]

        self.default_font = pygame.font.Font(
            pygame.font.get_default_font(), 12)

        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.event.set_blocked(pygame.MOUSEMOTION)  # We do not need
        # mouse movement
        # events, so we
        # block them.
        self.next_stone = tetris_shapes[rand(len(tetris_shapes))]
        self.init_game()

    def new_stone(self):
        self.stone = self.next_stone[:]
        global bags
        if len(bags) == 0:
            bags = [0, 1, 2, 3, 4, 5, 6]
            random.shuffle(bags)

        if not seven_bag:
            self.next_stone = tetris_shapes[rand(len(tetris_shapes))]
        else:
            self.next_stone = tetris_shapes[bags.pop(0)]

        self.stone_x = int(cols / 2 - len(self.stone[0]) / 2)
        self.stone_y = 0

        if check_collision(self.board,
                           self.stone,
                           (self.stone_x, self.stone_y)):
            self.gameover = True

    def init_game(self):
        self.board = new_board()
        self.new_stone()
        self.level = 1
        self.score = 0
        self.lines = 0
        pygame.time.set_timer(pygame.USEREVENT + 1, 1000)

    def disp_msg(self, msg, topleft):
        x, y = topleft
        for line in msg.splitlines():
            self.screen.blit(
                self.default_font.render(
                    line,
                    False,
                    (255, 255, 255),
                    (0, 0, 0)),
                (x, y))
            y += 14

    def center_msg(self, msg):
        for i, line in enumerate(msg.splitlines()):
            msg_image = self.default_font.render(line, False,
                                                 (255, 255, 255), (0, 0, 0))

            msgim_center_x, msgim_center_y = msg_image.get_size()
            msgim_center_x //= 2
            msgim_center_y //= 2

            self.screen.blit(msg_image, (
                self.width // 2 - msgim_center_x,
                self.height // 2 - msgim_center_y + i * 22))

    def draw_matrix(self, matrix, offset):
        off_x, off_y = offset
        for y, row in enumerate(matrix):
            for x, val in enumerate(row):
                if val:
                    pygame.draw.rect(
                        self.screen,
                        colors[val],
                        pygame.Rect(
                            (off_x + x) *
                            cell_size,
                            (off_y + y) *
                            cell_size,
                            cell_size,
                            cell_size), 0)

    def add_cl_lines(self, n):
        linescores = [0, 40, 100, 300, 1200]
        self.lines += n
        self.score += linescores[n] * self.level
        if self.lines >= self.level * 6:
            self.level += 1
            newdelay = 1000 - 50 * (self.level - 1)
            newdelay = 100 if newdelay < 100 else newdelay
            pygame.time.set_timer(pygame.USEREVENT + 1, newdelay)

    def move(self, delta_x):
        if not self.gameover and not self.paused:
            new_x = self.stone_x + delta_x
            if new_x < 0:
                new_x = 0
            if new_x > cols - len(self.stone[0]):
                new_x = cols - len(self.stone[0])
            if not check_collision(self.board,
                                   self.stone,
                                   (new_x, self.stone_y)):
                self.stone_x = new_x

    def quit(self):
        self.center_msg("Exiting...")
        pygame.display.update()
        sys.exit()

    def drop(self, manual):
        if not self.gameover and not self.paused:
            self.score += 1 if manual else 0
            self.stone_y += 1
            if check_collision(self.board,
                               self.stone,
                               (self.stone_x, self.stone_y)):
                self.board = join_matrixes(
                    self.board,
                    self.stone,
                    (self.stone_x, self.stone_y))
                self.new_stone()
                cleared_rows = 0
                while True:
                    for i, row in enumerate(self.board[:-1]):
                        if 0 not in row:
                            self.board = remove_row(
                                self.board, i)
                            cleared_rows += 1
                            break
                    else:
                        break
                self.add_cl_lines(cleared_rows)
                return True
        return False

    def insta_drop(self):
        if not self.gameover and not self.paused:
            while not self.drop(True):
                pass

    def rotate_stone(self):
        if not self.gameover and not self.paused:
            new_stone = rotate_clockwise(self.stone)
            if not check_collision(self.board,
                                   new_stone,
                                   (self.stone_x, self.stone_y)):
                self.stone = new_stone

    def toggle_pause(self):
        self.paused = not self.paused
        for l in self.board:
            print(l)

    def start_game(self):
        if self.gameover:
            self.init_game()
            self.gameover = False

    def ai_calculate(self):
        board_me = deepcopy(self.board)

        x = 0
        y_start = self.stone_y
        for y in range(y_start, len(self.board)):
            if not check_collision(board_me, self.stone, (x, y)):
                continue
            else:
                y_now = y - 1
        board_me = join_matrixes(board_me, self.stone, (x, y))
        score_calculation(board_me)

    def run(self):
        global ai
        key_actions = {
            'ESCAPE': self.quit,
            'LEFT': lambda: self.move(-1),
            'RIGHT': lambda: self.move(+1),
            'DOWN': lambda: self.drop(True),
            'UP': self.rotate_stone,
            'p': self.toggle_pause,
            'SPACE': self.start_game,
            'RETURN': self.insta_drop
        }

        self.gameover = False
        self.paused = False

        dont_burn_my_cpu = pygame.time.Clock()
        while 1:
            self.screen.fill((0, 0, 0))
            if self.gameover:
                self.center_msg("""Game Over!
Press space to continue""")
            else:
                if self.paused:
                    self.center_msg("Paused")
                else:

                    pygame.draw.line(self.screen,
                                     (255, 255, 255),
                                     (self.rlim + 1, 0),
                                     (self.rlim + 1, self.height - 1))
                    self.disp_msg("Next:", (
                        self.rlim + cell_size,
                        2))
                    self.disp_msg("Lines: %d" % (self.lines),
                                  (self.rlim + cell_size, cell_size * 5))
                    if ai:
                        print(score_calculation(self.board))

                    self.draw_matrix(self.bground_grid, (0, 0))
                    self.draw_matrix(self.board, (0, 0))
                    self.draw_matrix(self.stone,
                                     (self.stone_x, self.stone_y))
                    self.draw_matrix(self.next_stone,
                                     (cols + 1, 2))
            pygame.display.update()
            for event in pygame.event.get():
                if event.type == pygame.USEREVENT + 1:
                    self.drop(False)
                elif event.type == pygame.QUIT:
                    self.quit()
                elif event.type == pygame.KEYDOWN:
                    for key in key_actions:
                        if event.key == eval("pygame.K_"
                                             + key):
                            key_actions[key]()

            dont_burn_my_cpu.tick(maxfps)


if __name__ == '__main__':
    App = TetrisApp()
    App.run()
