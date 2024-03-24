
import socket
import json

class TicTacToe:
    def __init__(self, client1_sock, client1_username, client2_sock, client2_username) -> None:
        self.gameboard = [ [" ", " ", " "], [" ", " ", " "], [" ", " ", " "] ] # array of game board slot states.
        self.client1 = {'client_socket': client1_sock, 'username': client1_username, 'role': 'X'} # client1 gets role "X"
        self.client2 = {'client_socket': client2_sock, 'username': client2_username, 'role': '0'} # client2 gets role "O"

    def print_game_move_menu(self):
        help_menu = "\n--------------------------------- YOUR TURN -----------------------------------------\n"
        help_menu += "Enter the coordinates of the move you would like to make.\n"
        help_menu += "Example: '1,2'\n"
        help_menu += "-------------------------------------------------------------------------------------\n"
        self.send_both_clients_json({'chat': help_menu})

    # send a json object to a single client
    def send_client_json(self, client, message):
        message = json.dumps(message) # serialized json
        client.sendall(message.encode('utf-8'))

    # send a json object to a single client
    def send_both_clients_json(self, message):
        message = json.dumps(message) # serialized json
        self.client1['client_socket'].sendall(message.encode('utf-8'))
        self.client2['client_socket'].sendall(message.encode('utf-8'))
        
            
    def handle_game_move(self):
        pass

    def print_game_board(self):
        game_board = f"  0  -  1  -  2  \n"
        game_board = f"-------------\n"
        game_board += f"| {self.gameboard[0][0]} | {self.gameboard[0][1]} | {self.gameboard[0][2]} |\n"
        game_board += f"-------------\n"
        game_board += f"| {self.gameboard[1][0]} | {self.gameboard[1][1]} | {self.gameboard[1][2]} |\n"
        game_board += f"-------------\n"
        game_board += f"| {self.gameboard[2][0]} | {self.gameboard[2][1]} | {self.gameboard[2][2]} |\n"
        game_board += f"-------------\n"
        self.send_both_clients_json({'chat': game_board})

    def check_winner(self):
        pass

    def play_game(self):
        pass

