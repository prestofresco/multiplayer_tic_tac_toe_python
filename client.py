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
    top = tkinter.Tk()

    myLabel1 = tkinter.Label(top, text="Tic Tac Toe: A Game of Strategy")
    myLabel2 = tkinter.Label(top, text="My Name is Jeff Miller")
    myLabel1.grid(row=0,column=0)
    myLabel2.grid(row=1,column=0)

    top.mainloop()

    


if __name__ == "__main__":
    main()