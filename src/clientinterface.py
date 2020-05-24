import kivy
from kivy.app import App
from kivy.event import EventDispatcher
from kivy.graphics.context import Clock
from kivy.graphics.context_instructions import Color
from kivy.graphics.instructions import Callback
from kivy.graphics.vertex_instructions import Rectangle
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
import time
from kivy.uix.floatlayout import FloatLayout
from kivy.lang import Builder
from clientlogic import ClientLogic
import sys



class WelcomeWindow(Screen):
    def my_callback(self, dt):
        pass
    username = ObjectProperty(None)
    def submit(self):
        print(self.username.text + " was written when submitting")
        logic.username=self.username.text
        if not logic.try_to_connect():
            wm.current = "connError"
        else:
            wm.current = "wait"

# class MyEventDispatcher(EventDispatcher):
#     def __init__(self, **kwargs):
#         self.register_event_type('on_test')
#         super(MyEventDispatcher, self).__init__(**kwargs)
#
#     def do_something(self, value):
#         # when do_something is called, the 'on_test' event will be
#         # dispatched with the value
#         self.dispatch('on_test', value)
#
#     def on_test(self, *args):
#         print "I am dispatched", args


class WaitWindow(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas:
            #Color(1, 1, 1)
            #Rectangle(pos=self.pos, size=self.size)
            Callback(self.my_callback)
    def my_callback(self, dt):
        if logic.check_socket():
            print("WaitWindow Received ANY command")
            if logic.check_if_started():
                print("WaitWindow Received start command")
                wm.current = "quiz"

    def start(self):
        logic.start()
class QuizWindow(Screen):
    question = ObjectProperty(None)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    def my_callback(self, dt):
         if logic.check_socket():
             a, type = logic.check_question()
             print(f"QuizWindow received something {a} {type}")
             if type is False:
                 print(f"a is False {a}")
                 wm.current = "result"
                 return
             if type == "e":
                 sys.exit()
             if type == "w":
                self.winner_announced()
                a = a + " gave the first correct answer"
             print(f"a {a}")
             if type == "i" and a == "end":
                 wm.current_screen = "result"
                 return
             self.question.text = a

    def winner_announced(self):
        pass

class ResultWindow(Screen):
    def __init__(self, winner, **kwargs):
        super().__init__(**kwargs)
        self.winner = winner
    winner = ObjectProperty(None)
    def my_callback(self, dt):
        pass

class ConnErrWindow(Screen):
    def my_callback(self, dt):
        pass
    def try_again(self):
        print("trying again...")
        if logic.try_to_connect():
            print("succeed")
            wm.current = "welcome"
        else:
            print("failed")
            wm.current = "connError"

class WindowManager(ScreenManager):
    pass
Builder.load_file("client.kv")


wm = WindowManager()
logic = ClientLogic()

screens = [ConnErrWindow(name = "connError"), WelcomeWindow(name = "welcome"), WaitWindow(name="wait"), QuizWindow(name="quiz"), ResultWindow(winner="Nobody", name="result")]
for screen in screens:
    wm.add_widget(screen)

wm.current = "welcome"



class ClientApp(App):
    def build(self):
        Clock.schedule_interval(self.my_callback, 0.5)
        return wm
    def exit(self):
        logic.end_session()
        sys.exit()
    def my_callback(self, dt):
        if wm.current_screen == "quiz":
            pass
            #import pdb
            #pdb.set_trace()
        wm.current_screen.my_callback(dt)




if __name__ == "__main__":
    app = ClientApp()
    app.run()








    # logic = ClientLogic()
    # connected = False
    # while not connected:
    #     connected = logic.try_to_connect()
    #     if not connected:
    #         show_popup()
    # MyyApp().run()

# class Widgets(Widget):
#     def btn(self):
#         show_popup()
#
# class P(FloatLayout):
#     pass
#
# def show_popup():
#     show = P()
#     popupWindow = Popup(title="Popup window", content= show, size_hint= (None, None), size=(400,400))
#     popupWindow.open()

# self.title="Does the pinguin have elbows?"