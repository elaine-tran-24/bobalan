def check_collision(self, obstacle):
    """Check collision between cow and obstacle"""
    
    # Special handling for holes - check if cow center is over hole center
    if obstacle.obstacle_type == 'hole':
        cow_center_x = self.cow.center_x
        hole_center_x = obstacle.center_x
        
        # Only trigger hole fall when cow's center reaches hole's center
        # Add small tolerance to make it feel natural
        tolerance = 30  # pixels - you can adjust this value
        
        if abs(cow_center_x - hole_center_x) <= tolerance and self.cow.y <= self.cow.ground_level:
            print(f'Cow fell into hole center! Hole center: {hole_center_x}')
            self.cow.start_falling_into_hole(hole_center_x)
            self.play_sound_async('hit')
            return
    
    # Normal collision detection for other obstacles
    elif self.cow.collide_widget(obstacle):
        print(f'Cow hit obstacle: {obstacle.obstacle_type}')
        app = App.get_running_app()
        
        if obstacle.obstacle_type == 'electric_wire':
            self.play_sound_async('game_over')
            self.game_over()
            return
        
        else:
            # Regular obstacles
            self.play_sound_async('hit')
            self.cow.start_falling('hit')
            
            # Remove obstacle
            self.remove_widget(obstacle)
            self.obstacles.remove(obstacle)
            
            # Lose life after a short delay
            Clock.schedule_once(lambda dt: self.lose_life(), 0.5)

def lose_life(self):
    """Lose a life with delayed cow reappearance for holes"""
    self.lives -= 1
    self.update_ui()
    
    # Add delay for cow reappearance if it fell into a hole
    if self.cow.fall_reason == 'hole':
        # Longer delay for hole falls to make it feel more dramatic
        Clock.schedule_once(lambda dt: self._reset_cow_after_hole(), 1.5)
    else:
        # Immediate reset for other obstacles
        self._reset_cow_after_hole()
    
    if self.lives <= 0:
        self.game_over()

def _reset_cow_after_hole(self):
    """Helper method to reset cow position"""
    self.cow.reset_to_ground()
    self.cow.pos = (dp(100), self.cow.ground_level)