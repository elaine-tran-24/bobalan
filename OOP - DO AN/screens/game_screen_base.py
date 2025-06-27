"""
Game Screen for When Cows Fly
Main gameplay screen with cow, obstacles, and game logic
Fixed hole physics and obstacle behavior
"""
GRAVITY = 2.5
JUMP_STRENGTH = 20
GROUND_LEVEL = 60

import random
from kivy.uix.screenmanager import Screen
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Color, Rectangle, Ellipse, Line
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.app import App
from kivy.vector import Vector

class Cow(Widget):
    """Cow player character"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.velocity_y = 0
        self.gravity = GRAVITY
        self.jump_strength = JUMP_STRENGTH
        self.size_hint = (None, None)
        self.size = (40, 40)
        self.ground_level = GROUND_LEVEL
        self.is_falling = False
        self.fall_reason = None
        self.game_started = False
        
        # Set initial position on ground
        self.pos = (100, self.ground_level)
        
        # Draw the cow (simple representation)
        with self.canvas:
            Color(1, 1, 1, 1)  # White cow
            self.cow_shape = Ellipse(pos=self.pos, size=self.size)
        
        self.bind(pos=self.update_graphics)
    
    def update_graphics(self, *args):
        """Update cow graphics position"""
        self.cow_shape.pos = self.pos
            # Vẽ bounding box
        self.canvas.after.clear()
        with self.canvas.after:
            Color(1, 0, 0, 1)  # Viền đỏ
            Line(rectangle=(*self.pos, *self.size), width=1)
    
    def update(self, dt):
        """Update cow physics - Flappy Bird style with ground landing"""
        if not self.game_started:
            return

        # Apply gravity
        self.velocity_y -= self.gravity * dt
        self.y += self.velocity_y * dt

        # Gán lại self.pos để trigger update vẽ + bounding box
        self.pos = (self.x, self.y)

        # Nếu chạm đất
        if self.y <= self.ground_level:
            self.y = self.ground_level
            self.velocity_y = 0
            self.pos = (self.x, self.y)  # Cập nhật lại vì self.y vừa bị chỉnh

        # Cập nhật bounding box sau cùng
        self.update_graphics()

    
    def jump(self):
        """Make the cow jump (like Flappy Bird)"""
        # Start the game physics on first jump
        if not self.game_started:
            self.game_started = True
            
        # Jump regardless of current state (like Flappy Bird)
        self.velocity_y = self.jump_strength
        self.is_falling = False  # Reset falling state when jumping
    
    def start_falling(self, reason='hit'):
        """Start falling due to obstacle hit"""
        self.is_falling = True
        self.fall_reason = reason
        if reason == 'hit':
            # Add downward velocity when hit by obstacle
            self.velocity_y = -300
    
    def reset_to_ground(self):
        """Reset cow to ground position"""
        self.y = self.ground_level
        self.velocity_y = 0
        self.is_falling = False
        self.fall_reason = None


class Obstacle(Widget):
    """Base obstacle class"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.pos = (Window.width,GROUND_LEVEL)
        self.size = (100, 100)
        self.speed = 200
        self.size_hint = (None, None)
        self.bind(pos=self.update_graphics)
        self.update_graphics()    
        Clock.schedule_once(lambda dt: self.update_graphics(), 0)

    def update_graphics(self, *args):
        self.canvas.clear()
        with self.canvas:
            Color(0.8, 0.2, 0.2, 1)  # Red obstacle
            self.shape = Rectangle(pos=self.pos, size=self.size)
                # Vẽ bounding box
        self.canvas.after.clear()
        with self.canvas.after:
            Color(0, 1, 0, 1)  # Green bounding box for debugging
            Line(rectangle=(*self.pos, *self.size), width=1)
    def update(self, dt, speed_multiplier=1.0):
        # Di chuyển sang trái
        self.x -= self.speed * speed_multiplier * dt

        # Cập nhật lại pos để đồng bộ logic + canvas
        self.pos = (self.x, self.y)

        # Vẽ lại đồ họa + bounding box
        self.update_graphics()

        # Debug
        print(f"Obstacle x: {self.x} | pos: {self.pos}")

        # Trả về True nếu ra khỏi màn hình bên trái (để xóa)
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
        ob = Obstacle()
        self.add_widget(ob)
        self.obstacles.append(ob)

        """Build the game UI"""
        # Background
        with self.canvas.before:
            Color(0.5, 0.8, 1.0, 1)  # Light blue sky
            self.bg_rect = Rectangle(size=Window.size, pos=(0, 0))

            # Ground
            Color(0.2, 0.8, 0.2, 1)  # Green ground
            self.ground_rect = Rectangle(size=(Window.width, 60), pos=(0, 0))
            
            # Add some ground details
            Color(0.15, 0.6, 0.15, 1)  # Darker green for grass lines
            for i in range(0, Window.width, 20):
                Line(points=[i, 50, i+10, 60], width=1)
        
        # Bind to update background
        self.bind(size=self.update_bg)
        Window.bind(size=self.update_bg)
        
        # UI Layout
        ui_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.1), pos_hint={'top': 1})
        
        # Lives display
        self.lives_label = Label(
            text='live live live',
            font_size='24sp',
            size_hint=(0.3, 1),
            halign='left'
        )
        ui_layout.add_widget(self.lives_label)
        
        # Score display
        self.score_label = Label(
            text='Score: 0',
            font_size='20sp',
            size_hint=(0.7, 1),
            halign='right'
        )
        ui_layout.add_widget(self.score_label)
        
        self.add_widget(ui_layout)
        
        # Create cow
        self.cow = Cow()
        self.add_widget(self.cow)
        
        # Bind touch events
        self.bind(on_touch_down=self.on_touch_down)
    
    def update_bg(self, *args):
        """Update background size"""
        self.bg_rect.size = Window.size
        self.ground_rect.size = (Window.width, 60)
    
    def on_enter(self):
        """Called when entering the game screen"""
        self.start_game()
    
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
        # self.collectible_spawn_timer = 0
        
        # Reset cow to ground and disable physics until first jump
        self.cow.reset_to_ground()
        self.cow.pos = (100, self.cow.ground_level)
        self.cow.game_started = False  # Reset game started state

        for obstacle in self.obstacles:
            self.remove_widget(obstacle)
        self.obstacles.clear()
       # Update UI
        self.update_ui()
        
        # Start game loop
        Clock.schedule_interval(self.update_game, 1.0/60.0)
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
        # if self.spawn_timer >= 5.0 / self.speed_multiplier:
        if self.spawn_timer >= 5.0:
            self.spawn_obstacle()
            self.spawn_timer = 0
        for obstacle in self.obstacles[:]:
            if obstacle.update(dt, self.speed_multiplier):
                self.remove_widget(obstacle)
                self.obstacles.remove(obstacle)
            else:
                self.check_collision(obstacle)
        
    def spawn_obstacle(self):
        obstacle = Obstacle()
        print(f"Spawning obstacle at x: {obstacle.x}, y: {obstacle.y}")  # Debug
        self.obstacles.append(obstacle)
        self.add_widget(obstacle)

    def check_collision(self, obstacle):
        print(f"[DEBUG COLLISION] Cow: {self.cow.pos}, {self.cow.size}")
        print(f"[DEBUG COLLISION] Obs: {obstacle.pos}, {obstacle.size}")
        if self.cow.collide_widget(obstacle):
            print('o no, cow hit an obstacle!')
            self.cow.start_falling('hit')
            app = App.get_running_app()
            app.sound_manager.play_sound('hit')
            # Remove obstacle
            self.remove_widget(obstacle)
            self.obstacles.remove(obstacle)
            Clock.schedule_once(lambda dt: self.lose_life(), 0.2)

    def lose_life(self):
        """Lose a life"""
        self.lives -= 1
        self.update_ui()
        # Reset cow to ground
        self.cow.reset_to_ground()
        self.cow.pos = (100, self.cow.ground_level)
        
        if self.lives <= 0:
            self.game_over()
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
        heart_text = 'red ' * self.lives + 'blvck ' * (3 - self.lives)
        self.lives_label.text = heart_text.strip()
        # Update score
        self.score_label.text = f'Score: {self.score}'

    def on_space_press(self):
        """Handle space bar press"""
        if self.game_running:
            self.cow.jump()
            app = App.get_running_app()
            app.sound_manager.play_sound('fly')