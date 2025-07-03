"""
Animated Sprite System for When Cows Fly
Handles frame-based animation for characters and obstacles
"""

import os
from kivy.clock import Clock
from kivy.uix.image import Image
from kivy.resources import resource_find
from kivy.uix.widget import Widget


FRAME_DURATION = 0.2
class AnimatedSprite(Widget):
    """Base class for animated sprites using PNG frames"""
    
    def __init__(self, base_path, frame_count=4, frame_duration= FRAME_DURATION, **kwargs):
        super().__init__(**kwargs)
        
        self.base_path = base_path
        self.frame_count = frame_count
        self.frame_duration = frame_duration  # 20ms = 0.02 seconds
        self.current_frame = 0
        self.animation_time = 0
        
        # Load all frame paths
        self.frame_paths = []
        for i in range(frame_count):
            frame_path = f"{base_path}/{i}.png"
            if resource_find(frame_path):
                self.frame_paths.append(frame_path)
            else:
                print(f"Warning: Frame not found: {frame_path}")
                # Use first frame as fallback
                if i == 0:
                    self.frame_paths.append(f"{base_path}/0.png")
                else:
                    self.frame_paths.append(self.frame_paths[0])
        
        # Create the image widget
        self.image = Image(
            source=resource_find(self.frame_paths[0]) if self.frame_paths else "",
            size=self.size,
            pos=self.pos
        )
        self.add_widget(self.image)
        
        # Start animation
        self.animation_event = Clock.schedule_interval(self.update_animation, 1.0/60.0)
        
        # Bind position and size changes
        self.bind(pos=self.update_graphics, size=self.update_graphics)
    
    def update_graphics(self, *args):
        """Update image position and size"""
        if hasattr(self, 'image'):
            self.image.pos = self.pos
            self.image.size = self.size
    
    def update_animation(self, dt):
        """Update animation frame"""
        if not self.frame_paths:
            return
            
        self.animation_time += dt
        
        if self.animation_time >= self.frame_duration:
            self.animation_time = 0
            self.current_frame = (self.current_frame + 1) % len(self.frame_paths)
            
            # Update image source
            new_source = resource_find(self.frame_paths[self.current_frame])
            if new_source != self.image.source:
                self.image.source = new_source
    
    def stop_animation(self):
        """Stop the animation"""
        if hasattr(self, 'animation_event'):
            Clock.unschedule(self.animation_event)
    
    def start_animation(self):
        """Start the animation"""
        self.stop_animation()
        self.animation_event = Clock.schedule_interval(self.update_animation, 1.0/60.0)
    
    def set_frame(self, frame_index):
        """Set specific frame"""
        if 0 <= frame_index < len(self.frame_paths):
            self.current_frame = frame_index
            self.image.source = resource_find(self.frame_paths[frame_index])


