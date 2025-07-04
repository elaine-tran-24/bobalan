"""
Updated Game Screen for When Cows Fly - With Animated Sprites
Main gameplay screen with animated cow, obstacles, and game logic
"""

import random
from kivy.resources import resource_find
from kivy.uix.screenmanager import Screen
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.app import App
from kivy.vector import Vector
from kivy.metrics import dp
from kivy.uix.image import Image
from kivy.uix.widget import Widget
from screens.background import ParallaxWidget
from kivy.uix.behaviors import ButtonBehavior

# Import our animated sprite classes
from screens.animated_sprites import AnimatedCow, AnimatedKite

GRAVITY = 600
JUMP_STRENGTH = 400
GROUND_LEVEL = dp(100)
OBSTACLE_SPEED = 300

class ImageButton(ButtonBehavior, Image):
    pass

class Obstacle(Widget):
    """Enhanced obstacle class with special behaviors"""

    def __init__(self, obstacle_type, **kwargs):
        super().__init__(**kwargs)
        self.obstacle_type = obstacle_type
        self.speed = OBSTACLE_SPEED
        self.size_hint = (None, None)
        
        # Special physics for different obstacles
        self.velocity_y = 0
        self.gravity = 0
        self.rotation_speed = 0

        # Set size and position based on obstacle type
        if self.obstacle_type == 'electric_wire':
            self.size = (Window.width, Window.width * 0.033)
            self.path = "assets/images/obstacles/wire.png"
            self.pos = (0, Window.height-50)

        elif self.obstacle_type == 'hole':
            self.size = (dp(300), dp(GROUND_LEVEL))
            self.path = "assets/images/obstacles/hole.png"
            self.pos = (Window.width, 0)
            self.speed = 300
            
        elif self.obstacle_type == 'barrier':
            self.size = (dp(200), dp(230))
            self.pos = (Window.width, GROUND_LEVEL)
            self.path = "assets/images/obstacles/barrier.png"

        elif self.obstacle_type == 'kite':
            # For kite, we'll use AnimatedKite instead of regular obstacle
            return

        elif self.obstacle_type == 'bird':
            self.size = (dp(70), dp(93))
            self.pos = (Window.width, random.randint(
                int(GROUND_LEVEL + 40),
                int(Window.height - 80)
            ))
            self.speed = 1200
            self.path = "assets/images/obstacles/bird.png"

        self.initial_y = self.y
        self.rotation_angle = 0
        
        # Create image once and store reference
        self.image = Image(source=resource_find(self.path), size=self.size, pos=self.pos)
        self.add_widget(self.image)
        self.bind(pos=self.update_graphics)
        
    def update_graphics(self, *args):
        if hasattr(self, 'image'):
            self.image.pos = self.pos

    def update(self, dt, speed_multiplier=1.0):
        if self.obstacle_type == 'electric_wire':
            return False
        
        self.x -= self.speed * speed_multiplier * dt
        
        if self.obstacle_type == 'bird':
            bob_amplitude = 20
            bob_frequency = 5
            time_factor = (Window.width - self.x) * 0.01
            self.rotation_angle += 120 * dt
        
        return self.x < -self.width

