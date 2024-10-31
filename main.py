import asyncio
import pygame
from random import randint, uniform


class Player(pygame.sprite.Sprite):
    def __init__(self, group):
        super().__init__(group)
        self.image = pygame.image.load("images/player.png").convert_alpha()
        self.rect = self.image.get_rect(
            center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))
        self.direction = pygame.math.Vector2(0, 0)
        self.speed = 300

        self.can_shoot = True
        self.laser_shoot_time = 0
        self.cooldown_duration = 400

    def laser_time(self):
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.laser_shoot_time >= self.cooldown_duration:
                self.can_shoot = True

    def update(self, dt):
        keys = pygame.key.get_pressed()
        self.direction.x = int(
            keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT])
        self.direction.y = int(keys[pygame.K_DOWN]) - int(keys[pygame.K_UP])

        self.direction = self.direction.normalize(
        ) if self.direction else self.direction
        self.rect.center += (self.direction * self.speed * dt)

        recent_keys = pygame.key.get_just_pressed()
        if recent_keys[pygame.K_SPACE] and self.can_shoot:
            Laser(laser_surface, (all_sprites, laser_sprites), self.rect.midtop)
            self.can_shoot = False
            self.laser_shoot_time = pygame.time.get_ticks()

        self.laser_time()


class Star(pygame.sprite.Sprite):
    def __init__(self, group, surf):
        super().__init__(group)
        self.image = surf
        self.rect = self.image.get_frect(
            center=(randint(0, WINDOW_WIDTH), randint(0, WINDOW_HEIGHT))
        )


class Laser(pygame.sprite.Sprite):
    def __init__(self,  surf, group, pos):
        super().__init__(group)
        self.image = surf
        self.rect = self.image.get_frect(midbottom=pos)
        self.velocity = pygame.math.Vector2(0, -500)

    def update(self, dt):
        self.rect.center += self.velocity * dt
        if self.rect.bottom <= 0:
            self.kill()


class Meteor(pygame.sprite.Sprite):
    def __init__(self, group, surf):
        super().__init__(group)
        self.image = surf
        self.rect = self.image.get_rect(
            center=(randint(0, WINDOW_WIDTH), randint(-100, -10))
        )
        self.direction = pygame.math.Vector2(uniform(-0.5, 0.5), 1)
        self.speed = randint(100, 200)

    def update(self, dt):
        self.rect.center += self.direction * self.speed * dt
        if self.rect.top >= WINDOW_HEIGHT:
            print("Meteor is out of screen")
            self.kill()


# Initialize pygame
pygame.init()

# Setup
WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720
display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("SpaceWar 4990")
clock = pygame.time.Clock()

surface = pygame.Surface((100, 200))

all_sprites = pygame.sprite.Group()
meteor_sprites = pygame.sprite.Group()
laser_sprites = pygame.sprite.Group()
laser_surface = pygame.image.load("images/laser.png").convert_alpha()
meteor_surface = pygame.image.load("images/meteor.png").convert_alpha()
font = pygame.font.Font("images/Oxanium-Bold.ttf", 50)


async def main():

    global surface, all_sprites, laser_surface, meteor_surface, meteor_sprites, laser_sprites, text_surf
    points = 0

    def display_score():
        text_surf = font.render(str(points), True, (255, 255, 255))
        text_rect = text_surf.get_frect(
            midbottom=(WINDOW_WIDTH / 2, WINDOW_HEIGHT - 50))
        pygame.draw.rect(display_surface, 'white',
                         text_rect.inflate(20, 30).move(0, -10), 6, 10)
        display_surface.blit(text_surf, text_rect)

    player = Player(all_sprites)

    star_surface = pygame.image.load("images/star.png").convert_alpha()
    for _ in range(10):
        Star(all_sprites, star_surface)

    meteor_event = pygame.event.custom_type()
    pygame.time.set_timer(meteor_event, 2000)

    # Game loop
    running = True
    while running:
        delta_time = clock.tick(60) / 1000
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == meteor_event:
                Meteor((all_sprites, meteor_sprites), meteor_surface)

        # Update
        all_sprites.update(delta_time)
        if pygame.sprite.spritecollide(player, meteor_sprites, False):
            print("Player is hit")

        # Check for collision between laser and meteor
        for laser in laser_sprites:
            collision_meteors = pygame.sprite.spritecollide(
                laser, meteor_sprites, True)
            if collision_meteors:
                laser.kill()
                for meteor in collision_meteors:
                    points += 10
                    meteor.kill()

        # Draw the game
        display_surface.fill('darkgrey')
        all_sprites.draw(display_surface)

        display_score()
        pygame.display.update()
        await asyncio.sleep(0)

# pygame.quit() is handled automatically in the browser.
asyncio.run(main())
