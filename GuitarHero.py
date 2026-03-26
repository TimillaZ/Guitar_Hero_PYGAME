import pygame
import random
import sys

# --- Configuration ---
WIDTH, HEIGHT = 1920, 1080
HALF_HEIGHT = HEIGHT // 2
HIT_X = 180
HIT_TOLERANCE = 55

# Colors
BG_COLOR = (10, 10, 18)
DIVIDER_COLOR = (50, 50, 80)
WHITE = (240, 240, 240)
GRAY = (40, 40, 55)
STRING_COLORS = [
    (255, 51, 102), (255, 153, 51), (255, 255, 51),
    (51, 255, 153), (51, 204, 255), (153, 51, 255)
]

# Song Data
SONGS = [
    {"name": "Song 1", "speed": 8, "spawn_rate": 45, "desc": "Easy"},
    {"name": "Song 2", "speed": 12, "spawn_rate": 30, "desc": "Medium"},
    {"name": "Song 3", "speed": 16, "spawn_rate": 18, "desc": "Expert"}
]

# Controls
P1_KEYS = {pygame.K_a: 0, pygame.K_s: 1, pygame.K_d: 2, pygame.K_f: 3, pygame.K_g: 4, pygame.K_h: 5}
P2_KEYS = {pygame.K_j: 0, pygame.K_k: 1, pygame.K_l: 2, pygame.K_SEMICOLON: 3, pygame.K_QUOTE: 4, pygame.K_BACKSLASH: 5}

# --- Classes ---

class Note:
    def __init__(self, string_idx, speed, y_positions):
        self.string_idx = string_idx
        self.x = WIDTH + 50
        self.y = y_positions[string_idx]
        self.color = STRING_COLORS[string_idx]
        self.speed = speed
        self.active = True

    def update(self):
        self.x -= self.speed
        if self.x < -100: self.active = False

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), 35, 4)
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), 28)
        pygame.draw.circle(surface, BG_COLOR, (int(self.x), int(self.y)), 12)

