from tutorial.game_state import GameState
from tutorial.sprite import MySprite

class SpriteSheetAnimation(MySprite):
    def __init__(self, image, x, y, z_order,  num_frames, duration_secs):
        super().__init__(image=image, x=x, y=y, z_order=z_order)
        self.num_frames = num_frames
        self.frame_width = self.width / num_frames
        self.duration_secs = duration_secs
        self.total_frames = duration_secs * GameState.FRAME_RATE
        self.secs_per_keyframe = self.total_frames / num_frames
        self.frames_since_created = 0
        self.callback = None

    def draw(self, screen):
        self.frames_since_created += 1
        current_frame_ix = self.frames_since_created // self.secs_per_keyframe
        if current_frame_ix >= self.num_frames:
            self.destroy()
        else:
            screen.blit(self.get_image(current_frame_ix), (self.x, self.y))

    def get_image(self, index):
        return self.image.subsurface((index*self.frame_width, 0, self.frame_width, self.height))

    def when_finished(self, callback):
        self.callback = callback

    def on_destroyed(self):
        if self.callback is not None:
            self.callback()