""" Make sure to run server.py as the first file of this project.

    @author Daniel Burrell
"""


import socket
import datetime
import threading
from PyQt5 import QtWidgets
import sys
import pickle
from Client.Views import ChatRoom




class Client(ChatRoom.Ui_MainWindow):
    """Inherits the Main Window that displays the ChatRoom and sets up the functionalities as well
       as establishing a connection to the server.
    """

    __FORMAT = "utf-8"
    __BUFFER = 4000 #Can be changed if wanted to.
    __PORT = 5050 #Can be changed if wanted to.
    __HOST = socket.gethostbyname(socket.gethostname())
    __SERVER = (__HOST, __PORT)

    def  __init__(self, MainWindow, username):
        self.__connected = False
        self.__welcomescreen = None
        self.__receive_thread = threading.Thread(target=self.__receive_message)
        self.__chatroom = MainWindow
        self.__logged_user = username
        self.__client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__connect_to_server()
        self.__validate_user(self.__logged_user)
        

    def __connect_to_server(self):
        """Connects to the server socket."""

        try:
            self.__client.connect(self.__SERVER)
        
        except ConnectionRefusedError:
            print("Some Connection Error Occurred.")
            sys.exit()



    def __validate_user(self, username):
        """Sends the username to the server to be validated. If it is valid, the chatroom is shown.
           
           :param str username: The username submitted to the client.
           :raises OSError: The server is offline so the client is unable to send a message to it.
        
        """

        try:
            self.__client.send(username.encode(self.__FORMAT))
            if self.__client.recv(self.__BUFFER).decode(self.__FORMAT) == "Valid": #The server declares the username valid.
                self.__connected = True
                self.setupUi(self.__chatroom)
                self.__chatroom.setWindowTitle("ChatRoom")
                self.send_button.clicked.connect(self.__send_message)
                self.disconnect_button.clicked.connect(self.__disconnect)
                self.__chatroom.show()
                self.textBrowser.append("You have entered the chat.")
                self.__receive_thread.start()

            else:
                self.__show_welcomescreen()

        except(OSError): #Server file is not running for the client to send a message.
            print("Server is offline.")
            sys.exit()



    def __send_message(self):
        """Sends a message from the client to the server."
           
           :raises ConnectionResetError: The server file was stopped but client still attempted to send a message.

        """

        message = self.textEdit.toPlainText().strip()
        if message: #message is not empty
            try:
                message_date = datetime.datetime.now()
                self.__client.send(message.encode(self.__FORMAT))
                self.textBrowser.append(">YOU: " + message + " - " + message_date.strftime(" %x %I:%M %p"))

            except(ConnectionResetError): #Server has stopped running but client attempts to send message.
                self.textBrowser.append("The server is currently offline.")



    def __receive_message(self):
        """Responsible for receiving messages from the server on a separate thread.
           The message is received from the server and is first attempted to be converted to a list
           using the pickle module. This list represents the list of current clients in the chatroom.
           If an exception occurs while attempting to convert the list, the method understands the message to be
           a normal message from another client and shows it in the text area. Otherwise, the list is iterated through
           and the current clients are appended to the list widget.
        
        """

        try:
            while self.__connected:
                message = self.__client.recv(self.__BUFFER)
                if message:
                    try:
                        connected_users = pickle.loads(message)             
                        self.connected_clients.clear()
                        for name in connected_users:
                            self.connected_clients.addItem(name)

                    except:  #An error occurred while unpickling the message. As such, it is a normal message to be appended to the chat area.
                        self.textBrowser.append(message.decode(self.__FORMAT))

           
        except (ConnectionAbortedError, ConnectionResetError):
            print("User pressed Disconnect.")
            sys.exit()



  
    def __disconnect(self):
        """Disconnects the client from the server."""

        self.__connected = False #Possibly Remove
        try:  
            self.__client.send("DISCONNECT".encode(self.__FORMAT))

        except(ConnectionResetError):
            print("Error occurred here.")
            sys.exit()

        
        self.__client.close()
        self.__show_welcomescreen()



    def __show_welcomescreen(self):
        """Destroys client's ChatRoom and shows the welcome dialog."""

        from Client.welcome import WelcomeScreen  #Done to solve circular import between client.py and welcome.py
        self.__chatroom.destroy()
        dialog = QtWidgets.QDialog()
        self.__welcomescreen = WelcomeScreen(dialog)
