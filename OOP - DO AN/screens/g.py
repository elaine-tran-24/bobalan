"""
Game Screen for When Cows Fly - FIXED VERSION
Main gameplay screen with cow, obstacles, and game logic
"""
GRAVITY = 600
JUMP_STRENGTH = 400
GROUND_LEVEL = 100
OBSTACLE_SPEED = 300
import math
import random
import os
from kivy.uix.screenmanager import Screen
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Color, Rectangle, Ellipse, Line
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.app import App
from kivy.vector import Vector
from kivy.metrics import dp

from kivy.uix.image import Image
from kivy.graphics import InstructionGroup, Color, Ellipse
from kivy.uix.widget import Widget
from screens.background import ParallaxWidget
from kivy.uix.behaviors import ButtonBehavior

class ImageButton(ButtonBehavior, Image):
    pass

class Cow(Widget):
    def __init__(self, skin_path=None, trail_background=None, **kwargs):
        super().__init__(**kwargs)
        self.velocity_y = 0
        self.gravity = GRAVITY
        self.jump_strength = JUMP_STRENGTH
        self.size_hint = (None, None)
        self.size = (250, 171)
        self.ground_level = GROUND_LEVEL
        self.is_falling = False
        self.fall_reason = None
        self.game_started = False
        
        # Store original spawn position for proper reset
        self.original_x = Window.width * 0.5 - self.size[0] * 0.5
        self.original_y = self.ground_level
        
        # Hole-specific tracking
        self.hole_fall_start_x = None  # Track where hole fall started
        self.in_hole_phase = False     # Track if we're in hole falling phase
        
        # Flashing effect properties
        self.is_flashing = False
        self.flash_timer = 0
        self.flash_duration = 1.0
        self.flash_interval = 0.1
        
        self.pos = (self.original_x, self.original_y)
        self.skin_path = skin_path or "assets/images/characters/bo.gif"

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

        # Apply gravity
        self.velocity_y -= self.gravity * dt
        self.y += self.velocity_y * dt

        # FIXED: Improved hole falling logic
        if self.is_falling and self.fall_reason == 'hole':
            # If we just started falling into hole, record the start position
            if self.hole_fall_start_x is None:
                
                self.hole_fall_start_x = self.x
                self.in_hole_phase = True
            
            # Only move horizontally if still visible and in hole phase
            if self.in_hole_phase and self.top >= 0:
                self.x -= 200 * dt
            
            # Check if cow has fallen completely off screen
            if self.top < 0:
                self.in_hole_phase = False
                # Check if cow has moved past the hole
                if self.parent and self.parent.is_cow_past_all_holes():
                    if self.parent:
                        self.parent.lose_life()
                    return
        else:
            # Normal ground collision
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
            # Reset hole tracking variables
            self.hole_fall_start_x = None
            self.in_hole_phase = False
        
        if reason != 'hole':
            self.start_flashing()

    def start_flashing(self):
        self.is_flashing = True
        self.flash_timer = 0

    def reset_to_ground(self):
        # FIXED: Always reset to original spawn position
        self.pos = (self.original_x, self.original_y)
        self.velocity_y = 0
        self.is_falling = False
        self.fall_reason = None
        self.is_flashing = False
        self.flash_timer = 0
        self.image.opacity = 1.0
        
        # Reset hole-specific tracking
        self.hole_fall_start_x = None
        self.in_hole_phase = False
        
        self.update_graphics()

     
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
            self.size = (275, GROUND_LEVEL+50)
            self.path = "assets/images/obstacles/hole.png"
            self.pos = (Window.width, 0)
        elif self.obstacle_type == 'barrier':
            self.size = (200, 230)
            self.pos = (Window.width, GROUND_LEVEL)
            self.path = "assets/images/obstacles/barrier.png"
        elif self.obstacle_type == 'kite':
            self.size = (120,150)
            start_x = Window.width*random.uniform(0.4, 0.7)
            start_y = Window.height - random.randint(50, 100)
            self.path = "assets/images/obstacles/kite.gif"
            self.pos = (start_x, start_y)
            if start_x < 0.6:
                self.gravity = 1000*random.uniform(0.8, 1)
            else:
                self.gravity = 400*random.uniform(0.8, 1)
            self.velocity_y = 0
            self.rotation_speed = random.uniform(180, 360)
            self.horizontal_drift = random.uniform(50, 100)

        elif self.obstacle_type == 'bird':
            self.size = (70, 93)
            self.pos = (Window.width, random.randint(GROUND_LEVEL + 40, Window.height - 80))
            self.speed = 1200
            self.path = "assets/images/obstacles/bird.png"

        self.initial_y = self.y
        self.rotation_angle = 0
            
        self.add_widget(Image(source=self.path, size=self.size, pos=self.pos))
        self.bind(pos=self.update_graphics)
        
    def update_graphics(self, *args):
        self.canvas.clear()
        self.add_widget(Image(source=self.path, size=self.size, pos=self.pos))

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
            # bob_amplitude = 20
            # bob_frequency = 5
            # time_factor = (Window.width - self.x) * 0.01
            self.rotation_angle += 120 * dt
        elif self.obstacle_type == 'bird2':             
            bob_amplitude = 30           # Độ cao dao động (pixels)
            bob_frequency = 2            # Số lần dao động mỗi giây
            self.x -= self.speed * dt    # Di chuyển ngang (từ phải sang trái)

            self.y = self.start_y + bob_amplitude * math.sin(2 * math.pi * bob_frequency * self.total_time)
            self.rotation_angle = math.sin(2 * math.pi * bob_frequency * self.total_time) * 10

        
        return self.x < -self.width

