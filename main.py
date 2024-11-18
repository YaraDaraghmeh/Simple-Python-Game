import pygame
import random
import math
import os

# Initialize Pygame
pygame.init()
pygame.font.init()

# Set up the game window
WIDTH = 800
HEIGHT = 600
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Shooter")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Fonts
FONT_BIG = pygame.font.Font(None, 74)
FONT_MEDIUM = pygame.font.Font(None, 48)
FONT_SMALL = pygame.font.Font(None, 36)


class Button:
    def __init__(self, x, y, width, height, text, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.original_color = color
        self.is_hovered = False

    def draw(self, surface):
        color = self.color if not self.is_hovered else (*[min(c + 30, 255) for c in self.color[:3]], self.color[3])
        pygame.draw.rect(surface, color, self.rect, border_radius=12)
        text_surface = FONT_SMALL.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_hovered:
                return True
        return False


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((40, 40), pygame.SRCALPHA)
        pygame.draw.polygon(self.image, WHITE, [(0, 40), (20, 0), (40, 40)])
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH // 2
        self.rect.bottom = HEIGHT - 10
        self.speed_x = 0
        self.shoot_delay = 250
        self.last_shot = pygame.time.get_ticks()
        self.lives = 3

    def update(self):
        self.speed_x = 0
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_LEFT]:
            self.speed_x = -8
        if keystate[pygame.K_RIGHT]:
            self.speed_x = 8
        self.rect.x += self.speed_x
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            bullet = Bullet(self.rect.centerx, self.rect.top)
            all_sprites.add(bullet)
            bullets.add(bullet)


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((4, 10))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedy = -10

    def update(self):
        self.rect.y += self.speedy
        if self.rect.bottom < 0:
            self.kill()


class Asteroid(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
        pygame.draw.circle(self.image, WHITE, (15, 15), 15)
        self.rect = self.image.get_rect()
        self.reset_position()

    def reset_position(self):
        self.rect.x = random.randrange(WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speedy = random.randrange(1, 8)
        self.speedx = random.randrange(-3, 3)

    def update(self):
        self.rect.y += self.speedy
        self.rect.x += self.speedx
        if self.rect.top > HEIGHT + 10 or self.rect.left < -25 or self.rect.right > WIDTH + 20:
            self.reset_position()


class Game:
    def __init__(self):
        self.screen = window
        self.clock = pygame.time.Clock()
        self.running = True
        self.playing = False
        self.score = 0
        self.high_score = 0

        # Create buttons
        button_width = 200
        button_height = 50
        center_x = WIDTH // 2 - button_width // 2

        self.play_button = Button(center_x, HEIGHT // 2, button_width, button_height, "Play", (0, 100, 0, 255))
        self.retry_button = Button(center_x, HEIGHT // 2, button_width, button_height, "Retry", (0, 100, 0, 255))
        self.exit_button = Button(center_x, HEIGHT // 2 + 70, button_width, button_height, "Exit", (100, 0, 0, 255))

    def new_game(self):
        global all_sprites, bullets, asteroids, player

        # Create sprite groups
        all_sprites = pygame.sprite.Group()
        asteroids = pygame.sprite.Group()
        bullets = pygame.sprite.Group()

        # Create player
        player = Player()
        all_sprites.add(player)

        # Create asteroids
        for i in range(8):
            asteroid = Asteroid()
            all_sprites.add(asteroid)
            asteroids.add(asteroid)

        self.score = 0
        self.playing = True
        self.run()

    def run(self):
        while self.playing:
            self.clock.tick(60)
            self.handle_events()
            self.update()
            self.draw()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.playing = False
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player.shoot()
                elif event.key == pygame.K_ESCAPE:
                    self.playing = False

    def update(self):
        all_sprites.update()

        # Check for bullet/asteroid collisions
        hits = pygame.sprite.groupcollide(bullets, asteroids, True, True)
        for hit in hits:
            self.score += 10
            asteroid = Asteroid()
            all_sprites.add(asteroid)
            asteroids.add(asteroid)

        # Check for player/asteroid collisions
        hits = pygame.sprite.spritecollide(player, asteroids, True)
        if hits:
            player.lives -= 1
            if player.lives <= 0:
                self.high_score = max(self.score, self.high_score)
                self.playing = False

    def draw(self):
        self.screen.fill(BLACK)
        all_sprites.draw(self.screen)

        # Draw score and lives
        score_text = FONT_SMALL.render(f"Score: {self.score}", True, WHITE)
        lives_text = FONT_SMALL.render(f"Lives: {player.lives}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        self.screen.blit(lives_text, (10, 40))

        pygame.display.flip()

    def show_menu(self):
        while self.running:
            self.clock.tick(60)
            self.screen.fill(BLACK)

            # Draw title
            title = FONT_BIG.render("SPACE SHOOTER", True, WHITE)
            title_rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 3))
            self.screen.blit(title, title_rect)

            # Draw buttons
            self.play_button.draw(self.screen)
            self.exit_button.draw(self.screen)

            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                if self.play_button.handle_event(event):
                    self.new_game()
                elif self.exit_button.handle_event(event):
                    self.running = False

            pygame.display.flip()

    def show_game_over(self):
        waiting = True
        while waiting and self.running:
            self.clock.tick(60)
            self.screen.fill(BLACK)

            # Draw game over text
            game_over_text = FONT_BIG.render("GAME OVER", True, RED)
            score_text = FONT_MEDIUM.render(f"Score: {self.score}", True, WHITE)
            high_score_text = FONT_MEDIUM.render(f"High Score: {self.high_score}", True, WHITE)

            game_over_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 4))
            score_rect = score_text.get_rect(center=(WIDTH // 2, HEIGHT // 3))
            high_score_rect = high_score_text.get_rect(center=(WIDTH // 2, HEIGHT // 2.5))

            self.screen.blit(game_over_text, game_over_rect)
            self.screen.blit(score_text, score_rect)
            self.screen.blit(high_score_text, high_score_rect)

            # Draw buttons
            self.retry_button.draw(self.screen)
            self.exit_button.draw(self.screen)

            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
                    self.running = False

                if self.retry_button.handle_event(event):
                    waiting = False
                    self.new_game()
                elif self.exit_button.handle_event(event):
                    waiting = False
                    self.running = False

            pygame.display.flip()


# Create and run game
game = Game()
game.show_menu()

# Quit pygame
pygame.quit()