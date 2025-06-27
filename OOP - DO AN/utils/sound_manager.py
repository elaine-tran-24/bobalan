"""
Sound Manager for When Cows Fly
Handles loading and playing sound effects
"""

import os
import random
from kivy.core.audio import SoundLoader
from kivy.logger import Logger
from kivy.app import App


class SoundManager:
    """Manages sound effects for the game"""
    
    def __init__(self):
        self.sounds = {}
        self.sound_files = {
            'fly': 'fly.wav',
            'hit': 'hit.wav',
            'collect': 'collect.wav',
            'game_over': 'game_over.wav',
            'button_click': 'button.wav'
        }
        self.music_tracks = [f'background_{i}.mp3' for i in range(1, 7)]
        self.current_music = None
        self.background_music = None

    
    def play_background_music(self):
        app = App.get_running_app()
        if app and hasattr(app, 'data_manager'):
            if not app.data_manager.get_music_enabled():
                return

        if self.current_music and self.current_music.state == 'play':
            return  # Already playing

        music_file = random.choice(self.music_tracks)
        music_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'sounds','background_musics', music_file)

        if os.path.exists(music_path):
            self.current_music = SoundLoader.load(music_path)
            if self.current_music:
                self.current_music.loop = True
                self.current_music.volume = app.data_manager.get_volume() if app else 0.8
                self.current_music.play()
                Logger.info(f"SoundManager: Playing background music: {music_file}")
        else:
            Logger.warning(f"SoundManager: Background music file not found: {music_path}")

    def stop_background_music(self):
        if self.current_music:
            self.current_music.stop()
            self.current_music = None

    def load_sounds(self):
        assets_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'sounds')
        
        for sound_name, filename in self.sound_files.items():
            sound_path = os.path.join(assets_dir, filename)
            
            # Create placeholder sound file if it doesn't exist
            if not os.path.exists(sound_path):
                self.create_placeholder_sound(sound_path)
            
            try:
                sound = SoundLoader.load(sound_path)
                if sound:
                    self.sounds[sound_name] = sound
                    Logger.info(f"SoundManager: Loaded {sound_name}")
                else:
                    Logger.warning(f"SoundManager: Failed to load {sound_name}")
            except Exception as e:
                Logger.error(f"SoundManager: Error loading {sound_name}: {e}")
    
    # def create_placeholder_sound(self, sound_path):
    #     """Create a placeholder sound file"""
    #     try:
    #         # Ensure directory exists
    #         os.makedirs(os.path.dirname(sound_path), exist_ok=True)
            
    #         # Create a very simple WAV file (just header, no actual audio)
    #         # This is a minimal 44-byte WAV header for a silent sound
    #         wav_header = b'RIFF$\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x44\xac\x00\x00\x88X\x01\x00\x02\x00\x10\x00data\x00\x00\x00\x00'
            
    #         with open(sound_path, 'wb') as f:
    #             f.write(wav_header)
            
    #         Logger.info(f"SoundManager: Created placeholder sound: {sound_path}")
    #     except Exception as e:
    #         Logger.error(f"SoundManager: Error creating placeholder sound: {e}")
    
    def play_sound(self, sound_name):
        """Play a sound effect"""
        try:
            # Check if sound is enabled
            app = App.get_running_app()
            if app and hasattr(app, 'data_manager'):
                if not app.data_manager.get_sound_enabled():
                    return
                
                volume = app.data_manager.get_volume()
            else:
                volume = 0.8
            
            if sound_name in self.sounds and self.sounds[sound_name]:
                sound = self.sounds[sound_name]
                sound.volume = volume
                sound.play()
                Logger.debug(f"SoundManager: Played {sound_name}")
        except Exception as e:
            Logger.error(f"SoundManager: Error playing {sound_name}: {e}")
    
    def stop_all_sounds(self):
        """Stop all currently playing sounds"""
        try:
            for sound in self.sounds.values():
                if sound:
                    sound.stop()
        except Exception as e:
            Logger.error(f"SoundManager: Error stopping sounds: {e}")
    
    def set_volume(self, volume):
        """Set volume for all sounds and background music"""
        try:
            volume = max(0.0, min(1.0, volume))
            
            # Cập nhật sound effect
            for sound in self.sounds.values():
                if sound:
                    sound.volume = volume
            
            # Cập nhật background music nếu đang phát
            if self.current_music and self.current_music.state == 'play':
                self.current_music.volume = volume

        except Exception as e:
            Logger.error(f"SoundManager: Error setting volume: {e}")