class Collectible(Widget):
    """Collectible grass item"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.speed = 200
        self.size = (40, 40)
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
    """Main game screen"""
    
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

        self.cow = Cow()
        self.parallax = ParallaxWidget(cow=self.cow)
        self.add_widget(self.parallax)

        self.build_ui()
        self.is_paused = False

    def build_ui(self):
        """Build the game UI"""

        self.cow = Cow()
        self.parallax = ParallaxWidget(cow=self.cow)
        
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
            font_size='20sp',
            size_hint=(0.7, 1),
            halign='left',
            valign='middle',
            color=(1, 1, 1, 1)
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
            heart = Image(source='assets/images/icons/live.png', size_hint=(None, None), size=(40, 40))
            self.hearts.append(heart)
            self.hearts_layout.add_widget(heart)

        ui_layout.add_widget(self.score_label)
        ui_layout.add_widget(self.hearts_layout)
        self.add_widget(ui_layout)
        
        # Settings icon
        self.game_settings_btn = ImageButton(
            source='assets/images/buttons/setting.png',
            size_hint=(None, None),
            size=(80, 80),
            pos_hint={'right': 0.98, 'y': 0.02}
        )
        self.game_settings_btn.bind(on_press=self.show_settings)
        self.add_widget(self.game_settings_btn, index=0) 

        # Create cow
        self.cow = Cow()
        self.parallax = ParallaxWidget(cow=self.cow)

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

        skin_path = f"assets/images/characters/{skin_id}.gif" if skin_id else "assets/images/characters/bo.gif"
        print("Skin path:", skin_path, "| Exists:", os.path.exists(skin_path))
        
        # Create new Cow with skin
        if hasattr(self, 'cow'):
            self.remove_widget(self.cow)

        self.cow = Cow(skin_path=skin_path)
        self.cow.pos = (100, GROUND_LEVEL)
        self.cow.game_started = False
        self.add_widget(self.cow)
        print("Added cow with skin:", self.cow.skin_path)

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
    
    def pause_game(self):
        if self.game_running and not self.is_paused:  
            Clock.unschedule(self.update_game)
            self.game_running = False
            self.is_paused = True
            
    def resume_game(self):
        if not self.game_running and self.is_paused:
            Clock.schedule_interval(self.update_game, 1.0 / 60.0)
            self.game_running = True
            self.is_paused = False

    def update_game(self, dt):
        """Main game update loop"""
        if not self.game_running:
            return
        
        # Update cow
        self.cow.update(dt)
        
        # Only spawn obstacles and update game elements after cow starts moving
        if not self.cow.game_started:
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
            obstacle_types = ['hole','hole','hole','hole','hole']
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
        
        # Special handling for holes - check if cow center is over hole center
        if obstacle.obstacle_type == 'hole':
            cow_center_x = self.cow.center_x
            hole_center_x = obstacle.center_x
            
            # Only trigger hole fall when cow's center reaches hole's center
            # Add small tolerance to make it feel natural
            tolerance = 20  # pixels
            
            if abs(cow_center_x - hole_center_x) <= tolerance and self.cow.y <= self.cow.ground_level:
                print('Cow fell into hole center!')
                self.cow.start_falling('hole')
                return
        
        # Normal collision detection for other obstacles
        elif self.cow.collide_widget(obstacle):
            print('Oh no, cow hit an obstacle!')
            self.cow.start_falling(obstacle.obstacle_type)
            app = App.get_running_app()
            
            if obstacle.obstacle_type == 'electric_wire':
                # FIXED: Use non-blocking sound call
                self.play_sound_async('game_over')
                self.game_over()
                return
            
            else:
                # FIXED: Use non-blocking sound call
                self.play_sound_async('hit')
                
                # Make cow fall
                self.cow.start_falling('hit')
                
                # Remove obstacle
                self.remove_widget(obstacle)
                self.obstacles.remove(obstacle)
                
                # Lose life after a short delay
                Clock.schedule_once(lambda dt: self.lose_life(), 0.5)
    
    def lose_life(self):
        """Lose a life"""
        self.lives -= 1
        self.update_ui()
        
        # Reset cow to ground
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
    
    # FIXED: New method to check if cow has passed all holes
    def is_cow_past_all_holes(self):
        """Check if cow has moved past all holes completely"""
        for obstacle in self.obstacles:
            if obstacle.obstacle_type == 'hole':
                # If any hole is still to the right of cow's original position, cow hasn't passed it
                if obstacle.right > self.cow.original_x:
                    return False
        return True

    def check_collectible_collision(self, collectible):
        """Check collision between cow and collectible"""
        if self.cow.collide_widget(collectible):
            # FIXED: Use non-blocking sound call
            self.play_sound_async('collect')
            
            self.score += 1
            self.update_ui()
            self.remove_widget(collectible)
            self.collectibles.remove(collectible)
    
    # FIXED: Non-blocking sound playing method
    def play_sound_async(self, sound_name):
        """Play sound without blocking the game"""
        def _play_sound(dt):
            app = App.get_running_app()
            if app and hasattr(app, 'sound_manager'):
                app.sound_manager.play_sound(sound_name)
        
        # Schedule sound to play on next frame to avoid blocking
        Clock.schedule_once(_play_sound, 0)
    
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

        if self.game_running:
            self.cow.jump()
            # FIXED: Use non-blocking sound call
            self.play_sound_async('fly')
            return True  

        return False
    
    def on_space_press(self):
        """Handle space bar press"""
        if self.game_running:
            self.cow.jump()
            # FIXED: Use non-blocking sound call
            self.play_sound_async('fly')

    def show_settings(self, *args):
        self.pause_game()
        self.manager.current = 'game_settings'