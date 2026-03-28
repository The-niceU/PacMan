import math
import os
import random
import time

import pygame


# 基本设置
TILE = 24
ROWS = 21
COLS = 19
SCREEN_W = COLS * TILE
SCREEN_H = ROWS * TILE + 40
ASSET_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'images'))

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 200, 0)
RED = (220, 30, 30)
BLUE = (80, 160, 255)
WALL_COLOR = (0, 200, 255)
PELLET_COLOR = (245, 215, 60)
HUD_BG = (15, 15, 35)
HUD_TEXT = (200, 220, 255)
WALL_LINE_THICKNESS = 6
WALL_LINE_PADDING = 4
INVULNERABLE_DURATION = 1.5


class AssetManager:
    """负责加载 images 文件夹下的全部贴图资源。"""

    def __init__(self, tile_size: int):
        if not os.path.isdir(ASSET_DIR):
            raise FileNotFoundError(f'找不到资源目录: {ASSET_DIR}')
        self.tile_size = tile_size
        self._cache = {}
        self.pacman_frames = self._build_pacman_frames()
        self.ghost_frames = self._build_ghost_frames()
        self.fruit = self._load('FrightFruit.png', (tile_size - 6, tile_size - 6))
        self.life_icon = pygame.transform.smoothscale(
            self._load('PacMan3right.gif'), (tile_size - 4, tile_size - 4)
        )

    def _load(self, filename, scale=None):
        path = os.path.join(ASSET_DIR, filename)
        if not os.path.exists(path):
            raise FileNotFoundError(f'缺少资源文件: {filename}')
        key = (filename, scale)
        if key not in self._cache:
            surf = pygame.image.load(path).convert_alpha()
            if scale:
                surf = pygame.transform.smoothscale(surf, scale)
            self._cache[key] = surf
        return self._cache[key]

    def _build_pacman_frames(self):
        mapping = {
            'right': ['PacMan1.gif', 'PacMan2right.gif', 'PacMan3right.gif', 'PacMan4right.gif'],
            'left': ['PacMan1.gif', 'PacMan2left.gif', 'PacMan3left.gif', 'PacMan4left.gif'],
            'up': ['PacMan1.gif', 'PacMan2up.gif', 'PacMan3up.gif', 'PacMan4up.gif'],
            'down': ['PacMan1.gif', 'PacMan2down.gif', 'PacMan3down.gif', 'PacMan4down.gif'],
        }
        frames = {}
        for direction, names in mapping.items():
            frames[direction] = [self._load(name, (self.tile_size, self.tile_size)) for name in names]
        return frames

    def _build_ghost_frames(self):
        normal = [
            self._load('Ghost1.gif', (self.tile_size, self.tile_size)),
            self._load('Ghost2.gif', (self.tile_size, self.tile_size)),
        ]
        scared = [
            self._load('GhostScared1.gif', (self.tile_size, self.tile_size)),
            self._load('GhostScared2.gif', (self.tile_size, self.tile_size)),
        ]
        return {'normal': normal, 'scared': scared}


