import random
import sys

import pygame
from pygame import mixer

from tutorial.animation import SpriteSheetAnimation
from tutorial.colors import Color
from tutorial.draw_text import DrawText
from tutorial.game_state import GameState
from tutorial.input_handler import InputHandler
from tutorial.moveable_sprite import MoveableMySprite
from tutorial.sprite import Drawable
from tutorial.timer import Timer


class Player(MoveableMySprite):
    def __init__(self, image, input_handler, x=-1, y=-1, accel=0.0, max_speed=35.0, keep_in_screen_bounds=True):
        super().__init__(image=image, x=x, y=y, accel=accel, max_speed=max_speed,
                         z_order=1, keep_in_screen_bounds=keep_in_screen_bounds)
        self.input_handler = input_handler

    def on_before_update(self):
        if not self.alive:
            return

        keys_pressed = self.input_handler.keys_pressed
        keys_down = self.input_handler.keys_down

        if pygame.K_SPACE in keys_pressed:
            bullet = Bullet(player=self)
            bullet_sound.play()

        if pygame.K_LEFT not in keys_down and pygame.K_RIGHT not in keys_down:
            self.x_accel = 0
            self.x_change = 0
        else:
            if pygame.K_LEFT in keys_down:
                self.x_accel = -1 * self.accel
            if pygame.K_RIGHT in keys_down:
                self.x_accel = self.accel

    def on_destroyed(self):
        scaled_image = pygame.transform.scale(ship_explosion_image, (self.width * ship_explosion_frames, self.height))
        explosion_animation = SpriteSheetAnimation(
            image=scaled_image, x=self.x, y=self.y, z_order=self.z_order + 1,
            num_frames=ship_explosion_frames, duration_secs=SHIP_EXPLOSION_DURATION_MSECS/1000)
        ship_explosion_sound.play(maxtime=SHIP_EXPLOSION_DURATION_MSECS)

        def animation_complete():
            GameState.PLAYER_DIED = True

        explosion_animation.when_finished(animation_complete)

class Enemy(MoveableMySprite):
    DROP = 40
    def __init__(self, image, player, x=-1, y=-1, accel=0.0, max_speed=35.0, z_order=-1, keep_in_screen_bounds=True):
        super().__init__(image=image, x=x, y=y, accel=accel, max_speed=max_speed,
                         z_order=z_order, keep_in_screen_bounds=keep_in_screen_bounds)
        self.player = player
        self.facing_right = random.choice([True, False])

    def update(self, ms):
        if self.facing_right:
            self.x_accel = self.accel
        else:
            self.x_accel = -self.accel

        self.__apply_acceleration__()
        # if out of bound, switch direction
        if self.x < 0:
            self.facing_right = True
            self.x_accel = 0
            self.y += Enemy.DROP
        elif self.x > GameState.WIDTH - self.width:
            self.facing_right = False
            self.x_accel = 0
            self.y += Enemy.DROP

        # clip to player's y position so it doesn't drop off the screen
        self.y = min(self.player.y, self.y)
        self.__clip_to_screen_bounds__()
        self.on_updated()

    def on_updated(self):
        for spr in Drawable.drawables:
            if type(spr) == Player and self.has_collided_with(spr):
                spr.destroy()

    def on_destroyed(self):
        scaled_image = pygame.transform.scale(enemy_explosion_image, (self.width * enemy_explosion_frames, self.height))
        explosion_animation = SpriteSheetAnimation(
            image=scaled_image, x=self.x, y=self.y, z_order=self.z_order+1,
            num_frames=enemy_explosion_frames, duration_secs=ENEMY_EXPLOSION_DURATION_MSECS/1000)
        enemy_explosion_sound.play(maxtime=ENEMY_EXPLOSION_DURATION_MSECS)
        # Spawn new enemy
        # spawn_enemy() # causes an infinite loop when hitting the player, who kills the enemies
        spawn_enemy(self.player)

class Bullet(MoveableMySprite):
    def __init__(self, player, width=3, height=8):
        super().__init__(x=player.x + (player.width) / 2 - width / 2,
                         y=player.y + height / 4,
                         keep_in_screen_bounds=False, z_order = player.z_order-1)
        self.width = width
        self.height = height
        self.y_change = -1 * player.max_speed * 1.25
        # paint before (behind) the player
        self.max_speed = abs(self.y_change)

    def draw(self, screen):
        pygame.draw.rect(screen, Color.YELLOW, (self.x, self.y, self.width, self.height))

    def on_screen_bounds_exceeded(self):
        self.destroy()

    def get_rect(self):
        rect = pygame.Rect(self.x, self.y, self.width, self.height)
        return rect

    def on_updated(self):
         for enemy in Drawable.get_all_of_type(Enemy):
            if self.has_collided_with(enemy):
                self.destroy()
                enemy.destroy()
                GameState.SCORE += 1

