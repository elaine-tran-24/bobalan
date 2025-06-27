"""
Game Over Screen for When Cows Fly
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.app import App
from kivy.graphics import Color, Rectangle
from kivy.core.window import Window
from kivy.animation import Animation

class GameOverScreen(Screen):
    """Game over screen with score display and navigation buttons"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_score = 0
        self.is_new_high_score = False
        self.build_ui()
    
    def build_ui(self):
        """Build the game over UI"""
        # Main layout
        main_layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        
        # Add background
        with self.canvas.before:
            Color(0.2, 0.2, 0.3, 1)  # Dark background
            self.bg_rect = Rectangle(size=Window.size, pos=(0, 0))
        
        # Bind to update background on window resize
        self.bind(size=self.update_bg)
        Window.bind(size=self.update_bg)
        
        # Game Over title
        game_over_label = Label(
            text='[size=42][color=ff4444]GAME OVER[/color][/size]',
            markup=True,
            size_hint=(1, 0.2),
            halign='center'
        )
        main_layout.add_widget(game_over_label)
        
        # New high score label (initially hidden)
        self.high_score_label = Label(
            text='[size=24][color=ffff44]🎉 NEW HIGH SCORE! 🎉[/color][/size]',
            markup=True,
            size_hint=(1, 0.1),
            halign='center',
            opacity=0
        )
        main_layout.add_widget(self.high_score_label)
        
        # Score display
        self.score_display_label = Label(
            text='',
            markup=True,
            size_hint=(1, 0.25),
            halign='center'
        )
        main_layout.add_widget(self.score_display_label)
        
        # Spacer
        main_layout.add_widget(Widget(size_hint=(1, 0.1)))
        
        # Button layout
        button_layout = BoxLayout(orientation='vertical', spacing=15, size_hint=(1, 0.3))
        
        # Play Again button
        play_again_btn = Button(
            text='PLAY AGAIN',
            size_hint=(1, 0.5),
            font_size='22sp',
            background_color=(0.2, 0.8, 0.2, 1)
        )
        play_again_btn.bind(on_press=self.play_again)
        button_layout.add_widget(play_again_btn)
        
        # Main Menu button
        main_menu_btn = Button(
            text='MAIN MENU',
            size_hint=(1, 0.5),
            font_size='20sp',
            background_color=(0.8, 0.4, 0.2, 1)
        )
        main_menu_btn.bind(on_press=self.go_to_main_menu)
        button_layout.add_widget(main_menu_btn)
        
        main_layout.add_widget(button_layout)
        
        # Spacer
        main_layout.add_widget(Widget(size_hint=(1, 0.05)))
        
        self.add_widget(main_layout)
    
    def update_bg(self, *args):
        """Update background size"""
        self.bg_rect.size = Window.size
    
    def set_score_data(self, current_score, is_new_high_score):
        """Set the score data for display"""
        self.current_score = current_score
        self.is_new_high_score = is_new_high_score
    
    def on_enter(self):
        """Called when entering this screen"""
        self.update_score_display()
        if self.is_new_high_score:
            self.animate_high_score()
    
    def update_score_display(self):
        """Update the score display"""
        app = App.get_running_app()
        best_score = 0
        
        if app and hasattr(app, 'data_manager'):
            best_score = app.data_manager.get_best_score()
        
        # Update score text
        score_text = (
            f'[size=28][color=ffffff]Your Score: {self.current_score}[/color][/size]\n\n'
            f'[size=20][color=cccccc]Best Score: {best_score}[/color][/size]'
        )
        
        self.score_display_label.text = score_text
        
        # Show/hide high score label
        if self.is_new_high_score:
            self.high_score_label.opacity = 1
        else:
            self.high_score_label.opacity = 0
    
    def animate_high_score(self):
        """Animate the new high score text"""
        # Pulsing animation
        anim = Animation(opacity=0.3, duration=0.5) + Animation(opacity=1, duration=0.5)
        anim.repeat = True
        anim.start(self.high_score_label)
    
    def play_again(self, button):
        """Start a new game"""
        app = App.get_running_app()
        if app and hasattr(app, 'sound_manager'):
            app.sound_manager.play_sound('button_click')
        
        # Stop any animations
        Animation.stop_all(self.high_score_label)
        
        self.manager.current = 'game'
    
    def go_to_main_menu(self, button):
        """Go back to main menu"""
        app = App.get_running_app()
        if app and hasattr(app, 'sound_manager'):
            app.sound_manager.play_sound('button_click')
        
        # Stop any animations
        Animation.stop_all(self.high_score_label)
        
        self.manager.current = 'main_menu'