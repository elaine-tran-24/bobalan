from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.app import App
from kivy.graphics import Color, Rectangle
from kivy.core.window import Window
from kivy.animation import Animation
from screens.background import ParallaxWidget


class GameOverScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_score = 0
        self.is_new_high_score = False
        self.build_ui()

    def build_ui(self):
        # Parallax background
        self.bg_parallax = ParallaxWidget()
        self.add_widget(self.bg_parallax)

        # Overlay
        with self.canvas:
            self.overlay_color = Color(0, 0, 0, 0.2)
            self.overlay_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_overlay, size=self.update_overlay)

        # Layout chính
        main_layout = FloatLayout()
        self.add_widget(main_layout)

        # Khung nền ở giữa
        frame_img = Image(
            source='assets/images/backgrounds/gameover_background.png',
            size_hint=(0.9, 0.7),
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            allow_stretch=True,           
            keep_ratio= False  
        )
        main_layout.add_widget(frame_img)

        # ========== YOUR SCORE ROW ========== 
        your_score_row = BoxLayout(
            orientation='horizontal',
            size_hint=(0.8, 0.08),  # 80% chiều ngang, 8% chiều cao
            pos_hint={'center_x': 0.75, 'center_y': 0.53},
            spacing=10,
            # allow_stretch=True,           
            # keep_ratio=False  
        )
        self.your_score_icon = Image(
            source='assets/images/buttons/total_score.png',
            size_hint=(None, 1),  # Chiều cao theo bố mẹ, chiều rộng tự động (hoặc bạn có thể dùng size_hint=(0.1, 1))
            width=40
        )
        your_score_row.add_widget(self.your_score_icon)

        self.your_score_label = Label(
            text='',
            markup=True,
            font_name='assets/fonts/HeehawRegular.ttf',
            font_size='22sp',
            halign='left',
            valign='middle',
            size_hint=(1, 1)
        )
        self.your_score_label.bind(size=self._update_text_align)
        your_score_row.add_widget(self.your_score_label)
        main_layout.add_widget(your_score_row)

        # ========== BEST SCORE ROW ==========
        best_score_row = BoxLayout(
            orientation='horizontal',
            size_hint=(0.8, 0.08),
            pos_hint={'center_x': 0.75, 'center_y': 0.47},
            spacing=10,
            # allow_stretch=True,           
            # keep_ratio=False  
        )
        self.best_score_icon = Image(
            source='assets/images/buttons/best_score.png',
            size_hint=(None, 1),
            width=40
            # opacity=1
        )
        best_score_row.add_widget(self.best_score_icon)

        self.best_score_label = Label(
            text='',
            markup=True,
            font_name='assets/fonts/HeehawRegular.ttf',
            font_size='20sp',
            halign='left',
            valign='middle',
            size_hint=(1, 1)
        )
        self.best_score_label.bind(size=self._update_text_align)
        best_score_row.add_widget(self.best_score_label)
        main_layout.add_widget(best_score_row)

        # ========== NÚT PLAY AGAIN ==========
        play_btn = Button(
            size_hint=(0.2, 0.12),
            pos_hint={'center_x': 0.25, 'center_y': 0.36},
            background_normal='assets/images/buttons/return.png',
            background_color=(1, 1, 1, 1),
            text=''
        )
        play_btn.bind(on_press=self.play_again)
        main_layout.add_widget(play_btn)

        # ========== NÚT MAIN MENU ==========
        home_btn = Button(
            size_hint=(0.2, 0.12),
            pos_hint={'center_x': 0.5, 'center_y': 0.36},
            background_normal='assets/images/buttons/home.png',
            background_color=(1, 1, 1, 1),
            text=''
        )
        home_btn.bind(on_press=self.go_to_main_menu)
        main_layout.add_widget(home_btn)

        # ========== NÚT SHOP ==========
        shop_btn = Button(
            size_hint=(0.25, 0.12),
            pos_hint={'center_x': 0.75, 'center_y': 0.36},
            background_normal='assets/images/buttons/shop.png',
            background_color=(1, 1, 1, 1),
            text=''
        )
        shop_btn.bind(on_press=self.go_to_shop)
        main_layout.add_widget(shop_btn)


    def _update_text_align(self, instance, value):
        instance.text_size = instance.size

    def update_overlay(self, *args):
        self.overlay_rect.pos = self.pos
        self.overlay_rect.size = self.size

    def set_score_data(self, current_score, is_new_high_score):
        self.current_score = current_score
        self.is_new_high_score = is_new_high_score

    def on_enter(self):
        self.update_score_display()
        if self.is_new_high_score:
            self.animate_high_score()

    def update_score_display(self):
        app = App.get_running_app()
        best_score = 0
        if app and hasattr(app, 'data_manager'):
            best_score = app.data_manager.get_best_score()

        self.your_score_label.text = f'[color=ffffff]Your Score: {self.current_score}[/color]'
        self.best_score_label.text = f'[color=cccccc]Best Score: {best_score}[/color]'

        # if self.is_new_high_score:
        #     self.best_score_icon.opacity = 1
        # else:
        #     self.best_score_icon.opacity = 0

    def animate_high_score(self):
        anim = Animation(opacity=0.3, duration=0.5) + Animation(opacity=1, duration=0.5)
        anim.repeat = True
        anim.start(self.best_score_icon)

    def play_again(self, button):
        app = App.get_running_app()
        if app and hasattr(app, 'sound_manager'):
            app.sound_manager.play_sound('button_click')
        Animation.stop_all(self.best_score_icon)
        self.manager.current = 'game'

    def go_to_main_menu(self, button):
        app = App.get_running_app()
        if app and hasattr(app, 'sound_manager'):
            app.sound_manager.play_sound('button_click')
        Animation.stop_all(self.best_score_icon)
        self.manager.current = 'main_menu'

    def go_to_shop(self, button):
        app = App.get_running_app()
        if app and hasattr(app, 'sound_manager'):
            app.sound_manager.play_sound('button_click')
        Animation.stop_all(self.best_score_icon)
        self.manager.current = 'shop'