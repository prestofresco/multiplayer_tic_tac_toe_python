#This comment was made by Jeffrey Miller

import tkinter
import socket
import sys
import threading
import json

HOST = '127.0.0.1'
PORT = 5200

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
user = None
help_menu = "\n--------------------------------- HELP MENU ----------------------------------------\n"
help_menu += "Type a message to chat with other players.\n"
help_menu += "If you would like to start a game with another player type: 'play' in chat.\n"
help_menu += "To display the help menu type: 'help' in chat.\n"
help_menu += "To display active users type: 'users' in chat.\n" # TODO
help_menu += "------------------------------------------------------------------------------------\n"

class User:
    def __init__(self, username, player_role) -> None:
        self.username = username
        self.player_role = player_role # this will be either "X" or "O"


class TicTacToe:
    def __init__(self) -> None:
        self.gameboard = [ ["", "", ""], ["", "", ""], ["", "", ""] ] # array of game board slot states.


def establish_connection():
    client_socket.connect((HOST, PORT))
    global user
    username = input("Choose your username: ")
    # role = input("choose your game piece ('X' or 'O')")
    role = ""
    global user
    user = User(username, role)
    user_message = {'username': user.username}
    send_server_json(user_message)
    print("\nYou are connected to the chat room!")
    print(help_menu)


def send_server_json(json_msg):
    json_msg = json.dumps(json_msg)
    client_socket.sendall(json_msg.encode('utf-8'))


def initiate_game_start():
    while True:
        message = input("")
        if message.lower() == 'cancel':
            cancel_msg = {'cancel': ""}
            send_server_json(cancel_msg)
            break
        elif message.lower() == 'users':
            users_msg = {'users': ""}
            send_server_json(users_msg)
        else:
            username_msg = {'username': message}
            send_server_json(username_msg)


def handle_game_request():
    message = input("")
    if message.lower() == 'accept':
        send_server_json({'gamerequest': 'accept'})
    elif message.lower() == 'decline':
        send_server_json({'gamerequest': 'decline'})
    else:
        send_server_json({'gamerequest': 'invalid'})


def receive():
    while True:
        try:
            message = client_socket.recv(4096).decode('utf-8')
            message = json.loads(message)

            if 'chat' in message:
                print(message['chat'])
            elif 'gamerequest' in message:
                print(message['gamerequest'])
                handle_game_request()

        except Exception as error:
            print("An error occurred!", error)
            client_socket.close()
            break

def write():
    while True:
        message = input("") # get chat message input

        if message.lower() == 'play':
            start_game_msg = {'startgame': user.username}
            send_server_json(start_game_msg)
            initiate_game_start()


        elif message.lower() == 'help':
            print(help_menu)
        
        elif message.lower() == 'users':
            users_msg = {'users': ""}
            send_server_json(users_msg)
       
        else: # just a chat message
            message = f'{user.username}: {message}'
            chat_msg = {'chat': message}
            send_server_json(chat_msg)





# ------------------ MAIN --------------------
def main():
    establish_connection()
    threading.Thread(target=receive).start() # start the receive thread
    threading.Thread(target=write).start() # start the write thread


if __name__ == "__main__":
    main()
    