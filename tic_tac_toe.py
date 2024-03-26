
import socket
import json

class TicTacToe:
    def __init__(self, client1_sock, client1_username, client2_sock, client2_username) -> None:
        self.gameboard = [ [" ", " ", " "], [" ", " ", " "], [" ", " ", " "] ] # array of game board slot states.
        self.client1 = {'client_socket': client1_sock, 'username': client1_username, 'role': 'X'} # client1 gets role "X"
        self.client2 = {'client_socket': client2_sock, 'username': client2_username, 'role': 'O'} # client2 gets role "O"
        self.turn = 'X'
        self.move_count = 0
        self.winner = ""
        self.draw = False # boolean for if there is a draw, no winner

    def get_game_move_menu(self):
        help_menu = f"--------------------------------- YOUR TURN ({self.turn}) -----------------------------------------\n"
        help_menu += f"You are player: '{self.turn}'\n"
        help_menu += "Enter the coordinates of the move you would like to make.\n"
        help_menu += "Format: 'row, column'\n"
        help_menu += "Example: '1,2'\n"
        help_menu += "-------------------------------------------------------------------------------------\n"
        return help_menu

    # send a json object to a single client
    def send_client_json(self, client, message):
        message = json.dumps(message) # serialized json
        client.sendall(message.encode('utf-8'))

    # send a json object to a single client
    def send_both_clients_json(self, message):
        message = json.dumps(message) # serialized json
        self.client1['client_socket'].sendall(message.encode('utf-8'))
        self.client2['client_socket'].sendall(message.encode('utf-8'))

    # player 'X' goes on even turns, 'O' on odd turns.
    def get_turn(self):
        if self.move_count % 2 == 0:
            self.turn = 'X'
            return self.turn
        else:
            self.turn = 'O'
            return self.turn
        
    
    def get_client_by_turn(self):
        if (self.client1['role'] == self.get_turn()):
            return self.client1['client_socket']
        else:
            return self.client2['client_socket']
        
    def get_matching_client_dict(self, client):
        if self.client1['client_socket'] == client:
            return self.client1 
        else:
            return self.client2
 
            
    def handle_game_move(self):
        pass

    def get_game_board(self):
        game_board = f"\n    0 ~ 1 ~ 2  \n"
        game_board += f"  -------------\n"
        game_board += f"0 | {self.gameboard[0][0]} | {self.gameboard[0][1]} | {self.gameboard[0][2]} |\n"
        game_board += f"~ -------------\n"
        game_board += f"1 | {self.gameboard[1][0]} | {self.gameboard[1][1]} | {self.gameboard[1][2]} |\n"
        game_board += f"~ -------------\n"
        game_board += f"2 | {self.gameboard[2][0]} | {self.gameboard[2][1]} | {self.gameboard[2][2]} |\n"
        game_board += f"  -------------\n"
        # self.send_both_clients_json({'chat': game_board})
        return game_board

    def check_winner(self):
        # check for row wins
        for row in self.gameboard:
            if row[0] == row[1] == row[2] != " ":
                self.winner = row[0]
                return True # found a win
        # check for column wins
        for col in range(3):
            if self.gameboard[0][col] == self.gameboard[1][col] == self.gameboard[2][col] != " ":
                self.winner = self.gameboard[0][col]
                return True # found a win
        # check for diagonal wins
        if self.gameboard[0][0] == self.gameboard[1][1] == self.gameboard[2][2] != " ": # check first diagonal
            self.winner = self.gameboard[0][0]
            return True # found a win
        if self.gameboard[0][2] == self.gameboard[1][1] == self.gameboard[2][0] != " ": # check second diagonal
            self.winner = self.gameboard[0][2]
            return True # found a win
        # check for a draw
        if self.move_count == 8:
            self.draw = True
            return True # found a draw
        
        return False # no wins found

    # checks for correct move input, returns boolean
    def check_valid_move(self, move):
        move = move.split(',')
        if len(move) != 2: # check correct format
            return False
        # check that the args are both valid integers
        # we attempt to cast them, and return false on failure
        try:
            move1 = int(move[0])
            move2 = int(move[1])
        except:
            return False
        # check if any of the moves are out of bounds of the game grid
        if ((move1 > 2) or (move1 < 0)) or ((move2 > 2) or (move2 < 0)):
            return False
        # now check for empty spot
        return self.gameboard[int(move[0])][int(move[1])] == " " # returns true if this spot is empty

    def add_move(self, move, client):
        client_dict = self.get_matching_client_dict(client)
        client_role = client_dict['role']
        move = move.split(',') # get the two moves as a list
        # set the move on the gameboard with the client's game piece
        self.gameboard[int(move[0])][int(move[1])] = client_role

