import math
from abc import abstractmethod

class MySprite(object):
    active_sprites = []
    def __init__(self, image, x=-1, y=-1, z_order=0, persists_on_kill=False, visible=True):

        self.image = image

        self.height = self.image.get_clip().height
        self.width = self.image.get_clip().width

        self.x = x
        self.y = y
        self.z_order = z_order

        self.persists_on_kill = persists_on_kill
        self.visible = True
        self.rect = self.image.get_rect()
        # add oneself to the sprite collection
        MySprite.active_sprites.append(self)

    def get_rect(self):
        rect = self.image.get_rect()
        rect.center = (self.x, self.y)
        return rect

    def get_distance(self, other_sprite):
        return self.get_distance_from_coord(other_sprite.x, other_sprite.y)

    def get_distance_from_coord(self, x, y):
        x_diff = self.x - x
        y_diff = self.y - y
        return math.sqrt(x_diff ** 2 + y_diff ** 2)

    @abstractmethod
    def move(self):
       pass

    def draw(self, screen):
        if self.visible:
            screen.blit(self.image, (self.x, self.y))

    def kill(self):
        self.on_killed()
        if not self.persists_on_kill and self in MySprite.active_sprites:
            MySprite.active_sprites.remove(self)

    @abstractmethod
    def on_killed(self):
        pass

    @classmethod
    def render_sprites(cls, screen):
        for spr in sorted(MySprite.active_sprites, key = lambda s : s.z_order):
            spr.move()
            spr.draw(screen)

    @classmethod
    def get_all_of_type(cls, target_type):
        return [spr for spr in MySprite.active_sprites if type(spr) == target_type]

    @classmethod
    def kill_all(cls):
        for spr in MySprite.active_sprites:
            spr.kill()