class Collectible(Widget):
    """Collectible grass item"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.speed = 200
        self.size = (dp(50), dp(50))
        self.pos = (Window.width, random.randint(80, Window.height - 80))
        self.size_hint = (None, None)

        self.image = Image(
            source="assets/images/obstacles/collectible.png",
            size=self.size,
            size_hint=(None, None),
            pos=self.pos
        )
        self.add_widget(self.image)
        self.bind(pos=self.update_graphics)

    def update_graphics(self, *args):
        self.image.pos = self.pos
        
    def update(self, dt, speed_multiplier=1.0):
        self.x -= self.speed * speed_multiplier * dt
        return self.x < -self.width

class GameScreen(Screen):
    """Main game screen with animated sprites"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.game_running = False
        self.score = 0
        self.lives = 3
        self.speed_multiplier = 1.0
        self.obstacles = []
        self.collectibles = []
        self.spawn_timer = 0
        self.collectible_spawn_timer = 0

        self.cow = None
        self.parallax = None
        self.build_ui()
        self.is_paused = False

    def build_ui(self):
        """Build the game UI"""
        
        # UI Layout
        ui_layout = BoxLayout(
            orientation='horizontal',
            size_hint=(1, 0.1),
            pos_hint={'top': 1},
            padding=[dp(20), dp(10)],
            spacing=dp(10)
        )
        
        # Score display
        self.score_label = Label(
            text='Score: 0',
            font_size='30sp',
            color=(0.345, 0.192, 0.004, 1),  # #583101
            font_name=resource_find('assets/fonts/HeehawRegular.ttf'),
            markup=True,
            size_hint=(0.7, 1),
            halign='left',
            valign='middle',
        )
        self.score_label.bind(size=self._update_label_text_align)

        # Lives UI
        self.hearts = []
        self.hearts_layout = BoxLayout(
            orientation='horizontal',
            size_hint=(None, None),
            size=(dp(120), dp(40)),
            spacing=dp(5),
            pos_hint={'x': 0.01, 'top': 0.95}
        )

        for _ in range(3):
            heart = Image(source=resource_find('assets/images/icons/live.png'), size_hint=(None, None), size=(dp(40), dp(40)))
            self.hearts.append(heart)
            self.hearts_layout.add_widget(heart)

        ui_layout.add_widget(self.score_label)
        ui_layout.add_widget(self.hearts_layout)
        self.add_widget(ui_layout)
        
        # Settings icon
        self.game_settings_btn = ImageButton(
            source=resource_find('assets/images/buttons/setting.png'),
            size_hint=(None, None),
            size=(dp(80), dp(80)),
            pos_hint={'right': 0.98, 'y': 0.02}
        )
        self.game_settings_btn.bind(on_press=self.show_settings)
        self.add_widget(self.game_settings_btn, index=0)

    def _update_label_text_align(self, instance, value):
        instance.text_size = instance.size

    def on_enter(self):
        """Called when entering the game screen"""
        if self.is_paused:
            self.resume_game()
        else:
            self.start_game()
            App.get_running_app().sound_manager.play_background_music()
    
    def on_leave(self):
        """Called when leaving the game screen"""
        self.stop_game()
    
    def start_game(self):
        """Start the game"""
        self.game_running = True
        self.score = 0
        self.lives = 3
        self.speed_multiplier = 1.0
        self.spawn_timer = 0
        self.collectible_spawn_timer = 0

        # Get skin and background
        app = App.get_running_app()
        skin_id = app.data_manager.get_equipped_skin()
        print("Equipped skin_id:", skin_id)
        
        # Create new AnimatedCow with skin
        if hasattr(self, 'cow') and self.cow:
            self.cow.stop_animation()  # Stop animation before removing
            self.remove_widget(self.cow)

        # Create animated cow with the selected skin
        self.cow = AnimatedCow(skin_id=skin_id or "bo", size_hint=(None, None), size=(dp(200), dp(137)))
        self.cow.pos = (dp(100), GROUND_LEVEL)
        self.cow.game_started = False
        self.add_widget(self.cow)
        print("Added animated cow with skin:", skin_id)

        # Create parallax background
        if hasattr(self, 'parallax') and self.parallax:
            self.remove_widget(self.parallax)
        
        self.parallax = ParallaxWidget(cow=self.cow)
        self.add_widget(self.parallax, index=len(self.children))  # Add to back

        # Clear old obstacles and collectibles
        for obstacle in self.obstacles:
            if hasattr(obstacle, 'stop_animation'):
                obstacle.stop_animation()
            self.remove_widget(obstacle)
        for collectible in self.collectibles:
            self.remove_widget(collectible)
        self.obstacles.clear()
        self.collectibles.clear()

        self.spawn_obstacle('electric_wire')

        # UI
        self.update_ui()

        # Game loop
        Clock.schedule_interval(self.update_game, 1.0 / 60.0)

    def stop_game(self):
        """Stop the game"""
        self.game_running = False
        Clock.unschedule(self.update_game)
        
        # Stop all animations
        if self.cow:
            self.cow.stop_animation()
        for obstacle in self.obstacles:
            if hasattr(obstacle, 'stop_animation'):
                obstacle.stop_animation()
    
    def pause_game(self):
        if self.game_running and not self.is_paused:  
            Clock.unschedule(self.update_game)
            self.game_running = False
            self.is_paused = True
            # Pause animations
            if self.cow:
                self.cow.stop_animation()
            for obstacle in self.obstacles:
                if hasattr(obstacle, 'stop_animation'):
                    obstacle.stop_animation()
            
    def resume_game(self):
        if not self.game_running and self.is_paused:
            Clock.schedule_interval(self.update_game, 1.0 / 60.0)
            self.game_running = True
            self.is_paused = False
            # Resume animations
            if self.cow:
                self.cow.start_animation()
            for obstacle in self.obstacles:
                if hasattr(obstacle, 'start_animation'):
                    obstacle.start_animation()

    def update_game(self, dt):
        """Main game update loop"""
        if not self.game_running:
            return
        
        # Update cow
        if self.cow:
            self.cow.update(dt)
        
        # Only spawn obstacles and update game elements after cow starts moving
        if not self.cow or not self.cow.game_started:
            return
        
        # Update speed based on score
        self.speed_multiplier = 1.0 + (self.score // 50) * 0.2
        
        # Spawn obstacles
        self.spawn_timer += dt
        if self.spawn_timer >= 5.0 / self.speed_multiplier:
            self.spawn_obstacle()
            self.spawn_timer = 0
        
        # Spawn collectibles
        self.collectible_spawn_timer += dt
        if self.collectible_spawn_timer >= 3.0:
            self.spawn_collectible()
            self.collectible_spawn_timer = 0
        
        # Update obstacles
        for obstacle in self.obstacles[:]:
            if obstacle.update(dt, self.speed_multiplier):
                if hasattr(obstacle, 'stop_animation'):
                    obstacle.stop_animation()
                self.remove_widget(obstacle)
                self.obstacles.remove(obstacle)
            else:
                self.check_collision(obstacle)
        
        # Update collectibles
        for collectible in self.collectibles[:]:
            if collectible.update(dt, self.speed_multiplier):
                self.remove_widget(collectible)
                self.collectibles.remove(collectible)
            else:
                self.check_collectible_collision(collectible)
    
    def spawn_obstacle(self, obstacle_type=None):
        """Spawn a random obstacle"""
        if obstacle_type is None:
            obstacle_types = ['hole', 'kite', 'bird', 'barrier', 'electric_wire']
            obstacle_type = random.choice(obstacle_types)
        
        if obstacle_type == 'kite':
            # Create animated kite
            obstacle = AnimatedKite(size_hint=(None, None))
            obstacle.obstacle_type = 'kite'  # Set type for collision detection
        else:
            obstacle = Obstacle(obstacle_type=obstacle_type)
        
        self.obstacles.append(obstacle)
        try:
            cow_index = self.children.index(self.cow)
            if obstacle.obstacle_type == 'hole':
                self.add_widget(obstacle, index=cow_index + 1)
            else:
                self.add_widget(obstacle, index=cow_index)
        except ValueError:
            self.add_widget(obstacle)    
            
    def spawn_collectible(self):
        """Spawn a collectible grass"""
        collectible = Collectible()
        self.collectibles.append(collectible)
        try:
            cow_index = self.children.index(self.cow)
            self.add_widget(collectible, index=cow_index + 1)
        except ValueError:
            self.add_widget(collectible)    
    
    def is_spawn_position_safe(self):
        """Check if the cow's spawn position is safe from holes"""
        if not self.cow:
            return True
            
        cow_spawn_center_x = self.cow.original_x + self.cow.width / 2
        
        for obstacle in self.obstacles:
            if hasattr(obstacle, 'obstacle_type') and obstacle.obstacle_type == 'hole':
                hole_left = obstacle.x
                hole_right = obstacle.right
                
                # Check if spawn position overlaps with hole
                if hole_left <= cow_spawn_center_x <= hole_right:
                    return False
        return True
            
    def check_collision(self, obstacle):
        """Check collision between cow and obstacle"""
        if not self.cow or not self.cow.collide_widget(obstacle):
            return
            
        print('o no, cow hit an obstacle!')
        app = App.get_running_app()
        
        obstacle_type = getattr(obstacle, 'obstacle_type', 'unknown')
        
        if obstacle_type == 'electric_wire':
            self.cow.start_falling(obstacle_type)
            self.play_sound_async('game_over')
            self.game_over()
            return
        
        elif obstacle_type == 'hole':
            # When cow collides with hole, move it to center first, then fall
            hole_center_x = obstacle.x + obstacle.width / 2
            cow_center_offset = self.cow.width / 2
            
            # Move cow to center of hole before falling
            self.cow.x = hole_center_x - cow_center_offset
            self.cow.start_falling('hole')
            print('Cow hit hole! Moving to center and falling.')
            return
        
        else:
            self.play_sound_async('hit')
            # Make cow fall
            self.cow.start_falling('hit')
            
            # Remove obstacle
            if hasattr(obstacle, 'stop_animation'):
                obstacle.stop_animation()
            self.remove_widget(obstacle)
            self.obstacles.remove(obstacle)
            
            # Lose life after a short delay
            Clock.schedule_once(lambda dt: self.lose_life(), 0.5)
    
    def lose_life(self):
        """Lose a life"""
        self.lives -= 1
        self.update_ui()
        
        # Reset cow to ground
        if self.cow:
            self.cow.reset_to_ground()
            self.cow.pos = (100, self.cow.ground_level)
        
        if self.lives <= 0:
            self.game_over()
    
    def check_collectible_collision(self, collectible):
        """Check collision between cow and collectible"""
        if self.cow and self.cow.collide_widget(collectible):
            self.score += 1
            self.update_ui()
            self.remove_widget(collectible)
            self.collectibles.remove(collectible)
    
    def play_sound_async(self, sound_name):
        """Play sound without blocking the game"""
        try:
            app = App.get_running_app()
            if app and hasattr(app, 'sound_manager'):
                app.sound_manager.play_sound(sound_name)
        except Exception:
            # Silently ignore sound errors to prevent game crashes
            pass
    
    def game_over(self):
        """Handle game over"""
        self.stop_game()
        
        # Save score data
        app = App.get_running_app()
        if app and hasattr(app, 'data_manager'):
            app.data_manager.add_points(self.score)
            is_new_high_score = self.score > app.data_manager.get_best_score()
            app.data_manager.set_best_score(self.score)
            
            # Pass data to game over screen
            game_over_screen = self.manager.get_screen('game_over')
            game_over_screen.set_score_data(self.score, is_new_high_score)
        
        self.manager.current = 'game_over'
    
    def update_ui(self):
        # Update lives display
        for i in range(3):
            if i < self.lives:
                self.hearts[i].source = 'assets/images/icons/live.png'
            else:
                self.hearts[i].source = 'assets/images/icons/die.png'

        # Update score
        self.score_label.text = f'Score: {self.score}'

    def on_touch_down(self, touch):
        """Handle touch input"""
        if super().on_touch_down(touch):
            return True

        if self.game_running and self.cow:
            self.cow.jump()
            return True  

        return False
    
    def on_space_press(self):
        """Handle space bar press"""
        if self.game_running and self.cow:
            self.cow.jump()

    def show_settings(self, *args):
        self.pause_game()
        self.manager.current = 'game_settings'