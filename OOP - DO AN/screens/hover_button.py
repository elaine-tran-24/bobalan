from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
from kivy.properties import BooleanProperty
from kivy.core.window import Window

class HoverBehavior:
    hovered = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(mouse_pos=self.on_mouse_pos)

    def on_mouse_pos(self, *args):
        if not self.get_root_window():
            return
        pos = args[1]
        inside = self.collide_point(*self.to_widget(*pos))
        self.hovered = inside
        self.on_hover(inside)

    def on_hover(self, hovered):
        pass

class HoverImageButton(ButtonBehavior, Image, HoverBehavior):
    def on_hover(self, hovered):
        if hovered:
            self.opacity = 0.8
        else:
            self.opacity = 1.0