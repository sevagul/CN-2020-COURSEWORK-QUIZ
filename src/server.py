import socket
import select
import time

#defining protoclols parameters
HEADER_LENGTH = 10
exit_commands = ("close", "exit", "quit")
msg_types = {
    "j": "Username", #Information about the username immediately after connecting to the server
    "c": "command", #command for the server. Available commands: start
    "i": "inform", #inform clients about quiz start or end
    "q": "question", # ask question during the quiz
    "a": "answer", # send answer for the question
    "w": "winner", # announce the winner
    "e": "exit", # cancel the connection
    "o": "other" # other type. Temporary type to adopt previous version
    }


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

def accept_client(socket, sockets_list, clients):
    client_socket, client_address = socket.accept()
    user, type = receive_msg(client_socket)
    if type != "j":
        print(f"Connecting failed: type '{type}'' insted of 'j' in header" )
        return False
    if user is False:
        return False
    sockets_list.append(client_socket)
    clients[client_socket] = user
    print((f"Accepted new connectinon from {client_address[0]} : {client_address[1]}",
           f'{user}'))
    return True

def assert_type(expected, real, user, msg):
    if real != expected:
        print(f"Unexpected msg type {real}('{expected}' expected) \n"
              f"from {user} with payload {msg}. ")
        return False
    return True

def closed_connection(notified_socket, sockets_list, clients, user):
    print(f'Closed connection from {user}')
    sockets_list.remove(notified_socket)
    del clients[notified_socket]

def broadcast(msg, clients, msg_type="o"):
    for client in clients.keys():
        client.send(cr_msg(msg, msg_type))
    print(f"Broadcasting message {msg} type {msg_type}" )


#defining data for TCP and IP protocols
IP = "127.0.0.1"
PORT = 1234

server_soket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_soket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # allowing trying to connect to the port several times

#connecting to the port and starting listening to it
server_soket.bind((IP, PORT))
server_soket.listen()

#storing all the sockets
sockets_list = [server_soket]
clients = {}

#defining data for the quiz
questions = ["question1", 'question2', 'question3']
TIME_FOR_QUESTION = 10

run = True
while run: #main loop
    quiz_started = False

    while not quiz_started: #accepting all connections and listening to the commands
        read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)
        for notified_socket in read_sockets:
            if notified_socket == server_soket: # accepting connection
                if not accept_client(server_soket, sockets_list, clients):
                    print(f"Error with connecting client")
            else: #listening to the commands
                msg, type = receive_msg(notified_socket)
                user = clients[notified_socket]
                if type == "e": #connection closed
                    closed_connection(notified_socket, sockets_list, clients, user)
                    continue
                if type == "continue" or quiz_started:
                    continue

                if not assert_type('c', type, user, msg):
                    continue

                #print(f"Received command from {user}: {msg}")
                if msg == "start":
                    quiz_started = True
                    broadcast("start", clients, "i")
                    print("THE QUIZ IS STARTED")

        for notified_socket in exception_sockets:
            sockets_list.remove(notified_socket)
            del clients[notified_socket]

    for q in questions:

        print(f"Asking the question: {q}")
        broadcast(q, clients, "q")
        t = time.time()

        #listening to the answers
        while time.time() - t < TIME_FOR_QUESTION: # collecting the answers
            # import pdb
            # pdb.set_trace()
            read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list, 1)
            for notified_socket in read_sockets:
                if notified_socket == server_soket: #accepting new connection
                    if not accept_client(server_soket, sockets_list, clients):
                        print(f"Error with connecting client")
                else:
                    answ, type = receive_msg(notified_socket)
                    user = clients[notified_socket]
                    if type == "e":
                        closed_connection(notified_socket, sockets_list, clients, user)
                        continue
                    if type == "continue":
                        continue
                    if not assert_type('a', type, user, answ):
                        continue

                    print(f"Received an answer from {user}: {answ} on {int(time.time() - t)} seconds")

            for notified_socket in exception_sockets:
                sockets_list.remove(notified_socket)
                del clients[notified_socket]

        #announcing the winner
        broadcast("Friendship", clients, "w")
        print(f"time: {time.time() - t} ")
    broadcast("end", clients, "i")
