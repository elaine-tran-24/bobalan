
#!/usr/bin/env python3
"""
When Cows Fly - A Kivy-based endless runner game
Main entry point for the application
"""

import os
import sys
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from kivy.core.window import Window
Window.size = (Window.system_size[0], Window.system_size[1])

from kivy.logger import Logger
from kivy.clock import Clock

# Import our custom screens
from screens.main_menu_screen import MainMenuScreen
from screens.game_screen import GameScreen
from screens.shop_screen import ShopScreen
from screens.game_over_screen import GameOverScreen
from screens.tutorial_screen import TutorialScreen
from screens.settings_screen import SettingsScreen
from screens.game_settings_screen import GameSettingsScreen
from screens.background import ParallaxApp

# Import utilities
from utils.data_manager import DataManager
from utils.sound_manager import SoundManager
Window.size = (800,600)  # Landscape


class WhenCowsFlyApp(App):
    """Main application class for When Cows Fly game"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.data_manager = DataManager()
        self.sound_manager = SoundManager()
        
    def build(self):
        """Build the main application"""
        # Set window size for desktop (will be ignored on mobile)
        Window.size = (540, 960)  # Landscape

        
        # Bind keyboard events
        Window.bind(on_key_down=self.on_key_down)
        
        # Create screen manager
        self.screen_manager = ScreenManager()
        
        # Add all screens
        self.screen_manager.add_widget(MainMenuScreen(name='main_menu'))
        self.screen_manager.add_widget(GameScreen(name='game'))
        self.screen_manager.add_widget(ShopScreen(name='shop'))
        self.screen_manager.add_widget(GameOverScreen(name='game_over'))
        self.screen_manager.add_widget(TutorialScreen(name='tutorial'))
        self.screen_manager.add_widget(SettingsScreen(name='settings'))
        self.screen_manager.add_widget(GameSettingsScreen(name='game_settings'))
         
        # Set initial screen
        self.screen_manager.current = 'main_menu'
        
        Logger.info("WhenCowsFly: Application built successfully")
        return self.screen_manager
    
    def on_key_down(self, window, key, scancode, codepoint, modifier):
        """Handle keyboard input"""
        # Space bar for flying (key code 32)
        if key == 32:  # Space bar
            current_screen = self.screen_manager.get_screen(self.screen_manager.current)
            if hasattr(current_screen, 'on_space_press'):
                current_screen.on_space_press()
        
        # Back button handling for Android
        elif key == 27:  # Escape/Back button
            return self.on_back_button()
        
        return False
    
    def on_back_button(self):
        """Handle back button press (Android)"""
        current = self.screen_manager.current
        
        if current == 'main_menu':
            # Exit app if on main menu
            return False
        elif current == 'game':
            # Pause game and go to main menu
            game_screen = self.screen_manager.get_screen('game')
            if hasattr(game_screen, 'pause_game'):
                game_screen.pause_game()
            self.screen_manager.current = 'main_menu'
            return True
        else:
            # Go back to main menu from other screens
            self.screen_manager.current = 'main_menu'
            return True
    
    def on_start(self):
        """Called when the app starts"""
        Logger.info("WhenCowsFly: App started")
        # Load saved data
        self.data_manager.load_data()
        # Initialize sound manager
        self.sound_manager.load_sounds()
        self.sound_manager.play_background_music()
    
    def on_stop(self):
        """Called when the app stops"""
        Logger.info("WhenCowsFly: App stopping")
        # Save data before closing
        self.data_manager.save_data()
    
    def on_pause(self):
        """Called when app is paused (Android)"""
        # Pause the game if currently playing
        if self.screen_manager.current == 'game':
            game_screen = self.screen_manager.get_screen('game')
            if hasattr(game_screen, 'pause_game'):
                game_screen.pause_game()
        return True
    
    def on_resume(self):
        if self.screen_manager.current == 'game':
            game_screen = self.screen_manager.get_screen('game')
            if hasattr(game_screen, 'resume_game'):
                game_screen.resume_game()
print("window.width", Window.width, "window.height", Window.height)
if __name__ == '__main__':
    WhenCowsFlyApp().run()