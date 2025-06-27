"""
Game Screen for When Cows Fly with Parallax Background
Main gameplay screen with cow, obstacles, and parallax background
"""
GRAVITY = 600
JUMP_STRENGTH = 400
GROUND_LEVEL = 150

import random
import os
import math
from kivy.uix.screenmanager import Screen
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Color, Rectangle, Ellipse, Line, InstructionGroup
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.app import App
from kivy.vector import Vector
from kivy.metrics import dp
from kivy.uix.image import Image
from kivy.core.image import Image as CoreImage
from screens.parallax import ParallaxLayer, GroundLayer

class Cow(Widget):
    def __init__(self, skin_path=None, trail_background=None, **kwargs):
        super().__init__(**kwargs)
        self.velocity_y = 0
        self.gravity = GRAVITY
        self.jump_strength = JUMP_STRENGTH
        self.size_hint = (None, None)
        self.size = (150, 150)
        self.ground_level = GROUND_LEVEL
        self.is_falling = False
        self.fall_reason = None
        self.game_started = False
        
        # Flashing effect properties
        self.is_flashing = False
        self.flash_timer = 0
        self.flash_duration = 1.0
        self.flash_interval = 0.1

        self.pos = (100, self.ground_level)
        self.skin_path = skin_path or "assets/images/characters/bo_0.png"
        self.trail_background = trail_background

        # Display cow image
        self.image = Image(source=self.skin_path, size=self.size, pos=self.pos)
        self.add_widget(self.image)

        self.bind(pos=self.update_graphics, size=self.update_graphics)

    def update_graphics(self, *args):
        self.image.pos = self.pos

    def update(self, dt):
        if not self.game_started:
            return

        # Handle flashing effect
        if self.is_flashing:
            self.flash_timer += dt
            flash_cycle = int(self.flash_timer / self.flash_interval)
            self.image.opacity = 0.3 if flash_cycle % 2 == 0 else 1.0
            
            if self.flash_timer >= self.flash_duration:
                self.is_flashing = False
                self.flash_timer = 0
                self.image.opacity = 1.0

        self.velocity_y -= self.gravity * dt
        self.y += self.velocity_y * dt

        if self.is_falling and self.fall_reason == 'hole' and self.parent.is_cow_in_hole(self):
            if self.top >= 0:
                self.x -= 200 * dt
            if self.top < 0 and self.parent.is_cow_pass_hole(self):
                if self.parent:
                    self.parent.lose_life()
                return
            else:
                return
        else:
            if self.y <= self.ground_level:
                self.y = self.ground_level
                self.velocity_y = 0

    def jump(self):
        if not self.game_started:
            self.game_started = True

        if not self.is_falling:
            self.velocity_y = self.jump_strength

    def start_falling(self, reason='hit'):
        self.is_falling = True
        self.fall_reason = reason
        if reason == 'hole':
            self.velocity_y = -300
        
        if reason != 'hole':
            self.start_flashing()

    def start_flashing(self):
        self.is_flashing = True
        self.flash_timer = 0

    def reset_to_ground(self):
        self.x = 100
        self.y = self.ground_level
        self.velocity_y = 0
        self.is_falling = False
        self.fall_reason = None
        self.is_flashing = False
        self.flash_timer = 0
        self.image.opacity = 1.0

