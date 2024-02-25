import pygame

class Animation():
    def __init__(self, ui_container, duration : float) -> None:
        self.name = ""
        self.ui_element = ui_container
        
        self.duration = duration
        self.timer = 0.0

        self.finished = False

    def update(self, dt : float) -> None:
        self.timer += dt

    def reset(self):
        self.finished = False
        self.timer = 0

class AlphaAnimation(Animation):
    def __init__(self, ui_element, duration : float, alpha_from : int, alpha_to : int, easing = None) -> None:
        super().__init__(ui_element, duration)
        self.easing = easing
        self.alpha_from = alpha_from
        self.alpha_to = alpha_to
        self.alpha = alpha_from
    
    def update(self, dt: float) -> None:
        if not self.easing:
            self.alpha = self.alpha_from + (self.alpha_to - self.alpha_from) * (self.timer / self.duration)
        else:
            self.alpha = self.alpha_from + (self.alpha_to - self.alpha_from) * self.easing(self.timer / self.duration)
        
        self.ui_element._image.set_alpha(self.alpha)

        super().update(dt)
        
        if self.timer > self.duration:
            self.finished = True
            self.alpha = self.alpha_to

    def reset(self):
        super().reset()

class MoveAnimation():
    def __init__(self, duration, pos_from, pos_to, easing, end_event=lambda : None):
        self.timer = 0.0
        self.duration = duration
        self.pos_from : pygame.Vector2 = pos_from
        self.pos_to : pygame.Vector2  = pos_to
        self.easing = easing
        self.position : pygame.Vector2 = pygame.Vector2()
        self.finished = False
        self.end_event = end_event
    
    def update(self, dt : float):
        self.timer += dt
        if self.timer > self.duration:
            self.finished = True
            self.position = self.pos_to
            self.end_event()
            return
        
        t = pygame.math.clamp(self.easing(self.timer / self.duration), 0, 1)
        self.position = self.pos_from.lerp(self.pos_to, t)
    
    def reset(self):
        self.position = self.pos_from
        self.timer = 0.0
        self.finished = False