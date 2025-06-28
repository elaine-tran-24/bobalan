from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.slider import Slider
from kivy.uix.switch import Switch
from kivy.uix.widget import Widget
from kivy.app import App
from kivy.graphics import Color, Rectangle
from kivy.core.window import Window
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.behaviors import ToggleButtonBehavior
from kivy.metrics import dp
from screens.background import ParallaxWidget
from screens.hover_button import HoverImageButton
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image

class ImageSwitch(ToggleButtonBehavior, Image):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.update_source()
        self.bind(state=self.on_state_change)

    def on_state_change(self, *args):
        self.update_source()

    def update_source(self):
        self.source = 'assets/images/buttons/on_sound_effect.png' if self.state == 'down' else 'assets/images/buttons/off_sound_effect.png'

class GameSettingsScreen(Screen):
    """Settings screen for game configuration"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()
    
    def build_ui(self):
        """Build the settings UI"""

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
        
        # Title
        title_label = Label(
            text='[size=100][color=ffffff]Settings[/color][/size]',
            font_name="assets/fonts/HeehawRegular.ttf",
            markup=True,
            size_hint=(1, None),              
            height=dp(60),                    
            halign='center',
            valign='middle',
            pos_hint={'top': 0.9, 'center_x': 0.5}  
)
        main_layout.add_widget(title_label)
        
        # Settings content
        settings_layout = BoxLayout(orientation='vertical', spacing=30, size_hint=(1, 0.6))
        
        # Sound Enable/Disable
        sound_layout = BoxLayout(orientation='horizontal', size_hint=(1, None), height=dp(100), padding=(dp(40), 0, 0, 0))

        sound_label = Label(
            text='[size=30][color=ffffff]Sound Effects:[/color][/size]',
            font_name="assets/fonts/HeeHawRegular.ttf",
            markup=True,
            size_hint=(0.7, 1),
            halign='left',
            valign='middle'
        )
        sound_label.bind(size=sound_label.setter('text_size'))
        sound_layout.add_widget(sound_label)

        # Sound switch
        self.sound_switch = ImageSwitch(
            size_hint=(0.3, 1)
            )
        self.sound_switch.bind(on_press=self.on_sound_toggle)
        sound_layout.add_widget(self.sound_switch)
        
        settings_layout.add_widget(sound_layout)
        
        # Volume Slider
        volume_layout = BoxLayout(orientation='vertical', size_hint=(1, 0.4), padding=(dp(40), 0, 0, 0))
        
        volume_row = BoxLayout(
            orientation='horizontal',
            size_hint=(1, None),
            height=dp(60),  # Đảm bảo đủ cao cho slider
            spacing=20
        )
        
        volume_label = Label(
            text='[size=30][color=ffffff]Volume:[/color][/size]',
            font_name="assets/fonts/HeeHawRegular.ttf",
            markup=True,
            size_hint=(0.25, 1),
            halign='left',
            valign='middle'
        )
        volume_label.bind(size=volume_label.setter('text_size'))
        
        # Volume slider with value display
        
        self.volume_slider = Slider(
            min=0.0,
            max=1.0,
            value=0.8,
            step=0.1,
            size_hint=(0.6, 1),
            height=68,
            background_horizontal="assets/images/buttons/volume_1.png",  
            cursor_image="assets/images/buttons/volume_2.png"  
        )
        self.volume_slider.bind(value=self.on_volume_change)
        
        # Volume value label
        self.volume_value_label = Label(
            text='80%',
            font_size='20sp',
            size_hint=(0.15, 1),
            halign='center',
            valign='middle'
        )
        
        # add row
        volume_row.add_widget(volume_label)
        volume_row.add_widget(self.volume_slider)
        volume_row.add_widget(self.volume_value_label)

        # add row in vertical layout
        volume_layout.add_widget(volume_row)
        settings_layout.add_widget(volume_layout)


        # Reset Data & Return Section
        buttons_row = BoxLayout(
            orientation='vertical',
            size_hint=(1, None),
            height=dp(300),
            spacing=dp(30),
            padding=(dp(40), dp(10), dp(40), dp(10))
        )
        
        reset_btn = HoverImageButton(
            source="assets/images/buttons/reset.png",
            size_hint=(1, None),
            height=dp(80)
        )
        reset_btn.bind(on_press=self.reset_data)
        
        main_layout.add_widget(settings_layout)
        
        # Back button
        back_btn = HoverImageButton(
            source="assets/images/buttons/return.png",
            size_hint=(1, None),
            height=dp(100)
        )
        back_btn.bind(on_press=self.go_back)

        buttons_row.add_widget(reset_btn)
        buttons_row.add_widget(back_btn)

        settings_layout.add_widget(buttons_row)

    def update_overlay(self, *args):
        self.overlay_rect.pos = self.pos
        self.overlay_rect.size = self.size

    def toggle_music_state(self, instance):
        """Handle toggle background music"""
        app = App.get_running_app()
        is_on = instance.state == 'down'
        instance.text = 'Music: ON' if is_on else 'Music: OFF'
        app.data_manager.set_music_enabled(is_on)
        if hasattr(app, 'sound_manager'):
            if is_on:
                app.sound_manager.play_background_music()
            else:
                app.sound_manager.stop_background_music() 

    def update_bg(self, *args):
        """Update background size"""
        self.bg_rect.size = Window.size
    
    def on_enter(self):
        """Called when entering this screen"""
        self.load_settings()
    
    def load_settings(self):
        """Load current settings"""
        app = App.get_running_app()
        if app and hasattr(app, 'data_manager'):
            # Load sound settings
            self.sound_switch.active = app.data_manager.get_sound_enabled()
            
            # Load volume settings
            volume = app.data_manager.get_volume()
            self.volume_slider.value = volume
            self.volume_value_label.text = f'{int(volume * 100)}%'
            # self.music_toggle.state = 'down' if app.data_manager.get_music_enabled() else 'normal'
            # self.music_toggle.text = 'Music: ON' if app.data_manager.get_music_enabled() else 'Music: OFF'

    def on_sound_toggle(self, instance):
        """Handle sound toggle"""
        app = App.get_running_app()
        if app and hasattr(app, 'data_manager'):
            # Toggle sound setting
            value = instance.state == 'down'
            app.data_manager.set_sound_enabled(value)
            # Update sound switch appearance
            if value and hasattr(app, 'sound_manager'):
                app.sound_manager.play_sound('button_click')
    
    def on_volume_change(self, slider, value):
        """Handle volume change"""
        app = App.get_running_app()
        if app and hasattr(app, 'data_manager'):
            app.data_manager.set_volume(value)
            
            # Update volume display
            self.volume_value_label.text = f'{int(value * 100)}%'
            
            # Update sound manager volume
            if hasattr(app, 'sound_manager'):
                app.sound_manager.set_volume(value)
    
    def reset_data(self, button):
        """Reset all game data"""
        app = App.get_running_app()
        if app and hasattr(app, 'data_manager'):
            if hasattr(app, 'sound_manager'):
                app.sound_manager.play_sound('button_click')
            
            # Reset all data to defaults
            app.data_manager.data = app.data_manager.default_data.copy()
            app.data_manager.save_data()
            
            # Reload settings display
            self.load_settings()
            
            # Show confirmation (simple approach)
            button.text = 'DATA RESET!'
            def reset_button_text(dt):
                button.text = 'RESET ALL DATA'
            
            from kivy.clock import Clock
            Clock.schedule_once(reset_button_text, 2.0)
    
    def go_back(self, button):
        app = App.get_running_app()
        if app and hasattr(app, 'sound_manager'):
            app.sound_manager.play_sound('button_click')
        
        # Đảm bảo chỉ resume nếu đang pause
        game_screen = self.manager.get_screen('game')
        if game_screen.is_paused:
            game_screen.resume_game()
        self.manager.current = 'game'
