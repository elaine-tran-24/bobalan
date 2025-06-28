"""
Tutorial Screen for When Cows Fly
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.app import App
from kivy.graphics import Color, Rectangle
from kivy.core.window import Window
from screens.background import ParallaxWidget
from kivy.uix.floatlayout import FloatLayout
from screens.hover_button import HoverImageButton
from kivy.metrics import dp
from kivy.uix.image import Image

class TutorialScreen(Screen):
    """Tutorial screen explaining game mechanics"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()
    
    def build_ui(self):

        # Background setup
        self.bg_parallax = ParallaxWidget()
        self.add_widget(self.bg_parallax)

        with self.canvas:
            self.overlay_color = Color(0, 0, 0, 0.2)  # black, opacity 0.2 (20%)
            self.overlay_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_overlay, size=self.update_overlay)
        
        main_layout = FloatLayout()
        self.add_widget(main_layout)

        vertical_layout = BoxLayout(
            orientation='vertical',
            padding=20,
            spacing=20,
            size_hint=(1, 1)
        )
        # Tutorial 
        tutorial_img = Image(
            source="assets/images/backgrounds/tutorial_background.png", 
            allow_stretch=True,
            keep_ratio=True,
            size_hint=(0.8, 1),
            pos_hint={"center_x": 0.5, "center_y": 0.5}
        )
        main_layout.add_widget(tutorial_img)

        # Back button
        back_btn = HoverImageButton(
            source="assets/images/buttons/return.png",
            size_hint=(1, None),
            height=dp(100)
        )
        back_btn.bind(on_press=self.go_back)
        main_layout.add_widget(back_btn)

    def update_overlay(self, *args):
        self.overlay_rect.pos = self.pos
        self.overlay_rect.size = self.size

    def go_back(self, button):
        app = App.get_running_app()
        if app and hasattr(app, 'sound_manager'):
            app.sound_manager.play_sound('button_click')
        self.manager.current = 'main_menu'