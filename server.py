import socket
import threading
import json
from tic_tac_toe import TicTacToe
import time

HOST = '127.0.0.1'
PORT = 5200
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

clients = [] # list of dictionaries of each connected client {'username': name, 'client_socket': socket} , {} , ...
users = [] # list of connected usernames
pending_game_requests = [] # list of pending game request socket pairs. [ [client_who_requested_game, client2], [...], ...]
client_games = [] # list of clients currently playing a game. [ [client1, client2, tictactoe_game_obj], [...], ...]


# initial socket connection and listening
def establish_connection():
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    print(f"Server is running on {HOST}:{PORT}")

# remove client from the online directories
def remove_client(client, username):
    user_to_remove = None
    for user in clients:
        if user['username'] == username:
            user_to_remove = user

    clients.remove(user_to_remove)
    users.remove(username)

# move them into their own gameroom, which also holds their game object.
def move_clients_to_gameroom(client1, client2, game):
    client_games.append([client1, client2, game])

# finish game, remove clients from their gameroom, move them back to the chatroom 
def finish_game(client1, client2):
    for clients in client_games:
        if client1 in clients or client2 in clients:
            client_games.remove(clients)


# send a chat message to all online users in the main chatroom.
def send_chat_all(message):
    for client in clients:
        # check if the client is in a gameroom, ignore them if they are.
        if any(client['client_socket'] in game for game in client_games):
            continue
        chat_msg = {'chat': message}
        chat_msg = json.dumps(chat_msg) # serialized json
        client['client_socket'].sendall(chat_msg.encode('utf-8'))

# send a json object to a single client
def send_single_client_json(client, message):
    try:
        message = json.dumps(message) # serialized json
        client.sendall(message.encode('utf-8'))
    except:
        print("json error at message: ", message)

# send a message to both the clients in a gameroom
def send_gameroom_chat(client, message):
    for gameroom in client_games:
        if client in gameroom:
            # found the gameroom, so send both clients in that room the msg.
            send_single_client_json(gameroom[0], message)
            send_single_client_json(gameroom[1], message)

# get a username from a client's socket
def get_username_by_client(client):
    for user in clients:
        if user['client_socket'] == client:
            return user['username']
        
# get a client's socket from their username
def get_client_by_username(username):
    for user in clients:
        if user['username'] == username:
            return user['client_socket']
        
def get_active_game_by_client(client):
    for gameroom in client_games:
        if client in gameroom:
            return gameroom[2] # return the TicTacToe game object

# Displays all active users. This is sent to a single client. 
def display_active_users(client):
    users_msg = f"\n** Users in chat: ({len(users)}) ** \n-------------------------------------------------------------------------------------\n{users}\n"
    users_msg += "-------------------------------------------------------------------------------------"
    game_players = []
    for clients in client_games:
        game_players.append([get_username_by_client(clients[0]), get_username_by_client(clients[1])])
    users_msg += f"\n** Games in progress: ({len(client_games)}) ** \n-------------------------------------------------------------------------------------\n{game_players}\n"
    users_msg += "-------------------------------------------------------------------------------------\n"
    all_users_msg = {'chat': users_msg}
    send_single_client_json(client, all_users_msg)


def send_user_game_request(client, user_who_requested):
    client_who_requested = get_client_by_username(user_who_requested)
    send_single_client_json(client, {'gamerequest': f"\n'{user_who_requested}' would like to start a game with you!\nType 'accept' or 'decline'"})
    game_request = [client_who_requested, client]
    pending_game_requests.append(game_request)


# handle sending a request to another client to start a game.
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
                # if we found a matching username in active users, and the user is not the same as the requester
                if message['username'].lower() == user['username'].lower() and message['username'].lower() != get_username_by_client(client):
                    user_found = True # username match found
                    send_single_client_json(client, {'chat': f"\nUser: '{message['username']}' found!\nWaiting for them to accept your request...\n"})
                    send_user_game_request(user['client_socket'], get_username_by_client(client)) # Send the found user a request to start game here
                    break

            if user_found == False:
                send_single_client_json(client, {'chat': f"\nUser: '{message['username']}' was not found.\nType 'play' to try again.\n"})
                break
            else: # found user and sent request already
                break

# logic for handling a user's response to a game request.
def handle_game_request_response(message, client):
    clients = find_game_request(client) # find the client pair for the pending game request

    if message['gameresponse'].lower() == 'accept':
        if clients and clients[1] == client: # if client pair found, and this client is the one who was requested by another player
            pending_game_requests.remove(clients)
            # start the game between the two clients
            start_gameplay(clients[0], clients[1])
        else: # there was no pending game request for this client
            send_single_client_json(client, {'chat': "Sorry, you have no pending game requests. Type 'play' to begin a game, or 'help' for help menu."})
    
    elif message['gameresponse'].lower() == 'decline':
        if clients and clients[1] == client: # if client pair found, and this client is the one who was requested by another player
            pending_game_requests.remove(clients)
            send_single_client_json(clients[0], {'chat': f"\n* '{get_username_by_client(clients[1])}' declined your request to start the game. *\n"})
            send_single_client_json(clients[1], {'chat': f"\n* you successfully declined the game request from '{get_username_by_client(clients[0])}' *\n"})
        else:
            send_single_client_json(client, {'chat': "Sorry, you have no pending game requests. Type 'play' to begin a game, or 'help' for help menu."})




