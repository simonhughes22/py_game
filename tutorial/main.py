import random
import sys

import pygame

from tutorial.animation import SpriteSheetAnimation
from tutorial.game_state import GameState
from tutorial.moveable_sprite import MoveableMySprite
from tutorial.sprite import MySprite

class Player(MoveableMySprite):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.z_order = 1 # render after the default sprites
        self.keys_pressed = set()
        self.persists_on_kill = True

    def move(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                GameState.QUIT = True
            # Process Keyboard input
            if event.type == pygame.KEYDOWN:
                self.keys_pressed.add(event.key)
            if event.type == pygame.KEYUP:
                self.keys_pressed.remove(event.key)

            for key in self.keys_pressed:
                if key == pygame.K_ESCAPE:
                    GameState.QUIT = True
                if key == pygame.K_LEFT:
                    self.x_accel = -1*self.accel
                if key == pygame.K_RIGHT:
                    self.x_accel = self.accel
                if key == pygame.K_SPACE:
                    self.__spawn_bullet__()

            if pygame.K_LEFT not in self.keys_pressed and pygame.K_RIGHT not in self.keys_pressed:
                self.x_accel = 0
                self.x_change = 0

        # update player position
        self.__apply_acceleration__()
        # clamp the player to the screen boundaries
        self.__clip_to_screen_bounds__()

    def __spawn_bullet__(self):

        player = self

        class Bullet(MoveableMySprite):
            def __init__(self):
                super().__init__(image=bullet_image)
                self.x = player.x + (player.width) / 2 - self.width / 2
                self.y = player.y + player.height / 4
                self.y_change = -1 * player.max_speed * 1.5
                self.max_speed = abs(self.y_change)

            def on_screen_bounds_exceeded(self):
                self.kill()

            def on_moved(self):
                 for spr in MySprite.active_sprites:
                    if type(spr) == Enemy:
                        if self.has_collided_with(spr):
                            self.kill()
                            spr.kill()
                            GameState.SCORE += 1

        # create a new bullet
        # this automatically gets added to the active sprites list
        bullet = Bullet()

    def on_killed(self):
        scaled_image = pygame.transform.scale(explosion_image, (self.width * explosion_frames, self.height))
        explosion_animation = SpriteSheetAnimation(
            image=scaled_image, x=self.x, y=self.y, z_order=self.z_order + 1,
            num_frames=explosion_frames, duration_secs=0.3)

        self.visible = False
        def restore_visible():
            self.visible = True
        explosion_animation.when_finished(restore_visible)

class Enemy(MoveableMySprite):
    DROP = 40
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.facing_right = random.choice([True, False])

    def move(self):
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
        self.y = min(spr_player.y, self.y)
        self.__clip_to_screen_bounds__()
        self.on_moved()

    def on_moved(self):
        for spr in MySprite.active_sprites:
            if type(spr) == Player and self.has_collided_with(spr):
                MySprite.kill_all()
                GameState.LIVES -= 1

    def on_killed(self):
        scaled_image = pygame.transform.scale(explosion_image, (self.width * explosion_frames, self.height))
        explosion_animation = SpriteSheetAnimation(
            image=scaled_image, x=self.x, y=self.y, z_order=self.z_order+1,
            num_frames=explosion_frames, duration_secs=0.3)

        # Spawn new enemy
        # spawn_enemy() # causes an infinite loop when hitting the player, who kills the enemies


class Stars(MySprite):
    def __init__(self, background, num_stars):

        self.z_order = -1
        self.persists_on_kill = True
        # Do not call super this time
        self.background = background
        self.stars = [
            [random.randint(0, GameState.WIDTH), random.randint(0, GameState.HEIGHT), random.randint(1,3)]
            for x in range(num_stars)
        ]

    def draw(self, screen):
        for star in self.stars:
            if star[2] == 1:
                pygame.draw.line(background, (255, 255, 255), (star[0], star[1]), (star[0], star[1]), 1)
            elif star[2] == 2:
                # Twinkling Star
                if random.choice([True, False]):
                    pygame.draw.line(background, (255, 255, 255), (star[0],   star[1]),   (star[0], star[1]), 1)
                else:
                    pygame.draw.line(background, (255, 255, 255), (star[0]+1, star[1]-1), (star[0]+1, star[1]+1), 1)
            elif star[2] == 3:
                pygame.draw.line(background, (255, 255, 255), (star[0],   star[1]),   (star[0], star[1]), 1)
                pygame.draw.line(background, (255, 255, 255), (star[0]+1, star[1]-1), (star[0]+1, star[1]+1), 1)
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

background = pygame.Surface(screen.get_size()).convert()
pygame.display.set_caption("Space Invaders")

# Load Assets
ASSET_ROOT = "./assets"

bullet_image = pygame.image.load(f"{ASSET_ROOT}/bullet.png").convert_alpha()
# player_image = pygame.image.load(f"{ASSET_ROOT}/rocket.png").convert_alpha()
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
explosion_image  = pygame.image.load(f"{ASSET_ROOT}/explosion.png").convert_alpha()
explosion_frames = 12
explosion_duration_secs = 3

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
        for enemy in MySprite.get_all_of_type(Enemy):
            distance = enemy.get_distance_from_coord(enemy_x, enemy_y)
            if distance > 50:
                return enemy_x, enemy_y
    return enemy_x, enemy_y

def spawn_enemy():
    enemy_x, enemy_y = get_new_enemy_position()
    image = random.choice(enemy_images)
    enemy = Enemy(image=image, x=enemy_x, y=enemy_y, accel=ENEMY_BASE_SPEED/2, max_speed=ENEMY_BASE_SPEED)

NUM_ENEMIES = 8
PLAYER_SPEED = 10
ENEMY_BASE_SPEED = 12
NUM_STARS = 50

stars = Stars(background=background, num_stars=NUM_STARS)

spr_player = Player(player_image, x=370, y=540, accel=PLAYER_SPEED/5, max_speed=PLAYER_SPEED)
for i in range(NUM_ENEMIES):
    spawn_enemy()

clock = pygame.time.Clock()
while not GameState.QUIT:
    ms = clock.tick(GameState.FRAME_RATE)
    fps = clock.get_fps()
    print("FPS", fps)

    background.fill((0, 0, 0))  # black background
    stars.draw(screen)
    screen.blit(background, (0, 0))

    MySprite.render_sprites(screen)
    pygame.display.update()