class AnimatedCow(AnimatedSprite):
    """Animated cow sprite"""
    
    def __init__(self, skin_id="bo", **kwargs):
        # Determine base path based on skin_id
        base_path = f"assets/images/characters/{skin_id}"
        
        super().__init__(
            base_path=base_path,
            frame_count=4,
            frame_duration=FRAME_DURATION,  # 20ms per frame
            **kwargs
        )
        
        self.skin_id = skin_id
        
        # Cow-specific properties
        self.velocity_y = 0
        self.gravity = 600
        self.jump_strength = 400
        self.ground_level = 100
        self.is_falling = False
        self.fall_reason = None
        self.game_started = False
        
        # Store original spawn position for proper reset
        from kivy.core.window import Window
        from kivy.metrics import dp
        self.original_x = Window.width * 0.5 - self.size[0] * 0.5
        self.original_y = self.ground_level
        
        # Hole-specific tracking
        self.hole_fall_start_x = None
        self.in_hole_phase = False
        self.fell_in_hole = False
        self.hole_respawn_delay = 0
        
        # Flashing effect properties
        self.is_flashing = False
        self.flash_timer = 0
        self.flash_duration = 1.0
        self.flash_interval = 0.1
        
        self.pos = (self.original_x, self.original_y)
    
    def update(self, dt):
        """Update cow logic and animation"""
        # Call parent animation update
        super().update_animation(dt)
        
        if not self.game_started:
            return

        # Handle respawn delay after hole fall
        if self.fell_in_hole:
            self.hole_respawn_delay -= dt
            if self.hole_respawn_delay <= 0:
                if self.parent and self.parent.is_spawn_position_safe():
                    self.fell_in_hole = False
                    self.hole_respawn_delay = 0
                    if self.parent:
                        self.parent.lose_life()
                    return
                else:
                    self.hole_respawn_delay = 0.5
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

        # Handle falling logic
        if self.is_falling and self.fall_reason == 'hole':
            if self.hole_fall_start_x is None:
                self.hole_fall_start_x = self.x
                self.in_hole_phase = True
            
            if self.in_hole_phase and self.top >= 0:
                self.x -= 200 * dt
            
            elif self.top < 0 and self.in_hole_phase:
                self.in_hole_phase = False
                self.fell_in_hole = True
                self.hole_respawn_delay = 1.5
                return
        else:
            # Normal ground collision
            if self.y <= self.ground_level:
                self.y = self.ground_level
                self.velocity_y = 0

    def jump(self):
        """Make the cow jump"""   
        if not self.game_started:
            self.game_started = True

        if not self.is_falling and not self.fell_in_hole:
            self.velocity_y = self.jump_strength

    def start_falling(self, reason='hit'):
        """Start falling animation"""
        self.is_falling = True
        self.fall_reason = reason
        
        if reason == 'hole':
            self.velocity_y = -300
            self.hole_fall_start_x = None
            self.in_hole_phase = False
        
        if reason != 'hole':
            self.start_flashing()

    def start_flashing(self):
        """Start flashing effect"""
        self.is_flashing = True
        self.flash_timer = 0

    def reset_to_ground(self):
        """Reset cow to ground position"""
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
        self.fell_in_hole = False
        self.hole_respawn_delay = 0
        
        self.update_graphics()


class AnimatedKite(AnimatedSprite):
    """Animated kite obstacle"""
    
    def __init__(self, **kwargs):
        super().__init__(
            base_path="assets/images/obstacles/kite",
            frame_count=4,
            frame_duration=FRAME_DURATION   ,  # 20ms per frame
            **kwargs
        )
        
        # Kite-specific properties
        import random
        from kivy.core.window import Window
        from kivy.metrics import dp
        
        self.speed = 300
        self.size = (dp(120), dp(150))
        
        start_x = Window.width * random.uniform(0.4, 0.9)
        start_y = Window.height - random.randint(50, 100)
        self.pos = (start_x, start_y)
        
        if start_x < 0.6 * Window.width:
            self.gravity = 1000 * random.uniform(0.8, 1)
        else:
            self.gravity = 600 * random.uniform(0.8, 1)
            
        self.velocity_y = 0
        self.rotation_speed = random.uniform(180, 360)
        self.horizontal_drift = random.uniform(50, 100)
        self.rotation_angle = 0
    
    def update(self, dt, speed_multiplier=1.0):
        """Update kite movement and animation"""
        # Call parent animation update
        super().update_animation(dt)
        
        # Update position
        self.x -= self.speed * speed_multiplier * dt
        
        # Apply gravity and drift
        self.velocity_y -= self.gravity * dt
        self.velocity_y = max(self.velocity_y, -100)
        self.y += self.velocity_y * dt
        self.rotation_angle += self.rotation_speed * dt
        self.x -= self.horizontal_drift * dt
        
        # Return True if off screen
        return self.x < -self.width


# Helper function to create animated sprites
def create_animated_cow(skin_id="bo", **kwargs):
    """Create an animated cow with specified skin"""
    return AnimatedCow(skin_id=skin_id, **kwargs)

def create_animated_kite(**kwargs):
    """Create an animated kite obstacle"""
    return AnimatedKite(**kwargs)