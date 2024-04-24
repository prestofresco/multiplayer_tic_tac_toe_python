A simple python multi-user local network chatroom and tic-tac-toe game application using TCP sockets and the client/server design pattern.

Begin by running the server 'python3 server.py'\
The server will then wait for new connections and attempt to accept them.

Connect to the server by running the client 'python3 client.py'\
The user is then asked to pick a username. If the chosen username is already in use, they are asked to choose another. 

On successful login, the user enters the chatroom and is greeted by a help menu, which can be called any time by typing 'help'.
The user may enter a chat message to message all other online users, or use one of the commands outlined in the help menu.

------------------------------------------------------------------------------\
Chatroom Commands / Usage:\
Type a message to send a chat to all other active users.\
'play' - To request to start a game with another player.\
'help' - Prints the help menu in chat.\
'users' - Displays the usernames of all active users in chat, and users in game rooms.\
'logout' - logs the user out of the chatroom and exits the application.\
------------------------------------------------------------------------------\

Once two players have agreed to play a tic-tac-toe game, they are moved into their own game room.\
They may then play the game and chat privately in between their turns.\

------------------------------------------------------------------------------\
Tic Tac Toe Commands / Usage:\
Move input format: 'row, column'\
game inputs are checked for validity.
------------------------------------------------------------------------------\

