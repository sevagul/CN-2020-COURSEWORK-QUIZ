from tkinter import *

popup = Tk()
popup.title("Error")
label=Label(popup, text="Error while connecting to the server")
button1 = Button(popup, text="exit from program")
button2 = Button(popup, text="try to connect again")
label.grid(column=0, row=0, columnspan=2)
def cmd1():
    popup.destroy()
    return False
def cmd2():
    popup.destroy()
    return True
button1.configure(command = cmd1)
button2.configure(command = cmd2)
button1.grid(column=0, row=1)
button2.grid(column=1, row=1)
def f():
    print ("444")
    popup.after(1, f)
popup.after(100, f)
mainloop()