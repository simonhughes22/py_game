import math
from tutorial.drawable import Drawable

class MySprite(Drawable):
    def __init__(self, image=None, x=-1, y=-1, z_order=0):
        super().__init__(x=x, y=y, z_order=z_order)
        self.image = image
        if self.image:
            rect = self.get_rect()
            self.height = rect.height
            self.width = rect.width

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

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))
