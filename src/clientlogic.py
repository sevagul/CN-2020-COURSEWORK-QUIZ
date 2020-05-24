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
        self.username="Noname"
        # defining vars for clients logic
        roles = {"w",  # to wait for the quiz
                 "c",  # to write command for the server
                 "o"  # to just observe all the process
                 }

    def try_to_connect(self):
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.IP, self.PORT))
            self.client_socket.setblocking(False)
            self.send_msg(self.username, "j")
            print("Successfully connected to the server!")
            return True
        except Exception as ex:
            print("Failed connecting to the server!")
            print(str(ex))
            return False

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
        socket, *_ = select.select([self.client_socket], [], [self.client_socket], 0)
        if socket == []:
            return False
        return True

    def assert_type(self, expected, real, msg):
        if real != expected:
            print(f"Unexpected msg type {real}('{expected}' expected) \n"
                  f"from {self.username} with payload {msg}. ")
            return False
        return True

    def assert_types(self, expected, real, msg):
        if real not in expected:
            print(f"Unexpected msg type {real}('{expected}' expected) \n"
                  f"from {self.username} with payload {msg}. ")
            return False
        return True

    def end_session(self, send_msg=False):
        if send_msg:
            self.client_socket.send(self.cr_msg("Closing connection", "e"))
        self.client_socket.close()

    def send_msg(self, msg, type):
        self.client_socket.send(self.cr_msg(msg, type))
        print(f"\t\tSent message {self.cr_msg(msg, type)}")
    def start(self):
        self.send_msg("start", "c")
    def check_if_started(self):
        msg, type = self.receive_msg()
        print(f"Checking if it is start {msg} {type}")
        if self.assert_types("i", type, msg) and msg == "start":
            return True
        return False
    def check_question(self):
        quest, type = self.receive_msg()
        if type == "e":
            print("Connection closed by the server")
            self.end_session()
            return "","e"
        if not self.assert_types(("q", "i", "w"), type, quest):
            self.end_session(send_msg=True)
            return "", "e"
        if quest == "end" and type == "i":
            print("The quiz is ended. Now, lets wait for the next round")
            return False, False
        if type == "q":
            quest = self.decode_quest(quest)
        return quest, type
    def decode_quest(self, q):
        h = self.HEADER_LENGTH
        quest_len = int(q[:h])
        q = q[h+1:]
        quest = q[:quest_len]
        q = q[quest_len:]
        answs = []
        for i in range(4):
            answ_len = int(q[:h])
            q = q[h + 1:]
            answ = q[:answ_len]
            q = q[answ_len:]
            answs.append(answ)
        return (quest, answs)
    def check_winner(self):
        quest, type = self.receive_msg()
        if type == "e":
            print("Connection closed by the server")
            self.end_session()
            return "", "e"
        if not self.assert_type("w", type, quest):
            self.end_session(send_msg=True)
            return "", "e"
        if type == "w":
            return quest, type