class Entity:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class PacMan(Entity):
    def __init__(self, x, y, frames):
        super().__init__(x, y)
        self.vx = 0
        self.vy = 0
        self.speed = 2.5
        self.radius = TILE // 2 - 2
        self.frames = frames
        self.direction = 'right'
        self.anim_index = 0
        self.anim_timer = 0
        self.anim_delay = 0.08
        self.next_dir = None
        self.snap_threshold = TILE // 3

    def set_velocity(self, vx, vy, walls=None):
        direction = (vx, vy)
        if direction == (self.vx, self.vy):
            return
        self.next_dir = direction
        if walls is not None:
            self._try_turn(walls)

    def force_direction(self, vx, vy):
        self._apply_direction((vx, vy))
        self.next_dir = None

    def reset_state(self, position):
        self.x, self.y = position
        self.vx = 0
        self.vy = 0
        self.next_dir = None
        self.direction = 'right'
        self.anim_index = 0

    def update(self, walls, dt):
        self._try_turn(walls)
        nx = self.x + self.vx * self.speed
        ny = self.y + self.vy * self.speed
        if not collide_walls(nx, self.y, walls):
            self.x = nx
        if not collide_walls(self.x, ny, walls):
            self.y = ny
        self._animate(dt)

    def _try_turn(self, walls):
        if not self.next_dir:
            return
        vx, vy = self.next_dir

        if self._can_move(vx, vy, walls):
            self._apply_direction(self.next_dir)
            self.next_dir = None
            return

        if vx != 0:
            self._snap_axis('y')
        if vy != 0:
            self._snap_axis('x')
        if self._can_move(vx, vy, walls):
            self._apply_direction(self.next_dir)
            self.next_dir = None

    def _snap_axis(self, axis):
        if axis == 'x':
            target = self._grid_center(self.x)
            if abs(self.x - target) <= self.snap_threshold:
                self.x = target
        else:
            target = self._grid_center(self.y)
            if abs(self.y - target) <= self.snap_threshold:
                self.y = target

    def _grid_center(self, value):
        return round((value - TILE / 2) / TILE) * TILE + TILE / 2

    def _can_move(self, vx, vy, walls):
        test_x = self.x + vx * (self.speed + 4)
        test_y = self.y + vy * (self.speed + 4)
        return not collide_walls(test_x, test_y, walls)

    def _apply_direction(self, direction):
        self.vx, self.vy = direction
        if self.vx > 0:
            self.direction = 'right'
        elif self.vx < 0:
            self.direction = 'left'
        elif self.vy > 0:
            self.direction = 'down'
        elif self.vy < 0:
            self.direction = 'up'

    def _animate(self, dt):
        if self.vx == 0 and self.vy == 0:
            self.anim_timer = 0
            self.anim_index = 0
            return
        self.anim_timer += dt
        if self.anim_timer >= self.anim_delay:
            self.anim_timer = 0
            frames = self.frames[self.direction]
            self.anim_index = (self.anim_index + 1) % len(frames)

    def current_frame(self):
        return self.frames[self.direction][self.anim_index]


class Ghost(Entity):
    def __init__(self, x, y, frames):
        super().__init__(x, y)
        self.dir = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
        self.speed = 2.0
        self.scared = False
        self.respawn = False
        self.frames = frames
        self.anim_index = 0
        self.anim_timer = 0
        self.anim_delay = 0.12
        self.respawn_timer = 0

    def update(self, walls, pacman, dt):
        if self.respawn:
            if time.time() >= self.respawn_timer:
                self.respawn = False
                self.scared = False
            else:
                return
        if random.random() < 0.02:
            dx = pacman.x - self.x
            dy = pacman.y - self.y
            if abs(dx) > abs(dy):
                self.dir = (1 if dx > 0 else -1, 0)
            else:
                self.dir = (0, 1 if dy > 0 else -1)
        nx = self.x + self.dir[0] * self.speed
        ny = self.y + self.dir[1] * self.speed
        if collide_walls(nx, ny, walls):
            dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]
            random.shuffle(dirs)
            for d in dirs:
                if not collide_walls(self.x + d[0] * self.speed, self.y + d[1] * self.speed, walls):
                    self.dir = d
                    break
        else:
            self.x = nx
            self.y = ny
        self._animate(dt)

    def trigger_respawn(self):
        self.respawn = True
        self.respawn_timer = time.time() + 1.0

    def _animate(self, dt):
        self.anim_timer += dt
        frames = self.frames['scared'] if self.scared else self.frames['normal']
        if self.anim_timer >= self.anim_delay:
            self.anim_timer = 0
            self.anim_index = (self.anim_index + 1) % len(frames)

    def current_frame(self):
        frames = self.frames['scared'] if self.scared else self.frames['normal']
        return frames[self.anim_index]


