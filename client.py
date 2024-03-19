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
help_menu = "\n--------------------------------- HELP MENU -----------------------------------------\n"
help_menu += "Type a message to chat with other players.\n"
help_menu += "If you would like to start a game with another player type: 'play' in chat.\n"
help_menu += "To display the help menu type: 'help' in chat.\n"
help_menu += "To display active users type: 'users' in chat.\n" # TODO
help_menu += "-------------------------------------------------------------------------------------\n"
# declare the threads globally for access in methods
write_thread = None
receive_thread = None


class User:
    def __init__(self, username, player_role) -> None:
        self.username = username
        self.player_role = player_role # this will be either "X" or "O"


class TicTacToe:
    def __init__(self) -> None:
        self.gameboard = [ ["", "", ""], ["", "", ""], ["", "", ""] ] # array of game board slot states.


def establish_connection():
    username_success = False
    client_socket.connect((HOST, PORT))

    while not username_success:
        username = input("Choose your username: ")
        user_message = {'username': username}
        send_server_json(user_message) # send username choice
        username_response = client_socket.recv(4096).decode('utf-8')
        username_response = json.loads(username_response)
        if 'success' in username_response:
            global user
            username_success = True
            user = User(username, "")
            print("\nYou are connected to the chat room!")
            print(help_menu)
        else:
            print(f"** Username: '{username}' is invalid or already taken. Please choose another username.")


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
            break


def receive():
    while True:
        try:
            message = client_socket.recv(4096).decode('utf-8')
            message = json.loads(message)

            if 'chat' in message:
                print(message['chat'])
            elif 'gamerequest' in message:
                print(message['gamerequest'])

        except Exception as error:
            print("An error occurred!", error)
            client_socket.close()
            break


def write():
    while True:
        message = input("") # get chat message input

        if message.lower() == 'play':
            send_server_json({'startgame': user.username})
            initiate_game_start()

        elif message.lower() == 'help':
            print(help_menu)
        
        elif message.lower() == 'users':
            send_server_json({'users': ""})
        
        elif message.lower() == 'accept' or message.lower() == 'decline':
            send_server_json({'gameresponse': message})


        else: # just a chat message
            message = f'{user.username}: {message}'
            chat_msg = {'chat': message}
            send_server_json(chat_msg)




# ------------------ MAIN --------------------
def main():
    establish_connection()
    global write_thread, receive_thread
    receive_thread = threading.Thread(target=receive)
    write_thread = threading.Thread(target=write)
    receive_thread.start() # start the receive thread
    write_thread.start() # start the write thread


if __name__ == "__main__":
    main()
    