class Background(Drawable):
    def __init__(self, num_stars):
        super().__init__(x=0, y=0, z_order=-10)
        self.persists_on_kill = True
        # Do not call super this time
        self.stars = [
            [random.randint(0, GameState.WIDTH), random.randint(0, GameState.HEIGHT), random.randint(1,3)]
            for x in range(num_stars)
        ]
        self.background = pygame.Surface(screen.get_size()).convert()

    def draw(self, screen):
        # black background
        self.background.fill(Color.BLACK)
        self.__draw_stars__()
        screen.blit(self.background, (self.x, self.y)) # (0,0)

    def __draw_stars__(self):
        for star in self.stars:
            if star[2] == 1:
                pygame.draw.line(self.background, Color.WHITE, (star[0], star[1]), (star[0], star[1]), 1)
            elif star[2] == 2:
                # Twinkling Star
                if random.choice([True, False]):
                    pygame.draw.line(self.background, Color.WHITE, (star[0], star[1]), (star[0], star[1]), 1)
                else:
                    pygame.draw.line(self.background, Color.WHITE, (star[0] + 1, star[1] - 1),
                                     (star[0] + 1, star[1] + 1), 1)
            elif star[2] == 3:
                pygame.draw.line(self.background, Color.WHITE, (star[0], star[1]), (star[0], star[1]), 1)
                pygame.draw.line(self.background, Color.WHITE, (star[0] + 1, star[1] - 1), (star[0] + 1, star[1] + 1),
                                 1)
            else:
                raise Exception('width out of range')

            # move stars to the left
            star[0] = star[0] - 1
            if star[0] < 0:
                # offscreen, generate a new star on the right with a random y position
                star[0] = GameState.WIDTH
                star[1] = random.randint(0, GameState.HEIGHT)

def is_debug():
    tr = sys.gettrace()
    return tr is not None

pygame.init()
# If in debug, do not go full screen
if is_debug():
    screen = pygame.display.set_mode((GameState.WIDTH, GameState.HEIGHT))
else:
    screen = pygame.display.set_mode((GameState.WIDTH, GameState.HEIGHT), pygame.FULLSCREEN)

pygame.display.set_caption("Space Invaders")
# Load Assets
ASSET_ROOT = "./assets"

# load sounds
mixer.music.load(f"{ASSET_ROOT}/background.wav")
mixer.music.play(-1)

bullet_sound = mixer.Sound(f"{ASSET_ROOT}/laser.wav")
enemy_explosion_sound = mixer.Sound(f"{ASSET_ROOT}/explosion.wav")
ship_explosion_sound = mixer.Sound(f"{ASSET_ROOT}/ship_explosion.wav")

# IMAGES
bullet_image = pygame.image.load(f"{ASSET_ROOT}/bullet.png").convert_alpha()
player_image = pygame.image.load(f"{ASSET_ROOT}/spaceship-2.png").convert_alpha()

# Enemy images
alien_image  = pygame.image.load(f"{ASSET_ROOT}/alien.png").convert_alpha()
alien_2_image  = pygame.image.load(f"{ASSET_ROOT}/alien-2.png").convert_alpha()
ufo_image  = pygame.image.load(f"{ASSET_ROOT}/ufo.png").convert_alpha()
monster_spooky_image  = pygame.image.load(f"{ASSET_ROOT}/spooky.png").convert_alpha()
monster_2_image  = pygame.image.load(f"{ASSET_ROOT}/monsters-2.png").convert_alpha()
monster_3_image  = pygame.image.load(f"{ASSET_ROOT}/monsters-3.png").convert_alpha()
monster_medium_image  = pygame.image.load(f"{ASSET_ROOT}/monster_medium.png").convert_alpha()
monster_small_image  = pygame.image.load(f"{ASSET_ROOT}/monster_small.png").convert_alpha()

# animations
enemy_explosion_image  = pygame.image.load(f"{ASSET_ROOT}/explosion.png").convert_alpha()
enemy_explosion_frames = 12

ship_explosion_image  = pygame.image.load(f"{ASSET_ROOT}/ship_explosion.png").convert_alpha()
ship_explosion_frames = 6

enemy_images = [
    alien_image,
    alien_2_image,
    ufo_image,
    monster_medium_image,
    monster_small_image,
    monster_2_image,
    monster_3_image
]

def get_new_enemy_position():
    for _ in range(10): # do a max of 30 loops
        enemy_x, enemy_y = random.randint(0, GameState.WIDTH), random.randint(50, 200)
        for enemy in Drawable.get_all_of_type(Enemy):
            distance = enemy.get_distance_from_coord(enemy_x, enemy_y)
            if distance > 70:
                return enemy_x, enemy_y
    return enemy_x, enemy_y

def spawn_enemy(player):
    enemy_x, enemy_y = get_new_enemy_position()
    image = random.choice(enemy_images)
    enemy = Enemy(image=image, player=player, x=enemy_x, y=enemy_y, accel=ENEMY_SPEED / 2, max_speed=ENEMY_SPEED)

def initialize_sprites():
    player = Player(player_image, input_handler, x=370, y=540, accel=PLAYER_SPEED / 5, max_speed=PLAYER_SPEED)
    for i in range(NUM_ENEMIES):
        spawn_enemy(player)

NUM_ENEMIES = 10
PLAYER_SPEED = 10
ENEMY_SPEED = 8
NUM_STARS = 50
ENEMY_EXPLOSION_DURATION_MSECS = 1000
SHIP_EXPLOSION_DURATION_MSECS = 1000

if is_debug():
    PLAYER_SPEED *= 4
    ENEMY_SPEED *= 4

input_handler = InputHandler()
background = Background(num_stars=NUM_STARS)
score = DrawText(font_size=32, font_name='freesansbold.ttf', txt=lambda : f"Score: {GameState.SCORE}",
                 font_color=Color.WHITE, x=10, y=10)

initialize_sprites()
clock = pygame.time.Clock()

while not GameState.QUIT:
    # handle player death
    if GameState.PLAYER_DIED:
        GameState.PLAYER_DIED = False
        GameState.LIVES -= 1
        Drawable.remove_all()
        timer = Timer(wait_time_ms=1000, callback=initialize_sprites)

    ms = clock.tick(GameState.FRAME_RATE)
    fps = clock.get_fps()
    print("FPS", fps)

    new_key_presses = input_handler.process_events()
    background.draw(screen)

    Drawable.update_all(ms)
    Timer.update_all(ms)

    Drawable.draw_all(screen)
    score.draw(screen)

    # Update the display
    pygame.display.update()