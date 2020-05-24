import kivy
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup

from kivy.uix.floatlayout import FloatLayout
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen


class Widgets(Widget):
    def btn(self):
        show_popup()

class P(FloatLayout):
    pass





class MyyApp(App):
    def build(self):
        return Widgets()

def show_popup():
    show = P()
    popupWindow = Popup(title="Popup window", content= show, size_hint= (None, None), size=(400,400))

    popupWindow.open()



# kv = Builder.load_file("myy.kv")

if __name__ == "__main__":
    MyyApp().run()


