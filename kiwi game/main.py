from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.core.audio import SoundLoader
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.properties import NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics.transformation import Matrix
from kivy.graphics.context_instructions import PushMatrix, PopMatrix

import random
import math

class MainMenu(Screen):
    def __init__(self, **kwargs):
        super(MainMenu, self).__init__(**kwargs)
        self.add_background()
        self.add_start_button()
        self.add_mario_image()

    def add_background(self):
        background = Image(source='background.png')
        background.size = Window.size
        self.add_widget(background)

    def add_start_button(self):
        start_button = Button(text="Start Game", size_hint=(None, None), size=(200, 50), pos=(Window.width - 280, 250))
        start_button.bind(on_press=self.start_game)
        self.add_widget(start_button)

    def add_mario_image(self):
        mario_image = Image(source='mario.png', size_hint=(None, None), size=(200, 200), pos=(80, 250))
        self.add_widget(mario_image)

    def start_game(self, instance):
        self.manager.get_screen('game').start_game()
        self.manager.current = 'game'



class MarioGame(Widget):
    gravity = 0.3
    jump_strength = 7
    move_speed = 3
    score = NumericProperty(0)
    collision_radius = 20

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cols = []
        self.add_background()
        self.add_mario()
        self.sound_jump = SoundLoader.load('jump.wav')
        self.sound_score = SoundLoader.load('score.wav')
        self.sound_collision = SoundLoader.load('collision.wav')
        self.column_speed = self.move_speed
        self.game_started = False

    def add_background(self):
        background = Image(source='background.png')
        background.size = Window.size
        self.add_widget(background)

    def add_mario(self):
        self.mario = Image(source='mario.png')
        self.mario.size_hint = (None, None)
        self.mario.size = (70, 70)
        self.mario.pos = (100, 100)
        self.add_widget(self.mario)
        self.velocity_y = 0

    def create_columns(self):
        for i in range(3):
            # Generate top column
            top_column = Image(source='column.png')
            top_column.size_hint = (None, None)
            top_column.size = (100, random.randint(100, Window.height / 2))
            top_column.pos = (Window.width + i * 300, Window.height - top_column.height)
            self.add_widget(top_column)
            self.cols.append(top_column)

            # Generate bottom column
            bottom_column = Image(source='column.png')
            bottom_column.size_hint = (None, None)
            bottom_column.size = (100, Window.height - top_column.height - 200)
            bottom_column.pos = (Window.width + i * 300, 0)
            self.add_widget(bottom_column)
            self.cols.append(bottom_column)

    def update(self, dt):
        if not self.game_started:
            return

        # Movement of Mario
        self.velocity_y -= self.gravity
        self.mario.y += self.velocity_y

        # Check for collisions with columns
        self.check_collision()

        # Move columns to the left
        for column in self.cols:
            column.x -= self.column_speed
            if column.right < 0:
                column.x = Window.width
                if column.y == 0:
                    column.height = random.randint(100, Window.height / 2)
                else:
                    column.height = Window.height - column.height - 200
                self.score += 0.5
                self.sound_score.play()

        # Increase column speed with time
        self.column_speed += 0.001

    def check_collision(self):
        mario_center = Vector(self.mario.center)
        mario_radius = self.mario.width / 2 - self.collision_radius

        for column in self.cols:
            if column.collide_widget(self.mario):
                column_center = Vector(column.center)
                distance = mario_center.distance(column_center)

                if distance < mario_radius + column.width / 2:
                    self.velocity_y = 0
                    if column.y == 0:
                        self.mario.y = column.top
                    else:
                        self.mario.y = column.y - self.mario.height
                    self.sound_collision.play()
                    self.game_over()

    def game_over(self):
        message_box = BoxLayout(orientation='vertical')
        message = Label(text="Game Over!\nScore: {}".format(int(self.score)),
                        font_size='30sp', halign='center', valign='middle',
                        size_hint=(None, None), size=(Window.width * 0.8, Window.height * 0.8))
        message_box.add_widget(message)
        self.add_widget(message_box)
        Clock.unschedule(self.update)

    def on_touch_down(self, touch):
        self.velocity_y = self.jump_strength
        self.sound_jump.play()

    def start_game(self):
        self.create_columns()
        self.game_started = True
        Clock.schedule_interval(self.update, 1.0 / 60.0)

class GameScreen(Screen):
    def __init__(self, **kwargs):
        super(GameScreen, self).__init__(**kwargs)
        self.game = MarioGame()
        self.add_widget(self.game)

    def start_game(self):
        self.game.start_game()

class MarioApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MainMenu(name='menu'))
        sm.add_widget(GameScreen(name='game'))
        return sm

if __name__ == '__main__':
    MarioApp().run()
