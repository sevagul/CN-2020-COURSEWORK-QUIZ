import socket
import select
import errno
import sys
import time
from tkinter import *

# root = Tk()
# root.title("Does the pinguin have elbows?")
#
# def clearFrame():
#     # destroy all widgets from frame
#     for widget in root.winfo_children():
#        widget.destroy()
#
#     # this will clear frame and frame will be empty
#     # if you want to hide the empty panel then
#     root.pack_forget()
#
# def addWelcomeWindow():
#     global welcome_label, name_enter, buttonEnter, errorLabel
#     welcome_label = Label(root, text="Welcome!\n Please, enter your nickname:")
#     name_enter = Entry(root, text="Enter your nickname", borderwidth=5)
#     buttonEnter = Button(root, text="Enter")
#     buttonEnter.configure(command=lambda: print(name_enter.get()))
#     errorLabel = Label(text="")
#     welcome_label.pack()
#     name_enter.pack()
#     buttonEnter.pack()
#
# addWelcomeWindow()


#defining protocols parameters
HEADER_LENGTH = 10
exit_commands = ("close", "exit", "quit")
msg_types = {
    "j": "Username", #Information about the username immediately after connecting to the server
    "c": "command", #cammand for the server. Available commands: start
    "i": "inform", #inform clients about quiz start or end
    "q": "question", # ask question during the quiz
    "a": "answer", # send answer for the question
    "w": "winner", # announce the winner
    "e": "exit", # cancel the connection
    "o": "other" # other type. Temporary type to adopt previous version
    }


#definig functions for simlified work with protocol
def cr_header(str, msg_type):
    assert len(msg_type) == 1
    return f"{len(str):<{HEADER_LENGTH}}".encode() + msg_type.encode()
def cr_msg(msg, msg_type = "o"):
    return cr_header(msg, msg_type) + msg.encode()
def receive_msg(socket):
    try:
        msg_header = socket.recv(HEADER_LENGTH).decode()
        if msg_header == "":
            return ("", "e") # connection is closed
        msg_len = int(msg_header)
        msg_type = socket.recv(1).decode()
        msg = socket.recv(msg_len).decode()
        answ = (msg, msg_type)
        print(f"\t\t\tReceived msg: {msg}. type: {msg_type}")
        return answ
    except:
        return ("", "continue")

def check_msg(socket):
    # import pdb
    # pdb.set_trace()
    socket, *_ = select.select([socket], [], [], 0)
    if socket == []:
        return "continue"
    return "e"

def assert_type(expected, real, user, msg):
    if real != expected:
        print(f"Unexpected msg type {real}('{expected}' expected) \n"
              f"from {user} with payload {msg}. ")
        return False
    return True

def assert_types(expected, real, user, msg):
    if real not in expected:
        print(f"Unexpected msg type {real}('{expected}' expected) \n"
              f"from {user} with payload {msg}. ")
        return False
    return True
def end_session(socket, send_msg=False):
    if send_msg:
        socket.send(cr_msg("Closing connection", "e"))
    socket.close()
    sys.exit()
def send_msg(msg, type, socket):
    socket.send(cr_msg(msg, type))
    print(f"\t\tSent message {cr_msg(msg, type)}")



#defining data for TCP and IP protocols
IP = "127.0.0.1"
PORT = 1234

#defining vars for clients logic
roles = {"w", #to wait for the quiz
         "c", #to write command for the server
         "o"  #to just observe all the process
         }


#connecting to the server
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
while True:
    try:
        client_socket.connect(( IP, PORT ))
        client_socket.setblocking(False)
        print("Successfully connected to the server!")
        break
    except Exception as ex:
        print('Failed to connect to ', IP, " ", PORT, ".\n ERROR: ", str(ex))
        print("To try the connection again, type yes, to exit do whatewer you want.")
        answ = input(f"Enter the answer > ")
        if answ.strip() == "yes":
            continue
        else:
            sys.exit()

print(f"Welcome to the quiz!\n",
       f"Please enter your username in order to participate in the next available quiz.")
#nameEntered = False
#while not nameEntered:

my_username = input("Username: ")
client_socket.send(cr_msg(my_username, "j"))

while True: #main loop

    print("Please, type down, want do you want to do\n"
          "options are: \n"
          "w - wait for the quiz\n"
          "c - send commands to the server\n"
          "o - to observe the whole process")

    quiz_lasts = False
    # inputing the role of the client
    while True:
        role = input(f"{my_username} > ")
        if role in roles:
            if role == "c":
                print("Type 'start' to start the quiz\n",
                      "Press 'Enter' to check for the new info")
            if role == "w":
                print("Waiting for the quiz starts... (You will participate)")
            if role == "o":
                print("Waiting for the quiz starts... (You will only observe the process)")
            break
        if role.startswith(exit_commands):
            client_socket.send(cr_msg(role, "e"))
            end_session(client_socket, send_msg=True)
        else:
            if check_msg(client_socket) != "continue":
                msg, type = receive_msg(client_socket)
                if not assert_types("i", type) or msg != "start":
                    print("Quiz is in process. Do you want to wait for the current quiz to end?")
                    sys.exit()

                role = "w"
                print("quiz already started, so your role is w")
                quiz_lasts = True
                break

            print("Incorrect input. Try again")

    # waiting for quiz to start
    #quiz_started = False
    start_cmd_received = False
    while True and not quiz_lasts:
        if role == "c" and not start_cmd_received:
            cmd = input(f"{my_username} > ")
            if cmd:
                client_socket.send(cr_msg(cmd, "c"))
                if cmd == "start":
                    start_cmd_received = True

        msg, type = receive_msg(client_socket)
        if type == "continue":
            continue
        if type == "e":
            print("Connection closed by the server")
            end_session(client_socket)
        if not assert_type('i', type, "server", msg):
            end_session(client_socket, send_msg=True)
        # print(f"Message from the server: {msg}")
        if msg == "start":
            #quiz_started = True
            print("Quiz sarted")
            break


    quiz_lasts = True
    while quiz_lasts:
        if not check_msg(client_socket):
            print("Waiting for the question...")
        while True:
            time.sleep(0.5)
            quest, type = receive_msg(client_socket)
            if type == "continue":
                continue
            if type == "e":
                print("Connection closed by the server")
                end_session(client_socket)
            if not assert_types(("q", "i"), type, "server", quest):
                end_session(client_socket, send_msg=True)
            if quest == "end":
                print("The quiz is ended. Now, lets wait for the next round")
                quiz_lasts = False
                break
            print(f"Question: {quest}")
            break

        if quiz_lasts == False:
            break

        #answering the question
        answered = False
        while True:
            if role != "o" and check_msg(client_socket) == "continue" and not answered:
                answ = input(f"{my_username} (Your Suggestion) > ")
                if answ != "":
                    if answ.startswith(exit_commands):
                        end_session(client_socket, True)
                    type = check_msg(client_socket)
                    if type == "continue":
                        send_msg(answ, "a", client_socket)
                        answered = True
                        print("Waiting for the quiz results")
                    else:
                        print("Too late, go further")
            msg, type = receive_msg(client_socket)
            if type == "continue":
                continue
            if type == "e":
                print("Connection closed by the server")
                end_session(client_socket)
            if not assert_type("w", type, "server", msg):
                end_session(client_socket, send_msg=True)
            print(f"Winner: {msg}")
            break