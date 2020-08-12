""" This is the entry file into running the client. Run main.py and not client.py directly.
    Remember to run server.py as the first file of the project in order to make the host device listen
    for connections.

    @author Daniel Burrell
"""


from PyQt5 import QtWidgets, QtCore, QtGui
from Client.welcome import WelcomeScreen


def main():
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    welcome = WelcomeScreen(Dialog)
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
    