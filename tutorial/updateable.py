from abc import abstractmethod

class Updateable(object):
    @abstractmethod
    def update(self, ms):
        pass

    @abstractmethod
    def destroy(self):
        pass