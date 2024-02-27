#This comment was made by Jeffrey Miller

import tkinter
import socket
import sys


class User:
    def __init__(self, username, player_role) -> None:
        self.username = username
        self.player_role = player_role # this will be either "X" or "O"


class TicTacToe:
    def __init__(self) -> None:
        self.gameboard = ["", "", "", "", "", "", "", "", ""] # array of game board slot states.


def establish_connection():
    # TODO
    client_socket = socket(socket.AF_INET, socket.SOCK_STREAM)
    



# ------------------ MAIN --------------------
def main():
    print()
    


if __name__ == "__main__":
    main()