class Player:
    def __init__(self, name, keys, key_names):
        self.name = name
        self.keys = keys
        self.key_names = key_names
        self.score = 0
        self.notes = []
        self.surface = pygame.Surface((WIDTH, HALF_HEIGHT))
        
        margin = 80
        avail = HALF_HEIGHT - (margin * 2)
        self.y_pos = [margin + (i * (avail // 5)) for i in range(6)]

    def reset(self):
        self.score = 0
        self.notes = []

    def draw_lane(self, font):
        self.surface.fill(BG_COLOR)
        pressed = pygame.key.get_pressed()

        for i, y in enumerate(self.y_pos):
            pygame.draw.line(self.surface, GRAY, (0, y), (WIDTH, y), 2)
            is_down = any(pressed[k] for k, v in self.keys.items() if v == i)
            
            rad = 45 if is_down else 35
            width = 0 if is_down else 3
            pygame.draw.circle(self.surface, STRING_COLORS[i], (HIT_X, y), rad, width)
            
            lbl = font.render(self.key_names[i], True, WHITE if not is_down else BG_COLOR)
            self.surface.blit(lbl, lbl.get_rect(center=(HIT_X, y)))

        for note in self.notes:
            note.draw(self.surface)

# --- Main Game Engine ---

class TM4CGuitarHero:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
        self.clock = pygame.time.Clock()
        self.font_main = pygame.font.SysFont("trebuchetms", 36, bold=True)
        self.font_title = pygame.font.SysFont("trebuchetms", 110, bold=True)
        
        self.state = "MENU"
        self.menu_index = 0  # 0-2 are songs, 3 is Quit
        self.p1 = Player("PLAYER 1", P1_KEYS, ["A","S","D","F","G","H"])
        self.p2 = Player("PLAYER 2", P2_KEYS, ["J","K","L",";","'","\\"])
        self.spawn_timer = 0

    def run(self):
        while True:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT: self.quit_game()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.state == "PLAYING": self.state = "PAUSED"
                        elif self.state == "PAUSED": self.state = "PLAYING"

            if self.state == "MENU": self.menu_screen(events)
            elif self.state == "PLAYING": self.gameplay_loop(events)
            elif self.state == "PAUSED": self.pause_screen(events)

            pygame.display.flip()
            self.clock.tick(60)

    def quit_game(self):
        pygame.quit(); sys.exit()

    def menu_screen(self, events):
        self.screen.fill(BG_COLOR)
        title = self.font_title.render("TM4C GUITAR HERO", True, WHITE)
        self.screen.blit(title, (WIDTH//2 - title.get_width()//2, 100))

        # Render Songs
        for i, song in enumerate(SONGS):
            is_selected = (i == self.menu_index)
            color = STRING_COLORS[i % 6] if is_selected else GRAY
            txt = self.font_main.render(f"{song['name']} - {song['desc']}", True, color)
            rect = txt.get_rect(center=(WIDTH//2, 450 + i * 85))
            if is_selected:
                pygame.draw.rect(self.screen, color, rect.inflate(50, 15), 3)
            self.screen.blit(txt, rect)

        # Render Quit Button
        is_quit_selected = (self.menu_index == 3)
        quit_color = (255, 50, 50) if is_quit_selected else GRAY
        quit_txt = self.font_main.render("QUIT GAME", True, quit_color)
        quit_rect = quit_txt.get_rect(center=(WIDTH//2, 450 + 3 * 85 + 40))
        if is_quit_selected:
            pygame.draw.rect(self.screen, quit_color, quit_rect.inflate(50, 15), 3)
        self.screen.blit(quit_txt, quit_rect)

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP: self.menu_index = (self.menu_index - 1) % 4
                if event.key == pygame.K_DOWN: self.menu_index = (self.menu_index + 1) % 4
                if event.key == pygame.K_RETURN:
                    if self.menu_index == 3:
                        self.quit_game()
                    else:
                        self.p1.reset(); self.p2.reset()
                        self.state = "PLAYING"

    def pause_screen(self, events):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0,0))
        
        title = self.font_title.render("PAUSED", True, WHITE)
        resume = self.font_main.render("Press ESC to Resume", True, WHITE)
        quit_txt = self.font_main.render("Press Q to Return to Menu", True, STRING_COLORS[0])
        
        self.screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//3))
        self.screen.blit(resume, (WIDTH//2 - resume.get_width()//2, HEIGHT//2))
        self.screen.blit(quit_txt, (WIDTH//2 - quit_txt.get_width()//2, HEIGHT//2 + 100))

        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                self.state = "MENU"

    def gameplay_loop(self, events):
        song = SONGS[self.menu_index]
        self.spawn_timer += 1
        
        if self.spawn_timer >= song['spawn_rate']:
            lane = random.randint(0, 5)
            self.p1.notes.append(Note(lane, song['speed'], self.p1.y_pos))
            self.p2.notes.append(Note(lane, song['speed'], self.p2.y_pos))
            self.spawn_timer = 0

        for p in [self.p1, self.p2]:
            for event in events:
                if event.type == pygame.KEYDOWN and event.key in p.keys:
                    idx = p.keys[event.key]
                    for n in p.notes:
                        if n.active and n.string_idx == idx:
                            if abs(n.x - HIT_X) <= HIT_TOLERANCE:
                                n.active = False
                                p.score += 10
                                break
            
            for n in p.notes: n.update()
            p.notes = [n for n in p.notes if n.active]
            p.draw_lane(self.font_main)

        self.screen.blit(self.p1.surface, (0, 0))
        self.screen.blit(self.p2.surface, (0, HALF_HEIGHT))
        pygame.draw.line(self.screen, DIVIDER_COLOR, (0, HALF_HEIGHT), (WIDTH, HALF_HEIGHT), 6)

        s1 = self.font_main.render(f"P1 SCORE: {self.p1.score}", True, WHITE)
        s2 = self.font_main.render(f"P2 SCORE: {self.p2.score}", True, WHITE)
        self.screen.blit(s1, (60, 30))
        self.screen.blit(s2, (60, HALF_HEIGHT + 30))

if __name__ == "__main__":
    TM4CGuitarHero().run()