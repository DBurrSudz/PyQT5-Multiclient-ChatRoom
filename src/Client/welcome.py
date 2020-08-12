from Client.Views import UsernameDialog
from PyQt5 import QtCore, QtWidgets, QtGui
from Client.client import Client



class WelcomeScreen(UsernameDialog.Ui_Dialog):
    """Creates a welcome screen that prompts the user to enter a username to enter the chatroom."""

    def __init__(self, Dialog):
        self.__dialog = Dialog
        self.setupUi(self.__dialog)
        self.pushButton.clicked.connect(self.__server_connect)
        self.__dialog.setWindowTitle("Welcome")
        self.__dialog.show()
        self.__main_chat = QtWidgets.QMainWindow()
        self.__chatroom = None


    def __server_connect(self):
        """Checks if the username is already taken by someone present in the chatroom.
           If the username is available, the user is taken to the chatroom.
        """

        inputted_username = self.lineEdit.text().strip()
        self.__dialog.destroy()
        self.__main_chat = QtWidgets.QMainWindow()
        self.__chatroom = Client(self.__main_chat, inputted_username)