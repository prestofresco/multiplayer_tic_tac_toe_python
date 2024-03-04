import socket
import sys
import threading

HOST = 'localhost'
PORT = 6789

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))

def establish_connection():
    client, address = server.accept()
    print(f"Connected with {str(address)}")



# ------------------ MAIN --------------------
def main():
    
    server.listen()

    print(f"Server listening on {HOST}:{PORT}")

    establish_connection()
    


if __name__ == "__main__":
    main()