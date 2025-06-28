from kivy.uix.screenmanager import Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.popup import Popup
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.behaviors import ButtonBehavior
from screens.background import ParallaxWidget
from screens.hover_button import HoverImageButton
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.boxlayout import BoxLayout

# Button hình ảnh
class ImageButton(ButtonBehavior, Image):
    pass

class ShopScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Nền parallax
        self.bg_parallax = ParallaxWidget()
        self.add_widget(self.bg_parallax)

        self.current_index = 0
        self.skin_items = []

        self.build_ui()
        Window.bind(size=self.update_bg)

    def update_bg(self, *args):
        if hasattr(self, 'bg_parallax'):
            self.bg_parallax.on_resize()

    def build_ui(self):
        self.main_layout = FloatLayout()
        self.add_widget(self.main_layout)

       # Layout chứa icon và điểm
        points_container = BoxLayout(
            orientation='horizontal',
            size_hint=(None, None),
            size=(200, 50),
            pos_hint={'center_y': 0.87, 'center_x': 0.5},
            spacing=10
        )

        # Icon tiền
        coin_icon = Image(
            source="assets/images/buttons/total_score.png",  
            pos_hint={'center_y': 0.89, 'center_x': 0.5},
            size_hint=(None, None),
            size=(80, 80)
        )
        points_container.add_widget(coin_icon)

        # Nhãn số điểm
        self.points_label = Label(
            text='',
            markup=True,
            font_name="assets/fonts/HeeHawRegular.ttf",
            font_size=55,
            pos_hint={'center_y': 0.89, 'center_x': 0.5},
            halign='left',
            valign='middle'
        )
        self.points_label.bind(size=self.points_label.setter('text_size'))

        self.points_label.bind(size=self.points_label.setter('text_size'))

        points_container.add_widget(self.points_label)
        self.main_layout.add_widget(points_container)

        # Frame nền của shop
        self.shop_frame = Image(
            source="assets/images/backgrounds/shop.png",
            allow_stretch=True,
            keep_ratio=True,
            size_hint=(0.7, 0.7),
            size=(1000, 700),
            pos_hint={"center_x": 0.5, "center_y": 0.5}
        )
        self.main_layout.add_widget(self.shop_frame)

        # Ảnh nhân vật (skin)
        self.skin_image = Image(
            allow_stretch=True,
            size_hint=(None, None),
            size=(300, 300),
            pos_hint={"center_x": 0.5, "center_y": 0.50}
        )
        self.main_layout.add_widget(self.skin_image)

        # Nút trái
        self.left_btn = HoverImageButton(
            source="assets/images/buttons/left_button.png",
            size_hint=(None, None),
            size=(120, 120),
            pos_hint={"center_x": 0.29, "center_y": 0.42}
        )
        self.left_btn.bind(on_press=self.prev_skin)
        self.main_layout.add_widget(self.left_btn)

        # Nút phải
        self.right_btn = HoverImageButton(
            source="assets/images/buttons/right_button.png",
            size_hint=(None, None),
            size=(120, 120),
            pos_hint={"center_x": 0.70, "center_y": 0.42}
        )
        self.right_btn.bind(on_press=self.next_skin)
        self.main_layout.add_widget(self.right_btn)

        # Giá skin
        # Layout chứa hình và nhãn chồng lên nhau
        price_container = RelativeLayout(
            size_hint=(None, None),
            size=(160, 80),
            pos_hint={"center_x": 0.5, "center_y": 0.35}
        )

        # Hình nền phía sau
        price_bg = Image(
            source="assets/images/buttons/price.png", 
            allow_stretch=True,
            keep_ratio=False,
            size_hint=(None, None),
            size=(160, 80),
            pos_hint={"center_x": 0.5, "center_y": 0.35}
        )
        price_container.add_widget(price_bg)

        # Nhãn giá
        self.price_label = Label(
            text='',
            markup=True,
            font_name="assets/fonts/HeeHawRegular.ttf",
            halign='center',
            valign='middle',
            size_hint=(None, None),
            font_size=40,
            size=(160, 80),
            pos_hint={"center_x": 0.5, "center_y": 0.35}
        )
        self.price_label.bind(size=self.price_label.setter('text_size'))

        price_container.add_widget(self.price_label)

        # Thêm container vào layout chính
        self.main_layout.add_widget(price_container)

        # Nút hành động (Buy/Use/Using)
        self.action_btn = HoverImageButton(
            size_hint=(None, None),
            size=(260, 100),
            pos_hint={"center_x": 0.5, "center_y": 0.26},
            allow_stretch=True
        )
        self.action_btn.bind(on_press=self.on_action_pressed)
        self.main_layout.add_widget(self.action_btn)

        # Nút quay lại
        self.back_btn = HoverImageButton(
            source="assets/images/buttons/home.png",
            size_hint=(None, None),
            size=(120, 120),
            pos_hint={"right": 0.98, "y": 0.02}
        )
        self.back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'main_menu'))
        self.main_layout.add_widget(self.back_btn)

    def on_enter(self):
        app = App.get_running_app()
        self.dm = app.data_manager
        self.skin_items = [item for item in self.dm.get_shop_items() if item['type'] == 'skin']
        self.current_index = 0
        self.refresh_skin_display()

    def prev_skin(self, *args):
        self.current_index = (self.current_index - 1) % len(self.skin_items)
        self.refresh_skin_display()

    def next_skin(self, *args):
        self.current_index = (self.current_index + 1) % len(self.skin_items)
        self.refresh_skin_display()

    def refresh_skin_display(self):
        item = self.skin_items[self.current_index]
        app = App.get_running_app()
        points = self.dm.get_total_points()
        purchased = self.dm.get_purchased_items()
        equipped = self.dm.get_equipped_skin()

        self.points_label.text = f'[color=583101][b]${points}[/b][/color]'

        # Cập nhật ảnh nhân vật
        skin_path = f"assets/images/characters/{item['id']}.gif"
        self.skin_image.source = skin_path

        # Nhãn giá
        self.price_label.text = f"[color=583101][b]${item['cost']}[/b][/color]"

        # Cập nhật nút hành động
        if item['id'] not in purchased:
            self.action_btn.source = "assets/images/buttons/buy_button.png"
        elif item['id'] == equipped:
            self.action_btn.source = "assets/images/buttons/using_button.png"
        else:
            self.action_btn.source = "assets/images/buttons/use_button.png"

    def on_action_pressed(self, *args):
        item = self.skin_items[self.current_index]
        item_id = item['id']
        purchased = self.dm.get_purchased_items()
        equipped = self.dm.get_equipped_skin()
        app = App.get_running_app()

        if item_id not in purchased:
            if self.dm.purchase_item(item_id):
                app.sound_manager.play_sound('coin')
                self.dm.set_equipped_skin(item_id)
            else:
                self.show_popup("Not enough points!")
                return
        elif item_id != equipped:
            self.dm.set_equipped_skin(item_id)
            app.sound_manager.play_sound('equip')

        self.refresh_skin_display()

    def show_popup(self, message):
        popup = Popup(title='Shop',
                      content=Label(text=message),
                      size_hint=(None, None), size=(300, 200))
        popup.open()