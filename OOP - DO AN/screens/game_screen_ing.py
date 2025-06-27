"""
Game Screen for When Cows Fly
Main gameplay screen with cow, obstacles, and game logic
"""
GRAVITY = 600
JUMP_STRENGTH = 400
GROUND_LEVEL = 100

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

class Cow(Widget):
    def __init__(self, skin_path=None,trail_background=None, **kwargs):
        super().__init__(**kwargs)
        self.velocity_y = 0
        self.gravity = GRAVITY
        self.jump_strength = JUMP_STRENGTH
        self.size_hint = (None, None)
        self.size = (150,150)
        self.ground_level = GROUND_LEVEL
        self.is_falling = False
        self.fall_reason = None
        self.game_started = False

        self.pos = (100, self.ground_level)
        self.skin_path = skin_path or "assets/images/characters/bo_0.png"
        self.trail_background = trail_background

        # Hiển thị ảnh bò
        self.image = Image(source=self.skin_path, size=self.size, pos=self.pos)
        self.add_widget(self.image)

        self.bind(pos=self.update_graphics, size=self.update_graphics)

    def update_graphics(self, *args):
        self.image.pos = self.pos

    def update(self, dt):
        if not self.game_started:
            return

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

    def reset_to_ground(self):
        self.x = 100
        self.y = self.ground_level
        self.velocity_y = 0
        self.is_falling = False
        self.fall_reason = None

class Obstacle(Widget):
    """Base aclesacle class"""

    def __init__(self, obstacle_type, **kwargs):
        super().__init__(**kwargs)
        self.obstacle_type = obstacle_type
        self.speed = 200
        self.size_hint = (None, None)

        # Set size and position FIRST
        if self.obstacle_type == 'electric_wire':
            self.size = (Window.width, 20) # A small, dangerous segment
            self.pos = (0, Window.height -20)
        elif self.obstacle_type == 'hole':
            self.size = (80, GROUND_LEVEL) # Hole should cover the ground height
            self.pos = (Window.width, 0)
        elif self.obstacle_type == 'barrier':
            self.size = (20, random.randint(80, 140))
            self.pos = (Window.width, GROUND_LEVEL)
        else: # Kite, Bird
            self.size = (35, 30) # Standardized size for simplicity
            self.pos = (Window.width, random.randint(GROUND_LEVEL + 40, Window.height - 80))
            if obstacle_type == 'kite':
                self.size = (30, 40)
            elif obstacle_type == 'bird':
                self.size = (35, 25)

        # THEN call setup_obstacle() to draw the graphics at the correct initial position
        self.setup_obstacle()
        self.bind(pos=self.update_graphics)

    def setup_obstacle(self):
        """Setup obstacle based on type using RELATIVE coordinates."""
        with self.canvas:
            if self.obstacle_type == 'electric_wire':
                Color(1, 1, 0, 1)  # Yellow
                # Draw lines relative to the widget's bounding box
                Line(points=[self.x, self.center_y, self.right, self.center_y], width=3)
                # Draw "sparks" or posts
                Line(points=[self.x, self.y, self.x, self.top], width=2)
                Line(points=[self.right, self.y, self.right, self.top], width=2)

            elif self.obstacle_type == 'hole':
                Color(0, 0, 0, 1)  # Black hole
                # Use self.pos and self.size which are now correctly set
                Rectangle(pos=self.pos, size=self.size)
                # Add a brown border to make it look like a hole in the ground
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
                    tail_points.extend([self.center_x + random.randint(-5, 5), self.y - (i * 10)])
                Line(points=tail_points, width=1)

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
                Line(points=[self.x + 5, self.center_y, self.x + 15, self.center_y + 8], width=2)
                Line(points=[self.x + 20, self.center_y, self.right - 5, self.center_y + 8], width=2)

    def update_graphics(self, *args):
        self.canvas.clear()
        self.setup_obstacle()

    def update(self, dt, speed_multiplier=1.0):
        if self.obstacle_type == 'electric_wire':
            return False
        self.x -= self.speed * speed_multiplier * dt
        return self.x < -self.width
     
