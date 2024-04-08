import socket
import select
import sys

MSG_LEN = 5

if len(sys.argv) != 3: 
    print("Correct usage: script, host IP address, port number")
    exit() 

Server_IP = str(sys.argv[1])
Server_Port = int(sys.argv[2])

player_name = input("Enter Your Name: ")

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    client_socket.connect((Server_IP, Server_Port))
except:
    print("Failed to connect to the server!")
    sys.exit()

client_socket.setblocking(False)

def send_name_to_server(socket, name_message):
    if name_message == "":
        print("Please choose a name and join again")
        print("DISCONNECTED")
        sys.exit()
    else:
        try:
            socket.send(bytes(name_message, 'utf-8'))
        except:
            socket.close()
            clients_list.remove(receiver)

def send_to_server(socket, message):
    try:
        socket.send(bytes(message, 'utf-8'))
    except:
        socket.close()
        clients_list.remove(receiver)

def receive_message(client_socket):
    try:
        msg_len = client_socket.recv(MSG_LEN)

        if not len(msg_len):
            return False

        message_length = int(msg_len.decode('utf-8').strip())
        return {'Length': msg_len, 'data': client_socket.recv(message_length)}

    except:
        return False

send_name_to_server(client_socket, player_name)

while True:
    sockets_list = [sys.stdin, client_socket]
    read_sockets, _, _ = select.select(sockets_list,[],[])
    for current_socket in read_sockets:
        if current_socket == client_socket:
            encoded_message = receive_message(current_socket)
            if not encoded_message:
                print("DISCONNECTED")
                sys.exit()
            else:
                received_data = encoded_message['data'].decode('utf-8')
                print(received_data)

        else:
            message = sys.stdin.readline()
            send_to_server(client_socket, message)

client_socket.close()
sys.exit()
