"""
Settings Screen for When Cows Fly
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.slider import Slider
from kivy.uix.switch import Switch
from kivy.uix.widget import Widget
from kivy.app import App
from kivy.graphics import Color, Rectangle
from kivy.core.window import Window
from kivy.uix.togglebutton import ToggleButton
from kivy.metrics import dp


class SettingsScreen(Screen):
    """Settings screen for game configuration"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()
    
    def build_ui(self):
        """Build the settings UI"""
        # Main layout
        main_layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        
        # Add background
        with self.canvas.before:
            Color(0.2, 0.3, 0.5, 1)  # Blue-gray background
            self.bg_rect = Rectangle(size=Window.size, pos=(0, 0))
        
        # Bind to update background on window resize
        self.bind(size=self.update_bg)
        Window.bind(size=self.update_bg)
        
        # Title
        title_label = Label(
            text='[size=36][color=ffffff]Settings[/color][/size]',
            markup=True,
            size_hint=(1, 0.15),
            halign='center'
        )
        main_layout.add_widget(title_label)
        
        # Settings content
        settings_layout = BoxLayout(orientation='vertical', spacing=30, size_hint=(1, 0.6))
        
        # Sound Enable/Disable
        sound_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.3))
        
        sound_label = Label(
            text='[size=20][color=ffffff]Sound Effects:[/color][/size]',
            markup=True,
            size_hint=(0.7, 1),
            halign='left'
        )
        sound_label.bind(size=sound_label.setter('text_size'))
        sound_layout.add_widget(sound_label)
        
        self.sound_switch = Switch(
            size_hint=(0.3, 1),
            active=True
        )
        self.sound_switch.bind(active=self.on_sound_toggle)
        sound_layout.add_widget(self.sound_switch)
        
        settings_layout.add_widget(sound_layout)
        
        # Volume Slider
        volume_layout = BoxLayout(orientation='vertical', size_hint=(1, 0.4))
        
        volume_label = Label(
            text='[size=20][color=ffffff]Volume:[/color][/size]',
            markup=True,
            size_hint=(1, 0.3),
            halign='left'
        )
        volume_label.bind(size=volume_label.setter('text_size'))
        volume_layout.add_widget(volume_label)
        
        # Volume slider with value display
        slider_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.7))
        
        self.volume_slider = Slider(
            min=0.0,
            max=1.0,
            value=0.8,
            step=0.1,
            size_hint=(0.8, 1)
        )
        self.volume_slider.bind(value=self.on_volume_change)
        slider_layout.add_widget(self.volume_slider)
        
        self.volume_value_label = Label(
            text='80%',
            size_hint=(0.2, 1),
            halign='center'
        )
        slider_layout.add_widget(self.volume_value_label)
        
        volume_layout.add_widget(slider_layout)
        settings_layout.add_widget(volume_layout)
        
        # Reset Data Section
        reset_layout = BoxLayout(orientation='vertical', size_hint=(1, 0.3))
        
        reset_label = Label(
            text='[size=18][color=ffcccc]Reset Game Data:[/color][/size]',
            markup=True,
            size_hint=(1, 0.4),
            halign='center'
        )
        reset_layout.add_widget(reset_label)
        
        reset_btn = Button(
            text='RESET ALL DATA',
            size_hint=(1, 0.6),
            font_size='16sp',
            background_color=(0.8, 0.2, 0.2, 1)
        )
        reset_btn.bind(on_press=self.reset_data)
        reset_layout.add_widget(reset_btn)
        
        settings_layout.add_widget(reset_layout)
        
        main_layout.add_widget(settings_layout)
        
        # Spacer
        main_layout.add_widget(Widget(size_hint=(1, 0.1)))
        
        # Back button
        back_btn = Button(
            text='BACK TO MENU',
            size_hint=(1, 0.15),
            font_size='20sp',
            background_color=(0.4, 0.6, 0.8, 1)
        )
        back_btn.bind(on_press=self.go_back)
        main_layout.add_widget(back_btn)
        
        self.add_widget(main_layout)

        # Music background toggle
        app = App.get_running_app()
        self.music_toggle = ToggleButton(
            text='Music: ON' if app.data_manager.get_music_enabled() else 'Music: OFF',
            state='down' if app.data_manager.get_music_enabled() else 'normal',
            size_hint=(1, 0.2),
            height=dp(40)
        )
        self.music_toggle.bind(on_press=self.toggle_music_state)
        settings_layout.add_widget(self.music_toggle)

    
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
            self.music_toggle.state = 'down' if app.data_manager.get_music_enabled() else 'normal'
            self.music_toggle.text = 'Music: ON' if app.data_manager.get_music_enabled() else 'Music: OFF'

    def on_sound_toggle(self, switch, value):
        """Handle sound toggle"""
        app = App.get_running_app()
        if app and hasattr(app, 'data_manager'):
            app.data_manager.set_sound_enabled(value)
            
            # Play test sound if enabled
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
        """Go back to main menu"""
        app = App.get_running_app()
        if app and hasattr(app, 'sound_manager'):
            app.sound_manager.play_sound('button_click')
        
        self.manager.current = 'main_menu'