from tutorial.updateable import Updateable

class Timer(Updateable):
    timers = []
    def __init__(self, wait_time_ms, callback):
        self.wait_time_ms = wait_time_ms
        self.callback = callback
        self.alive = True
        Timer.timers.append(self)

    def update(self, ms):
        if not self.alive:
            return
        self.wait_time_ms -= ms
        if self.wait_time_ms <= 0:
            self.callback()
            self.destroy()

    def destroy(self):
        self.alive = False
        if self in Timer.timers:
            Timer.timers.remove(self)

    @classmethod
    def update_all(cls, ms):
        for timer in Timer.timers:
            timer.update(ms)