# starts the game between two clients
def start_gameplay(client1, client2):
    # send clients the game started message
    send_single_client_json(client1, {'game_started': ""})
    send_single_client_json(client2, {'game_started': ""})
    time.sleep(0.1)
    # create the new game instance
    this_game = TicTacToe(client1, get_username_by_client(client1), client2, get_username_by_client(client2))
    # move the clients into their own game room
    move_clients_to_gameroom(client1, client2, this_game)

    # notify them of game starting, and print game board
    send_single_client_json(client1, {'chat': f"\nGame with '{get_username_by_client(client2)}' starting! \n{this_game.get_game_board()}"})
    send_single_client_json(client2, {'chat': f"\nGame with '{get_username_by_client(client1)}' starting! \n{this_game.get_game_board()}"})

    print(f"** Game started between '{get_username_by_client(client1)}', '{get_username_by_client(client2)}'!")

    curr_client_turn = this_game.get_client_by_turn()
    # send the player who goes first the game move menu.
    time.sleep(0.1)
    send_single_client_json(curr_client_turn, {'chat': this_game.get_game_move_menu()})



def handle_game_move(client, move):
    game = get_active_game_by_client(client)
    if not game.check_winner():
        curr_client_turn = game.get_client_by_turn()

        if client == curr_client_turn:
            # it is their turn, so process the move.
            move = move['game_move']
            # check for validity of move
            if game.check_valid_move(move):
                game.add_move(move, client) # add the move
                game.move_count += 1 # increment the turn 
                # send updated game boards.
                send_gameroom_chat(client, {'chat': f"\n'{get_username_by_client(curr_client_turn)}' played: {move}\n{game.get_game_board()}"})
                time.sleep(0.2)
                # check for win now
                if game.check_winner():
                    # send the clients game finished indicator, and a winner message.
                    if (game.is_draw()): # check for draw
                        send_gameroom_chat(client, {'game_finished': "", 'chat': f"* Game over! It was a draw!! *\n* You are back in the chatroom now!"})
                        finish_game(game.client1['client_socket'], game.client2['client_socket'])
                    else:
                        send_gameroom_chat(client, {'game_finished': "", 'chat': f"* Game over! winner: {game.winner} *\n* You are back in the chatroom now!"})
                        finish_game(game.client1['client_socket'], game.client2['client_socket'])
                else: # no winner yet
                    # get the next client who's turn it is to play, and send them the game move menu.
                    next_client_turn = game.get_client_by_turn()
                    send_single_client_json(next_client_turn, {'chat': game.get_game_move_menu()})

            else: # not a valid move
                send_single_client_json(client, {'chat': "** Not a valid game move. Please try again."})

        else:
            # it is not their turn, so send their message as a chat to the two players. 
            send_single_client_json(client, {'chat': "* Waiting for the other player to make their move"})
            time.sleep(0.05)
            send_gameroom_chat(client, {'chat': f"{get_username_by_client(client)}: {move['game_move']}"})
    
    else: # found a winner
         # send the clients game finished indicator, and a winner message.
        if (game.is_draw()): # check for draw
            send_gameroom_chat(client, {'game_finished': "", 'chat': f"* Game over! It was a draw!! *\n* You are back in the chatroom now!"})
            finish_game(game.client1['client_socket'], game.client2['client_socket'])
        else:
            send_gameroom_chat(client, {'game_finished': "", 'chat': f"* Game over! winner: {game.winner} *\n* You are back in the chatroom now!"})
            finish_game(game.client1['client_socket'], game.client2['client_socket'])



# finds a pending game request.
def find_game_request(client):
    for clients in pending_game_requests:
        if client in clients:
            return clients


# handle new client connections.
def receive_new_client():
    while True:
        client, address = server_socket.accept()
        print(f"New connection with {str(address)}")
        username_verified = False

        while not username_verified:
            # handle the new user's username choice
            username_response = client.recv(4096).decode('utf-8')
            username_response = json.loads(username_response)

            if (verify_username(username_response['username'])):
                username_verified = True
                users.append(username_response['username'])
                send_single_client_json(client, {'success': ""})
                clients.append({'username': username_response['username'], 'client_socket': client})
                print(f"New client connected! Username: {username_response['username']}!")
                # start a thread to handle the client interactions
                threading.Thread(target=handle_client, args=(client,)).start()
                send_chat_all(f"* '{username_response['username']}' joined the server! *")
            else:
                send_single_client_json(client, {'fail': ""})


# verify that a username is not already in use.
def verify_username(username):
    if not users: 
        return True
    else:
        if username in users:
            return False
        return True


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

            elif 'game_move' in message:
                handle_game_move(client, message)

            elif 'logout' in message:
                username = get_username_by_client(client)
                remove_client(client, username)
                send_single_client_json(client, {'logout_success': '* You have been logged out. Goodbye! *'})
                send_chat_all(f"* '{username}' logged out! *")
                break
                

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