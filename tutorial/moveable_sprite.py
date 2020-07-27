from abc import abstractmethod

from tutorial.game_state import GameState
from tutorial.sprite import MySprite

def clip(val, min_val, max_val):
    assert min_val < max_val, "Min must be less than max"
    return max(min_val, min(max_val, val))

class MoveableMySprite(MySprite):
    active_sprites = []
    def __init__(self, image, x=-1, y=-1, accel=0.0, max_speed=35.0, z_order=0,
                 keep_in_screen_bounds=True, persists_on_kill=False, visible=True):
        super().__init__(image=image, x=x, y=y, z_order=z_order,persists_on_kill=persists_on_kill, visible=visible)

        self.x_change = 0
        self.y_change = 0

        self.x_accel = 0
        self.y_accel = 0

        self.accel = accel
        self.max_speed = max_speed

        self.z_order = z_order
        self.keep_in_screen_bounds = keep_in_screen_bounds
        self.persists_on_kill = persists_on_kill

    def __apply_acceleration__(self):
        # X
        self.x_change += self.x_accel
        # clamp the change to +10 and -10
        self.x_change = clip(self.x_change, -self.max_speed, self.max_speed)
        self.x += self.x_change

        # Y
        self.y_change += self.y_accel
        # clamp the change to +10 and -10
        self.y_change = clip(self.y_change, -self.max_speed, self.max_speed)
        self.y += self.y_change

    def __clip_to_screen_bounds__(self):
        self.x = clip(self.x, 0, GameState.WIDTH - self.width)
        self.y = clip(self.y, 0, GameState.HEIGHT - self.height)

    def move(self):
        # update player position
        self.__apply_acceleration__()

        # Check bounds
        if self.x < 0 or self.x + self.width > GameState.WIDTH:
            self.on_screen_bounds_exceeded()
        elif self.y < 0 or self.y + self.height > GameState.HEIGHT:
            self.on_screen_bounds_exceeded()
        # clamp the player to the screen boundaries
        if self.keep_in_screen_bounds:
            self.__clip_to_screen_bounds__()
        self.on_moved()

    @abstractmethod
    def on_moved(self):
        pass

    @abstractmethod
    def on_screen_bounds_exceeded(self):
        pass

    def has_collided_with(self, other_sprite):
        return self.get_rect().colliderect(other_sprite.get_rect())