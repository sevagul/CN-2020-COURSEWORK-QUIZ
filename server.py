import socket
import select

HEADER_LENGTH = 10

IP = "127.0.0.1"
PORT = 1234

server_soket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_soket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server_soket.bind((IP, PORT))

server_soket.listen()

sockets_list = [server_soket]

clients = {}

def cr_header(str):
    return f"{len(str):<{HEADER_LENGTH}}".encode("utf-8")
def cr_msg(msg):
    return cr_header(msg) + msg.encode("utf-8")

def receive_message(client_socket):
    try:
        message_header = client_socket.recv(HEADER_LENGTH)
        if not len(message_header):
            return False
        message_length = int(message_header.decode("utf-8"))
        if message_length > 500:
            return False
        return {"header": message_header, "data": client_socket.recv(message_length)}
    except:
        return False


def broadcast(msg):
    for client in clients.keys():
        client.send(cr_msg(msg))
    print(f"sended message {cr_msg(msg)}" )



while True:
    # question = "How old Seva is?"
    read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)
    for notified_socket in read_sockets:
        if notified_socket == server_soket:
            client_socket, client_address = notified_socket.accept()
            user = receive_message(client_socket)
            if user is False:
                continue
            sockets_list.append(client_socket)
            clients[client_socket] = user
            print((f"Accepted new connectinon from {client_address[0]} : {client_address[1]}",
                   f'{user["data"].decode("utf-8")}'))
            # broadcast(question)
        else:
            msg = receive_message(notified_socket)
            if msg is False:
                print(f'Closed connection from {clients[notified_socket]["data"].decode("utf-8")}')
                sockets_list.remove(notified_socket)
                del clients[notified_socket]
                continue
            user = clients[notified_socket]
            print(f"Received message from {user['data'].decode('utf-8')}: {msg['data'].decode('utf-8')}")
            for client_socket in clients:
                if client_socket != notified_socket:
                    client_socket.send(user['header']+user['data']+msg['header']+msg['data'])

    for notified_socket in exception_sockets:
        sockets_list.remove(notified_socket)
        del clients[notified_socket]
