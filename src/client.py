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
    username = ObjectProperty(None)
    def submit(self):
        print(self.username.text.strip() + " was written when submitting")
        logic.username=self.username.text.strip()
        if (len(self.username.text.strip()) == 0):
            return
        app.title = "QUIZ IT! (" + logic.username + ")"
        if not logic.try_to_connect():
            wm.current = "connError"
        else:
            wm.current = "wait"

class WaitWindow(Screen):
    info = ObjectProperty(None)
    users = ObjectProperty(None)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    def start(self):
        logic.start()
    def process(self, msg):
        pass
    def setUsers(self, usrs):
        self.users.text = "List of users\n"
        for usr in usrs:
            self.users.text += usr + "\n"




class QuizWindow(Screen):
    question = ObjectProperty(None)

    b1 = ObjectProperty(None)
    b2 = ObjectProperty(None)
    b3 = ObjectProperty(None)
    b4 = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def button_pressed(self, answer):
        print("button " + answer + " pressed")
        if not self.answered:
            logic.send_msg(answer, "a")
            self.answered = True
            return
        if not self.question.text.endswith("Wait for result now..."):
            self.question.text = self.question.text + "\nWait for result now..."

    def redraw_quest(self, q):
        self.answered = False
        self.question.text = q[0]
        self.b1.text = q[1][0]
        self.b2.text = q[1][1]
        self.b3.text = q[1][2]
        self.b4.text = q[1][3]

    def process_quest(self, q):
        self.redraw_quest(q)
        print("Draw a question!")
        return

    def process_win(self, w):
        if w == logic.username:
            w = "Correct!"
        else:
            w = w + " gave the correct answer"
        self.question.text = w

class ResultWindow(Screen):
    winner = ObjectProperty(None)
    def __init__(self, winnerName, **kwargs):
        super().__init__(**kwargs)
        self.winnerName = winnerName
    winner = ObjectProperty(None)
    def return_start(self, dt):
        wm.current = "wait"
    def process(self, msg):
        print(f"ResultWindow received something {msg}")
        if msg.split(" ")[0] != logic.username:
            self.winner.text = "'" + msg + "'" + "Won\n"
            self.winner.text += "'" + logic.username + ", " + "keep trying\n"
        if msg.split(" ")[0] == logic.username:
            self.winner.text = f"Congrats! You Won!\n{msg}"
        Clock.schedule_once(self.return_start, 5)

class ConnErrWindow(Screen):
    def try_again(self):
        print("trying again...")
        if logic.try_to_connect():
            print("succeed")
            wm.current = "wait"
        else:
            print("failed")
            wm.current = "connError"

class WindowManager(ScreenManager):
    pass
Builder.load_file("client.kv")


wm = WindowManager()
logic = ClientLogic()


waitWindow = WaitWindow(name="wait")
screens = [ConnErrWindow(name = "connError"), WelcomeWindow(name = "welcome"), waitWindow, QuizWindow(name="quiz"), ResultWindow(winnerName="Nobody", name="result")]
for screen in screens:
    wm.add_widget(screen)

wm.current = "welcome"



class ClientApp(App):
    def build(self):
        self.title = "QUIZ IT!"
        Clock.schedule_interval(self.my_callback, 0.2)
        return wm
    def exit(self):
        logic.end_session()
        sys.exit()
    def my_callback(self, dt):
        msg, msg_type = logic.get_income()
        if msg_type is False:
            return
        if msg_type == "e":
            if wm.current == "connError":
                return
            if msg == "closed":
                wm.current = "connError"
                return
            logic.end_session()
            app.stop()
            sys.exit()
        if msg_type == "i":
            if msg == "start":
                wm.current = "quiz"
                return
            if msg == "already":
                wm.current = "quiz"
                return
            if msg == "end":
                wm.current = "result"
                return
        if msg_type == "W":
            wm.current = "result"
            wm.current_screen.process(msg)
            return
        if msg_type == "q":
            wm.current = "quiz"
            wm.current_screen.process_quest(msg)
            return
        if msg_type == "w":
            wm.current = "quiz"
            wm.current_screen.process_win(msg)
            return
        if msg_type == "o":
            if type(msg) == type(123):
                if msg == "gotowait":
                    wm.current = "wait"
                    return
                print("Got msg_type 'o' but unknown instructions")
            print("Got msg_type 'o' but unknown instructions")
        if msg_type == "u":
            waitWindow.setUsers(msg)
            return

        print(f"Got unrecognized message {msg} of msg_type {msg_type}" )
            #pdb.set_trace()
        #wm.current_screen.my_callback(dt)




if __name__ == "__main__":
    app = ClientApp()
    app.run()