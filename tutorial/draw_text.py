from tutorial.drawable import Drawable
import pygame

class DrawText(Drawable):
    def __init__(self, font_size, font_name, font_color, txt, x, y, z_order=999):
        super().__init__(x=x, y=y, z_order=z_order)
        self.font = pygame.font.Font(font_name, font_size)
        self.font_color = font_color
        self.txt = txt

    def draw(self, screen):
        if callable(self.txt):
            txt_to_draw = self.txt()
        elif type(self.txt) == str:
            txt_to_draw = self.txt
        else:
            raise Exception("Unsupported parameter type for parameter <txt>")
        rendered_txt = self.font.render(txt_to_draw, True, self.font_color)
        screen.blit(rendered_txt, (self.x, self.y))