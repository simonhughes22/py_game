from abc import abstractmethod

class Drawable(object):
    drawables = []

    def __init__(self, z_order=-1):
        self.z_order = z_order
        self.alive = True
        Drawable.drawables.append(self)

    @abstractmethod
    def update(self, ms):
        pass

    @abstractmethod
    def draw(self, screen):
        pass

    def destroy(self):
        self.alive = False
        self.on_destroyed()
        if self in Drawable.drawables:
            Drawable.drawables.remove(self)

    @abstractmethod
    def on_destroyed(self):
        pass

    @classmethod
    def render(cls, screen, ms):
        for spr in sorted(Drawable.drawables, key=lambda s : s.z_order):
            spr.update(ms)
            spr.draw(screen)

    @classmethod
    def get_all_of_type(cls, target_type):
        return [spr for spr in Drawable.drawables if type(spr) == target_type]

    @classmethod
    def destroy_all(cls, of_type=None):
        for spr in Drawable.drawables:
            if of_type is None or type(spr) == of_type:
                spr.destroy()

    @classmethod
    def remove_all(cls):
        Drawable.drawables = []