"""
Tutorial Screen for When Cows Fly
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.app import App
from kivy.graphics import Color, Rectangle
from kivy.core.window import Window

class TutorialScreen(Screen):
    """Tutorial screen explaining game mechanics"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()
    
    def build_ui(self):
        """Build the tutorial UI"""
        # Main layout
        main_layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # Add background
        with self.canvas.before:
            Color(0.1, 0.3, 0.6, 1)  # Dark blue background
            self.bg_rect = Rectangle(size=Window.size, pos=(0, 0))
        
        # Bind to update background on window resize
        self.bind(size=self.update_bg)
        Window.bind(size=self.update_bg)
        
        # Title
        title_label = Label(
            text='[size=36][color=ffffff]How to Play[/color][/size]',
            markup=True,
            size_hint=(1, 0.15),
            halign='center'
        )
        main_layout.add_widget(title_label)
        
        # Scrollable content
        scroll = ScrollView(size_hint=(1, 0.75))
        
        # Content layout
        content_layout = BoxLayout(orientation='vertical', spacing=20, size_hint_y=None)
        content_layout.bind(minimum_height=content_layout.setter('height'))
        
        # Tutorial sections
        sections = [
            {
                'title': '🐄 Controls',
                'content': (
                    '• Tap the screen or press SPACE to make the cow fly up\n'
                    '• The cow will fall down due to gravity\n'
                    '• Keep the cow above ground level to avoid falling!'
                )
            },
            {
                'title': '⚡ Obstacles to Avoid',
                'content': (
                    '• Electric Wire (Yellow): Instant game over if touched\n'
                    '• Holes (Black): Cow falls through, loses 1 life\n'
                    '• Kites (Orange): Floating obstacles, lose 1 life\n'
                    '• Barriers (Brown): Wooden obstacles, lose 1 life'
                )
            },
            {
                'title': '🌱 Collectibles',
                'content': (
                    '• Green Grass: Collect to increase your score\n'
                    '• Each grass gives you 1 point\n'
                    '• Points contribute to your total accumulated score'
                )
            },
            {
                'title': '❤️ Lives System',
                'content': (
                    '• You start with 3 lives (hearts)\n'
                    '• Most obstacles remove 1 life when hit\n'
                    '• Electric wire causes instant game over\n'
                    '• Game ends when all lives are lost'
                )
            },
            {
                'title': '📈 Difficulty Scaling',
                'content': (
                    '• Game speed increases every 50 points\n'
                    '• Obstacles spawn more frequently\n'
                    '• Challenge yourself to beat your high score!'
                )
            },
            {
                'title': '🎯 Scoring',
                'content': (
                    '• Collect grass to earn points\n'
                    '• Beat your personal best score\n'
                    '• Accumulate total points across all games\n'
                    '• Check your progress on the main menu'
                )
            }
        ]
        
        for section in sections:
            # Section title
            section_title = Label(
                text=f'[size=24][color=ffff88]{section["title"]}[/color][/size]',
                markup=True,
                size_hint_y=None,
                height=40,
                halign='left',
                valign='top'
            )
            section_title.bind(size=section_title.setter('text_size'))
            content_layout.add_widget(section_title)
            
            # Section content
            section_content = Label(
                text=f'[size=16][color=ffffff]{section["content"]}[/color][/size]',
                markup=True,
                size_hint_y=None,
                halign='left',
                valign='top'
            )
            section_content.bind(texture_size=section_content.setter('size'))
            section_content.bind(size=section_content.setter('text_size'))
            content_layout.add_widget(section_content)
        
        scroll.add_widget(content_layout)
        main_layout.add_widget(scroll)
        
        # Back button
        back_btn = Button(
            text='BACK TO MENU',
            size_hint=(1, 0.1),
            font_size='20sp',
            background_color=(0.8, 0.4, 0.2, 1)
        )
        back_btn.bind(on_press=self.go_back)
        main_layout.add_widget(back_btn)
        
        self.add_widget(main_layout)
    
    def update_bg(self, *args):
        """Update background size"""
        self.bg_rect.size = Window.size
    
    def go_back(self, button):
        """Go back to main menu"""
        app = App.get_running_app()
        if app and hasattr(app, 'sound_manager'):
            app.sound_manager.play_sound('button_click')
        
        self.manager.current = 'main_menu'