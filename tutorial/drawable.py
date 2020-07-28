from abc import abstractmethod
from tutorial.updateable import Updateable

class Drawable(Updateable):
    drawables = []

    def __init__(self, x=-1, y=-1, z_order=-1, add_to_drawables=True):
        self.x = x
        self.y = y
        self.z_order = z_order
        self.alive = True
        if add_to_drawables:
            Drawable.drawables.append(self)

    @abstractmethod
    def draw(self, screen):
        pass

    def destroy(self):
        if not self.alive:
            return # don't destroy me twice
        self.alive = False
        self.on_destroyed()
        if self in Drawable.drawables:
            Drawable.drawables.remove(self)

    @abstractmethod
    def on_destroyed(self):
        pass

    @classmethod
    def update_all(cls, ms):
        for spr in Drawable.drawables:
            if spr.alive: # don't update if already destroyed
                spr.update(ms)

    @classmethod
    def draw_all(cls, screen):
        for spr in sorted(Drawable.drawables, key=lambda s: s.z_order):
            if spr.alive:  # don't draw if already destroyed
                spr.draw(screen)

    @classmethod
    def get_all_of_type(cls, target_type=None):
        return [spr for spr in Drawable.drawables if target_type is None or type(spr) == target_type]

    @classmethod
    def destroy_all(cls, of_type=None):
        for spr in Drawable.drawables:
            if of_type is None or type(spr) == of_type:
                spr.destroy()

    @classmethod
    def remove_all(cls):
        Drawable.drawables = []