# Keep your existing Obstacle and Collectible classes unchanged
class Obstacle(Widget):
    """Enhanced obstacle class with special behaviors"""

    def __init__(self, obstacle_type, **kwargs):
        super().__init__(**kwargs)
        self.obstacle_type = obstacle_type
        self.speed = 200
        self.size_hint = (None, None)
        
        # Special physics for different obstacles
        self.velocity_y = 0
        self.gravity = 0
        self.rotation_speed = 0

        # Set size and position based on obstacle type
        if self.obstacle_type == 'electric_wire':
            self.size = (Window.width, 20)
            self.pos = (0, Window.height - 20)
        elif self.obstacle_type == 'hole':
            self.size = (80, GROUND_LEVEL)
            self.pos = (Window.width, 0)
        elif self.obstacle_type == 'barrier':
            self.size = (20, random.randint(80, 140))
            self.pos = (Window.width, GROUND_LEVEL)
        elif self.obstacle_type == 'kite':
            self.size = (30, 40)
            start_x = Window.width*random.uniform(0.4, 0.7)
            start_y = Window.height - random.randint(50, 100)
            self.pos = (start_x, start_y)
            if start_x < 0.6:
                self.gravity = 700
            else:
                self.gravity = 200*random.uniform(0.8, 1)
            self.velocity_y = 0
            self.rotation_speed = random.uniform(180, 360)
            self.horizontal_drift = random.uniform(50, 100)
        elif self.obstacle_type == 'bird':
            self.size = (35, 25)
            self.pos = (Window.width, random.randint(GROUND_LEVEL + 40, Window.height - 80))
            self.speed = 2000

        self.initial_y = self.y
        self.rotation_angle = 0
            
        self.setup_obstacle()
        self.bind(pos=self.update_graphics)

    def setup_obstacle(self):
        """Setup obstacle based on type using RELATIVE coordinates."""
        with self.canvas:
            if self.obstacle_type == 'electric_wire':
                Color(1, 1, 0, 1)
                Line(points=[self.x, self.center_y, self.right, self.center_y], width=3)
                Line(points=[self.x, self.y, self.x, self.top], width=2)
                Line(points=[self.right, self.y, self.right, self.top], width=2)

            elif self.obstacle_type == 'hole':
                Color(0, 0, 0, 1)
                Rectangle(pos=self.pos, size=self.size)
                Color(0.3, 0.2, 0.1, 1)
                Line(points=[self.x, self.top, self.right, self.top], width=4)

            elif self.obstacle_type == 'kite':
                Color(1, 0.5, 0, 1)
                points = [
                    self.center_x, self.top,
                    self.right, self.center_y,
                    self.center_x, self.y,
                    self.x, self.center_y
                ]
                Line(points=points + points[:2], width=2)
                Color(1, 0, 0, 1)
                tail_points = []
                for i in range(5):
                    offset_x = random.randint(-8, 8)
                    offset_y = i * 12
                    tail_points.extend([self.center_x + offset_x, self.y - offset_y])
                Line(points=tail_points, width=2)

            elif self.obstacle_type == 'barrier':
                Color(0.5, 0.3, 0.1, 1)
                Rectangle(pos=self.pos, size=self.size)
                Color(0.3, 0.2, 0.05, 1)
                for i in range(0, int(self.height), 15):
                    Line(points=[self.x, self.y + i, self.right, self.y + i], width=1)

            elif self.obstacle_type == 'bird':
                Color(0.4, 0.4, 0.4, 1)
                Ellipse(pos=self.pos, size=self.size)
                Color(0.2, 0.2, 0.2, 1)
                wing_offset = 8 + 4 * abs(self.rotation_angle % 60 - 30) / 30
                Line(points=[self.x + 5, self.center_y, self.x + 15, self.center_y + wing_offset], width=2)
                Line(points=[self.x + 20, self.center_y, self.right - 5, self.center_y + wing_offset], width=2)

    def update_graphics(self, *args):
        self.canvas.clear()
        self.setup_obstacle()

    def update(self, dt, speed_multiplier=1.0):
        if self.obstacle_type == 'electric_wire':
            return False
        
        self.x -= self.speed * speed_multiplier * dt
        
        if self.obstacle_type == 'kite':
            self.velocity_y -= self.gravity * dt
            self.velocity_y = max(self.velocity_y, -100)
            self.y += self.velocity_y * dt
            self.rotation_angle += self.rotation_speed * dt
            self.x -= self.horizontal_drift * dt
        
        elif self.obstacle_type == 'bird':
            bob_amplitude = 20
            bob_frequency = 5
            time_factor = (Window.width - self.x) * 0.01
            self.rotation_angle += 120 * dt
        
        return self.x < -self.width