class Collectible(Widget):
    """Collectible grass item"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.speed = 200
        self.size = (25, 25)
        self.pos = (Window.width, random.randint(80, Window.height - 80))
        self.size_hint = (None, None)
        self.bind(pos=self.update_graphics)
        self.update_graphics()

    def update_graphics(self, *args):
        self.canvas.clear()
        with self.canvas:
            Color(0, 0.8, 0, 1)
            Ellipse(pos=self.pos, size=self.size)
            Color(0, 0.6, 0, 1)
            small_size = (8, 8)
            Ellipse(pos=(self.x + 4, self.center_y + 4), size=small_size)
            Ellipse(pos=(self.center_x + 4, self.y + 4), size=small_size)
            Ellipse(pos=(self.center_x - 4, self.center_y + 4), size=small_size)
            Ellipse(pos=(self.x + 4, self.center_y - 4), size=small_size)

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
        self.build_ui()
    
    def build_ui(self):
        """Build the game UI"""
        # Background
        with self.canvas.before:
            #nền trời
            self.bg_rect = Rectangle(size=self.size, pos=self.pos)
            # nền đất
            ground_height = Window.height * 4 / 7
            self.ground_rect = Rectangle(
                source="assets/images/ground/ground_1.png",
                size=(Window.width, ground_height),
                pos=(0, 0)
            )


        # Bind to update background
        self.bind(size=self.update_bg)
        Window.bind(size=self.update_bg)
        
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
            halign='right'
        )
        ui_layout.add_widget(self.lives_label)
        ui_layout.add_widget(self.score_label)
        
        self.add_widget(ui_layout)
        
        # Create cow
        self.cow = Cow()
        self.add_widget(self.cow)
        
        # # Bind touch events
        # self.bind(on_touch_down=self.on_touch_down)


    def update_bg(self, *args):
        self.bg_rect.size = Window.size
        self.bg_rect.pos = (0, 0)

            # Cập nhật nền đất
        ground_height = Window.height * 4 / 7
        self.ground_rect.size = (Window.width, ground_height)
        self.ground_rect.pos = (0, 0)
    
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

        # Lấy skin và background
        app = App.get_running_app()
        skin_id = app.data_manager.get_equipped_skin()   # <-- đổi tên đúng
        print("Equipped skin_id:", skin_id)

        background_id = app.data_manager.get_equipped_background()  # <-- đổi tên đúng

        skin_path = f"assets/images/characters/{skin_id}.png" if skin_id else "assets/images/characters/bo_0.png"
        print("Skin path:", skin_path, "| Exists:", os.path.exists(skin_path))
        
        bg_path = f"assets/images/backgrounds/{background_id}.png" if background_id else "assets/images/backgrounds/background_menu.png"

        # Tạo mới Cow với skin/background
        if hasattr(self, 'cow'):
            self.remove_widget(self.cow)

        self.cow = Cow(skin_path=skin_path, trail_background=background_id)
        self.cow.pos = (100, GROUND_LEVEL)
        self.cow.game_started = False
        self.add_widget(self.cow)
        print("Added cow with skin:", self.cow.skin_path)


        if bg_path and os.path.exists(bg_path):
            self.bg_rect.source = bg_path


        # Xoá vật cản và cỏ cũ
        for obstacle in self.obstacles:
            self.remove_widget(obstacle)
        for collectible in self.collectibles:
            self.remove_widget(collectible)
        self.obstacles.clear()
        self.collectibles.clear()

        self.spawn_obstacle('electric_wire')  # Khởi đầu với một vật cản

        # UI
        self.update_ui()

        # Game loop
        Clock.schedule_interval(self.update_game, 1.0 / 60.0)


    def stop_game(self):
        """Stop the game"""
        self.game_running = False
        Clock.unschedule(self.update_game)
    
    def pause_game(self):
        """Pause the game"""
        if self.game_running:
            Clock.unschedule(self.update_game)
            self.game_running = False
    
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
        # CHANGED: Added 'electric_wire' to the main list
        if obstacle_type is None:
            obstacle_types = ['hole', 'kite', 'barrier', 'bird', 'electric_wire']
            obstacle_type = random.choice(obstacle_types)
        
        obstacle = Obstacle(obstacle_type=obstacle_type) # Pass type as keyword arg
        
        self.obstacles.append(obstacle)
        # FIXED: Removed the extra spawn and now add the single created obstacle
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
                # Instant game over for electric wire
                if app and hasattr(app, 'sound_manager'):
                    app.sound_manager.play_sound('game_over')
                self.game_over()
                return
            
            elif obstacle.obstacle_type == 'hole':
                # Don't handle hole collision here - handled in cow physics
                pass
            
            else:
                # Other obstacles cause cow to fall and lose life
                if app and hasattr(app, 'sound_manager'):
                    app.sound_manager.play_sound('hit')
                
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
                
                # Check if cow is over the hole
                # if hole_left <= cow_center <= hole_right:
                if cow_center >= (hole_left + hole_right) / 2:
                    return True
        return False
    
    def is_cow_pass_hole(self, cow):
        """Check if cow is positioned over a hole"""
        for obstacle in self.obstacles:
            if obstacle.obstacle_type == 'hole':
                hole_left = obstacle.x
                hole_right = obstacle.right
                
                # Check if cow is over the hole
                # if hole_left <= cow_center <= hole_right:
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
        """Update UI elements"""
        # Update lives display
        heart_text = 'L ' * self.lives + 'D ' * (3 - self.lives)
        self.lives_label.text = heart_text.strip()
        
        # Update score
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
    
import os
print("Files in characters folder:", os.listdir("assets/images/characters"))

