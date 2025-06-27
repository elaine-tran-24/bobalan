"""
Data Manager for When Cows Fly
Handles saving and loading game data using JSON
"""

import json
import os
from kivy.logger import Logger
from kivy.app import App

class DataManager:
    """Manages game data persistence"""

    def __init__(self):
        self.data_file = self.get_data_path()
        self.default_data = {
            'best_score': 0,
            'total_points': 0,
            'purchased_items': [],
            'equipped_skin': None,
            'equipped_background': None,
            'settings': {
                'sound_enabled': True,
                'volume': 0.8,
                'background_music_enabled': True 
            }
        }
        self.load_data()

        # Generate character skins: bo_0 to bo_19, cost 5 to 2000
        self.shop_items = [
            {'id': f'bo_{i}', 'name': f'Character {i}', 'type': 'skin', 'cost': 5 + i * 15} for i in range(20)
        ]
        # Add backgrounds: background_1 to background_10, cost 20 to 3000
        self.shop_items += [
            {'id': f'background_{i+1}', 'name': f'Background {i+1}', 'type': 'background', 'cost': 20 + i * 30} for i in range(10)
        ]

    def get_data_path(self):
        try:
            app = App.get_running_app()
            if app:
                user_data_dir = app.user_data_dir
                if not os.path.exists(user_data_dir):
                    os.makedirs(user_data_dir)
                return os.path.join(user_data_dir, 'game_data.json')
        except Exception as e:
            Logger.warning(f"DataManager: Could not access user data dir: {e}")
        return 'game_data.json'

    def load_data(self):
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    loaded_data = json.load(f)
                    self.data = {**self.default_data, **loaded_data}
                    if 'settings' not in self.data:
                        self.data['settings'] = self.default_data['settings']
                    else:
                        self.data['settings'] = {**self.default_data['settings'], **self.data['settings']}
                Logger.info(f"DataManager: Data loaded successfully")
            else:
                Logger.info("DataManager: No save file found, using defaults")
                self.data = self.default_data.copy()
        except Exception as e:
            Logger.error(f"DataManager: Error loading data: {e}")
            self.data = self.default_data.copy()

    def save_data(self):
        try:
            data_dir = os.path.dirname(self.data_file)
            if data_dir and not os.path.exists(data_dir):
                os.makedirs(data_dir)
            with open(self.data_file, 'w') as f:
                json.dump(self.data, f, indent=2)
            Logger.info(f"DataManager: Data saved successfully. DataManager: Saved to {self.data_file}")
        except Exception as e:
            Logger.error(f"DataManager: Error saving data: {e}")

    # Score & Points
    def get_best_score(self):
        return self.data.get('best_score', 0)

    def set_best_score(self, score):
        self.data['best_score'] = max(score, self.get_best_score())
        self.save_data()

    def get_total_points(self):
        return self.data.get('total_points', 0)

    def add_points(self, points):
        self.data['total_points'] = self.get_total_points() + points
        self.save_data()

    # Settings
    def get_setting(self, key, default=None):
        return self.data.get('settings', {}).get(key, default)

    def set_setting(self, key, value):
        self.data.setdefault('settings', {})[key] = value
        self.save_data()

    def get_sound_enabled(self):
        return self.get_setting('sound_enabled', True)

    def set_sound_enabled(self, enabled):
        self.set_setting('sound_enabled', enabled)

    def get_volume(self):
        return self.get_setting('volume', 0.8)

    def set_volume(self, volume):
        self.set_setting('volume', max(0.0, min(1.0, volume)))

    # Shop & Purchase
    def get_shop_items(self):
        """Return a static list of shop items"""
        items = []
        # Skins bo_0 to bo_19
        for i in range(20):
            items.append({
                "id": f"bo_{i}",
                "name": f"Bo {i}",
                "cost": 50 + i * 10,
                "type": "skin"
            })

        # Backgrounds background_1 to background_10
        for i in range(1, 11):
            items.append({
                "id": f"background_{i}",
                "name": f"Background {i}",
                "cost": 100 + i * 20,
                "type": "background"
            })

        return items

    def get_purchased_items(self):
        return self.data.get('purchased_items', [])

    def has_purchased(self, item_id):
        return item_id in self.get_purchased_items()

    def purchase_item(self, item_id):
        if self.has_purchased(item_id):
            Logger.info(f"DataManager: Item '{item_id}' already purchased.")
            return False

        item = next((i for i in self.shop_items if i['id'] == item_id), None)
        if not item:
            Logger.warning(f"DataManager: Item '{item_id}' not found in shop.")
            return False

        if self.get_total_points() >= item['cost']:
            self.data['total_points'] -= item['cost']
            self.data.setdefault('purchased_items', []).append(item_id)
            self.save_data()
            Logger.info(f"DataManager: Purchased item '{item_id}' successfully.")
            return True
        else:
            Logger.info(f"DataManager: Not enough points to purchase '{item_id}'.")
            return False

    def get_purchased_skins(self):
        return [item_id for item_id in self.get_purchased_items()
                if any(i['id'] == item_id and i['type'] == 'skin' for i in self.shop_items)]

    def get_purchased_backgrounds(self):
        return [item_id for item_id in self.get_purchased_items()
                if any(i['id'] == item_id and i['type'] == 'background' for i in self.shop_items)]

    # Equipped Items
    def get_equipped_skin(self):
        return self.data.get('equipped_skin', None)

    def set_equipped_skin(self, item_id):
        self.data['equipped_skin'] = item_id
        self.save_data()

    def get_equipped_background(self):
        return self.data.get('equipped_background', None)

    def set_equipped_background(self, item_id):
        self.data['equipped_background'] = item_id
        self.save_data()

    def get_item_by_id(self, item_id):
        """Return item dict by ID"""
        return next((item for item in self.shop_items if item['id'] == item_id), None)
    
    def get_music_enabled(self):
        return self.data.get("settings", {}).get("music_enabled", True)

    def set_music_enabled(self, enabled):
        self.set_setting('background_music_enabled', enabled)
