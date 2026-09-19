import pygame
import random
import sys

pygame.init()

WIDTH, HEIGHT = 900, 600
FPS = 60
GAME_TIME = 120

SKY = (174, 225, 255)
WHITE = (255, 255, 255)
BLACK = (30, 30, 30)
GREEN = (55, 185, 95)
DARK_GREEN = (35, 145, 70)
RED = (230, 70, 70)
PINK = (255, 190, 220)
YELLOW = (255, 230, 110)
BLUE = (90, 160, 255)
GRAY = (230, 230, 230)

GOOD_ITEMS = ["📘", "📄", "✏️", "💻", "📝", "🎒", "📏", "🧮"]
BAD_ITEMS = ["🎬", "📸", "🎧", "🎵", "▶️","📱"]


class FallingItem:
    def __init__(self, kind, round_level):
        self.kind = kind
        self.x = random.randint(40, WIDTH - 80)
        self.y = -70
        self.speed = random.randint(3 + round_level, 5 + round_level)

        if kind == "good":
            self.text = random.choice(GOOD_ITEMS)
            self.points = 2
            self.rect = pygame.Rect(self.x, self.y, 28, 28)
        elif kind == "bad":
            self.text = random.choice(BAD_ITEMS)
            self.points = -4
            self.rect = pygame.Rect(self.x, self.y, 28, 28)
        elif kind == "bomb":
            self.text = "💣"
            self.points = 0
            self.rect = pygame.Rect(self.x, self.y, 30, 30)
        else:
            self.text = "⭐"
            self.points = 0
            self.rect = pygame.Rect(self.x, self.y, 32, 32)

    def update(self):
        self.y += self.speed
        self.rect.y = self.y

    def draw(self, screen, emoji_font):
        label = emoji_font.render(self.text, True, BLACK)
        screen.blit(label, (self.rect.centerx - label.get_width() // 2,
                            self.rect.centery - label.get_height() // 2))


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("SEO PyGame Project - Exam Catcher")

        self.clock = pygame.time.Clock()

        self.font = pygame.font.SysFont("arial", 20, bold=True)
        self.big_font = pygame.font.SysFont("arial", 48, bold=True)
        self.medium_font = pygame.font.SysFont("arial", 30, bold=True)

        self.emoji_font = pygame.font.SysFont("Apple Color Emoji", 18)
        self.student_font = pygame.font.SysFont("Apple Color Emoji", 24)
        self.player_font = pygame.font.SysFont("Apple Color Emoji", 32)

        self.player = pygame.Rect(WIDTH // 2 - 32, HEIGHT - 85, 64, 64)
        self.gender = "female"

        self.items = []
        self.score = 0
        self.state = "start"
        self.end_message = ""
        self.start_ticks = 0
        self.round_level = 1

        self.bombs_spawned = 0
        self.star_spawned = False

        self.start_button = pygame.Rect(WIDTH // 2 - 130, 340, 260, 80)
        self.settings_button = pygame.Rect(WIDTH - 85, 25, 60, 60)
        self.return_button = pygame.Rect(WIDTH // 2 - 60, 405, 120, 55)

        self.games_played = 0
        self.passes = 0
        self.total_points = 0
        self.best_score = 0

    def draw_text_center(self, text, font, color, y):
        img = font.render(text, True, color)
        self.screen.blit(img, (WIDTH // 2 - img.get_width() // 2, y))

    def draw_settings_icon(self):
        pygame.draw.rect(self.screen, WHITE, self.settings_button, border_radius=14)
        pygame.draw.rect(self.screen, BLACK, self.settings_button, 3, border_radius=14)

        center = self.settings_button.center
        pygame.draw.circle(self.screen, BLACK, center, 15, 4)
        pygame.draw.circle(self.screen, BLACK, center, 4)

        for angle in range(0, 360, 45):
            import math
            rad = math.radians(angle)
            x1 = center[0] + int(math.cos(rad) * 20)
            y1 = center[1] + int(math.sin(rad) * 20)
            x2 = center[0] + int(math.cos(rad) * 26)
            y2 = center[1] + int(math.sin(rad) * 26)
            pygame.draw.line(self.screen, BLACK, (x1, y1), (x2, y2), 4)

    def draw_school_background(self, mood="normal"):
        if mood == "happy":
            self.screen.fill((190, 255, 205))
        elif mood == "sad":
            self.screen.fill((255, 195, 195))
        else:
            self.screen.fill(SKY)

        pygame.draw.rect(self.screen, (255, 245, 210), (0, 430, WIDTH, 170))
        pygame.draw.rect(self.screen, (185, 145, 95), (0, 560, WIDTH, 40))
        pygame.draw.circle(self.screen, YELLOW, (760, 110), 45)

        for x in [110, 420, 690]:
            pygame.draw.rect(self.screen, (185, 110, 65), (x, 455, 110, 55), border_radius=8)
            pygame.draw.rect(self.screen, (120, 75, 45), (x + 15, 510, 10, 50))
            pygame.draw.rect(self.screen, (120, 75, 45), (x + 85, 510, 10, 50))

    def draw_start_screen(self):
        self.draw_school_background("normal")

        self.draw_text_center("SEO PyGame Project", self.big_font, BLACK, 70)
        self.draw_text_center("Exam Catcher", self.medium_font, BLACK, 130)
        self.draw_text_center("Catch school items. Avoid distractions.", self.font, BLACK, 185)
        self.draw_text_center("Bomb = kicked out. Star = automatic pass.", self.font, BLACK, 215)

        pygame.draw.rect(self.screen, GREEN, self.start_button, border_radius=25)
        pygame.draw.rect(self.screen, DARK_GREEN, self.start_button, 4, border_radius=25)

        text = self.medium_font.render("START", True, WHITE)
        self.screen.blit(text, (self.start_button.centerx - text.get_width() // 2,
                                self.start_button.centery - text.get_height() // 2))

        self.draw_settings_icon()
        pygame.display.flip()

    def draw_settings_screen(self):
        self.screen.fill(WHITE)

        self.draw_text_center("Settings", self.big_font, BLACK, 30)
        self.draw_text_center("Choose Student", self.medium_font, BLACK, 110)

        female_button = pygame.Rect(190, 185, 170, 100)
        male_button = pygame.Rect(540, 185, 170, 100)

        pygame.draw.rect(self.screen, PINK if self.gender == "female" else GRAY, female_button, border_radius=18)
        pygame.draw.rect(self.screen, BLUE if self.gender == "male" else GRAY, male_button, border_radius=18)

        f = self.student_font.render("👩‍🎓", True, BLACK)
        m = self.student_font.render("👨‍🎓", True, BLACK)

        self.screen.blit(f, (female_button.centerx - f.get_width() // 2, female_button.centery - f.get_height() // 2))
        self.screen.blit(m, (male_button.centerx - m.get_width() // 2, male_button.centery - m.get_height() // 2))

        self.draw_text_center("Score Summary", self.medium_font, BLACK, 330)

        self.screen.blit(self.font.render(f"Games Played: {self.games_played}", True, BLACK), (330, 380))
        self.screen.blit(self.font.render(f"Passes: {self.passes}", True, BLACK), (330, 415))
        self.screen.blit(self.font.render(f"Total Points: {self.total_points}", True, BLACK), (330, 450))
        self.screen.blit(self.font.render(f"Best Score: {self.best_score}%", True, BLACK), (330, 485))

        back_button = pygame.Rect(25, 25, 90, 45)
        pygame.draw.rect(self.screen, RED, back_button, border_radius=12)

        back = self.font.render("Back", True, WHITE)
        self.screen.blit(back, (back_button.centerx - back.get_width() // 2,
                                back_button.centery - back.get_height() // 2))

        pygame.display.flip()
        return female_button, male_button, back_button

    def reset_game(self):
        self.items = []
        self.score = 0
        self.state = "playing"
        self.start_ticks = pygame.time.get_ticks()
        self.bombs_spawned = 0
        self.star_spawned = False
        self.end_message = ""
        self.round_level = 1
        self.player.x = WIDTH // 2 - 32

    def spawn_item(self):
        roll = random.randint(1, 100)

        if roll <= 3 and self.bombs_spawned < 3:
            self.items.append(FallingItem("bomb", self.round_level))
            self.bombs_spawned += 1
        elif roll <= 5 and not self.star_spawned:
            self.items.append(FallingItem("star", self.round_level))
            self.star_spawned = True
        else:
            if self.round_level == 1:
                choices = ["good", "good", "good", "good", "bad"]
            elif self.round_level == 2:
                choices = ["good", "good", "good", "bad", "bad"]
            else:
                choices = ["good", "good", "bad", "bad", "bad"]

            self.items.append(FallingItem(random.choice(choices), self.round_level))

    def draw_player(self):
        student_icon = "👩‍🎓" if self.gender == "female" else "👨‍🎓"
        student = self.player_font.render(student_icon, True, BLACK)

        self.screen.blit(student, (self.player.centerx - student.get_width() // 2,
                                   self.player.centery - student.get_height() // 2))

    def draw_playing_screen(self, time_left):
        self.draw_school_background("normal")

        self.screen.blit(self.font.render(f"Score: {self.score}%", True, BLACK), (20, 20))
        self.screen.blit(self.font.render(f"Time: {time_left}", True, BLACK), (WIDTH - 130, 20))
        self.screen.blit(self.font.render(f"Round: {self.round_level}", True, BLACK), (390, 20))

        self.draw_player()

        for item in self.items:
            item.draw(self.screen, self.emoji_font)

        pygame.display.flip()

    def record_score(self, passed):
        self.games_played += 1
        self.total_points += self.score
        self.best_score = max(self.best_score, self.score)

        if passed:
            self.passes += 1

    def set_end_message(self, reason):
        passed = False

        if reason == "bomb":
            self.end_message = "OOP you have been kicked out of school."
        elif reason == "star":
            self.score = 100
            self.end_message = "⭐ Automatic pass! You passed your exam!"
            passed = True
        elif self.score >= 100:
            self.end_message = "Yay! You passed your exam with a 100%!"
            passed = True
        elif self.score >= 65:
            self.end_message = f"You passed! Your grade is {self.score}%"
            passed = True
        else:
            self.end_message = "Whomp whomp, you failed your exam."

        self.record_score(passed)
        self.state = "end"

    def draw_end_screen(self):
        won = "passed" in self.end_message or "Automatic" in self.end_message or "100%" in self.end_message

        if won:
            self.draw_school_background("happy")
            self.draw_text_center("Congratulations!", self.big_font, BLACK, 110)
        else:
            self.draw_school_background("sad")
            self.draw_text_center("Better Luck Next Time", self.big_font, BLACK, 110)

        self.draw_text_center(self.end_message, self.medium_font, BLACK, 230)

        pygame.draw.rect(self.screen, GREEN, self.return_button, border_radius=18)

        return_icon = self.player_font.render("↩️", True, WHITE)
        self.screen.blit(return_icon, (self.return_button.centerx - return_icon.get_width() // 2,
                                       self.return_button.centery - return_icon.get_height() // 2))

        self.draw_text_center("Click return to restart", self.font, BLACK, 485)
        pygame.display.flip()

    def run(self):
        running = True

        while running:
            self.clock.tick(FPS)

            if self.state == "start":
                self.draw_start_screen()

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        if self.start_button.collidepoint(event.pos):
                            self.reset_game()
                        elif self.settings_button.collidepoint(event.pos):
                            self.state = "settings"

            elif self.state == "settings":
                female_button, male_button, back_button = self.draw_settings_screen()

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        if female_button.collidepoint(event.pos):
                            self.gender = "female"
                        elif male_button.collidepoint(event.pos):
                            self.gender = "male"
                        elif back_button.collidepoint(event.pos):
                            self.state = "start"

            elif self.state == "playing":
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False

                keys = pygame.key.get_pressed()

                if keys[pygame.K_LEFT] and self.player.left > 0:
                    self.player.x -= 8
                if keys[pygame.K_RIGHT] and self.player.right < WIDTH:
                    self.player.x += 8

                seconds_passed = (pygame.time.get_ticks() - self.start_ticks) // 1000
                time_left = max(0, GAME_TIME - seconds_passed)

                if seconds_passed < 40:
                    self.round_level = 1
                    spawn_chance = 28
                elif seconds_passed < 85:
                    self.round_level = 2
                    spawn_chance = 22
                else:
                    self.round_level = 3
                    spawn_chance = 16

                if random.randint(1, spawn_chance) == 1:
                    self.spawn_item()

                for item in self.items[:]:
                    item.update()

                    if item.rect.colliderect(self.player):
                        if item.kind == "bomb":
                            self.set_end_message("bomb")
                        elif item.kind == "star":
                            self.set_end_message("star")
                        else:
                            self.score += item.points
                            self.score = max(0, self.score)

                        self.items.remove(item)

                    elif item.y > HEIGHT:
                        self.items.remove(item)

                if self.score >= 100:
                    self.set_end_message("score")
                elif time_left <= 0:
                    self.set_end_message("time")

                self.draw_playing_screen(time_left)

            elif self.state == "end":
                self.draw_end_screen()

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        if self.return_button.collidepoint(event.pos):
                            self.state = "start"

        pygame.quit()
        sys.exit()