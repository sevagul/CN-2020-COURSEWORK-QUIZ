from tkinter import *
class Window:
    def __init__(self):
        self.root = Tk()
        root = self.root
        self.welcomeWindow = WelcomeWindow(root)
        self.welcomeWindow.pack()
        root.configure(bg="blue", width=100, height=100 )
        root.title("Does a pinguin have elbows?")
        self.root.mainloop()
    def setContinueCmd(self, cmd):
        self.welcomeWindow.setClickCmd(cmd)
    def






class WelcomeWindow:
    def __init__(self, root):
        self.root = root
        self.welcome_label = Label(root, text="Welcome!\n Please. enter your nickname!")
        self.name_enter = Entry(root, text="Enter your nickname", borderwidth=5)
        self.buttonEnter = Button(root, text="Enter")
        self.setClickCmd(lambda :print("buttonClicked"))
    def pack(self):
        self.welcome_label.pack()
        self.name_enter.pack()
        self.buttonEnter.pack()
    def setClickCmd(self, cmd):
        self.buttonEnter.configure(command=cmd)
    def getText(self):
        return self.name_enter.get()
