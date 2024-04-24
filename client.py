import tkinter
import socket
import os
import threading
import json

HOST = '127.0.0.1'
PORT = 5200

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
user = None
help_menu = "\n--------------------------------- HELP MENU -----------------------------------------\n"
help_menu += "Type a message to chat with other players.\n"
help_menu += "'play' To start a game with another player type: 'play' in chat.\n"
help_menu += "'help' To display the help menu in chat.\n"
help_menu += "'users' To display active users in chat.\n"
help_menu += "'logout' To logout and disconnect from the chat.\n"
help_menu += "-------------------------------------------------------------------------------------\n"

client_playing_game = False


class User:
    def __init__(self, username, player_role) -> None:
        self.username = username
        self.player_role = player_role # this will be either "X" or "O"


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

# send the server a json message
def send_server_json(json_msg):
    json_msg = json.dumps(json_msg)
    client_socket.sendall(json_msg.encode('utf-8'))

# method to initiate requesting a game to be started.
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

# receive thread method
def receive():
    while True:
        try:
            message = client_socket.recv(4096).decode('utf-8')
            message = json.loads(message)

            if 'chat' in message:
                print(message['chat'])
            elif 'gamerequest' in message:
                print(message['gamerequest'])
            if 'game_started' in message:
                global client_playing_game
                client_playing_game = True
            if 'game_finished' in message:
                client_playing_game = False
            if 'logout_success' in message:
                print(message['logout_success'])
                client_socket.close()
                os._exit(1)

        except Exception as error:
            print("An error occurred!", error, message)
            client_socket.close()
            break

# write thread method
def write():
    while True:
        message = input("") # get chat message input

        if (client_playing_game): # if client is playing a game, we send as game moves
            send_server_json({'game_move': message})
            continue

        if message.lower() == 'play':
            send_server_json({'startgame': user.username})
            initiate_game_start()

        elif message.lower() == 'help':
            print(help_menu)
        
        elif message.lower() == 'users':
            send_server_json({'users': ""})
        
        elif message.lower() == 'accept' or message.lower() == 'decline':
            send_server_json({'gameresponse': message})

        elif message.lower() == 'logout':
            send_server_json({'logout': ""})

        else: # just a chat message
            message = f'{user.username}: {message}'
            chat_msg = {'chat': message}
            send_server_json(chat_msg)




# ------------------ MAIN --------------------
def main():
    establish_connection()
    receive_thread = threading.Thread(target=receive)
    write_thread = threading.Thread(target=write)
    receive_thread.start() # start the receive thread
    write_thread.start() # start the write thread


if __name__ == "__main__":
    main()
    