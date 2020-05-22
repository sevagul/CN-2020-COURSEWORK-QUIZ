import socket
import select
import errno
import sys

HEADER_LENGTH = 10

def cr_header(str):
    return f"{len(str):<{HEADER_LENGTH}}".encode("utf-8")
def get_len(header):
    return int(header)

def cr_msg(msg):
    return cr_header(msg) + msg.encode("utf-8")

IP = "127.0.0.1"
PORT = 1234

print(f"Welcome to the quiz!\n",
       f"Please enter your username in order to participate in the next available quiz."
       )
my_username = input("Username: ")

while True:
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect(( IP, PORT ))
        client_socket.setblocking(False)
        print("Successfully connected to the server!")
        break
    except Exception as ex:
        print('Failed to connect to ', IP, " ", PORT, ".\n ERROR: ", str(ex))
        print("To try the connection again, type yes, to exit do whatewer you want.")
        answ = input(f"{my_username} > ")
        if answ.strip() == "yes":
            continue
        else:
            sys.exit()




username = my_username.encode("utf-8")
username_header = cr_header(username)
client_socket.send(username_header + username)

print("Please, type down want do you want to do\n"
      "options are: "
      "w - wait for the quiz"
      "c - send the commands to the serwer")

while True:
    role = input(f"{my_username} > ")
    if role == "w" or role == "c":
        break
    else:
        print("Incorrect input. Try again")

if role == "c":

    quiz_started = False
    while not quiz_started:
        cmd = input(f"{my_username} > ")
        if cmd:
            client_socket.send(cr_msg(cmd))
        try:
            while True:
                msg_header = client_socket.recv(HEADER_LENGTH)
                if not len(msg_header):
                    print("connection closed by the server")
                    sys.exit()
                msg_len = int(msg_header.decode("utf-8"))
                msg = client_socket.recv(msg_len).decode("utf-8")

                # msg_header = client_socket.recv(HEADER_LENGTH)
                # msg_length = int(msg_header)
                #
                # msg = client_socket.recv(msg_length)
                # msg = msg.decode("utf-8")

                print(f"Question: {msg}")

        except IOError as e:
            #print(str(e))
            if e.errno != errno.EAGAIN or e.errno != errno.EWOULDBLOCK:
                print("Reading error ", str(e))
            continue

        except Exception as ex:
            print('General error ', str(ex))
            sys.exit()
if role == "w":
    pass