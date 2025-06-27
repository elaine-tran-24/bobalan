from kivy.app import App
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.graphics import Rectangle, InstructionGroup
from kivy.clock import Clock
import math


import os

# Kích thước cửa sổ
Window.size = (800, 520)

# Cấu hình đường dẫn
BASE_PATH = os.path.join("assets", "images", "background_1")

GROUND_PATH = r"assets\images\backgrounds\ground.png"

class ParallaxLayer:
    def __init__(self, source, speed):
        self.source = source
        self.speed = speed
        self.offset = 0
        self.rects = []
        self.group = InstructionGroup()
        from kivy.core.image import Image as CoreImage
        self.texture = CoreImage(self.source).texture
        self.img_width = self.texture.width
        self.img_height = self.texture.height

    def init_graphics(self, canvas, y=0, height=Window.height):
        from kivy.graphics import Color
        self.group.clear()
        self.rects = []
        self.group.add(Color(1, 1, 1, 1))  # Đảm bảo hiển thị
        num_tiles = math.ceil(Window.width / self.img_width) + 2
        for i in range(num_tiles):
            rect = Rectangle(texture=self.texture, pos=(i * self.img_width, y),
                             size=(self.img_width, self.img_height))
            self.rects.append(rect)
            self.group.add(rect)
        canvas.add(self.group)

    def move(self, scroll):
      scroll_offset = scroll * self.speed
      total_width = self.img_width * len(self.rects)
      for i, rect in enumerate(self.rects):
          x_pos = (i * self.img_width) - (scroll_offset % total_width)
          if x_pos + self.img_width < 0:
              x_pos += total_width
          rect.pos = (x_pos, rect.pos[1])

          


class GroundLayer:
    def __init__(self, source, scroll_speed):
        self.source = source
        self.scroll_speed = scroll_speed
        self.offset = 0
        self.rects = []
        self.group = InstructionGroup()
        self.image = self.source
        from kivy.core.image import Image as CoreImage
        self.texture = CoreImage(self.image).texture
        self.ground_width = self.texture.size[0]
        self.ground_height = self.texture.size[1]

    def init_graphics(self, canvas, y):
        from kivy.graphics import Color
        self.group.clear()
        self.rects = []
        self.group.add(Color(1, 1, 1, 1))  # Đảm bảo hiển thị

    
        num_tiles = math.ceil(Window.width / self.ground_width) + 2
        for i in range(15):
            rect = Rectangle(texture=self.texture, pos=(i * self.ground_width, y),
                             size=(self.ground_width, self.ground_height))
            self.rects.append(rect)
            self.group.add(rect)
        canvas.add(self.group)

    def move(self, scroll):
      scroll_offset = scroll * self.scroll_speed
      total_width = self.ground_width * len(self.rects)
      for i, rect in enumerate(self.rects):
          x_pos = (i * self.ground_width) - (scroll_offset % total_width)
          if x_pos + self.ground_width < 0:
              x_pos += total_width
          rect.pos = (x_pos, rect.pos[1])


class ParallaxWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.scroll = 0
        self.scroll_max = 3000

        # Load background layers
        self.layers = []
        speed = 1.0
        for i in range(1, 7):
            layer_path = os.path.join(BASE_PATH, f"layer_{i}.png")
            layer = ParallaxLayer(layer_path, speed)
            layer.init_graphics(self.canvas)
            self.layers.append(layer)
            speed += 0.2

        # Load ground
        self.ground = GroundLayer(GROUND_PATH, scroll_speed=6)
        window_height = Window.height
        # ground_y = window_height - self.ground.ground_height
        ground_y =0
        self.ground.init_graphics(self.canvas, y=ground_y)
        

        # Update loop
        Clock.schedule_interval(self.update, 1 / 60)

        # Keyboard
      
        Window.bind(on_key_down=self.key_down)

    def key_down(self, window, key, scancode, codepoint, modifier):
        if key == 276 and self.scroll > 0:  # LEFT
            self.scroll -= 5
        elif key == 275 and self.scroll < self.scroll_max:  # RIGHT
            self.scroll += 5

    def update(self, dt):
      self.scroll += 2  # tốc độ cuộn, bạn có thể điều chỉnh
      for layer in self.layers:
          layer.move(self.scroll)
      self.ground.move(self.scroll)


class ParallaxApp(App):
    def build(self):
        return ParallaxWidget()

if __name__ == '__main__':
    ParallaxApp().run()