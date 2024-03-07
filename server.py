import socket
import sys
import threading
import json
from client import User, TicTacToe

HOST = '127.0.0.1'
PORT = 5200
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

clients = [] # array of connected clients
users = [] # array of connected usernames

class GameInstance:
    def __init__(self, user, tictactoe) -> None:
        self.users = []
        self.tictactoe = TicTacToe()


def establish_connection():
    # TODO
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    print(f"Server is running on {HOST}:{PORT}")


def send_chat_all(message):
    for client in clients:
        chat_msg = {'chat': message}
        chat_msg = json.dumps(chat_msg) # serialized json
        client.sendall(chat_msg.encode('utf-8'))


# handle client interactions
def handle_client(client):
    while True:
        try:
            message = client.recv(4096).decode('utf-8')
            message = json.loads(message)
            if 'chat' in message:
                send_chat_all(message['chat'])

            elif 'startgame' in message:
                start_msg = {'chat': "game start initiated! (not implemented yet)"}
                start_msg = json.dumps(start_msg) # serialized json
                client.sendall(start_msg.encode('utf-8'))
                

        except:
            index = clients.index(client)
            clients.remove(client)
            client.close()
            username = users[index]
            send_chat_all(f"* {username} disconnected! *")
            users.remove(username)
            break


def receive_new_client():
    while True:
        client, address = server_socket.accept()
        print(f"New connection with {str(address)}")

        # handle the new user's username choice
        username_response = client.recv(4096).decode('utf-8')
        username_response = json.loads(username_response)
        users.append(username_response['username'])
        clients.append(client)

        print(f"New client connected! Username: {username_response['username']}!")
        send_chat_all(f"'{username_response['username']}' joined the server!")

        # start the thread to handle the client interactions
        threading.Thread(target=handle_client, args=(client,)).start()



# ------------------ MAIN --------------------
def main():
    establish_connection()
    receive_new_client()
    


if __name__ == "__main__":
    main()