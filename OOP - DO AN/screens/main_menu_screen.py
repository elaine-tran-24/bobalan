"""
Main Menu Screen for When Cows Fly
"""
import os
from kivy.uix.screenmanager import Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.image import Image
from screens.hover_button import HoverImageButton 
from kivy.uix.behaviors import ButtonBehavior
from screens.background import ParallaxWidget  

class ImageButton(ButtonBehavior, Image):
    pass

class MainMenuScreen(Screen):
    """Main menu screen with background, title, cow image, buttons, and score"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()
        self.music_tracks = [f'background_{i}.mp3' for i in range(1, 7)]
        self.current_music = None


    def build_ui(self):
        self.bg_parallax = ParallaxWidget()
        self.add_widget(self.bg_parallax)
        # 2. Layout gốc
        main_layout = FloatLayout()
        self.add_widget(main_layout)

        # 3. Layout dọc chính
        vertical_layout = BoxLayout(
            orientation='vertical',
            padding=20,
            spacing=20,
            size_hint=(1, 1)
        )

        # 4. Cow Preview
        self.cow_preview = Image(source="assets/images/characters/logo.png",size_hint=(None, None), size=(500, 400), allow_stretch=True, keep_ratio=True)
        self.preview_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.4), spacing=20, padding=[0, 20])
        self.preview_layout.add_widget(Widget(size_hint=(0.5, 1)))  # spacer trái
        self.preview_layout.add_widget(self.cow_preview)
        self.preview_layout.add_widget(Widget(size_hint=(0.5, 1)))  # spacer phải

        # 6. Score
        self.score_label = Label(
            text='',
            markup=True,
            size_hint=(1, 0.15),
            halign='center'
        )

        # 7. Buttons
        button_layout = BoxLayout(orientation='vertical', spacing=5, size_hint=(1, 0.45))

        play_btn = ImageButton(source='assets/images/buttons/play_button.png', size_hint=(None, None), size=(200, 100), allow_stretch=True)
        shop_btn = ImageButton(source='assets/images/buttons/shop_button.png', size_hint=(None, None), size=(200, 100), allow_stretch=True)
        tutorial_btn = ImageButton(source='assets/images/buttons/tutorial_button.png', size_hint=(None, None), size=(200, 100), allow_stretch=True)

        for btn in [play_btn, shop_btn, tutorial_btn]:
            btn.pos_hint = {'center_x': 0.5}

        play_btn.bind(on_press=self.start_game)
        shop_btn.bind(on_press=self.open_shop)
        tutorial_btn.bind(on_press=self.show_tutorial)

        button_layout.add_widget(play_btn)
        button_layout.add_widget(shop_btn)
        button_layout.add_widget(tutorial_btn)

        # 8. Add các thành phần vào vertical_layout
        vertical_layout.add_widget(self.preview_layout)
        vertical_layout.add_widget(self.score_label)
        vertical_layout.add_widget(button_layout)

        # 9. Thêm layout chính
        main_layout.add_widget(vertical_layout)

        # 10. Settings icon
        settings_btn = ImageButton(
            source='assets/images/buttons/setting.png',
            size_hint=(None, None),
            size=(80, 80),
            pos_hint={'right': 0.98, 'y': 0.02}
        )
        settings_btn.bind(on_press=self.show_settings)
        main_layout.add_widget(settings_btn)

        # 11. Auto resize background
        Window.bind(size=self.update_bg_image)

    #     # Background image
    #     self.bg_image = Image(
    #         source='assets/images/backgrounds/background_1.png',  # Sửa đúng đường dẫn và không có dấu cách
    #         allow_stretch=True,
    #         keep_ratio=False,
    #         size=Window.size,
    #         size_hint=(None, None),
    #         pos=(0, 0)
    #     )
    #     self.bg_image.size_hint = (None, None)
    #     self.bg_image.size = Window.size
    #     self.add_widget(self.bg_image)

    #     # Main layout
    #     main_layout = FloatLayout()
    #     self.add_widget(main_layout)

    #    # Tạo layout dọc để chứa các thành phần chính
    #     vertical_layout = BoxLayout(
    #         orientation='vertical',
    #         padding=20,
    #         spacing=20,
    #         size_hint=(1, 1)
    #     )

    #     # Giả sử các widget này đã được tạo trước đó:
    #     # self.preview_layout = Widget()  hoặc Image() chẳng hạn
    #     # title_label = Label(text="When Cows Fly")
    #     # self.score_label = Label(text="Best Score: 0")
    #     # button_layout = BoxLayout(orientation='horizontal') ...

        
    #     # Sau đó thêm vertical_layout vào màn hình hoặc layout cha
    #     self.add_widget(vertical_layout)

    #     # --- PREVIEW AREA ---
      
    #     self.preview_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.4), spacing=10, padding=[0, 20])
    #     self.preview_layout.add_widget(Widget(size_hint=(0.5, 1)))  # spacer trái
    #     self.preview_layout.add_widget(self.cow_preview)
    #     self.preview_layout.add_widget(Widget(size_hint=(0.5, 1)))  # spacer phải

    #     self.cow_preview = Image(size_hint=(None, None), size=(300, 200), allow_stretch=True, keep_ratio=True)

    #     vertical_layout.add_widget(self.preview_layout)
    #     vertical_layout.add_widget(title_label)
    #     vertical_layout.add_widget(self.score_label)
    #     vertical_layout.add_widget(button_layout)


    #     self.preview_layout.add_widget(self.cow_preview)
    #     main_layout.add_widget(self.preview_layout)


    #     # Game title
    #     title_label = Label(
    #         text='[size=48][color=ffffff]When Cows Fly[/color][/size]',
    #         markup=True,
    #         size_hint=(1, 0.15),
    #         halign='center'
    #     )
    #     main_layout.add_widget(title_label)

        
    #     # Score display
    #     self.score_label = Label(
    #         text='',
    #         markup=True,
    #         size_hint=(1, 0.15),
    #         halign='center'
    #     )
    #     main_layout.add_widget(self.score_label)

    #     # Button layout
    #     button_layout = BoxLayout(orientation='vertical', spacing=15, size_hint=(1, 0.45))

    #     # PLAY button
    #     play_btn = HoverButton(text='PLAY', font_size='24sp', size_hint=(1, 0.25))
    #     play_btn.bind(on_press=self.start_game)
    #     button_layout.add_widget(play_btn)

    #     # SHOP button
    #     shop_btn = HoverButton(text='SHOP', font_size='20sp', size_hint=(1, 0.25))
    #     shop_btn.bind(on_press=self.open_shop)
    #     button_layout.add_widget(shop_btn)

    #     # TUTORIAL button
    #     tutorial_btn = HoverButton(text='TUTORIAL', font_size='20sp', size_hint=(1, 0.25))
    #     tutorial_btn.bind(on_press=self.show_tutorial)
    #     button_layout.add_widget(tutorial_btn)
        
    #     for btn in [play_btn, shop_btn, tutorial_btn]:
    #         btn.size_hint = (None, None)
    #         btn.size = (200, 60)
    #         btn.pos_hint = {'center_x': 0.5}

        
        
    #     # SETTINGS button
    #     # settings_btn = HoverButton(text='SETTINGS', font_size='20sp', size_hint=(1, 0.25))
    #     # settings_btn.bind(on_press=self.show_settings)
    #     # button_layout.add_widget(settings_btn)
    #     settings_btn = ImageButton(source='assets/images/icons/settings_icon.png',
    #                        size_hint=(None, None), size=(80, 80),
    #                        pos_hint={'right': 0.98, 'y': 0.02})  # Góc dưới phải

    #     settings_btn.bind(on_press=self.show_settings)
    #     main_layout.add_widget(settings_btn)

    #     # Spacer
    #     main_layout.add_widget(Widget(size_hint=(1, 0.05)))

    #     Window.bind(size=self.update_bg_image)


    def on_enter(self):
        """Update score, skin, and effect when screen is entered"""
        self.update_score_display()
        self.update_preview()
        

    def update_score_display(self):
        """Get score and total points from DataManager"""
        app = App.get_running_app()
        if app and hasattr(app, 'data_manager'):
            best = app.data_manager.get_best_score()
            pts = app.data_manager.get_total_points()
            self.score_label.font_name = "assets/fonts/HeehawRegular.ttf"
            self.score_label.text = (
                f'[size=40][color=ffffff]Best Score: {best}[/color][/size]\n'
                f'[size=30][color=ffffaa]Total Points: {pts}[/color][/size]'
            )

    def update_preview(self):
        """Update skin and effect preview"""
        app = App.get_running_app()
        dm = app.data_manager

        skin_id = dm.get_equipped_skin()
                
        # Load cow skin image preview
        skin_path = f"assets/images/characters/{skin_id}.png" if skin_id else "assets/images/characters/bo.gif"
        
    # def on_pre_enter(self):
    #     """Update preview before entering"""
    #     app = App.get_running_app()
    #     dm = app.data_manager

    #     skin_id = dm.get_equipped_skin()
    #     bg_id = dm.get_equipped_background()

    #     # Set default values if not chosen
    #     skin_path = f"assets/images/characters/{skin_id}.png" if skin_id else "assets/images/characters/bo.png"
    #     bg_path = f"assets/images/backgrounds/{bg_id}.png" if bg_id else "assets/images/backgrounds/background_1.png"

    #     # Preview character and background
    #     if os.path.exists(skin_path):
    #         self.cow_preview.source = skin_path
    #     else:
    #         self.cow_preview.source = "assets/images/characters/bo.png"
        
    #     if os.path.exists(bg_path):
    #         self.bg_image.source = bg_path
    #     else:
    #         self.bg_image.source = "assets/images/backgrounds/background_1.png"

        
    def start_game(self, instance):
        app = App.get_running_app()
        if hasattr(app, 'sound_manager'):
            app.sound_manager.play_sound('button_click')
        self.manager.current = 'game'

    def open_shop(self, instance):
        app = App.get_running_app()
        if hasattr(app, 'sound_manager'):
            app.sound_manager.play_sound('button_click')
        self.manager.current = 'shop'

    def show_tutorial(self, instance):
        app = App.get_running_app()
        if hasattr(app, 'sound_manager'):
            app.sound_manager.play_sound('button_click')
        self.manager.current = 'tutorial'

    def show_settings(self, instance):
        app = App.get_running_app()
        if hasattr(app, 'sound_manager'):
            app.sound_manager.play_sound('button_click')
        self.manager.current = 'settings'

    def update_bg_image(self, *args):
        if hasattr(self, 'bg_parallax'):
            self.bg_parallax.on_resize()  # hoặc update_size(Window.size) nếu bạn có hàm đó
