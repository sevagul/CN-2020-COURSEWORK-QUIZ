import socket
import select
import errno
import sys
import time

class ClientLogic:
    def __init__(self, ):
        self.HEADER_LENGTH = 10
        self.exit_commands = ("close", "exit", "quit")
        self.msg_types = {
            "j": "Username",  # Information about the username immediately after connecting to the server
            "c": "command",  # cammand for the server. Available commands: start
            "i": "inform",  # inform clients about quiz start or end
            "q": "question",  # ask question during the quiz
            "a": "answer",  # send answer for the question
            "w": "winner",  # announce the winner
            "e": "exit",  # cancel the connection
            "o": "other"  # other type. Temporary type to adopt previous version
        }
        self.client_sates = {
            "connecting": 0,
            "identification": 1,
            "waiting_for_quiz": 2,
            "answering_the_question": 3,
            "waiting_for_the_next_question": 4,
            "watching_the_results": 5,
        }
        self.IP = "127.0.0.1"
        self.PORT = 1234

        # defining vars for clients logic
        roles = {"w",  # to wait for the quiz
                 "c",  # to write command for the server
                 "o"  # to just observe all the process
                 }

        # connecting to the server
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)



    def try_to_connect(self):
        try:
            self.client_socket.connect((self.IP, self.PORT))
            self.client_socket.setblocking(False)
            print("Successfully connected to the server!")
            return True
        except Exception as ex:
            print(str(ex))
            return False
        # print('Failed to connect to ', IP, " ", PORT, ".\n ERROR: ", str(ex))
        # print("To try the connection again, type yes, to exit do whatewer you want.")
        # answ = input(f"Enter the answer > ")
        # if answ.strip() == "yes":
        #     continue
        # else:
        #     sys.exit()

    def cr_header(self, str, msg_type):
        assert len(msg_type) == 1
        return f"{len(str):<{self.HEADER_LENGTH}}".encode() + msg_type.encode()

    def cr_msg(self, msg, msg_type="o"):
        return self.cr_header(msg, msg_type) + msg.encode()

    def receive_msg(self):
        try:
            msg_header = self.client_socket.recv(self.HEADER_LENGTH).decode()
            if msg_header == "":
                return ("", "e")  # connection is closed
            msg_len = int(msg_header)
            msg_type = self.client_socket.recv(1).decode()
            msg = self.client_socket.recv(msg_len).decode()
            answ = (msg, msg_type)
            print(f"\t\t\tReceived msg: {msg}. type: {msg_type}")
            return answ
        except:
            return ("", "continue")

    def check_socket(self):
        import pdb
        pdb.set_trace()
        socket, *_ = select.select([self.client_socket], [], [self.client_socket], 0)
        if socket == []:
            return "continue"
        return "e"

    def assert_type(self, expected, real, user, msg):
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

    def end_session(self, send_msg=False):
        if send_msg:
            self.client_socket.send(self.cr_msg("Closing connection", "e"))
        self.client_socket.close()
        sys.exit()

    def send_msg(self, msg, type):
        self.client_socket.send(self.cr_msg(msg, type))
        print(f"\t\tSent message {self.cr_msg(msg, type)}")