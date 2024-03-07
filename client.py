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
    user_message = json.dumps(user_message)
    client_socket.sendall(user_message.encode('utf-8'))
    print("\nYou are connected to the chat room!")
    print(help_menu)
    

def receive():
    while True:
        try:
            message = client_socket.recv(4096).decode('utf-8')
            message = json.loads(message)

            if 'chat' in message:
                print(message['chat'])

        except Exception as error:
            print("An error occurred!", error)
            client_socket.close()
            break

def write():
    while True:
        message = input("") # get chat message input

        if message.lower() == 'play':
            start_game_msg = {'startgame': user.username}
            start_game_msg = json.dumps(start_game_msg) # serialized json
            client_socket.sendall(start_game_msg.encode('utf-8'))
        
        elif message.lower() == 'help':
            print(help_menu)
       
        else: # just a chat message
            message = f'{user.username}: {message}'
            chat_msg = {'chat': message}
            chat_msg = json.dumps(chat_msg) # serialized json
            client_socket.sendall(chat_msg.encode('utf-8'))





# ------------------ MAIN --------------------
def main():
    establish_connection()
    threading.Thread(target=receive).start() # start the receive thread
    threading.Thread(target=write).start() # start the write thread


if __name__ == "__main__":
    main()
    