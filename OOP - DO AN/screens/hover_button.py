from kivy.uix.button import Button
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

class HoverButton(Button, HoverBehavior):
    def on_hover(self, hovered):
        if hovered:
            self.background_color = (1, 1, 0.7, 1)  # Vàng nhạt khi hover
        else:
            self.background_color = (1, 1, 1, 1)    # Trắng mặc định
