from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.metrics import dp
from kivy.app import App
from kivy.logger import Logger

class ShopScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_tab = 'skin'  # Default tab
        self.build_ui()

    def build_ui(self):
        self.main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Title
        title = Label(text='[b][size=32]🛒 Shop[/size][/b]', markup=True, size_hint=(1, 0.1))
        self.main_layout.add_widget(title)

        # Points display
        self.points_label = Label(text='', size_hint=(1, 0.05), halign='center')
        self.points_label.markup = True
        self.main_layout.add_widget(self.points_label)

        # Tab buttons
        tab_layout = BoxLayout(size_hint=(1, 0.1), spacing=10)
        skin_btn = Button(text='Skins', on_press=lambda x: self.switch_tab('skin'))
        background_btn = Button(text='Backgrounds', on_press=lambda x: self.switch_tab('background'))
        tab_layout.add_widget(skin_btn)
        tab_layout.add_widget(background_btn)
        self.main_layout.add_widget(tab_layout)

        # Scrollable item list
        scroll = ScrollView(size_hint=(1, 0.65))
        self.item_container = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None)
        self.item_container.bind(minimum_height=self.item_container.setter('height'))
        scroll.add_widget(self.item_container)
        self.main_layout.add_widget(scroll)

        # Back button
        back_btn = Button(text='← Back', size_hint=(1, 0.1))
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'main_menu'))
        self.main_layout.add_widget(back_btn)

        self.add_widget(self.main_layout)

    def switch_tab(self, tab_type):
        self.current_tab = tab_type
        self.refresh_shop()

    def on_enter(self):
        self.refresh_shop()

    def refresh_shop(self):
        self.item_container.clear_widgets()
        app = App.get_running_app()
        dm = app.data_manager

        points = dm.get_total_points()
        purchased = dm.get_purchased_items()
        items = [item for item in dm.get_shop_items() if item['type'] == self.current_tab]

        # Chọn đúng loại đã trang bị
        equipped = dm.get_equipped_skin() if self.current_tab == 'skin' else dm.get_equipped_background()

        self.points_label.text = f'[b]Points: {points}[/b]'

        for item in items:
            item_id = item['id']
            name = item['name']
            cost = item['cost']

            box = BoxLayout(size_hint_y=None, height=dp(60), padding=5, spacing=10)

            label = Label(
                text=f'{name} [color=ffffaa]{cost} pts[/color]',
                markup=True,
                halign='left',
                valign='middle',
                size_hint=(0.6, 1)
            )
            label.bind(size=label.setter('text_size'))

            btn = Button(size_hint=(0.4, 1))

            if item_id in purchased:
                if item_id == equipped:
                    btn.text = 'Using'
                    btn.disabled = True
                else:
                    btn.text = 'Use'
                    btn.bind(on_press=lambda b, i=item_id: self.use_item(i))
            else:
                btn.text = f'Buy ({cost})'
                if cost <= points:
                    btn.bind(on_press=lambda b, i=item_id: self.buy_item(i))
                else:
                    btn.bind(on_press=lambda b: self.show_popup("Not enough points!"))

            box.add_widget(label)
            box.add_widget(btn)
            self.item_container.add_widget(box)

    def buy_item(self, item_id):
        app = App.get_running_app()
        dm = app.data_manager
        if dm.purchase_item(item_id):
            app.sound_manager.play_sound('coin')
            self.show_popup("Purchase successful!")
            self.use_item(item_id)  # Tự động trang bị luôn sau khi mua
        else:
            app.sound_manager.play_sound('error')
            self.show_popup("Not enough points or already owned!")
        self.refresh_shop()

    def use_item(self, item_id):
        app = App.get_running_app()
        dm = app.data_manager
        item = dm.get_item_by_id(item_id)
        if not item:
            self.show_popup("Invalid item.")
            return

        if item['type'] == 'skin':
            dm.set_equipped_skin(item_id)
        elif item['type'] == 'background':
            dm.set_equipped_background(item_id)

        app.sound_manager.play_sound('equip')
        self.preview_item(item_id)
        self.refresh_shop()

    def preview_item(self, item_id):
        app = App.get_running_app()
        if item_id.startswith("bo_"):
            path = f"assets/images/characters/{item_id}.png"
        elif item_id.startswith("background_"):
            path = f"assets/images/backgrounds/{item_id}.png"
        else:
            return
        Logger.info(f"Previewing: {path}")
        # Hiển thị ở một nơi nào đó (nếu bạn muốn)

    def show_popup(self, message):
        popup = Popup(title='Shop',
                      content=Label(text=message),
                      size_hint=(None, None), size=(300, 200))
        popup.open()
