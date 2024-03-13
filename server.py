import socket
import sys
import threading
import json
from client import User, TicTacToe

HOST = '127.0.0.1'
PORT = 5200
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

clients = [] # list of dictionaries of each connected client {'username': name, 'client_socket': socket} , {} , ...
users = [] # list of connected usernames
pending_game_requests = [] # list of pending game request socket pairs. [ [client_who_requested_game, client2], [...], ...]

class GameInstance:
    def __init__(self, user, tictactoe) -> None:
        self.users = []
        self.tictactoe = TicTacToe()


def establish_connection():
    # TODO
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    print(f"Server is running on {HOST}:{PORT}")


def remove_client(client, username):
    user_to_remove = None
    for user in clients:
        if user['username'] == username:
            user_to_remove = user

    clients.remove(user_to_remove)
    users.remove(username)


def send_chat_all(message):
    for client in clients:
        chat_msg = {'chat': message}
        chat_msg = json.dumps(chat_msg) # serialized json
        client['client_socket'].sendall(chat_msg.encode('utf-8'))


def send_single_client_json(client, message):
    message = json.dumps(message) # serialized json
    client.sendall(message.encode('utf-8'))


def get_username_by_client(client):
    for user in clients:
        if user['client_socket'] == client:
            return user['username']
        

def get_client_by_username(username):
    for user in clients:
        if user['username'] == username:
            return user['client_socket']


def display_active_users(client):
    users_msg = f"\nUsers Online: \n{users}"
    all_users_msg = {'chat': users_msg}
    send_single_client_json(client, all_users_msg)


def send_user_game_request(client, user_who_requested):
    client_who_requested = get_client_by_username(user_who_requested)
    send_single_client_json(client, {'gamerequest': f"\n'{user_who_requested}' would like to start a game with you!\nType 'accept' or 'decline'"})
    game_request = [client_who_requested, client]
    pending_game_requests.append(game_request)


def handle_game_start(client):
    game_instructions = "\nGame waiting to start! Please type the username of the player you would like to play with\n"
    game_instructions += "Type 'users' to see a list of active users, or 'cancel' to go back to the chatroom.\n"
    start_msg = {'chat': game_instructions}
    send_single_client_json(client, start_msg)

    while True:
        message = client.recv(4096).decode('utf-8')
        message = json.loads(message)
        # print("handle game msg:", message) # debug

        if 'cancel' in message:
            send_single_client_json(client, {'chat': "\n* Cancelling game... You are now back in the chatrom. *\n"})
            break
        elif 'users' in message:
            display_active_users(client)
            continue
        elif 'username' in message:
            user_found = False
            for user in clients:
                if message['username'].lower() == user['username'].lower():
                    user_found = True # username match found
                    send_single_client_json(client, {'chat': f"\nUser: '{message['username']}' found!\nWaiting for them to accept your request...\n"})
                    send_user_game_request(user['client_socket'], get_username_by_client(client)) # Send the found user a request to start game here
                    break

            if user_found == False:
                send_single_client_json(client, {'chat': f"\nUser: '{message['username']}' was not found.\nType 'play' to try again.\n"})
                break
            else: # found user and sent request already
                break


def handle_game_request_response(message, client):
    clients = find_game_request(client) # find the client pair for the pending game request

    if message['gameresponse'].lower() == 'accept':
        if clients:
            start_gameplay(clients[0], clients[1])
        else: # there was no pending game request for this client
            send_single_client_json(client, {'chat': "Sorry, you have no pending game requests. Type 'play' to begin a game, or 'help' for help menu."})
    
    elif message['gameresponse'].lower() == 'decline':
        if clients:
            pending_game_requests.remove(clients)
            send_single_client_json(clients[0], {'chat': f"\n* '{get_username_by_client(clients[1])}' declined your request to start the game. *\n"})
        else:
            send_single_client_json(client, {'chat': "Sorry, you have no pending game requests. Type 'play' to begin a game, or 'help' for help menu."})


def start_gameplay(client1, client2):
    send_single_client_json(client1, {'chat': f"Game with '{get_username_by_client(client2)}' initiated! (not implemented yet)\n"})
    send_single_client_json(client2, {'chat': f"Game with '{get_username_by_client(client1)}' initiated! (not implemented yet)\n"})


def find_game_request(client):
    for clients in pending_game_requests:
        if client in clients:
            return clients



def receive_new_client():
    while True:
        client, address = server_socket.accept()
        print(f"New connection with {str(address)}")

        # handle the new user's username choice
        username_response = client.recv(4096).decode('utf-8')
        username_response = json.loads(username_response)
        users.append(username_response['username'])
        clients.append({'username': username_response['username'], 'client_socket': client})

        print(f"New client connected! Username: {username_response['username']}!")
        send_chat_all(f"* '{username_response['username']}' joined the server! *")

        # start a thread to handle the client interactions
        threading.Thread(target=handle_client, args=(client,)).start()


# handle client interactions
def handle_client(client):
    while True:
        try:
            message = client.recv(4096).decode('utf-8')
            message = json.loads(message)
            # print("handling: ", get_username_by_client(client), message) # debug

            if 'chat' in message:
                send_chat_all(message['chat'])

            elif 'startgame' in message:
                handle_game_start(client)

            elif 'users' in message:
                display_active_users(client)

            elif 'gameresponse' in message:
                handle_game_request_response(message, client)
                

        except: # exception or disconnect, remove the client and close connection.
            username = get_username_by_client(client)
            remove_client(client, username)
            send_chat_all(f"* '{username}' disconnected! *")
            break



# ------------------ MAIN --------------------
def main():
    establish_connection()
    receive_new_client()
    


if __name__ == "__main__":
    main()