class Collectible(Widget):
    """Enhanced collectible grass item"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.speed = 200
        self.size = (25, 25)
        self.pos = (Window.width, random.randint(GROUND_LEVEL + 30, Window.height - 80))
        self.size_hint = (None, None)
        self.pulse_timer = 0
        self.bind(pos=self.update_graphics)
        self.update_graphics()

    def update_graphics(self, *args):
        self.canvas.clear()
        with self.canvas:
            pulse_scale = 1.0 + 0.2 * abs(__import__('math').sin(self.pulse_timer * 4))
            scaled_size = (self.size[0] * pulse_scale, self.size[1] * pulse_scale)
            offset = ((self.size[0] - scaled_size[0]) / 2, (self.size[1] - scaled_size[1]) / 2)
            
            Color(0, 0.8, 0, 1)
            Ellipse(pos=(self.pos[0] + offset[0], self.pos[1] + offset[1]), size=scaled_size)
            Color(0, 0.6, 0, 1)
            small_size = (8 * pulse_scale, 8 * pulse_scale)
            Ellipse(pos=(self.x + 4, self.center_y + 4), size=small_size)
            Ellipse(pos=(self.center_x + 4, self.y + 4), size=small_size)
            Ellipse(pos=(self.center_x - 4, self.center_y + 4), size=small_size)
            Ellipse(pos=(self.x + 4, self.center_y - 4), size=small_size)

    def update(self, dt, speed_multiplier=1.0):
        self.pulse_timer += dt
        self.x -= self.speed * speed_multiplier * dt
        self.update_graphics()
        return self.x < -self.width

class GameScreen(Screen):
    """Main game screen with parallax background"""
    
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
        
        # Parallax background properties
        self.scroll = 0
        self.scroll_speed = 2  # Base scroll speed
        self.parallax_layers = []
        self.ground_layer = None
        
        self.build_ui()
    
    def build_ui(self):
        """Build the game UI with parallax background"""
        # Initialize parallax background
        self.setup_parallax_background()
        
        # UI Layout
        ui_layout = BoxLayout(
            orientation='horizontal',
            size_hint=(1, 0.1),
            pos_hint={'top': 1},
            padding=[dp(20), dp(10)],
            spacing=dp(10)
        )
        
        # Lives display
        self.lives_label = Label(
            text='live live live',
            font_size='24sp',
            size_hint=(0.3, 1),
            halign='left'
        )
        
        # Score display
        self.score_label = Label(
            text='Score: 0',
            font_size='20sp',
            size_hint=(0.7, 1),
            halign='right'
        )
        ui_layout.add_widget(self.lives_label)
        ui_layout.add_widget(self.score_label)
        
        self.add_widget(ui_layout)
        
        # Create cow
        self.cow = Cow()
        self.add_widget(self.cow)

    def setup_parallax_background(self):
        """Setup parallax background layers"""
        try:
            # Configure paths
            BASE_PATH = os.path.join("assets", "images", "backgrounds")
            GROUND_PATH = os.path.join("assets", "images", "backgrounds", "ground.png")
            
            # Clear existing layers
            self.parallax_layers = []
            
            # Load background layers
            speed = 0.5  # Start with slower speed for background layers
            for i in range(1, 7):
                layer_path = os.path.join(BASE_PATH, f"layer_{i}.png")
                if os.path.exists(layer_path):
                    layer = ParallaxLayer(layer_path, speed)
                    layer.init_graphics(self.canvas.before)
                    self.parallax_layers.append(layer)
                    speed += 0.3  # Increase speed for each layer
            
            # Load ground layer
            if os.path.exists(GROUND_PATH):
                self.ground_layer = GroundLayer(GROUND_PATH, scroll_speed=1.5)
                self.ground_layer.init_graphics(self.canvas.before, y=0)
            
        except Exception as e:
            print(f"Error setting up parallax background: {e}")
            # Fallback to solid color background
            with self.canvas.before:
                Color(0.5, 0.8, 1, 1)  # Sky blue
                self.bg_rect = Rectangle(size=Window.size, pos=(0, 0))
                Color(0.3, 0.7, 0.2, 1)  # Ground green
                self.ground_rect = Rectangle(
                    size=(Window.width, GROUND_LEVEL),
                    pos=(0, 0)
                )

    def update_parallax(self, dt):
        """Update parallax background"""
        if not self.cow.game_started:
            return
            
        # Update scroll based on game speed
        self.scroll += self.scroll_speed * self.speed_multiplier
        
        # Update all parallax layers
        for layer in self.parallax_layers:
            layer.move(self.scroll)
        
        # Update ground layer
        if self.ground_layer:
            self.ground_layer.move(self.scroll)
    
    def on_enter(self):
        """Called when entering the game screen"""
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
        self.scroll = 0  # Reset scroll

        # Get skin
        app = App.get_running_app()
        skin_id = app.data_manager.get_equipped_skin()
        background_id = app.data_manager.get_equipped_background()
        
        skin_path = f"assets/images/characters/{skin_id}.png" if skin_id else "assets/images/characters/bo_0.png"

        # Create new Cow with skin
        if hasattr(self, 'cow'):
            self.remove_widget(self.cow)

        self.cow = Cow(skin_path=skin_path, trail_background=background_id)
        self.cow.pos = (100, GROUND_LEVEL)
        self.cow.game_started = False
        self.add_widget(self.cow)

        # Clear old obstacles and collectibles
        for obstacle in self.obstacles:
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
    
    def update_game(self, dt):
        """Main game update loop"""
        if not self.game_running:
            return
        
        # Update parallax background
        self.update_parallax(dt)
        
        # Update cow
        self.cow.update(dt)
        
        # Only spawn obstacles and update game elements after cow starts moving
        if not self.cow.game_started:
            return
        
        # Update speed based on score
        self.speed_multiplier = 1.0 + (self.score // 30) * 0.3
        
        # Spawn obstacles
        self.spawn_timer += dt
        spawn_interval = 3.5 / self.speed_multiplier
        if self.spawn_timer >= spawn_interval:
            self.spawn_obstacle()
            self.spawn_timer = 0
        
        # Spawn collectibles
        self.collectible_spawn_timer += dt
        collectible_interval = 2.0
        if self.collectible_spawn_timer >= collectible_interval:
            num_collectibles = random.choices([1, 2, 3], weights=[60, 30, 10])[0]
            for _ in range(num_collectibles):
                self.spawn_collectible()
            self.collectible_spawn_timer = 0
        
        # Update obstacles
        for obstacle in self.obstacles[:]:
            if obstacle.update(dt, self.speed_multiplier):
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
            obstacle_types = ['hole', 'kite', 'kite', 'kite', 'barrier', 'bird', 'electric_wire']
            obstacle_type = random.choice(obstacle_types)
        
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
    
    def check_collision(self, obstacle):
        """Check collision between cow and obstacle"""
        if self.cow.collide_widget(obstacle):
            print('o no, cow hit an obstacle!')
            self.cow.start_falling(obstacle.obstacle_type)
            app = App.get_running_app()
            
            if obstacle.obstacle_type == 'electric_wire':
                if app and hasattr(app, 'sound_manager'):
                    app.sound_manager.play_sound('game_over')
                self.game_over()
                return
            
            elif obstacle.obstacle_type == 'hole':
                pass
            
            else:
                if app and hasattr(app, 'sound_manager'):
                    app.sound_manager.play_sound('hit')
                
                self.cow.start_falling('hit')
                
                self.remove_widget(obstacle)
                self.obstacles.remove(obstacle)
                
                Clock.schedule_once(lambda dt: self.lose_life(), 0.5)
    
    def lose_life(self):
        """Lose a life"""
        self.lives -= 1
        self.update_ui()
        
        self.cow.reset_to_ground()
        self.cow.pos = (100, self.cow.ground_level)
        
        if self.lives <= 0:
            self.game_over()
    
    def is_cow_in_hole(self, cow):
        """Check if cow is positioned over a hole"""
        for obstacle in self.obstacles:
            if obstacle.obstacle_type == 'hole':
                hole_left = obstacle.x
                hole_right = obstacle.right
                cow_center = cow.center_x
                
                if cow_center >= (hole_left + hole_right) / 2:
                    return True
        return False
    
    def is_cow_pass_hole(self, cow):
        """Check if cow is positioned over a hole"""
        for obstacle in self.obstacles:
            if obstacle.obstacle_type == 'hole':
                hole_left = obstacle.x
                hole_right = obstacle.right
                
                if hole_right <= 100 * 0.8:
                    return True
        return False

    def check_collectible_collision(self, collectible):
        """Check collision between cow and collectible"""
        if self.cow.collide_widget(collectible):
            app = App.get_running_app()
            if app and hasattr(app, 'sound_manager'):
                app.sound_manager.play_sound('collect')
            
            self.score += 1
            self.update_ui()
            self.remove_widget(collectible)
            self.collectibles.remove(collectible)
    
    def game_over(self):
        """Handle game over"""
        self.stop_game()
        
        app = App.get_running_app()
        if app and hasattr(app, 'data_manager'):
            app.data_manager.add_points(self.score)
            is_new_high_score = self.score > app.data_manager.get_best_score()
            app.data_manager.set_best_score(self.score)
            
            game_over_screen = self.manager.get_screen('game_over')
            game_over_screen.set_score_data(self.score, is_new_high_score)
        
        self.manager.current = 'game_over'
    
    def update_ui(self):
        """Update UI elements"""
        heart_text = 'L ' * self.lives + 'D ' * (3 - self.lives)
        self.lives_label.text = heart_text.strip()
        self.score_label.text = f'Score: {self.score}'
    
    def on_touch_down(self, touch):
        """Handle touch input"""
        if self.game_running:
            self.cow.jump()
            app = App.get_running_app()
            if app and hasattr(app, 'sound_manager'):
                app.sound_manager.play_sound('fly')
        return True
    
    def on_space_press(self):
        """Handle space bar press"""
        if self.game_running:
            self.cow.jump()
            app = App.get_running_app()
            if app and hasattr(app, 'sound_manager'):
                app.sound_manager.play_sound('fly')