def collide_walls(x, y, walls):
    rect = pygame.Rect(int(x - TILE / 2 + 2), int(y - TILE / 2 + 2), TILE - 4, TILE - 4)
    return any(rect.colliderect(w) for w in walls)


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption('PacMan - 期末大作业 原型')
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('arial', 24)
        self.score_font = pygame.font.SysFont('arial', 26, bold=True)
        self.assets = AssetManager(TILE)

        self.levels = [self._default_map(), self._level2_map()]
        self.level_index = 0
        self.score = 0
        self.lives = 3
        self.invulnerable_end = 0
        self.reset_level()

    def reset_level(self):
        self.map_data = self.levels[self.level_index]
        self.walls = []
        self.pellets = set()
        self.fright_fruits = set()
        self.ghosts = []
        self.spawn_points = []

        for r, row in enumerate(self.map_data):
            for c, ch in enumerate(row):
                x = c * TILE + TILE // 2
                y = r * TILE + TILE // 2
                if ch == '#':
                    self.walls.append(pygame.Rect(c * TILE, r * TILE, TILE, TILE))
                elif ch == '.':
                    self.pellets.add((c, r))
                elif ch == 'F':
                    self.fright_fruits.add((c, r))
                elif ch == 'G':
                    self.spawn_points.append((x, y))

        pac_start = self.spawn_points[-1] if self.spawn_points else (TILE + TILE // 2, TILE + TILE // 2)
        self.pac_start = pac_start
        self.pacman = PacMan(pac_start[0], pac_start[1], self.assets.pacman_frames)

        for sp in self.spawn_points[:4]:
            g = Ghost(sp[0], sp[1], self.assets.ghost_frames)
            g.appear_time = time.time() + random.uniform(0.5, 3.0)
            self.ghosts.append(g)

        if not self.spawn_points:
            self.spawn_points.append((pac_start[0], pac_start[1]))
        self.fright_end = 0
        self._build_maze_surface()
        self.invulnerable_end = 0

    def _build_maze_surface(self):
        self.maze_surface = pygame.Surface((SCREEN_W, ROWS * TILE), pygame.SRCALPHA)
        thickness = WALL_LINE_THICKNESS
        pad = WALL_LINE_PADDING

        def is_wall(rr, cc):
            return 0 <= rr < ROWS and 0 <= cc < COLS and self.map_data[rr][cc] == '#'

        for r in range(ROWS):
            for c in range(COLS):
                if self.map_data[r][c] != '#':
                    continue

                cell_left = c * TILE
                cell_top = r * TILE
                left = cell_left + pad
                right = cell_left + TILE - pad
                top = cell_top + pad
                bottom = cell_top + TILE - pad

                if not is_wall(r - 1, c):
                    pygame.draw.line(self.maze_surface, WALL_COLOR, (left, top), (right, top), thickness)
                if not is_wall(r + 1, c):
                    pygame.draw.line(self.maze_surface, WALL_COLOR, (left, bottom), (right, bottom), thickness)
                if not is_wall(r, c - 1):
                    pygame.draw.line(self.maze_surface, WALL_COLOR, (left, top), (left, bottom), thickness)
                if not is_wall(r, c + 1):
                    pygame.draw.line(self.maze_surface, WALL_COLOR, (right, top), (right, bottom), thickness)

                corner_size = 2 * pad + thickness
                if not is_wall(r - 1, c) and not is_wall(r, c - 1):
                    rect = pygame.Rect(left - pad, top - pad, corner_size, corner_size)
                    pygame.draw.arc(
                        self.maze_surface,
                        WALL_COLOR,
                        rect,
                        math.radians(180),
                        math.radians(270),
                        thickness,
                    )
                if not is_wall(r - 1, c) and not is_wall(r, c + 1):
                    rect = pygame.Rect(right - corner_size + pad, top - pad, corner_size, corner_size)
                    pygame.draw.arc(
                        self.maze_surface,
                        WALL_COLOR,
                        rect,
                        math.radians(270),
                        math.radians(360),
                        thickness,
                    )
                if not is_wall(r + 1, c) and not is_wall(r, c + 1):
                    rect = pygame.Rect(right - corner_size + pad, bottom - corner_size + pad, corner_size, corner_size)
                    pygame.draw.arc(
                        self.maze_surface,
                        WALL_COLOR,
                        rect,
                        math.radians(0),
                        math.radians(90),
                        thickness,
                    )
                if not is_wall(r + 1, c) and not is_wall(r, c - 1):
                    rect = pygame.Rect(left - pad, bottom - corner_size + pad, corner_size, corner_size)
                    pygame.draw.arc(
                        self.maze_surface,
                        WALL_COLOR,
                        rect,
                        math.radians(90),
                        math.radians(180),
                        thickness,
                    )

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(60) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_LEFT:
                        self.pacman.set_velocity(-1, 0, self.walls)
                    elif event.key == pygame.K_RIGHT:
                        self.pacman.set_velocity(1, 0, self.walls)
                    elif event.key == pygame.K_UP:
                        self.pacman.set_velocity(0, -1, self.walls)
                    elif event.key == pygame.K_DOWN:
                        self.pacman.set_velocity(0, 1, self.walls)

            self.update(dt)
            self.draw()

        pygame.quit()

    def update(self, dt):
        self.pacman.update(self.walls, dt)

        pc = (int(self.pacman.x) // TILE, int(self.pacman.y) // TILE)
        if pc in self.pellets:
            self.pellets.remove(pc)
            self.score += 1
        if pc in self.fright_fruits:
            self.fright_fruits.remove(pc)
            self.score += 2
            self.fright_end = time.time() + 3.0
            for g in self.ghosts:
                g.scared = True

        for g in self.ghosts:
            if hasattr(g, 'appear_time') and time.time() < g.appear_time:
                continue
            if g.respawn:
                if time.time() >= g.respawn_timer:
                    g.x, g.y = random.choice(self.spawn_points)
                    g.respawn = False
                    g.scared = False
                else:
                    continue
            g.update(self.walls, self.pacman, dt)

            if time.time() < self.invulnerable_end:
                continue
            if circle_collide(g.x, g.y, TILE // 2 - 2, self.pacman.x, self.pacman.y, self.pacman.radius):
                if g.scared:
                    # blue ghosts只是害怕，不会与PacMan产生任何效果
                    continue
                self._handle_pacman_hit()
                return

        if time.time() > self.fright_end:
            for g in self.ghosts:
                g.scared = False

        if not self.pellets and not self.fright_fruits:
            self.level_index += 1
            if self.level_index >= len(self.levels):
                self.win()
            else:
                self.reset_level()

    def _handle_pacman_hit(self):
        if time.time() < self.invulnerable_end:
            return
        self.lives -= 1
        if self.lives <= 0:
            self.game_over()
            return
        self.fright_end = 0
        for g in self.ghosts:
            g.scared = False
        self.invulnerable_end = time.time() + INVULNERABLE_DURATION

    def draw(self):
        self.screen.fill(BLACK)
        pygame.draw.rect(
            self.screen,
            WALL_COLOR,
            pygame.Rect(4, 4, SCREEN_W - 8, ROWS * TILE - 8),
            width=4,
            border_radius=18,
        )

        if hasattr(self, 'maze_surface'):
            self.screen.blit(self.maze_surface, (0, 0))

        for (c, r) in self.pellets:
            x = c * TILE + TILE // 2
            y = r * TILE + TILE // 2
            pygame.draw.circle(self.screen, PELLET_COLOR, (x, y), 2)

        fruit_sprite = self.assets.fruit
        for (c, r) in self.fright_fruits:
            x = c * TILE + TILE // 2
            y = r * TILE + TILE // 2
            rect = fruit_sprite.get_rect(center=(x, y))
            self.screen.blit(fruit_sprite, rect)

        pac_frame = self.pacman.current_frame()
        pac_rect = pac_frame.get_rect(center=(int(self.pacman.x), int(self.pacman.y)))
        self.screen.blit(pac_frame, pac_rect)

        for g in self.ghosts:
            if hasattr(g, 'appear_time') and time.time() < g.appear_time:
                continue
            if g.respawn:
                continue
            ghost_frame = g.current_frame()
            rect = ghost_frame.get_rect(center=(int(g.x), int(g.y)))
            self.screen.blit(ghost_frame, rect)

        hud_rect = pygame.Rect(0, ROWS * TILE, SCREEN_W, SCREEN_H - ROWS * TILE)
        pygame.draw.rect(self.screen, HUD_BG, hud_rect)

        for idx in range(self.lives):
            icon_rect = self.assets.life_icon.get_rect()
            icon_rect.left = 12 + idx * (icon_rect.width + 6)
            icon_rect.centery = ROWS * TILE + (hud_rect.height // 2)
            self.screen.blit(self.assets.life_icon, icon_rect)

        score_txt = self.score_font.render(f'Score: {self.score}', True, HUD_TEXT)
        self.screen.blit(score_txt, (SCREEN_W - score_txt.get_width() - 16, SCREEN_H - score_txt.get_height() - 8))

        level_txt = self.font.render(f'Level {self.level_index + 1}', True, HUD_TEXT)
        self.screen.blit(level_txt, (SCREEN_W // 2 - level_txt.get_width() // 2, SCREEN_H - level_txt.get_height() - 8))

        pygame.display.flip()

    def game_over(self):
        self.show_message('Game Over')
        pygame.time.wait(1000)
        pygame.quit()
        raise SystemExit

    def win(self):
        self.show_message('You Win!')
        pygame.time.wait(1000)
        pygame.quit()
        raise SystemExit

    def show_message(self, text):
        surf = self.font.render(text, True, WHITE)
        rect = surf.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2))
        self.screen.blit(surf, rect)
        pygame.display.flip()

    def _default_map(self):
        return [
            "###################",
            "#........#........#",
            "#.##.###.#.###.##.#",
            "#F........G.......#",
            "#.##.#.#####.#.##.#",
            "#....#...#...#....#",
            "####.### # ###.####",
            "   #.#       #.#   ",
            "####.# ## ## #.####",
            "     .#     #.     ",
            "####.# ##### #.####",
            "   #.#       #.#   ",
            "####.# ##### #.####",
            "#........G........#",
            "#.##.###.#.###.##.#",
            "#F..#.....#.....#F#",
            "#.##.#.#####.#.##.#",
            "#....#...#...#....#",
            "#.######.#.######.#",
            "#.................#",
            "###################",
        ]

    def _level2_map(self):
        return [
            "###################",
            "#F........#......F#",
            "#.##.###.#.###.##.#",
            "#...G....#....G...#",
            "#.##.#.#####.#.##.#",
            "#....#...#...#....#",
            "####.### # ###.####",
            "   #.#       #.#   ",
            "####.# ## ## #.####",
            "     .#     #.     ",
            "####.# ##### #.####",
            "   #.#       #.#   ",
            "####.# ##### #.####",
            "#...G........G....#",
            "#.##.###.#.###.##.#",
            "#F..#.....#.....#F#",
            "#.##.#.#####.#.##.#",
            "#....#...#...#....#",
            "#.######.#.######.#",
            "#.................#",
            "###################",
        ]


def circle_collide(x1, y1, r1, x2, y2, r2):
    dx = x1 - x2
    dy = y1 - y2
    return dx * dx + dy * dy <= (r1 + r2) ** 2
