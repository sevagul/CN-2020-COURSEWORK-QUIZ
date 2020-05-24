import kivy
from kivy.app import App
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



class WelcomeWindow(Screen):
    pass
class ConnErrWindow(Screen):
    pass
class WindowManager(ScreenManager):
    pass
Builder.load_file("client.kv")


wm = WindowManager()
logic = ClientLogic()

screens = [ConnErrWindow(name = "connError"), WelcomeWindow(name = "welcome")]
for screen in screens:
    wm.add_widget(screen)

if not logic.try_to_connect():
    wm.current = "connError"
else:
    wm.current = "welcome"



class ClientApp(App):
    def build(self):
        return wm

if __name__ == "__main__":
    ClientApp().run()






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